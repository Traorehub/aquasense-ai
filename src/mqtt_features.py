"""Construction du vecteur de features à partir de télémétrie MQTT + profil pompe."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.preprocessing import PumpPreprocessor

BASELINE_FLOW = 12.0
BASELINE_PRESSURE = 4.2


def build_feature_row(profile: dict[str, Any], readings: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Fusionne le profil statique (enquête Pump It Up) et la télémétrie agrégée.

    Les capteurs simulés (pression, vibration, débit) modulent des proxies
    tabulaires (`amount_tsh`, `gps_height`) pour refléter la dégradation.
    """
    feature_cols = PumpPreprocessor().get_feature_columns()
    row: dict[str, Any] = {col: profile[col] for col in feature_cols if col in profile}

    if readings:
        flow_mean = float(np.mean([r["flow"] for r in readings]))
        pressure_mean = float(np.mean([r["pressure"] for r in readings]))

        flow_ratio = float(np.clip(flow_mean / BASELINE_FLOW, 0.05, 1.5))
        pressure_ratio = float(np.clip(pressure_mean / BASELINE_PRESSURE, 0.0, 1.2))

        if "amount_tsh" in row:
            row["amount_tsh"] = float(row["amount_tsh"]) * flow_ratio
        if "gps_height" in row:
            row["gps_height"] = float(row["gps_height"]) * (0.85 + 0.15 * pressure_ratio)

    for col in feature_cols:
        row.setdefault(col, 0)

    return pd.DataFrame([row], columns=feature_cols)


def health_index(readings: list[dict[str, Any]]) -> float:
    """Score synthétique 0–1 dérivé de la télémétrie (pour le dashboard S7)."""
    if not readings:
        return 1.0
    flow_mean = float(np.mean([r["flow"] for r in readings]))
    pressure_mean = float(np.mean([r["pressure"] for r in readings]))
    vibration_mean = float(np.mean([r["vibration"] for r in readings]))

    flow_score = np.clip(flow_mean / BASELINE_FLOW, 0.0, 1.0)
    pressure_score = np.clip(pressure_mean / BASELINE_PRESSURE, 0.0, 1.0)
    vibration_penalty = np.clip(1.0 - vibration_mean / 0.5, 0.0, 1.0)
    return float((flow_score + pressure_score + vibration_penalty) / 3.0)
