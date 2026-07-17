# MietCheck – Sprechskript für 10–15 Minuten

Zielzeit: **12 Minuten Vortrag plus Fragen**. Die Folien 13 und 14 sind Backup-Folien und werden nur bei Rückfragen gezeigt.

## Folie 1 – Einstieg (0:00–0:40)

„Wer heute umzieht, vergleicht meist zwei Zahlen, die methodisch nicht vergleichbar sind: die eigene Bestandsmiete und aktuelle Angebotsmieten. MietCheck trennt deshalb drei Realitäten: den lokalen Wohnungsbestand, den aktuellen Angebotsmarkt und die persönliche Belastung. Meine Leitfrage lautet: Wie lässt sich diese Lücke mit einem großen, offenen Datensatz, einem räumlich belastbar evaluierten ML-Modell und einer transparenten App sichtbar machen?“

## Folie 2 – Drei Mietrealitäten (0:40–1:25)

„Der Bestandsanker basiert auf dem Zensus-Stichtag 15. Mai 2022. Der Angebotsmarkt kommt aus dem aktuellen GREIX-Quartal 2026-Q1. Die persönliche Realität entsteht aus Vertragsmiete, Wohnfläche und optional dem Haushaltsnettoeinkommen. Der Mehrwert liegt gerade darin, diese Werte nicht zu vermischen. Der Umzugsaufschlag beschreibt die Differenz zwischen lokalem Bestand und heutigem Angebot, ohne daraus eine Rechtsaussage abzuleiten.“

## Folie 3 – Alleinstellungsmerkmal (1:25–2:10)

„Bestehende Lösungen decken Teilprobleme ab: Destatis zeigt Bestand, Immobilienportale zeigen aktuelle Angebote, Mietspiegel liefern kommunale Vergleichswerte. In meiner Marktprüfung habe ich kein offenes Angebot gefunden, das Bestand, aktuellen Markt, persönliche Belastung, Unsicherheit und eine vollständig nachvollziehbare ML-Methode gemeinsam zeigt. Genau diese Kombination ist der USP – nicht ein weiterer Preisrechner.“

## Folie 4 – Datenbasis (2:10–3:00)

„Die ML-Basis besteht aus sieben amtlichen Zensusprodukten im 100-Meter-Gitter. Nach dem reproduzierbaren Build entstehen 2,06 Millionen Modellzeilen auf 1,18 Millionen eindeutigen Rasterzellen. Der GREIX bleibt bewusst getrennt: Er aktualisiert die Marktseite der App, wird aber nicht als historisch unpassendes Trainingsziel in das Zensusmodell gemischt. Downloads, SHA-256-Prüfsummen und Datenverträge machen die Herkunft prüfbar.“

## Folie 5 – QUA³CK-Nachweiskette (3:00–3:50)

„QUA³CK ist hier kein Inhaltsverzeichnis, sondern eine Kette von überprüfbaren Entscheidungen. Qualität prüft Hashes, Granularität und Missingness. Understanding dokumentiert EDA und räumliche Struktur. Auswahl vergleicht fünf Modellfamilien. Anpassung umfasst acht Tuningvarianten und vier Ablationen. Anwendung erzeugt Modell und Kalibrierung. Comparing misst den unangetasteten Test und Subgruppen. Knowledge übersetzt das Ergebnis in die App. Alle sieben Notebooks sind ausgeführt: 33 von 33 Codezellen, ohne Fehleroutput.“

## Folie 6 – Räumlicher Holdout (3:50–4:45)

„Ein zufälliger Zeilensplit wäre bei benachbarten 100-Meter-Zellen zu optimistisch. Deshalb fasse ich Zellen in 25-Kilometer-Blöcke zusammen und trenne ganze Räume. 465 Blöcke liegen in Entwicklung, 99 ausschließlich in der Kalibrierung und 99 ausschließlich im finalen Test. Zwischen den Mengen gibt es keinen gemeinsamen Block. Der Test simuliert damit besser die Übertragung in unbekannte Räume.“

## Folie 7 – Modellvergleich (4:45–5:40)

„Alle Modelle sehen dieselben 600.000 Entwicklungszeilen und dieselbe dreifache Spatial-Cross-Validation. HistGradientBoosting erreicht mit 1,305 Euro pro Quadratmeter den besten mittleren CV-MAE. Random Forest liegt mit 1,320 dicht dahinter. Ridge und der Kategorienmedian bleiben deutlich schwächer. Ich wähle HGB wegen der besten Güte, der kleinen Artefaktgröße und der schnellen Inferenz; Random Forest bleibt als dokumentierter Challenger erhalten.“

## Folie 8 – Finaler Test und Unsicherheit (5:40–6:45)

„Nach Modellwahl und Tuning wird der finale Test genau einmal ausgewertet. Der MAE beträgt 1,413 Euro pro Quadratmeter, der Medianfehler 0,956 und R² 0,584. Gegenüber dem Kategorienmedian verbessert sich der Fehler um 38,3 Prozent. Für die Intervalle nutze ich Split Conformal Prediction auf der separaten Kalibrierungsmenge. Das nominale 90-Prozent-Intervall erreicht räumlich 86,8 Prozent. Diese Unterdeckung wird nicht versteckt, sondern in App, Model Card und Risikoanalyse ausgewiesen.“

## Folie 9 – Erkenntnis am Beispiel Berlin (6:45–7:35)

„Für das gezeigte Berliner Szenario liegt der modellierte Bestandsanker bei 7,27 Euro pro Quadratmeter. Der aktuelle GREIX-Angebotsmedian beträgt 15,50 Euro. Das sind rund 113 Prozent beziehungsweise ungefähr 576 Euro monatlicher Aufschlag bei 70 Quadratmetern. Das ist keine exakte Wohnungsbewertung, sondern eine nachvollziehbare Größenordnung für die Umzugsentscheidung.“

## Folie 10 – App und Live-Demo (7:35–9:20)

„Die Streamlit-App übersetzt die Methodik in eine kurze Entscheidungskette: Erst Region und Wohnungsszenario, dann drei klar getrennte Vergleichswerte, anschließend Unsicherheit und Grenzen direkt am Ergebnis.“

Jetzt die Demo nach `docs/DEMO_RUNBOOK.md` durchführen. Nicht länger als 90 Sekunden demonstrieren.

## Folie 11 – Grenzen und verantwortliche Nutzung (9:20–10:15)

„Das Modell kennt weder Ausstattung, Energiezustand, Etage noch adressgenaue Mikrolage. Es ist kein amtlicher Mietspiegel und keine Rechtsberatung. Regionen ohne GREIX werden nicht mit erfundenen Marktwerten gefüllt. Die empirische Coverage von 86,8 statt nominal 90 Prozent steht sichtbar im Produkt. Datenschutz, Bias und mögliche Fehlanwendungen sind im Risk Assessment dokumentiert.“

## Folie 12 – Fazit (10:15–11:10)

„MietCheck behauptet nicht, die eine faire Miete zu kennen. Es trennt drei Mietrealitäten und macht ihre Differenz nachvollziehbar. Die technische Basis sind 2,06 Millionen Modellzeilen, ein räumlicher Holdout, 38,3 Prozent Verbesserung gegenüber der Baseline und transparent kommunizierte 86,8 Prozent Coverage. Der eigentliche Mehrwert ist deshalb nicht die Prognose allein, sondern eine besser informierte Umzugsentscheidung.“

## Abschluss und Übergang zu Fragen (11:10–12:00)

„Code, Notebooks, Modellartefakt, Datenpipeline, Tests, Präsentation und Handout sind öffentlich reproduzierbar im Repository. Vielen Dank – ich freue mich auf Ihre Fragen.“

## Typische Rückfragen

- **Warum kein Deep Learning?** Tabellarische, überwiegend kategoriale und räumliche Daten; HGB erreicht bessere validierte Güte bei kleinerem Artefakt und einfacher reproduzierbarer Inferenz.
- **Warum GREIX nicht mittrainieren?** Zensus und GREIX messen unterschiedliche Zeitpunkte und Realitäten. Eine Vermischung würde Aktualität suggerieren, aber das Trainingsziel methodisch verfälschen.
- **Warum 25-km-Blöcke?** Sie reduzieren räumliches Leakage deutlich und liefern ausreichend viele Gruppen für Entwicklung, Kalibrierung und Test.
- **Warum nur 86,8 % Coverage?** Conformal Prediction garantiert unter Austauschbarkeit; räumlicher Distribution Shift verletzt diese Annahme teilweise. Die Abweichung ist ein Ergebnis, kein Grund zum Schönrechnen.
- **Was wäre der nächste Schritt?** Wiederholter Zensus-/Mikrozensus-Refresh, breitere offene Angebotsdaten, räumlich adaptive Kalibrierung und Monitoring der Coverage über Zeit.
