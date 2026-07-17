# Anforderungs- und Abnahmecheckliste

Statuswerte: `OFFEN`, `IN ARBEIT`, `ERFÜLLT`, `BLOCKIERT`.

| Bereich | Anforderung | Nachweis | Status |
|---|---|---|---|
| Prüfungsform | 10–15 Minuten Präsentation pro Person | 12-Minuten-Sprechskript, Sprecherhinweise und 90-Sekunden-Demo-Runbook | ERFÜLLT |
| Prüfungsform | Handout mit maximal 5 DIN-A4-Seiten oder Poster nach Vorgabe | visuell geprüfter PDF-Export, exakt 5 DIN-A4-Seiten | ERFÜLLT |
| Prüfungsform | wissenschaftliche Quellen und korrekte Zitation | Quellenfolien, Handout, Datenblatt, Modellkarte und README | ERFÜLLT |
| Inhalt | Problem, Zielgruppe und KPIs klar definieren | `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md`, Überblicks-Notebook | ERFÜLLT |
| Daten | großer öffentlicher Datensatz | Zensus 2022 mit 2.058.569 Modellzeilen | ERFÜLLT |
| Daten | aktuelle Marktreferenz | GREIX bis Q1/2026, 37 lokale Märkte | ERFÜLLT |
| Daten | reproduzierbarer Download | `scripts/download_data.py`, SHA-256-Manifest | ERFÜLLT |
| Daten | Lizenz, Quelle und Datenstand | `DATA_CARD.md`, Manifeste, README und App-Quellenansicht | ERFÜLLT |
| Methodik | vollständige QUA³CK-Struktur | sieben automatisiert ausgeführte Notebooks; Laufbericht 37/37 Zellen ohne Fehler | ERFÜLLT |
| Methodik | EDA und Datenqualitätsprüfung | U-Notebook mit Quellenprüfung, Qualitätsgates und realem 2,06-Mio.-Datensatz | ERFÜLLT |
| Methodik | mehrere Modelle und Baselines | fünf Modellfamilien auf identischer 3-Fold-Spatial-CV | ERFÜLLT |
| Methodik | Feature-Anpassung und Hyperparameteroptimierung | 8-Kandidaten-Tuning, 4-stufige Ablation, ausgeführtes A³-Notebook | ERFÜLLT |
| Methodik | räumlich robuste, leckagefreie Evaluation | 276.458 Testzeilen aus 99 gesperrten 25-km-Gruppen | ERFÜLLT |
| Methodik | quantitative und qualitative Modellwahl | HGB-Champion, RF-Challenger, Modellkarte und Baseline-Vergleich | ERFÜLLT |
| Methodik | Unsicherheitsabschätzung | separate Split-Conformal-Kalibrierung; 86,8 % Test-Coverage transparent | ERFÜLLT |
| Produkt | belegbares Alleinstellungsmerkmal | Konkurrenzanalyse, finaler Hook und Drei-Realitäten-Nutzerreise | ERFÜLLT |
| Produkt | professionelle Streamlit-App | Desktop- und Mobil-Screenshots, AppTest und echter Browser-Smoke-Test ohne Fehler | ERFÜLLT |
| Produkt | verständliche Erklärbarkeit | getrennte Messkonzepte, Bandbreiten, Modellvergleich, Permutationsbeiträge und Grenzen in der App | ERFÜLLT |
| Qualität | automatisierte Tests | 34 lokale Tests, ML-Release-Gates, Ruff und GitHub Actions | ERFÜLLT |
| MLOps | Experiment-Tracking und Model Registry | drei MLflow-Runs, Modell-Signatur, Registry-Version 1 und Alias `@champion` | ERFÜLLT |
| MLOps | Modell-Lineage und reproduzierbarer Container | SHA-256-Modellmanifest, Release-Prüfung, Docker-Build und Health-Smoke-Test | ERFÜLLT |
| Qualität | Datenschutz, Bias, Grenzen und Sicherheit | `RISK_AND_ETHICS.md`, Datenblatt, Modellkarte und sichtbare App-Hinweise | ERFÜLLT |
| Veröffentlichung | öffentliches GitHub-Repository | `https://github.com/neleknaak-31/MietCheck`, öffentlicher `main`-Branch | ERFÜLLT |
| Veröffentlichung | öffentliches Streamlit-Deployment | App-URL und Produktions-Smoke-Test | OFFEN |
| Prüfung | Präsentation, Handout und Demo-Ablauf | 14 geprüfte Folien ohne Überlauf, 5 geprüfte A4-Seiten, Sprechskript und Offline-Fallback | ERFÜLLT |
