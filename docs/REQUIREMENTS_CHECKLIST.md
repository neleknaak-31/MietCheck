# Anforderungs- und Abnahmecheckliste

Statuswerte: `OFFEN`, `IN ARBEIT`, `ERFÜLLT`, `BLOCKIERT`.

| Bereich | Anforderung | Nachweis | Status |
|---|---|---|---|
| Prüfungsform | 10–15 Minuten Präsentation pro Person | 12-Minuten-Sprechskript, Sprecherhinweise und Screenshot-Runbook ohne Live-Demo | ERFÜLLT |
| Prüfungsform | Handout mit maximal 5 DIN-A4-Seiten oder Poster nach Vorgabe | visuell geprüfter PDF-Export, exakt 5 DIN-A4-Seiten | ERFÜLLT |
| Prüfungsform | wissenschaftliche Quellen und korrekte Zitation | Quellenfolien, Handout, Datenblatt, Modellkarte und README | ERFÜLLT |
| Inhalt | Problem, Zielgruppe und KPIs klar definieren | `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md`, `Q-Phase.ipynb` | ERFÜLLT |
| Daten | großer öffentlicher Datensatz | Zensus 2022 mit 2.058.569 Modellzeilen | ERFÜLLT |
| Daten | aktuelle Marktreferenz | GREIX bis Q1/2026, 37 lokale Märkte | ERFÜLLT |
| Daten | reproduzierbarer Download | `scripts/download_data.py`, SHA-256-Manifest | ERFÜLLT |
| Daten | Lizenz, Quelle und Datenstand | `DATA_CARD.md`, Manifeste, README und App-Quellenansicht | ERFÜLLT |
| Methodik | vollständige QUA³CK-Struktur | vier Referenz-konform benannte Phasen-Notebooks plus `K-Phase.md`; Q als reine Konzeptphase, U/A/C mit 11/11 fehlerfrei ausgeführten Analysezellen | ERFÜLLT |
| Methodik | EDA und Datenqualitätsprüfung | U-Notebook mit Quellenprüfung, Qualitätsgates und realem 2,06-Mio.-Datensatz | ERFÜLLT |
| Methodik | mehrere Modelle und Baselines | sieben Hauptkandidaten auf identischer 3-Fold-Spatial-CV; ergänzend Linear- vs. RBF-SVR auf transparenter 10k-Machbarkeitsstichprobe | ERFÜLLT |
| Methodik | Feature-Anpassung und Hyperparameteroptimierung | 8-Kandidaten-Tuning, 4-stufige Ablation, ausgeführtes A³-Notebook | ERFÜLLT |
| Methodik | räumlich robuste, leckagefreie Evaluation | 276.458 Testzeilen aus 99 gesperrten 25-km-Gruppen | ERFÜLLT |
| Methodik | quantitative und qualitative Modellwahl | HGB-Champion, RF-Challenger, Modellkarte und Baseline-Vergleich | ERFÜLLT |
| Methodik | Unsicherheitsabschätzung | separate Split-Conformal-Kalibrierung; 86,8 % Test-Coverage transparent | ERFÜLLT |
| Produkt | belegbares Alleinstellungsmerkmal | Konkurrenzanalyse, finaler Hook und Drei-Realitäten-Nutzerreise | ERFÜLLT |
| Produkt | professionelle Streamlit-App | Desktop- und Mobil-Screenshots, AppTest und echter Browser-Smoke-Test ohne Fehler | ERFÜLLT |
| Produkt | verständliche Erklärbarkeit | getrennte Messkonzepte, Bandbreiten, Modellvergleich, Permutationsbeiträge und Grenzen in der App | ERFÜLLT |
| Qualität | automatisierte Tests | 36 lokale Tests, ML-Release-Gates, Ruff und GitHub Actions | ERFÜLLT |
| MLOps | Experiment-Tracking und Model Registry | drei MLflow-Runs, Modell-Signatur, Registry-Version 1 und Alias `@champion` | ERFÜLLT |
| MLOps | Modell-Lineage und reproduzierbarer Container | SHA-256-Modellmanifest, Release-Prüfung, Docker-Build und Health-Smoke-Test | ERFÜLLT |
| Qualität | Datenschutz, Bias, Grenzen und Sicherheit | `RISK_AND_ETHICS.md`, Datenblatt, Modellkarte und sichtbare App-Hinweise | ERFÜLLT |
| Veröffentlichung | öffentliches GitHub-Repository | `https://github.com/neleknaak-31/MietCheck`, öffentlicher `main`-Branch | ERFÜLLT |
| Veröffentlichung | öffentliches Streamlit-Deployment | App ist technisch deployt und für die Abnahme bewusst privat; öffentliche Freigabe, anonymer Produktions-Smoke-Test und Dokumentationsupdate folgen erst nach ausdrücklicher Endfreigabe | OFFEN |
| Prüfung | Präsentation, Handout und Screenshot-Ablauf | 16 geprüfte Folien ohne Überlauf, 5 geprüfte A4-Seiten, Sprechskript und Screenshot-Fallback | ERFÜLLT |

## Abgleich mit den mündlichen Hinweisen vom 16.07.2026

Quelle: „Big Data and Data Analytics – Summary“, vierseitige Zusammenfassung der
letzten Vorlesung. Die dort genannten nächsten Schritte sind bewusst einzeln
nachgewiesen:

| Hinweis des Professors | Umsetzung in MietCheck | Status |
|---|---|---|
| klassische ML-Verfahren: lineare und Kernel-SVM, Entscheidungsbaum und Ensemble | LinearSVR im Hauptvergleich, RBF-SVR als skalierungsbegründete Zusatzstudie, Decision Tree, Random Forest und HGB; MLP nur als zusätzlicher Challenger | ERFÜLLT |
| Hyperparameter automatisiert optimieren | acht reproduzierbar ausgewertete HGB-Konfigurationen auf räumlichen Entwicklungsfolds; Testset bleibt bis zur finalen Evaluation gesperrt | ERFÜLLT |
| interaktive Streamlit-App und funktionierender Link | Szenario-, Wohnungs- und Budgeteingaben, Markt-/Methodikansichten sowie deployte URL; Freigabe bleibt bis zum finalen Release-Gate absichtlich privat | TECHNISCH ERFÜLLT / FREIGABE OFFEN |
| strukturiertes GitHub-Repository mit README, Code und Phasen-Notebooks | öffentliche Repository-Struktur; exakt referenzkonforme Dateien `Q-Phase`, `U-Phase`, `A-Phase`, `C-Phase` und `K-Phase` | ERFÜLLT |
| Präsentation mit App-Screenshots statt riskanter Live-Demo | 16 Folien im App-Design, drei geprüfte Produktionsscreenshots, 12-Minuten-Sprechskript und Screenshot-Runbook | ERFÜLLT |
| fünfseitige schriftliche Ausarbeitung als erweitertes Handout | editierbares DOCX und visuell geprüfter PDF-Export mit exakt fünf DIN-A4-Seiten | ERFÜLLT |

Word ist laut Zusammenfassung neben Markdown und LaTeX ausdrücklich zulässig. Das
Handout ist daher das maßgebliche schriftliche Abgabedokument; eine zusätzliche
Langfassung ist nicht erforderlich.
