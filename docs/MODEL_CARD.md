# Modellkarte: MietCheck Zensus-Bestandsmiete

Stand: 16. Juli 2026  
Modellversion: 1.0.0-rc1

## Zweck

Das Modell schätzt die durchschnittliche Nettokaltmiete je Quadratmeter für eine 100-m-Zensus-Gitterzelle und eine grobe Kombination aus Gebäudealter und Wohnungsgröße. Es bildet die **Bestandsmiete zum Zensus-Stichtag 15. Mai 2022** ab und dient in MietCheck als historisch-lokaler Anker für den Vergleich mit aktuellen GREIX-Angebotsmieten.

## Nicht vorgesehene Nutzung

Das Modell ist:

- kein amtlicher Mietspiegel,
- keine Rechtsberatung und keine Prüfung der Mietpreisbremse,
- keine exakte Bewertung einer einzelnen Wohnung,
- keine aktuelle Angebotsmiete,
- nicht für Kredit-, Versicherungs- oder behördliche Entscheidungen gedacht.

## Daten

- Quelle: Statistische Ämter des Bundes und der Länder, Zensus 2022
- offene 100-m-Gitterdaten, Veröffentlichung 2025
- 2.058.569 Zielzeilen in 1.184.386 Gitterzellen
- Lizenz: Datenlizenz Deutschland – Namensnennung – Version 2.0
- Ziel: durchschnittliche Nettokaltmiete €/m²
- Merkmale: LAEA-Koordinaten, Gebäudealterklasse, Wohnungsgrößenklasse, Bevölkerung, Haushaltsgröße, Eigentümerquote, Leerstand, Wohnfläche, Wohnungszahl und fünf amtliche Qualitätskennzeichen

Die Zielvariable und ihr Unsicherheitskennzeichen sind keine Eingabefeatures.

## Modell und Training

- `HistGradientBoostingRegressor`, absolute-error loss
- 1.518.322 Entwicklungszeilen aus 465 25-km-Blöcken
- räumlicher Algorithmusvergleich und räumliches Hyperparameter-Tuning
- 263.789 separate Kalibrierungszeilen aus 99 Blöcken
- 276.458 finale Testzeilen aus weiteren 99 Blöcken
- Random State 2026

## Finale Testgüte

| Kennzahl | Wert |
|---|---:|
| MAE | 1,413 €/m² |
| Median AE | 0,956 €/m² |
| RMSE | 2,130 €/m² |
| R² | 0,584 |
| MAE-Verbesserung zur Kategorien-Baseline | 38,3 % |

## Unsicherheitsbereich

Das kategoriespezifische Split-Conformal-Band wurde auf separaten Regionen kalibriert. Nominelles Ziel waren 90 %, auf den finalen räumlichen Testblöcken wurden 86,8 % erreicht. Die App muss daher „empirisch ca. 87 % Testabdeckung“ anzeigen und darf keine 90%-Garantie versprechen.

Halbbreiten in €/m²:

| Gebäudealter | Wohnungsgröße | Halbbreite |
|---|---|---:|
| bis 1990 | bis 65 m² | 2,877 |
| bis 1990 | über 65 m² | 2,318 |
| nach 1990 | bis 65 m² | 3,477 |
| nach 1990 | über 65 m² | 3,001 |

## Bekannte Grenzen und Risiken

- Räumlicher Verteilungswechsel: unbekannte Regionen können systematisch von Trainingsregionen abweichen.
- Zeitbezug: Die lokale Zensus-Komponente beschreibt 2022, nicht den heutigen Angebotsmarkt.
- Aggregation: Gitterzellenmittel verdecken Unterschiede bei Ausstattung, Etage, Zustand, Energieeffizienz und Mikrolage.
- Grobe Kategorien: Gebäudealter und Wohnungsgröße liegen nur binär vor.
- Gruppenunterschiede: Neue Gebäude weisen MAE 1,64–1,91 €/m² und niedrigere Intervall-Coverage auf.
- Räumliche Koordinaten dominieren die Prognose; Extrapolation außerhalb der Datenabdeckung ist unzulässig.
- Die offene Datenbasis enthält amtlich gekennzeichnete unsichere beziehungsweise geheim gehaltene Werte.

## Schutzmaßnahmen im Produkt

- Bestands-, Angebots- und persönliche Miete werden visuell getrennt.
- Datenstand und Quelle stehen direkt am Ergebnis.
- Prognoseband und empirische Abdeckung sind sichtbar.
- Für nicht abgedeckte oder schwach belegte Regionen wird eine niedrigere Vertrauensstufe angezeigt.
- Negative oder unplausible Eingaben werden validiert.
- Rechtliche Aussagen und Scheingenauigkeit werden vermieden.

## Wartung

Bei neuen Zensus-, GREIX- oder Geodaten müssen Download-Manifest, Datenprofil, räumliche Splits, Modellvergleich, Kalibrierung, Subgruppen und Modellkarte erneut erzeugt werden. Ein Modellupdate ist erst nach bestandenen Tests und dokumentierter Vergleichsmessung zulässig.

Maschinenlesbare Metadaten: `models/zensus_hgb_meta.json`  
Evaluation: `reports/final_model_evaluation.json`
