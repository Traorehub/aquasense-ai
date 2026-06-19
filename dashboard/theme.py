"""Thème visuel AquaSense AI — eau, Maroc, maintenance prédictive."""

from __future__ import annotations

THEME = {
    "primary": "#0D3B66",
    "secondary": "#3E92CC",
    "accent": "#5BC0BE",
    "light": "#F4F9FC",
    "card": "#FFFFFF",
    "sand": "#C4A77D",
    "text_muted": "#5C7A8A",
}

STATUS_COLORS = {
    "functional": "#1A936F",
    "functional needs repair": "#F4A261",
    "non functional": "#C1121F",
    "inconnu": "#94A3B8",
}

CHART_COLORS = ["#0D3B66", "#3E92CC", "#5BC0BE", "#1A936F", "#F4A261", "#C4A77D"]

PLOTLY_LAYOUT = dict(
    font=dict(family="Segoe UI, sans-serif", color=THEME["primary"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=CHART_COLORS,
    margin=dict(l=24, r=24, t=48, b=24),
)


def inject_css() -> str:
    t = THEME
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', 'Segoe UI', sans-serif;
    }}

    .block-container {{
        padding-top: 1.2rem;
        max-width: 1400px;
    }}

    .aq-hero {{
        background: linear-gradient(135deg, {t['primary']} 0%, {t['secondary']} 55%, {t['accent']} 100%);
        border-radius: 16px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(13, 59, 102, 0.18);
    }}
    .aq-hero h1 {{
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    .aq-hero p {{
        margin: 0.4rem 0 0;
        opacity: 0.92;
        font-size: 0.95rem;
    }}

    .aq-pipeline {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        background: {t['card']};
        border: 1px solid #D6E8F0;
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(13, 59, 102, 0.06);
    }}
    .aq-step {{
        background: {t['light']};
        color: {t['primary']};
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #C5DFEB;
    }}
    .aq-arrow {{ color: {t['secondary']}; font-weight: 700; }}
    .aq-pipeline-detail {{
        color: {t['text_muted']};
        font-size: 0.82rem;
        margin: -0.4rem 0 1rem 0.2rem;
    }}
    .aq-live {{
        background: #D8F3E5;
        color: #0F6B4A;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-left: auto;
    }}
    .aq-offline {{
        background: #FDE8E8;
        color: #9B1C1C;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-left: auto;
    }}

    .aq-kpi-row {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
        margin-bottom: 1rem;
    }}
    @media (max-width: 1100px) {{
        .aq-kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .aq-kpi {{
        background: {t['card']};
        border-radius: 12px;
        padding: 1rem 1.1rem;
        border-left: 4px solid {t['secondary']};
        box-shadow: 0 2px 12px rgba(13, 59, 102, 0.07);
    }}
    .aq-kpi.ok {{ border-left-color: {STATUS_COLORS['functional']}; }}
    .aq-kpi.warn {{ border-left-color: {STATUS_COLORS['functional needs repair']}; }}
    .aq-kpi.danger {{ border-left-color: {STATUS_COLORS['non functional']}; }}
    .aq-kpi.info {{ border-left-color: {t['accent']}; }}
    .aq-kpi-label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {t['text_muted']};
        font-weight: 600;
    }}
    .aq-kpi-value {{
        font-size: 1.65rem;
        font-weight: 700;
        color: {t['primary']};
        line-height: 1.2;
        margin-top: 0.2rem;
    }}
    .aq-kpi-sub {{
        font-size: 0.75rem;
        color: {t['text_muted']};
        margin-top: 0.15rem;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: #D6E8F0 !important;
        border-radius: 14px !important;
        background: {t['card']};
        box-shadow: 0 2px 14px rgba(13, 59, 102, 0.06);
        padding: 0.25rem 0.5rem 0.5rem;
    }}

    .aq-alert {{
        background: #FFF8F0;
        border-left: 4px solid {STATUS_COLORS['functional needs repair']};
        border-radius: 8px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.5rem;
        font-size: 0.88rem;
        color: {t['primary']};
    }}

    [data-testid="stSidebar"] {{
        background-color: {t['light']};
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        background-color: {t['light']};
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: {t['primary']};
    }}
    [data-testid="stSidebar"] .stRadio label {{
        color: {t['primary']} !important;
        font-weight: 500;
    }}
    [data-testid="stSidebar"] .stRadio label p {{
        color: {t['primary']} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: #C5DFEB;
    }}

    div[data-testid="stMetric"] {{
        background: {t['card']};
        border-radius: 12px;
        padding: 0.75rem;
        border: 1px solid #D6E8F0;
    }}
</style>
"""
