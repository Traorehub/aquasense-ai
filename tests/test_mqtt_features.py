"""Tests mqtt_features — Sprint 8."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mqtt_features import build_feature_row, health_index


def _reading(scenario: str, pressure: float, flow: float, vibration: float = 0.05) -> dict:
    return {
        "pump_id": "pump_001",
        "pressure": pressure,
        "vibration": vibration,
        "flow": flow,
        "scenario": scenario,
        "month": 6,
        "sim_day": 0,
    }


def test_health_index_healthy_high(pump_profiles):
    readings = [_reading("healthy", 4.2, 12.0, 0.05) for _ in range(5)]
    assert health_index(readings) > 0.8


def test_health_index_failure_low(pump_profiles):
    readings = [_reading("failure", 0.0, 0.0, 0.8) for _ in range(3)]
    assert health_index(readings) < 0.4


def test_health_index_empty_defaults_to_one():
    assert health_index([]) == 1.0


def test_build_feature_row_has_all_columns(pump_profiles):
    profile = pump_profiles["pump_001"]
    readings = [_reading("healthy", 4.2, 12.0)]
    X = build_feature_row(profile, readings)
    assert len(X.columns) == 26
    assert len(X) == 1


def test_build_feature_row_degradation_reduces_amount_tsh(pump_profiles):
    profile = pump_profiles["pump_001"]
    base_tsh = float(profile["amount_tsh"])
    healthy = build_feature_row(profile, [_reading("healthy", 4.2, 12.0)])
    degraded = build_feature_row(profile, [_reading("degradation", 1.0, 2.0)])
    assert float(degraded["amount_tsh"].iloc[0]) < float(healthy["amount_tsh"].iloc[0])
    assert float(degraded["amount_tsh"].iloc[0]) <= base_tsh


def test_build_feature_row_no_readings_keeps_profile(pump_profiles):
    profile = pump_profiles["pump_002"]
    X = build_feature_row(profile, [])
    assert float(X["amount_tsh"].iloc[0]) == float(profile["amount_tsh"])
