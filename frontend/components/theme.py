"""Shared visual theme and algorithm colors for the Streamlit dashboard."""

import streamlit as st


ALGORITHM_COLORS = {
    "Greedy": "#64748B",
    "Random Feasible": "#F59E0B",
    "ACO": "#2563EB",
}


THEME_TOKENS = {
    "Light": {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "plotly": "plotly_white",
        "penalty_bg": "#FFFBEB",
        "penalty_border": "#F59E0B",
        "penalty_badge_bg": "#FEF3C7",
        "penalty_badge_text": "#B45309",
        "ok_badge_bg": "#D1FAE5",
        "ok_badge_text": "#047857",
    },
    "Dark": {
        "background": "#0B1120",
        "surface": "#111827",
        "surface_alt": "#1E293B",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "#334155",
        "plotly": "plotly_dark",
        "penalty_bg": "rgba(245, 158, 11, 0.14)",
        "penalty_border": "#F59E0B",
        "penalty_badge_bg": "rgba(245, 158, 11, 0.24)",
        "penalty_badge_text": "#FCD34D",
        "ok_badge_bg": "rgba(16, 185, 129, 0.22)",
        "ok_badge_text": "#6EE7B7",
    },
}


def theme_tokens(mode: str) -> dict[str, str]:
    """Return visual tokens for the selected mode."""
    return THEME_TOKENS.get(mode, THEME_TOKENS["Light"])


def apply_theme(mode: str) -> None:
    """Apply a session-selectable light or dark theme with CSS variables."""
    tokens = theme_tokens(mode)
    st.markdown(
        f"""
        <style>
        :root {{
            --examant-bg: {tokens['background']};
            --examant-surface: {tokens['surface']};
            --examant-surface-alt: {tokens['surface_alt']};
            --examant-text: {tokens['text']};
            --examant-muted: {tokens['muted']};
            --examant-border: {tokens['border']};
        }}
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {{
            background-color: var(--examant-bg);
            color: var(--examant-text);
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-color: var(--examant-surface);
        }}
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: var(--examant-text);
        }}
        [data-testid="stMetric"],
        [data-testid="stExpander"],
        [data-testid="stDataFrame"] {{
            background-color: var(--examant-surface);
            border: 1px solid var(--examant-border);
            border-radius: 12px;
        }}
        [data-testid="stMetric"] {{
            padding: 1rem 1.1rem;
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] > div,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p {{
            color: var(--examant-text) !important;
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] > div {{
            font-size: 1.55rem !important;
            line-height: 1.25 !important;
        }}
        [data-testid="stMetricLabel"] p {{
            font-size: 0.82rem !important;
            line-height: 1.35 !important;
            margin-bottom: 0.35rem !important;
        }}
        [data-testid="stDownloadButton"] button,
        button[kind="secondary"] {{
            background: var(--examant-surface) !important;
            color: var(--examant-text) !important;
            border-color: var(--examant-border) !important;
        }}
        [data-testid="stDownloadButton"] button p,
        button[kind="secondary"] p {{
            color: var(--examant-text) !important;
        }}
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-testid="stNumberInput"] input {{
            background: var(--examant-surface-alt) !important;
            color: var(--examant-text) !important;
            border-color: var(--examant-border) !important;
        }}
        code {{
            background: var(--examant-surface-alt) !important;
            color: var(--examant-text) !important;
        }}
        .examant-table-wrap {{
            max-height: 370px;
            overflow: auto;
            margin: 10px 0 18px;
            border: 1px solid var(--examant-border);
            border-radius: 12px;
            background: var(--examant-surface);
        }}
        .examant-table {{
            width: 100%;
            border-collapse: collapse;
            color: var(--examant-text);
            font-size: 0.9rem;
        }}
        .examant-table th {{
            position: sticky;
            top: 0;
            z-index: 1;
            padding: 10px 12px;
            text-align: left;
            background: var(--examant-surface-alt);
            border-bottom: 1px solid var(--examant-border);
        }}
        .examant-table td {{
            padding: 9px 12px;
            border-bottom: 1px solid var(--examant-border);
            white-space: nowrap;
        }}
        .examant-table tr:last-child td {{
            border-bottom: 0;
        }}
        .winner-card {{
            min-height: 126px;
            padding: 18px;
            border-radius: 14px;
            background: var(--examant-surface);
            border: 1px solid var(--examant-border);
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
        }}
        .winner-card .eyebrow {{
            color: var(--examant-muted);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .winner-card .winner {{
            color: var(--examant-text);
            font-size: 1.25rem;
            font-weight: 800;
            line-height: 1.3;
            margin: 6px 0 4px;
        }}
        .winner-card .value {{
            color: var(--examant-muted);
            font-size: 0.92rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
