"""
Pipeline de nettoyage et feature engineering — Sprint 2 AquaSense AI.

Problème visé : maintenance forages & points d'eau (contexte Maroc).
Dataset : benchmark proxy Pump It Up (Tanzanie).

Usage:
    from src.preprocessing import PumpPreprocessor, load_and_preprocess

    prep = PumpPreprocessor()
    train_clean, test_clean = load_and_preprocess()
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEAN_DIR = PROJECT_ROOT / "data" / "cleaned"

# Colonnes quasi-dupliquées ou sans valeur prédictive
DROP_COLUMNS = [
    "quantity_group",
    "extraction_type_group",
    "waterpoint_type_group",
    "quality_group",
    "region_code",
    "district_code",
    "recorded_by",
    "scheme_name",
    "wpt_name",
    "subvillage",
    "ward",
    "lga",
]

LOW_CARDINALITY_COLS = ["basin", "water_quality", "payment", "source_type", "management"]
HIGH_CARDINALITY_COLS = ["funder", "installer", "extraction_type", "region"]

NUMERIC_FEATURES = [
    "amount_tsh",
    "gps_height",
    "longitude",
    "latitude",
    "population",
    "construction_year",
    "pump_age",
    "year_recorded",
    "month_recorded",
    "day_of_year",
    "age_at_recording",
    "dist_to_basin_center",
    "year_unknown",
    "tsh_is_zero",
    "num_private",
]

BINARY_COLS = ["public_meeting", "permit"]


def _normalize_text(series: pd.Series) -> pd.Series:
    return series.fillna("unknown").astype(str).str.strip().str.lower()


def _haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    """Distance approximative en km entre deux points."""
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


class PumpPreprocessor:
    """Nettoie et enrichit les données Pump It Up."""

    def __init__(self, reference_year: int = 2024, top_n: int = 20):
        self.reference_year = reference_year
        self.top_n = top_n
        self.basin_centroids_: dict[str, tuple[float, float]] = {}
        self.region_centroids_: dict[str, tuple[float, float]] = {}
        self.year_median_by_basin_: dict[str, float] = {}
        self.year_median_global_: float = 0.0
        self.gps_height_median_by_basin_: dict[str, float] = {}
        self.gps_height_median_global_: float = 0.0
        self.tsh_median_: float = 0.0
        self.top_funders_: list[str] = []
        self.top_installers_: list[str] = []
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> "PumpPreprocessor":
        valid = df[(df["longitude"] != 0) & (df["latitude"] != 0)].copy()
        self.basin_centroids_ = (
            valid.groupby("basin")[["latitude", "longitude"]].median().to_dict("index")
        )
        self.basin_centroids_ = {
            k: (v["latitude"], v["longitude"]) for k, v in self.basin_centroids_.items()
        }
        self.region_centroids_ = (
            valid.groupby("region")[["latitude", "longitude"]].median().to_dict("index")
        )
        self.region_centroids_ = {
            k: (v["latitude"], v["longitude"]) for k, v in self.region_centroids_.items()
        }

        valid_years = df.loc[df["construction_year"] > 0, "construction_year"]
        self.year_median_global_ = float(valid_years.median())
        self.year_median_by_basin_ = (
            df.loc[df["construction_year"] > 0]
            .groupby("basin")["construction_year"]
            .median()
            .to_dict()
        )

        valid_height = df.loc[df["gps_height"] >= 0, "gps_height"]
        self.gps_height_median_global_ = float(valid_height.median())
        self.gps_height_median_by_basin_ = (
            df.loc[df["gps_height"] >= 0]
            .groupby("basin")["gps_height"]
            .median()
            .to_dict()
        )

        self.tsh_median_ = float(df.loc[df["amount_tsh"] > 0, "amount_tsh"].median())

        funder_norm = _normalize_text(df["funder"])
        installer_norm = _normalize_text(df["installer"])
        self.top_funders_ = funder_norm.value_counts().head(self.top_n).index.tolist()
        self.top_installers_ = installer_norm.value_counts().head(self.top_n).index.tolist()

        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("Appeler fit() avant transform().")

        out = df.copy()
        out = self._fix_gps(out)
        out = self._fix_construction_year(out)
        out = self._fix_gps_height(out)
        out = self._fix_funder_installer(out)
        out = self._fix_amount_tsh(out)
        out = self._engineer_features(out)
        out = self._encode_binary(out)
        out = self._drop_columns(out)
        return out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)

    def _fix_gps(self, df: pd.DataFrame) -> pd.DataFrame:
        invalid = (df["longitude"].abs() < 0.01) | (df["latitude"].abs() < 0.01)
        for idx in df.index[invalid]:
            basin = df.at[idx, "basin"]
            region = df.at[idx, "region"]
            if basin in self.basin_centroids_:
                lat, lon = self.basin_centroids_[basin]
            elif region in self.region_centroids_:
                lat, lon = self.region_centroids_[region]
            else:
                lat = df["latitude"].median()
                lon = df["longitude"].median()
            df.at[idx, "latitude"] = lat
            df.at[idx, "longitude"] = lon
        return df

    def _fix_construction_year(self, df: pd.DataFrame) -> pd.DataFrame:
        df["year_unknown"] = (df["construction_year"] == 0).astype(int)
        mask = df["construction_year"] == 0
        df.loc[mask, "construction_year"] = df.loc[mask, "basin"].map(
            self.year_median_by_basin_
        ).fillna(self.year_median_global_)
        return df

    def _fix_gps_height(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[df["gps_height"] < 0, "gps_height"] = np.nan
        df["gps_height"] = df["gps_height"].fillna(
            df["basin"].map(self.gps_height_median_by_basin_)
        ).fillna(self.gps_height_median_global_)
        return df

    def _fix_funder_installer(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, top_list in [("funder", self.top_funders_), ("installer", self.top_installers_)]:
            normalized = _normalize_text(df[col])
            df[col] = normalized.where(normalized.isin(top_list), "other")
        return df

    def _fix_amount_tsh(self, df: pd.DataFrame) -> pd.DataFrame:
        df["tsh_is_zero"] = (df["amount_tsh"] == 0).astype(int)
        zero_mask = df["amount_tsh"] == 0
        df.loc[zero_mask, "amount_tsh"] = self.tsh_median_
        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        dates = pd.to_datetime(df["date_recorded"], errors="coerce")
        df["year_recorded"] = dates.dt.year
        df["month_recorded"] = dates.dt.month
        df["day_of_year"] = dates.dt.dayofyear

        df["pump_age"] = self.reference_year - df["construction_year"]
        df["age_at_recording"] = df["year_recorded"] - df["construction_year"]

        basin_lat = df["basin"].map({k: v[0] for k, v in self.basin_centroids_.items()})
        basin_lon = df["basin"].map({k: v[1] for k, v in self.basin_centroids_.items()})
        df["dist_to_basin_center"] = _haversine_km(
            df["latitude"].values,
            df["longitude"].values,
            basin_lat.values,
            basin_lon.values,
        )
        df["dist_to_basin_center"] = df["dist_to_basin_center"].fillna(0.0)
        return df

    def _encode_binary(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in BINARY_COLS:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .map({"True": 1, "False": 0, True: 1, False: 0, "true": 1, "false": 0})
                    .fillna(0)
                    .astype(int)
                )
        return df

    def _drop_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        to_drop = [c for c in DROP_COLUMNS if c in df.columns]
        return df.drop(columns=to_drop)

    def get_feature_columns(self) -> list[str]:
        return NUMERIC_FEATURES + LOW_CARDINALITY_COLS + HIGH_CARDINALITY_COLS + BINARY_COLS


def build_encoder(scaler: Literal["standard", "minmax", "none"] = "standard") -> ColumnTransformer:
    """Construit un encodeur sklearn pour les modèles ML/DL."""
    numeric = NUMERIC_FEATURES + BINARY_COLS
    if scaler == "standard":
        num_pipe = StandardScaler()
    elif scaler == "minmax":
        num_pipe = MinMaxScaler()
    else:
        num_pipe = "passthrough"

    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, numeric),
            ("low_cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), LOW_CARDINALITY_COLS),
            ("high_cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), HIGH_CARDINALITY_COLS),
        ],
        remainder="drop",
    )


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_values = pd.read_csv(RAW_DIR / "train_values.csv")
    train_labels = pd.read_csv(RAW_DIR / "train_labels.csv")
    test_values = pd.read_csv(RAW_DIR / "test_values.csv")
    return train_values, train_labels, test_values


def load_and_preprocess(
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge, nettoie et sauvegarde train/test."""
    train_values, train_labels, test_values = load_raw_data()

    prep = PumpPreprocessor()
    train_clean = prep.fit_transform(train_values)
    test_clean = prep.transform(test_values)

    train_clean = train_clean.merge(train_labels, on="id", how="left")

    if save:
        CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        train_clean.to_csv(CLEAN_DIR / "train_clean.csv", index=False)
        test_clean.to_csv(CLEAN_DIR / "test_clean.csv", index=False)

    return train_clean, test_clean


if __name__ == "__main__":
    train, test = load_and_preprocess()
    feature_cols = PumpPreprocessor().get_feature_columns()
    present = [c for c in feature_cols if c in train.columns]
    nan_count = train[present].isna().sum().sum()
    print(f"train_clean : {train.shape}")
    print(f"test_clean  : {test.shape}")
    print(f"Features utilisées : {len(present)}")
    print(f"NaN restants dans features : {nan_count}")
    print(f"Sauvegardé dans {CLEAN_DIR}")
