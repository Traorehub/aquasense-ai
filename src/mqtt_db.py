"""Persistance SQLite des messages MQTT — Sprint 6."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MqttDatabase:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pump_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    pressure REAL,
                    vibration REAL,
                    flow REAL,
                    scenario TEXT,
                    month INTEGER,
                    sim_day REAL
                );

                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pump_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence REAL,
                    health_index REAL,
                    proba_json TEXT,
                    latency_ms REAL
                );

                CREATE INDEX IF NOT EXISTS idx_telemetry_pump ON telemetry(pump_id);
                CREATE INDEX IF NOT EXISTS idx_predictions_pump ON predictions(pump_id);
                """
            )

    def insert_telemetry(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO telemetry
                    (pump_id, timestamp, pressure, vibration, flow, scenario, month, sim_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["pump_id"],
                    payload.get("timestamp", _utc_now()),
                    payload.get("pressure"),
                    payload.get("vibration"),
                    payload.get("flow"),
                    payload.get("scenario"),
                    payload.get("month"),
                    payload.get("sim_day"),
                ),
            )

    def insert_prediction(
        self,
        pump_id: str,
        prediction: str,
        confidence: float,
        health_index: float,
        proba: dict[str, float],
        latency_ms: float,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO predictions
                    (pump_id, timestamp, prediction, confidence, health_index, proba_json, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pump_id,
                    _utc_now(),
                    prediction,
                    confidence,
                    health_index,
                    json.dumps(proba, ensure_ascii=False),
                    latency_ms,
                ),
            )

    def recent_predictions(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT pump_id, timestamp, prediction, confidence, health_index, latency_ms
                FROM predictions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
