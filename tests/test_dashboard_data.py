"""Tests chargement dashboard — Sprint 8."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.data import (
    apply_morocco_display,
    load_alerts,
    load_dashboard_data,
    morocco_site_for_pump,
)
from src.mqtt_config import DB_PATH


def test_morocco_site_inland_bounds():
    site = morocco_site_for_pump("pump_001")
    assert 27.0 <= site["latitude"] <= 36.0
    assert -13.0 <= site["longitude"] <= -1.0
    assert site["region"] in {
        "Souss-Massa", "Marrakech-Safi", "Béni Mellal-Khénifra",
        "Casablanca-Settat", "Rabat-Salé-Kénitra", "Fès-Meknès",
        "Oriental", "Tanger-Tétouan-Al Hoceïma", "Drâa-Tafilalet",
        "Guelmim-Oued Noun",
    }


def test_apply_morocco_display_adds_locality():
    df = pd.DataFrame({"pump_id": ["pump_001", "pump_002"], "latitude": [-3.0, -4.0], "longitude": [32.0, 33.0]})
    out = apply_morocco_display(df)
    assert "locality" in out.columns
    assert out["latitude"].between(27, 36).all()


@pytest.mark.skipif(not DB_PATH.exists(), reason="aquasense.db absent")
def test_load_dashboard_data_50_pumps():
    df, counts = load_dashboard_data()
    assert len(df) == 50
    assert counts.get("telemetry", 0) > 0
    assert counts.get("predictions", 0) > 0


@pytest.mark.skipif(not DB_PATH.exists(), reason="aquasense.db absent")
def test_load_alerts_needs_repair_count():
    df, _ = load_dashboard_data()
    alerts = load_alerts(df)
    assert len(alerts) == 5
    assert (alerts["prediction"] == "functional needs repair").all()


@pytest.mark.skipif(not DB_PATH.exists(), reason="aquasense.db absent")
def test_expected_alert_pumps_present():
    df, _ = load_dashboard_data()
    alerts = load_alerts(df)
    expected = {"pump_011", "pump_021", "pump_027", "pump_029", "pump_043"}
    assert set(alerts["pump_id"]) == expected
