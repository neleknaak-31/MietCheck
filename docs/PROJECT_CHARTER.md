# MietCheck - Projektauftrag

## Ziel

MietCheck wird als benotungsreifes Data-Analytics- und Big-Data-Projekt umgesetzt. Das Endprodukt besteht aus einer reproduzierbaren Machine-Learning-Pipeline, einer öffentlich erreichbaren Streamlit-App, einem nachvollziehbaren GitHub-Repository, ausführbaren QUA3CK-Notebooks sowie Präsentation und Handout.

Die Zielnote 1,0 ist ein Qualitätsanspruch, keine garantierbare Bewertung. Jede fachliche Aussage muss durch Code, Daten, Quellen oder überprüfbare Artefakte belegt werden.

## Produkt-Hook

**MietCheck zeigt nicht nur eine vermeintlich "faire Miete", sondern erklärt die zwei deutschen Mietmärkte:**

1. amtliche Bestandsmiete im direkten Wohnumfeld,
2. aktuelle Angebotsmiete für einen heutigen Umzug,
3. persönliche Miete beziehungsweise persönliches Budget.

Die App quantifiziert daraus den **Umzugsaufschlag**, die **persönliche Mietbelastung**, die **lokale Marktanspannung** und die **Unsicherheit der Schätzung**. Jede Zahl erhält einen sichtbaren Datenstand und eine Quellenangabe.

Dieser Produkt-Hook ist vorläufig. Er wird erst nach abgeschlossenem Konkurrenzvergleich und einem prüfbaren USP-Gate als endgültig markiert.

## Wissenschaftliche Leitfrage

> Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren erklären sie und wie zuverlässig lässt sie sich für eine konkrete Wohnsituation schätzen?

## Nutzergruppen

- Mieterinnen und Mieter, die ihre aktuelle Miete einordnen möchten
- Wohnungssuchende, die die realen Kosten eines Umzugs verstehen möchten
- Studierende und Berufseinsteiger mit begrenztem Wohnbudget
- Interessierte, die regionale Mietunterschiede transparent untersuchen möchten

## Nicht verhandelbare Qualitätskriterien

- große, öffentlich zugängliche und rechtlich nutzbare Datenbasis
- automatisierbarer Download und reproduzierbare Aufbereitung
- Trennung von Rohdaten, verarbeiteten Daten und Ergebnissen
- QUA3CK vollständig und nachvollziehbar dokumentiert
- mehrere geeignete Baselines und ML-Modelle
- räumlich robuste Validierung statt nur zufälligem Train-Test-Split
- Hyperparameteroptimierung ausschließlich innerhalb der Trainingsdaten
- Unsicherheit und Grenzen sichtbar kommuniziert
- keine Bezeichnung als amtlicher Mietspiegel oder Rechtsberatung
- Quellen, Lizenz und Datenstand direkt in App und Dokumentation
- öffentliches GitHub-Repository und öffentliches Streamlit-Deployment
- automatisierte Tests und reproduzierbarer End-to-End-Lauf
- Präsentation, Handout und belastbarer Demo-Ablauf

## Geplante Kernartefakte

- `src/`: Download, Validierung, Aufbereitung, Features, Training und Inferenz
- `notebooks/`: ein Notebook je QUA3CK-Phase plus Gesamtüberblick
- `app.py` und `views/`: professionelle Streamlit-Anwendung
- `tests/`: Unit-, Datenvertrags- und Smoke-Tests
- `docs/`: Methodik, Datenblatt, Modellkarte, Quellen und Prüfungsunterlagen
- `reports/`: reproduzierbare Kennzahlen und Abbildungen
- GitHub Actions für Tests und Qualitätskontrollen

## Definition of Done

Das Projekt ist erst fertig, wenn alle Anforderungen in `docs/REQUIREMENTS_CHECKLIST.md` durch konkrete Evidenz erfüllt sind, die App öffentlich erreichbar ist, ein frischer Klon reproduzierbar ausgeführt werden kann und Präsentation sowie Handout visuell geprüft wurden.

