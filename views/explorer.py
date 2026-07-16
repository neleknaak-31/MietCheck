"""Seite: Markt-Explorer – interaktive regionale Mietanalyse (QUA³CK-U)."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import TARGET
from views.common import (C, eur, kpi, kreis_stats, load_clean, load_geojson,
                          region_stats, section)


def render(loc):
    df = load_clean()
    de_med = df["eur_sqm"].median()

    st.markdown("<div class='hero'><div class='hero-t'>Markt-Explorer</div>"
                "<div class='hero-s'>Wie teuer ist Miete wirklich – in ganz "
                "Deutschland?</div></div>", unsafe_allow_html=True)

    # --- Deutschland-Karte -------------------------------------------------
    section("🗺️ Mietkarte Deutschland", "Median Kaltmiete pro m² je Bundesland")
    rs = region_stats().sort_values("eur_sqm")
    geo = load_geojson()
    if geo is not None:
        fig = px.choropleth(
            rs, geojson=geo, locations="state", featureidkey="properties.name",
            color="eur_sqm", color_continuous_scale="Emrld",
            hover_name="state",
            hover_data={"eur_sqm": ":.2f", "rent": ":.0f", "state": False})
        fig.update_geos(fitbounds="locations", visible=False,
                        bgcolor="rgba(0,0,0,0)")
        fig.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0),
                          coloraxis_colorbar=dict(title="€/m²"),
                          dragmode=False)
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})
    cheap, exp = rs.iloc[0], rs.iloc[-1]
    k1, k2, k3 = st.columns(3)
    with k1:
        kpi("Günstigstes Land", cheap["state"], eur(cheap["eur_sqm"], 2) + "/m²", "green")
    with k2:
        kpi("Teuerstes Land", exp["state"], eur(exp["eur_sqm"], 2) + "/m²", "red")
    with k3:
        kpi("Ø Deutschland", eur(de_med, 2) + "/m²", "Median aller Angebote", "blue")

    # --- Region wählen -----------------------------------------------------
    section("🔎 Region im Detail")
    c1, c2 = st.columns([2, 1])
    bls = sorted(df["regio1"].unique())
    default = loc["regio1"] if loc["regio1"] in bls else bls[0]
    bl = c1.selectbox("Bundesland", bls, index=bls.index(default),
                      format_func=lambda x: x.replace("_", "-"))
    max_sqm = c2.slider("Max. €/m² in Grafiken", 5, 40, 25)
    sub = df[df["regio1"] == bl]
    bl_med = sub["eur_sqm"].median()
    delta = (bl_med - de_med) / de_med * 100

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi("Median €/m²", eur(bl_med, 2), f"{delta:+.0f}% vs. DE",
            "green" if delta <= 0 else "red")
    with k2:
        kpi("Median Miete", eur(sub[TARGET].median()), "typische Wohnung", "blue")
    with k3:
        kpi("Angebote", f"{len(sub):,}".replace(",", "."), "in der Analyse", "muted")
    with k4:
        kpi("Ø Fläche", f"{sub['livingSpace'].median():.0f} m²",
            f"{sub['noRooms'].median():.1f} Zi.", "muted")

    # --- Teuerste Städte im Bundesland -------------------------------------
    section("🏙️ Teuerste Städte", "im gewählten Bundesland · min. 30 Angebote")
    cm = (sub.groupby("regio2")["eur_sqm"].agg(["median", "count"])
          .query("count >= 30").sort_values("median", ascending=False).head(12))
    if len(cm):
        fig = px.bar(cm.reset_index(), x="median", y="regio2", orientation="h",
                     text=cm["median"].round(1))
        fig.update_traces(marker_color=C["green"], textposition="outside",
                          texttemplate="%{text} €")
        fig.update_layout(height=380, yaxis=dict(autorange="reversed", title=""),
                          xaxis_title="€/m²")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- Miete nach Zimmerzahl ---------------------------------------------
    section("🚪 Miete nach Zimmerzahl", bl.replace("_", "-"))
    rr = sub[sub["noRooms"].between(1, 5)].copy()
    rr["Zimmer"] = rr["noRooms"].round().astype(int).astype(str)
    rm = rr.groupby("Zimmer")[TARGET].median().reset_index()
    fig = px.bar(rm, x="Zimmer", y=TARGET, text=rm[TARGET].round(0))
    fig.update_traces(marker_color=C["blue"], textposition="outside",
                      texttemplate="%{text} €")
    fig.update_layout(height=300, yaxis_title="Median Kaltmiete (€)",
                      xaxis_title="Zimmer")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- Verteilung Region vs. DE ------------------------------------------
    section("📈 Preisverteilung", "Region vs. ganz Deutschland")
    d1 = df[df["eur_sqm"] <= max_sqm]
    d2 = sub[sub["eur_sqm"] <= max_sqm]
    fig = go.Figure()
    fig.add_histogram(x=d1["eur_sqm"], histnorm="probability density",
                      name="Deutschland", marker_color=C["muted"], opacity=0.55, nbinsx=40)
    fig.add_histogram(x=d2["eur_sqm"], histnorm="probability density",
                      name=bl.replace("_", "-"), marker_color=C["green"],
                      opacity=0.75, nbinsx=40)
    fig.add_vline(x=bl_med, line_dash="dash", line_color=C["green"])
    fig.add_vline(x=de_med, line_dash="dash", line_color=C["muted"])
    fig.update_layout(barmode="overlay", height=320, xaxis_title="€/m²",
                      yaxis_title="Dichte", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- Bundesweites Städte-Ranking (durchsuchbar) ------------------------
    section("🏆 Städte-Ranking Deutschland", "alle Landkreise/Städte · durchsuchbar")
    ks = kreis_stats().copy()
    ks["Stadt / Landkreis"] = ks["regio2"].str.replace("_Kreis", " (Kreis)").str.replace("_", " ")
    ks["Bundesland"] = ks["regio1"].str.replace("_", "-")
    c1, c2 = st.columns([2, 1])
    q = c1.text_input("🔎 Stadt suchen", "", placeholder="z. B. München, Leipzig …")
    order = c2.radio("Sortierung", ["Teuerste zuerst", "Günstigste zuerst"],
                     horizontal=False)
    view = ks[ks["Stadt / Landkreis"].str.contains(q, case=False, na=False)] if q else ks
    view = view.sort_values("eur_sqm", ascending=(order == "Günstigste zuerst"))
    view = view.assign(**{
        "€/m²": view["eur_sqm"].round(2),
        "Median-Miete (€)": view["rent"].round(0).astype(int),
        "Angebote": view["n"],
    })[["Stadt / Landkreis", "Bundesland", "€/m²", "Median-Miete (€)", "Angebote"]]
    st.dataframe(view, use_container_width=True, hide_index=True, height=380)
    st.caption(f"{len(view):,} Regionen".replace(",", ".") +
               " · Datenbasis: Immoscout24-Angebote")
