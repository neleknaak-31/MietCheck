# 🏠 MietCheck – Zahle ich zu viel Miete?

Ein Data-Science-Prototyp für das Modul **Data Analytics & Big Data** (IU, 4. Semester),
umgesetzt entlang des **QUA³CK-Prozessmodells**.

> **USP für Alltagsuser:** Jeder wohnt zur Miete oder sucht eine Wohnung. MietCheck
> beantwortet in Sekunden die eine Frage, die alle stellen: *„Ist diese Miete fair?"* –
> mit einem datenbasierten Richtwert aus **über 200.000 echten Wohnungsangeboten** und
> einem klaren Urteil: **Schnäppchen · Fair · Zu teuer.**

---

## 🎯 Die Idee in einem Satz

Nutzer geben ein paar einfache Eckdaten ein (Ort, Größe, Zimmer, Baujahr, Ausstattung),
MietCheck schätzt die **faire Kaltmiete** und vergleicht sie mit dem tatsächlichen Angebot.
**Bewusst wenige Eingaben, ein klares Ergebnis** – damit niemand den Überblick verliert.

---

## 📊 Datenbasis

| | |
|---|---|
| Mietpreise (Training) | *Apartment rental offers in Germany* (Immoscout24), Kaggle |
| Umfang roh | 268.850 Angebote × 49 Merkmale |
| Nach Qualitätsprüfung | **202.908 Angebote** (24,5 % Ausreißer/Fehler entfernt) |
| Zielgröße | Kaltmiete (`baseRent`) in € |
| Städteverzeichnis | **OpenPLZ API** (offen, live) – **10.786 Städte/Gemeinden**, ganz Deutschland |
| Zuordnung | jede Stadt → Landkreis (= `regio2`, 87 % direkt getroffen) |

---

## 🔄 Umsetzung entlang QUA³CK

| Phase | Was passiert | Datei |
|-------|--------------|-------|
| **Q** – Qualitätsprüfung | Unplausible Werte & Ausreißer entfernen (z. B. 5 €/m² oder 9,9 Mio. € Miete), Plausibilitätsgrenzen | `src/data_prep.py` |
| **U** – Understanding the Data | EDA: Verteilungen, Preis/m² je Bundesland, Korrelationen, Fläche↔Miete | `src/data_prep.py`, `notebooks/02_understanding_the_data.ipynb` |
| **A** – Algorithmenauswahl | Vergleich: Lineare Regression · Random Forest · Gradient Boosting | `src/train.py` |
| **Modellentwicklung** | sklearn-Pipeline: Imputation → Scaling → One-Hot-Encoding → Modell | `src/train.py` |
| **C** – Kreuzvalidierung | 5-fache CV, faire Modellauswahl | `src/train.py` |
| **K** – Wissensextraktion | Merkmalswichtigkeit + **App als Deployment** | `app.py`, `reports/` |

---

## 🏆 Ergebnisse

Bestes Modell: **Gradient Boosting** (Auswahl per 5-facher Kreuzvalidierung)

| Modell | CV-MAE |
|--------|--------|
| Lineare Regression | 120,5 € |
| Random Forest | 102,7 € |
| **Gradient Boosting** | **90,2 €** |

**Auf dem Testset (40.582 Wohnungen):**
- Mittlerer absoluter Fehler (MAE): **± 89,7 €**
- Bestimmtheitsmaß **R² = 0,898**
- Mittlerer prozentualer Fehler (MAPE): **13,7 %**

Wichtigste Preistreiber (Permutations-Wichtigkeit): **Wohnfläche → Stadt → Bundesland.**

---

## 🚀 Loslegen

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. (Nur einmal) Daten von Kaggle laden – braucht ~/.kaggle/kaggle.json
kaggle datasets download -d corrieaar/apartment-rental-offers-in-germany --unzip -p data

# 3. Datenphase + Training (erzeugt Modell, Grafiken, Metadaten)
python3 src/data_prep.py
python3 src/train.py

# 4. App starten  👉  http://localhost:8501
streamlit run app.py
```

Schnellstart als Skript: `./start.command` (macOS).

---

## 📁 Projektstruktur

```
MietCheck/
├── app.py                  # Multipage-Controller: Theme + Bottom-Navigation
├── views/                  # die 5 Seiten der App
│   ├── check.py            #   🏠 Predictor + Warmmiete/Spanne/Wertbeitrag/Urteil
│   ├── explorer.py         #   🗺️ Markt – Deutschland-Karte, Ranking, Zimmer-Analyse
│   ├── budget.py           #   🧮 Leistbarkeits-Rechner
│   ├── insights.py         #   📈 Modell & Qualität – Kennzahlen, QUA³CK
│   ├── about.py            #   ℹ️ Über – Idee, Datenquellen, Grenzen
│   └── common.py           #   Theme, Lader, KPI-Karten, Logo, Aggregate
├── assets/                 # Logo (SVG: logo.svg + logo_mark.svg)
├── .streamlit/config.toml  # helles Theme
├── src/
│   ├── config.py           # Pfade, Merkmale, Grenzwerte (Single Source of Truth)
│   ├── data_prep.py        # QUA³CK Q + U : Qualitätsprüfung & EDA
│   ├── train.py            # QUA³CK A + C : Modellvergleich & Kreuzvalidierung
│   └── fetch_cities.py     # holt ALLE dt. Städte via OpenPLZ API → cities_de.json
├── notebooks/              # ausführbare Analyse (für die Abgabe)
│   ├── 00_gesamtueberblick_qua3ck.ipynb   # alle Phasen kompakt
│   ├── 01_qualitaetspruefung.ipynb        # Q
│   ├── 02_understanding_the_data.ipynb    # U
│   ├── 03_algorithmenauswahl.ipynb        # A
│   ├── 04_modellentwicklung.ipynb         # Modellentwicklung
│   ├── 05_kreuzvalidierung.ipynb          # C
│   └── 06_wissensextraktion.ipynb         # K
├── data/                   # Rohdaten + bereinigter Datensatz
├── models/                 # Trainiertes Modell + Metadaten
├── reports/                # EDA-Grafiken, Kennzahlen
└── requirements.txt
```

### Die App (5 Seiten, Bottom-Navigation, eigenes Logo)

| Seite | Inhalt |
|---|---|
| 🏠 **Check** | faire Kaltmiete **+ Warmmiete + Preisspanne**, Regionsvergleich, **„Warum dieser Preis?"** (Wertbeitrag der Ausstattung), Tacho-Urteil, Einkommens-Empfehlung |
| 🗺️ **Markt** | **Deutschland-Mietkarte** (Choropleth), günstigstes/teuerstes Land, teuerste Städte, Miete nach Zimmerzahl, Preisverteilung, **bundesweites Städte-Ranking (durchsuchbar)** |
| 🧮 **Budget** | Leistbarkeits-Rechner: Einkommen → leistbare Warm-/Kaltmiete + Wohnfläche, Städtevergleich „was bekomme ich wo?" |
| 📈 **Modell** | Genauigkeit, Modellvergleich (CV), Merkmalswichtigkeit, QUA³CK-Ablauf |
| ℹ️ **Über** | Idee/USP, beide Datenquellen, Technik, Grenzen |

Standortauswahl (alle 10.786 Städte) liegt global in der **Sidebar** und speist alle Seiten.
**Helles, massentaugliches Design · alle Diagramme interaktiv (Plotly, mit Hover-Tooltips).**

---

## ⚠️ Hinweis

Die Schätzung ist ein datenbasierter **Richtwert** auf Basis historischer Angebote,
keine Miet- oder Rechtsberatung und kein amtlicher Mietspiegel.
