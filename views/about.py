"""Seite: Über MietCheck – Projekt, USP, Datenquelle, Grenzen."""
import streamlit as st

from views.common import kpi, load_cities, load_metrics, section


def render(loc=None):
    m = load_metrics()

    st.markdown("<div class='hero'><div class='hero-t'>Über MietCheck</div>"
                "<div class='hero-s'>Ein Data-Science-Projekt mit klarem "
                "Alltagsnutzen.</div></div>", unsafe_allow_html=True)

    section("💡 Die Idee")
    st.markdown(
        "**MietCheck** beantwortet die eine Frage, die fast jeden betrifft: "
        "*„Ist meine Miete fair?“* – mit einem datenbasierten Richtwert aus "
        "über 200.000 echten Wohnungsangeboten und einem klaren Urteil "
        "(**Schnäppchen · Fair · Zu teuer**). Bewusst wenige Eingaben, ein "
        "klares Ergebnis – das ist der **USP für Alltagsuser**.")

    section("📚 Steckbrief")
    cities = load_cities()
    k1, k2, k3 = st.columns(3)
    with k1:
        kpi("Trainingsdaten", "202.908", "Wohnungsangebote", "green")
    with k2:
        kpi("Städte-Abdeckung", f"{cities.get('n_cities', 0):,}".replace(",", "."),
            "ganz Deutschland", "blue")
    with k3:
        kpi("Genauigkeit", f"R² {m['test_r2']:.2f}", f"± {m['test_mae']:.0f} €", "yellow")

    section("🗂️ Datenquellen")
    st.markdown(
        "**1. Mietpreise (Modelltraining)**\n"
        "- *Apartment rental offers in Germany* (Immoscout24) via Kaggle\n"
        "- Kaggle-ID: `corrieaar/apartment-rental-offers-in-germany`\n"
        "- Zielgröße: Kaltmiete (`baseRent`)\n\n"
        "**2. Städteverzeichnis (Standortauswahl)**\n"
        "- **OpenPLZ API** (`openplzapi.org`) – offene API, live abgefragt\n"
        "- alle deutschen Gemeinden inkl. Landkreis & Bundesland\n"
        "- jede Stadt wird ihrem Landkreis (= Trainingsregion) zugeordnet\n\n"
        "**Prozessmodell:** QUA³CK (IU – Data Analytics & Big Data)")

    section("🛠️ Technik")
    st.markdown(
        "Python · pandas · scikit-learn (Gradient Boosting) · Plotly · Streamlit. "
        "Der komplette Data-Science-Workflow steht im Notebook "
        "`notebooks/01_mietcheck_qua3ck.ipynb`, der Code in `src/`.")

    section("⚠️ Grenzen")
    st.markdown(
        "MietCheck liefert einen **datenbasierten Richtwert**, keinen amtlichen "
        "Mietspiegel und keine Rechtsberatung. Sehr seltene Orte oder extreme "
        "Wohnungen werden weniger genau getroffen; der Datensatz ist ein "
        "Zeit-Snapshot.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.caption("MietCheck · Uni-Projekt Data Analytics & Big Data · "
               "QUA³CK-Prozessmodell · Datenbasis: Immoscout24 (Kaggle)")
