"""
Gemeinsame Bausteine für alle Seiten:
Farbpalette, gecachte Datenlader, Plotly-Dark-Theme und kleine UI-Helfer.
"""
import json

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from joblib import load

from src.config import (CLEAN_PARQUET, DATA_DIR, META_FILE, MODEL_FILE,
                        REPORT_DIR, ROOT, TARGET)

CITIES_FILE = DATA_DIR / "cities_de.json"
GEOJSON_FILE = DATA_DIR / "bundeslaender.geojson"
UNKNOWN_REGION = "__unbekannt__"   # nicht im Training -> Modell fällt auf Bundesland zurück

# Logo (Icon) inline – für die Topbar
LOGO_MARK = """<svg width="34" height="34" viewBox="0 0 48 48" fill="none">
<defs><linearGradient id="tlg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#059669"/></linearGradient></defs>
<rect x="1" y="1" width="46" height="46" rx="13" fill="url(#tlg)"/>
<path d="M24 11 L37 22" stroke="#0d1117" stroke-width="3.2" stroke-linecap="round"/>
<path d="M24 11 L11 22" stroke="#0d1117" stroke-width="3.2" stroke-linecap="round"/>
<rect x="14.5" y="22" width="19" height="16.5" rx="2.5" fill="#0d1117"/>
<path d="M18.5 30.5 l3.4 3.4 L29 26.5" stroke="#34d399" stroke-width="3.2"
stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>"""

# --- Farbpalette (helles, massentaugliches Theme) ---------------------------
C = {
    "bg": "#f5f7fa", "card": "#ffffff", "card2": "#f1f5f9",
    "border": "#e2e8f0", "text": "#0f172a", "muted": "#64748b",
    "faint": "#94a3b8",
    "green": "#10b981", "blue": "#2563eb", "yellow": "#d97706",
    "red": "#dc2626", "pink": "#db2777", "purple": "#7c3aed",
}


# --- Gecachte Lader ---------------------------------------------------------
@st.cache_resource
def load_model():
    return load(MODEL_FILE)


@st.cache_data
def load_meta():
    return json.loads(META_FILE.read_text())


@st.cache_data
def load_metrics():
    return json.loads((REPORT_DIR / "metrics.json").read_text())


@st.cache_data
def load_cities():
    """Alle deutschen Städte (OpenPLZ). Fallback: Trainings-Regionen aus meta."""
    if CITIES_FILE.exists():
        return json.loads(CITIES_FILE.read_text())
    meta = load_meta()
    cbl = {bl: [{"label": c.replace("_", " "), "regio2": c}
                for c in meta["cities_by_bl"].get(bl, [])]
           for bl in meta["bundeslaender"]}
    return {"source": "Trainingsdaten (Kaggle)", "n_cities": 0,
            "match_rate": 100.0, "cities_by_bl": cbl}


@st.cache_data
def load_clean():
    """Bereinigter Datensatz + Preis pro m² (für den Markt-Explorer)."""
    df = pd.read_parquet(CLEAN_PARQUET)
    df["eur_sqm"] = df[TARGET] / df["livingSpace"]
    return df


@st.cache_data
def load_geojson():
    if GEOJSON_FILE.exists():
        return json.loads(GEOJSON_FILE.read_text())
    return None


@st.cache_data
def region_stats():
    """Kennzahlen je Bundesland (für die Deutschland-Karte)."""
    df = load_clean()
    g = df.groupby("regio1").agg(
        eur_sqm=("eur_sqm", "median"),
        rent=(TARGET, "median"),
        n=(TARGET, "size")).reset_index()
    g["state"] = g["regio1"].str.replace("_", "-")   # -> GeoJSON-Name
    return g


@st.cache_data
def kreis_stats(min_n=30):
    """Kennzahlen je Landkreis/Stadt (für Ranking & Vergleich)."""
    df = load_clean()
    g = df.groupby(["regio1", "regio2"]).agg(
        eur_sqm=("eur_sqm", "median"),
        rent=(TARGET, "median"),
        n=(TARGET, "size")).reset_index()
    return g[g["n"] >= min_n].copy()


@st.cache_data
def pred_sample(n=3000):
    """Stichprobe Vorhersage vs. Realität für einen interaktiven Scatter."""
    from src.config import FEATURES
    df = load_clean().sample(min(n, len(load_clean())), random_state=0)
    model = load_model()
    pred = model.predict(df[FEATURES])
    return pd.DataFrame({"real": df[TARGET].values, "pred": pred,
                         "flaeche": df["livingSpace"].values})


def warm_rent(cold, sqm):
    """Warmmiete = Kaltmiete + geschätzte Nebenkosten (aus meta)."""
    w = load_meta().get("warm", {"nk_per_sqm": 2.35})
    return cold + w["nk_per_sqm"] * sqm


def predict_range(model, row, mae):
    """Punktschätzung + einfaches Intervall (± MAE)."""
    import pandas as _pd
    point = float(model.predict(_pd.DataFrame([row]))[0])
    return max(0, point - mae), point, point + mae


# --- Plotly-Dark-Theme ------------------------------------------------------
def apply_plotly_theme():
    pio.templates["mietcheck"] = go.layout.Template(
        layout=dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C["muted"], size=12,
                      family="-apple-system, Segoe UI, sans-serif"),
            xaxis=dict(gridcolor=C["border"], zerolinecolor=C["border"]),
            yaxis=dict(gridcolor=C["border"], zerolinecolor=C["border"]),
            colorway=[C["green"], C["blue"], C["pink"], C["yellow"],
                      C["purple"], C["red"]],
            margin=dict(l=10, r=10, t=40, b=10),
            hoverlabel=dict(bgcolor=C["card"], bordercolor=C["border"],
                            font_color=C["text"], font_size=12),
        )
    )
    pio.templates.default = "mietcheck"


# --- UI-Helfer --------------------------------------------------------------
def section(title, sub=None):
    st.markdown(
        f"<div class='sec'><span class='sec-t'>{title}</span>"
        + (f"<span class='sec-s'>{sub}</span>" if sub else "")
        + "</div>", unsafe_allow_html=True)


def kpi(label, value, sub="", color="text"):
    st.markdown(
        f"""<div class='kpi'>
              <div class='kpi-l'>{label}</div>
              <div class='kpi-v' style='color:{C[color]}'>{value}</div>
              <div class='kpi-s'>{sub}</div>
            </div>""", unsafe_allow_html=True)


def eur(x, dec=0):
    """Deutsche Zahlenformatierung: 1.234 € bzw. 12,34 €."""
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{s} €"


def render_sidebar():
    """Globale Sidebar: Standort (alle deutschen Städte) + Datenbasis.

    Rückgabe: dict mit regio1, city, regio2 (fürs Modell), matched (bool).
    """
    cities = load_cities()
    meta, metrics = load_meta(), load_metrics()
    cbl = cities["cities_by_bl"]

    with st.sidebar:
        st.markdown("<div class='sb-h'>📍 Standort</div>", unsafe_allow_html=True)
        bls = sorted(cbl.keys())
        bl = st.selectbox("Bundesland", bls,
                          index=bls.index("Berlin") if "Berlin" in bls else 0,
                          format_func=lambda x: x.replace("_", "-"),
                          key="sb_bl")
        items = cbl.get(bl, [])
        labels = [it["label"] for it in items]
        pick = st.selectbox(f"Stadt / Gemeinde  ({len(labels):,})".replace(",", "."),
                            labels, key="sb_city") if labels else None
        chosen = next((it for it in items if it["label"] == pick), None)
        regio2 = chosen["regio2"] if chosen and chosen["regio2"] else UNKNOWN_REGION
        matched = bool(chosen and chosen["regio2"])

        if matched:
            st.markdown(f"<div class='sb-ok'>✓ Landkreis-Daten: "
                        f"<b>{regio2.replace('_Kreis',' (Kreis)').replace('_',' ')}"
                        f"</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='sb-warn'>ⓘ Kleinere Gemeinde – Schätzung auf "
                        "Bundesland-Ebene.</div>", unsafe_allow_html=True)

        st.markdown("<div class='sb-h' style='margin-top:18px'>📊 Datenbasis</div>",
                    unsafe_allow_html=True)
        n_cities = cities.get("n_cities", 0)
        st.markdown(
            f"<div class='sb-info'>"
            f"<div><b>{metrics['n_train']:,}</b> Wohnungsangebote<br>"
            f"<span>Immoscout24 · Kaggle</span></div>"
            f"<div><b>{n_cities:,}</b> Städte & Gemeinden<br>"
            f"<span>OpenPLZ API (live)</span></div>"
            f"<div><b>± {metrics['test_mae']:.0f} €</b> Modellfehler<br>"
            f"<span>R² {metrics['test_r2']:.2f} · {metrics['best_model']}</span></div>"
            f"</div>".replace(",", "."), unsafe_allow_html=True)

    return {"regio1": bl, "city": pick or bl.replace("_", "-"),
            "regio2": regio2, "matched": matched}
