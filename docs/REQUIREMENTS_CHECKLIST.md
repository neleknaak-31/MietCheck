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
| Daten | Lizenz und Quellenangabe | Datenblatt und App-Quellenansicht | IN ARBEIT |
| Methodik | vollständige QUA3CK-Struktur | sieben ausführbare Notebooks | IN ARBEIT |
| Methodik | EDA und Datenqualitätsprüfung | validierter Big-Data-Build vorhanden; U-Notebook noch offen | IN ARBEIT |
| Methodik | mehrere Modelle und Baselines | fünf Modellfamilien auf identischer 3-Fold-Spatial-CV verglichen | ERFUELLT |
| Methodik | Feature-Anpassung und Hyperparameteroptimierung | A3-Notebook und Experimentprotokoll | OFFEN |
| Methodik | räumlich robuste, leckagefreie Evaluation | leakage-bereinigter Holdout und 3-Fold-Spatial-CV vorhanden; finale Evaluation noch offen | IN ARBEIT |
| Methodik | quantitative und qualitative Modellwahl | Benchmark begründet HGB als Champion und Random Forest als Challenger; C-Notebook und Modellkarte folgen | IN ARBEIT |
| Methodik | Unsicherheitsabschätzung | kalibrierte Intervalle und Coverage-Test | OFFEN |
| Produkt | belegbares Alleinstellungsmerkmal | Konkurrenzmatrix und USP-Test | IN ARBEIT |
| Produkt | professionelle Streamlit-App | visuelle, funktionale und mobile Prüfung | OFFEN |
| Produkt | verständliche Erklärbarkeit | lokale Erklärungen und Datenstand je Ergebnis | OFFEN |
| Qualität | automatisierte Tests | 11 lokale Tests bestehen; CI-Workflow vorhanden, GitHub-Lauf noch offen | IN ARBEIT |
| Qualität | Datenschutz, Bias, Grenzen und Sicherheit | Modellkarte und Risikoanalyse | OFFEN |
| Veröffentlichung | öffentliches GitHub-Repository | Repository-URL | OFFEN |
| Veröffentlichung | öffentliches Streamlit-Deployment | App-URL und Smoke-Test | OFFEN |
| Prüfung | Präsentation, Handout und Demo-Ablauf | final gerenderte Artefakte | OFFEN |
