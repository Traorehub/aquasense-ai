"""
Dashboard Streamlit AquaSense AI — Sprint 7.
Vue Maroc · données temps réel SQLite (pipeline MQTT S6).

Usage:
    python -m streamlit run dashboard/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.data import (
    STATUS_COLORS,
    STATUS_LABELS,
    apply_morocco_display,
    load_alerts,
    load_dashboard_data,
    load_model_comparison,
    load_pipeline_status,
    morocco_display_region,
    telemetry_df,
)
from dashboard.theme import CHART_COLORS, PLOTLY_LAYOUT, inject_css

NEEDS_REPAIR = "functional needs repair"
PAGES = ("Vue d'ensemble", "Alertes", "Détail pompe", "Modèles", "À propos")


def _fmt_pct(value) -> str:
    return f"{float(value):.0%}" if pd.notna(value) else "N/D"


def _fmt_float(value, decimals: int = 2) -> str:
    return f"{float(value):.{decimals}f}" if pd.notna(value) else "N/D"


def _fmt_ms(value) -> str:
    return f"{float(value):.0f} ms" if pd.notna(value) else "N/D"


def _fmt_latency_avg(pipeline: dict) -> str:
    value = pipeline.get("avg_latency_ms")
    return f"{float(value):.0f}" if value is not None else "0"


@st.fragment(run_every=10)
def refresh_data():
    st.session_state["pumps_df"], st.session_state["db_counts"] = load_dashboard_data()
    st.session_state["pipeline"] = load_pipeline_status(st.session_state["db_counts"])


def _init_state():
    if "pumps_df" not in st.session_state:
        df, counts = load_dashboard_data()
        st.session_state["pumps_df"] = df
        st.session_state["db_counts"] = counts
        st.session_state["pipeline"] = load_pipeline_status(counts)
    if "assignments" not in st.session_state:
        st.session_state["assignments"] = {}


def _plotly_defaults(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def _section(title: str):
    """Carte native Streamlit — évite le HTML coupé qui s'affiche en texte."""
    return st.container(border=True)


def render_hero(page: str) -> None:
    subtitles = {
        "Vue d'ensemble": "Surveillance des forages simulés · Maroc",
        "Alertes": "Priorisation des interventions terrain",
        "Détail pompe": "Télémétrie MQTT & prédiction ML",
        "Modèles": "Arbitrage S3-S5 · champion production",
        "À propos": "Pipeline complet AquaSense AI",
    }
    st.markdown(
        f"""
        <div class="aq-hero">
            <h1>💧 AquaSense AI</h1>
            <p>{subtitles.get(page, "Maintenance prédictive · EHTP MIG S4")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pipeline_banner(pipeline: dict) -> None:
    if pipeline.get("active"):
        badge = '<span class="aq-live">● Pipeline actif</span>'
        detail = (
            f"{pipeline['telemetry_count']:,} msg MQTT · "
            f"{pipeline['predictions_count']:,} inférences · "
            f"~{_fmt_latency_avg(pipeline)} ms · "
            f"{pipeline.get('model', 'modèle')}"
        )
    else:
        badge = '<span class="aq-offline">○ Pipeline inactif</span>'
        detail = "Lancez le consumer et le simulateur MQTT"

    st.markdown(
        f"""
        <div class="aq-pipeline">
            <span class="aq-step">Simulateur</span>
            <span class="aq-arrow">→</span>
            <span class="aq-step">MQTT</span>
            <span class="aq-arrow">→</span>
            <span class="aq-step">Inférence ML</span>
            <span class="aq-arrow">→</span>
            <span class="aq-step">SQLite</span>
            <span class="aq-arrow">→</span>
            <span class="aq-step">Dashboard</span>
            {badge}
        </div>
        <p class="aq-pipeline-detail">{detail}</p>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(df: pd.DataFrame, counts: dict[str, int]) -> None:
    total = len(df) if not df.empty else 50
    if df.empty:
        st.markdown(
            f"""
            <div class="aq-kpi-row">
                <div class="aq-kpi info"><div class="aq-kpi-label">Pompes</div>
                <div class="aq-kpi-value">{total}</div></div>
                <div class="aq-kpi"><div class="aq-kpi-label">MQTT</div>
                <div class="aq-kpi-value">{counts.get('telemetry', 0):,}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.warning(
            "Aucune inférence en base. Lancez dans la venv :\n\n"
            "`python -m src.mqtt_consumer` puis `python -m src.simulator`"
        )
        return

    n_func = int((df["prediction"] == "functional").sum())
    n_repair = int((df["prediction"] == NEEDS_REPAIR).sum())
    n_down = int((df["prediction"] == "non functional").sum())
    risk_pct = round(100 * (n_repair + n_down) / max(total, 1), 1)
    mqtt_n = counts.get("telemetry", 0)

    st.markdown(
        f"""
        <div class="aq-kpi-row">
            <div class="aq-kpi info">
                <div class="aq-kpi-label">Pompes suivies</div>
                <div class="aq-kpi-value">{total}</div>
            </div>
            <div class="aq-kpi ok">
                <div class="aq-kpi-label">Opérationnelles</div>
                <div class="aq-kpi-value">{n_func}</div>
            </div>
            <div class="aq-kpi warn">
                <div class="aq-kpi-label">Maintenance requise</div>
                <div class="aq-kpi-value">{n_repair}</div>
                <div class="aq-kpi-sub">{risk_pct}% à risque</div>
            </div>
            <div class="aq-kpi danger">
                <div class="aq-kpi-label">Hors service</div>
                <div class="aq-kpi-value">{n_down}</div>
            </div>
            <div class="aq-kpi info">
                <div class="aq-kpi-label">Messages MQTT</div>
                <div class="aq-kpi-value">{mqtt_n:,}</div>
                <div class="aq-kpi-sub">télémétrie simulée</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_donut(df: pd.DataFrame) -> None:
    if df.empty:
        return
    counts = df["prediction"].value_counts().reset_index()
    counts.columns = ["prediction", "count"]
    counts["label"] = counts["prediction"].map(STATUS_LABELS).fillna("Inconnu")
    fig = px.pie(
        counts,
        values="count",
        names="label",
        color="prediction",
        color_discrete_map=STATUS_COLORS,
        hole=0.55,
        height=280,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    _plotly_defaults(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_map(df: pd.DataFrame) -> None:
    st.subheader("Carte des forages (Maroc)")
    st.caption(
        "Positions **démo** sur localités rurales marocaines · "
        "profils ML = proxy Pump It Up (Tanzanie) · pas de GPS réel Maroc dans le projet"
    )
    if df.empty or df["latitude"].isna().all():
        st.warning("Carte indisponible sans données de prédiction.")
        return

    plot_df = apply_morocco_display(df.dropna(subset=["latitude", "longitude"]))
    fig = px.scatter_mapbox(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="prediction",
        color_discrete_map=STATUS_COLORS,
        hover_name="pump_id",
        hover_data={
            "region": True,
            "locality": True,
            "confidence": ":.0%",
            "health_index": ":.2f",
            "prediction": False,
            "latitude": False,
            "longitude": False,
        },
        zoom=5.2,
        height=500,
        labels={"prediction": "Statut ML"},
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 31.8, "lon": -7.0},
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="Prédiction ML",
        paper_bgcolor="#F4F9FC",
    )
    st.plotly_chart(fig, use_container_width=True)


def page_overview(df: pd.DataFrame, counts: dict[str, int], pipeline: dict) -> None:
    render_pipeline_banner(pipeline)
    render_kpis(df, counts)
    col_map, col_side = st.columns([2, 1])

    with col_map:
        render_map(df)

    with col_side:
        with _section("donut"):
            st.subheader("Répartition des statuts")
            render_status_donut(df)

        with _section("alerts"):
            st.subheader("Alertes prioritaires")
            alerts = load_alerts(df)
            if alerts.empty:
                st.success("Aucune alerte maintenance pour l'instant.")
            else:
                for _, row in alerts.head(6).iterrows():
                    st.markdown(
                        f"""
                        <div class="aq-alert">
                            <strong>{row['pump_id']}</strong><br>
                            Confiance {row['confidence']:.0%} · Santé capteur {row['health_index']:.2f}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


def page_alerts(df: pd.DataFrame) -> None:
    with _section("alerts-panel"):
        st.subheader("Panel alertes · maintenance prédictive")
        st.caption("Pompes prédites « functional needs repair » par le modèle champion (inférence MQTT).")

        alerts = load_alerts(df)
        if alerts.empty:
            st.info("Lancez le simulateur et le consumer MQTT pour générer des alertes.")
            return

        alerts = alerts.copy()
        alerts["region"] = alerts["pump_id"].map(morocco_display_region)
        display = alerts[
            ["pump_id", "region", "confidence", "health_index", "proba_needs_repair", "latency_ms", "timestamp"]
        ].copy()
        display["confidence"] = display["confidence"].map(lambda v: _fmt_pct(v))
        display["health_index"] = display["health_index"].map(lambda v: _fmt_float(v))
        display["proba_needs_repair"] = display["proba_needs_repair"].map(
            lambda v: _fmt_pct(v) if pd.notna(v) else "N/D"
        )
        display["latency_ms"] = display["latency_ms"].map(
            lambda v: f"{float(v):.0f}" if pd.notna(v) else "N/D"
        )
        display["timestamp"] = pd.to_datetime(display["timestamp"], errors="coerce").dt.strftime(
            "%d/%m/%Y %H:%M"
        )
        display = display.rename(
            columns={
                "pump_id": "Pompe",
                "region": "Région",
                "confidence": "Confiance ML",
                "health_index": "Santé capteur",
                "proba_needs_repair": "Prob. maintenance",
                "latency_ms": "Latence (ms)",
                "timestamp": "Dernière inférence",
            }
        )
        st.dataframe(display, use_container_width=True, hide_index=True)

    with _section("assign"):
        st.subheader("Assigner un technicien")
        if alerts.empty:
            return
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            pump_choice = st.selectbox("Pompe", alerts["pump_id"].tolist(), label_visibility="collapsed")
        with c2:
            tech_name = st.text_input("Technicien", placeholder="Ex. Ahmed B.", label_visibility="collapsed")
        with c3:
            if st.button("Assigner", type="primary", use_container_width=True):
                if tech_name.strip():
                    st.session_state["assignments"][pump_choice] = tech_name.strip()
                    st.success(f"**{pump_choice}** → {tech_name.strip()}")
                else:
                    st.error("Nom requis.")

        if st.session_state["assignments"]:
            for pid, tech in st.session_state["assignments"].items():
                st.write(f"🔧 {pid} → **{tech}**")


def page_detail(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Aucune pompe disponible.")
        return

    pump_id = st.selectbox("Pompe", df["pump_id"].tolist())
    row = df[df["pump_id"] == pump_id].iloc[0]
    pred = row["prediction"]
    label = STATUS_LABELS.get(pred, pred)

    with _section("pump-header"):
        st.subheader(f"{pump_id} · {morocco_display_region(pump_id)}")
        if pred == "functional":
            st.success(f"Statut : {label}")
        elif pred == NEEDS_REPAIR:
            st.warning(f"Statut : {label}")
        elif pred == "non functional":
            st.error(f"Statut : {label}")
        else:
            st.info(f"Statut : {label}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Confiance ML", _fmt_pct(row["confidence"]))
    c2.metric("Santé capteur", _fmt_float(row["health_index"]))
    c3.metric("Latence inférence", _fmt_ms(row["latency_ms"]))
    c4.metric("Messages MQTT", len(telemetry_df(pump_id, limit=500)))

    hist = telemetry_df(pump_id)
    if hist.empty:
        st.warning("Pas encore de télémétrie MQTT pour cette pompe.")
        return

    with _section("telemetry"):
        st.subheader("Télémétrie simulée (MQTT)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist["timestamp"], y=hist["pressure"], name="Pression (bar)",
            line=dict(color=CHART_COLORS[0], width=2), mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=hist["timestamp"], y=hist["flow"], name="Débit (L/min)",
            line=dict(color=CHART_COLORS[2], width=2), mode="lines", yaxis="y2",
        ))
        fig.update_layout(
            height=340,
            yaxis=dict(title="Pression", gridcolor="#E2EEF4"),
            yaxis2=dict(title="Débit", overlaying="y", side="right", gridcolor="#E2EEF4"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(gridcolor="#E2EEF4"),
        )
        _plotly_defaults(fig)
        st.plotly_chart(fig, use_container_width=True)

    fig2 = px.area(
        hist, x="timestamp", y="vibration",
        title="Vibration (g)",
        color_discrete_sequence=[CHART_COLORS[1]],
        height=260,
    )
    fig2.update_traces(line=dict(width=0))
    _plotly_defaults(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    if "scenario" in hist.columns:
        st.caption(f"Scénario simulateur : **{hist['scenario'].iloc[-1]}** · mois={hist['month'].iloc[-1]}")


def page_models() -> None:
    comp = load_model_comparison()
    if comp.empty:
        st.warning("Fichier `sprint_05_final_comparison.csv` introuvable.")
        return

    with _section("models-table"):
        st.subheader("Comparaison modèles S3-S5")
        st.dataframe(comp.sort_values("f1_macro", ascending=False), use_container_width=True, hide_index=True)

    top = comp.sort_values("f1_macro", ascending=False).head(6)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=top["f1_macro"], theta=top["model"],
        fill="toself", name="F1-Macro", line_color=CHART_COLORS[0],
    ))
    fig.add_trace(go.Scatterpolar(
        r=top["recall_needs_repair"], theta=top["model"],
        fill="toself", name="Recall maintenance", line_color=CHART_COLORS[2],
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#D6E8F0"),
            bgcolor="rgba(0,0,0,0)",
        ),
        title="Radar des top 6 modèles",
        height=440,
    )
    _plotly_defaults(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Inférence MQTT (S6)** : `champion_production_v1.joblib`, recall maintenance optimisé. "
        "**Analytics** : `voting_rf_xgb_soft` pour F1-Macro."
    )


def page_about(pipeline: dict) -> None:
    with _section("about-pipeline"):
        st.subheader("Pipeline temps réel : comment ça marche ?")
        st.markdown(
            """
1. **`src/simulator.py`** publie la télémétrie (pression, vibration, débit) sur MQTT
2. **`src/mqtt_consumer.py`** reçoit chaque message, fusionne profil + capteurs, **exécute l'inférence**
3. Résultats stockés dans **`data/mqtt/aquasense.db`** (SQLite)
4. **Ce dashboard** lit SQLite toutes les 10 s (pas de connexion MQTT directe)
            """
        )
        st.metric("Messages MQTT en base", f"{pipeline['telemetry_count']:,}")
        st.metric("Inférences enregistrées", f"{pipeline['predictions_count']:,}")
        st.caption(f"Modèle : `{pipeline.get('model', 'champion_production_v1.joblib')}`")

    st.markdown(
        r"""
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohammed · EHTP MIG S4

**Problème :** maintenance prédictive des forages, contexte **Maroc**.

**Entraînement :** Pump It Up (Tanzanie, proxy structurel).

**Lancer la démo (venv) :**
```powershell
.\.venv\Scripts\Activate.ps1
python -m src.mqtt_consumer
python -m src.simulator
python -m streamlit run dashboard/app.py
```
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="AquaSense AI",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(inject_css(), unsafe_allow_html=True)

    _init_state()
    refresh_data()

    pipeline = st.session_state.get("pipeline", load_pipeline_status())
    df = st.session_state["pumps_df"]
    counts = st.session_state["db_counts"]

    st.sidebar.title("💧 AquaSense AI")
    st.sidebar.caption("Maintenance prédictive · Maroc · EHTP MIG S4")
    page = st.sidebar.radio("Navigation", PAGES)
    st.sidebar.divider()
    if pipeline.get("active"):
        st.sidebar.success("Pipeline MQTT actif")
    else:
        st.sidebar.error("Pipeline inactif")
    st.sidebar.markdown(
        f"**{counts.get('predictions', 0):,}** inférences  \n"
        f"**{counts.get('telemetry', 0):,}** messages MQTT  \n"
        f"~**{_fmt_latency_avg(pipeline)}** ms / inférence"
    )
    st.sidebar.caption("Rafraîchissement auto · 10 s")

    render_hero(page)

    if page == "Vue d'ensemble":
        page_overview(df, counts, pipeline)
    elif page == "Alertes":
        page_alerts(df)
    elif page == "Détail pompe":
        page_detail(df)
    elif page == "Modèles":
        page_models()
    else:
        page_about(pipeline)


if __name__ == "__main__":
    main()
