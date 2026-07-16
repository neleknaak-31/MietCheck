# Finale räumliche Modellevaluation

Stand: 16. Juli 2026

## Versuchsaufbau

Das nach räumlicher Cross-Validation gewählte und abgestimmte Histogram-Gradient-Boosting-Modell wurde auf allen 1.518.322 Entwicklungszeilen trainiert. Die 263.789 Kalibrierungszeilen dienten ausschließlich zur Bestimmung der Prognoseintervalle. Anschließend erfolgte die finale Auswertung auf 276.458 Zeilen aus 99 räumlich getrennten 25-km-Blöcken.

Die finale Testpartition war während Hyperparameteroptimierung, Feature-Ablation und Intervallkalibrierung gesperrt. Frühere Machbarkeits- und Algorithmuspiloten vor Definition dieses Workflows sind ausdrücklich explorativ und nicht Teil der finalen Güteschätzung.

## Punktvorhersage

| Modell | MAE €/m² | Median AE €/m² | RMSE €/m² | R² |
|---|---:|---:|---:|---:|
| Kategorien-Median | 2,292 | 1,560 | 3,339 | -0,022 |
| finales HGB | **1,413** | **0,956** | **2,130** | **0,584** |

Das finale Modell reduziert den MAE gegenüber der fachlichen Kategorien-Baseline um **38,3 %**. Bei einer 70-m²-Wohnung entspricht der MAE als intuitive Größenordnung rund 99 € Nettokaltmiete pro Monat. Diese Umrechnung ist keine individuelle Fehlergarantie.

Der finale Test-MAE ist höher als der Mittelwert der Tuning-Folds. Das ist kein Widerspruch: Die räumliche Zusammensetzung der gesperrten Testblöcke ist anders und die finale Zahl bildet den strengeren Generalisierungsfall ab.

## Unsicherheit und Kalibrierung

Aus den absoluten Fehlern der separaten Kalibrierungspartition wurden endliche Split-Conformal-Quantile berechnet. Die Halbbreite wird nach Gebäudealter- und Wohnungsgrößenklasse angepasst.

| Intervall | nominelles Ziel | beobachtete Test-Coverage | mittlere Gesamtbreite |
|---|---:|---:|---:|
| global | 90 % | 86,77 % | 5,46 €/m² |
| kategoriespezifisch | 90 % | **86,82 %** | 5,46 €/m² |

Das nominelle 90%-Intervall erreicht in unbekannten Raumblöcken nur 86,8 %. Diese Unterdeckung wird als reale Grenze dokumentiert: Die für klassische Split-Conformal-Garantien nötige Austauschbarkeit ist bei räumlichem Verteilungswechsel nicht vollständig erfüllt. In der App wird deshalb **keine 90%-Garantie** behauptet. Stattdessen wird das Band als auf separaten Daten kalibrierter Unsicherheitsbereich mit empirisch rund 87 % Testabdeckung bezeichnet.

Die Coverage liegt bei den beiden Kategorien neuer Gebäude mit 85,1–85,2 % niedriger als bei älteren Gebäuden mit 87,4–87,6 %. Dieses Ergebnis wird in der Modellkarte als Fairness- und Zuverlässigkeitsgrenze hervorgehoben.

## Subgruppen

| Gruppe | Zeilen | MAE €/m² | R² | Intervall-Coverage |
|---|---:|---:|---:|---:|
| amtliches Ziel nicht unsicher markiert | 244.888 | 1,414 | 0,570 | 86,78 % |
| amtliches Ziel unsicher markiert | 31.570 | 1,405 | 0,181 | 87,18 % |
| älter, bis 65 m² | 81.662 | 1,436 | 0,547 | 87,37 % |
| älter, über 65 m² | 114.791 | **1,170** | **0,603** | 87,61 % |
| neuer, bis 65 m² | 29.417 | 1,907 | 0,487 | 85,22 % |
| neuer, über 65 m² | 50.588 | 1,642 | 0,550 | 85,10 % |

Der höhere Fehler für nach 1990 errichtete Wohnungen ist produktrelevant und muss sichtbar kommuniziert werden. Eine pauschale Gleichgüte über alle Wohnungstypen wäre nicht belegt.

## Wichtigste Merkmale

Die Permutationswichtigkeit wurde auf 50.000 separaten Kalibrierungszeilen berechnet, nicht auf dem finalen Test. Die stärksten MAE-Anstiege nach Permutation sind:

1. Nord-Süd-Koordinate: 0,388 €/m²
2. Ost-West-Koordinate: 0,377 €/m²
3. Gebäudealterklasse: 0,099 €/m²
4. Wohnungsgrößenklasse: 0,072 €/m²
5. Unsicherheitskennzeichen der Wohnungszahl: 0,063 €/m²
6. durchschnittliche Wohnfläche: 0,043 €/m²

Permutationswichtigkeit beschreibt prädiktiven Beitrag, keine Kausalität. Bei korrelierten Merkmalen kann sich Wichtigkeit verteilen.

## Fazit

Das Modell besteht die fachlichen Gates: deutliche Verbesserung gegen eine sinnvolle Baseline, räumlich getrennte Evaluation, unabhängige Intervallkalibrierung, nachvollziehbare Subgruppen und ein deploybares Artefakt. Seine Grenzen – insbesondere der regionale Verteilungswechsel, gröbere Wohnungskategorien und die Intervall-Unterdeckung – werden nicht verborgen.

Reproduktion: `python scripts/train_final_model.py`

Maschinenlesbarer Bericht: `reports/final_model_evaluation.json`
