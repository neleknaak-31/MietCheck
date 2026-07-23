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
import pandas as pd
import matplotlib.pyplot as plt

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


def notebook_metadata() -> dict:
    return {
        "kernelspec": {
            "display_name": "Python (MietCheck)",
            "language": "python",
            "name": "mietcheck",
        },
        "language_info": {"name": "python", "version": "3.12"},
    }


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
        metadata=notebook_metadata(),
    )


def q_phase() -> nbf.NotebookNode:
    return nbf.v4.new_notebook(
        cells=[
            markdown(
                """# 🏠 MietCheck · Q-Phase

**Question – Problem, Forschungsfrage, Zielgruppen, Nutzenversprechen und Erfolgskriterien**

Mietpreise werden meist entweder als historischer Bestand, aktuelles Angebot oder persönliche Belastung betrachtet. MietCheck verbindet diese Perspektiven, ohne ihre unterschiedlichen Messkonzepte zu vermischen.

### 🔬 Zentrale Forschungsfrage

> **Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren erklären die Bestandsmiete und was bedeutet der Abstand für eine konkrete Wohnsituation?**

Die App trennt drei Mietrealitäten:

1. den modellierten lokalen **Bestandsanker** aus dem Zensus 2022,
2. den aktuellen **Angebotsmarkt** aus GREIX 2026-Q1,
3. die **persönliche Vertragsmiete und Mietbelastung**.

Die Differenz aus Angebot und Bestand heißt **Umzugsaufschlag**. Sie ist ein deskriptiver Vergleich – keine zulässige oder „faire“ Miete.

### 🧭 Thematische Forschungsfragen

1. Wie stark variieren Zensus-Bestandsmieten innerhalb und zwischen Regionen?
2. Verbessern räumliche und strukturelle Merkmale eine fachliche Kategorien-Baseline?
3. Welches klassische Regressionsverfahren generalisiert auf unbekannte räumliche Gebiete?
4. Wie wirken Skalierung und Algorithmuswahl bei Ridge, SVM, Bäumen und neuronalen Netzen?
5. Wie groß ist der Abstand zum aktuellen GREIX-Angebotsmarkt?
6. Wie lässt sich Modellunsicherheit sichtbar und ohne Scheingenauigkeit kommunizieren?

### 🎯 Zielgruppen und Anwendungsnutzen

| Zielgruppe | Typische Entscheidung | Mehrwert in MietCheck |
|---|---|---|
| Bestandsmietende | Bleiben oder umziehen? | eigene Miete vs. Bestand vs. aktuelles Angebot |
| Wohnungssuchende | Welche Mehrkosten sind plausibel? | Umzugsaufschlag in €/m², Euro und Prozent |
| Studierende und Berufseinsteigende | Wie verändert sich die Belastung? | Anteil der Kaltmiete am Haushaltsnetto |
| Dateninteressierte | Wie unterscheiden sich Märkte? | Zeitreihe, Markt-IQR, Methodik und Grenzen |

### 🗂️ Datengrundlage und Scope

| Baustein | Versionierter Nachweis | Verwendung |
|---|---:|---|
| Zensus-Modellzeilen | 2.058.569 | Training und räumliche Evaluation |
| eindeutige 100-m-Zellen | 1.184.386 | kleinräumiger Bestandsanker |
| 25-km-Raumblöcke | 663 | leakage-arme Gruppensplits |
| GREIX-Märkte | 37 lokal + Deutschland | aktueller Angebotsmarkt |
| GREIX-Datenstand | 2026-Q1 | aktuelle Vergleichsebene |

- **ML-Ziel:** durchschnittliche Nettokaltmiete am 15.05.2022 im 100-m-Zensusgitter
- **Geografischer Scope:** Deutschland; aktuelle Marktwerte nur für belegte GREIX-Regionen
- **Datenschutz:** persönliche Eingaben werden nicht gespeichert
- **Abgrenzung:** keine adressgenaue Wohnungsschätzung, kein Mietspiegel, keine Rechts- oder Finanzberatung

### ⚖️ Marktumfeld und Alleinstellungsmerkmal

Destatis beschreibt den Bestand, Immobilienportale aktuelle Angebote, kommunale Mietspiegel einen rechtlich definierten lokalen Vergleich und Budgetrechner die persönliche Belastung. Für die dokumentiert geprüften öffentlichen Vergleichsangebote wurde keine Anwendung mit derselben Kombination gefunden:

> **kleinräumiges ML-Bestandsmodell + aktueller unabhängiger Angebotsmarkt + persönliche Mietbelastung + zwei getrennte Unsicherheitsarten**

Der Markt-IQR beschreibt die Streuung heutiger Angebote; das conformale Modellband beschreibt den Fehler des Zensusmodells. Beide werden sichtbar getrennt.

### ✅ Vorab definierte Erfolgskriterien

| Dimension | Go/No-Go-Regel | Ergebnis |
|---|---|---:|
| Big Data | mindestens 2 Mio. Modellzeilen | ✅ 2.058.569 |
| Algorithmusauswahl | Baseline + linear + SVM + Baum + Ensemble + NN | ✅ 7 Hauptkandidaten |
| Generalisierung | räumlich disjunkte Entwicklung, Kalibrierung und Test | ✅ 465 / 99 / 99 Blöcke |
| Nutzen | mindestens 15 % niedrigerer Test-MAE als Kategorienmedian | ✅ 38,3 % |
| Unsicherheit | separates Kalibrierungsset und gemessene Coverage | ✅ 99 Blöcke |
| Reproduzierbarkeit | Download, Hashes, Tests, CI und Notebooks | ✅ versioniert |
| Produkt | transparente Streamlit-App mit Quellen und Grenzen | ✅ umgesetzt |

### 🖥️ Umsetzungskonzept und App-Skizze

Die K-Phase übersetzt das Modell in drei App-Tabs: **Dein Mietbild**, **Marktverlauf** und **Methodik & Quellen**. Nutzerinnen und Nutzer wählen Region, Fläche und Baualtersklasse und können eigene Miete sowie Einkommen ergänzen. Ausgegeben werden Bestandsanker, Modellband, GREIX-Median, Markt-IQR, Umzugsaufschlag und persönliche Belastung.

![MietCheck-App: Eingaben und drei Mietrealitäten](../reports/streamlit_overview.png)

---

**Reproduzierbarkeit:** Die Q-Phase definiert Problem, Scope und Prüfkriterien bewusst ohne Analysecode. Die nachfolgenden Phasen führen die Berechnungen aus und verweisen auf versionierte Reports."""
            )
        ],
        metadata=notebook_metadata(),
    )


def u_phase() -> nbf.NotebookNode:
    return notebook(
        "🔎 U-Phase · Understanding the Data",
        "Quellenwahl, Datenqualität, Exploration, räumliche Struktur und Skalierung.",
        [
            markdown(
                """## 🗂️ Aufgabe 1: Datensätze auswählen und verstehen

### 1.1 Zensus 2022 – Trainingsbasis

Sieben amtliche Gitterprodukte werden über die `Gitter_ID_100m` verbunden: Nettokaltmiete nach Baualter/Wohnungsgröße, Bevölkerung, Haushaltsgröße, Eigentumsquote, Leerstand, Wohnfläche und Wohnungszahl. Lizenz: Datenlizenz Deutschland – Namensnennung 2.0.

### 1.2 GREIX – aktueller Markt

Der GREIX des Kiel Instituts liefert nominale quartalsweise Angebotsmieten. Er bleibt **außerhalb des Zensus-Trainingsziels**, weil beide Quellen unterschiedliche Zeitpunkte und Mietrealitäten messen.

| Quelle/Kennzahl | Wert | Einordnung |
|---|---:|---|
| Zensus-Ziel | Nettokaltmiete in €/m² | Stichtag 15.05.2022 |
| Modellzeilen | 2.058.569 | reproduzierbarer Join |
| eindeutige 100-m-Zellen | 1.184.386 | Deutschland |
| amtlich unsicheres Ziel | 11,5 % | Kennzeichnung bleibt erhalten |
| GREIX | 2.166 Beobachtungen | 2012-Q1 bis 2026-Q1 |

**Grain der Trainingsmatrix:** Eine Zeile steht für die Kombination aus einer 100-m-Gitterzelle, einer Baualtersklasse und einer Wohnungsgrößenklasse. Der aktuelle GREIX-Markt wird erst in der App auf Regionsebene ergänzt."""
            ),
            markdown(
                """## 📊 Aufgabe 2: Erste Graphen und deskriptive Analyse

Für die Visualisierung wird eine deterministische Stichprobe von höchstens 200.000 Zeilen verwendet. Die ML-Pipeline trainiert später auf der vollständigen bzw. jeweils dokumentierten Datenmenge. Die folgenden Codezellen erzeugen echte Analysen; reine Beschreibungs- und Ergebnistabellen stehen direkt als Markdown im Notebook."""
            ),
            code(
                """features = ["x_laea_m", "y_laea_m", "building_after_1990",
            "dwelling_over_65sqm", "population", "avg_household_size",
            "ownership_rate_pct", "vacancy_rate_pct", "avg_dwelling_area_sqm",
            "dwelling_count", "rent_eur_sqm", "spatial_block_25km"]
data = pd.read_parquet(ROOT / "data/processed/model_table.parquet", columns=features)
sample = data.sample(n=min(200_000, len(data)), random_state=2026)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
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
            markdown(
                """**Interpretation:** Die Zielverteilung ist rechtsschief und räumlich deutlich strukturiert. Hohe und niedrige Mieten bilden regionale Cluster statt zufälliger Einzelpunkte. Deshalb wäre ein zufälliger Zeilensplit zu optimistisch; die A- und C-Phase trennen vollständige 25-km-Raumblöcke."""
            ),
            markdown("## 🧹 Aufgabe 3: Fehlende Werte und Datenqualität"),
            code(
                """build = load_json("reports/dataset_build_report.json")
non_null = pd.Series(build["feature_non_null_share"]).sort_values()
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
                """## ⚖️ Aufgabe 4: Alles auf einen vergleichbaren Maßstab bringen

### 4.1 Wahl der Skalierungsmethode

`StandardScaler` transformiert jedes numerische Merkmal mit Mittelwert und Standardabweichung des jeweiligen **Trainingsfolds**:

**z = (x − μ<sub>train</sub>) / σ<sub>train</sub>**

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

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
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
                """### 4.2 Ergebnis und Auswirkungen auf die Algorithmen

| Modellfamilie | StandardScaler? | Fachlicher Grund |
|---|---:|---|
| Ridge | ja | Regularisierung hängt von der Merkmalsgröße ab |
| LinearSVR / RBF-SVR | ja | Abstände und Margin müssen vergleichbar sein |
| MLP | ja | stabilere Gradientenoptimierung |
| Decision Tree / Random Forest / HGB | nein | Schwellenaufteilungen sind skaleninvariant |

Die Skalierung steckt als Pipeline-Schritt in jedem CV-Fold und wird niemals vor dem Split auf den Gesamtdaten gefittet. So entsteht kein Leakage. Für den später ausgewählten HGB-Champion wird bewusst **kein** Scaler gespeichert, weil er fachlich unnötig wäre; der Skalierungsnachweis gehört zur fairen Auswahl der skalenempfindlichen Kandidaten."""
            ),
            markdown(
                """## ✅ Aufgabe 5: Zusammenfassung und Interpretation

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
        "🤖 A-Phase · Algorithm Selection, Adapting & Adjusting",
        "Klassische Modelle vergleichen, Features anpassen und Hyperparameter optimieren.",
        [
            markdown(
                """## 🤖 A¹: Auswahl geeigneter Algorithmen

Alle Hauptkandidaten erhalten dieselben 600.000 deterministischen Zeilen und dieselben drei `GroupKFold`-Splits über 25-km-Raumblöcke.

| Kandidat | Typ | StandardScaler? | Rolle |
|---|---|---:|---|
| Kategorienmedian | fachliche Baseline | nein | Mindestvergleich |
| Ridge | linear/regularisiert | ja | interpretierbare Baseline |
| LinearSVR | lineare SVM | ja | robuste epsilon-insensitive Regression |
| Decision Tree | einzelner Baum | nein | nichtlineare klassische Referenz |
| Random Forest | Bagging-Ensemble | nein | robuster Challenger |
| HistGradientBoosting | Boosting-Ensemble | nein | skalierbarer Kandidat |
| MLP | neuronales Netz | ja | zusätzlicher nichtlinearer Vergleich |

| Rang | Modell | CV-MAE ± Std. in €/m² |
|---:|---|---:|
| 1 | HistGradientBoosting | **1,305 ± 0,055** |
| 2 | Random Forest | 1,320 ± 0,053 |
| 3 | Decision Tree | 1,393 ± 0,037 |
| 4 | MLP | 1,397 ± 0,076 |
| 5 | Ridge | 1,632 ± 0,105 |
| 6 | LinearSVR | 1,635 ± 0,104 |
| 7 | Kategorienmedian | 1,719 ± 0,125 |"""
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
plot = ranking.sort_values("mean_mae", ascending=True)
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
            markdown(
                """| SVM-Variante | Zeilen | MAE in €/m² | Training je Fold |
|---|---:|---:|---:|
| LinearSVR | 10.000 | 1,620 | 0,017 s |
| RBF-SVR | 10.000 | **1,518** | 2,315 s |

Der Kernel verbessert den kleinen Machbarkeitstest, benötigt aber bereits rund das 137-Fache der Trainingszeit. Wegen des superlinearen Wachstums ist RBF-SVR kein glaubwürdiger Kandidat für den 600.000-Zeilen-Hauptvergleich."""
            ),
            markdown(
                """**A¹-Entscheidung:** HistGradientBoosting gewinnt den fairen Hauptvergleich (MAE ≈ 1,305 €/m²), knapp vor Random Forest. Es ist zugleich kompakter und schneller bei der Inferenz. SVM und Einzelbaum erfüllen den klassischen Methodenvergleich, erreichen aber nicht die beste räumliche Generalisierung."""
            ),
            markdown("## 🧩 A²: Feature Engineering und inkrementelle Anpassung"),
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

ax = ablation_df.plot(
    x="Feature-Set",
    y="MAE",
    marker="o",
    color=COLORS["teal"],
    legend=False,
)
ax.set(title="A²: zusätzlicher Informationswert der Feature-Gruppen",
       ylabel="mittlerer räumlicher CV-MAE (€/m²)", xlabel="")
ax.tick_params(axis="x", rotation=25)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """Die vier Stufen sind: Kategorien → + Lagekoordinaten → + Wohnumfeld → + amtliche Unsicherheitsindikatoren. Die Lage liefert den größten Zusatznutzen. Unsicherheitsindikatoren bleiben trotz kleinerem inkrementellem Effekt erhalten, weil sie die Datenqualität fachlich abbilden."""
            ),
            markdown("## ⚙️ A³: Automatisierte Hyperparameteroptimierung"),
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
fig, ax = plt.subplots(figsize=(9, 4.8))
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
                """## ✅ Ergebnis der A-Phase

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
        "✅ C-Phase · Conclude and Compare",
        "Finales Modell quantitativ, qualitativ und gegen Erfolgskriterien bewerten.",
        [
            markdown(
                """## 🔁 1. Vergleich der A-Phasen

A¹ wählt HGB aus sieben Kandidaten, A² prüft den Zusatznutzen der Feature-Gruppen und A³ optimiert acht HGB-Konfigurationen. Erst danach wird das Modell auf allen Entwicklungsblöcken trainiert. Kalibrierung und finaler Test bleiben räumlich disjunkt.

| Partition | Zeilen | 25-km-Blöcke | SHA-256-Präfix |
|---|---:|---:|---|
| Entwicklung | 1.518.322 | 465 | `efab4dce9c55` |
| Kalibrierung | 263.789 | 99 | `d1fe0f764572` |
| finaler Test | 276.458 | 99 | `7da06f24d239` |

Die drei Gruppen-Hashes sind versioniert. Damit lässt sich prüfen, dass kein Raumblock zwischen Entwicklung, Kalibrierung und Test wechselt."""
            ),
            markdown(
                """## 📏 2. Formale KPI-Validierung auf dem unangetasteten Test

| KPI | Ergebnis | Interpretation |
|---|---:|---|
| MAE | **1,413 €/m²** | mittlerer absoluter Fehler |
| MedianAE | 0,956 €/m² | robuster typischer Fehler |
| RMSE | 2,130 €/m² | gewichtet große Fehler stärker |
| R² | 0,584 | erklärte Varianz auf neuen Raumblöcken |
| Baseline-MAE | 2,292 €/m² | Kategorienmedian als Mindestvergleich |
| MAE-Verbesserung | **38,3 %** | Go-Regel von 15 % deutlich erfüllt |
| Intervall-Coverage | 86,8 % | empirisch bei nominal 90 % |"""
            ),
            code(
                """final = load_json("reports/final_model_evaluation.json")
point = final["test"]["point_metrics"]
baseline = final["test"]["category_median_baseline_metrics"]
interval = final["test"]["category_specific_90_percent_interval"]
comparison = pd.DataFrame({
    "Modell": ["Kategorienmedian", "HGB-Champion"],
    "Test-MAE": [baseline["mae"], point["mae"]],
})
ax = comparison.plot.bar(x="Modell", y="Test-MAE",
                         color=[COLORS["grey"], COLORS["teal"]], legend=False)
title = (
    "Finaler Test: "
    f"{final['test']['mae_improvement_vs_baseline']:.1%} weniger MAE"
)
ax.set(title=title, ylabel="MAE (€/m²)", xlabel="")
ax.tick_params(axis="x", rotation=0)
plt.tight_layout(); plt.show()"""
            ),
            markdown(
                """## 🎯 3. Unsicherheit mit Split Conformal Prediction

Absolute Residuen der **separaten Kalibrierungsblöcke** bestimmen kategoriespezifische 90-%-Bänder. Auf unbekannten Testregionen werden empirisch 86,8 % abgedeckt. Diese Unterdeckung gegenüber nominal 90 % wird als räumlicher Distribution Shift dokumentiert und nicht schöngerechnet.

| Teilgruppe | Zeilen | MAE in €/m² | Coverage | mittlere Bandbreite |
|---|---:|---:|---:|---:|
| amtliches Ziel sicher | 244.888 | 1,414 | 86,8 % | 5,472 €/m² |
| amtliches Ziel unsicher | 31.570 | 1,405 | 87,2 % | 5,390 €/m² |
| alt / klein | 81.662 | 1,436 | 87,4 % | 5,753 €/m² |
| alt / groß | 114.791 | **1,170** | 87,6 % | 4,636 €/m² |
| neu / klein | 29.417 | 1,907 | 85,2 % | 6,954 €/m² |
| neu / groß | 50.588 | 1,642 | 85,1 % | 6,003 €/m² |

Die Teilgruppenprüfung zeigt den schwierigsten Bereich offen: Neuere kleine Wohnungen besitzen den höchsten MAE und das breiteste Band."""
            ),
            markdown(
                """## ⚖️ 4. Qualitative Bewertungsmatrix

| Kriterium | HGB | Random Forest | LinearSVR/RBF | Einzelbaum |
|---|---:|---:|---:|---:|
| räumlicher CV-MAE | sehr gut | sehr gut | schwächer | mittel |
| Skalierbarkeit auf 2,06 Mio. | sehr gut | gut | linear gut / RBF schwach | sehr gut |
| Artefakt/Inference | sehr gut | mittel | gut / schwach | sehr gut |
| nichtlineare Interaktionen | sehr gut | sehr gut | kernelabhängig | begrenzt |
| Transparenz | mittel | mittel | mittel | hoch |

Die Wahl von HGB basiert damit nicht nur auf MAE, sondern auf Generalisierung, Rechenaufwand und Deployment-Tauglichkeit."""
            ),
            markdown("## 🧭 5. Feature-Wirkung und Plausibilität"),
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
                """## ✅ 6. Finale Entscheidung und Grenzen

Alle vorab definierten Gates sind erfüllt: Big Data, räumlich disjunkte Splits, sieben Hauptkandidaten, >15 % Baseline-Verbesserung, separates Kalibrierungsset und reproduzierbare Artefakte. Der HGB-Champion wird deshalb an K übergeben.

| Entscheidung | Ergebnis |
|---|---|
| Champion | `HistGradientBoostingRegressor` |
| Test-MAE | 1,413 €/m² |
| Verbesserung vs. Baseline | 38,3 % |
| empirische Coverage | 86,8 % |
| Freigabe an K | ✅ ja |

**Grenzen:** keine Ausstattung, Energieklasse, Etage oder adressgenaue Mikrolage; Zensus-Stichtag 2022; GREIX nur für abgedeckte Märkte; empirische Coverage unter nominal 90 %; keine Rechtsberatung und kein amtlicher Mietspiegel."""
            ),
        ],
    )


def k_markdown() -> str:
    return """# 🚀 K-Phase · Knowledge Transfer

## 🎯 1. Ziel

Die K-Phase übersetzt das räumlich validierte Zensusmodell in die Streamlit-App **MietCheck**. Der Erkenntnisgewinn ist nicht „die eine richtige Miete“, sondern die methodisch saubere Trennung von Bestandsanker 2022, aktuellem GREIX-Angebotsmarkt und persönlicher Mietbelastung.

## 🏗️ 2. Architektur der Streamlit-Anwendung

1. Versioniertes HGB-Modell und Metadaten erzeugen regionale Bestandsprofile.
2. GREIX liefert aktuelle Angebotsmediane und Interquartilsabstände.
3. `src/app_logic.py` berechnet Umzugsaufschlag und persönliche Belastung.
4. `app.py` stellt Ergebnisse, Zeitbezug, Quellen, Unsicherheit und Grenzen interaktiv dar.
5. Die Laufzeit-App benötigt weder Rohdaten noch Trainingsmatrix oder MLflow-Server.

## 🖥️ 3. UI/UX und Nutzerführung

- **Dein Mietbild:** Region, Fläche, Baualter, persönliche Kaltmiete und Einkommen
- **Drei getrennte Werte:** eigene Miete, ML-Bestandsanker, GREIX-Angebotsmedian
- **Marktverlauf:** Quartalszeitreihe plus Markt-IQR
- **Methodik & Quellen:** Datenstand, Spatial Holdout, Modellvergleich, Coverage und Disclaimer
- **Responsiv:** klare Karten, wenige Farben und dieselbe visuelle Sprache wie die Präsentation

## 🔄 4. Toolentwicklung und Datenintegration

Öffentliche Downloads werden automatisiert bezogen, per SHA-256 dokumentiert und in Rohdaten, Trainingsmatrix, Reports und kleine App-Datenprodukte getrennt. GitHub Actions führt Ruff, Pytest, Datenverträge, Modellgates und Docker-Build aus. MLflow protokolliert A¹, A³ und das finale C/K-Artefakt; die Registry markiert den Champion.

## 🤖 5. ML-Integration

Der `HistGradientBoostingRegressor` nutzt 15 räumliche, wohnungsbezogene und qualitätsbezogene Merkmale. Er benötigt keinen `StandardScaler`; skalierte Pipelines wurden in A¹ korrekt für Ridge, LinearSVR, RBF-SVR und MLP verwendet. Split Conformal Prediction liefert kategoriespezifische Modellbänder. Das Modellartefakt, Metadaten und Evaluation sind über ein SHA-256-Manifest verbunden.

## 📸 6. App-Screenshots für Präsentation und Dokumentation

- `reports/streamlit_overview.png` – Eingaben, drei Mietrealitäten und Umzugsaufschlag
- `reports/streamlit_market.png` – aktueller Markt und Zeitreihe
- `reports/streamlit_method.png` – Methodik, Quellen, Modellgüte und Grenzen

Die Präsentation führt ohne Live-Demo durch Q, U, A, C und K. Die Screenshots sind belastbarer als ein Netzwerk-abhängiger Live-Ablauf und entsprechen dem Prüfhinweis.

## 💡 7. Ergebnis und Produktnutzen

MietCheck basiert auf 2.058.569 Modellzeilen und aktuellen GREIX-Daten bis 2026-Q1. Der finale räumliche Test-MAE beträgt 1,413 €/m², eine Verbesserung von 38,3 % gegenüber dem Kategorienmedian. Die empirische 90-%-Intervall-Coverage liegt bei 86,8 % und wird sichtbar kommuniziert.

Der USP ist die quelloffene Verbindung aus **kleinräumigem ML-Bestandsanker, aktuellem Angebotsmarkt, persönlicher Belastung und getrennten Unsicherheiten**. Die App bleibt bis zur gemeinsamen Endabnahme privat; Repository, Methode und Artefakte sind öffentlich nachvollziehbar.

## ⚠️ 8. Grenzen und verantwortungsvolle Nutzung

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
        if (
            old.is_file()
            and old.suffix in {".ipynb", ".md"}
            and old.name
            not in {
                *expected,
                "K-Phase.md",
            }
        ):
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
