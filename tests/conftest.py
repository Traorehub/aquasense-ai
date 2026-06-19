"""Fixtures partagées — Sprint 8."""
from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROFILES_PATH = ROOT / "data" / "simulated" / "pump_profiles.json"
MODEL_PATH = ROOT / "models" / "champion_production_v1.joblib"


@pytest.fixture(scope="session", autouse=True)
def _patch_joblib_pickle_classes():
    """Le joblib champion référence __main__ — enregistrer les classes pour pytest."""
    import sys

    import src.train as train_mod
    from src.train import (
        SoftVotingEnsemble,
        ThresholdCalibratedClassifier,
        XGBStringLabelPipeline,
    )

    main = sys.modules["__main__"]
    main.ThresholdCalibratedClassifier = ThresholdCalibratedClassifier
    main.XGBStringLabelPipeline = XGBStringLabelPipeline
    main.SoftVotingEnsemble = SoftVotingEnsemble


@pytest.fixture
def pump_profiles() -> dict:
    if not PROFILES_PATH.exists():
        pytest.skip("pump_profiles.json manquant")
    with open(PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def champion_model():
    if not MODEL_PATH.exists():
        pytest.skip("champion_production_v1.joblib manquant")
    import joblib
    from src.train import ThresholdCalibratedClassifier, XGBStringLabelPipeline

    # Classes requises pour désérialiser le joblib (pickle __main__ ou src.train)
    _ = ThresholdCalibratedClassifier, XGBStringLabelPipeline
    try:
        return joblib.load(MODEL_PATH)
    except AttributeError:
        import src.train as train_mod
        import sys
        sys.modules["__main__"] = train_mod
        return joblib.load(MODEL_PATH)


@pytest.fixture
def mqtt_db_tmp(tmp_path):
    from src.mqtt_db import MqttDatabase

    return MqttDatabase(tmp_path / "test_aquasense.db")


def broker_available(host: str = "127.0.0.1", port: int = 1883, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.fixture
def require_mosquitto():
    if not broker_available():
        pytest.skip("Mosquitto non disponible sur 127.0.0.1:1883")
