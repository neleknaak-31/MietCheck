# ruff: noqa: E501
"""Generate the seven clean, executable QUA³CK notebooks.

The notebooks intentionally consume versioned machine-readable reports. Heavy
data builds and model fits remain in tested scripts; notebook cells inspect,
validate, visualise and interpret those results without silently recomputing a
different experiment.

Usage:
    python scripts/generate_notebooks.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

SETUP = """from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

ROOT = Path.cwd().resolve()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent

COLORS = {"navy": "#14213D", "blue": "#2563EB", "teal": "#0F766E",
          "amber": "#F59E0B", "red": "#DC2626", "grey": "#64748B"}
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"figure.figsize": (9, 4.8), "axes.titleweight": "bold",
                     "axes.labelsize": 10, "figure.dpi": 110})

def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

print(f"Projektwurzel: {ROOT}")"""

FOOTER = """---

**Reproduzierbarkeit:** Die visualisierten Kennzahlen stammen aus versionierten JSON-/CSV-Artefakten. Die jeweils genannten Skripte erzeugen diese Artefakte aus den öffentlichen Rohdaten erneut. Relative Pfade funktionieren sowohl aus der Projektwurzel als auch aus `notebooks/`."""


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def notebook(title: str, subtitle: str, cells: list) -> nbf.NotebookNode:
    intro = f"# {title}\n\n{subtitle}\n\n**Projekt:** MietCheck · Data Analytics & Big Data"
    nb = nbf.v4.new_notebook(
        cells=[markdown(intro), code(SETUP), *cells, markdown(FOOTER)],
        metadata={
            "kernelspec": {
                "display_name": "Python (MietCheck)",
                "language": "python",
                "name": "mietcheck",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    return nb


def build_notebooks() -> dict[str, nbf.NotebookNode]:
    overview = notebook(
        "00 · Gesamtüberblick QUA³CK",
        "Vom prüfbaren Problem zur transparenten Machine-Learning-App.",
        [
            markdown(
                """## Forschungsfrage und Produktidee

**Forschungsfrage:** Wie stark weichen aktuelle Angebotsmieten von lokal erwartbaren Bestandsmieten ab, und wie verändert dieser Abstand die persönliche Mietbelastung?

MietCheck trennt drei Größen, die andere Rechner häufig vermischen:

1. modellierte lokale Zensus-Bestandsmiete (Stichtag 15.05.2022),
2. aktuelle GREIX-Angebotsmiete (Q1/2026),
3. persönliche Miete beziehungsweise Budget.

Der daraus berechnete **Umzugsaufschlag** ist das Alleinstellungsmerkmal. Er wird mit Datenstand, Marktstreuung, Modellunsicherheit und Grenzen ausgegeben."""
            ),
            code(
                """build = load_json("reports/dataset_build_report.json")
greix = load_json("data/app/greix_metadata.json")
benchmark = load_json("reports/algorithm_benchmark.json")
final = load_json("reports/final_model_evaluation.json")

kpis = pd.DataFrame([
    ("Zensus-Zielzeilen", f"{build['rows']:,}"),
    ("100-m-Gitterzellen", f"{build['unique_grid_cells']:,}"),
    ("GREIX-Regionen", greix["regions"]),
    ("Aktueller Datenstand", greix["latest_period"]),
    ("verglichene Modellfamilien", len(benchmark["models"])),
    ("finaler räumlicher Test-MAE", f"{final['test']['point_metrics']['mae']:.3f} €/m²"),
    ("empirische Intervall-Coverage", f"{final['test']['category_specific_90_percent_interval']['coverage']:.1%}"),
], columns=["Nachweis", "Wert"])
display(kpis.style.hide(axis="index"))"""
            ),
            code(
                """profiles = pd.read_csv(ROOT / "data/app/region_profiles.csv")
snapshot = pd.DataFrame({
    "Kennzahl": ["lokale GREIX-Märkte", "Angebotsmedian min.", "Angebotsmedian max.",
                 "Zensus-Referenz", "GREIX-Referenz"],
    "Wert": [len(profiles), f"{profiles['asking_median_eur_sqm'].min():.2f} €/m²",
             f"{profiles['asking_median_eur_sqm'].max():.2f} €/m²",
             "15.05.2022", profiles['period'].max()],
})
display(snapshot.style.hide(axis="index"))"""
            ),
            markdown(
                """## QUA³CK-Nachweiskette

| Phase | Leitfrage | Notebook / Evidenz |
|---|---|---|
| Q · Question | Welches Problem, für wen und mit welchen KPIs? | `01_question.ipynb` |
| U · Understanding | Sind Quellen belastbar und wie verteilen sich Ziel und Merkmale? | `02_understanding_the_data.ipynb` |
| A¹ · Auswahl | Welche Modellfamilie generalisiert räumlich? | `03_algorithmenauswahl.ipynb` |
| A² · Adapting | Welche Feature-Gruppen liefern Zusatznutzen? | `04_modellentwicklung.ipynb` |
| A³ · Adjusting | Welche Hyperparameter generalisieren stabil? | `04_modellentwicklung.ipynb` |
| C · Comparing | Wie gut ist es auf gesperrten Regionen? | `05_kreuzvalidierung.ipynb` |
| K · Knowledge | Welcher Mehrwert entsteht für Mietende? | `06_wissensextraktion.ipynb` |"""
            ),
            code(
                """models = pd.DataFrame(benchmark["ranking_by_mean_mae"])
models["improvement_vs_baseline_pct"] = (
    1 - models["mean_mae"] / models.loc[models["model"].eq("category_median"), "mean_mae"].iloc[0]
) * 100
display(models.round(3))

ax = models.sort_values("mean_mae").plot.barh(
    x="model", y="mean_mae", xerr="std_mae", color=COLORS["blue"], legend=False
)
ax.set(title="Räumlicher Modellvergleich", xlabel="MAE in €/m²", ylabel="")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## Vorab definierte Erfolgskriterien

- mindestens 2 Mio. Beobachtungen und reproduzierbarer Download,
- mindestens vier Modellfamilien plus fachliche Baseline,
- keine räumliche Überschneidung zwischen Trainings-, Kalibrierungs- und Testblöcken,
- mindestens 15 % MAE-Verbesserung gegenüber der Kategorien-Baseline,
- sichtbare Unsicherheit ohne falsche Garantie,
- aktueller Marktstand und Quellen direkt am Ergebnis,
- Streamlit-App, GitHub, Tests, Modellkarte, Präsentation und Handout."""
            ),
        ],
    )

    question = notebook(
        "01 · Q – Question",
        "Problem, Zielgruppe, Forschungsfragen, KPIs und geplante Bereitstellung.",
        [
            markdown(
                """## Position im QUA³CK-Prozess

Jedes belastbare Data-Science-Projekt beginnt nicht mit einem Algorithmus, sondern mit einer klaren Entscheidung darüber, **welches Problem gelöst werden soll**. Die Q-Phase übersetzt den gesellschaftlichen Kontext steigender Wohnkosten in eine prüfbare Data-Science-Aufgabe. Sie definiert Zielgruppen, Forschungsfragen, Erfolgsmetriken, Grenzen und das Deployment-Ziel, bevor Daten oder Modelle ausgewählt werden.

> **Zentrale Forschungsfrage:** Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren erklären die Bestandsmiete und wie zuverlässig lässt sie sich für eine konkrete Wohnsituation schätzen?"""
            ),
            markdown(
                """## Problem und Relevanz

Bestehende Mietverhältnisse, heutige Wohnungsangebote und die persönliche Vertragsmiete messen drei unterschiedliche Realitäten. Viele Rechner verdichten sie trotzdem zu einer einzigen vermeintlich „fairen“ Miete. Dadurch bleiben Zeitbezug, Marktstreuung und Modellfehler unsichtbar.

MietCheck trennt deshalb:

1. **Bestandsrealität:** amtliche Zensus-Nettokaltmiete zum 15.05.2022,
2. **Umzugsrealität:** aktuelle GREIX-Angebotsmiete bis Q1/2026,
3. **persönliche Realität:** eigene Vertragsmiete und Mietbelastung.

Der daraus abgeleitete **Umzugsaufschlag** beantwortet eine konkrete Alltagsfrage: Was würde ein heutiger Umzug gegenüber dem lokalen Wohnungsbestand und meiner jetzigen Situation finanziell verändern?"""
            ),
            markdown(
                """## Zielgruppen und Entscheidungssituationen

| Zielgruppe | Konkrete Entscheidung | Benötigte Information |
|---|---|---|
| Mieterinnen und Mieter | eigene Miete einordnen | persönliche Miete vs. lokaler Bestand |
| Wohnungssuchende | Umzug finanziell bewerten | aktueller Angebotsmedian und Markt-IQR |
| Studierende / Berufseinsteiger | Budgetfolgen abschätzen | monatliche Belastung relativ zum Einkommen |
| dateninteressierte Öffentlichkeit | regionale Unterschiede verstehen | Zeitreihen, Methodik, Quellen und Grenzen |

Die App ist bewusst **keine Rechtsprüfung**, kein amtlicher Mietspiegel und keine punktgenaue Wohnungsbewertung."""
            ),
            code(
                """stakeholders = pd.DataFrame([
    ("Mietende", "aktuelle Vertragsmiete einordnen", "Bestandsanker + eigenes Mietbild"),
    ("Wohnungssuchende", "Umzugsfolgen abschätzen", "Angebotsmedian + Umzugsaufschlag"),
    ("Studierende / Berufseinsteiger", "Budgetrisiko prüfen", "Mietbelastung am Haushaltsnetto"),
    ("Öffentlichkeit", "regionale Unterschiede verstehen", "Zeitreihe + Methodik + Grenzen"),
], columns=["Zielgruppe", "Entscheidung", "App-Ausgabe"])
display(stakeholders.style.hide(axis="index"))"""
            ),
            markdown(
                """## Thematische Forschungsfragen

1. Wie stark variiert die Bestandsmiete innerhalb und zwischen deutschen Regionen?
2. Verbessern strukturelle Wohnumfeldmerkmale eine rein kategoriale Baseline?
3. Welches Regressionsverfahren generalisiert auf bislang ungesehene räumliche Gebiete?
4. Wie groß ist die Differenz zwischen Zensus-Bestandsmiete 2022 und GREIX-Angebotsmiete 2026?
5. Wie verändert diese Differenz die persönliche Mietbelastung bei einem Umzug?
6. Wie muss Unsicherheit dargestellt werden, damit aus einem Modellwert keine Scheingenauigkeit wird?"""
            ),
            markdown(
                """## Vorab definierte KPIs und Go/No-Go-Regeln

| Dimension | Ziel vor Modellierung | Konsequenz bei Nichterfüllung |
|---|---|---|
| Big Data | mindestens 2 Mio. reproduzierbare Modellzeilen | Datenkonzept neu bewerten |
| Modellvergleich | mindestens vier Modellfamilien plus fachliche Baseline | A¹ erweitern |
| Generalisierung | räumlich disjunkte Entwicklung, Kalibrierung und Test | kein Deployment |
| Modellnutzen | mindestens 15 % niedrigerer Test-MAE als Baseline | Produkt-Hook neu bewerten |
| Unsicherheit | separates Kalibrierungsset und gemessene Coverage | keine Punktzahl ohne Warnung |
| Produkt | zentrale Nutzerreise unter zwei Sekunden und mobil lesbar | Optimierung vor Freigabe |
| Reproduzierbarkeit | Download, Tests, GitHub Actions und ausgeführte Notebooks | keine Abgabe |

Die Schwellenwerte werden **vor** dem finalen Test festgelegt. Dadurch kann ein Ergebnis nicht nachträglich passend erklärt werden."""
            ),
            code(
                """criteria = pd.DataFrame([
    ("Datenumfang", "≥ 2.000.000 Zeilen", "reports/dataset_build_report.json"),
    ("Modellvergleich", "≥ 4 Familien + Baseline", "reports/algorithm_benchmark.json"),
    ("Testdesign", "0 gemeinsame 25-km-Blöcke", "reports/hgb_tuning.json"),
    ("Modellnutzen", "≥ 15 % MAE-Verbesserung", "reports/final_model_evaluation.json"),
    ("Unsicherheit", "separate Kalibrierung + Coverage", "reports/final_model_evaluation.json"),
    ("Deployment", "Streamlit + GitHub + CI", "app.py / .github/workflows/ci.yml"),
], columns=["Dimension", "Erfolgskriterium", "späterer Nachweis"])
display(criteria.style.hide(axis="index"))"""
            ),
            markdown(
                """## Marktumfeld und Alleinstellungsmerkmal

Amtliche Mietspiegel, Immobilienportale und Budgetrechner beantworten jeweils Teilfragen. MietCheck verbindet in **einer quelloffenen Nutzerreise** einen kleinräumigen ML-Bestandsanker, einen aktuellen unabhängigen Angebotsmarkt und die persönliche Mietbelastung. Entscheidend ist nicht ein weiterer Preisrechner, sondern die methodische Trennung:

- **Zensus:** Was wurde im Bestand 2022 durchschnittlich gezahlt?
- **GREIX:** Was wird bei heutigen Angeboten in einem Markt verlangt?
- **persönliche Eingabe:** Was bedeutet der Abstand für diesen Haushalt?

Diese Kombination ist der USP; jede Einzelkomponente bleibt hinsichtlich Datenstand, Abdeckung und Unsicherheit sichtbar."""
            ),
            markdown(
                """## Deployment-Ziel und Lieferobjekte

Das Ergebnis der K-Phase ist eine responsive Streamlit-App mit reservierter URL `mietcheck.streamlit.app`, ein öffentlich nachvollziehbares GitHub-Repository, vollständig ausgeführte QUA³CK-Notebooks, Modell- und Datenkarte, automatisierte Tests sowie Präsentations- und Dokumentationsartefakte.

**Bewusste Grenzen:** keine Portal-Scrapes, keine personenbezogene Speicherung, keine Rechts- oder Finanzberatung, keine lokale Angebotsbehauptung außerhalb der 37 belegten GREIX-Märkte."""
            ),
            code(
                """deliverables = pd.DataFrame([
    ("ML-Nachweis", "ausgeführte QUA³CK-Notebooks + versionierte Reports"),
    ("Produkt", "responsive Streamlit-App"),
    ("Reproduzierbarkeit", "GitHub, Downloadskripte, Tests und CI"),
    ("Transparenz", "Datenkarte, Modellkarte, Risiko-/Ethikdokument"),
    ("Prüfung", "Präsentation, schriftliche Ausarbeitung und Demo-Runbook"),
], columns=["Lieferobjekt", "Abnahmekriterium"])
display(deliverables.style.hide(axis="index"))"""
            ),
        ],
    )

    understanding = notebook(
        "02 · U – Understanding the Data",
        "Explorative Analyse von 2,06 Mio. Zielzeilen und räumlichem Kontext.",
        [
            markdown(
                """## Aufgabe der U-Phase

Die U-Phase klärt, **was die Daten tatsächlich messen**, wie vollständig und belastbar sie sind und welche Muster die spätere Modellwahl beeinflussen. MietCheck kombiniert bewusst zwei Datenprodukte, die nicht dieselbe Grundgesamtheit beschreiben:

| Datenquelle | Messkonzept | räumlich/zeitlicher Grain | Rolle im Produkt |
|---|---|---|---|
| Zensus 2022, 100-m-Gitter | durchschnittliche Nettokaltmiete bestehender Mietverhältnisse | Gitterzelle × Gebäudealter × Wohnungsgröße, Stichtag 15.05.2022 | ML-Ziel und lokaler Bestandsanker |
| GREIX Mietpreisindex | nominale Angebotsmieten aus Inseraten | Quartal × Markt, 2012-Q1 bis 2026-Q1 | aktuelle Umzugsrealität und Markt-IQR |

Die Differenz zwischen beiden Quellen wird **deskriptiv** als Umzugsaufschlag bezeichnet. Sie ist keine Preisfortschreibung des Zensus und kein kausaler Markteffekt."""
            ),
            markdown(
                """## Herkunft, Lizenz und Auswahlentscheidung

Die Zensus-Gitterdaten stammen von den Statistischen Ämtern des Bundes und der Länder und stehen unter der Datenlizenz Deutschland – Namensnennung – Version 2.0. GREIX wird vom Kiel Institut für Weltwirtschaft auf Basis der VALUE-Marktdatenbank veröffentlicht. Beide Quellen sind öffentlich nachvollziehbar, vermeiden kommerzielles Portal-Scraping und besitzen klar dokumentierte Datenstände.

**Warum diese Kombination?** Zensus liefert die für Big Data erforderliche räumliche Tiefe; GREIX liefert die aktuelle Marktdynamik. Keine Quelle kann die jeweils andere ersetzen."""
            ),
            markdown(
                """## Qualitätslogik vor der EDA

Die Modellzeile ist eindeutig durch `GITTER_ID_100m × Gebäudealterklasse × Wohnungsgrößenklasse`. Kontextquellen werden zunächst je Gitterzelle validiert und anschließend als `many_to_one` an das Zielgrain gejoint. Zielwerte werden nie imputiert. So verhindert der Build unbemerkte Zeilenvervielfachung und künstlich erfundene Mieten."""
            ),
            code(
                """report = load_json("reports/dataset_build_report.json")
target = report["target"]
quality_summary = pd.DataFrame({
    "Kennzahl": ["Zeilen", "eindeutige Gitterzellen", "25-km-Blöcke",
                 "Zielminimum", "Zielmedian", "Zielmittel", "Zielmaximum",
                 "amtlich unsicherer Zielanteil"],
    "Wert": [report["rows"], report["unique_grid_cells"], report["spatial_blocks_25km"],
             target["min"], target["median"], target["mean"], target["max"],
             target["uncertain_share"]],
})
display(quality_summary.style.hide(axis="index"))"""
            ),
            code(
                """coverage = pd.Series(report["feature_non_null_share"], name="non_null_share")
coverage = coverage.sort_values().to_frame()
coverage["missing_share"] = 1 - coverage["non_null_share"]
display(coverage.style.format("{:.2%}"))

ax = coverage["non_null_share"].plot.barh(color=COLORS["teal"])
ax.axvline(0.99, color=COLORS["amber"], linestyle="--", label="99%-Marke")
ax.set(xlim=(0.985, 1.0), xlabel="Anteil vorhanden", ylabel="",
       title="Kontext-Feature-Coverage")
ax.legend(); plt.tight_layout(); plt.show()"""
            ),
            code(
                """sources = report["raw_source_manifest"]["sources"]
source_table = pd.DataFrame([
    {"key": key, "Datei": value["filename"], "MB": value["bytes"] / 1e6,
     "SHA-256 (kurz)": value["sha256"][:12], "Lizenz": value["license"]}
    for key, value in sources.items()
]).set_index("key")
display(source_table.round({"MB": 2}))

assert report["rows"] >= 2_000_000
assert report["unique_grid_cells"] >= 1_000_000
assert min(report["feature_non_null_share"].values()) >= 0.99
assert 0.5 <= target["min"] <= target["max"] <= 60
print("✓ Alle zentralen Datenqualitäts-Gates bestanden")"""
            ),
            markdown(
                """### Kritische Datenentscheidungen

- Das amtliche Zeichen `–` bedeutet in den ausgewählten Zensusdateien **exakt beziehungsweise auf 0 geändert**, nicht „fehlend“. Der Parser schützt diese Semantik mit Tests.
- `KLAMMERN` wird als amtliches Unsicherheitsflag erhalten.
- Das Unsicherheitsflag der **Zielmiete** wird ausgewertet, aber nicht als Eingabefeature verwendet.
- Roharchive bleiben unverändert; URL, Abrufzeitpunkt, Dateigröße und SHA-256 dokumentieren ihren Stand.
- Sensible Merkmale wie Religion oder Staatsangehörigkeit werden nicht modelliert."""
            ),
            markdown(
                """## Daten laden und inspizieren

Für Diagramme wird eine deterministische Stichprobe gezogen; Kennzahlen und Modelle nutzen weiterhin die vollständige Tabelle beziehungsweise die dokumentierten großen Splits."""
            ),
            code(
                """data_path = ROOT / "data/processed/model_table.parquet"
if not data_path.exists():
    raise FileNotFoundError("Zuerst: python scripts/download_data.py && python scripts/build_dataset.py")

columns = ["x_laea_m", "y_laea_m", "rent_eur_sqm", "building_after_1990",
           "dwelling_over_65sqm", "population", "avg_household_size",
           "ownership_rate_pct", "vacancy_rate_pct", "avg_dwelling_area_sqm",
           "dwelling_count", "target_uncertain"]
df = pd.read_parquet(data_path, columns=columns)
sample = df.sample(n=200_000, random_state=2026)
print(f"Vollbestand: {len(df):,} Zeilen · EDA-Stichprobe: {len(sample):,}")
display(sample["rent_eur_sqm"].describe(percentiles=[.01, .25, .5, .75, .99]).to_frame())"""
            ),
            markdown(
                """## Zielvariable und Merkmalsgruppen

**Zielvariable:** durchschnittliche Nettokaltmiete in Euro pro Quadratmeter. Eine Zeile beschreibt kein individuelles Inserat, sondern ein amtliches Aggregat für eine 100-m-Gitterzelle und eine grobe Wohnungsgruppe.

| Merkmalsgruppe | Beispiele | Modelllogik |
|---|---|---|
| Lage | ETRS89-LAEA x/y | regionale und urbane Mietstruktur |
| Wohnung | Baujahr vor/nach 1990, bis/über 65 m² | grobe Alters- und Größenunterschiede |
| Bevölkerung | Einwohner, Haushaltsgröße | lokaler Siedlungskontext |
| Wohnungsmarktstruktur | Eigentum, Leerstand, Wohnfläche, Wohnungszahl | Bestands- und Angebotsdruck im Umfeld |
| Qualität | fünf amtliche Unsicherheitskennzeichen | Verlässlichkeit der Kontextwerte |

Koordinaten und Kontext dürfen prädiktiv nützlich sein, werden aber später **nicht kausal** interpretiert."""
            ),
            markdown(
                """## Aufgabe 1: Verteilung und Kategorien

Der lange rechte Rand der Mietverteilung macht den Mittelwert empfindlich gegenüber Extremwerten. Deshalb werden später MAE und Median Absolute Error als robuste Hauptmetriken verwendet. Die Kategorienvisualisierung prüft, ob Gebäudealter und Wohnungsgröße bereits ohne komplexes Modell erkennbare Unterschiede tragen."""
            ),
            code(
                """fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
sample["rent_eur_sqm"].clip(upper=20).plot.hist(
    bins=60, ax=axes[0], color=COLORS["blue"], alpha=.85
)
axes[0].set(title="Zielverteilung (bei 20 €/m² gekappt)", xlabel="Bestandsmiete €/m²")

grouped = sample.groupby(["building_after_1990", "dwelling_over_65sqm"])["rent_eur_sqm"].median()
labels = ["alt · klein", "alt · groß", "neu · klein", "neu · groß"]
grouped.plot.bar(ax=axes[1], color=COLORS["teal"])
axes[1].set(title="Median nach amtlichen Kategorien", xlabel="Alter · Größe", ylabel="€/m²")
axes[1].set_xticklabels(labels, rotation=25, ha="right")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## Aufgabe 2: Räumliche Struktur

Benachbarte Gitterzellen ähneln sich häufig. Würden sie zufällig auf Training und Test verteilt, könnte das Modell räumliche Nachbarn „wiedererkennen“ und seine Güte würde zu optimistisch erscheinen. Die Karte begründet deshalb den späteren Split in 25-km-Blöcke."""
            ),
            code(
                """plot_sample = sample.sample(n=50_000, random_state=2026)
fig, ax = plt.subplots(figsize=(8.5, 7))
points = ax.scatter(plot_sample["x_laea_m"], plot_sample["y_laea_m"],
                    c=plot_sample["rent_eur_sqm"].clip(upper=15), s=3,
                    cmap="viridis", alpha=.35, linewidths=0)
fig.colorbar(points, ax=ax, label="Bestandsmiete €/m² (bis 15)")
ax.set(title="Räumliche Struktur der Zensus-Bestandsmieten",
       xlabel="ETRS89-LAEA x", ylabel="ETRS89-LAEA y")
ax.set_aspect("equal"); plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## Aufgabe 3: Zusammenhänge und Grenzen der Interpretation

Rangkorrelationen zeigen monotone Beziehungen auch bei schiefen Verteilungen. Sie sind ein Diagnosewerkzeug für Redundanz und Feature Engineering, aber kein Nachweis für Ursache und Wirkung. Besonders räumliche Lage, Eigentum und Leerstand können gemeinsame regionale Strukturen abbilden."""
            ),
            code(
                """numeric = ["rent_eur_sqm", "population", "avg_household_size",
           "ownership_rate_pct", "vacancy_rate_pct", "avg_dwelling_area_sqm",
           "dwelling_count"]
corr = sample[numeric].corr(method="spearman")
fig, ax = plt.subplots(figsize=(8, 6))
image = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(numeric)), [x.replace("_", " ") for x in numeric], rotation=60, ha="right")
ax.set_yticks(range(len(numeric)), [x.replace("_", " ") for x in numeric])
fig.colorbar(image, ax=ax, label="Spearman ρ")
ax.set_title("Rangkorrelationen der Kontextmerkmale")
plt.tight_layout(); plt.show()

print("Zielunsicherheit:", f"{df['target_uncertain'].mean():.1%}")"""
            ),
            markdown(
                """## EDA-Schlussfolgerungen

- Starke räumliche Struktur macht zufällige Zeilensplits ungeeignet.
- Neue Gebäude und kleinere Wohnungen weisen tendenziell höhere €/m²-Werte auf.
- Kontextmerkmale sind korreliert; Wichtigkeiten dürfen nicht kausal interpretiert werden.
- Die Zielverteilung besitzt einen langen rechten Rand. MAE und Median AE sind deshalb zentrale, robuste Metriken.
- Zensuswerte sind Gitterzellenaggregate, keine Einzelwohnungsbeobachtungen."""
            ),
        ],
    )

    algorithms = notebook(
        "03 · A¹ – Algorithmenauswahl",
        "Fünf Modellfamilien unter identischer räumlicher GroupKFold-Validierung.",
        [
            markdown(
                """## Position in der A³-Schleife

Nach der U-Phase ist klar: Die Zielgröße ist kontinuierlich, räumlich strukturiert und rechtsschief. A¹ wählt deshalb nicht einfach den modernsten Algorithmus, sondern vergleicht repräsentative Regressionsfamilien unter exakt denselben räumlichen Bedingungen.

| Kandidat | einfache Vorstellung | Stärke | erwartbare Grenze |
|---|---|---|---|
| Kategorien-Median | typischer Wert je Alter/Größe | fachlich verständliche Baseline | ignoriert Lage und Kontext |
| Ridge | regulierte Regressionsgerade | schnell und transparent | bildet Nichtlinearität nur begrenzt ab |
| Random Forest | Mittel vieler Entscheidungsbäume | flexible Interaktionen | groß und langsamer |
| HistGradientBoosting | Bäume korrigieren schrittweise Fehler | stark auf großen Tabellen | weniger direkt erklärbar |
| MLP | neuronales Netz für Tabellendaten | flexible Funktionsform | tuning- und rechenintensiv |

Alle Modelle lösen dasselbe **Regressionsproblem**: Aus Lage, Wohnungskategorie und Kontext wird eine Bestandsmiete in €/m² geschätzt."""
            ),
            markdown(
                """## Faires Vergleichsdesign

600.000 identische Zeilen, 660 räumliche 25-km-Blöcke und drei identische `GroupKFold`-Splits für Baseline, Ridge, Random Forest, Histogram Gradient Boosting und MLP. Primäre Metrik ist der MAE in €/m²."""
            ),
            markdown(
                """### Warum MAE, RMSE und R² gemeinsam?

- **MAE:** durchschnittlicher absoluter Fehler in €/m²; leicht erklärbar und robust.
- **RMSE:** bestraft große Einzelfehler stärker und macht Risikospitzen sichtbar.
- **R²:** Anteil der erklärten Streuung; hilfreich, aber für räumliche Holdouts nicht allein entscheidend.
- **Trainingszeit:** qualitative Produktionsmetrik für Reproduzierbarkeit und Wartbarkeit.

Der MAE entscheidet das Ranking, die anderen Größen verhindern eine eindimensionale Modellwahl."""
            ),
            code(
                """report = load_json("reports/algorithm_benchmark.json")
ranking = pd.DataFrame(report["ranking_by_mean_mae"])
summaries = []
for model, detail in report["models"].items():
    summaries.append({
        "model": model,
        "MAE": detail["summary"]["mae"]["mean"],
        "MAE_std": detail["summary"]["mae"]["std"],
        "RMSE": detail["summary"]["rmse"]["mean"],
        "R2": detail["summary"]["r2"]["mean"],
        "train_s": np.mean([f.get("training_seconds", np.nan) for f in detail["folds"]]),
    })
summary = pd.DataFrame(summaries).sort_values("MAE")
display(summary.round(3).style.hide(axis="index"))"""
            ),
            code(
                """fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
ordered = summary.sort_values("MAE", ascending=True)
axes[0].barh(ordered["model"], ordered["MAE"], xerr=ordered["MAE_std"],
             color=[COLORS["teal"] if m == "hist_gradient_boosting" else COLORS["grey"]
                    for m in ordered["model"]])
axes[0].set(title="Räumlicher CV-Fehler", xlabel="MAE €/m²")

timed = summary.dropna(subset=["train_s"]).sort_values("train_s")
axes[1].barh(timed["model"], timed["train_s"], color=COLORS["blue"])
axes[1].set(title="Mittlere Trainingszeit je Fold", xlabel="Sekunden")
plt.tight_layout(); plt.show()"""
            ),
            code(
                """folds = []
for model, detail in report["models"].items():
    for fold in detail["folds"]:
        folds.append({"model": model, "fold": fold["fold"], "MAE": fold["metrics"]["mae"]})
fold_table = pd.DataFrame(folds).pivot(index="model", columns="fold", values="MAE")
fold_table["Mittel"] = fold_table.mean(axis=1)
display(fold_table.sort_values("Mittel").round(3))

baseline = summary.loc[summary["model"].eq("category_median"), "MAE"].iloc[0]
champion = summary.iloc[0]
print(f"Champion: {champion['model']} · Verbesserung zur Baseline: {(1-champion['MAE']/baseline):.1%}")"""
            ),
            markdown(
                """## Entscheidung und Übergang zu A²

Histogram Gradient Boosting gewinnt mit MAE 1,305 €/m² knapp vor Random Forest (1,320), trainiert aber etwa 2,4-mal schneller. Der Vorsprung von nur 0,016 €/m² wird **nicht** als statistisch große Überlegenheit verkauft; Random Forest bleibt Challenger.

Ridge und Kategorien-Median bleiben interpretierbare Referenzen. Das MLP belegt, dass ein neuronaler Ansatz geprüft wurde, erreichte aber sein Iterationslimit und war deutlich langsamer. Damit ist HGB der fachlich ausgewogene Kandidat für die nächste Schleife: beste räumliche CV-Güte, akzeptable Rechenzeit und erklärbar über Permutationsbeiträge."""
            ),
        ],
    )

    development = notebook(
        "04 · A²/A³ – Features anpassen, Hyperparameter justieren",
        "Räumliches HGB-Tuning, inkrementelle Feature-Ablation und Modellartefakt.",
        [
            markdown(
                """## A² – Adapting Features

Die zweite A-Iteration fragt nicht „welches Modell?“, sondern „welche Information hilft dem gewählten Modell wirklich?“. MietCheck ergänzt Merkmale inkrementell:

1. **Kategorien-Baseline:** nur Gebäudealter und Wohnungsgröße,
2. **+ Lage:** ETRS89-LAEA-Koordinaten,
3. **+ Kontext:** Bevölkerung, Haushalt, Eigentum, Leerstand und Wohnungsbestand,
4. **+ Qualitätsflags:** amtliche Unsicherheitskennzeichen.

Die Ablation fügt Gruppen schrittweise hinzu und prüft jede Stufe auf denselben Raum-Folds. So wird nicht nur eine Feature Importance gezeigt, sondern der messbare Zusatznutzen ganzer Informationsgruppen."""
            ),
            markdown(
                """## A³ – Adjusting Hyperparameters

HGB besitzt Regler für Lernrate, Baumkomplexität, Mindestbeobachtungen je Blatt, Regularisierung und Iterationszahl. Acht begründete Konfigurationen werden innerhalb der Entwicklungsdaten verglichen. Das finale Testset bleibt während dieser Suche vollständig versiegelt."""
            ),
            markdown(
                """## Datensperre

Vor dem Tuning wurden 663 Raumblöcke in Entwicklung (70 %), Kalibrierung (15 %) und Test (15 %) geteilt. Nur Entwicklungsblöcke dürfen Parameter und Features beeinflussen. SHA-256-Fingerabdrücke machen Partitionsdrift sichtbar."""
            ),
            code(
                """tuning = load_json("reports/hgb_tuning.json")
partition = pd.DataFrame(tuning["partition"]).T
display(partition)
assert partition["group_sha256"].nunique() == 3
assert partition["blocks"].sum() == 663
print("✓ Drei disjunkt versionierte Partitionsfingerabdrücke")"""
            ),
            code(
                """candidate_rows = []
for item in tuning["candidates"]:
    candidate_rows.append({"Kandidat": item["candidate"], **item["parameters"], **item["summary"]})
candidates = pd.DataFrame(candidate_rows).sort_values("mean_mae")
display(candidates.round(4).style.hide(axis="index"))

ax = candidates.sort_values("mean_mae", ascending=False).plot.barh(
    x="Kandidat", y="mean_mae", xerr="std_mae", color=COLORS["blue"], legend=False
)
ax.set(title="Acht HGB-Konfigurationen · Spatial CV", xlabel="MAE €/m²", ylabel="Kandidat")
plt.tight_layout(); plt.show()
print("Gewählte Parameter:", tuning["selected_parameters"])"""
            ),
            code(
                """ablation = load_json("reports/feature_ablation.json")
rows = []
for item in ablation["incremental_comparison"]:
    detail = ablation["feature_sets"][item["feature_set"]]
    rows.append({**item, "features": len(detail["features"]),
                 "mean_r2": detail["summary"]["mean_r2"]})
abl = pd.DataFrame(rows)
display(abl.round(4).style.hide(axis="index"))

ax = abl.plot.bar(x="feature_set", y="mean_mae", color=COLORS["teal"], legend=False)
ax.set(title="Inkrementeller Feature-Wert", ylabel="MAE €/m²", xlabel="")
ax.tick_params(axis="x", rotation=25)
plt.tight_layout(); plt.show()"""
            ),
            code(
                """meta = load_json("models/zensus_hgb_meta.json")
artifact = ROOT / "models/zensus_hgb.joblib"
artifact_summary = pd.DataFrame([
    ("Modell", meta["model_name"]),
    ("Features", len(meta["feature_order"])),
    ("Trainingszeilen", meta["training_rows"]),
    ("Kalibrierungszeilen", meta["calibration_rows"]),
    ("Testzeilen", meta["test_rows"]),
    ("Artefaktgröße MB", artifact.stat().st_size / 1e6),
    ("scikit-learn", meta["sklearn_version"]),
], columns=["Eigenschaft", "Wert"])
display(artifact_summary)
assert artifact.exists() and artifact.stat().st_size > 100_000"""
            ),
            markdown(
                """## Ergebnis und Modellartefakt

Kandidat 6 (`learning_rate=.06`, 127 Blätter, 100 Mindestbeobachtungen je Blatt, L2=5) besitzt sowohl den niedrigsten mittleren als auch den niedrigsten schlechtesten Fold-MAE. Die Entscheidung belohnt damit nicht nur den besten Durchschnitt, sondern auch Stabilität.

Standort bringt in A² den größten Effekt. Numerischer Kontext und Qualitätsflags verbessern jedoch **alle** Folds und bleiben deshalb im 15-Feature-Modell. Modell, Feature-Reihenfolge, Softwareversion, Splits und Parameter werden gemeinsam versioniert; die App muss exakt dieses Artefakt laden und trainiert nichts stillschweigend neu.

**Übergabe an C:** Erst nach Abschluss aller A-Entscheidungen wird das gesperrte Testset einmalig geöffnet."""
            ),
        ],
    )

    validation = notebook(
        "05 · C – Comparing & Kreuzvalidierung",
        "Finale räumliche Güte, Baseline, Intervalle, Subgruppen und Erklärbarkeit.",
        [
            markdown(
                """## Position der C-Phase

Die A³-Schleife hat gebaut und optimiert; C **entscheidet**. Es werden keine neuen Features und keine neuen Hyperparameter mehr gesucht. Die Phase beantwortet fünf Fragen:

1. Erfüllt das gewählte Modell die vorab definierten KPIs?
2. Wie groß ist der Vorteil gegenüber der fachlichen Baseline?
3. Wo irrt das Modell systematisch stärker?
4. Wie belastbar sind die Unsicherheitsintervalle auf neuen Regionen?
5. Ist HGB auch unter qualitativen Kriterien die richtige App-Entscheidung?

Damit bleibt der finale Test ein ehrlicher Nachweis und wird nicht zu einer weiteren Tuningrunde."""
            ),
            markdown(
                """## Finale Evaluation

Das gewählte Modell wird auf 1.518.322 Entwicklungszeilen trainiert. 263.789 separate Zeilen kalibrieren Split-Conformal-Bänder. Erst danach werden 276.458 Zeilen aus 99 gesperrten Raumblöcken ausgewertet."""
            ),
            code(
                """report = load_json("reports/final_model_evaluation.json")
test = report["test"]
comparison = pd.DataFrame([
    {"Modell": "Kategorien-Median", **test["category_median_baseline_metrics"]},
    {"Modell": "Finales HGB", **test["point_metrics"]},
])
display(comparison.round(3).style.hide(axis="index"))
print(f"MAE-Verbesserung zur Baseline: {test['mae_improvement_vs_baseline']:.1%}")"""
            ),
            markdown(
                """### Formales KPI-Gate

Die vorab geforderte Verbesserung von mindestens 15 % wird mit 38,3 % deutlich erreicht. MAE 1,413 €/m² beschreibt den durchschnittlichen absoluten Fehler auf völlig neuen Raumblöcken; Median AE 0,956 €/m² zeigt, dass mindestens die Hälfte der Prognosen weniger als rund einen Euro pro Quadratmeter abweicht."""
            ),
            code(
                """intervals = pd.DataFrame([
    {"Intervall": "global", **test["global_90_percent_interval"]},
    {"Intervall": "kategoriespezifisch",
     **{k: v for k, v in test["category_specific_90_percent_interval"].items()
        if k != "calibrated_half_widths_eur_sqm"}},
])
display(intervals.round(3).style.hide(axis="index"))

ax = intervals.plot.bar(x="Intervall", y="coverage", color=COLORS["amber"], legend=False)
ax.axhline(.90, color=COLORS["red"], linestyle="--", label="nominelles Ziel 90 %")
ax.set(ylim=(.80, .92), ylabel="Coverage", xlabel="",
       title="Räumlicher Coverage-Test: ehrliche Unterdeckung")
ax.legend(); plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """### Warum die Coverage unter 90 % liegt

Split Conformal Prediction garantiert die nominelle Coverage nur unter Austauschbarkeit von Kalibrierungs- und Testbeobachtungen. Neue räumliche Regionen unterscheiden sich systematisch; deshalb erreicht das kategoriespezifische 90-%-Band empirisch 86,8 %. Wissenschaftlich korrekt ist nicht, die Zielzahl zu verstecken, sondern die **gemessene Testabdeckung** in App und Modellkarte auszuweisen."""
            ),
            code(
                """subgroups = []
for name, detail in test["subgroups"].items():
    subgroups.append({"Gruppe": name, "Zeilen": detail["rows"],
                      "MAE": detail["point_metrics"]["mae"],
                      "R2": detail["point_metrics"]["r2"],
                      "Coverage": detail["interval_metrics"]["coverage"]})
subgroups = pd.DataFrame(subgroups)
display(subgroups.round(3).style.hide(axis="index"))

category_groups = subgroups[subgroups["Gruppe"].str.startswith("category")]
ax = category_groups.plot.bar(x="Gruppe", y="MAE", color=COLORS["blue"], legend=False)
ax.set(title="Fehler nach Gebäudealter-/Größenklasse", ylabel="MAE €/m²", xlabel="")
ax.tick_params(axis="x", rotation=25)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """### Qualitative Bewertung

Die Professorenvorgabe verlangt neben Kennzahlen auch Interpretierbarkeit, Effizienz und Wartbarkeit. Die folgende Matrix ist eine transparente fachliche Bewertung auf einer Skala von 1 (schwach) bis 5 (stark); sie ersetzt keine Messwerte, sondern dokumentiert den Produktions-Trade-off."""
            ),
            code(
                """decision = pd.DataFrame({
    "Kriterium": ["räumliche CV-Güte", "Test-/Produktionsnähe", "Interpretierbarkeit",
                  "Trainingsökonomie", "Wartbarkeit"],
    "Gewicht": [0.40, 0.20, 0.15, 0.10, 0.15],
    "HGB": [5, 5, 3, 4, 4],
    "Random Forest": [5, 4, 3, 2, 3],
    "Ridge": [3, 3, 5, 5, 5],
    "MLP": [3, 2, 2, 1, 2],
    "Kategorien-Median": [2, 2, 5, 5, 5],
})
scores = {
    model: float((decision[model] * decision["Gewicht"]).sum())
    for model in decision.columns[2:]
}
display(decision.style.format({"Gewicht": "{:.0%}"}).hide(axis="index"))
display(pd.Series(scores, name="gewichteter Score / 5").sort_values(ascending=False).to_frame())
print("Hinweis: Ordinales Entscheidungshilfsmittel; quantitative Messwerte bleiben separat.")"""
            ),
            code(
                """importance = pd.DataFrame(
    report["permutation_importance_on_calibration_sample"]["results"]
).sort_values("mae_increase_mean").tail(10)
ax = importance.plot.barh(x="feature", y="mae_increase_mean",
                          xerr="mae_increase_std", color=COLORS["teal"], legend=False)
ax.set(title="Permutationswichtigkeit auf Kalibrierungsdaten",
       xlabel="MAE-Anstieg nach Permutation", ylabel="")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## Finale Modellentscheidung und kritische Interpretation

- MAE 1,413 €/m² und R² 0,584 auf unbekannten Raumblöcken.
- 38,3 % MAE-Verbesserung gegenüber der fachlichen Baseline.
- Das nominelle 90%-Band erreicht nur 86,8 %: räumlicher Shift verletzt perfekte Austauschbarkeit. Die App zeigt daher empirisch ca. 87 % statt einer falschen 90%-Garantie.
- Neue Gebäude sind mit MAE 1,64–1,91 €/m² schwieriger; diese Grenze wird sichtbar.
- Wichtigkeit ist prädiktiv und nicht kausal."""
            ),
            markdown(
                """## Go/No-Go und Übergabe an K

**Go mit sichtbaren Grenzen:** HGB erfüllt Daten-, Generalisierungs- und Nutzen-KPIs und gewinnt auch den dokumentierten Produktions-Trade-off. Die Unterdeckung des Intervalls und die schwächere Güte bei Neubauten verhindern keine Demonstrations-App, verlangen aber klare Warnungen.

An K werden `models/zensus_hgb.joblib`, Metadaten mit fester Feature-Reihenfolge, regionale Profile, GREIX-Zeitreihen und die gemessenen Qualitätskennzahlen übergeben. Das Testset bleibt nach dieser Entscheidung unverändert."""
            ),
        ],
    )

    knowledge = notebook(
        "06 · K – Wissensextraktion",
        "Vom Modelloutput zum nachvollziehbaren Umzugsaufschlag und Budgetsignal.",
        [
            markdown(
                """## Position der K-Phase

Knowledge Transfer bedeutet mehr als Deployment: Technische Ergebnisse werden so dokumentiert, visualisiert und in eine Anwendung übersetzt, dass die Zielgruppen aus Q damit eine echte Entscheidung vorbereiten können. MietCheck überführt das trainierte Modell deshalb nicht als isolierte Prognose, sondern als nachvollziehbare Vergleichsreise.

| Übergabeartefakt | Funktion in der App |
|---|---|
| `zensus_hgb.joblib` + Metadaten | reproduzierbarer Bestandsanker |
| regionale Zensus-Profile | schnelle Laufzeit ohne Rohdaten-Download |
| GREIX-Quartalswerte | aktueller Angebotsmarkt und Markt-IQR |
| Conformal-Halbbreiten | sichtbares Modellband |
| Daten-/Modellkarte | Quellen, Zweck, Risiken und Grenzen |
| getestete App-Logik | Umzugsaufschlag und Mietbelastung |
| MLflow-Runs + Registry | Parameter, Metriken, Signatur und Champion-Version |
| SHA-256-Modellmanifest | überprüfbare Train-/Serving-Lineage |

Die produktive App speichert keine persönlichen Eingaben und benötigt zur Laufzeit kein Training."""
            ),
            markdown(
                """## MLOps- und Governance-Nachweis

Die drei rechenintensiven Entscheidungsschritte werden zusätzlich zu den versionierten JSON-Berichten in MLflow dokumentiert:

| MLflow-Run | QUA³CK-Bezug | Inhalt |
|---|---|---|
| Algorithmusvergleich | A¹ | fünf Modellfamilien, Spatial CV und Vergleichsmetriken |
| HGB-Tuning | A³ | acht Kandidaten, Parameter und gesperrte Datenpartitionen |
| finales Modell | C/K | Testmetriken, Intervall-Coverage, Governance-Dokumente und Modellartefakt |

Das finale Modell ist als `MietCheck-Zensus-Stock-Rent` Version 1 mit dem Alias `@champion` registriert. `models/model_manifest.json` sichert Joblib-Modell, Metadaten und Evaluation per SHA-256. GitHub Actions prüft Code, Datenverträge, Modell- und Segment-Gates sowie den Docker-Build.

**Serving-Entscheidung:** Das als Registry-Version dokumentierte Modellartefakt erzeugt in einem reproduzierbaren Batch-Schritt 37 regionale Profile. Streamlit kombiniert diese geprüften ML-Ausgaben interaktiv mit GREIX und persönlichen Eingaben. Dadurch benötigt die öffentliche App weder Trainingsmatrix noch laufenden MLflow-Server."""
            ),
            markdown(
                """## Drei Mietrealitäten

Der Erkenntniswert liegt nicht in einer weiteren „fairen Miete“, sondern in der Trennung von **Bestand 2022**, **Angebotsmarkt Q1/2026** und **persönlicher Situation**. Die Differenz zwischen Bestand und Angebot wird deskriptiv als Umzugsaufschlag bezeichnet."""
            ),
            code(
                """profiles = pd.read_csv(ROOT / "data/app/region_profiles.csv")
greix = pd.read_csv(ROOT / "data/app/greix_quarterly.csv")
profiles["stock_reference_eur_sqm"] = profiles["stock_2022_age0_size1_eur_sqm"]
profiles["moving_premium_eur_sqm"] = (
    profiles["asking_median_eur_sqm"] - profiles["stock_reference_eur_sqm"]
)
profiles["moving_premium_pct"] = (
    profiles["moving_premium_eur_sqm"] / profiles["stock_reference_eur_sqm"] * 100
)

ranking = profiles[["region", "stock_reference_eur_sqm", "asking_median_eur_sqm",
                    "moving_premium_eur_sqm", "moving_premium_pct"]].sort_values(
                        "moving_premium_pct", ascending=False
                    )
display(ranking.head(12).round(2).style.hide(axis="index"))"""
            ),
            code(
                """fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(profiles["stock_reference_eur_sqm"], profiles["asking_median_eur_sqm"],
           s=45, color=COLORS["blue"], alpha=.8)
limit = max(profiles["asking_median_eur_sqm"].max(), profiles["stock_reference_eur_sqm"].max()) + 1
ax.plot([0, limit], [0, limit], linestyle="--", color=COLORS["grey"], label="kein Abstand")
for _, row in profiles.nlargest(5, "moving_premium_eur_sqm").iterrows():
    ax.annotate(row["region"], (row["stock_reference_eur_sqm"], row["asking_median_eur_sqm"]),
                xytext=(4, 3), textcoords="offset points", fontsize=8)
ax.set(xlabel="modellierter Bestandsanker 2022 €/m²",
       ylabel="GREIX-Angebotsmedian Q1/2026 €/m²",
       title="Bestand und aktueller Angebotsmarkt sind zwei Mietrealitäten")
ax.legend(); plt.tight_layout(); plt.show()"""
            ),
            code(
                """region = "Berlin"
timeline = greix[(greix["region"] == region) & (greix["year"] >= 2019)].copy()
timeline["date"] = pd.PeriodIndex(timeline["period"], freq="Q").to_timestamp(how="end")
ax = timeline.plot(x="date", y="asking_median_eur_sqm", color=COLORS["blue"], legend=False)
ax.fill_between(timeline["date"], timeline["asking_p25_eur_sqm"],
                timeline["asking_p75_eur_sqm"], color=COLORS["blue"], alpha=.15,
                label="Markt-IQR")
ax.set(title=f"{region}: Angebotsmiete und Marktstreuung", xlabel="", ylabel="€/m²")
ax.legend(); plt.tight_layout(); plt.show()"""
            ),
            code(
                """def scenario(region, area_sqm, net_income, current_cold_rent,
                 building_after_1990=False):
    row = profiles.loc[profiles["region"].eq(region)].iloc[0]
    size = int(area_sqm > 65)
    age = int(building_after_1990)
    stock_sqm = row[f"stock_2022_age{age}_size{size}_eur_sqm"]
    half_width = row[f"interval_age{age}_size{size}_half_width_eur_sqm"]
    asking_sqm = row["asking_median_eur_sqm"]
    return pd.Series({
        "Bestandsanker monatlich": stock_sqm * area_sqm,
        "Angebotsmedian monatlich": asking_sqm * area_sqm,
        "aktuelle persönliche Miete": current_cold_rent,
        "Umzugsaufschlag vs. Bestand": (asking_sqm - stock_sqm) * area_sqm,
        "Belastung aktuell": current_cold_rent / net_income,
        "Belastung am Angebotsmedian": asking_sqm * area_sqm / net_income,
        "Modell-Halbbreite monatlich": half_width * area_sqm,
    })

example = scenario("Berlin", area_sqm=70, net_income=3_200, current_cold_rent=850)
display(example.to_frame("Wert").style.format("{:.2f}"))"""
            ),
            code(
                """values = example[["Bestandsanker monatlich", "aktuelle persönliche Miete",
                  "Angebotsmedian monatlich"]]
ax = values.plot.bar(color=[COLORS["teal"], COLORS["navy"], COLORS["amber"]], legend=False)
ax.set(title="Beispielszenario Berlin · 70 m²", ylabel="Nettokaltmiete pro Monat (€)", xlabel="")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## Wissensgewinn und Handlungsnutzen

- Der Umzugsaufschlag macht sichtbar, warum Bestandsmietende einen Umzug als wesentlich teurer erleben können.
- Die persönliche Belastung übersetzt €/m² in eine haushaltsnahe Größe, ohne eine starre „leistbar“-Entscheidung vorzugeben.
- Markt-IQR und Modellband beantworten unterschiedliche Fragen und bleiben getrennt.
- München, Berlin und andere angespannte Märkte zeigen große Abstände; dies ist eine deskriptive Beobachtung, keine Kausalbehauptung.
- Nutzerinnen und Nutzer erhalten Datenstand, Quelle, Coverage und Modellgrenzen direkt am Ergebnis.

**Kein Mietspiegel, keine Rechtsberatung, keine individuelle Angebotsprognose.**"""
            ),
            markdown(
                """## Nutzerführung in der Streamlit-App

1. Region, Wohnfläche und Baujahr wählen.
2. Optional aktuelle Nettokaltmiete und Haushaltsnettoeinkommen eingeben.
3. Drei Werte getrennt lesen: persönliche Miete, Bestandsanker, Angebotsmedian.
4. Umzugsaufschlag und persönliche Mehrbelastung interpretieren.
5. Marktverlauf, IQR, Modellband, Coverage und Quellen prüfen.

Die App zeigt damit nicht nur **was** das Modell schätzt, sondern auch **wann**, **für welchen Raum**, **mit welcher Unsicherheit** und **wofür die Zahl nicht verwendet werden darf**."""
            ),
            markdown(
                """## Portfolio- und Deployment-Nachweis

- responsive Streamlit-App unter der reservierten URL `mietcheck.streamlit.app`,
- öffentlich nachvollziehbares GitHub-Repository mit Installations- und Reproduktionsanleitung,
- 33 automatisierte Tests, ML-Release-Gates und GitHub Actions,
- drei MLflow-Runs, Model Registry Version 1 mit Alias `@champion`,
- SHA-256-Modelllineage und reproduzierbarer Docker-Container,
- sieben vollständig ausgeführte QUA³CK-Notebooks,
- Datenkarte, Modellkarte, Risiko-/Ethikdokument und Demo-Runbook,
- Präsentation und schriftliche Ausarbeitung.

Die App bleibt bis zur gemeinsamen Abnahme privat. Erst danach wird ihre öffentliche Sichtbarkeit freigegeben."""
            ),
            markdown(
                """## Schlussfolgerung

Der fachliche Mehrwert liegt nicht in maximaler Scheingenauigkeit, sondern in einer überprüfbaren Entscheidungshilfe: **Bestand, Angebot und persönliche Belastung bleiben drei sauber getrennte Realitäten.** Das ML-Modell liefert den kleinräumigen Bestandsanker; aktuelle Marktdaten und persönliche Eingaben werden methodisch getrennt ergänzt. Genau diese Übersetzung von Big Data zu einer verständlichen Nutzerentscheidung schließt den QUA³CK-Prozess."""
            ),
        ],
    )

    return {
        "00_gesamtueberblick_qua3ck.ipynb": overview,
        "01_question.ipynb": question,
        "02_understanding_the_data.ipynb": understanding,
        "03_algorithmenauswahl.ipynb": algorithms,
        "04_modellentwicklung.ipynb": development,
        "05_kreuzvalidierung.ipynb": validation,
        "06_wissensextraktion.ipynb": knowledge,
    }


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    notebooks = build_notebooks()
    for filename, content in notebooks.items():
        path = NOTEBOOK_DIR / filename
        nbf.write(content, path)
        print(f"Generated {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
