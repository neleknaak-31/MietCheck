# MietCheck - verbindliche Produktspezifikation

Version: 0.1

Stand: 16. Juli 2026

## Produktversprechen

MietCheck beantwortet nicht nur die Frage "Ist meine Miete hoch?", sondern trennt drei unterschiedliche Perspektiven:

1. **Bestandsrealität:** Was zahlen bestehende Mietverhältnisse in einem vergleichbaren lokalen Wohnumfeld?
2. **Umzugsrealität:** Welche Angebotsmiete wird bei einem heutigen Umzug typischerweise verlangt?
3. **Persönliche Realität:** Wie unterscheiden sich die eigene Miete und das eigene Budget davon?

Der zentrale Ergebniswert ist der **Umzugsaufschlag** in Euro und Prozent. Er wird durch Datenstand, räumliche Abdeckung, Unsicherheit und Quellen ergänzt.

## Wissenschaftliche Leitfrage

Wie groß ist die Lücke zwischen kleinräumiger Bestandsmiete und aktueller Angebotsmiete in Deutschland, welche räumlichen und wohnungsbezogenen Faktoren erklären sie und wie zuverlässig lässt sie sich für eine konkrete Wohnsituation schätzen?

## Teilfragen

1. Wie stark variiert die Bestandsmiete innerhalb und zwischen deutschen Regionen?
2. Verbessern strukturelle Wohnumfeldmerkmale eine rein räumliche Baseline?
3. Wie stark verschlechtert sich die Modellgüte bei räumlich getrennten Testgebieten gegenüber einer zufälligen Aufteilung?
4. Wie groß ist die Differenz zwischen Zensus-Bestandsmiete 2022 und GREIX-Angebotsmiete 2026?
5. Wie verändert diese Differenz die persönliche Mietbelastung bei einem Umzug?

## Zielgruppen

- Mieterinnen und Mieter, die ihre aktuelle Wohnsituation einordnen möchten
- Wohnungssuchende, die einen möglichen Umzug finanziell bewerten möchten
- Studierende und Berufseinsteiger mit begrenztem Budget
- dateninteressierte Personen, die regionale Mietunterschiede nachvollziehen möchten

## Abdeckungsstufen

### Stufe A - aktuelle lokale Marktreferenz

Für die von GREIX veröffentlichten Städte und Regionen werden lokale Angebotsmieten bis zum jeweils jüngsten Datenstand genutzt. Die App zeigt Mittelwert, Median sowie 25.- und 75.-Perzentil.

### Stufe B - deutschlandweite Bestandsreferenz

Für Deutschland wird eine kleinräumige Bestandsmietenschätzung aus offenen Zensusdaten angeboten. Sie ist keine aktuelle Angebotsmiete und kein amtlicher Mietspiegel.

### Stufe C - nationale Zeitkorrektur

Außerhalb der lokalen GREIX-Abdeckung darf eine bundesweite Indexkorrektur angezeigt werden. Sie wird ausdrücklich als grobe Orientierung mit geringerer regionaler Aussagekraft gekennzeichnet und nicht als lokale Marktprognose bezeichnet.

## Kernfunktionen der Streamlit-App

### 1. MietCheck

- Standort und Wohnungskategorie auswählen
- eigene Kaltmiete und optional Haushaltsnettoeinkommen eingeben
- Bestandsmiete mit kalibriertem Unsicherheitsintervall anzeigen
- aktuelle Angebotsmiete gemäß Abdeckungsstufe anzeigen
- Umzugsaufschlag in Euro, Euro pro Quadratmeter und Prozent berechnen
- persönliche Mietbelastung und erforderliches Einkommen darstellen
- Datenstand, Abdeckung und Quellen direkt am Ergebnis anzeigen

### 2. Marktvergleich

- regionale Bestandsmieten vergleichen
- GREIX-Zeitreihe ab 2012 darstellen
- Bestands-/Angebotslücke für verfügbare Regionen zeigen
- Filter nach Gebäudealter und Wohnungsgröße

### 3. Leistbarkeit

- heutige und potenzielle Mietbelastung vergleichen
- Szenarien für Einkommen, Wohnfläche und Region berechnen
- Faustregeln klar als Faustregeln und nicht als Rechts- oder Finanzberatung kennzeichnen

### 4. Modell und Daten

- Modellvergleich und räumliche Validierung
- erklärbare Featurebeiträge
- Unsicherheit und Datenqualitätskennzeichen
- Datenblatt, Modellkarte, Lizenzen und bekannte Grenzen

## ML-Aufgabe

Zielgröße ist die durchschnittliche Nettokaltmiete pro Quadratmeter einer Kombination aus 100-m-Gitterzelle, Gebäudealterklasse und Wohnungsgrößenklasse im Zensus 2022.

Geplante Modellgruppen:

- robuste Median-Baselines
- lineares beziehungsweise regularisiertes Regressionsmodell
- baumbasiertes Ensemble
- Histogram Gradient Boosting
- neuronale Regression als dokumentierter Zusatzvergleich, sofern Laufzeit und Güte dies rechtfertigen

Der Modellvergleich erfolgt nicht nur zufällig, sondern primär über räumlich getrennte Gruppen. Hyperparameter werden ausschließlich innerhalb der Trainingsdaten ausgewählt.

## Features

- räumliche Koordinaten in ETRS89-LAEA
- Gebäude vor/nach 1990
- Wohnung bis/über 65 m²
- Bevölkerung der Gitterzelle
- durchschnittliche Haushaltsgröße
- Eigentümerquote
- Leerstandsquote
- durchschnittliche Wohnfläche
- Anzahl der Wohnungen
- amtliche Unsicherheitskennzeichen

Sensible Merkmale wie Religion oder Staatsangehörigkeit werden nicht verwendet.

## Erfolgskriterien

### Daten

- mindestens 2 Millionen reproduzierbar verarbeitete Modellzeilen
- mindestens 98 % Join-Abdeckung der verwendeten Kontextmerkmale oder begründete Ausnahme
- Rohdaten unverändert und per SHA-256 dokumentiert
- jeder veröffentlichte Wert besitzt Quelle und Datenstand

### Modell

- mindestens 15 % niedrigerer MAE als die definierte Median-Baseline im räumlichen Holdout; falls nicht erreicht, wird das Produktkonzept fachlich neu bewertet
- MAE, RMSE, R² und Median Absolute Error für zufällige und räumliche Splits
- getrennte Güteauswertung für amtlich unsichere Zielwerte
- Unsicherheitsintervall mit dokumentierter empirischer Coverage
- keine Testdatenverwendung bei Modellauswahl oder Featureentscheidung

### Produkt

- zentrale Nutzerreise ohne Fehlermeldung im automatisierten Smoke-Test
- Ergebnisberechnung nach geladenen Artefakten in unter zwei Sekunden
- verständliche Darstellung auf Desktop und Smartphone
- keine Zahl ohne Einheit, Datenstand und fachliche Bedeutung
- sichtbarer Hinweis: kein amtlicher Mietspiegel, keine Rechts- oder Finanzberatung

### Reproduzierbarkeit

- frischer Klon kann Daten laden, Modelltable bauen, Notebooks ausführen, Modell trainieren und App starten
- automatisierte Tests und GitHub Actions sind erfolgreich
- alle Notebooks laufen ohne manuelle Zellreihenfolge durch

## Bewusst nicht im Scope

- Rechtsprüfung nach Mietpreisbremse oder lokalen Mietspiegeln
- Mietvertrags-OCR oder generative Vertragsanalyse
- Scraping kommerzieller Immobilienportale
- Behauptung einer lokalen aktuellen Angebotsmiete außerhalb belegter Datenabdeckung
- Produktivempfehlungen für Vermieter oder rechtsverbindliche Miethöhen

Diese Abgrenzung schützt wissenschaftliche Klarheit, Datenlizenz, Wartbarkeit und den realistischen Prüfungsumfang.

## Benötigte Endartefakte

- öffentliches GitHub-Repository
- öffentliches Streamlit-Deployment
- reproduzierbare Daten- und Trainingspipeline
- sieben QUA3CK-Notebooks plus Gesamtüberblick
- Datenblatt und Modellkarte
- Test- und Evaluationsbericht
- Präsentation für 10-15 Minuten
- Handout mit maximal fünf DIN-A4-Seiten
- Demo-Drehbuch und Vorbereitung auf Rückfragen
