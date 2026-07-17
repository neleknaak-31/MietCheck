# Data Card – MietCheck

## Zweck

MietCheck verbindet amtliche Bestandsmieten aus dem Zensus 2022 mit aktuellen
GREIX-Angebotsmieten. Der ML-Datensatz dient ausschließlich dazu, einen
kleinräumigen Bestandsanker in Euro je Quadratmeter zu modellieren. GREIX ist eine
separate Referenz für den heutigen Angebotsmarkt und fließt nicht als Zielvariable
in das Bestandsmodell ein.

## Quellen und Lizenzen

### Zensus 2022

- Herausgeber: Statistische Ämter des Bundes und der Länder
- Landingpage: <https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Zensus2022/_publikationen.html>
- räumliche Ebene: INSPIRE-konforme 100-m-Gitterzellen
- Stichtag: 15.05.2022
- Veröffentlichung der verwendeten offenen Gitterprodukte: 2025
- Lizenz: Datenlizenz Deutschland – Namensnennung – Version 2.0
- Zitierhinweis: „Statistische Ämter des Bundes und der Länder, Zensus 2022;
  eigene Verarbeitung.“

Verwendete Produkte:

1. Nettokaltmiete nach Gebäudealter und Wohnungsgröße,
2. Bevölkerungszahl,
3. durchschnittliche Haushaltsgröße,
4. Eigentümerquote,
5. Leerstandsquote,
6. durchschnittliche Wohnfläche je Wohnung,
7. Nettokaltmiete und Anzahl der Wohnungen.

### GREIX

- Herausgeber: Kiel Institut für Weltwirtschaft
- Landingpage: <https://www.kielinstitut.de/de/institut/forschungszentren/makrooekonomie/makrofinanzen/mietpreisindex/>
- Datengrundlage laut Quelle: VALUE Marktdatenbank
- Verwendung: nominale Quartalswerte von 2012-Q1 bis 2026-Q1
- Umfang: 2.166 Beobachtungen, 37 lokale Märkte plus Deutschlandreferenz
- Zitierhinweis: „Kiel Institut für Weltwirtschaft auf Basis der VALUE
  Marktdatenbank; eigene Verarbeitung.“

Die GREIX-Datei ist öffentlich abrufbar. Für Weiterverwendung und Veröffentlichung
sind die jeweils aktuellen Quellen- und Nutzungsbedingungen des Kiel Instituts zu
beachten.

### Regionszentren

- Geocoding: Nominatim / OpenStreetMap
- Lizenz: Open Database License (ODbL)
- Verwendung: ausschließlich zur einmaligen Bestimmung der Zentren der
  37 GREIX-Regionen

## Download und Provenienz

`scripts/download_data.py` lädt alle Quelldateien über feste offizielle URLs. Für
jede Datei werden Abrufzeitpunkt, Bytezahl und SHA-256-Hash in
`data/raw/source_manifest.json` protokolliert. Mindestgröße und Dateisignatur
schützen vor HTML-Fehlerseiten oder unvollständigen Downloads.

Rohdaten sind wegen Größe und Drittanbieterbedingungen nicht Teil des Git-
Repositories. Die für die App nötigen abgeleiteten, kompakten Tabellen liegen unter
`data/app/`.

## ML-Tabelle

`scripts/build_dataset.py` erzeugt die Modellmatrix aus den Zensusprodukten.

| Eigenschaft | Wert |
|---|---:|
| Zeilen | 2.058.569 |
| eindeutige 100-m-Gitterzellen | 1.184.386 |
| räumliche 25-km-Gruppen | 663 |
| Zielvariable | durchschnittliche Nettokaltmiete in €/m² |
| Ziel-Median | 6,60 €/m² |
| Ziel-Mittelwert | 7,06 €/m² |
| Zielbereich | 1,00 bis 49,59 €/m² |

Eine Gitterzelle kann mehrfach vorkommen, weil der Zielwert nach zwei binären
Wohnungskategorien differenziert wird:

- Gebäude bis einschließlich 1990 / nach 1990,
- Wohnfläche bis einschließlich 65 m² / über 65 m².

Weitere Merkmale sind LAEA-Koordinaten, Bevölkerung, Haushaltsgröße,
Eigentümerquote, Leerstand, durchschnittliche Wohnfläche, Wohnungszahl sowie
Indikatoren für statistisch unsichere oder imputierte Angaben.

## Datenqualität

Die Nicht-Null-Anteile der numerischen Kontextmerkmale liegen zwischen 99,1 % und
99,8 %. Fehlende Werte werden ausschließlich auf Trainingsdaten mit Medianen
behandelt; Unsicherheitsindikatoren bleiben als eigene Features erhalten.

11,5 % der Zielwerte tragen in der amtlichen Quelle einen Unsicherheitshinweis.
Diese Information wird dokumentiert und für Sensitivitätsanalysen genutzt, nicht
verschwiegen.

Automatisierte Datenverträge prüfen unter anderem:

- erwartete Spalten und Datentypen,
- eindeutige Schlüssel der Quelltabellen,
- plausible Wertebereiche,
- räumliche Join-Abdeckung,
- GREIX-Perioden, Quartile und Duplikate,
- Mindestumfang und Aktualität der Quellen.

## Räumliche Trennung und Leakage-Schutz

Zufällige Zeilensplits wären bei benachbarten 100-m-Zellen zu optimistisch. Daher
werden aus den Koordinaten 25-km-Raumgruppen gebildet. Entwicklung,
Kalibrierung und finaler Test verwenden disjunkte Gruppen:

| Teilmenge | Zeilen | Raumgruppen |
|---|---:|---:|
| Entwicklung | 1.518.322 | 465 |
| Intervall-Kalibrierung | 263.789 | 99 |
| finaler Test | 276.458 | 99 |

Hyperparameterwahl und Feature-Ablation verwenden nur den Entwicklungsbereich. Der
finale Test wird erst nach Modellwahl ausgewertet.

## Deploybare Regionsprofile

Für jede der 37 GREIX-Regionen wird aus bis zu 500 bewohnten Zensuszellen innerhalb
von zehn Kilometern um das Regionszentrum ein robuster Median-Kontext gebildet.
Falls weniger Zellen im Radius liegen, werden mindestens die 100 nächsten Zellen
verwendet. Koordinatensystem: ETRS89-extended / LAEA Europe (EPSG:3035).

Die Profile sind eine regionale Entscheidungshilfe. Sie sind keine adressgenaue
Vorhersage und keine flächendeckende Abdeckung aller deutschen Gemeinden.

## Repräsentativität und bekannte Grenzen

- Bestands- und Angebotsdaten messen unterschiedliche Marktsegmente und Zeitpunkte.
- GREIX deckt vor allem größere Städte und ausgewählte Kreise ab.
- Die Zensus-Zielvariable ist ein Gitteraggregat, keine einzelne Vertragsmiete.
- Vertragsbeginn, Modernisierung, Ausstattung, Energiezustand und Mikrolage sind
  nicht vollständig enthalten.
- Kleine Zellbesetzungen und statistische Geheimhaltung erzeugen Unsicherheit.
- Historische oder strukturelle Ungleichheiten des Wohnungsmarkts können sich in
  den Daten fortsetzen.

Die Daten dürfen deshalb nicht für automatisierte rechtliche Entscheidungen,
Bonitätsprüfungen oder individuelle Mietfestsetzungen eingesetzt werden.

## Aktualisierung

GREIX kann quartalsweise mit Download und Build neu erzeugt werden. Die Zensusbasis
wird aktualisiert, sobald ein fachlich vergleichbares amtliches Produkt verfügbar
ist. Nach jeder Quellenaktualisierung sind Datenverträge, räumliche Evaluation,
Intervall-Coverage und App-Texte erneut zu prüfen.
