# QUA³CK- und MLOps-Nachweismatrix

Stand: 17. Juli 2026

Diese Matrix ordnet die Anforderungen aus „Der QUA³CK-Prozess mit MLOps,
MLflow und Streamlit“ konkreten, prüfbaren MietCheck-Artefakten zu. Sie trennt
verbindliche Projektnachweise von bewusst nicht automatisierten
Produktionsfunktionen.

| Anforderung | Umsetzung | Nachweis | Status |
|---|---|---|---|
| Q – Problem, Zielgruppen, Anforderungen, KPIs und Constraints | Forschungsfrage, Nutzerentscheidungen, Go/No-Go-Gates und Einsatzgrenzen | `notebooks/Q-Phase.ipynb`, `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md` | erfüllt |
| U – EDA, Datenqualität, Skalierung und Leakage | ausgeführte EDA, Datenverträge, StandardScaler-Vorher/Nachher-Nachweis, fold-interne Imputation und räumlicher Leakage-Schutz | `notebooks/U-Phase.ipynb`, `DATA_CARD.md`, `scripts/build_dataset.py` | erfüllt |
| A¹ – geeignete Algorithmen vergleichen | Baseline, Ridge, LinearSVR, Decision Tree, Random Forest, HGB und MLP auf identischen räumlichen Folds; RBF-SVR als skalierungsbegründete Zusatzstudie | `notebooks/A-Phase.ipynb`, `reports/algorithm_benchmark.json`, `reports/svm_kernel_benchmark.json` | erfüllt |
| A² – Feature-Anpassung | vier inkrementelle Merkmalsgruppen und dokumentierte Ablation | `notebooks/A-Phase.ipynb`, `reports/feature_ablation.json` | erfüllt |
| A³ – Hyperparameter-Tuning | acht theoriegeleitete Kandidaten; Kalibrierung und Test bleiben gesperrt | `notebooks/A-Phase.ipynb`, `reports/hgb_tuning.json` | erfüllt |
| C – quantitative und qualitative Auswahl | räumlicher Holdout, vier Punktmetriken, Baseline-Gate, Intervalle, Subgruppen und Modellkarte | `notebooks/C-Phase.ipynb`, `reports/final_model_evaluation.json` | erfüllt |
| K – Dokumentation und Deployment | Streamlit-App, README, Daten-/Modellkarte, Risikoanalyse und Screenshot-Präsentation | `notebooks/K-Phase.md`, `app.py`, `docs/` | erfüllt; öffentliche Freigabe folgt nach Abnahme |
| Experiment-Tracking mit MLflow | bestehende unveränderliche JSON-Ergebnisse werden als A¹-, A³- und C/K-Runs mit Parametern, Metriken und Artefakten publiziert | `scripts/publish_mlflow.py`, `src/mlflow_tracking.py`, `reports/mlflow_publish.json` | erfüllt |
| Model Registry und Modell-Signatur | finales scikit-learn-Modell mit Inputbeispiel und inferierter Signatur; Alias `@champion` | `scripts/publish_mlflow.py`, `models/model_manifest.json` | erfüllt |
| Codeversionierung | GitHub, CI und klarer Repository-Aufbau | `.git/`, `.github/workflows/ci.yml`, `README.md` | erfüllt |
| Datenprovenienz | offizielle URLs, Abrufzeit, Größe, Signatur und SHA-256; große Rohdaten bewusst nicht in Git | `scripts/download_data.py`, `data/raw/source_manifest.json`, `DATA_CARD.md` | erfüllt ohne DVC |
| Modellversionierung und Lineage | semantische Version, SHA-256 für Modell, Metadaten und Evaluation | `models/model_manifest.json`, `scripts/verify_release.py` | erfüllt |
| Automatisierte ML-Tests | Code-, Daten-, Split-, Leakage-, Modell-, Segment-, Notebook-, Serving- und App-Tests | `tests/`, `scripts/verify_release.py` | erfüllt |
| CI | Lint, Format, Pytest, Release-Gates und Container-Build | `.github/workflows/ci.yml` | erfüllt |
| Docker | reproduzierbarer Streamlit-Container und lokaler MLflow-Dienst | `Dockerfile`, `docker-compose.yml` | erfüllt |
| Governance | Datenkarte, Modellkarte, Risikoanalyse, Freigabegate, Hashmanifest und Champion-Alias | `docs/`, `models/model_manifest.json` | erfüllt |
| Drift/Fairness | räumlicher Distribution Shift, amtliche Unsicherheit und Wohnungskategorien werden als Zuverlässigkeitssegmente geprüft | `final_model_evaluation.json`, `RISK_AND_ETHICS.md`, `verify_release.py` | erfüllt für bekannte Segmente |
| Live-Monitoring, CT und automatischer Rollback | wegen fehlender gelabelter Produktionsdaten und Prüfungs-Prototyp bewusst nicht automatisiert; Update- und Freigabeprozess dokumentiert | `DATA_CARD.md`, `MODEL_CARD.md`, `RISK_AND_ETHICS.md` | begründet nicht im Prototyp-Scope |

## Fachliche Abweichungen von den Kursbeispielen

### Big 3

Decision Tree, KNN und K-Means sind Beispiele aus dem Kurs, aber keine
problemagnostische Pflichtkombination. MietCheck ist eine überwachte Regression
auf mehr als zwei Millionen räumlich abhängigen Zeilen. Random Forest und HGB
decken die Baumfamilie ab. K-Means löst nicht die Regressionsaufgabe; KNN ist bei
dieser Datenmenge als produktive Inferenz ungeeignet. Ridge, zwei Baum-Ensembles
und MLP bilden deshalb den fachlich passenderen Vergleich.

### Serving-Architektur

Das Modell wird nicht bei jeder Streamlit-Interaktion neu geladen. Ein versionierter
Batch-Schritt erzeugt aus Modell, Metadaten und Zensus-Kontext die 37 regionalen
Profile. Die App kombiniert diese unveränderlichen ML-Vorhersagen in Echtzeit mit
Wohnfläche, Baujahr, persönlicher Miete und Einkommen. Das reduziert Cloud-Ressourcen,
verhindert Rohdatenzugriff im Produktivbetrieb und erhält eine überprüfbare
Train-/Serving-Lineage über Modellhash und Profilmetadaten.

### DVC und kontinuierliches Training

Die offiziellen Rohdateien sind groß und dürfen nicht beliebig gespiegelt werden.
MietCheck nutzt deshalb URL-, Zeit-, Größen- und SHA-256-Provenienz statt eines
eigenen DVC-Remotes. Automatisches Retraining wäre ohne fachlich vergleichbare neue
Zensus-Zielwerte Scheinautomatisierung. Neue Daten werden erst nach den dokumentierten
Qualitäts-, Segment- und Freigabegates übernommen.
