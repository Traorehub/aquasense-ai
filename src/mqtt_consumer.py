"""
Consumer MQTT + inférence temps réel — Sprint 6 AquaSense AI.

Subscribe : aquasense/+/telemetry
Publish   : aquasense/{pump_id}/prediction

Usage:
    py -3.10 -m src.mqtt_consumer
    py -3.10 -m src.mqtt_consumer --model models/champion_production_v1.joblib
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from collections import defaultdict, deque
from typing import Any

import joblib
import paho.mqtt.client as mqtt

from src.mqtt_config import (
    BUFFER_SIZE,
    DB_PATH,
    MODEL_PATH,
    MQTT_CLIENT_ID_PREFIX,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_TOPIC_PREFIX,
)
from src.mqtt_db import MqttDatabase
from src.mqtt_features import build_feature_row, health_index
from src.pump_registry import ensure_pump_profiles
from src.train import CLASS_ORDER, ThresholdCalibratedClassifier, XGBStringLabelPipeline

# Requis pour désérialiser le modèle joblib
_ = ThresholdCalibratedClassifier, XGBStringLabelPipeline


class MqttInferenceConsumer:
    def __init__(
        self,
        model_path: str | None = None,
        host: str = MQTT_HOST,
        port: int = MQTT_PORT,
        buffer_size: int = BUFFER_SIZE,
        db_path: str | None = None,
        topic_prefix: str | None = None,
    ):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.model_path = model_path or str(MODEL_PATH)
        self.topic_prefix = topic_prefix or MQTT_TOPIC_PREFIX
        self.model = joblib.load(self.model_path)
        self.profiles = ensure_pump_profiles()
        self.buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=buffer_size))
        self.db = MqttDatabase(db_path or DB_PATH)

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"{MQTT_CLIENT_ID_PREFIX}_consumer_{uuid.uuid4().hex[:8]}",
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: mqtt.ReasonCode,
        properties: Any = None,
    ) -> None:
        if reason_code.is_failure:
            print(f"Échec connexion MQTT : {reason_code}")
            return
        topic = f"{self.topic_prefix}/+/telemetry"
        client.subscribe(topic, qos=0)
        print(f"Consumer connecté — subscribe {topic}")
        print(f"  Modèle : {self.model_path}")
        print(f"  Profils : {len(self.profiles)} pompes | buffer={self.buffer_size}")
        print(f"  SQLite : {self.db.path}\n")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        pump_id = payload.get("pump_id")
        if not pump_id or pump_id not in self.profiles:
            return

        self.db.insert_telemetry(payload)
        self.buffers[pump_id].append(payload)

        readings = list(self.buffers[pump_id])
        profile = self.profiles[pump_id]
        X = build_feature_row(profile, readings)

        t0 = time.perf_counter()
        prediction = self.model.predict(X)[0]
        proba_arr = self.model.predict_proba(X)[0]
        latency_ms = (time.perf_counter() - t0) * 1000

        proba = {cls: float(p) for cls, p in zip(CLASS_ORDER, proba_arr)}
        confidence = float(max(proba_arr))
        h_idx = health_index(readings)

        result = {
            "pump_id": pump_id,
            "timestamp": payload.get("timestamp"),
            "prediction": str(prediction),
            "confidence": round(confidence, 4),
            "health_index": round(h_idx, 4),
            "proba": proba,
            "latency_ms": round(latency_ms, 2),
            "buffer_size": len(readings),
            "scenario": payload.get("scenario"),
        }

        client.publish(
            f"{self.topic_prefix}/{pump_id}/prediction", json.dumps(result), qos=0
        )
        self.db.insert_prediction(
            pump_id=pump_id,
            prediction=str(prediction),
            confidence=confidence,
            health_index=h_idx,
            proba=proba,
            latency_ms=latency_ms,
        )

        print(
            f"[{pump_id}] {prediction} "
            f"(conf={confidence:.2f}, health={h_idx:.2f}, {latency_ms:.1f}ms, "
            f"buf={len(readings)})"
        )

    def run(self) -> None:
        print(f"Connexion MQTT {self.host}:{self.port}...")
        self.client.connect(self.host, self.port, keepalive=60)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nArrêt consumer.")
        finally:
            self.client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Consumer MQTT + inférence AquaSense")
    parser.add_argument("--model", default=str(MODEL_PATH))
    parser.add_argument("--host", default=MQTT_HOST)
    parser.add_argument("--port", type=int, default=MQTT_PORT)
    parser.add_argument("--buffer", type=int, default=BUFFER_SIZE)
    parser.add_argument("--db", default=str(DB_PATH))
    args = parser.parse_args()

    consumer = MqttInferenceConsumer(
        model_path=args.model,
        host=args.host,
        port=args.port,
        buffer_size=args.buffer,
        db_path=args.db,
    )
    consumer.run()


if __name__ == "__main__":
    main()
