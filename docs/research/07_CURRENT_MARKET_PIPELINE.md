# Aktuelle Markt- und Regionspipeline

Stand: 16. Juli 2026

## Zweck

Das Alleinstellungsmerkmal von MietCheck entsteht erst durch die saubere Trennung und Verknüpfung zweier Mietrealitäten:

- **Bestandsmiete:** lokal modellierter Zensus-Anker zum 15. Mai 2022
- **Angebotsmiete:** nominaler GREIX-Marktwert bis Q1/2026

Beide Werte werden nicht als identische Zielgrößen ausgegeben. Ihre Differenz ist der deskriptive **Umzugsaufschlag**: der Abstand zwischen typischer aktueller Angebotsmiete und lokalem Bestandsmietanker.

## GREIX-Aufbereitung

Die offizielle GREIX-Arbeitsmappe enthält Monats-, Quartals- und Jahreswerte sowie nominale und inflationsbereinigte Reihen. Die App verwendet ausschließlich nominale Quartalswerte:

- 2.166 Region-Quartal-Beobachtungen
- 37 Städte beziehungsweise Kreise plus nationale GREIX-Referenz
- Q1/2012 bis Q1/2026
- Mittelwert, Median, 25. und 75. Perzentil der Angebotsmiete
- Quartals- und Jahresänderung des Index

Validierungen verhindern doppelte Region-Quartale, vertauschte Perzentile, unplausible Preise und veraltete Releases.

## Räumliche Verknüpfung

Die 37 lokalen GREIX-Regionen wurden einmalig über OpenStreetMap Nominatim georeferenziert. Die Abfragen erfolgten sequenziell mit 1,1 Sekunden Abstand; die Ergebnisse werden inklusive OSM-Typ, OSM-ID und Anzeigename gespeichert und unter ODbL attribuiert.

Die WGS84-Koordinaten werden mit `pyproj` nach ETRS89-LAEA (EPSG:3035), dem Koordinatensystem der Zensusgitter, transformiert. Für jede Region entsteht ein robuster Kontextvektor aus den Medianen von bis zu 500 bewohnten beziehungsweise mietbeobachteten Zensuszellen im Umkreis von 10 km. Falls weniger als 30 Zellen im Radius liegen, werden die 100 nächsten Zellen verwendet.

Aus diesem Kontext erzeugt das finale Modell vier Bestandsmietanker:

1. Gebäude bis 1990, Wohnung bis 65 m²
2. Gebäude bis 1990, Wohnung über 65 m²
3. Gebäude nach 1990, Wohnung bis 65 m²
4. Gebäude nach 1990, Wohnung über 65 m²

Die zugehörigen empirischen Unsicherheitsbreiten werden aus der Modellkalibrierung übernommen.

## Produktgrenzen

- Der Regionsmittelpunkt repräsentiert keine konkrete Adresse oder jeden Stadtteil.
- GREIX deckt 37 lokale Märkte ab, nicht alle deutschen Gemeinden.
- Zensus-Bestands- und GREIX-Angebotsmiete unterscheiden sich in Zeitbezug und Mietpopulation.
- Der Umzugsaufschlag ist eine transparente Vergleichskennzahl, keine kausale Schätzung und keine Rechtsaussage.
- Das GREIX-Interquartilsband beschreibt Marktstreuung; das Modellband beschreibt Prognoseunsicherheit. Beide dürfen visuell nicht vermischt werden.

## Reproduktion

```text
python scripts/download_data.py
python scripts/build_greix.py
python scripts/build_region_profiles.py
```

Ein erneuter Nominatim-Abruf ist nur mit `--refresh-centres` nötig. Standardmäßig wird die geprüfte, attribuierte Lookup-Datei verwendet.

Maschinenlesbare Produkte:

- `data/app/greix_quarterly.csv`
- `data/app/greix_latest.csv`
- `data/app/greix_metadata.json`
- `data/app/greix_region_centres.csv`
- `data/app/region_profiles.csv`
- `data/app/region_profiles_metadata.json`
