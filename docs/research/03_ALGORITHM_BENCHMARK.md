# Räumlich robuster Algorithmus-Benchmark

Stand: 16. Juli 2026

## Fragestellung

Welcher Regressionsalgorithmus schätzt die durchschnittliche Zensus-Bestandsmiete in bislang ungesehenen räumlichen Gebieten am zuverlässigsten und ist zugleich für Training und Deployment praktikabel?

Dieser Benchmark dient der begründeten Auswahl einer Modellfamilie. Er ist noch keine finale Güteschätzung: Hyperparameteroptimierung, finale räumliche Evaluation und Intervallkalibrierung folgen getrennt.

## Faires Versuchsdesign

- deterministische Stichprobe mit 600.000 der 2.058.569 Beobachtungen
- 660 räumliche 25-km-Blöcke
- drei Folds mit `GroupKFold`
- je Fold 400.000 Trainings- und 200.000 Testbeobachtungen
- identische Zeilen, Features und Folds für alle Kandidaten
- primäre Metrik: mittlerer absoluter Fehler (MAE) in €/m²
- sekundäre Metriken: Median AE, RMSE, R² und Trainingszeit
- Random State 2026

Die räumliche Gruppierung verhindert, dass nahe beieinanderliegende 100-m-Gitterzellen gleichzeitig in Training und Test liegen. Ein zufälliger Zeilensplit würde wegen der starken räumlichen Autokorrelation eine unrealistisch gute Güte vortäuschen.

Das amtliche Unsicherheitskennzeichen der Zielvariable ist kein Feature. Damit wird Ziel-Leakage vermieden. Unsicherheitsmerkmale der unabhängigen Kontextdaten bleiben erlaubt, weil sie zum Vorhersagezeitpunkt bekannt sind.

## Verglichene Modellfamilien

1. Kategorien-Median als einfache fachliche Baseline
2. Ridge-Regression als lineares, regularisiertes Modell
3. LinearSVR als lineare Support-Vector-Regression
4. einzelner Entscheidungsbaum als klassische nichtlineare Referenz
5. Random Forest als Bagging-Ensemble
6. Histogram Gradient Boosting als Boosting-Ensemble
7. mehrschichtiges Perzeptron (MLP) als neuronales Netz

Ridge, LinearSVR und MLP erhalten innerhalb jedes Trainingsfolds
Median-Imputation und `StandardScaler`. Entscheidungsbaum, Random Forest und HGB
werden nicht skaliert, weil ihre Schwellenaufteilungen gegenüber monotoner
Skalierung invariant sind.

## Ergebnisse

| Rang | Modell | MAE €/m² | Standardabweichung | R² | Ø Trainingszeit/Fold |
|---:|---|---:|---:|---:|---:|
| 1 | Histogram Gradient Boosting | **1,305** | 0,055 | **0,402** | 12,8 s |
| 2 | Random Forest | 1,320 | **0,053** | 0,401 | 30,3 s |
| 3 | Decision Tree | 1,393 | 0,037 | 0,347 | 5,4 s |
| 4 | MLP | 1,397 | 0,076 | 0,348 | 74,2 s |
| 5 | Ridge | 1,632 | 0,105 | 0,176 | 1,0 s |
| 6 | LinearSVR | 1,635 | 0,104 | 0,176 | 1,5 s |
| 7 | Kategorien-Median | 1,719 | 0,125 | 0,051 | – |

Histogram Gradient Boosting reduziert den MAE gegenüber der fachlichen Baseline um **24,1 %**. Gegenüber Random Forest beträgt sein MAE-Vorteil nur rund **1,2 %**, es trainiert in diesem Lauf jedoch etwa **2,4-mal schneller**. Die beiden Ensembleverfahren liegen fachlich eng beieinander; die endgültige Aussage darf daher nicht allein auf dem kleinen Abstand ihrer Mittelwerte beruhen.

Das MLP erreichte in allen Folds das Iterationslimit ohne vollständige Konvergenz. Mehr Rechenzeit oder eine gezielte Abstimmung könnten es verbessern, sein aktueller Fehler und die deutlich längere Laufzeit rechtfertigen aber keine Priorisierung für die nächste Stufe.

## Modellentscheidung

**Histogram Gradient Boosting wird als primäre Modellfamilie weitergeführt.** Ausschlaggebend sind:

- niedrigster mittlerer räumlicher CV-MAE,
- praktisch identisches R² zum Random Forest,
- deutlich kürzere Trainingszeit,
- native Eignung für große tabellarische Datensätze,
- kompaktere und schnellere spätere Bereitstellung als ein großer Wald.

Random Forest bleibt Challenger und wird in der finalen Evaluation als Plausibilitätsvergleich beibehalten. Ridge und Kategorien-Median bleiben interpretierbare Referenzen.

## Ergänzende lineare-vs.-Kernel-SVM-Studie

Ein exakter RBF-SVR wächst bei Speicher- und Laufzeitbedarf superlinear und ist
kein glaubwürdiger Vollkandidat für 600.000 Zeilen. `svm_kernel_benchmark.py`
vergleicht deshalb LinearSVR und RBF-SVR ergänzend auf 10.000 deterministischen
Zeilen mit derselben räumlichen 3-Fold-Logik. Beide Varianten nutzen
fold-interne Median-Imputation und `StandardScaler`.

| SVM-Variante | MAE €/m² | R² | Ø Trainingszeit/Fold |
|---|---:|---:|---:|
| LinearSVR | 1,620 | 0,159 | 0,017 s |
| RBF-SVR | **1,518** | **0,214** | 2,315 s |

Der Kernel verbessert die kleine Machbarkeitsstichprobe, skaliert aber nicht
vertretbar in den 600k-Hauptvergleich. Maschinenlesbare Evidenz:
`reports/svm_kernel_benchmark.json`.

## Grenzen und nächste Schritte

- Die 600.000 Beobachtungen sind eine große, aber nicht vollständige Auswahlbasis.
- Es wurden bewusst nur plausible Startparameter verglichen; ein Parametervergleich folgt ausschließlich innerhalb räumlicher Trainingsfolds.
- Drei Folds erlauben noch keinen starken Signifikanzanspruch für den kleinen Abstand zwischen den Ensemblemodellen.
- Die Zielgröße ist ein amtlicher Gitterzellenmittelwert und keine individuelle Angebots- oder Vertragsmiete.
- Als Nächstes folgen räumliche Hyperparameteroptimierung, Feature-Ablation, Fehlerkarten und kalibrierte Vorhersageintervalle.

Reproduktion:

```text
python scripts/algorithm_benchmark.py
python scripts/svm_kernel_benchmark.py
```

Maschinenlesbarer Bericht: `reports/algorithm_benchmark.json`
