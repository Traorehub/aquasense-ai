"""Test rapide du pipeline MQTT (nécessite Mosquitto local)."""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict, deque

import joblib
import paho.mqtt.client as mqtt

from src.mqtt_features import build_feature_row
from src.pump_registry import ensure_pump_profiles
from src.train import CLASS_ORDER, ThresholdCalibratedClassifier, XGBStringLabelPipeline

_ = ThresholdCalibratedClassifier, XGBStringLabelPipeline


def main() -> int:
    model = joblib.load("models/champion_production_v1.joblib")
    profiles = ensure_pump_profiles(50)
    buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=5))
    received: list[tuple] = []

    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        pid = payload["pump_id"]
        if pid not in profiles:
            return
        buffers[pid].append(payload)
        X = build_feature_row(profiles[pid], list(buffers[pid]))
        pred = model.predict(X)[0]
        received.append((pid, pred, payload.get("scenario")))
        print(f"OK {pid} -> {pred} ({payload.get('scenario')})")

    sub = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="test_sub")
    sub.on_message = on_message
    sub.connect("127.0.0.1", 1883)
    sub.subscribe("aquasense/+/telemetry")
    sub.loop_start()
    time.sleep(0.5)

    pub = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="test_pub")
    pub.connect("127.0.0.1", 1883)
    for pid in ("pump_001", "pump_040", "pump_050"):
        msg = {
            "pump_id": pid,
            "pressure": 4.2,
            "vibration": 0.05,
            "flow": 12.0,
            "scenario": "healthy",
            "month": 6,
            "sim_day": 0,
        }
        pub.publish(f"aquasense/{pid}/telemetry", json.dumps(msg))
    pub.disconnect()
    time.sleep(1.5)
    sub.loop_stop()
    sub.disconnect()

    print(f"Messages inférés : {len(received)}")
    return 0 if received else 1


if __name__ == "__main__":
    sys.exit(main())
