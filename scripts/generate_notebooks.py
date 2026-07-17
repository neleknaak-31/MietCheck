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
| Q · Quality | Sind Quellen, Werte und Joins belastbar? | `01_qualitaetspruefung.ipynb` |
| U · Understanding | Wie verteilen sich Ziel und Merkmale räumlich? | `02_understanding_the_data.ipynb` |
| A¹ · Auswahl | Welche Modellfamilie generalisiert räumlich? | `03_algorithmenauswahl.ipynb` |
| A² · Anpassung | Welche Parameter und Features helfen? | `04_modellentwicklung.ipynb` |
| A³ · Anwendung | Wie wird das Modell kalibriert und gespeichert? | `04_modellentwicklung.ipynb` |
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

    quality = notebook(
        "01 · Q – Qualitätsprüfung",
        "Quellen, Schema, Zielgrain, Missingness und amtliche Unsicherheit.",
        [
            markdown(
                """## Qualitätslogik

Die Modellzeile ist eindeutig durch `GITTER_ID_100m × Gebäudealterklasse × Wohnungsgrößenklasse`. Kontextquellen werden zunächst je Gitterzelle validiert und anschließend als `many_to_one` an das Zielgrain gejoint. Zielwerte werden nie imputiert."""
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
display(quality_summary)"""
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
                """## Kritische Entscheidungen

- Das amtliche Zeichen `–` bedeutet in den ausgewählten Zensusdateien **exakt beziehungsweise auf 0 geändert**, nicht „fehlend“. Der Parser schützt diese Semantik mit Tests.
- `KLAMMERN` wird als Unsicherheitsflag erhalten.
- Das Unsicherheitsflag der **Zielmiete** wird nur ausgewertet, niemals als Feature verwendet.
- Die Roharchive bleiben unverändert; SHA-256-Hashes dokumentieren den exakten Stand.
- Keine Portal-Scrapes und keine personenbezogenen Daten."""
            ),
        ],
    )

    understanding = notebook(
        "02 · U – Understanding the Data",
        "Explorative Analyse von 2,06 Mio. Zielzeilen und räumlichem Kontext.",
        [
            markdown(
                """## Daten laden

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
                """## Faires Design

600.000 identische Zeilen, 660 räumliche 25-km-Blöcke und drei identische `GroupKFold`-Splits für Baseline, Ridge, Random Forest, Histogram Gradient Boosting und MLP. Primäre Metrik ist der MAE in €/m²."""
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
                """## Entscheidung

Histogram Gradient Boosting gewinnt mit MAE 1,305 €/m² knapp vor Random Forest (1,320), trainiert aber etwa 2,4-mal schneller. Der kleine Fehlerabstand wird nicht als statistisch große Überlegenheit verkauft; Random Forest bleibt Challenger. Ridge und Kategorien-Median bleiben interpretierbare Referenzen. Das MLP erreichte sein Iterationslimit und war deutlich langsamer."""
            ),
        ],
    )

    development = notebook(
        "04 · A²/A³ – Anpassung und Anwendung",
        "Räumliches HGB-Tuning, inkrementelle Feature-Ablation und Modellartefakt.",
        [
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
                """## Ergebnis

Kandidat 6 (`learning_rate=.06`, 127 Blätter, 100 Mindestbeobachtungen je Blatt, L2=5) besitzt den niedrigsten mittleren und schlechtesten Fold-MAE. Standort bringt den größten Effekt; numerischer Kontext und Qualitätsflags verbessern jedoch alle Folds und bleiben deshalb im 15-Feature-Modell."""
            ),
        ],
    )

    validation = notebook(
        "05 · C – Comparing & Kreuzvalidierung",
        "Finale räumliche Güte, Baseline, Intervalle, Subgruppen und Erklärbarkeit.",
        [
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
                """## Kritische Interpretation

- MAE 1,413 €/m² und R² 0,584 auf unbekannten Raumblöcken.
- 38,3 % MAE-Verbesserung gegenüber der fachlichen Baseline.
- Das nominelle 90%-Band erreicht nur 86,8 %: räumlicher Shift verletzt perfekte Austauschbarkeit. Die App zeigt daher empirisch ca. 87 % statt einer falschen 90%-Garantie.
- Neue Gebäude sind mit MAE 1,64–1,91 €/m² schwieriger; diese Grenze wird sichtbar.
- Wichtigkeit ist prädiktiv und nicht kausal."""
            ),
        ],
    )

    knowledge = notebook(
        "06 · K – Wissensextraktion",
        "Vom Modelloutput zum nachvollziehbaren Umzugsaufschlag und Budgetsignal.",
        [
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
        ],
    )

    return {
        "00_gesamtueberblick_qua3ck.ipynb": overview,
        "01_qualitaetspruefung.ipynb": quality,
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
