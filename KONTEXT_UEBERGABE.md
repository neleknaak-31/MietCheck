# 📦 MietCheck – Kontext & Übergabe

**Für:** die Weiterarbeit am Projekt
**Projekt:** MietCheck – „Zahle ich zu viel Miete?"
**Modul:** Data Analytics & Big Data (IU, 4. Semester)
**Methodik:** QUA³CK-Prozessmodell
**Stand:** funktionsfähiger Prototyp, End-to-End getestet

---

## 1. Worum geht es? (der USP)

Miete betrifft **jeden**. MietCheck beantwortet in Sekunden die Alltagsfrage
*„Ist diese Miete fair?"*: Man gibt ein paar einfache Eckdaten einer Wohnung ein
(Ort, Größe, Zimmer, Baujahr, Ausstattung) und bekommt

1. die geschätzte **faire Kaltmiete** (€ und €/m²), und
2. ein klares **Urteil**: 🎉 Schnäppchen · 👍 Fair · ⚠️ Zu teuer.

Bewusst **wenige Eingabefelder** und **ein klares Ergebnis** – damit auch Laien
nicht überfordert werden. Das ist der Kern des USP.

---

## 2. Datenbasis

| | |
|---|---|
| Quelle | *Apartment rental offers in Germany* (Immoscout24), Kaggle |
| Kaggle-ID | `corrieaar/apartment-rental-offers-in-germany` |
| Roh | 268.850 Angebote × 49 Merkmale (Datei `data/immo_data.csv`, 272 MB) |
| Nach Bereinigung | **202.908 Angebote** (`data/immo_clean.parquet`, 1,9 MB) |
| Zielgröße | Kaltmiete `baseRent` (€) |
| Abdeckung Training | alle 16 Bundesländer, 407 Landkreise |
| Städteverzeichnis | **OpenPLZ API** (offen, live): **10.786 Städte/Gemeinden** ganz Deutschlands |

**Zweite Datenquelle – Städte per offener Web-API:** Für die Standort-Sidebar
werden **alle deutschen Städte** von der **OpenPLZ API** (`openplzapi.org`, kein
Key nötig) geladen. Jede Stadt wird automatisch ihrem **Landkreis** zugeordnet –
also der Ebene, auf der das Modell trainiert ist (87 % direkt getroffen; kleinere
Gemeinden ohne eigene Trainingsdaten fallen sauber auf die Bundesland-Schätzung
zurück). Das Ergebnis liegt fertig in `data/cities_de.json` – **die App braucht
dafür kein Internet.** Neu ziehen mit: `python3 src/fetch_cities.py`.

> ⚠️ **Wichtig:** Die 272-MB-Rohdatei `data/immo_data.csv` ist aus dem
> E-Mail-ZIP **entfernt** (zu groß). Sie ist **nicht nötig**, um die App zu starten
> oder das Modell zu benutzen – der bereinigte Datensatz und das trainierte Modell
> liegen bei. Nur wer die Datenphase (`data_prep.py`) **neu** rechnen will, lädt sie
> mit einem Befehl nach (siehe Abschnitt 5).

---

## 3. Was ist fertig?

- ✅ **Echte Daten** heruntergeladen, bereinigt (Qualitätsprüfung), exploriert (EDA)
- ✅ **Modell trainiert & ausgewählt** per 5-facher Kreuzvalidierung
- ✅ **Streamlit-App** läuft (getestet, HTTP 200)
- ✅ **Notebook** läuft komplett durch (mit gerenderten Grafiken)
- ✅ **6 EDA-/Ergebnis-Grafiken** in `reports/`

**Ergebnis des besten Modells (Gradient Boosting):**

| Kennzahl | Wert |
|---|---|
| Mittlerer absoluter Fehler (MAE) | **± 89,7 €** |
| Bestimmtheitsmaß R² | **0,898** |
| Mittlerer prozentualer Fehler (MAPE) | **13,7 %** |

Modellvergleich (CV-MAE): Lineare Regression 120,5 € · Random Forest 102,7 € ·
**Gradient Boosting 90,2 €** ← gewählt.

Wichtigste Preistreiber: **Wohnfläche → Stadt → Bundesland.**

---

## 4. Projektstruktur

```
MietCheck/
├── app.py                          # Multipage-Controller: Theme + Bottom-Navigation
├── views/                          # die 5 Seiten der App
│   ├── check.py                    #   🏠 Predictor + Warmmiete/Spanne/Wertbeitrag
│   ├── explorer.py                 #   🗺️ Markt: Deutschland-Karte, Ranking, Zimmer
│   ├── budget.py                   #   🧮 Leistbarkeits-Rechner
│   ├── insights.py                 #   📈 Modell & Qualität + QUA³CK
│   ├── about.py                    #   ℹ️ Über das Projekt
│   └── common.py                   #   Theme, Lader, KPI-Karten, Logo, Aggregate
├── assets/                         # Logo (logo.svg + logo_mark.svg)
├── data/bundeslaender.geojson      # Grenzen für die Deutschland-Karte
├── .streamlit/config.toml          # helles Theme
├── KONTEXT_UEBERGABE.md            # ← diese Datei
├── README.md                       # Kurzüberblick + Startanleitung
├── requirements.txt                # Python-Abhängigkeiten
├── start.command                   # Doppelklick-Start (macOS)
├── src/
│   ├── config.py                   # Pfade, Merkmale, Grenzwerte (zentral!)
│   ├── data_prep.py                # QUA³CK Q + U: Qualitätsprüfung & EDA
│   ├── train.py                    # QUA³CK A + C: Modellvergleich & CV
│   └── fetch_cities.py             # holt alle dt. Städte via OpenPLZ API
├── data/cities_de.json             # 10.786 Städte (aus OpenPLZ, für die Sidebar)
├── notebooks/                      # Abgabe-Artefakte: 1 Notebook pro QUA³CK-Phase
│   ├── 00_gesamtueberblick_qua3ck.ipynb   # alle Phasen kompakt in einem
│   ├── 01_qualitaetspruefung.ipynb        # Q – Qualitätsprüfung
│   ├── 02_understanding_the_data.ipynb    # U – EDA
│   ├── 03_algorithmenauswahl.ipynb        # A – Modellvergleich
│   ├── 04_modellentwicklung.ipynb         # Pipeline & Training
│   ├── 05_kreuzvalidierung.ipynb          # C – 5-fache CV
│   └── 06_wissensextraktion.ipynb         # K – Erkenntnisse & App
├── data/
│   └── immo_clean.parquet          # bereinigter Datensatz (Rohdatei separat nachladbar)
├── models/
│   ├── mietcheck_model.joblib      # trainiertes Modell
│   └── meta.json                   # Dropdown-Optionen + Defaults für die App
└── reports/
    ├── 01–06_*.png                 # EDA- & Ergebnis-Grafiken
    └── metrics.json                # alle Kennzahlen
```

### Die App besteht aus 5 Seiten (Navigation über die Bottom-Bar unten)

| Seite | Inhalt |
|---|---|
| 🏠 **Check** | faire Kaltmiete **+ Warmmiete + Preisspanne (± MAE)**, Regionsvergleich, **„Warum dieser Preis?"** (Wertbeitrag jeder Ausstattung, per Modell berechnet), Tacho-Urteil, empfohlenes Einkommen |
| 🗺️ **Markt** | **Deutschland-Mietkarte** (Choropleth je Bundesland), günstigstes/teuerstes Land, teuerste Städte, Miete nach Zimmerzahl, Preisverteilung, **bundesweites Städte-Ranking (Suche + Sortierung)** |
| 🧮 **Budget** | Leistbarkeits-Rechner: Einkommen + Wohnkostenanteil → leistbare Warm-/Kaltmiete & Wohnfläche, Großstadt-Vergleich „was bekomme ich wo?" |
| 📈 **Modell** | Genauigkeit, Modellvergleich (Kreuzvalidierung), Merkmalswichtigkeit, QUA³CK |
| ℹ️ **Über** | Idee/USP, beide Datenquellen, Technik, Grenzen |

> Die Seiten liegen in `views/`. Neue Funktion = neue Datei dort + ein Eintrag im
> `PAGES`-Dict oben in `app.py`. Standort/Sidebar & Logo stecken in `views/common.py`.
> Das Logo liegt als SVG in `assets/` (`logo.svg`, `logo_mark.svg`).

---

## 5. Loslegen (Schritt für Schritt)

### ⚡ Schnellstart auf dem Mac (Desktop)

1. **ZIP entpacken** – Doppelklick auf `MietCheck.zip`. Es entsteht der Ordner
   `MietCheck` (am besten direkt auf den Desktop legen).
2. **Terminal öffnen** (Cmd+Leertaste → „Terminal") und diese 3 Zeilen nacheinander
   einfügen:

```bash
cd ~/Desktop/MietCheck
pip3 install -r requirements.txt      # nur beim allerersten Mal (dauert 1–2 Min.)
streamlit run app.py
```

3. Es öffnet sich automatisch der Browser unter **http://localhost:8501**.
   Fertig. 🎉  Stoppen mit **Strg+C** im Terminal.

> Modell, Städte-Daten und Karte liegen bei – die App läuft **sofort, offline,
> ohne Training und ohne Kaggle/Internet**.

**Voraussetzung:** Python 3.9+ (Test: `python3 --version`). Falls nicht vorhanden:
python.org → Download → installieren, dann Terminal neu öffnen.

**Häufige Stolpersteine**
- `streamlit: command not found` → stattdessen `python3 -m streamlit run app.py`
- `pip3: command not found` → `python3 -m pip install -r requirements.txt`
- Anderer Port gewünscht → `streamlit run app.py --server.port 8502`
- Alternativ (ohne Terminal): Rechtsklick auf `start.command` → „Öffnen" → „Öffnen"
  (beim 1. Mal fragt macOS wegen unbekanntem Entwickler nach).

### ⚡ Schnellstart auf Windows (der einfachste Weg)

1. **ZIP entpacken:** Rechtsklick auf `MietCheck.zip` → „Alle extrahieren…".
   Ordner am besten auf den Desktop legen.
2. **Doppelklick auf `start.bat`** – fertig. Das Skript installiert beim ersten
   Mal automatisch alle Pakete und startet die App im Browser.

> Falls Windows „Der Computer wurde durch Windows geschützt" meldet:
> „Weitere Informationen" → „Trotzdem ausführen".

**Oder manuell über die Eingabeaufforderung:**
1. Den Ordner `MietCheck` öffnen, oben in die **Adressleiste** `cmd` tippen + Enter
   (öffnet die Eingabeaufforderung direkt in diesem Ordner).
2. Diese zwei Zeilen nacheinander:
   ```bat
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```
3. Der Browser öffnet automatisch **http://localhost:8501**. Beenden mit Strg+C.

**Voraussetzung Windows:** Python 3.9+ von python.org – beim Setup unbedingt
**„Add Python to PATH"** anhaken. Test in der Eingabeaufforderung: `python --version`.

### Notebook ansehen / ausführen

```bash
jupyter notebook notebooks/          # dann Phase 01…06 der Reihe nach öffnen
```

### Optional: Datenphase & Training komplett neu rechnen

```bash
# Rohdaten (272 MB) einmalig von Kaggle nachladen – braucht ~/.kaggle/kaggle.json
kaggle datasets download -d corrieaar/apartment-rental-offers-in-germany --unzip -p data

python3 src/data_prep.py     # Qualitätsprüfung + EDA  → immo_clean.parquet, reports/
python3 src/train.py         # Modellvergleich + CV    → models/mietcheck_model.joblib
```
> Kaggle-Zugang: kostenloses Konto auf kaggle.com → *Account → Create API Token* →
> die Datei `kaggle.json` nach `~/.kaggle/kaggle.json` legen.

---

## 6. Umsetzung entlang QUA³CK (fürs Verständnis / die Ausarbeitung)

| Phase | Bedeutung | Wo im Code |
|---|---|---|
| **Q** Qualitätsprüfung | Datenfehler & Ausreißer entfernen (z. B. 5 €/m², 9,9 Mio. € Miete); Plausibilitätsgrenzen | `src/data_prep.py → quality_check()` |
| **U** Understanding the Data | EDA: Verteilungen, Preis/m² je Bundesland, Korrelationen, Fläche↔Miete | `src/data_prep.py → eda()`, Notebook |
| **A** Algorithmenauswahl | 3 Modelle vergleichen (LinReg, RandomForest, GradientBoosting) | `src/train.py → get_models()` |
| Modellentwicklung | sklearn-Pipeline: Imputation → Scaling → One-Hot → Modell | `src/train.py → build_preprocessor()` |
| **C** Kreuzvalidierung | 5-fache CV, faire Auswahl des besten Modells | `src/train.py → cross_val_score` |
| **K** Wissensextraktion | Merkmalswichtigkeit + **App als Deployment** | `app.py`, `reports/06_...png` |

---

## 7. Ideen zum Weitermachen (Ausbaustufen)

Bewusst **nicht** eingebaut, um den Prototyp einfach zu halten – gute Kandidaten für
die nächste Iteration bzw. die Note-Steigerung:

- **Warmmiete-Modus** (zusätzlich zur Kaltmiete `totalRent` vorhersagen).
- **Deutschland-Karte** der Mietpreise (z. B. mit `folium`/`plotly` über PLZ/`geo_plz`).
- **PLZ-Suche** statt Stadt-Dropdown (Spalte `geo_plz` ist vorhanden).
- **Hyperparameter-Tuning** (GridSearch/RandomizedSearch) fürs Gradient Boosting.
- **SVM/SVR** als zusätzlicher Modellvergleich (passt zu Kapitel 5 der Vorlesung).
- **Öffentliches Deployment** auf *Streamlit Community Cloud* (kostenloser Link zum Vorführen).
- **Schriftliche Ausarbeitung / Präsentationsfolien** entlang der QUA³CK-Phasen.

---

## 8. Grenzen & Hinweise

- Die Schätzung ist ein **datenbasierter Richtwert** auf Basis historischer
  Angebotsdaten – **kein amtlicher Mietspiegel** und keine Rechtsberatung.
- Sehr seltene Orte oder extreme Wohnungen (Luxus/winzig) werden schlechter getroffen.
- Der Datensatz ist ein Stichtags-Snapshot; für Produktivbetrieb müsste man ihn
  regelmäßig aktualisieren.

---

*Viel Erfolg beim Weiterbauen! Der Prototyp ist so gebaut, dass `src/config.py` die
zentrale Stellschraube ist: Merkmale, Grenzwerte und Pfade an einem Ort.*
