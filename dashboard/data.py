"""Chargement des données pour le dashboard Streamlit — Sprint 7."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.mqtt_config import DB_PATH, MODEL_PATH, PROJECT_ROOT
from src.mqtt_db import MqttDatabase
from src.pump_registry import PROFILES_PATH

from dashboard.theme import STATUS_COLORS

COMPARISON_CSV = PROJECT_ROOT / "reports" / "sprint_05_final_comparison.csv"

STATUS_LABELS = {
    "functional": "Opérationnelle",
    "functional needs repair": "Maintenance requise",
    "non functional": "Hors service",
}

# Positions DÉMO pour la carte — forages ruraux par région marocaine.
# Ce ne sont PAS des coordonnées réelles du projet : les profils ML viennent
# de Pump It Up (Tanzanie). Aucun jeu public ONEE/ABH avec GPS marocain labellisé.
MOROCCO_SITES: list[dict[str, str | float]] = [
    # Souss-Massa
    {"region": "Souss-Massa", "locality": "Taroudant", "lat": 30.49, "lon": -8.88},
    {"region": "Souss-Massa", "locality": "Tiznit", "lat": 29.70, "lon": -9.73},
    {"region": "Souss-Massa", "locality": "Biougra", "lat": 30.22, "lon": -9.37},
    {"region": "Souss-Massa", "locality": "Oulad Teïma", "lat": 30.39, "lon": -9.21},
    {"region": "Souss-Massa", "locality": "Inezgane", "lat": 30.35, "lon": -9.54},
    # Marrakech-Safi
    {"region": "Marrakech-Safi", "locality": "El Kelâa", "lat": 32.10, "lon": -7.41},
    {"region": "Marrakech-Safi", "locality": "Chichaoua", "lat": 31.54, "lon": -8.76},
    {"region": "Marrakech-Safi", "locality": "Amizmiz", "lat": 31.73, "lon": -8.23},
    {"region": "Marrakech-Safi", "locality": "Demnate", "lat": 31.73, "lon": -7.04},
    {"region": "Marrakech-Safi", "locality": "Rhamna", "lat": 32.05, "lon": -7.80},
    # Béni Mellal-Khénifra
    {"region": "Béni Mellal-Khénifra", "locality": "Khénifra", "lat": 32.94, "lon": -5.67},
    {"region": "Béni Mellal-Khénifra", "locality": "Béni Mellal", "lat": 32.37, "lon": -6.36},
    {"region": "Béni Mellal-Khénifra", "locality": "Azilal", "lat": 31.96, "lon": -6.57},
    {"region": "Béni Mellal-Khénifra", "locality": "Fkih Ben Salah", "lat": 32.50, "lon": -6.70},
    {"region": "Béni Mellal-Khénifra", "locality": "Khouribga", "lat": 32.88, "lon": -6.91},
    # Casablanca-Settat
    {"region": "Casablanca-Settat", "locality": "Berrechid", "lat": 33.27, "lon": -7.59},
    {"region": "Casablanca-Settat", "locality": "Settat", "lat": 33.00, "lon": -7.62},
    {"region": "Casablanca-Settat", "locality": "Benslimane", "lat": 33.62, "lon": -7.12},
    {"region": "Casablanca-Settat", "locality": "Youssoufia", "lat": 32.25, "lon": -8.53},
    {"region": "Casablanca-Settat", "locality": "Nouaceur", "lat": 33.37, "lon": -7.58},
    # Rabat-Salé-Kénitra
    {"region": "Rabat-Salé-Kénitra", "locality": "Khémisset", "lat": 33.82, "lon": -6.07},
    {"region": "Rabat-Salé-Kénitra", "locality": "Kénitra", "lat": 34.26, "lon": -6.58},
    {"region": "Rabat-Salé-Kénitra", "locality": "Sidi Kacem", "lat": 34.22, "lon": -5.71},
    {"region": "Rabat-Salé-Kénitra", "locality": "Tiflet", "lat": 33.89, "lon": -6.32},
    {"region": "Rabat-Salé-Kénitra", "locality": "Rommani", "lat": 33.53, "lon": -6.60},
    # Fès-Meknès
    {"region": "Fès-Meknès", "locality": "Meknès", "lat": 33.89, "lon": -5.55},
    {"region": "Fès-Meknès", "locality": "Sefrou", "lat": 33.83, "lon": -4.84},
    {"region": "Fès-Meknès", "locality": "Taza", "lat": 34.21, "lon": -4.01},
    {"region": "Fès-Meknès", "locality": "Ifrane", "lat": 33.53, "lon": -5.11},
    {"region": "Fès-Meknès", "locality": "Boulemane", "lat": 33.36, "lon": -4.73},
    # Oriental
    {"region": "Oriental", "locality": "Taourirt", "lat": 34.41, "lon": -2.90},
    {"region": "Oriental", "locality": "Berkane", "lat": 34.92, "lon": -2.32},
    {"region": "Oriental", "locality": "Jerada", "lat": 34.31, "lon": -2.16},
    {"region": "Oriental", "locality": "Figuig", "lat": 32.11, "lon": -1.23},
    {"region": "Oriental", "locality": "Guercif", "lat": 34.23, "lon": -3.35},
    # Tanger-Tétouan-Al Hoceïma
    {"region": "Tanger-Tétouan-Al Hoceïma", "locality": "Chefchaouen", "lat": 35.17, "lon": -5.27},
    {"region": "Tanger-Tétouan-Al Hoceïma", "locality": "Larache", "lat": 35.19, "lon": -6.16},
    {"region": "Tanger-Tétouan-Al Hoceïma", "locality": "Ouezzane", "lat": 34.80, "lon": -5.58},
    {"region": "Tanger-Tétouan-Al Hoceïma", "locality": "Al Hoceïma", "lat": 35.25, "lon": -3.93},
    {"region": "Tanger-Tétouan-Al Hoceïma", "locality": "Ouazzane", "lat": 34.80, "lon": -5.58},
    # Drâa-Tafilalet
    {"region": "Drâa-Tafilalet", "locality": "Errachidia", "lat": 31.93, "lon": -4.43},
    {"region": "Drâa-Tafilalet", "locality": "Midelt", "lat": 32.68, "lon": -4.73},
    {"region": "Drâa-Tafilalet", "locality": "Tinghir", "lat": 31.51, "lon": -5.53},
    {"region": "Drâa-Tafilalet", "locality": "Zagora", "lat": 30.33, "lon": -5.84},
    {"region": "Drâa-Tafilalet", "locality": "Rissani", "lat": 31.28, "lon": -4.27},
    # Guelmim-Oued Noun (zones intérieures / pré-sahariennes)
    {"region": "Guelmim-Oued Noun", "locality": "Tata", "lat": 29.74, "lon": -7.97},
    {"region": "Guelmim-Oued Noun", "locality": "Taliouine", "lat": 30.53, "lon": -7.92},
    {"region": "Guelmim-Oued Noun", "locality": "Foum Zguid", "lat": 30.09, "lon": -6.87},
    {"region": "Guelmim-Oued Noun", "locality": "Tafraout", "lat": 29.72, "lon": -8.97},
    {"region": "Guelmim-Oued Noun", "locality": "Assa", "lat": 28.61, "lon": -9.42},
]

MOROCCO_REGIONS = sorted({str(s["region"]) for s in MOROCCO_SITES})


def _jitter_deg(pump_id: str, scale: float = 0.06) -> tuple[float, float]:
    """Petit décalage déterministe pour éviter la superposition des points."""
    seed = sum(ord(c) for c in pump_id)
    dlat = ((seed % 100) / 100 - 0.5) * 2 * scale
    dlon = (((seed // 100) % 100) / 100 - 0.5) * 2 * scale
    return dlat, dlon


def morocco_site_for_pump(pump_id: str) -> dict[str, str | float]:
    idx = int(pump_id.rsplit("_", 1)[-1]) - 1
    site = MOROCCO_SITES[idx % len(MOROCCO_SITES)]
    dlat, dlon = _jitter_deg(pump_id)
    return {
        "region": str(site["region"]),
        "locality": str(site["locality"]),
        "latitude": float(site["lat"]) + dlat,
        "longitude": float(site["lon"]) + dlon,
    }


def morocco_display_region(pump_id: str) -> str:
    return str(morocco_site_for_pump(pump_id)["region"])


def apply_morocco_display(df: pd.DataFrame) -> pd.DataFrame:
    """Place les pompes sur des localités rurales marocaines (carte démo uniquement)."""
    if df.empty:
        return df
    out = df.copy()
    sites = out["pump_id"].map(morocco_site_for_pump)
    out["latitude"] = sites.map(lambda s: s["latitude"])
    out["longitude"] = sites.map(lambda s: s["longitude"])
    out["region"] = sites.map(lambda s: s["region"])
    out["locality"] = sites.map(lambda s: s["locality"])
    return out


def load_pump_profiles() -> dict[str, dict]:
    if not PROFILES_PATH.exists():
        return {}
    with open(PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_dashboard_data() -> tuple[pd.DataFrame, dict[str, int]]:
    """Fusionne profils + dernières prédictions SQLite."""
    profiles = load_pump_profiles()
    db = MqttDatabase(DB_PATH)
    counts = db.count_rows()
    preds = db.latest_predictions_by_pump()

    if not profiles and not preds:
        return pd.DataFrame(), counts

    pred_map = {r["pump_id"]: r for r in preds}
    rows = []
    for pump_id, profile in sorted(profiles.items()):
        pred = pred_map.get(pump_id, {})
        proba = {}
        if pred.get("proba_json"):
            try:
                proba = json.loads(pred["proba_json"])
            except json.JSONDecodeError:
                proba = {}

        rows.append(
            {
                "pump_id": pump_id,
                "latitude": profile.get("latitude"),
                "longitude": profile.get("longitude"),
                "region": profile.get("region", "non renseigné"),
                "basin": profile.get("basin", "non renseigné"),
                "management": profile.get("management", "non renseigné"),
                "prediction": pred.get("prediction", "en attente"),
                "confidence": pred.get("confidence"),
                "health_index": pred.get("health_index"),
                "latency_ms": pred.get("latency_ms"),
                "timestamp": pred.get("timestamp"),
                "proba_needs_repair": proba.get("functional needs repair"),
                "status_label": STATUS_LABELS.get(
                    pred.get("prediction", ""), pred.get("prediction", "En attente")
                ),
            }
        )

    return pd.DataFrame(rows), counts


def load_alerts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    alerts = df[df["prediction"] == "functional needs repair"].copy()
    if alerts.empty:
        return alerts
    alerts = alerts.sort_values(
        ["proba_needs_repair", "confidence"],
        ascending=[False, False],
        na_position="last",
    )
    return alerts


def load_model_comparison() -> pd.DataFrame:
    if not COMPARISON_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(COMPARISON_CSV)


def telemetry_df(pump_id: str, limit: int = 100) -> pd.DataFrame:
    db = MqttDatabase(DB_PATH)
    rows = db.telemetry_history(pump_id, limit=limit)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def load_pipeline_status(counts: dict[str, int] | None = None) -> dict:
    """État du pipeline S6 : simulateur → MQTT → inférence → SQLite."""
    db = MqttDatabase(DB_PATH)
    counts = counts or db.count_rows()
    recent = db.recent_predictions(100)
    avg_latency = None
    last_ts = None
    if recent:
        latencies = [r["latency_ms"] for r in recent if r.get("latency_ms") is not None]
        if latencies:
            avg_latency = round(sum(latencies) / len(latencies), 1)
        last_ts = recent[0].get("timestamp")

    active = counts.get("telemetry", 0) > 0 and counts.get("predictions", 0) > 0
    return {
        "active": active,
        "telemetry_count": counts.get("telemetry", 0),
        "predictions_count": counts.get("predictions", 0),
        "avg_latency_ms": avg_latency,
        "last_inference": last_ts,
        "model": MODEL_PATH.name,
    }
