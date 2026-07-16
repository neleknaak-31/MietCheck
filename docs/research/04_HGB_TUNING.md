# Räumliches Hyperparameter-Tuning

Stand: 16. Juli 2026

## Schutz vor Optimismus

Vor dem Tuning wurden die 663 räumlichen 25-km-Blöcke deterministisch in drei disjunkte Bereiche geteilt:

| Partition | Zeilen | Blöcke | Zweck |
|---|---:|---:|---|
| Entwicklung | 1.518.322 | 465 | Hyperparameterwahl und Training |
| Kalibrierung | 263.789 | 99 | spätere Prognoseintervalle |
| Test | 276.458 | 99 | einmalige finale Güteschätzung |

Kalibrierungs- und Testpartition wurden während der Parametersuche weder trainiert noch ausgewertet. Die Gruppenlisten sind über SHA-256-Fingerabdrücke im maschinenlesbaren Bericht nachprüfbar. Diese Sperre gilt ab Beginn des Tuning-Workflows; frühere Machbarkeits- und Algorithmus-Piloten werden separat als explorativ ausgewiesen.

## Suchdesign

- Modellfamilie: Histogram Gradient Boosting
- 750.000 deterministisch gezogene Entwicklungszeilen
- 463 in der Stichprobe vertretene Entwicklungsblöcke
- drei identische `GroupKFold`-Folds je Kandidat
- acht theoriegeleitete Kombinationen statt unkontrollierter Brute-Force-Suche
- primäre Metrik: MAE in €/m²
- sekundär: Fold-Streuung, schlechtester Fold, R² und Laufzeit
- Early Stopping ausschließlich innerhalb des jeweiligen äußeren Trainingsfolds

Variiert wurden Lernrate, maximale Iterationen, Blattzahl, minimale Blattgröße und L2-Regularisierung.

## Rangfolge

| Rang | Kandidat | MAE €/m² | Standardabweichung |
|---:|---:|---:|---:|
| 1 | 6 | **1,2701** | 0,0318 |
| 2 | 7 | 1,2708 | 0,0322 |
| 3 | 8 | 1,2721 | **0,0318** |
| 4 | 5 | 1,2721 | 0,0348 |
| 5 | 3 | 1,2736 | 0,0366 |
| 6 | 4 | 1,2757 | 0,0342 |
| 7 | 2 | 1,2860 | 0,0396 |
| 8 | 1 | 1,2911 | 0,0420 |

Die Top-Kandidaten liegen eng beieinander. Die Auswahl von Kandidat 6 stützt sich daher nicht auf einen behaupteten großen Effekt, sondern auf den niedrigsten mittleren MAE und zugleich den niedrigsten schlechtesten Fold-MAE der getesteten Varianten.

## Gewählte Parameter

```text
learning_rate       = 0.06
max_iter            = 300
max_leaf_nodes      = 127
min_samples_leaf    = 100
l2_regularization   = 5.0
loss                = absolute_error
```

Die komplexere Baumstruktur mit stärkerer L2-Regularisierung verbessert die räumliche Generalisierung geringfügig. Da der Abstand zu Kandidat 7 und 8 klein ist, wird die Schlussfolgerung als robuste praktische Auswahl und nicht als statistischer Beweis der Überlegenheit formuliert.

## Nächste methodische Stufe

1. räumliche Feature-Ablation nur innerhalb der Entwicklungspartition,
2. Training des gewählten Modells auf allen Entwicklungsblöcken,
3. Intervallkalibrierung auf der reservierten Kalibrierungspartition,
4. einmalige Auswertung auf der reservierten Testpartition,
5. Modellkarte, Fehlercluster und Deployment-Artefakte.

Reproduktion: `python scripts/tune_hgb.py`

Maschinenlesbarer Bericht: `reports/hgb_tuning.json`
