"""
Entraînement Deep Learning — Sprint 4 AquaSense AI.

Usage:
    python -m src.train_dl           # MLP + ResidualMLP + 1D-CNN
    python -m src.train_dl tune      # + grid search 9 combinaisons + export TFLite
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pandas as pd

from src.dl_utils import (
    MODELS_DIR,
    REPORTS_DIR,
    build_cnn1d,
    build_mlp,
    build_residual_mlp,
    compile_model,
    evaluate_keras_model,
    export_tflite,
    load_ml_comparison_metrics,
    permutation_importance_keras,
    prepare_dl_data,
    train_keras_model,
)

EPOCHS = 100
BATCH_SIZE = 512


def _train_architecture(
    name: str,
    model,
    data: dict[str, Any],
    *,
    validation_split: float | None = None,
    verbose: int = 1,
) -> tuple[Any, dict[str, Any]]:
    compile_model(model, lr=1e-3, class_weight=data["class_weight"])
    train_keras_model(
        model,
        data,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=validation_split,
        verbose=verbose,
    )
    metrics = evaluate_keras_model(model, data["X_val"], data["y_val"], data["label_encoder"])
    print(
        f"  F1-Macro={metrics['f1_macro']:.4f} | "
        f"Recall needs repair={metrics['recall_needs_repair']:.4f}"
    )
    return model, metrics


def train_dl_models(tune: bool = False, save: bool = True, epochs: int = EPOCHS) -> dict[str, Any]:
    global EPOCHS
    EPOCHS = epochs

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    data = prepare_dl_data(test_size=0.2)
    results: dict[str, Any] = {"input_dim": data["input_dim"], "class_weight": data["class_weight"], "models": {}}
    trained: dict[str, Any] = {}

    print("\n=== MLP baseline ===")
    mlp, mlp_metrics = _train_architecture(
        "mlp_baseline",
        build_mlp(data["input_dim"], dropout=0.3),
        data,
        validation_split=0.2,
    )
    trained["mlp_baseline"] = mlp
    results["models"]["mlp_baseline"] = mlp_metrics

    print("\n=== Residual MLP ===")
    res, res_metrics = _train_architecture(
        "residual_mlp",
        build_residual_mlp(data["input_dim"], dropout=0.3),
        data,
        validation_split=None,
    )
    trained["residual_mlp"] = res
    results["models"]["residual_mlp"] = res_metrics

    print("\n=== 1D-CNN ===")
    cnn, cnn_metrics = _train_architecture(
        "cnn1d",
        build_cnn1d(data["input_dim"], dropout=0.3),
        data,
        validation_split=None,
    )
    trained["cnn1d"] = cnn
    results["models"]["cnn1d"] = cnn_metrics

    best_name = max(results["models"], key=lambda k: results["models"][k]["f1_macro"])
    best_model = trained[best_name]
    results["champion_dl"] = best_name

    if tune:
        print("\n=== Grid search MLP (9 combinaisons) ===")
        grid = {"dropout": [0.2, 0.3, 0.5], "lr": [1e-2, 1e-3, 1e-4]}
        best_score = -1.0
        best_cfg: dict[str, Any] = {}
        tuned_best = None

        for dropout in grid["dropout"]:
            for lr in grid["lr"]:
                model = build_mlp(data["input_dim"], dropout=dropout, l2_reg=0.001)
                compile_model(
                    model,
                    lr=lr,
                    class_weight=data["class_weight"],
                    use_weighted_loss=True,
                )
                train_keras_model(
                    model,
                    data,
                    epochs=EPOCHS,
                    batch_size=BATCH_SIZE,
                    validation_split=None,
                    use_class_weight=False,
                    use_sample_weight=True,
                    verbose=0,
                )
                metrics = evaluate_keras_model(model, data["X_val"], data["y_val"], data["label_encoder"])
                print(
                    f"  dropout={dropout} lr={lr} → F1={metrics['f1_macro']:.4f} | "
                    f"recall_nr={metrics['recall_needs_repair']:.4f}"
                )
                if metrics["f1_macro"] > best_score:
                    best_score = metrics["f1_macro"]
                    best_cfg = {"dropout": dropout, "lr": lr, "batch_size": BATCH_SIZE, "l2_reg": 0.001}
                    tuned_best = model

        if tuned_best is not None:
            tuned_metrics = evaluate_keras_model(
                tuned_best, data["X_val"], data["y_val"], data["label_encoder"]
            )
            results["models"]["mlp_tuned"] = {"config": best_cfg, **tuned_metrics}
            trained["mlp_tuned"] = tuned_best
            if tuned_metrics["f1_macro"] > results["models"][best_name]["f1_macro"]:
                best_model = tuned_best
                best_name = "mlp_tuned"
                results["champion_dl"] = best_name

        print("\n=== Comparaison L2 (0.0 vs 0.001) ===")
        for l2 in [0.0, 0.001]:
            model = build_mlp(data["input_dim"], dropout=0.3, l2_reg=l2)
            compile_model(model, lr=1e-3, class_weight=data["class_weight"])
            train_keras_model(
                model,
                data,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                validation_split=None,
                verbose=0,
            )
            m = evaluate_keras_model(model, data["X_val"], data["y_val"], data["label_encoder"])
            results["models"][f"mlp_l2_{l2}"] = m
            print(f"  L2={l2} → F1={m['f1_macro']:.4f}")

    print(f"\n=== Champion DL : {best_name} (F1-Macro={results['models'][best_name]['f1_macro']:.4f}) ===")

    comparison_rows = []
    for name, info in results["models"].items():
        if "f1_macro" not in info:
            continue
        comparison_rows.append(
            {
                "architecture": name,
                "f1_macro": info["f1_macro"],
                "f1_needs_repair": info["f1_needs_repair"],
                "recall_needs_repair": info.get("recall_needs_repair", 0),
                "accuracy": info["accuracy"],
            }
        )
    comparison_df = pd.DataFrame(comparison_rows).sort_values("f1_macro", ascending=False)
    results["comparison"] = comparison_df.to_dict(orient="records")

    if save:
        mlp.save(MODELS_DIR / "mlp_best_v1.keras")
        res.save(MODELS_DIR / "residual_mlp_v1.keras")
        cnn.save(MODELS_DIR / "cnn1d_v1.keras")
        best_model.save(MODELS_DIR / "best_dl_model.keras")
        export_tflite(best_model, MODELS_DIR / "best_dl_model.tflite")

        if tune and "mlp_tuned" in trained:
            trained["mlp_tuned"].save(MODELS_DIR / "mlp_tuned_best_v1.keras")
            export_tflite(trained["mlp_tuned"], MODELS_DIR / "mlp_tuned_best_v1.tflite")

        comparison_df.to_csv(REPORTS_DIR / "sprint_04_dl_comparison.csv", index=False)

        ml_df = load_ml_comparison_metrics()
        if not ml_df.empty:
            ml_top = ml_df.sort_values("f1_macro", ascending=False).head(3).copy()
            ml_top["type"] = "ML"
            dl_top = comparison_df.head(3).rename(columns={"architecture": "model"}).copy()
            dl_top["type"] = "DL"
            pd.concat([ml_top, dl_top], ignore_index=True).to_csv(
                REPORTS_DIR / "sprint_04_ml_vs_dl.csv", index=False
            )

        with open(REPORTS_DIR / "sprint_04_metrics.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        if tune and "mlp_tuned" in trained:
            perm = permutation_importance_keras(
                trained["mlp_tuned"],
                data["X_val"][:2000],
                data["y_val"][:2000],
                data["feature_names"],
                n_repeats=3,
            )
            perm.head(15).to_csv(REPORTS_DIR / "sprint_04_perm_importance.csv", index=False)

        print(f"Métriques → {REPORTS_DIR / 'sprint_04_metrics.json'}")
        print(f"Modèles → {MODELS_DIR}")

    results["trained_models"] = trained
    results["data"] = data
    return results


def main() -> None:
    tune = len(sys.argv) > 1 and sys.argv[1] == "tune"
    results = train_dl_models(tune=tune, save=True)
    champ = results["champion_dl"]
    f1 = results["models"][champ]["f1_macro"]
    recall_nr = results["models"][champ].get("recall_needs_repair", 0)
    print("\n--- Critères Sprint 4 ---")
    print(f"F1-Macro DL ≥ 0.72 : {'OK' if f1 >= 0.72 else 'NON'} ({f1:.4f})")
    print(f"Recall needs repair : {recall_nr:.4f}")
    print(f"Architectures évaluées : {len(results['comparison'])}")


if __name__ == "__main__":
    main()
