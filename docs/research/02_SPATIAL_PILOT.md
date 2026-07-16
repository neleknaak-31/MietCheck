# Räumlicher ML-Machbarkeitstest

Stand: 16. Juli 2026

## Zweck

Der Pilot prüft, ob die neue offene Datenbasis überhaupt genügend Signal für eine belastbare ML-Aufgabe enthält. Er ist ausdrücklich keine finale Modellauswahl.

## Split

- 2.058.569 Gesamtzeilen
- 1.591.192 Trainingszeilen
- 467.377 Testzeilen
- 530 räumliche 25-km-Blöcke im Training
- 133 vollständig getrennte 25-km-Blöcke im Test
- keine gemeinsamen räumlichen Blöcke
- fester Random State 42

Die räumliche Trennung ist strenger als ein zufälliger Zeilensplit. Sie verhindert, dass dasselbe lokale Umfeld gleichzeitig in Training und Test auftaucht.

## Modelle

1. Kategorien-Median nach Gebäudealter- und Wohnungsgrößenklasse
2. Histogram Gradient Boosting nur mit Koordinaten und beiden Wohnungskategorien
3. Histogram Gradient Boosting mit Koordinaten, Wohnungskategorien und Kontextmerkmalen

Das amtliche Unsicherheitskennzeichen der Zielmiete wurde nach einer Leakage-Prüfung **nicht** als Feature verwendet. Es dient ausschließlich zur getrennten Auswertung.

## Ergebnisse auf dem räumlichen Holdout

| Modell | MAE €/m² | Median AE €/m² | RMSE €/m² | R² |
|---|---:|---:|---:|---:|
| Kategorien-Median | 1,635 | 1,250 | 2,288 | 0,057 |
| Gradient Boosting - Standort | 1,301 | 0,925 | 1,906 | 0,345 |
| Gradient Boosting - Standort + Kontext | **1,258** | **0,886** | **1,862** | **0,376** |

Verbesserung des Kontextmodells gegenüber der Kategorien-Median-Baseline: **23,1 % MAE**. Das vorab definierte Machbarkeitsgate von 15 % ist damit bestanden.

Die Kontextmerkmale verbessern den MAE gegenüber dem reinen Standortmodell zusätzlich um rund 3,3 %. Dieser Effekt ist nützlich, aber deutlich kleiner als der räumliche Effekt und wird in der finalen Ablationsanalyse kritisch geprüft.

## Datenqualität

| Zielgruppe | MAE €/m² | Median AE €/m² | R² |
|---|---:|---:|---:|
| amtlich nicht als unsicher markiert | 1,238 | 0,857 | 0,350 |
| amtlich als unsicher markiert | 1,417 | 1,172 | 0,185 |

Die geringere Güte bei amtlich unsicheren Zielwerten bestätigt, dass das Kennzeichen in App, Modellkarte und Unsicherheitsanalyse sichtbar berücksichtigt werden muss.

## Interpretation

- Die offene Zensusbasis enthält ausreichend Signal für ein echtes ML-Projekt.
- Der räumliche Holdout ist deutlich anspruchsvoller als der bisherige zufällige Split des Prototyps.
- Ein Fehler von 1,258 €/m² entspricht bei 70 m² grob 88 € Monatsmiete. Diese Umrechnung ist nur eine intuitive Größenordnung, da die Zielgröße ein Gitterzellenmittel und keine individuelle Wohnungsmiete ist.
- Das Modell darf daher nicht als amtlicher Mietspiegel oder exakte Einzelwohnungsbewertung bezeichnet werden.

## Noch offene methodische Arbeit

- mehrere räumliche Folds statt eines einzelnen Holdouts
- lineare, Ensemble- und neuronale Vergleichsmodelle
- Hyperparameteroptimierung nur innerhalb der Trainingsblöcke
- endgültige Feature-Ablation
- kalibrierte Vorhersageintervalle und Coverage-Prüfung
- Analyse räumlicher Fehlercluster
- finale Modellkarte und Reproduzierbarkeitsprüfung

Maschinenlesbarer Pilotbericht: `reports/pilot_spatial_metrics.json`.
