# ruff: noqa: E501
"""Generate the MietCheck notebooks in the proven Q-, U-, A-, C-, K-phase layout.

The structure deliberately mirrors the course's 1.0 reference project while
retaining MietCheck's stronger spatial validation, uncertainty calibration and
MLOps evidence. Computationally expensive experiments remain in tested scripts;
the notebooks inspect, visualise and interpret their versioned outputs.

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

**Reproduzierbarkeit:** Kennzahlen stammen aus versionierten JSON-/CSV-Artefakten. Die genannten Skripte erzeugen sie aus den öffentlichen Rohdaten erneut. Schwere Trainingsläufe liegen bewusst in getesteten Skripten, damit Notebook und produktive Pipeline dieselben Splits, Parameter und Reports verwenden."""


def markdown(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def notebook(title: str, subtitle: str, cells: list[nbf.NotebookNode]) -> nbf.NotebookNode:
    return nbf.v4.new_notebook(
        cells=[
            markdown(
                f"# {title}\n\n{subtitle}\n\n"
                "**Projekt:** MietCheck · Big Data & Data Analytics · QUA³CK"
            ),
            code(SETUP),
            *cells,
            markdown(FOOTER),
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python (MietCheck)",
                "language": "python",
                "name": "mietcheck",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )


def q_phase() -> nbf.NotebookNode:
    return notebook(
        "Q-Phase · Question",
        "Problem, Forschungsfrage, Zielgruppen, Nutzenversprechen und Erfolgskriterien.",
        [
            markdown(
                """## 1. Zentrale Forschungsfrage

> **Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren erklären die Bestandsmiete und was bedeutet der Abstand für eine konkrete Wohnsituation?**

MietCheck trennt drei Größen, die herkömmliche Rechner häufig vermischen:

1. den modellierten lokalen **Bestandsanker** aus dem Zensus 2022,
2. den aktuellen **Angebotsmarkt** aus GREIX 2026-Q1,
3. die **persönliche Vertragsmiete und Mietbelastung**.

Die Differenz aus Angebot und Bestand heißt in der App **Umzugsaufschlag**. Sie ist ein deskriptiver Vergleich, keine zulässige oder „faire“ Miete."""
            ),
            markdown(
                """## 2. Thematische Forschungsfragen

1. Wie stark variieren Zensus-Bestandsmieten innerhalb und zwischen Regionen?
2. Verbessern räumliche und strukturelle Merkmale eine fachliche Kategorien-Baseline?
3. Welches klassische Regressionsverfahren generalisiert auf unbekannte räumliche Gebiete?
4. Wie wirken Skalierung und Algorithmuswahl bei Ridge, SVM, Bäumen und neuronalen Netzen?
5. Wie groß ist der Abstand zum aktuellen GREIX-Angebotsmarkt?
6. Wie lässt sich Modellunsicherheit sichtbar und ohne Scheingenauigkeit kommunizieren?"""
            ),
            markdown(
                """## 3. Zielgruppe und Anwendungsnutzen

| Zielgruppe | Entscheidung | Mehrwert in der App |
|---|---|---|
| Bestandsmietende | Bleiben oder umziehen? | eigene Miete vs. Bestand vs. aktuelles Angebot |
| Wohnungssuchende | Welche Mehrkosten sind plausibel? | Umzugsaufschlag in €/m², Euro und Prozent |
| Studierende/Berufseinsteigende | Wie verändert sich die Belastung? | Anteil am Haushaltsnetto |
| Dateninteressierte | Wie unterscheiden sich Märkte? | Zeitreihe, IQR, Methodik und Grenzen |"""
            ),
            markdown(
                """## 4. Datenbasis, Scope und Grenzen

- **ML-Ziel:** durchschnittliche Nettokaltmiete am 15.05.2022 im 100-m-Zensusgitter
- **Aktueller Markt:** GREIX-Angebotsmieten bis 2026-Q1, methodisch getrennt vom Training
- **Geografischer Scope:** Deutschland; aktuelle Marktwerte nur für belegte GREIX-Regionen
- **Keine Behauptung:** keine adressgenaue Wohnungsschätzung, kein Mietspiegel, keine Rechts- oder Finanzberatung
- **Datenschutz:** persönliche Eingaben werden nicht gespeichert"""
            ),
            code(
                """build = load_json("reports/dataset_build_report.json")
greix = load_json("data/app/greix_metadata.json")

scope = pd.DataFrame([
    ("Zensus-Modellzeilen", f"{build['rows']:,}"),
    ("eindeutige 100-m-Zellen", f"{build['unique_grid_cells']:,}"),
    ("25-km-Raumblöcke", build["spatial_blocks_25km"]),
    ("GREIX-Regionen", greix["regions"]),
    ("GREIX-Datenstand", greix["latest_period"]),
], columns=["Scope-Nachweis", "Wert"])
display(scope.style.hide(axis="index"))"""
            ),
            markdown(
                """## 5. Marktumfeld und Alleinstellungsmerkmal

Destatis beschreibt den Bestand, Immobilienportale aktuelle Angebote, kommunale Mietspiegel einen rechtlich definierten lokalen Vergleich und Budgetrechner die persönliche Belastung. MietCheck verbindet erstmals in einer **quelloffenen, reproduzierbaren Nutzerreise**:

**kleinräumiges ML-Bestandsmodell + aktueller unabhängiger Angebotsmarkt + persönliche Mietbelastung + zwei getrennte Unsicherheitsarten.**

Der Markt-IQR beschreibt die Streuung heutiger Angebote; das conformale Modellband beschreibt den Fehler des Zensusmodells. Beide werden niemals vermischt."""
            ),
            markdown(
                """## 6. Erfolgskriterien vor dem finalen Test

| Dimension | Go/No-Go-Regel |
|---|---|
| Big Data | mindestens 2 Mio. reproduzierbare Modellzeilen |
| A¹ Auswahl | klassische Baseline plus lineare, SVM-, Baum-, Ensemble- und NN-Verfahren |
| Generalisierung | räumlich disjunkte Entwicklung, Kalibrierung und Test |
| Nutzen | mindestens 15 % niedrigerer Test-MAE als Kategorienmedian |
| Unsicherheit | separates Kalibrierungsset und empirisch gemessene Coverage |
| Reproduzierbarkeit | Download, Hashes, Tests, CI und ausgeführte Notebooks |
| Produkt | transparente Streamlit-App mit Quellen, Datenstand und Grenzen |"""
            ),
            code(
                """benchmark = load_json("reports/algorithm_benchmark.json")
final = load_json("reports/final_model_evaluation.json")
checks = pd.DataFrame([
    ("Big Data", build["rows"] >= 2_000_000, build["rows"]),
    ("mind. 7 Kandidaten inkl. Baseline", len(benchmark["models"]) >= 7, len(benchmark["models"])),
    ("MAE-Verbesserung ≥ 15 %", final["test"]["mae_improvement_vs_baseline"] >= .15,
     final["test"]["mae_improvement_vs_baseline"]),
    ("separate Kalibrierung", final["partition"]["calibration"]["blocks"] > 0,
     final["partition"]["calibration"]["blocks"]),
], columns=["Kriterium", "erfüllt", "Nachweis"])
display(checks.style.hide(axis="index"))"""
            ),
            markdown(
                """## 7. Web-App-Konzept

Die K-Phase übersetzt das Modell in drei App-Tabs: **Dein Mietbild**, **Marktverlauf** und **Methodik & Quellen**. Nutzerinnen und Nutzer wählen Region, Fläche und Baualtersklasse und können eigene Miete sowie Einkommen ergänzen. Ausgegeben werden Bestandsanker, Modellband, GREIX-Median, Markt-IQR, Umzugsaufschlag und persönliche Belastung."""
            ),
        ],
    )


def u_phase() -> nbf.NotebookNode:
    return notebook(
        "U-Phase · Understanding the Data",
        "Quellenwahl, Datenqualität, Exploration, räumliche Struktur und Skalierung.",
        [
            markdown(
                """## Aufgabe 1: Datensätze auswählen und verstehen

### 1.1 Zensus 2022 – Trainingsbasis

Sieben amtliche Gitterprodukte werden über die `Gitter_ID_100m` verbunden: Nettokaltmiete nach Baualter/Wohnungsgröße, Bevölkerung, Haushaltsgröße, Eigentumsquote, Leerstand, Wohnfläche und Wohnungszahl. Lizenz: Datenlizenz Deutschland – Namensnennung 2.0.

### 1.2 GREIX – aktueller Markt

Der GREIX des Kiel Instituts liefert nominale quartalsweise Angebotsmieten. Er bleibt **außerhalb des Zensus-Trainingsziels**, weil beide Quellen unterschiedliche Zeitpunkte und Mietrealitäten messen."""
            ),
            code(
                """build = load_json("reports/dataset_build_report.json")
greix_meta = load_json("data/app/greix_metadata.json")
quality = pd.DataFrame([
    ("Zensus-Ziel", build["target"]["name"], "15.05.2022"),
    ("Modellzeilen", f"{build['rows']:,}", "reproduzierbarer Join"),
    ("100-m-Zellen", f"{build['unique_grid_cells']:,}", "Deutschland"),
    ("Ziel unsicher", f"{build['target']['uncertain_share']:.1%}", "amtliche Kennzeichnung"),
    ("GREIX", f"{greix_meta['rows']:,} Beobachtungen", greix_meta["latest_period"]),
], columns=["Quelle/Kennzahl", "Wert", "Einordnung"])
display(quality.style.hide(axis="index"))"""
            ),
            markdown("## Aufgabe 2: Erste Graphen und deskriptive Analyse"),
            code(
                """features = ["x_laea_m", "y_laea_m", "building_after_1990",
            "dwelling_over_65sqm", "population", "avg_household_size",
            "ownership_rate_pct", "vacancy_rate_pct", "avg_dwelling_area_sqm",
            "dwelling_count", "rent_eur_sqm", "spatial_block_25km"]
data = pd.read_parquet(ROOT / "data/processed/model_table.parquet", columns=features)
sample = data.sample(n=min(200_000, len(data)), random_state=2026)
display(sample.describe(percentiles=[.05, .25, .5, .75, .95]).T.round(2))"""
            ),
            code(
                """fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].hist(sample["rent_eur_sqm"], bins=60, color=COLORS["blue"], alpha=.85)
axes[0].axvline(sample["rent_eur_sqm"].median(), color=COLORS["amber"], linestyle="--",
                label=f"Median {sample['rent_eur_sqm'].median():.2f} €/m²")
axes[0].set(title="Zielverteilung", xlabel="Nettokaltmiete €/m²", ylabel="Zellen")
axes[0].legend()
axes[1].scatter(sample["x_laea_m"], sample["y_laea_m"], c=sample["rent_eur_sqm"],
                s=2, alpha=.25, cmap="viridis")
axes[1].set(title="Räumliche Struktur im 100-m-Gitter", xlabel="LAEA x", ylabel="LAEA y")
plt.tight_layout(); plt.show()"""
            ),
            markdown("## Aufgabe 3: Fehlende Werte und Datenqualität"),
            code(
                """non_null = pd.Series(build["feature_non_null_share"]).sort_values()
missing = (1 - non_null).mul(100)
ax = missing.plot.barh(color=COLORS["teal"])
ax.set(title="Fehlende Werte der Strukturmerkmale", xlabel="fehlend (%)", ylabel="")
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f%%", padding=3)
plt.tight_layout(); plt.show()

assert build["rows"] >= 2_000_000
assert build["unique_grid_cells"] > 1_000_000
assert non_null.min() > .98"""
            ),
            markdown(
                """Fehlende Strukturmerkmale werden **innerhalb jedes Trainingsfolds** per Median imputiert; Missing-Indikatoren erhalten die Information, dass ein Wert fehlte. Das Ziel wird nie imputiert. Unsicherheitskennzeichen der amtlichen Quelle bleiben als Merkmale erhalten."""
            ),
            markdown(
                """## Aufgabe 4: Alles auf einen vergleichbaren Maßstab bringen (Skalierung)

### 4.1 Wahl der Skalierungsmethode

`StandardScaler` transformiert jedes numerische Merkmal mit Mittelwert und Standardabweichung des jeweiligen **Trainingsfolds**:

\\[
z = \\frac{x - \\mu_{train}}{\\sigma_{train}}
\\]

Das ist für Ridge, LinearSVR, RBF-SVR und MLP wichtig, weil Distanz, Regularisierung oder Gradienten sonst durch große Einheiten wie LAEA-Meter dominiert würden. Entscheidungsbaum, Random Forest und HistGradientBoosting benötigen keine Skalierung, weil Schwellenaufteilungen gegenüber monotoner Skalierung invariant sind."""
            ),
            code(
                """from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

scale_features = ["x_laea_m", "population", "ownership_rate_pct",
                  "vacancy_rate_pct", "avg_dwelling_area_sqm"]
train_like = sample[scale_features].iloc[:150_000]
imputed = SimpleImputer(strategy="median").fit_transform(train_like)
scaler = StandardScaler().fit(imputed)
scaled = pd.DataFrame(scaler.transform(imputed), columns=scale_features)

comparison = pd.DataFrame({
    "vorher Mittelwert": train_like.mean(),
    "vorher Standardabw.": train_like.std(ddof=0),
    "nachher Mittelwert": scaled.mean(),
    "nachher Standardabw.": scaled.std(ddof=0),
})
display(comparison.round(3))"""
            ),
            code(
                """fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
before = train_like.sample(5_000, random_state=2026)
after = scaled.sample(5_000, random_state=2026)
before.boxplot(ax=axes[0], rot=35)
after.boxplot(ax=axes[1], rot=35)
axes[0].set_title("Vor StandardScaler: Einheiten dominieren")
axes[1].set_title("Nach StandardScaler: vergleichbarer Maßstab")
axes[1].set_ylabel("z-Wert")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """### 4.2 Auswirkungen auf ML-Algorithmen

Die Skalierung steckt als Pipeline-Schritt in jedem CV-Fold und wird niemals vor dem Split auf den Gesamtdaten gefittet. So entsteht kein Leakage. Für den später ausgewählten HGB-Champion wird bewusst **kein** Scaler gespeichert, weil er fachlich unnötig wäre; der Skalierungsnachweis gehört zur fairen Auswahl der skalenempfindlichen Kandidaten."""
            ),
            markdown(
                """## Aufgabe 5: Zusammenfassung und Interpretation

- 2.058.569 Zeilen und 1.184.386 Gitterzellen erfüllen den Big-Data-Anspruch.
- Ziel und Merkmale zeigen starke räumliche Struktur; Random Split wäre zu optimistisch.
- Datenlücken sind gering, werden aber fold-intern behandelt und dokumentiert.
- Zensus und GREIX bleiben wegen unterschiedlicher Messkonzepte getrennt.
- StandardScaler ist für SVM/Ridge/MLP notwendig, für baumbasierte Verfahren nicht."""
            ),
        ],
    )


def a_phase() -> nbf.NotebookNode:
    return notebook(
        "A-Phase · Algorithm Selection, Adapting & Adjusting",
        "Klassische Modelle vergleichen, Features anpassen und Hyperparameter optimieren.",
        [
            markdown(
                """## A1: Auswahl geeigneter Algorithmen

Alle Hauptkandidaten erhalten dieselben 600.000 deterministischen Zeilen und dieselben drei `GroupKFold`-Splits über 25-km-Raumblöcke.

| Kandidat | Typ | StandardScaler? | Rolle |
|---|---|---:|---|
| Kategorienmedian | fachliche Baseline | nein | Mindestvergleich |
| Ridge | linear/regularisiert | ja | interpretierbare Baseline |
| LinearSVR | lineare SVM | ja | robuste epsilon-insensitive Regression |
| Decision Tree | einzelner Baum | nein | nichtlineare klassische Referenz |
| Random Forest | Bagging-Ensemble | nein | robuster Challenger |
| HistGradientBoosting | Boosting-Ensemble | nein | skalierbarer Kandidat |
| MLP | neuronales Netz | ja | zusätzlicher nichtlinearer Vergleich |"""
            ),
            code(
                """benchmark = load_json("reports/algorithm_benchmark.json")
ranking = pd.DataFrame(benchmark["ranking_by_mean_mae"])
labels = {
    "category_median": "Kategorienmedian", "ridge": "Ridge",
    "linear_svr": "LinearSVR", "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "hist_gradient_boosting": "HistGradientBoosting", "mlp": "MLP",
}
ranking["Modell"] = ranking["model"].map(labels)
display(ranking[["Modell", "mean_mae", "std_mae"]].round(3).style.hide(axis="index"))"""
            ),
            code(
                """plot = ranking.sort_values("mean_mae", ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(plot["Modell"], plot["mean_mae"], xerr=plot["std_mae"],
        color=[COLORS["teal"] if name == "HistGradientBoosting" else COLORS["blue"]
               for name in plot["Modell"]], alpha=.9)
ax.set(title="A¹: identische räumliche CV für sieben Kandidaten",
       xlabel="mittlerer MAE (€/m²; kleiner ist besser)", ylabel="")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """### Ergänzung: lineare und Kernel-SVM

Ein exakter RBF-SVR skaliert superlinear und ist für 600.000 Zeilen kein glaubwürdiger Produktionskandidat. Deshalb vergleicht ein ergänzender Machbarkeitstest LinearSVR und RBF-SVR auf 10.000 deterministischen Zeilen mit identischer räumlicher 3-Fold-Logik. Beide Pipelines enthalten den `StandardScaler` innerhalb des Folds."""
            ),
            code(
                """svm = load_json("reports/svm_kernel_benchmark.json")
svm_table = pd.DataFrame([
    {
        "Variante": name,
        "Zeilen": svm["scope"]["rows"],
        "MAE": details["summary"]["mae"]["mean"],
        "Training/Fold (s)": details["summary"]["training_seconds"]["mean"],
    }
    for name, details in svm["models"].items()
])
display(svm_table.round(3).style.hide(axis="index"))
assert svm["preprocessing"]["scaler"] == "StandardScaler"
assert svm["scope"]["not_full_benchmark"] is True"""
            ),
            markdown(
                """**A¹-Entscheidung:** HistGradientBoosting gewinnt den fairen Hauptvergleich (MAE ≈ 1,305 €/m²), knapp vor Random Forest. Es ist zugleich kompakter und schneller bei der Inferenz. SVM und Einzelbaum erfüllen den klassischen Methodenvergleich, erreichen aber nicht die beste räumliche Generalisierung."""
            ),
            markdown("## A2: Feature Engineering und inkrementelle Anpassung"),
            code(
                """ablation = load_json("reports/feature_ablation.json")
ablation_rows = []
for name, details in ablation["feature_sets"].items():
    ablation_rows.append({
        "Feature-Set": name,
        "Anzahl Merkmale": len(details["features"]),
        "MAE": details["summary"]["mean_mae"],
        "R²": details["summary"]["mean_r2"],
    })
ablation_df = pd.DataFrame(ablation_rows)
display(ablation_df.round(3).style.hide(axis="index"))

ax = ablation_df.plot(x="Feature-Set", y="MAE", marker="o", color=COLORS["teal"], legend=False)
ax.set(title="A²: zusätzlicher Informationswert der Feature-Gruppen",
       ylabel="mittlerer räumlicher CV-MAE (€/m²)", xlabel="")
ax.tick_params(axis="x", rotation=25)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """Die vier Stufen sind: Kategorien → + Lagekoordinaten → + Wohnumfeld → + amtliche Unsicherheitsindikatoren. Die Lage liefert den größten Zusatznutzen. Unsicherheitsindikatoren bleiben trotz kleinerem inkrementellem Effekt erhalten, weil sie die Datenqualität fachlich abbilden."""
            ),
            markdown("## A3: Automatisierte Hyperparameteroptimierung"),
            code(
                """tuning = load_json("reports/hgb_tuning.json")
tuning_df = pd.DataFrame([
    {
        "Kandidat": item["candidate"],
        "MAE": item["summary"]["mean_mae"],
        "Std.": item["summary"]["std_mae"],
        "Worst Fold": item["summary"]["worst_fold_mae"],
        "R²": item["summary"]["mean_r2"],
    }
    for item in tuning["candidates"]
]).sort_values("MAE")
display(tuning_df.round(3).style.hide(axis="index"))
print("Gewählt:", tuning["selected_candidate"], tuning["selected_parameters"])"""
            ),
            code(
                """fig, ax = plt.subplots(figsize=(9, 4.8))
ax.errorbar(tuning_df["Kandidat"].astype(str), tuning_df["MAE"],
            yerr=tuning_df["Std."], fmt="o", color=COLORS["blue"], capsize=4)
selected = str(tuning["selected_candidate"])
row = tuning_df[tuning_df["Kandidat"].astype(str) == selected].iloc[0]
ax.scatter([selected], [row["MAE"]], s=140, color=COLORS["teal"], zorder=3,
           label="gewählter Kandidat")
ax.set(title="A³: acht HGB-Konfigurationen auf Entwicklungsblöcken",
       xlabel="Kandidat", ylabel="CV-MAE (€/m²)")
ax.legend(); plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """Das theory-guided Grid variiert Lernrate, Iterationen, Blattzahl, Mindestblattgröße und L2-Regularisierung. Kalibrierungs- und Testblöcke bleiben während A¹–A³ gesperrt. Die Auswahl berücksichtigt mittleren MAE, Streuung und schlechtesten Fold – nicht nur einen Einzelwert."""
            ),
            markdown(
                """## Ergebnis der A-Phase

- **Champion:** `HistGradientBoostingRegressor`
- **Challenger:** Random Forest
- **Scaler:** in Ridge-, LinearSVR-, RBF-SVR- und MLP-Pipelines fold-intern; nicht beim baumbasierten Champion
- **Features:** Lage + Kategorien + Wohnumfeld + Unsicherheitsindikatoren
- **Tuning:** acht reproduzierbare Kandidaten ausschließlich auf Entwicklungsblöcken
- **Übergabe an C:** Parameter und Split-Hashes werden versioniert eingefroren"""
            ),
        ],
    )


def c_phase() -> nbf.NotebookNode:
    return notebook(
        "C-Phase · Conclude and Compare",
        "Finales Modell quantitativ, qualitativ und gegen Erfolgskriterien bewerten.",
        [
            markdown(
                """## 1. Vergleich der A-Phasen

A¹ wählt HGB aus sieben Kandidaten, A² prüft den Zusatznutzen der Feature-Gruppen und A³ optimiert acht HGB-Konfigurationen. Erst danach wird das Modell auf allen Entwicklungsblöcken trainiert. Kalibrierung und finaler Test bleiben räumlich disjunkt."""
            ),
            code(
                """final = load_json("reports/final_model_evaluation.json")
partition = pd.DataFrame([
    (name, details["rows"], details["blocks"], details["group_sha256"][:12])
    for name, details in final["partition"].items()
], columns=["Partition", "Zeilen", "25-km-Blöcke", "Gruppen-Hash"])
display(partition.style.hide(axis="index"))
assert partition["25-km-Blöcke"].sum() == 663
assert partition["Gruppen-Hash"].nunique() == 3"""
            ),
            markdown("## 2. Formale KPI-Validierung auf dem unangetasteten Test"),
            code(
                """point = final["test"]["point_metrics"]
baseline = final["test"]["category_median_baseline_metrics"]
interval = final["test"]["category_specific_90_percent_interval"]
kpis = pd.DataFrame([
    ("MAE", point["mae"], "€/m²", "kleiner besser"),
    ("MedianAE", point["median_ae"], "€/m²", "robuster typischer Fehler"),
    ("RMSE", point["rmse"], "€/m²", "bestraft große Fehler"),
    ("R²", point["r2"], "", "erklärte Varianz"),
    ("Baseline-MAE", baseline["mae"], "€/m²", "fachlicher Mindestvergleich"),
    ("MAE-Verbesserung", final["test"]["mae_improvement_vs_baseline"], "%", "Go ≥ 15 %"),
    ("Intervall-Coverage", interval["coverage"], "%", "nominal 90 %"),
], columns=["KPI", "Wert", "Einheit", "Interpretation"])
display(kpis.style.hide(axis="index").format({"Wert": "{:.3f}"}))"""
            ),
            code(
                """comparison = pd.DataFrame({
    "Modell": ["Kategorienmedian", "HGB-Champion"],
    "Test-MAE": [baseline["mae"], point["mae"]],
})
ax = comparison.plot.bar(x="Modell", y="Test-MAE",
                         color=[COLORS["grey"], COLORS["teal"]], legend=False)
ax.set(title=f"Finaler Test: {final['test']['mae_improvement_vs_baseline']:.1%} weniger MAE",
       ylabel="MAE (€/m²)", xlabel="")
ax.tick_params(axis="x", rotation=0)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## 3. Unsicherheit mit Split Conformal Prediction

Absolute Residuen der **separaten Kalibrierungsblöcke** bestimmen kategoriespezifische 90-%-Bänder. Auf unbekannten Testregionen werden empirisch 86,8 % abgedeckt. Diese Unterdeckung gegenüber nominal 90 % wird als räumlicher Distribution Shift dokumentiert und nicht schöngerechnet."""
            ),
            code(
                """subgroups = final["test"]["subgroups"]
subgroup_df = pd.DataFrame([
    {
        "Gruppe": name,
        "Zeilen": details["rows"],
        "MAE": details["point_metrics"]["mae"],
        "R²": details["point_metrics"]["r2"],
        "Coverage": details["interval_metrics"]["coverage"],
        "Bandbreite": details["interval_metrics"]["mean_width_eur_sqm"],
    }
    for name, details in subgroups.items()
])
display(subgroup_df.round(3).style.hide(axis="index"))"""
            ),
            markdown(
                """## 4. Qualitative Bewertungsmatrix

| Kriterium | HGB | Random Forest | LinearSVR/RBF | Einzelbaum |
|---|---:|---:|---:|---:|
| räumlicher CV-MAE | sehr gut | sehr gut | schwächer | mittel |
| Skalierbarkeit auf 2,06 Mio. | sehr gut | gut | linear gut / RBF schwach | sehr gut |
| Artefakt/Inference | sehr gut | mittel | gut / schwach | sehr gut |
| nichtlineare Interaktionen | sehr gut | sehr gut | kernelabhängig | begrenzt |
| Transparenz | mittel | mittel | mittel | hoch |

Die Wahl von HGB basiert damit nicht nur auf MAE, sondern auf Generalisierung, Rechenaufwand und Deployment-Tauglichkeit."""
            ),
            markdown("## 5. Feature-Wirkung und Plausibilität"),
            code(
                """importance = pd.DataFrame(
    final["permutation_importance_on_calibration_sample"]["results"]
).head(10).sort_values("mae_increase_mean")
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(importance["feature"], importance["mae_increase_mean"], color=COLORS["blue"])
ax.set(title="Permutation Importance auf separater Kalibrierungsstichprobe",
       xlabel="MAE-Anstieg bei Permutation (€/m²)", ylabel="")
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """Koordinaten dominieren, was zur bekannten räumlichen Mietstruktur passt. Wichtig: Permutation Importance ist keine Kausalitätsanalyse. Sie zeigt Modellabhängigkeit unter korrelierten Merkmalen, nicht den Effekt politischer oder individueller Maßnahmen."""
            ),
            markdown(
                """## 6. Finale Entscheidung und Grenzen

Alle vorab definierten Gates sind erfüllt: Big Data, räumlich disjunkte Splits, sieben Hauptkandidaten, >15 % Baseline-Verbesserung, separates Kalibrierungsset und reproduzierbare Artefakte. Der HGB-Champion wird deshalb an K übergeben.

**Grenzen:** keine Ausstattung, Energieklasse, Etage oder adressgenaue Mikrolage; Zensus-Stichtag 2022; GREIX nur für abgedeckte Märkte; empirische Coverage unter nominal 90 %; keine Rechtsberatung und kein amtlicher Mietspiegel."""
            ),
            code(
                """decision = {
    "Champion": final["model"]["type"],
    "Test-MAE": round(point["mae"], 3),
    "Verbesserung vs. Baseline": f"{final['test']['mae_improvement_vs_baseline']:.1%}",
    "Coverage": f"{interval['coverage']:.1%}",
    "Freigabe an K": (
        final["test"]["mae_improvement_vs_baseline"] >= .15
        and final["partition"]["test"]["blocks"] > 0
    ),
}
display(pd.Series(decision).to_frame("Entscheidung"))"""
            ),
        ],
    )


def k_markdown() -> str:
    return """# K-Phase · Knowledge Transfer

## 1. Ziel

Die K-Phase übersetzt das räumlich validierte Zensusmodell in die Streamlit-App **MietCheck**. Der Erkenntnisgewinn ist nicht „die eine richtige Miete“, sondern die methodisch saubere Trennung von Bestandsanker 2022, aktuellem GREIX-Angebotsmarkt und persönlicher Mietbelastung.

## 2. Architektur der Streamlit-Anwendung

1. Versioniertes HGB-Modell und Metadaten erzeugen regionale Bestandsprofile.
2. GREIX liefert aktuelle Angebotsmediane und Interquartilsabstände.
3. `src/app_logic.py` berechnet Umzugsaufschlag und persönliche Belastung.
4. `app.py` stellt Ergebnisse, Zeitbezug, Quellen, Unsicherheit und Grenzen interaktiv dar.
5. Die Laufzeit-App benötigt weder Rohdaten noch Trainingsmatrix oder MLflow-Server.

## 3. UI/UX und Nutzerführung

- **Dein Mietbild:** Region, Fläche, Baualter, persönliche Kaltmiete und Einkommen
- **Drei getrennte Werte:** eigene Miete, ML-Bestandsanker, GREIX-Angebotsmedian
- **Marktverlauf:** Quartalszeitreihe plus Markt-IQR
- **Methodik & Quellen:** Datenstand, Spatial Holdout, Modellvergleich, Coverage und Disclaimer
- **Responsiv:** klare Karten, wenige Farben und dieselbe visuelle Sprache wie die Präsentation

## 4. Toolentwicklung und Datenintegration

Öffentliche Downloads werden automatisiert bezogen, per SHA-256 dokumentiert und in Rohdaten, Trainingsmatrix, Reports und kleine App-Datenprodukte getrennt. GitHub Actions führt Ruff, Pytest, Datenverträge, Modellgates und Docker-Build aus. MLflow protokolliert A¹, A³ und das finale C/K-Artefakt; die Registry markiert den Champion.

## 5. ML-Integration

Der `HistGradientBoostingRegressor` nutzt 15 räumliche, wohnungsbezogene und qualitätsbezogene Merkmale. Er benötigt keinen `StandardScaler`; skalierte Pipelines wurden in A¹ korrekt für Ridge, LinearSVR, RBF-SVR und MLP verwendet. Split Conformal Prediction liefert kategoriespezifische Modellbänder. Das Modellartefakt, Metadaten und Evaluation sind über ein SHA-256-Manifest verbunden.

## 6. App-Screenshots für Präsentation und Dokumentation

- `reports/streamlit_overview.png` – Eingaben, drei Mietrealitäten und Umzugsaufschlag
- `reports/streamlit_market.png` – aktueller Markt und Zeitreihe
- `reports/streamlit_method.png` – Methodik, Quellen, Modellgüte und Grenzen

Die Präsentation führt ohne Live-Demo durch Q, U, A, C und K. Die Screenshots sind belastbarer als ein Netzwerk-abhängiger Live-Ablauf und entsprechen dem Prüfhinweis.

## 7. Ergebnis und Produktnutzen

MietCheck basiert auf 2.058.569 Modellzeilen und aktuellen GREIX-Daten bis 2026-Q1. Der finale räumliche Test-MAE beträgt 1,413 €/m², eine Verbesserung von 38,3 % gegenüber dem Kategorienmedian. Die empirische 90-%-Intervall-Coverage liegt bei 86,8 % und wird sichtbar kommuniziert.

Der USP ist die quelloffene Verbindung aus **kleinräumigem ML-Bestandsanker, aktuellem Angebotsmarkt, persönlicher Belastung und getrennten Unsicherheiten**. Die App bleibt bis zur gemeinsamen Endabnahme privat; Repository, Methode und Artefakte sind öffentlich nachvollziehbar.

## 8. Grenzen und verantwortungsvolle Nutzung

Kein Mietspiegel, keine Rechtsberatung, keine adressgenaue Angebotsprognose. Persönliche Eingaben werden nicht gespeichert. Regionen ohne GREIX-Abdeckung erhalten keine erfundenen aktuellen Marktwerte.

---

**Reproduzierbarkeit:** `README.md`, `docs/DATA_CARD.md`, `docs/MODEL_CARD.md`, `docs/RISK_AND_ETHICS.md`, `reports/` und die ausgeführten Phasen-Notebooks bilden die vollständige Nachweiskette.
"""


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    expected = {
        "Q-Phase.ipynb": q_phase(),
        "U-Phase.ipynb": u_phase(),
        "A-Phase.ipynb": a_phase(),
        "C-Phase.ipynb": c_phase(),
    }
    for old in NOTEBOOK_DIR.iterdir():
        if old.is_file() and old.suffix in {".ipynb", ".md"} and old.name not in {
            *expected,
            "K-Phase.md",
        }:
            old.unlink()
    for filename, content in expected.items():
        path = NOTEBOOK_DIR / filename
        nbf.write(content, path)
        print(f"Generated {path.relative_to(PROJECT_ROOT)}")
    knowledge_path = NOTEBOOK_DIR / "K-Phase.md"
    knowledge_path.write_text(k_markdown(), encoding="utf-8")
    print(f"Generated {knowledge_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
