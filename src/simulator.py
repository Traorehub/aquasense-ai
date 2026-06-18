"""
Simulateur de capteurs IoT — Sprint 6 AquaSense AI.

Publie de la télémétrie MQTT pour N pompes avec 3 scénarios :
  - healthy      : pompe saine
  - degradation  : dégradation progressive (14 jours simulés)
  - failure      : panne (pression/débit nuls, vibrations erratiques)

Usage:
    py -3.10 -m src.simulator
    py -3.10 -m src.simulator --pumps 10 --interval 2
"""
from __future__ import annotations

import argparse
import json
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from src.mqtt_config import (
    MQTT_CLIENT_ID_PREFIX,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_TOPIC_PREFIX,
    NUM_PUMPS,
    PUBLISH_INTERVAL_S,
    SIM_SECONDS_PER_DAY,
    telemetry_topic,
)

SCENARIOS = ("healthy", "degradation", "failure")
DRY_MONTHS = {6, 7, 8, 9}
DRY_FLOW_FACTOR = 0.85

PRESSURE_DROP_PER_DAY = 0.3
VIBRATION_RISE_PER_DAY = 0.02
FLOW_DROP_PER_DAY = 0.5
MAX_DEGRADATION_DAYS = 14


@dataclass
class PumpState:
    pump_id: str
    scenario: str
    sim_day: float = 0.0
    rng: random.Random = field(default_factory=random.Random)

    def advance_time(self, interval_s: float, seconds_per_day: float) -> None:
        if self.scenario == "degradation":
            self.sim_day += interval_s / seconds_per_day

    def sample(self, month: int) -> dict:
        if self.scenario == "healthy":
            pressure = self.rng.gauss(4.2, 0.1)
            vibration = max(0.0, self.rng.gauss(0.05, 0.01))
            flow = max(0.0, self.rng.gauss(12.0, 0.5))
        elif self.scenario == "degradation":
            day = min(self.sim_day, MAX_DEGRADATION_DAYS)
            pressure = max(0.0, 4.2 - PRESSURE_DROP_PER_DAY * day + self.rng.gauss(0, 0.05))
            vibration = max(0.0, 0.05 + VIBRATION_RISE_PER_DAY * day + self.rng.gauss(0, 0.01))
            flow = max(0.0, 12.0 - FLOW_DROP_PER_DAY * day + self.rng.gauss(0, 0.3))
        else:
            pressure = 0.0
            flow = 0.0
            vibration = self.rng.uniform(0.3, 1.0) if self.rng.random() < 0.4 else self.rng.gauss(0.08, 0.03)

        if month in DRY_MONTHS:
            flow *= DRY_FLOW_FACTOR

        return {
            "pump_id": self.pump_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pressure": round(pressure, 3),
            "vibration": round(max(0.0, vibration), 4),
            "flow": round(max(0.0, flow), 3),
            "scenario": self.scenario,
            "month": month,
            "sim_day": round(self.sim_day, 2),
        }


def assign_scenarios(pump_ids: list[str], seed: int = 42) -> dict[str, str]:
    """Répartition ~60 % saines, 25 % dégradation, 15 % panne."""
    rng = random.Random(seed)
    shuffled = pump_ids.copy()
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_failure = max(1, int(n * 0.15))
    n_degradation = max(1, int(n * 0.25))
    n_healthy = n - n_failure - n_degradation

    mapping: dict[str, str] = {}
    for pid in shuffled[:n_healthy]:
        mapping[pid] = "healthy"
    for pid in shuffled[n_healthy : n_healthy + n_degradation]:
        mapping[pid] = "degradation"
    for pid in shuffled[n_healthy + n_degradation :]:
        mapping[pid] = "failure"
    return mapping


def build_pump_states(n_pumps: int, month: int, seed: int = 42) -> list[PumpState]:
    pump_ids = [f"pump_{i:03d}" for i in range(1, n_pumps + 1)]
    scenarios = assign_scenarios(pump_ids, seed=seed)
    states = []
    for i, pump_id in enumerate(pump_ids):
        rng = random.Random(seed + i)
        states.append(PumpState(pump_id=pump_id, scenario=scenarios[pump_id], rng=rng))
    return states


def run_simulator(
    n_pumps: int = NUM_PUMPS,
    interval_s: float = PUBLISH_INTERVAL_S,
    month: int | None = None,
    seconds_per_day: float = SIM_SECONDS_PER_DAY,
    host: str = MQTT_HOST,
    port: int = MQTT_PORT,
) -> None:
    month = month or datetime.now().month
    states = build_pump_states(n_pumps, month=month)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"{MQTT_CLIENT_ID_PREFIX}_sim_{uuid.uuid4().hex[:8]}",
    )
    client.connect(host, port, keepalive=60)
    client.loop_start()

    counts = {s: 0 for s in SCENARIOS}
    for st in states:
        counts[st.scenario] += 1

    print(f"Simulateur AquaSense — {n_pumps} pompes -> {host}:{port}")
    print(f"  Scénarios : {counts} | mois={month} | intervalle={interval_s}s")
    print(f"  Topic : {MQTT_TOPIC_PREFIX}/{{pump_id}}/telemetry")
    print("  Ctrl+C pour arrêter.\n")

    try:
        while True:
            for state in states:
                payload = state.sample(month=month)
                topic = telemetry_topic(state.pump_id)
                client.publish(topic, json.dumps(payload), qos=0)
                state.advance_time(interval_s, seconds_per_day)
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("\nArrêt simulateur.")
    finally:
        client.loop_stop()
        client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulateur MQTT AquaSense")
    parser.add_argument("--pumps", type=int, default=NUM_PUMPS)
    parser.add_argument("--interval", type=float, default=PUBLISH_INTERVAL_S)
    parser.add_argument("--month", type=int, default=None, help="Mois simulé (6-9 = saison sèche)")
    parser.add_argument("--host", default=MQTT_HOST)
    parser.add_argument("--port", type=int, default=MQTT_PORT)
    args = parser.parse_args()

    run_simulator(
        n_pumps=args.pumps,
        interval_s=args.interval,
        month=args.month,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
