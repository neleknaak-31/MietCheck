# Anforderungs- und Abnahmecheckliste

Statuswerte: `OFFEN`, `IN ARBEIT`, `ERFUELLT`, `BLOCKIERT`.

| Bereich | Anforderung | Nachweis | Status |
|---|---|---|---|
| Prüfungsform | 10-15 Minuten Präsentation pro Person | finaler Demo- und Sprechzeitentest | OFFEN |
| Prüfungsform | Handout mit maximal 5 DIN-A4-Seiten oder Poster nach Vorgabe | gerendertes und geprüftes PDF | OFFEN |
| Prüfungsform | wissenschaftliche Quellen und korrekte Zitation | Literaturverzeichnis und Quellenprüfung | IN ARBEIT |
| Inhalt | Problem, Zielgruppe und KPIs klar definieren | Projektauftrag und Q-Notebook | IN ARBEIT |
| Daten | großer öffentlicher Datensatz | Zensus 2022 mit 2.058.569 Beobachtungen | ERFUELLT |
| Daten | aktuelle Marktreferenz | GREIX bis Q1/2026 | ERFUELLT |
| Daten | reproduzierbarer Download | `scripts/download_data.py`, lokales SHA-256-Manifest | ERFUELLT |
| Daten | Lizenz und Quellenangabe | Zensus-, GREIX- und OSM-Attribution in Manifesten und Forschungsdokumentation; Datenblatt und App-Ansicht folgen | IN ARBEIT |
| Methodik | vollständige QUA3CK-Struktur | sieben ausführbare Notebooks | IN ARBEIT |
| Methodik | EDA und Datenqualitätsprüfung | validierter Big-Data-Build vorhanden; U-Notebook noch offen | IN ARBEIT |
| Methodik | mehrere Modelle und Baselines | fünf Modellfamilien auf identischer 3-Fold-Spatial-CV verglichen | ERFUELLT |
| Methodik | Feature-Anpassung und Hyperparameteroptimierung | räumliches 8-Kandidaten-Tuning und 4-stufige Ablation abgeschlossen; A3-Notebook folgt | IN ARBEIT |
| Methodik | räumlich robuste, leckagefreie Evaluation | finale Auswertung auf 276.458 Zeilen aus 99 gesperrten Testblöcken | ERFUELLT |
| Methodik | quantitative und qualitative Modellwahl | HGB-Champion, RF-Challenger, Modellkarte und finale Baseline-Messung | ERFUELLT |
| Methodik | Unsicherheitsabschätzung | separate Split-Conformal-Kalibrierung; 86,8 % Test-Coverage transparent dokumentiert | ERFUELLT |
| Produkt | belegbares Alleinstellungsmerkmal | Konkurrenzmatrix und USP-Test | IN ARBEIT |
| Produkt | professionelle Streamlit-App | visuelle, funktionale und mobile Prüfung | OFFEN |
| Produkt | verständliche Erklärbarkeit | lokale Erklärungen und Datenstand je Ergebnis | OFFEN |
| Qualität | automatisierte Tests | 11 lokale Tests bestehen; CI-Workflow vorhanden, GitHub-Lauf noch offen | IN ARBEIT |
| Qualität | Datenschutz, Bias, Grenzen und Sicherheit | Modellkarte vorhanden; App- und Gesamtrisikoanalyse folgen | IN ARBEIT |
| Veröffentlichung | öffentliches GitHub-Repository | Repository-URL | OFFEN |
| Veröffentlichung | öffentliches Streamlit-Deployment | App-URL und Smoke-Test | OFFEN |
| Prüfung | Präsentation, Handout und Demo-Ablauf | final gerenderte Artefakte | OFFEN |
