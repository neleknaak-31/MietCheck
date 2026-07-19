# MietCheck – Projektauftrag

## Ziel

MietCheck ist ein benotungsreifes Data-Analytics- und Big-Data-Projekt. Das
Endprodukt besteht aus einer reproduzierbaren Machine-Learning-Pipeline, einer
öffentlich erreichbaren Streamlit-App, einem nachvollziehbaren GitHub-Repository,
vollständig ausgeführten QUA³CK-Notebooks sowie Präsentation und Handout.

Bis zur gemeinsamen Endabnahme bleibt die bereits deployte Streamlit-App auf
„Only specific people can view this app“. Das Repository bleibt öffentlich. Die
öffentliche App-Freigabe ist ein bewusstes finales Release-Gate und kein
Zwischenstand während der Qualitätsprüfung.

Die Zielnote 1,0 ist ein Qualitätsanspruch, keine garantierbare Bewertung. Jede
fachliche Aussage muss durch Code, Daten, Quellen oder ein überprüfbares Artefakt
belegt sein.

## Finaler Produkt-Hook

**MietCheck zeigt drei Mietrealitäten, die herkömmliche Mietrechner häufig
vermischen:**

1. den kleinräumigen ML-Bestandsanker aus dem Zensus 2022,
2. die aktuelle GREIX-Angebotsmiete bei einem heutigen Umzug,
3. die persönliche Vertragsmiete und Mietbelastung.

Die App quantifiziert daraus den **Umzugsaufschlag** in Euro und Prozent. Jede
Ergebniszahl erhält Einheit, Zeitbezug, Streuung oder Unsicherheit und eine
fachliche Einordnung. Der Hook hat den Konkurrenz- und Machbarkeitstest bestanden:
Er beruht auf zwei unterschiedlich messenden öffentlichen Datenquellen und einem
räumlich evaluierten ML-Modell; er ist keine umbenannte Portalpreisschätzung.

## Wissenschaftliche Leitfrage

> Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller
> Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren
> erklären sie und wie zuverlässig lässt sie sich für eine konkrete
> Wohnsituation schätzen?

## Nutzergruppen

- Mieterinnen und Mieter, die ihre aktuelle Wohnsituation einordnen möchten
- Wohnungssuchende, die einen möglichen Umzug finanziell bewerten möchten
- Studierende und Berufseinsteiger mit begrenztem Wohnbudget
- dateninteressierte Personen, die regionale Mietunterschiede nachvollziehen möchten

## Nicht verhandelbare Qualitätskriterien

- große, öffentlich zugängliche und nachvollziehbar lizenzierte Datenbasis
- automatisierbarer Download mit Hash-Provenienz
- Trennung von Rohdaten, abgeleiteten Datenprodukten und Ergebnissen
- QUA³CK vollständig und ausführbar dokumentiert
- mehrere geeignete Baselines und ML-Modelle
- räumlich robuste Validierung statt zufälligem Zeilensplit
- Hyperparameteroptimierung ausschließlich innerhalb der Entwicklungsdaten
- separat kalibrierte und ehrlich gemessene Unsicherheit
- keine Bezeichnung als amtlicher Mietspiegel oder Rechtsberatung
- Quellen, Lizenz und Datenstand in App und Dokumentation
- öffentliches GitHub-Repository und öffentliches Streamlit-Deployment
- automatisierte Tests und reproduzierbarer End-to-End-Lauf
- Präsentation, Handout und belastbarer Demo-Ablauf

## Kernartefakte

- `scripts/`: Download, Datenbau, Experimente, Training und Notebook-Ausführung
- `src/app_logic.py`: reine und getestete Szenarioberechnungen
- `notebooks/`: sieben QUA³CK-Notebooks einschließlich Gesamtüberblick
- `app.py`: professionelle responsive Streamlit-Anwendung
- `tests/`: Unit-, Datenvertrags-, Notebook- und App-Smoke-Tests
- `docs/`: Spezifikation, Datenblatt, Modellkarte, Quellen und Prüfungsunterlagen
- `reports/`: maschinenlesbare Experimentergebnisse und geprüfte Screenshots
- `.github/workflows/ci.yml`: automatisierte Qualitätsgates

## Definition of Done

Das Projekt ist erst fertig, wenn jede Zeile in
`docs/REQUIREMENTS_CHECKLIST.md` durch konkrete Evidenz erfüllt ist, die App
öffentlich erreichbar ist, ein frischer Klon reproduzierbar geprüft wurde und
Präsentation sowie Handout visuell und inhaltlich abgenommen wurden.

Der Übergang von privater Abnahme zu öffentlicher App ist erst zulässig, wenn die
fachliche, visuelle und technische Endabnahme dokumentiert ist und die
Projekteigentümerin die Veröffentlichung ausdrücklich freigibt.
