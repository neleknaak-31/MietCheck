# QUA³CK-Notebook-Leitfaden

Stand: 19. Juli 2026

Die Dateinamen und die Phasenbündelung orientieren sich bewusst am mit 1,0
bewerteten Referenzprojekt des Moduls. MietCheck ergänzt räumliche Validierung,
SVM-Skalierungsstudie, conformale Unsicherheit und MLOps-Lineage.

| Phase | Artefakt | Inhalt | Reproduzierbare Evidenz |
|---|---|---|---|
| Q | `Q-Phase.ipynb` | Forschungsfrage, Zielgruppen, USP, Scope und Go/No-Go-Gates | `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md` |
| U | `U-Phase.ipynb` | Quellen, EDA, Missingness, Raumstruktur und StandardScaler-Vorher/Nachher | `download_data.py`, `build_dataset.py`, `model_table.parquet` |
| A¹/A²/A³ | `A-Phase.ipynb` | sieben Hauptkandidaten, SVM-Zusatzstudie, vier Feature-Ablationen und acht HGB-Tunings | `algorithm_benchmark.py`, `svm_kernel_benchmark.py`, `feature_ablation.py`, `tune_hgb.py` |
| C | `C-Phase.ipynb` | finaler Spatial Test, Baseline, Intervalle, Subgruppen, qualitative Matrix und Wichtigkeit | `train_final_model.py`, `final_model_evaluation.json` |
| K | `K-Phase.md` | App-Architektur, UX, MLOps, Screenshots, Nutzen und Grenzen | `app.py`, GREIX-/Regionsprofile, Governance-Dokumente |

## Ausführung

```text
python scripts/generate_notebooks.py
python scripts/execute_notebooks.py
```

`generate_notebooks.py` hält Struktur und Narrative konsistent.
`execute_notebooks.py` führt die vier Rechennotebooks mit dem Projektkernel aus,
bricht beim ersten Fehler ab, speichert alle Outputs und schreibt
`reports/notebook_execution.json`.

Der verifizierte Lauf umfasst 24 von 24 ausgeführte Codezellen ohne
Fehleroutput. `K-Phase.md` ist wie in der Referenz ein schriftlicher
Knowledge-Transfer statt eines Rechennotebooks.

## StandardScaler-Nachweis

Das U-Notebook zeigt vor und nach der Standardisierung Mittelwerte,
Standardabweichungen und Boxplots. Der Scaler wird ausschließlich innerhalb
jedes Trainingsfolds nach der Median-Imputation gefittet. Er kommt bei Ridge,
LinearSVR, RBF-SVR und MLP zum Einsatz. Decision Tree, Random Forest und HGB
benötigen keine Skalierung; deshalb enthält das finale HGB-Artefakt bewusst
keinen unnötigen Scaler.

## Methodischer Hinweis

Rechenintensive Downloads, Joins, Cross-Validierungen und Trainingsläufe liegen
in getesteten Python-Skripten. Die Notebooks lesen deren versionierte,
maschinenlesbare Berichte, validieren Gates, visualisieren Resultate und
interpretieren sie. So können Präsentation, Notebook und produktive Pipeline
nicht unbemerkt unterschiedliche Splits oder Parameter verwenden.
