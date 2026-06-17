"""
Utilitaires Deep Learning — Sprint 4 AquaSense AI.

Usage:
    from src.dl_utils import prepare_dl_data, build_mlp, train_keras_model
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder, OrdinalEncoder
from tensorflow import keras
from tensorflow.keras import layers, regularizers

from src.preprocessing import (
    BINARY_COLS,
    CLEAN_DIR,
    HIGH_CARDINALITY_COLS,
    LOW_CARDINALITY_COLS,
    NUMERIC_FEATURES,
    PROJECT_ROOT,
)
from src.train import CLASS_ORDER, NEEDS_REPAIR, RANDOM_STATE, TARGET_COL

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_clean_train() -> pd.DataFrame:
    path = CLEAN_DIR / "train_clean.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} introuvable — exécuter src/preprocessing.py")
    return pd.read_csv(path)


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    drop_cols = [c for c in ["id", TARGET_COL, "date_recorded"] if c in df.columns]
    X = df.drop(columns=drop_cols)
    y = df[TARGET_COL]
    return X, y


def build_dl_preprocessor() -> ColumnTransformer:
    numeric = NUMERIC_FEATURES + BINARY_COLS
    return ColumnTransformer(
        transformers=[
            ("num", MinMaxScaler(), numeric),
            (
                "low_cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                LOW_CARDINALITY_COLS,
            ),
            (
                "high_cat",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                HIGH_CARDINALITY_COLS,
            ),
        ],
        remainder="drop",
    )


def prepare_dl_data(test_size: float = 0.2) -> dict[str, Any]:
    """Prépare X/y encodés pour Keras (hold-out stratifié 80/20)."""
    df = load_clean_train()
    X_raw, y_raw = split_xy(df)

    le = LabelEncoder()
    le.fit(CLASS_ORDER)
    y = le.transform(y_raw)

    preprocessor = build_dl_preprocessor()
    X = preprocessor.fit_transform(X_raw)

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    y_train_oh = keras.utils.to_categorical(y_train, num_classes=3)
    y_val_oh = keras.utils.to_categorical(y_val, num_classes=3)

    class_counts = np.bincount(y_train, minlength=3)
    total = class_counts.sum()
    class_weight = {i: float(total / (3 * c)) if c > 0 else 1.0 for i, c in enumerate(class_counts)}

    freq = class_counts / total
    inv_freq = 1.0 / np.clip(freq, 1e-8, None)
    sample_weights = inv_freq[y_train] / inv_freq.mean()

    feature_names = _get_feature_names(preprocessor)

    return {
        "X_train": X_train.astype(np.float32),
        "X_val": X_val.astype(np.float32),
        "y_train": y_train,
        "y_val": y_val,
        "y_train_oh": y_train_oh,
        "y_val_oh": y_val_oh,
        "class_weight": class_weight,
        "sample_weights": sample_weights.astype(np.float32),
        "label_encoder": le,
        "preprocessor": preprocessor,
        "feature_names": feature_names,
        "input_dim": X_train.shape[1],
        "n_classes": 3,
    }


def _get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    names: list[str] = []
    for name, trans, cols in preprocessor.transformers_:
        if name == "remainder":
            continue
        if hasattr(trans, "get_feature_names_out"):
            names.extend(trans.get_feature_names_out(cols).tolist())
        else:
            names.extend(cols)
    return names


def build_mlp(
    input_dim: int,
    n_classes: int = 3,
    dropout: float = 0.3,
    l2_reg: float = 0.0,
) -> keras.Model:
    reg = regularizers.l2(l2_reg) if l2_reg > 0 else None
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim,)),
            layers.Dense(256, activation="relu", kernel_regularizer=reg),
            layers.BatchNormalization(),
            layers.Dropout(dropout),
            layers.Dense(128, activation="relu", kernel_regularizer=reg),
            layers.BatchNormalization(),
            layers.Dropout(dropout),
            layers.Dense(64, activation="relu", kernel_regularizer=reg),
            layers.Dense(n_classes, activation="softmax"),
        ],
        name="mlp_baseline",
    )
    return model


def _residual_block(x: tf.Tensor, units: int, dropout: float, l2_reg: float = 0.0) -> tf.Tensor:
    reg = regularizers.l2(l2_reg) if l2_reg > 0 else None
    skip = x
    if int(x.shape[-1]) != units:
        skip = layers.Dense(units, kernel_regularizer=reg)(x)
    out = layers.Dense(units, activation="relu", kernel_regularizer=reg)(x)
    out = layers.BatchNormalization()(out)
    out = layers.Dropout(dropout)(out)
    out = layers.Dense(units, activation="relu", kernel_regularizer=reg)(out)
    out = layers.Add()([out, skip])
    out = layers.Activation("relu")(out)
    return out


def build_residual_mlp(
    input_dim: int,
    n_classes: int = 3,
    dropout: float = 0.3,
    l2_reg: float = 0.0,
) -> keras.Model:
    inputs = layers.Input(shape=(input_dim,))
    x = layers.Dense(128, activation="relu")(inputs)
    for _ in range(3):
        x = _residual_block(x, 128, dropout, l2_reg)
    x = layers.Dense(64, activation="relu")(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)
    return keras.Model(inputs, outputs, name="residual_mlp")


def build_cnn1d(
    input_dim: int,
    n_classes: int = 3,
    dropout: float = 0.3,
    l2_reg: float = 0.0,
) -> keras.Model:
    reg = regularizers.l2(l2_reg) if l2_reg > 0 else None
    inputs = layers.Input(shape=(input_dim,))
    x = layers.Reshape((input_dim, 1))(inputs)
    x = layers.Conv1D(64, kernel_size=3, activation="relu", padding="same", kernel_regularizer=reg)(x)
    x = layers.GlobalMaxPooling1D()(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Dense(64, activation="relu", kernel_regularizer=reg)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)
    return keras.Model(inputs, outputs, name="cnn1d")


def weighted_categorical_crossentropy(class_weights: dict[int, float]):
    weights = tf.constant([class_weights[i] for i in range(len(class_weights))], dtype=tf.float32)

    def loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        base = keras.losses.categorical_crossentropy(y_true, y_pred)
        sample_weight = tf.reduce_sum(y_true * weights, axis=-1)
        return base * sample_weight

    return loss


def default_callbacks() -> list[keras.callbacks.Callback]:
    return [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
        ),
    ]


def compile_model(
    model: keras.Model,
    lr: float = 1e-3,
    class_weight: dict[int, float] | None = None,
    use_weighted_loss: bool = False,
) -> keras.Model:
    if use_weighted_loss and class_weight is not None:
        loss = weighted_categorical_crossentropy(class_weight)
    else:
        loss = keras.losses.CategoricalCrossentropy()

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss=loss,
        metrics=["accuracy"],
    )
    return model


def train_keras_model(
    model: keras.Model,
    data: dict[str, Any],
    epochs: int = 100,
    batch_size: int = 512,
    validation_split: float | None = None,
    use_class_weight: bool = True,
    use_sample_weight: bool = False,
    verbose: int = 1,
) -> keras.callbacks.History:
    fit_kwargs: dict[str, Any] = {
        "epochs": epochs,
        "batch_size": batch_size,
        "callbacks": default_callbacks(),
        "verbose": verbose,
    }

    if validation_split is not None:
        fit_kwargs["validation_split"] = validation_split
        x_fit, y_fit = data["X_train"], data["y_train_oh"]
    else:
        fit_kwargs["validation_data"] = (data["X_val"], data["y_val_oh"])
        x_fit, y_fit = data["X_train"], data["y_train_oh"]

    if use_class_weight and not use_sample_weight:
        fit_kwargs["class_weight"] = data["class_weight"]
    if use_sample_weight:
        fit_kwargs["sample_weight"] = data["sample_weights"][: len(x_fit)]

    return model.fit(x_fit, y_fit, **fit_kwargs)


def evaluate_keras_model(
    model: keras.Model,
    X: np.ndarray,
    y: np.ndarray,
    label_encoder: LabelEncoder,
) -> dict[str, Any]:
    y_prob = model.predict(X, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    f1_macro = f1_score(y, y_pred, average="macro", zero_division=0)
    f1_per_class = f1_score(y, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    recall_per_class = recall_score(y, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    acc = accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred, labels=[0, 1, 2])

    needs_repair_idx = 1
    return {
        "f1_macro": float(f1_macro),
        "f1_functional": float(f1_per_class[0]),
        "f1_needs_repair": float(f1_per_class[needs_repair_idx]),
        "f1_non_functional": float(f1_per_class[2]),
        "recall_needs_repair": float(recall_per_class[needs_repair_idx]),
        "accuracy": float(acc),
        "confusion_matrix": cm.tolist(),
        "y_pred": y_pred,
        "y_prob": y_prob,
    }


def export_tflite(model: keras.Model, output_path: Path) -> Path:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(tflite_model)
    return output_path


def permutation_importance_keras(
    model: keras.Model,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    n_repeats: int = 5,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    baseline = f1_score(y, np.argmax(model.predict(X, verbose=0), axis=1), average="macro")

    importances = []
    for j, name in enumerate(feature_names):
        scores = []
        for _ in range(n_repeats):
            X_perm = X.copy()
            rng.shuffle(X_perm[:, j])
            pred = np.argmax(model.predict(X_perm, verbose=0), axis=1)
            scores.append(f1_score(y, pred, average="macro"))
        importances.append({"feature": name, "importance": baseline - np.mean(scores)})

    return pd.DataFrame(importances).sort_values("importance", ascending=False)


def load_ml_comparison_metrics() -> pd.DataFrame:
    json_path = REPORTS_DIR / "sprint_03_metrics.json"
    if json_path.exists():
        import json

        with open(json_path, encoding="utf-8") as f:
            results = json.load(f)
        rows = []
        for name, info in results.get("models", {}).items():
            m = info["metrics"]
            rows.append(
                {
                    "model": name,
                    "f1_macro": m["f1_macro"],
                    "f1_needs_repair": m["f1_per_class"].get(NEEDS_REPAIR, 0),
                    "accuracy": m["accuracy"],
                }
            )
        return pd.DataFrame(rows)

    csv_path = REPORTS_DIR / "sprint_03_model_comparison.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()
