"""Configuration MQTT partagée — Sprint 6 AquaSense AI."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def _load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file()

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "aquasense")
MQTT_CLIENT_ID_PREFIX = os.getenv("MQTT_CLIENT_ID_PREFIX", "aquasense")

MODEL_PATH = Path(os.getenv("MODEL_PATH", str(PROJECT_ROOT / "models" / "champion_production_v1.joblib")))
DB_PATH = Path(os.getenv("MQTT_DB_PATH", str(PROJECT_ROOT / "data" / "mqtt" / "aquasense.db")))

PUBLISH_INTERVAL_S = float(os.getenv("PUBLISH_INTERVAL_S", "5"))
NUM_PUMPS = int(os.getenv("NUM_PUMPS", "50"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "30"))
SIM_SECONDS_PER_DAY = float(os.getenv("SIM_SECONDS_PER_DAY", "60"))

TELEMETRY_TOPIC = f"{MQTT_TOPIC_PREFIX}/+/telemetry"
prediction_topic = lambda pump_id: f"{MQTT_TOPIC_PREFIX}/{pump_id}/prediction"
telemetry_topic = lambda pump_id: f"{MQTT_TOPIC_PREFIX}/{pump_id}/telemetry"
