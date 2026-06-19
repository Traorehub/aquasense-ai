"""Tests consumer MQTT hors broker (mock messages) — Sprint 8."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mqtt_consumer import MqttInferenceConsumer
from src.train import CLASS_ORDER


def _payload(pump_id: str, scenario: str, pressure: float, flow: float, vibration: float = 0.05) -> bytes:
    return json.dumps(
        {
            "pump_id": pump_id,
            "timestamp": "2026-06-19T12:00:00+00:00",
            "pressure": pressure,
            "vibration": vibration,
            "flow": flow,
            "scenario": scenario,
            "month": 6,
            "sim_day": 14 if scenario == "degradation" else 0,
        }
    ).encode("utf-8")


def _make_msg(payload: bytes) -> Mock:
    msg = Mock()
    msg.payload = payload
    return msg


@pytest.fixture
def consumer(tmp_path):
    db_path = tmp_path / "consumer_test.db"
    c = MqttInferenceConsumer(db_path=str(db_path), buffer_size=5)
    return c


def test_consumer_healthy_inference(consumer):
    msg = _make_msg(_payload("pump_003", "healthy", 4.2, 12.0))
    consumer._on_message(consumer.client, None, msg)
    preds = consumer.db.recent_predictions(1)
    assert len(preds) == 1
    assert preds[0]["prediction"] in CLASS_ORDER
    assert preds[0]["latency_ms"] < 500


def test_consumer_failure_stores_telemetry(consumer):
    msg = _make_msg(_payload("pump_002", "failure", 0.0, 0.0, 0.9))
    consumer._on_message(consumer.client, None, msg)
    rows = consumer.db.telemetry_history("pump_002", limit=1)
    assert len(rows) == 1
    assert rows[0]["pressure"] == 0.0


def test_consumer_50_pumps_no_loss(consumer):
    latencies = []
    for i in range(1, 51):
        pid = f"pump_{i:03d}"
        msg = _make_msg(_payload(pid, "healthy", 4.1, 11.5))
        t0 = time.perf_counter()
        consumer._on_message(consumer.client, None, msg)
        latencies.append((time.perf_counter() - t0) * 1000)

    counts = consumer.db.count_rows()
    assert counts["telemetry"] == 50
    assert counts["predictions"] == 50
    assert max(latencies) < 500


def test_consumer_needs_repair_pumps_detected(consumer):
    """S8-05 : les 5 pompes alerte connues produisent needs repair avec télémétrie saine."""
    repair_pumps = ["pump_011", "pump_021", "pump_027", "pump_029", "pump_043"]
    detected = []
    for pid in repair_pumps:
        msg = _make_msg(_payload(pid, "healthy", 4.2, 12.0))
        consumer._on_message(consumer.client, None, msg)
        pred = consumer.db.recent_predictions(1)[0]["prediction"]
        if pred == "functional needs repair":
            detected.append(pid)
    assert len(detected) >= 3, f"Recall partiel attendu, obtenu: {detected}"


def test_consumer_invalid_json_ignored(consumer):
    msg = Mock()
    msg.payload = b"not-json"
    consumer._on_message(consumer.client, None, msg)
    assert consumer.db.count_rows()["telemetry"] == 0


def test_consumer_unknown_pump_ignored(consumer):
    msg = _make_msg(_payload("pump_999", "healthy", 4.2, 12.0))
    consumer._on_message(consumer.client, None, msg)
    assert consumer.db.count_rows()["telemetry"] == 0
