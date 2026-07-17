# Risiko-, Datenschutz- und Ethikbewertung

## Einsatzgrenze

MietCheck ist eine explorative Entscheidungshilfe für Bildung und
Markttransparenz. Die App darf nicht als amtlicher Mietspiegel, Rechtsprüfung,
adressgenaue Bewertung, Bonitätsentscheidung oder Empfehlung für eine zulässige
Miethöhe verwendet werden.

## Datenschutz

- Die Trainingsdaten sind veröffentlichte, statistisch geschützte
  100-m-Gitteraggregate und enthalten keine Namen, Vertragsnummern oder Adressen.
- Die App fragt nur Region, Wohnfläche, Baujahr, optionale Kaltmiete und optionales
  Haushaltsnettoeinkommen ab.
- Eingaben werden im Arbeitsspeicher der Streamlit-Sitzung verarbeitet und vom
  Projektcode weder protokolliert noch dauerhaft gespeichert.
- Es gibt keine Nutzerkonten, Tracker, Werbenetzwerke oder externe
  Inferenzschnittstelle.
- Betreiberlogs der Deployment-Plattform liegen außerhalb des Projektcodes und
  müssen nach den Einstellungen und Datenschutzbedingungen der Plattform geprüft
  werden.

## Modell- und Datenrisiken

| Risiko | mögliche Folge | Gegenmaßnahme |
|---|---|---|
| räumlicher Verteilungswechsel | Fehler in bislang ungesehenen Regionen | 25-km-Gruppensplits, finales räumliches Holdout, sichtbarer Test-MAE |
| unterdecktes Intervall | falsches Sicherheitsgefühl | empirische Coverage 86,8 % statt nominale 90 % anzeigen |
| schwächere Neubauleistung | verzerrte Einordnung neuer Gebäude | kategorieweise Intervalle und Grenze in App/Modellkarte |
| fehlende Wohnungsmerkmale | konkrete Wohnung weicht stark ab | keine adressgenaue Behauptung; Ausstattung/Mikrolage explizit nennen |
| Zeitdifferenz 2022/2026 | Bestands- und Angebotseffekt wird verwechselt | drei Messkonzepte trennen und jeden Datenstand direkt anzeigen |
| GREIX-Stadtauswahl | Übertragungsfehler auf nicht erfasste Orte | App auf 37 belegte lokale Märkte beschränken |
| amtliche Geheimhaltung/Unsicherheit | instabilere Zellmittel | Unsicherheitsflag analysieren; Ergebnisse aggregiert ausgeben |

## Fairness und gesellschaftliche Wirkung

Das Modell verwendet keine direkten sensiblen Merkmale wie Religion,
Staatsangehörigkeit oder ethnische Zuordnung. Räumliche und sozioökonomische
Kontextmerkmale können dennoch bestehende Segregation und historische
Ungleichheiten indirekt abbilden. Eine gute Prognose ist deshalb nicht automatisch
eine faire oder normativ wünschenswerte Miete.

MietCheck formuliert Ergebnisse deskriptiv: Es zeigt beobachtete Bestands- und
Angebotsunterschiede, legitimiert sie aber nicht. Das Modell ist nicht für
Vermieterentscheidungen, Preisoptimierung oder die Auswahl von Mietinteressierten
bestimmt.

## Missbrauchsszenarien

- **Mieterhöhung begründen:** unzulässig, weil der Wert weder Rechtsgrundlage noch
  qualifizierter Mietspiegel ist.
- **Wohnung als „zu teuer“ deklarieren:** unzulässig, weil Ausstattung,
  Vertragslage und Mikrolage fehlen.
- **Haushalte nach Leistbarkeit sortieren:** unzulässig; die Belastungsquote ist
  nur eine persönliche Szenariorechnung.
- **Werte auf nicht abgedeckte Orte übertragen:** unzulässig; die App lässt nur
  belegte GREIX-Regionen zu.

## Technische und betriebliche Risiken

- Quellen-URLs oder Schemas können sich ändern. Mindestgröße, Signatur,
  Datenverträge und Tests lassen den Build dann kontrolliert scheitern.
- Ein neues scikit-learn-Release kann Joblib-Artefakte inkompatibel machen.
  Versionsgrenzen und Modellmetadaten dokumentieren die Trainingsumgebung.
- Eine neue GREIX-Veröffentlichung darf erst nach Plausibilitätsprüfung,
  Screenshot-Test und Aktualisierung des Datenstands deployt werden.
- Die App zeigt voraggregierte Modellprofile und benötigt im Produktivbetrieb
  keinen Zugriff auf Rohdaten.

## Freigabegate vor jeder Veröffentlichung

1. Daten- und Lizenzstand prüfen.
2. Download- und Datenvertragstests ausführen.
3. räumliche Modellgüte und Intervall-Coverage erneut messen.
4. AppTest sowie Desktop-/Mobil-Smoke-Test durchführen.
5. Quellen, Stichtage und Grenzen in README, App, Datenblatt und Modellkarte
   synchronisieren.
6. öffentliche App auf fehlende Geheimnisse und unerwartete Loggingpfade prüfen.
