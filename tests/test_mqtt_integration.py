"""Tests intégration MQTT live (Mosquitto requis) — Sprint 8.

Lancer avec : pytest tests/test_mqtt_integration.py -v
Prérequis : Mosquitto sur 127.0.0.1:1883

Note : utilise le préfixe `aquasense_s8test` pour ne pas interférer
avec un simulateur/consumer déjà lancé sur `aquasense/`.
"""
from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

import paho.mqtt.client as mqtt
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mqtt_consumer import MqttInferenceConsumer

pytestmark = pytest.mark.integration

TEST_PREFIX = f"aquasense_s8test_{uuid.uuid4().hex[:6]}"
TARGET_PUMPS = ("pump_001", "pump_011", "pump_021")


def _payload(pump_id: str, scenario: str = "healthy") -> dict:
    return {
        "pump_id": pump_id,
        "timestamp": "2026-06-19T12:00:00+00:00",
        "pressure": 4.2,
        "vibration": 0.05,
        "flow": 12.0,
        "scenario": scenario,
        "month": 6,
        "sim_day": 0,
    }


def _count_target_rows(db, table: str = "telemetry") -> int:
    n = 0
    for pid in TARGET_PUMPS:
        if table == "telemetry":
            n += len(db.telemetry_history(pid, limit=1))
        else:
            preds = db.recent_predictions(50)
            n += sum(1 for p in preds if p["pump_id"] == pid)
    return n


def test_live_broker_publish_subscribe(require_mosquitto):
    """S8-03 : message publié → reçu en < 5 s."""
    topic = f"{TEST_PREFIX}/pump_001/telemetry"
    received: list[str] = []

    def on_message(client, userdata, msg):
        received.append(msg.topic)

    sub = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"s8_test_sub_{uuid.uuid4().hex[:6]}",
    )
    sub.on_message = on_message
    sub.connect("127.0.0.1", 1883)
    sub.subscribe(f"{TEST_PREFIX}/+/telemetry")
    sub.loop_start()
    time.sleep(0.3)

    pub = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"s8_test_pub_{uuid.uuid4().hex[:6]}",
    )
    pub.connect("127.0.0.1", 1883)
    pub.publish(topic, json.dumps(_payload("pump_001")))
    pub.disconnect()

    deadline = time.time() + 5
    while time.time() < deadline and not received:
        time.sleep(0.1)

    sub.loop_stop()
    sub.disconnect()
    assert received == [topic]


def test_live_consumer_end_to_end(require_mosquitto, tmp_path):
    """S8-04 : consumer in-process + publish MQTT → SQLite (topic isolé)."""
    db_path = tmp_path / "live_e2e.db"
    consumer = MqttInferenceConsumer(
        db_path=str(db_path),
        buffer_size=3,
        topic_prefix=TEST_PREFIX,
    )
    consumer.client.connect("127.0.0.1", 1883)
    consumer.client.loop_start()
    time.sleep(0.5)

    pub = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"s8_e2e_pub_{uuid.uuid4().hex[:6]}",
    )
    pub.connect("127.0.0.1", 1883)
    for pid in TARGET_PUMPS:
        pub.publish(f"{TEST_PREFIX}/{pid}/telemetry", json.dumps(_payload(pid)))
    pub.disconnect()

    deadline = time.time() + 5
    while time.time() < deadline and _count_target_rows(consumer.db, "telemetry") < 3:
        time.sleep(0.1)

    consumer.client.loop_stop()
    consumer.client.disconnect()

    for pid in TARGET_PUMPS:
        assert consumer.db.telemetry_history(pid, limit=1), f"Pas de télémétrie pour {pid}"
        recent = consumer.db.recent_predictions(20)
        assert any(p["pump_id"] == pid for p in recent), f"Pas de prédiction pour {pid}"
