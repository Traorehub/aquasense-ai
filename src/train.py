"""
Entraînement baseline ML — Sprint 3 AquaSense AI (CPU).

Usage:
    python -m src.train

    from src.train import evaluate_model, train_baselines, load_training_data
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from src.preprocessing import (
    CLEAN_DIR,
    PROJECT_ROOT,
    PumpPreprocessor,
    build_encoder,
    load_and_preprocess,
)

TARGET_COL = "status_group"
NEEDS_REPAIR = "functional needs repair"
RANDOM_STATE = 42
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

CLASS_ORDER = [
    "functional",
    "functional needs repair",
    "non functional",
]


def load_training_data() -> pd.DataFrame:
    """Charge train_clean.csv ou régénère via preprocessing."""
    path = CLEAN_DIR / "train_clean.csv"
    if path.exists():
        return pd.read_csv(path)
    train, _ = load_and_preprocess(save=True)
    return train


def get_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_cols = PumpPreprocessor().get_feature_columns()
    present = [c for c in feature_cols if c in df.columns]
    missing = set(feature_cols) - set(present)
    if missing:
        raise ValueError(f"Colonnes features manquantes : {missing}")
    X = df[present].copy()
    y = df[TARGET_COL].copy()
    return X, y


def stratified_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=RANDOM_STATE,
    )


def _ensure_proba(model: Any, X: pd.DataFrame) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    return None


def evaluate_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    classes: list[str] | None = None,
) -> dict[str, Any]:
    """
    Évalue un modèle (ou Pipeline) sur le jeu de test.

    Retourne F1-Macro, F1 par classe, accuracy, ROC-AUC OvR, matrice de confusion,
    temps d'inférence (ms/échantillon).
    """
    classes = classes or CLASS_ORDER

    start = time.perf_counter()
    y_pred = model.predict(X_test)
    elapsed_ms = (time.perf_counter() - start) * 1000
    latency_ms = elapsed_ms / len(X_test)

    f1_macro = f1_score(y_test, y_pred, average="macro", labels=classes, zero_division=0)
    f1_per_class = f1_score(y_test, y_pred, average=None, labels=classes, zero_division=0)
    recall_per_class = recall_score(y_test, y_pred, average=None, labels=classes, zero_division=0)
    accuracy = accuracy_score(y_test, y_pred)

    roc_auc = None
    proba = _ensure_proba(model, X_test)
    if proba is not None:
        try:
            roc_auc = roc_auc_score(
                y_test,
                proba,
                multi_class="ovr",
                average="macro",
                labels=classes,
            )
        except ValueError:
            roc_auc = None

    cm = confusion_matrix(y_test, y_pred, labels=classes)
    report = classification_report(y_test, y_pred, labels=classes, zero_division=0)

    return {
        "f1_macro": float(f1_macro),
        "f1_per_class": {c: float(v) for c, v in zip(classes, f1_per_class)},
        "recall_per_class": {c: float(v) for c, v in zip(classes, recall_per_class)},
        "recall_needs_repair": float(
            recall_per_class[classes.index(NEEDS_REPAIR)] if NEEDS_REPAIR in classes else 0.0
        ),
        "accuracy": float(accuracy),
        "roc_auc_macro_ovr": roc_auc,
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "latency_ms_per_sample": float(latency_ms),
        "n_test": len(y_test),
    }


def _make_lr_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("prep", build_encoder("standard")),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _make_knn_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("prep", build_encoder("standard")),
            ("clf", KNeighborsClassifier(n_neighbors=5, metric="euclidean", n_jobs=-1)),
        ]
    )


def _make_rf_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("prep", build_encoder("none")),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=200,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def _make_xgb_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("prep", build_encoder("none")),
            (
                "clf",
                XGBClassifier(
                    n_estimators=300,
                    objective="multi:softprob",
                    eval_metric="mlogloss",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=0,
                ),
            ),
        ]
    )


def _fit_pipeline(
    pipeline: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
) -> Pipeline:
    if model_name == "xgboost":
        sw = compute_sample_weight(class_weight="balanced", y=y_train)
        pipeline.fit(X_train, y_train, clf__sample_weight=sw)
    else:
        pipeline.fit(X_train, y_train)
    return pipeline


def _cross_val_f1(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, model_name: str) -> dict[str, float]:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    if model_name == "xgboost":
        # CV manuelle avec sample weights pour XGB
        scores = []
        for train_idx, val_idx in cv.split(X, y):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
            pipe = _clone_pipeline(model_name)
            if model_name == "xgboost":
                sw = compute_sample_weight(class_weight="balanced", y=y_tr)
                pipe.fit(X_tr, y_tr, clf__sample_weight=sw)
            else:
                pipe.fit(X_tr, y_tr)
            pred = pipe.predict(X_val)
            scores.append(f1_score(y_val, pred, average="macro", zero_division=0))
        arr = np.array(scores)
    else:
        pipe = _clone_pipeline(model_name)
        arr = cross_val_score(
            pipe,
            X,
            y,
            cv=cv,
            scoring="f1_macro",
            n_jobs=-1,
        )
    return {"mean": float(arr.mean()), "std": float(arr.std())}


def _clone_pipeline(model_name: str) -> Pipeline:
    builders = {
        "logistic_regression": _make_lr_pipeline,
        "knn": _make_knn_pipeline,
        "random_forest": _make_rf_pipeline,
        "xgboost": _make_xgb_pipeline,
    }
    return builders[model_name]()


def tune_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> GridSearchCV:
    pipe = _make_rf_pipeline()
    param_grid = {
        "clf__max_depth": [None, 20, 40],
        "clf__min_samples_leaf": [1, 2, 4],
        "clf__max_features": ["sqrt", "log2"],
    }
    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        scoring="f1_macro",
        n_jobs=-1,
        verbose=1,
    )
    grid.fit(X_train, y_train)
    return grid


def tune_xgboost(X_train: pd.DataFrame, y_train: pd.Series) -> GridSearchCV:
    pipe = _make_xgb_pipeline()
    sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)
    param_grid = {
        "clf__learning_rate": [0.05, 0.1],
        "clf__max_depth": [4, 6, 8],
        "clf__subsample": [0.8, 1.0],
        "clf__colsample_bytree": [0.8, 1.0],
    }
    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        scoring="f1_macro",
        n_jobs=-1,
        verbose=1,
    )
    grid.fit(X_train, y_train, clf__sample_weight=sample_weight)
    return grid


def get_encoded_feature_names(prep) -> list[str]:
    """Noms des features après ColumnTransformer."""
    names: list[str] = []
    for name, trans, cols in prep.transformers_:
        if name == "remainder":
            continue
        if trans == "passthrough":
            names.extend(cols)
        elif hasattr(trans, "get_feature_names_out"):
            names.extend(trans.get_feature_names_out(cols).tolist())
        else:
            names.extend(cols)
    return names


def train_baselines(
    tune: bool = True,
    save: bool = True,
) -> dict[str, Any]:
    """Pipeline complet Sprint 3 : 4 baselines + tuning RF/XGB."""
    df = load_training_data()
    X, y = get_feature_matrix(df)
    X_train, X_test, y_train, y_test = stratified_split(X, y)

    results: dict[str, Any] = {
        "split": {"train": len(X_train), "test": len(X_test)},
        "imbalance_strategy": {
            "lr_rf": "class_weight='balanced'",
            "knn": "pas de pondération (baseline géométrique)",
            "xgboost": "sample_weight balanced",
            "smote": "non utilisé (class_weight suffisant en S3)",
        },
        "models": {},
    }

    baselines = [
        ("logistic_regression", _make_lr_pipeline),
        ("knn", _make_knn_pipeline),
        ("random_forest", _make_rf_pipeline),
        ("xgboost", _make_xgb_pipeline),
    ]

    trained: dict[str, Any] = {}

    for name, builder in baselines:
        print(f"\n=== Entraînement {name} ===")
        pipe = builder()
        pipe = _fit_pipeline(pipe, X_train, y_train, name)
        metrics = evaluate_model(pipe, X_test, y_test)
        cv_stats = _cross_val_f1(X_train, y_train, name)
        trained[name] = pipe
        results["models"][name] = {
            "metrics": metrics,
            "cv_f1_macro": cv_stats,
        }
        print(
            f"  F1-Macro={metrics['f1_macro']:.4f} | "
            f"Recall needs repair={metrics['recall_per_class'].get(NEEDS_REPAIR, 0):.4f} | "
            f"CV={cv_stats.get('mean', 'n/a')}"
        )

    if tune:
        print("\n=== GridSearch Random Forest ===")
        rf_grid = tune_random_forest(X_train, y_train)
        rf_best = rf_grid.best_estimator_
        rf_metrics = evaluate_model(rf_best, X_test, y_test)
        trained["random_forest_tuned"] = rf_best
        results["models"]["random_forest_tuned"] = {
            "metrics": rf_metrics,
            "best_params": rf_grid.best_params_,
            "cv_f1_macro": {"mean": float(rf_grid.best_score_), "std": 0.0},
        }
        print(f"  Best params: {rf_grid.best_params_}")
        print(f"  F1-Macro={rf_metrics['f1_macro']:.4f}")

        print("\n=== GridSearch XGBoost ===")
        xgb_grid = tune_xgboost(X_train, y_train)
        xgb_best = xgb_grid.best_estimator_
        xgb_metrics = evaluate_model(xgb_best, X_test, y_test)
        trained["xgboost_tuned"] = xgb_best
        results["models"]["xgboost_tuned"] = {
            "metrics": xgb_metrics,
            "best_params": xgb_grid.best_params_,
            "cv_f1_macro": {"mean": float(xgb_grid.best_score_), "std": 0.0},
        }
        print(f"  Best params: {xgb_grid.best_params_}")
        print(f"  F1-Macro={xgb_metrics['f1_macro']:.4f}")

    # Tableau comparatif
    comparison = []
    for name, info in results["models"].items():
        m = info["metrics"]
        comparison.append(
            {
                "model": name,
                "f1_macro": m["f1_macro"],
                "f1_needs_repair": m["f1_per_class"].get(NEEDS_REPAIR, 0),
                "recall_needs_repair": m["recall_per_class"].get(NEEDS_REPAIR, 0),
                "accuracy": m["accuracy"],
                "roc_auc": m["roc_auc_macro_ovr"],
                "latency_ms": m["latency_ms_per_sample"],
            }
        )
    comparison_df = pd.DataFrame(comparison).sort_values("f1_macro", ascending=False)
    results["comparison"] = comparison_df.to_dict(orient="records")

    champion_row = comparison_df.iloc[0]
    results["champion"] = champion_row["model"]
    print(f"\n=== Champion : {results['champion']} (F1-Macro={champion_row['f1_macro']:.4f}) ===")

    if save:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        joblib.dump(trained["random_forest_tuned"], MODELS_DIR / "rf_best_v1.joblib")
        joblib.dump(trained["xgboost_tuned"], MODELS_DIR / "xgb_best_v1.joblib")

        # Sauvegarder aussi le champion global
        champion_name = results["champion"]
        joblib.dump(trained[champion_name], MODELS_DIR / "champion_ml_v1.joblib")

        metrics_path = REPORTS_DIR / "sprint_03_metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        comparison_df.to_csv(REPORTS_DIR / "sprint_03_model_comparison.csv", index=False)
        print(f"Métriques → {metrics_path}")
        print(f"Modèles → {MODELS_DIR}")

    results["trained_models"] = trained
    results["X_test"] = X_test
    results["y_test"] = y_test
    return results


def main() -> None:
    results = train_baselines(tune=True, save=True)
    champ = results["champion"]
    f1 = results["models"][champ]["metrics"]["f1_macro"]
    recall_nr = results["models"][champ]["metrics"]["f1_per_class"].get(NEEDS_REPAIR, 0)
    print("\n--- Critères Sprint 3 ---")
    print(f"F1-Macro champion ≥ 0.72 : {'OK' if f1 >= 0.72 else 'NON'} ({f1:.4f})")
    best_nr = max(m["metrics"]["recall_per_class"].get(NEEDS_REPAIR, 0) for m in results["models"].values())
    print(f"Recall needs repair ≥ 0.65 (meilleur modèle) : {'OK' if best_nr >= 0.65 else 'NON'} ({best_nr:.4f})")


if __name__ == "__main__":
    main()
