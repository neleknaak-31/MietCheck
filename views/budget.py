"""Seite: Budget – Leistbarkeits-Rechner (Alltags-USP)."""
import plotly.express as px
import streamlit as st

from views.common import (C, eur, kpi, kreis_stats, load_clean, load_meta,
                          section)

# Kuratierte Großstädte fürs Vergleichs-Ranking (regio2-Schlüssel)
BIG_CITIES = ["München", "Frankfurt_am_Main", "Stuttgart", "Hamburg", "Berlin",
              "Köln", "Düsseldorf", "Bremen", "Hannover", "Dortmund", "Leipzig",
              "Dresden", "Essen"]


def render(loc):
    meta = load_meta()
    factor = meta.get("warm", {}).get("factor", 1.31)
    df = load_clean()

    st.markdown("<div class='hero'><div class='hero-t'>Budget-Rechner</div>"
                "<div class='hero-s'>Wie viel Miete – und wie viel Wohnung – "
                "kannst du dir leisten?</div></div>", unsafe_allow_html=True)

    section("💰 Deine Eckdaten")
    c1, c2 = st.columns(2)
    income = c1.number_input("Netto-Haushaltseinkommen (€/Monat)", 500, 20000,
                             3000, step=100)
    share = c2.slider("Anteil fürs Wohnen (%)", 20, 45, 30,
                      help="Faustregel: max. 30 % des Nettoeinkommens für die Warmmiete.")

    warm_budget = income * share / 100
    cold_budget = warm_budget / factor

    section("🎯 Dein Miet-Budget")
    k1, k2, k3 = st.columns(3)
    with k1:
        kpi("Leistbare Warmmiete", eur(warm_budget), f"{share}% vom Netto", "green")
    with k2:
        kpi("davon Kaltmiete", eur(cold_budget), "ohne Nebenkosten", "blue")
    with k3:
        kpi("pro Jahr", eur(warm_budget * 12), "Wohnkosten p. a.", "muted")

    # --- Fläche in der gewählten Stadt -------------------------------------
    regio2 = loc["regio2"]
    sub = df[df["regio2"] == regio2] if loc["matched"] else df[df["regio1"] == loc["regio1"]]
    if len(sub) < 20:
        sub = df[df["regio1"] == loc["regio1"]]
    city_sqm = sub["eur_sqm"].median()
    afford = cold_budget / city_sqm
    where = (regio2.replace("_Kreis", " (Kreis)").replace("_", " ")
             if loc["matched"] else loc["regio1"].replace("_", "-"))

    section("📐 Wie groß in deiner Region?", where)
    c1, c2 = st.columns(2)
    with c1:
        kpi("Leistbare Wohnfläche", f"{afford:.0f} m²",
            f"in {where}", "green" if afford >= 60 else "yellow")
    with c2:
        kpi("Mietniveau dort", eur(city_sqm, 2) + "/m²", "Median Kaltmiete", "muted")

    # --- Vergleich: leistbare Fläche in Großstädten ------------------------
    section("🏙️ Was bekommst du wo?", "Leistbare Wohnfläche für dein Budget")
    ks = kreis_stats().set_index("regio2")
    rows = []
    for c in BIG_CITIES:
        if c in ks.index:
            sqm = cold_budget / ks.loc[c, "eur_sqm"]
            rows.append((c.replace("_", " "), sqm, ks.loc[c, "eur_sqm"]))
    if rows:
        rows.sort(key=lambda x: x[1])
        fig = px.bar(x=[r[1] for r in rows], y=[r[0] for r in rows],
                     orientation="h", text=[f"{r[1]:.0f} m²" for r in rows],
                     labels={"x": "leistbare Wohnfläche (m²)", "y": ""})
        colors = [C["red"] if r[1] < 50 else C["yellow"] if r[1] < 75 else C["green"]
                  for r in rows]
        fig.update_traces(marker_color=colors, textposition="outside")
        fig.update_layout(height=420, xaxis_title="leistbare Wohnfläche (m²)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("Berechnet aus deiner leistbaren Kaltmiete geteilt durch die "
                   "mediane €/m²-Miete der Stadt.")

    st.info("💡 Die 30-%-Regel ist eine grobe Orientierung. Banken rechnen bei "
            "Finanzierungen oft mit 30–40 % – je nach Fixkosten und Haushaltsgröße.")
