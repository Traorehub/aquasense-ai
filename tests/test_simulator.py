"""Tests simulateur PumpState — Sprint 8."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.simulator import PumpState, assign_scenarios


def test_assign_scenarios_covers_all_types():
    pumps = [f"pump_{i:03d}" for i in range(1, 51)]
    mapping = assign_scenarios(pumps, seed=42)
    values = list(mapping.values())
    assert len(mapping) == 50
    assert set(values) <= {"healthy", "degradation", "failure"}
    assert values.count("healthy") >= 20
    assert values.count("degradation") >= 5
    assert values.count("failure") >= 3


def test_healthy_scenario_normal_sensors():
    state = PumpState(pump_id="pump_001", scenario="healthy", rng=__import__("random").Random(0))
    sample = state.sample(month=6)
    assert sample["pressure"] > 3.0
    assert sample["flow"] > 8.0
    assert sample["scenario"] == "healthy"


def test_failure_scenario_zero_pressure_flow():
    state = PumpState(pump_id="pump_001", scenario="failure", rng=__import__("random").Random(0))
    sample = state.sample(month=6)
    assert sample["pressure"] == 0.0
    assert sample["flow"] == 0.0


def test_degradation_worsens_over_sim_days():
    state = PumpState(pump_id="pump_001", scenario="degradation", rng=__import__("random").Random(1))
    state.sim_day = 0
    early = state.sample(month=6)
    state.sim_day = 14
    late = state.sample(month=6)
    assert late["pressure"] < early["pressure"]
    assert late["flow"] < early["flow"]


def test_dry_season_reduces_flow():
    state = PumpState(pump_id="pump_001", scenario="healthy", rng=__import__("random").Random(2))
    wet = state.sample(month=3)
    dry = state.sample(month=7)
    assert dry["flow"] <= wet["flow"]
