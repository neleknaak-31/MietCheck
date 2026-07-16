"""Seite: Modell & Qualität – Transparenz, Kennzahlen, QUA³CK (A + C + K)."""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from views.common import C, kpi, load_metrics, pred_sample, section


def render(loc=None):
    m = load_metrics()

    st.markdown("<div class='hero'><div class='hero-t'>Modell & Qualität</div>"
                "<div class='hero-s'>Wie gut schätzt MietCheck – und wie kommt "
                "die Zahl zustande?</div></div>", unsafe_allow_html=True)

    section("🎯 Güte des Modells", m["best_model"])
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi("Ø Fehler (MAE)", f"± {m['test_mae']:.0f} €", "je Schätzung", "green")
    with k2:
        kpi("Bestimmtheit R²", f"{m['test_r2']:.3f}", "erklärte Varianz", "blue")
    with k3:
        kpi("MAPE", f"{m['test_mape']:.1f} %", "prozentualer Fehler", "yellow")
    with k4:
        kpi("Trainingsdaten", f"{m['n_train']:,}".replace(",", "."),
            "echte Angebote", "muted")

    # --- Modellvergleich (QUA³CK-A + C) ------------------------------------
    section("⚖️ Modellvergleich", "5-fache Kreuzvalidierung · niedriger = besser")
    cv = {k: v["cv_mae"] for k, v in m["cv_results"].items()}
    names, vals, best = list(cv.keys()), list(cv.values()), m["best_model"]
    fig = px.bar(x=vals, y=names, orientation="h", text=[f"{v:.1f} €" for v in vals],
                 labels={"x": "CV-MAE (€)", "y": ""})
    fig.update_traces(marker_color=[C["green"] if n == best else C["faint"]
                                    for n in names], textposition="outside")
    fig.update_layout(height=240, xaxis_title="Mittlerer Fehler (€)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(f"Gewählt: **{best}** – der niedrigste Kreuzvalidierungs-Fehler.")

    # --- Merkmalswichtigkeit (interaktiv) ----------------------------------
    section("🧠 Was treibt den Preis?", "Permutations-Wichtigkeit · interaktiv")
    imp = m.get("importances", [])
    if imp:
        imp = sorted(imp, key=lambda x: x["value"])
        fig = px.bar(x=[i["value"] for i in imp], y=[i["feature"] for i in imp],
                     orientation="h", text=[f"{i['value']:.0f} €" for i in imp],
                     labels={"x": "Einfluss auf den Fehler (€)", "y": ""})
        fig.update_traces(marker_color=C["purple"], textposition="outside")
        fig.update_layout(height=60 + 30 * len(imp),
                          xaxis_title="Ø Preis-Einfluss (€, je größer desto wichtiger)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Wohnfläche, Stadt und Bundesland bestimmen die Miete am stärksten.")

    # --- Vorhersage vs. Realität (interaktiv) ------------------------------
    section("📉 Vorhersage vs. Realität", "Testfälle · Punkte nahe der Linie = gut")
    s = pred_sample()
    lim = float(np.percentile(s["real"], 99))
    fig = go.Figure()
    fig.add_scatter(x=s["real"], y=s["pred"], mode="markers",
                    marker=dict(color=C["green"], size=5, opacity=0.35),
                    name="Wohnungen",
                    hovertemplate="tatsächlich %{x:.0f} €<br>geschätzt %{y:.0f} €<extra></extra>")
    fig.add_scatter(x=[0, lim], y=[0, lim], mode="lines",
                    line=dict(color=C["muted"], dash="dash"), name="perfekt")
    fig.update_layout(height=420, xaxis_title="tatsächliche Kaltmiete (€)",
                      yaxis_title="geschätzte Kaltmiete (€)",
                      xaxis_range=[0, lim], yaxis_range=[0, lim],
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- QUA³CK-Prozess ----------------------------------------------------
    section("🔄 Der Weg dahin: QUA³CK")
    steps = [
        ("Q", "Qualitätsprüfung", "268.850 → 202.908 Angebote; Ausreißer & "
         "Datenfehler entfernt.", C["red"]),
        ("U", "Understanding the Data", "EDA: Verteilungen, Preis/m² je Region, "
         "Korrelationen.", C["yellow"]),
        ("A", "Algorithmenauswahl", "Lineare Regression · Random Forest · "
         "Gradient Boosting.", C["green"]),
        ("A", "Modellentwicklung", "Pipeline: Imputation → Scaling → One-Hot → "
         "Modell.", C["blue"]),
        ("C", "Kreuzvalidierung", "5-fache CV wählt das beste Modell.", C["purple"]),
        ("K", "Wissensextraktion", "Diese App – der USP für Alltagsuser.", C["pink"]),
    ]
    html = "<div class='steps'>"
    for letter, title, desc, col in steps:
        html += (f"<div class='step'><div class='step-b' style='background:{col}'>"
                 f"{letter}</div><div class='step-x'><div class='step-t'>{title}"
                 f"</div><div class='step-d'>{desc}</div></div></div>")
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
