"""Profils de pompes simulées — métadonnées ML échantillonnées depuis train_clean."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.preprocessing import PumpPreprocessor, PROJECT_ROOT
from src.train import TARGET_COL, load_training_data

PROFILES_PATH = PROJECT_ROOT / "data" / "simulated" / "pump_profiles.json"


def ensure_pump_profiles(n_pumps: int = 50, seed: int = 42) -> dict[str, dict]:
    """Charge ou génère les profils ML pour chaque pompe simulée."""
    if PROFILES_PATH.exists():
        with open(PROFILES_PATH, encoding="utf-8") as f:
            profiles = json.load(f)
        if len(profiles) >= n_pumps:
            return {k: profiles[k] for k in sorted(profiles)[:n_pumps]}

    df = load_training_data()
    sample = df.sample(n=min(n_pumps, len(df)), random_state=seed).reset_index(drop=True)

    feature_cols = PumpPreprocessor().get_feature_columns()
    profiles: dict[str, dict] = {}
    for i, row in sample.iterrows():
        pump_id = f"pump_{i + 1:03d}"
        record = {col: row[col] for col in feature_cols if col in row.index}
        if TARGET_COL in row.index:
            record[TARGET_COL] = row[TARGET_COL]
        if "id" in row.index:
            record["source_id"] = int(row["id"])
        profiles[pump_id] = record

    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False, default=str)

    return profiles
