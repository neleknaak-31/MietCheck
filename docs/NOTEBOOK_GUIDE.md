# QUA³CK-Notebook-Leitfaden

Stand: 16. Juli 2026

| Nr. | Phase | Inhalt | Reproduzierbare Evidenz |
|---:|---|---|---|
| 00 | Gesamtüberblick | Forschungsfrage, USP, KPIs, Gates und Nachweiskette | alle versionierten Reports |
| 01 | Q – Quality | Quellen, Hashes, Grain, Missingness, amtliche Unsicherheit | `download_data.py`, `build_dataset.py` |
| 02 | U – Understanding | Zielverteilung, Kategorien, Raumstruktur, Korrelationen | `model_table.parquet` |
| 03 | A¹ – Auswahl | fünf Modellfamilien auf identischen Raum-Folds | `algorithm_benchmark.py` |
| 04 | A²/A³ – Anpassung & Anwendung | acht HGB-Varianten, Feature-Ablation, Artefakt | `tune_hgb.py`, `feature_ablation.py` |
| 05 | C – Comparing | finale Testgüte, Intervalle, Subgruppen, Wichtigkeit | `train_final_model.py` |
| 06 | K – Knowledge | Umzugsaufschlag, Marktverlauf, persönliche Belastung | GREIX- und Regionsprofile |

## Ausführung

Nach Installation und Datenaufbau:

```text
python scripts/generate_notebooks.py
python scripts/execute_notebooks.py
```

`generate_notebooks.py` hält Struktur und Narrative konsistent. `execute_notebooks.py` führt alle Codezellen mit dem Projektkernel aus, bricht beim ersten Fehler ab, speichert die Outputs und schreibt `reports/notebook_execution.json`.

Der verifizierte Lauf vom 16. Juli 2026 umfasst sieben bestandene Notebooks. Alle Codezellen besitzen einen Execution Count; alte Kaggle-Daten, `immo_clean` und die frühere Kennzahl „202.908 Angebote“ kommen nicht mehr vor.

## Methodischer Hinweis

Rechenintensive Downloads, Joins, Cross-Validierungen und Trainingsläufe liegen bewusst in getesteten Python-Skripten. Die Notebooks lesen deren versionierte, maschinenlesbare Berichte, validieren die zentralen Gates, visualisieren Resultate und interpretieren sie. So wird verhindert, dass Präsentationsnotebooks unbemerkt andere Splits oder Parameter als die produktive Pipeline verwenden.
