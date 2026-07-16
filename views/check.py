"""Seite: MietCheck – der Kern-Predictor (QUA³CK-K / Anwendung)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import CONDITION_LABELS, FLAT_LABELS, QUALITY_LABELS
from views.common import (C, eur, kpi, load_clean, load_meta, load_metrics,
                          load_model, section, warm_rent)

AMENITIES = [("balcony", "Balkon / Terrasse"), ("hasKitchen", "Einbauküche"),
             ("cellar", "Keller"), ("lift", "Aufzug"),
             ("garden", "Garten"), ("newlyConst", "Neubau")]


def _label(mapping, k):
    return mapping.get(k, k)


def _gauge(asking, fair):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=asking,
        number={"suffix": " €", "font": {"color": C["text"], "size": 28}},
        delta={"reference": fair, "suffix": " €",
               "increasing": {"color": C["red"]}, "decreasing": {"color": C["green"]}},
        gauge={"axis": {"range": [fair * 0.6, fair * 1.4], "tickcolor": C["muted"]},
               "bar": {"color": C["text"], "thickness": 0.18}, "bgcolor": C["card"],
               "borderwidth": 0,
               "steps": [{"range": [fair * 0.6, fair * 0.9], "color": C["green"]},
                         {"range": [fair * 0.9, fair * 1.1], "color": C["yellow"]},
                         {"range": [fair * 1.1, fair * 1.4], "color": C["red"]}],
               "threshold": {"line": {"color": C["blue"], "width": 3},
                             "thickness": 0.85, "value": fair}}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=10))
    return fig


def render(loc):
    meta, model, metrics = load_meta(), load_model(), load_metrics()
    bl, city, regio2 = loc["regio1"], loc["city"], loc["regio2"]
    mae = metrics["test_mae"]

    st.markdown(
        "<div class='hero'><div class='hero-t'>Zahle ich zu viel Miete?</div>"
        "<div class='hero-s'>Faire Kaltmiete in Sekunden – aus über 200.000 "
        "echten Wohnungsangeboten.</div></div>", unsafe_allow_html=True)

    basis = ("📍 <b>" + city + "</b>, " + bl.replace("_", "-")
             + (" · Landkreis-Daten" if loc["matched"] else " · Bundesland-Schätzung"))
    st.markdown(f"<div class='locbar'>{basis} &nbsp;·&nbsp; "
                "<span class='locbar-x'>Standort links in der Sidebar ändern</span></div>",
                unsafe_allow_html=True)

    with st.form("check"):
        section("🏡 Eckdaten")
        c3, c4, c5 = st.columns(3)
        living = c3.number_input("Wohnfläche (m²)", 15, 300, 70, step=5)
        rooms = c4.number_input("Zimmer", 1.0, 8.0, 2.0, step=0.5)
        year = c5.number_input("Baujahr", 1900, 2025,
                               int(meta["defaults"]["yearConstructed"]))
        cond = st.selectbox("Zustand", meta["conditions"],
                            format_func=lambda k: _label(CONDITION_LABELS, k))

        section("✨ Ausstattung")
        a1, a2, a3 = st.columns(3)
        vals = {}
        vals["balcony"] = a1.checkbox("Balkon / Terrasse", True)
        vals["hasKitchen"] = a2.checkbox("Einbauküche", True)
        vals["cellar"] = a3.checkbox("Keller", False)
        a4, a5, a6 = st.columns(3)
        vals["lift"] = a4.checkbox("Aufzug", False)
        vals["garden"] = a5.checkbox("Garten", False)
        vals["newlyConst"] = a6.checkbox("Neubau", False)

        with st.expander("Weitere Angaben (optional)"):
            qk = meta["qualities"]
            qual = st.selectbox("Ausstattungsqualität", qk,
                                index=qk.index(meta["defaults"]["interiorQual"])
                                if meta["defaults"]["interiorQual"] in qk else 0,
                                format_func=lambda k: _label(QUALITY_LABELS, k))
            fk = meta["flat_types"]
            flat = st.selectbox("Wohnungstyp", fk,
                                index=fk.index(meta["defaults"]["typeOfFlat"])
                                if meta["defaults"]["typeOfFlat"] in fk else 0,
                                format_func=lambda k: _label(FLAT_LABELS, k))

        section("💶 Vergleich (optional)")
        asking = st.number_input("Deine angebotene / aktuelle Kaltmiete (€)",
                                 0, 6000, 0, step=10,
                                 help="0 lassen, wenn du nur den fairen Wert schätzen willst.")
        go_btn = st.form_submit_button("Miete prüfen  🔍", use_container_width=True)

    if not go_btn:
        return

    row = {"livingSpace": living, "noRooms": rooms, "yearConstructed": year,
           "regio1": bl, "regio2": regio2, "condition": cond,
           "interiorQual": qual, "typeOfFlat": flat, **vals}
    fair = float(model.predict(pd.DataFrame([row]))[0])
    fair_sqm = fair / living
    warm = warm_rent(fair, living)
    low, high = max(0, fair - mae), fair + mae

    # --- Kernergebnis ------------------------------------------------------
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("💡 Ergebnis")
    k1, k2, k3 = st.columns(3)
    with k1:
        kpi("Faire Kaltmiete", eur(fair), f"Spanne {eur(low)}–{eur(high)}", "green")
    with k2:
        kpi("≈ Warmmiete", eur(warm), "inkl. Nebenkosten", "blue")
    with k3:
        kpi("Preis pro m²", eur(fair_sqm, 2), f"{living:.0f} m² · {city}", "muted")

    # --- Regionsvergleich --------------------------------------------------
    df = load_clean()
    sub = df[df["regio2"] == regio2] if loc["matched"] else df[df["regio1"] == bl]
    if len(sub) < 20:
        sub = df[df["regio1"] == bl]
    med = sub["eur_sqm"].median()
    dpct = (fair_sqm - med) / med * 100
    where = (regio2.replace("_Kreis", " (Kreis)").replace("_", " ")
             if loc["matched"] else bl.replace("_", "-"))
    if dpct <= -5:
        st.markdown(f"<div class='note n-good'>Diese Wohnung ist mit "
                    f"<b>{eur(fair_sqm,2)}/m²</b> rund <b>{abs(dpct):.0f}% günstiger</b> "
                    f"als der Schnitt in {where} ({eur(med,2)}/m²).</div>",
                    unsafe_allow_html=True)
    elif dpct < 5:
        st.markdown(f"<div class='note n-ok'>Mit <b>{eur(fair_sqm,2)}/m²</b> liegt sie "
                    f"<b>im Schnitt</b> von {where} ({eur(med,2)}/m²).</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='note n-warn'>Mit <b>{eur(fair_sqm,2)}/m²</b> liegt sie "
                    f"<b>{dpct:.0f}% über</b> dem Schnitt in {where} ({eur(med,2)}/m²) "
                    f"– hochpreisige Lage/Ausstattung.</div>", unsafe_allow_html=True)

    # --- Urteil (wenn Angebot angegeben) -----------------------------------
    if asking > 0:
        section("⚖️ Dein Angebot im Check")
        st.plotly_chart(_gauge(asking, fair), use_container_width=True,
                        config={"displayModeBar": False})
        diff, pct = asking - fair, (asking - fair) / fair * 100
        if pct <= -10:
            st.markdown(f"<div class='verdict v-good'>🎉 <b>Schnäppchen!</b> "
                        f"{abs(pct):.0f}% ({eur(abs(diff))}) <b>unter</b> fair.</div>",
                        unsafe_allow_html=True)
        elif pct < 10:
            st.markdown(f"<div class='verdict v-ok'>👍 <b>Fair.</b> Abweichung "
                        f"{pct:+.0f}%.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='verdict v-bad'>⚠️ <b>Zu teuer.</b> {pct:.0f}% "
                        f"({eur(diff)}) <b>über</b> fair.</div>", unsafe_allow_html=True)

    # --- Warum dieser Preis? (Ausstattungsbeitrag) -------------------------
    contribs = []
    for key, label in AMENITIES:
        if vals[key]:
            alt = dict(row); alt[key] = False
            p = float(model.predict(pd.DataFrame([alt]))[0])
            contribs.append((label, fair - p))
    if contribs:
        section("🔍 Warum dieser Preis?", "Wertbeitrag deiner Ausstattung")
        contribs.sort(key=lambda x: x[1])
        fig = go.Figure(go.Bar(
            x=[c[1] for c in contribs], y=[c[0] for c in contribs],
            orientation="h", marker_color=C["green"],
            text=[eur(c[1]) for c in contribs], textposition="outside"))
        fig.update_layout(height=60 + 34 * len(contribs), xaxis_title="€ / Monat",
                          margin=dict(l=10, r=30, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- Leistbarkeit ------------------------------------------------------
    section("🧮 Leistbarkeit", "Faustregel: max. 30 % des Netto-Einkommens")
    need = warm / 0.30
    c1, c2 = st.columns(2)
    with c1:
        kpi("Empf. Netto-Einkommen", eur(need), "für diese Wohnung", "yellow")
    with c2:
        kpi("Warmmiete / Jahr", eur(warm * 12), "Gesamtkosten p. a.", "muted")
    st.caption("Genauere Rechnung? → Seite **🧮 Budget** in der unteren Navigation.")

    with st.expander("ℹ️ Wie zuverlässig ist die Schätzung?"):
        st.markdown(
            f"- Modell: **{metrics['best_model']}** · Ø Fehler **± {mae:.0f} €** (MAE)\n"
            f"- Erklärte Varianz **R² = {metrics['test_r2']:.2f}** · "
            f"trainiert auf **{metrics['n_train']:,} Angeboten**".replace(",", ".") +
            "\n\nRichtwert auf Basis historischer Angebote – kein amtlicher Mietspiegel.")
