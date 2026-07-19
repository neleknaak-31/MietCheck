# MietCheck – Sprechskript für 10–15 Minuten

Zielzeit: **etwa 12 Minuten plus Fragen**. Folie 15 ist eine Backup-Folie.
Die App wird anhand von drei Screenshots gezeigt; eine Live-Demo ist nicht
vorgesehen.

## Folie 1 – Einstieg (0:00–0:35)

„MietCheck führt von 2,06 Millionen amtlichen Zensuszeilen zu einer
persönlichen Umzugsentscheidung. Ich zeige den vollständigen QUA³CK-Prozess:
Fragestellung, Datenverständnis, drei A-Phasen, finale Bewertung und
Wissenstransfer in die App.“

## Folie 2 – Q: Forschungsfrage (0:35–1:25)

„Die Leitfrage lautet: Wie groß ist die Lücke zwischen lokalem Bestand,
aktuellem Angebot und persönlicher Mietbelastung? Der Bestandsanker bezieht sich
auf den Zensus-Stichtag 15. Mai 2022, der Angebotsmarkt auf GREIX 2026-Q1 und
die persönliche Realität auf Vertrag, Fläche und optionales Einkommen.“

## Folie 3 – Q: USP und Gates (1:25–2:10)

„Der USP ist nicht ein weiterer Preisrechner. MietCheck verbindet Bestand,
aktuellen Markt, persönliche Belastung, Marktstreuung, Modellunsicherheit und
eine offene ML-Methode. Vor dem finalen Test gelten vier Gates: mindestens zwei
Millionen Zeilen, sieben Kandidaten inklusive Baseline, räumlicher Holdout und
mindestens 15 Prozent MAE-Verbesserung.“

## Folie 4 – U: Datenbasis (2:10–3:00)

„Sieben amtliche Zensus-Gitterprodukte werden über die 100-Meter-Gitter-ID
verbunden. Daraus entstehen 2,058 Millionen Modellzeilen auf 1,184 Millionen
eindeutigen Zellen. GREIX bleibt bewusst getrennt, weil Angebot 2026 und Bestand
2022 nicht dasselbe Ziel messen. URLs, Hashes, Datenverträge und Missingness
unter einem Prozent sichern die Herkunft.“

## Folie 5 – U: StandardScaler (3:00–4:10)

„Der StandardScaler ist bei Ridge, LinearSVR, RBF-SVR und MLP notwendig, weil
sonst Größen wie Koordinaten in Metern kleine Prozentmerkmale dominieren. Zuerst
wird im Trainingsfold imputiert, dann werden nur dort Mittelwert und
Standardabweichung gelernt und anschließend z-transformiert. Dadurch entsteht
kein Leakage. Bäume und HGB brauchen keine Skalierung; deshalb speichert der
HGB-Champion bewusst keinen unnötigen Scaler.“

## Folie 6 – A: räumlicher Split (4:10–5:00)

„Benachbarte 100-Meter-Zellen sind ähnlich. Ein Random Split wäre daher zu
optimistisch. MietCheck trennt 25-Kilometer-Blöcke: 465 für Entwicklung, 99 nur
für Intervallkalibrierung und 99 nur für den finalen Test. Zwischen den drei
Mengen gibt es null gemeinsame Blöcke.“

## Folie 7 – A¹: Algorithmenauswahl (5:00–6:00)

„Sieben Hauptkandidaten laufen auf denselben 600.000 Zeilen und denselben drei
Spatial Folds: Kategorienmedian, Ridge, LinearSVR, Decision Tree, Random Forest,
HGB und MLP. HGB erreicht mit 1,305 Euro pro Quadratmeter den besten CV-MAE.
Random Forest bleibt Challenger. Ein exakter RBF-SVR wird zusätzlich auf 10.000
räumlich validierten Zeilen geprüft, weil Kernel-SVR nicht glaubwürdig auf
600.000 Zeilen skaliert.“

## Folie 8 – A²/A³: Features und Tuning (6:00–6:55)

„Vier Feature-Stufen zeigen, dass Lage den größten Zusatznutzen liefert.
Anschließend werden acht theoriegeleitete HGB-Konfigurationen automatisiert
verglichen. Kalibrierungs- und Testblöcke bleiben dabei gesperrt. Die Auswahl
berücksichtigt mittleren MAE, Streuung und schlechtesten Fold.“

## Folie 9 – C: finaler Test (6:55–7:55)

„Der unangetastete Test umfasst 276.458 Zeilen aus 99 Raumblöcken. Der MAE liegt
bei 1,413 Euro pro Quadratmeter, R² bei 0,584 und die Verbesserung gegenüber dem
Kategorienmedian bei 38,3 Prozent. Split Conformal Prediction erreicht
empirisch 86,8 statt nominal 90 Prozent Coverage. Diese Unterdeckung wird offen
kommuniziert.“

## Folie 10 – K: Dein Mietbild (7:55–8:40)

„Der erste Screenshot zeigt die Übersetzung in die Nutzerentscheidung:
persönliche Miete, Bestandsanker und Angebotsmedian bleiben getrennt. Für das
Berliner 70-Quadratmeter-Szenario wird der deskriptive Umzugsaufschlag direkt in
Euro und Prozent sichtbar.“

## Folie 11 – K: Marktverlauf (8:40–9:20)

„Der zweite Screenshot zeigt den aktuellen GREIX-Verlauf und den Markt-IQR.
Diese Streuung beschreibt heutige Angebote. Sie ist methodisch etwas anderes
als das Modellband des Zensusmodells.“

## Folie 12 – K: Methodik in der App (9:20–10:05)

„Der dritte Screenshot belegt, dass Transparenz Teil des Produkts ist:
Datenstand, Spatial Holdout, sieben Kandidaten, MLOps-Lineage, finale Testgüte,
Coverage und Grenzen stehen direkt in der App. Eine Live-Demo ist deshalb nicht
nötig.“

## Folie 13 – Grenzen (10:05–10:55)

„Das Modell kennt Ausstattung, Energiezustand, Etage und adressgenaue Mikrolage
nicht. Es ist kein Mietspiegel und keine Rechtsberatung. Regionen ohne GREIX
werden nicht erfunden. Der Zeitversatz und die 86,8-Prozent-Coverage stehen
sichtbar in App, Model Card und Risk Assessment.“

## Folie 14 – Fazit (10:55–11:45)

„Q definiert den Mehrwert, U prüft Daten und Skalierung, A wählt und optimiert,
C bewertet ehrlich und K überträgt das Wissen in die App. MietCheck behauptet
nicht, die eine faire Miete zu kennen. Es übersetzt Big Data und transparentes
Machine Learning in eine nachvollziehbare Umzugsentscheidung.“

## Folie 15 – Backup: Quellen und Reproduzierbarkeit

Nur bei Rückfragen zeigen. Zensus, GREIX, vier ausgeführte Rechennotebooks,
K-Transfer, JSON-Reports, Tests, CI, MLflow, Karten und Docker sind im
Repository nachvollziehbar.

## Typische Rückfragen

- **Warum kein Deep Learning als Champion?** Das tabellarische HGB generalisiert
  besser, trainiert effizient und liefert ein kleines Artefakt.
- **Warum GREIX nicht mittrainieren?** Zensus und GREIX messen unterschiedliche
  Zeitpunkte und Mietrealitäten.
- **Warum nur 10.000 Zeilen beim RBF-SVR?** Exakter Kernel-SVR skaliert
  superlinear; die Teilstudie prüft den Kernel, ohne ihn als 600k-Kandidaten
  auszugeben.
- **Warum kein Scaler im finalen Artefakt?** HGB ist skaleninvariant. Der
  StandardScaler gehört korrekt in die Pipelines der skalenempfindlichen
  Vergleichsmodelle.
- **Warum nur 86,8 % Coverage?** Räumlicher Distribution Shift schwächt die
  Austauschbarkeitsannahme. Die Abweichung ist ein wichtiges Ergebnis.
