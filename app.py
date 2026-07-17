# ruff: noqa: E501
"""MietCheck Streamlit application.

Run locally with:
    streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.app_logic import evaluate_scenario

ROOT = Path(__file__).resolve().parent
PROFILES_FILE = ROOT / "data" / "app" / "region_profiles.csv"
GREIX_FILE = ROOT / "data" / "app" / "greix_quarterly.csv"
FINAL_REPORT = ROOT / "reports" / "final_model_evaluation.json"
BENCHMARK_REPORT = ROOT / "reports" / "algorithm_benchmark.json"
BUILD_REPORT = ROOT / "reports" / "dataset_build_report.json"
MODEL_META = ROOT / "models" / "zensus_hgb_meta.json"
MODEL_MANIFEST = ROOT / "models" / "model_manifest.json"
MLFLOW_REPORT = ROOT / "reports" / "mlflow_publish.json"

COLORS = {
    "ink": "#132238",
    "green": "#0B6E4F",
    "green_soft": "#DFF3EC",
    "blue": "#2D5BFF",
    "blue_soft": "#E7ECFF",
    "amber": "#D97706",
    "amber_soft": "#FEF3C7",
    "coral": "#E85D3F",
    "grey": "#667085",
    "line": "#D9E0E8",
    "paper": "#FFFFFF",
    "canvas": "#F4F6F3",
}

st.set_page_config(
    page_title="MietCheck · Drei Mietrealitäten",
    page_icon="⌂",
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict, dict, dict, dict, dict, dict]:
    profiles = pd.read_csv(PROFILES_FILE)
    greix = pd.read_csv(GREIX_FILE)
    final = json.loads(FINAL_REPORT.read_text(encoding="utf-8"))
    benchmark = json.loads(BENCHMARK_REPORT.read_text(encoding="utf-8"))
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    model_meta = json.loads(MODEL_META.read_text(encoding="utf-8"))
    model_manifest = json.loads(MODEL_MANIFEST.read_text(encoding="utf-8"))
    mlflow_report = json.loads(MLFLOW_REPORT.read_text(encoding="utf-8"))
    return profiles, greix, final, benchmark, build, model_meta, model_manifest, mlflow_report


def euro(value: float, digits: int = 0) -> str:
    return f"{value:,.{digits}f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def number(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def metric_card(label: str, value: str, detail: str, tone: str = "green") -> None:
    st.markdown(
        f"""
        <div class="metric-card tone-{tone}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rent_reality_chart(scenario: dict) -> go.Figure:
    labels = ["Bestandsanker 2022", f"Angebotsmarkt {scenario['period']}"]
    values = [scenario["stock_monthly"], scenario["asking_monthly"]]
    colors = [COLORS["green"], COLORS["blue"]]
    text = [
        f"{euro(scenario['stock_monthly'])}<br>Modellband ± {euro(scenario['interval_half_width_monthly'])}",
        f"{euro(scenario['asking_monthly'])}<br>Markt-IQR {euro(scenario['market_p25_monthly'])}–{euro(scenario['market_p75_monthly'])}",
    ]
    if scenario["current_cold_rent"] not in (None, 0):
        labels.append("Deine aktuelle Miete")
        values.append(scenario["current_cold_rent"])
        colors.append(COLORS["coral"])
        text.append(euro(scenario["current_cold_rent"]))

    figure = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=text,
            textposition="outside",
            hovertemplate="%{x}<br>%{y:,.0f} € / Monat<extra></extra>",
        )
    )
    figure.update_layout(
        title="Monatliche Nettokaltmiete: drei getrennte Realitäten",
        yaxis_title="€ pro Monat",
        xaxis_title="",
        showlegend=False,
        margin=dict(l=20, r=20, t=55, b=20),
        height=430,
    )
    return style_figure(figure)


def range_chart(scenario: dict) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=[scenario["stock_lower_sqm"], scenario["stock_upper_sqm"]],
            y=["Bestandsanker", "Bestandsanker"],
            mode="lines",
            line=dict(color=COLORS["green"], width=18),
            name="Modellband (empirisch ca. 87 %)",
            hovertemplate="Modellband: %{x:.2f} €/m²<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[scenario["market_p25_sqm"], scenario["market_p75_sqm"]],
            y=["Angebotsmarkt", "Angebotsmarkt"],
            mode="lines",
            line=dict(color=COLORS["blue"], width=18),
            name="GREIX-Markt-IQR",
            hovertemplate="Markt-IQR: %{x:.2f} €/m²<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[scenario["stock_sqm"], scenario["asking_sqm"]],
            y=["Bestandsanker", "Angebotsmarkt"],
            mode="markers",
            marker=dict(size=14, color=[COLORS["ink"], COLORS["ink"]], symbol="diamond"),
            name="Mittel-/Medianwert",
            hovertemplate="%{x:.2f} €/m²<extra></extra>",
        )
    )
    if scenario["current_sqm"] is not None:
        figure.add_vline(
            x=scenario["current_sqm"],
            line_width=3,
            line_dash="dot",
            line_color=COLORS["coral"],
            annotation_text=f"Deine Miete {number(scenario['current_sqm'], 2)} €/m²",
            annotation_position="top",
        )
    figure.update_layout(
        title="Bandbreiten sind nicht dasselbe: Modellunsicherheit vs. Marktstreuung",
        xaxis_title="Nettokaltmiete €/m²",
        yaxis_title="",
        height=330,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", y=-0.25),
    )
    return style_figure(figure)


def market_timeline(greix: pd.DataFrame, region: str) -> go.Figure:
    timeline = greix.loc[greix["region"].eq(region)].copy()
    timeline["date"] = pd.PeriodIndex(timeline["period"], freq="Q").to_timestamp()
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=timeline["date"],
            y=timeline["asking_p75_eur_sqm"],
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=timeline["date"],
            y=timeline["asking_p25_eur_sqm"],
            fill="tonexty",
            fillcolor="rgba(45,91,255,.13)",
            line=dict(width=0),
            name="25.–75. Perzentil",
            hovertemplate="P25: %{y:.2f} €/m²<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=timeline["date"],
            y=timeline["asking_median_eur_sqm"],
            mode="lines",
            line=dict(color=COLORS["blue"], width=3),
            name="Median",
            hovertemplate="%{x|Q%q %Y}<br>%{y:.2f} €/m²<extra></extra>",
        )
    )
    figure.update_layout(
        title=f"{region}: nominale GREIX-Angebotsmiete seit 2012",
        xaxis_title="",
        yaxis_title="€/m²",
        height=470,
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.04, x=0),
    )
    return style_figure(figure)


def regional_scatter(profiles: pd.DataFrame, selected_region: str, scenario: dict) -> go.Figure:
    chart = profiles.copy()
    stock_column = (
        f"stock_2022_age{scenario['building_after_1990']}"
        f"_size{scenario['dwelling_over_65sqm']}_eur_sqm"
    )
    chart["stock"] = chart[stock_column]
    chart["premium"] = chart["asking_median_eur_sqm"] - chart["stock"]
    selected = chart["region"].eq(selected_region)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=chart.loc[~selected, "stock"],
            y=chart.loc[~selected, "asking_median_eur_sqm"],
            mode="markers",
            marker=dict(size=9, color=COLORS["grey"], opacity=0.55),
            text=chart.loc[~selected, "region"],
            name="andere Märkte",
            hovertemplate="%{text}<br>Bestand %{x:.2f}<br>Angebot %{y:.2f} €/m²<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=chart.loc[selected, "stock"],
            y=chart.loc[selected, "asking_median_eur_sqm"],
            mode="markers+text",
            marker=dict(size=16, color=COLORS["coral"]),
            text=chart.loc[selected, "region"],
            textposition="top center",
            name=selected_region,
            hovertemplate="%{text}<br>Bestand %{x:.2f}<br>Angebot %{y:.2f} €/m²<extra></extra>",
        )
    )
    high = max(chart["asking_median_eur_sqm"].max(), chart["stock"].max()) + 1
    figure.add_trace(
        go.Scatter(
            x=[0, high],
            y=[0, high],
            mode="lines",
            line=dict(color=COLORS["line"], dash="dash"),
            name="kein Abstand",
            hoverinfo="skip",
        )
    )
    figure.update_layout(
        title=(
            "37 lokale Märkte: Bestandsanker vs. aktueller Angebotsmedian"
            f"<br><sup>gewählte Zensus-Kategorie: Gebäude "
            f"{'nach 1990' if scenario['building_after_1990'] else 'bis 1990'}, "
            f"Wohnung {'über 65 m²' if scenario['dwelling_over_65sqm'] else 'bis 65 m²'}</sup>"
        ),
        xaxis_title="modellierter Bestandsanker 2022 €/m²",
        yaxis_title="GREIX-Angebotsmedian Q1/2026 €/m²",
        height=520,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return style_figure(figure)


def style_figure(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLORS["ink"]),
        paper_bgcolor=COLORS["paper"],
        plot_bgcolor=COLORS["paper"],
        hoverlabel=dict(bgcolor=COLORS["ink"], font_color="white"),
    )
    figure.update_xaxes(gridcolor="#EBEFF3", zeroline=False)
    figure.update_yaxes(gridcolor="#EBEFF3", zeroline=False)
    return figure


st.markdown(
    f"""
    <style>
    :root {{ --ink:{COLORS["ink"]}; --green:{COLORS["green"]}; --blue:{COLORS["blue"]}; }}
    #MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
    header[data-testid="stHeader"] {{ background:rgba(244,246,243,.88); }}
    [data-testid="stAppViewContainer"] {{ background:{COLORS["canvas"]}; }}
    [data-testid="stSidebar"] {{ background:#101E2D; }}
    [data-testid="stSidebar"] * {{ color:#F8FAFC; }}
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] [role="combobox"] {{
      color:#132238 !important;
    }}
    .block-container {{ max-width:1180px; padding-top:1.4rem; padding-bottom:4rem; }}
    .brand-row {{ display:flex; justify-content:space-between; align-items:center;
      gap:20px; padding:14px 0 20px; border-bottom:1px solid {COLORS["line"]}; }}
    .brand {{ font-size:28px; font-weight:850; letter-spacing:-1px; color:{COLORS["ink"]}; }}
    .brand span {{ color:{COLORS["green"]}; }}
    .brand-sub {{ font-size:12px; color:{COLORS["grey"]}; letter-spacing:.08em;
      text-transform:uppercase; margin-top:2px; }}
    .data-pill {{ background:{COLORS["green_soft"]}; color:{COLORS["green"]};
      border:1px solid #B7E1D3; padding:7px 11px; border-radius:999px;
      font-size:12px; font-weight:750; white-space:nowrap; }}
    .hero {{ background:linear-gradient(125deg,#132238 0%,#174C48 100%); color:white;
      border-radius:22px; padding:34px 38px; margin:24px 0 20px;
      box-shadow:0 18px 45px rgba(19,34,56,.13); }}
    .hero-kicker {{ color:#8EE0C1; font-weight:750; font-size:12px; letter-spacing:.1em;
      text-transform:uppercase; }}
    .hero h1 {{ color:white; font-size:38px; line-height:1.08; letter-spacing:-1.4px;
      margin:9px 0 10px; max-width:820px; }}
    .hero p {{ color:#DCE6E4; max-width:850px; font-size:16px; line-height:1.55; margin:0; }}
    .metric-card {{ background:white; border:1px solid {COLORS["line"]}; border-radius:16px;
      padding:18px 18px 16px; min-height:145px; box-shadow:0 5px 18px rgba(19,34,56,.05); }}
    .metric-card.tone-green {{ border-top:4px solid {COLORS["green"]}; }}
    .metric-card.tone-blue {{ border-top:4px solid {COLORS["blue"]}; }}
    .metric-card.tone-coral {{ border-top:4px solid {COLORS["coral"]}; }}
    .metric-label {{ color:{COLORS["grey"]}; text-transform:uppercase; letter-spacing:.08em;
      font-size:10px; font-weight:800; }}
    .metric-value {{ color:{COLORS["ink"]}; font-size:27px; font-weight:850;
      letter-spacing:-.6px; margin:8px 0 6px; }}
    .metric-detail {{ color:{COLORS["grey"]}; font-size:12px; line-height:1.4; }}
    .callout {{ border-radius:16px; padding:20px 22px; margin:16px 0;
      border:1px solid #B7E1D3; background:{COLORS["green_soft"]}; color:{COLORS["ink"]}; }}
    .callout strong {{ color:{COLORS["green"]}; font-size:19px; }}
    .callout.warn {{ background:{COLORS["amber_soft"]}; border-color:#F7D784; }}
    .callout.warn strong {{ color:{COLORS["amber"]}; }}
    .section-title {{ color:{COLORS["ink"]}; font-size:22px; font-weight:850;
      letter-spacing:-.4px; margin:28px 0 3px; }}
    .section-sub {{ color:{COLORS["grey"]}; font-size:13px; margin-bottom:14px; }}
    .source-box {{ background:white; border:1px solid {COLORS["line"]}; border-radius:14px;
      padding:16px 18px; color:{COLORS["grey"]}; font-size:13px; line-height:1.55; }}
    [data-testid="stMetric"] {{ background:white; border:1px solid {COLORS["line"]};
      padding:14px; border-radius:14px; }}
    [data-baseweb="tab-list"] {{ gap:8px; }}
    [data-baseweb="tab"] {{ background:white; border:1px solid {COLORS["line"]};
      border-radius:999px; padding:8px 16px; }}
    [aria-selected="true"] {{ background:{COLORS["ink"]} !important; color:white !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

(
    profiles,
    greix,
    final,
    benchmark,
    build,
    model_meta,
    model_manifest,
    mlflow_report,
) = load_data()
regions = sorted(profiles["region"].tolist())

with st.sidebar:
    st.markdown("## Dein Szenario")
    st.caption("Eingaben bleiben im Browser und werden nicht gespeichert.")
    default_region = regions.index("Berlin") if "Berlin" in regions else 0
    region = st.selectbox("GREIX-Markt", regions, index=default_region)
    area_sqm = st.slider("Wohnfläche", 20, 180, 70, 5, format="%d m²")
    construction_year = st.slider("Baujahr", 1900, 2026, 1985)
    st.divider()
    current_cold_rent = st.number_input(
        "Deine aktuelle Nettokaltmiete (optional)",
        min_value=0,
        max_value=10_000,
        value=850,
        step=25,
        help="0 wählen, wenn keine persönliche Miete verglichen werden soll.",
    )
    net_income = st.number_input(
        "Haushaltsnettoeinkommen (optional)",
        min_value=0,
        max_value=50_000,
        value=3_200,
        step=100,
        help="Nur für eine deskriptive Mietbelastungsquote; keine Finanzberatung.",
    )
    category_text = (
        ("nach 1990", "über 65 m²")
        if construction_year > 1990 and area_sqm > 65
        else (
            "nach 1990" if construction_year > 1990 else "bis 1990",
            "über 65 m²" if area_sqm > 65 else "bis 65 m²",
        )
    )
    st.caption(f"Zensus-Kategorie: Gebäude {category_text[0]} · Wohnung {category_text[1]}")
    st.divider()
    st.markdown("**Abdeckung**")
    st.caption("37 GREIX-Städte/-Kreise · Zensus 100-m-Gitter · Datenstand Q1/2026")

profile = profiles.loc[profiles["region"].eq(region)].iloc[0]
scenario = evaluate_scenario(
    profile,
    area_sqm=area_sqm,
    construction_year=construction_year,
    current_cold_rent=None if current_cold_rent == 0 else current_cold_rent,
    net_income=None if net_income == 0 else net_income,
)

st.markdown(
    f"""
    <div class="brand-row">
      <div><div class="brand">Miet<span>Check</span></div>
      <div class="brand-sub">Bestand · Angebot · persönliche Miete</div></div>
      <div class="data-pill">Aktueller Markt: {scenario["period"]}</div>
    </div>
    <div class="hero">
      <div class="hero-kicker">Drei Mietrealitäten, eine klare Entscheidungshilfe</div>
      <h1>Was kostet Wohnen in {region} – und was würde ein Umzug verändern?</h1>
      <p>MietCheck verbindet einen lokalen ML-Bestandsanker mit dem aktuellen GREIX-Angebotsmarkt
      und deiner persönlichen Situation. Keine Scheingenauigkeit: Zeitbezug, Streuung und
      Modellgrenzen stehen direkt am Ergebnis.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

overview_tab, market_tab, method_tab = st.tabs(
    ["Dein Mietbild", "Marktverlauf", "Methodik & Quellen"]
)

with overview_tab:
    st.markdown('<div class="section-title">Die drei Vergleichswerte</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Nicht vermischen: persönliche Vertragsmiete, modellierter Bestand und aktueller Angebotsmarkt.</div>',
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    with columns[0]:
        if scenario["current_sqm"] is None:
            metric_card(
                "Deine Miete", "nicht angegeben", "Optional links in der Sidebar ergänzen.", "coral"
            )
        else:
            burden = (
                "ohne Einkommensangabe"
                if scenario["current_burden"] is None
                else f"{number(scenario['current_burden'] * 100, 1)} % vom Haushaltsnetto"
            )
            metric_card(
                "Deine aktuelle Miete",
                f"{number(scenario['current_sqm'], 2)} €/m²",
                f"{euro(scenario['current_cold_rent'])} pro Monat · {burden}",
                "coral",
            )
    with columns[1]:
        metric_card(
            "Bestandsanker · 15.05.2022",
            f"{number(scenario['stock_sqm'], 2)} €/m²",
            f"{euro(scenario['stock_monthly'])}/Monat · Modellband ± {number(scenario['interval_half_width_sqm'], 2)} €/m²",
            "green",
        )
    with columns[2]:
        metric_card(
            f"Angebotsmarkt · {scenario['period']}",
            f"{number(scenario['asking_sqm'], 2)} €/m²",
            f"{euro(scenario['asking_monthly'])}/Monat · IQR {number(scenario['market_p25_sqm'], 2)}–{number(scenario['market_p75_sqm'], 2)} €/m²",
            "blue",
        )

    premium_text = (
        f"Der aktuelle Angebotsmedian liegt bei dieser Wohnungsgröße rund "
        f"{euro(abs(scenario['moving_premium_monthly']))} pro Monat "
        f"{'über' if scenario['moving_premium_monthly'] >= 0 else 'unter'} dem lokalen Bestandsanker."
    )
    st.markdown(
        f"""
        <div class="callout"><strong>Umzugsaufschlag: {number(scenario["moving_premium_pct"], 0)} %</strong><br>
        {premium_text} Das ist ein deskriptiver Marktvergleich – kein amtlicher Mietspiegel und keine Rechtsaussage.</div>
        """,
        unsafe_allow_html=True,
    )
    if scenario["personal_move_delta_monthly"] is not None:
        delta = scenario["personal_move_delta_monthly"]
        direction = "mehr" if delta >= 0 else "weniger"
        st.info(
            f"Persönliches Umzugsszenario: Zum aktuellen Angebotsmedian wären es "
            f"{euro(abs(delta))} pro Monat {direction} als deine heutige Nettokaltmiete."
        )

    st.plotly_chart(rent_reality_chart(scenario), width="stretch")
    st.plotly_chart(range_chart(scenario), width="stretch")

    st.markdown('<div class="section-title">Budgetwirkung</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Die Quote ist eine deskriptive Orientierung und keine individuelle Finanzempfehlung.</div>',
        unsafe_allow_html=True,
    )
    if scenario["asking_burden"] is None:
        st.info("Haushaltsnettoeinkommen ergänzen, um die Mietbelastung zu vergleichen.")
    else:
        budget_columns = st.columns(3)
        with budget_columns[0]:
            st.metric(
                "Belastung am Angebotsmedian",
                f"{number(scenario['asking_burden'] * 100, 1)} %",
                scenario["asking_burden_label"],
                delta_color="off",
            )
        with budget_columns[1]:
            if scenario["current_burden"] is not None:
                st.metric(
                    "Deine aktuelle Belastung",
                    f"{number(scenario['current_burden'] * 100, 1)} %",
                    scenario["current_burden_label"],
                    delta_color="off",
                )
            else:
                st.metric("Deine aktuelle Belastung", "–", "keine Miete angegeben")
        with budget_columns[2]:
            st.metric(
                "GREIX-Jahresänderung",
                f"{scenario['index_yoy_pct']:+.1f} %".replace(".", ","),
                f"Quartal {scenario['index_qoq_pct']:+.1f} %".replace(".", ","),
                delta_color="off",
            )

    st.markdown(
        """
        <div class="source-box"><strong>So liest du das Ergebnis:</strong><br>
        Der Bestandsanker ist eine ML-Schätzung für das lokale Zensus-Niveau 2022. Das grüne Band
        ist Modellunsicherheit mit empirisch rund 87 % Abdeckung auf unbekannten Raumblöcken.
        Der GREIX-Wert ist der Median aktueller Inserate; das blaue Band zeigt deren 25.–75. Perzentil.
        Unterschiede bei Ausstattung, Energieeffizienz, Etage und konkreter Mikrolage sind nicht modelliert.</div>
        """,
        unsafe_allow_html=True,
    )

with market_tab:
    st.markdown('<div class="section-title">Aktueller Angebotsmarkt</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Nominale Quartalswerte des GREIX-Mietpreisindex – keine hochgerechneten Portal-Scrapes.</div>',
        unsafe_allow_html=True,
    )
    market_columns = st.columns(4)
    with market_columns[0]:
        st.metric("Median Q1/2026", f"{number(scenario['asking_sqm'], 2)} €/m²")
    with market_columns[1]:
        st.metric("25. Perzentil", f"{number(scenario['market_p25_sqm'], 2)} €/m²")
    with market_columns[2]:
        st.metric("75. Perzentil", f"{number(scenario['market_p75_sqm'], 2)} €/m²")
    with market_columns[3]:
        st.metric(
            "Index ggü. Vorjahr",
            f"{scenario['index_yoy_pct']:+.1f} %".replace(".", ","),
        )
    st.plotly_chart(market_timeline(greix, region), width="stretch")
    st.plotly_chart(regional_scatter(profiles, region, scenario), width="stretch")

    comparison = profiles.copy()
    selected_stock_column = (
        f"stock_2022_age{scenario['building_after_1990']}"
        f"_size{scenario['dwelling_over_65sqm']}_eur_sqm"
    )
    comparison["Bestandsanker 2022 €/m²"] = comparison[selected_stock_column]
    comparison["Angebotsmedian Q1/2026 €/m²"] = comparison["asking_median_eur_sqm"]
    comparison["Umzugsaufschlag %"] = (
        comparison["Angebotsmedian Q1/2026 €/m²"] / comparison["Bestandsanker 2022 €/m²"] - 1
    ) * 100
    st.markdown("#### Märkte mit dem größten relativen Abstand")
    st.dataframe(
        comparison[
            [
                "region",
                "Bestandsanker 2022 €/m²",
                "Angebotsmedian Q1/2026 €/m²",
                "Umzugsaufschlag %",
            ]
        ]
        .sort_values("Umzugsaufschlag %", ascending=False)
        .head(10)
        .style.format(
            {
                "Bestandsanker 2022 €/m²": "{:.2f}",
                "Angebotsmedian Q1/2026 €/m²": "{:.2f}",
                "Umzugsaufschlag %": "{:.1f}",
            }
        ),
        hide_index=True,
        width="stretch",
    )

with method_tab:
    st.markdown(
        '<div class="section-title">Was steckt hinter der Zahl?</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-sub">Große offene Daten, räumlich ehrliche Evaluation und sichtbare Grenzen.</div>',
        unsafe_allow_html=True,
    )
    method_columns = st.columns(4)
    with method_columns[0]:
        st.metric("Modellzeilen", f"{number(build['rows'] / 1_000_000, 2)} Mio.")
    with method_columns[1]:
        st.metric(
            "100-m-Gitter",
            f"{number(build['unique_grid_cells'] / 1_000_000, 2)} Mio.",
        )
    with method_columns[2]:
        st.metric(
            "Finaler Test-MAE",
            f"{number(final['test']['point_metrics']['mae'], 3)} €/m²",
        )
    with method_columns[3]:
        st.metric(
            "räumliche Coverage",
            f"{number(final['test']['category_specific_90_percent_interval']['coverage'] * 100, 1)} %",
        )

    st.markdown("#### Reproduzierbare Pipeline")
    pipeline_columns = st.columns(5)
    steps = [
        ("1", "Download", "offizielle URLs + SHA-256"),
        ("2", "Build", "2,06 Mio. validierte Joins"),
        ("3", "Spatial CV", "25-km-Gruppen statt Zufallssplit"),
        ("4", "Kalibrierung", "separate Regionen für Intervalle"),
        ("5", "App", "37 GREIX-Märkte · Q1/2026"),
    ]
    for column, (step, title, detail) in zip(pipeline_columns, steps, strict=True):
        with column:
            st.markdown(f"**{step}. {title}**")
            st.caption(detail)

    st.markdown("#### MLOps, Modell-Lineage und reproduzierbares Serving")
    mlops_columns = st.columns(4)
    with mlops_columns[0]:
        st.metric("MLflow-Runs", len(mlflow_report["runs"]))
    with mlops_columns[1]:
        st.metric("Registry-Version", mlflow_report["registry"]["version"])
    with mlops_columns[2]:
        st.metric("Modell-Alias", mlflow_report["registry"]["alias"])
    with mlops_columns[3]:
        st.metric("automatisierte Tests", "33")

    with st.expander("Wie Training, Registry, CI und App zusammenhängen", expanded=False):
        st.markdown(
            f"""
            - **Experiment-Tracking:** Algorithmusvergleich, HGB-Tuning und finale
              räumliche Evaluation sind als drei MLflow-Runs mit Parametern,
              Metriken und Artefakten dokumentiert.
            - **Model Registry:** Das finale Modell ist als
              `{mlflow_report["registry"]["model_name"]}` Version
              `{mlflow_report["registry"]["version"]}` registriert. Die geprüfte
              Version trägt den Alias `@{mlflow_report["registry"]["alias"]}`.
            - **Lineage:** Modellversion `{model_manifest["model_version"]}` besitzt
              den SHA-256-Fingerabdruck
              `{model_manifest["files"]["zensus_hgb.joblib"]["sha256"][:16]}…`.
              Metadaten und finaler Evaluationsbericht werden ebenfalls per Hash
              geprüft.
            - **Serving:** Ein versionierter Batch-Schritt erzeugt mit dem als
              Registry-Version dokumentierten Modellartefakt die 37 regionalen
              Zensus-Profile. Die App kombiniert diese geprüften ML-Vorhersagen
              interaktiv mit GREIX und persönlichen Eingaben. Sie trainiert nicht
              im Browser und benötigt keine Rohdaten.
            - **Qualitätsgates:** GitHub Actions führt Lint, Formatierung, 33 Tests,
              Modell-/Segment-Gates und einen Docker-Build aus. Der Container besitzt
              einen eigenen Health-Endpunkt.

            Die lokale MLflow-Datenbank ist kein Bestandteil der öffentlichen App.
            Der reproduzierbare Publishing-Schritt und seine Run-/Registry-IDs
            liegen im GitHub-Repository.
            """
        )

    ranking = pd.DataFrame(benchmark["ranking_by_mean_mae"]).sort_values("mean_mae")
    model_figure = go.Figure(
        go.Bar(
            x=ranking["mean_mae"],
            y=ranking["model"],
            orientation="h",
            error_x=dict(type="data", array=ranking["std_mae"]),
            marker_color=[
                COLORS["green"] if model == "hist_gradient_boosting" else COLORS["grey"]
                for model in ranking["model"]
            ],
            hovertemplate="%{y}<br>MAE %{x:.3f} €/m²<extra></extra>",
        )
    )
    model_figure.update_layout(
        title="Fünf Modellfamilien auf identischen räumlichen Folds",
        xaxis_title="mittlerer MAE €/m²",
        yaxis_title="",
        height=390,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(style_figure(model_figure), width="stretch")

    importance = pd.DataFrame(
        final["permutation_importance_on_calibration_sample"]["results"]
    ).head(10)
    importance_figure = go.Figure(
        go.Bar(
            x=importance["mae_increase_mean"].sort_values(),
            y=importance.sort_values("mae_increase_mean")["feature"],
            orientation="h",
            marker_color=COLORS["blue"],
            hovertemplate="%{y}<br>MAE-Anstieg %{x:.3f}<extra></extra>",
        )
    )
    importance_figure.update_layout(
        title="Prädiktiver Beitrag auf separaten Kalibrierungsdaten",
        xaxis_title="MAE-Anstieg nach Permutation",
        yaxis_title="",
        height=430,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(style_figure(importance_figure), width="stretch")

    st.markdown(
        f"""
        <div class="callout warn"><strong>Warum zeigt die App ca. 87 % statt 90 %?</strong><br>
        Das Split-Conformal-Band wurde mit nominal 90 % auf separaten Regionen kalibriert,
        erreicht auf den finalen unbekannten Raumblöcken aber
        {number(final["test"]["category_specific_90_percent_interval"]["coverage"] * 100, 1)} %.
        Räumlicher Verteilungswechsel verletzt perfekte Austauschbarkeit. MietCheck zeigt die
        gemessene Coverage und behauptet keine Garantie.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Quellen und Lizenzen", expanded=True):
        st.markdown(
            """
            - [Zensus 2022 – offene 100-m-Gitterdaten](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Zensus2022/_publikationen.html) · Statistische Ämter des Bundes und der Länder · Datenlizenz Deutschland – Namensnennung 2.0
            - [GREIX-Mietpreisindex](https://www.kielinstitut.de/de/institut/forschungszentren/makrooekonomie/makrofinanzen/mietpreisindex/) · Kiel Institut für Weltwirtschaft auf Basis der VALUE Marktdatenbank
            - Regionszentren: © OpenStreetMap-Mitwirkende · Nominatim · ODbL
            - Code und eigene Verarbeitung: MietCheck-Projekt, siehe GitHub-Repository und `docs/`.
            """
        )
    with st.expander("Was die App ausdrücklich nicht ist"):
        st.markdown(
            """
            - kein amtlicher Mietspiegel und keine Rechtsberatung,
            - keine Prüfung der Mietpreisbremse,
            - keine Bewertung einer konkreten Wohnung oder Adresse,
            - keine Aussage über Warmmiete, Nebenkosten oder Energieverbrauch,
            - keine Finanz-, Kredit- oder behördliche Entscheidungshilfe.

            Der lokale Anker nutzt einen Regionsmittelpunkt und aggregierte Zensuskontexte. Ausstattung,
            Etage, Zustand, Energieeffizienz und Mikrolage fehlen. Neue Gebäude weisen im Test höhere
            Fehler auf. Details stehen in `docs/MODEL_CARD.md`.
            """
        )

st.markdown(
    """
    <div style="margin-top:34px;padding-top:18px;border-top:1px solid #D9E0E8;
    color:#667085;font-size:12px;line-height:1.5">
    MietCheck · Data Analytics & Big Data · Zensus-Stichtag 15.05.2022 · GREIX Q1/2026 ·
    transparent, reproduzierbar, ohne personenbezogene Speicherung
    </div>
    """,
    unsafe_allow_html=True,
)
