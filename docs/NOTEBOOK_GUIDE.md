# QUA³CK-Notebook-Leitfaden

Stand: 16. Juli 2026

| Nr. | Phase | Inhalt | Reproduzierbare Evidenz |
|---:|---|---|---|
| 00 | Gesamtüberblick | Forschungsfrage, USP, KPIs, Gates und Nachweiskette | alle versionierten Reports |
| 01 | Q – Question | Problem, Zielgruppen, Forschungsfragen, KPIs, USP und Deployment-Ziel | `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md` |
| 02 | U – Understanding | Quellen, Qualität, Zielverteilung, Kategorien, Raumstruktur, Korrelationen | `download_data.py`, `build_dataset.py`, `model_table.parquet` |
| 03 | A¹ – Auswahl | fünf Modellfamilien auf identischen Raum-Folds | `algorithm_benchmark.py` |
| 04 | A²/A³ – Adapting & Adjusting | acht HGB-Varianten, Feature-Ablation, Datensperre und Artefakt | `tune_hgb.py`, `feature_ablation.py` |
| 05 | C – Comparing | finale Testgüte, Intervalle, Subgruppen, Wichtigkeit | `train_final_model.py` |
| 06 | K – Knowledge | Umzugsaufschlag, Marktverlauf, persönliche Belastung | GREIX- und Regionsprofile |

## Ausführung

Nach Installation und Datenaufbau:

```text
python scripts/generate_notebooks.py
python scripts/execute_notebooks.py
```

`generate_notebooks.py` hält Struktur und Narrative konsistent. `execute_notebooks.py` führt alle Codezellen mit dem Projektkernel aus, bricht beim ersten Fehler ab, speichert die Outputs und schreibt `reports/notebook_execution.json`.

Der verifizierte Lauf umfasst sieben bestandene Notebooks einschließlich Gesamtüberblick. Alle Codezellen besitzen einen Execution Count; alte Kaggle-Daten, `immo_clean` und die frühere Kennzahl „202.908 Angebote“ kommen nicht mehr vor.

## Methodischer Hinweis

Rechenintensive Downloads, Joins, Cross-Validierungen und Trainingsläufe liegen bewusst in getesteten Python-Skripten. Die Notebooks lesen deren versionierte, maschinenlesbare Berichte, validieren die zentralen Gates, visualisieren Resultate und interpretieren sie. So wird verhindert, dass Präsentationsnotebooks unbemerkt andere Splits oder Parameter als die produktive Pipeline verwenden.
