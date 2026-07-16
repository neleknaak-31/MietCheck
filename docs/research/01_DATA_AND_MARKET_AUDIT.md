# Daten- und Marktaudit

Stand: 16. Juli 2026

## Kurzentscheidung

Der bestehende Prototyp wird nicht unverändert weitergeführt. Die Streamlit-Struktur und Teile der QUA3CK-Dokumentation sind wiederverwendbar, die bisherige fachliche Basis reicht für den Anspruch "aktuell, offen und einzigartig" jedoch nicht aus.

Empfohlene Datenarchitektur:

1. **Zensus 2022, 100-m-Gitter** als offene, deutschlandweite Big-Data-Basis für kleinräumige Bestandsmieten.
2. **GREIX-Mietpreisindex** als laufend aktualisierter Marktanker für Angebotsmieten.
3. Weitere offene Zensus- beziehungsweise Regionalmerkmale nur dann, wenn sie nachweislich zusätzliche Prognosekraft liefern.

## Geprüfte Datenquellen

### 1. Bisheriger Kaggle-/ImmoScout24-Datensatz

- 268.850 Inserate und 49 Variablen
- drei Erhebungszeitpunkte: 22.09.2018, 10.05.2019 und 08.10.2019
- auf Kaggle als vor sechs Jahren aktualisiert ausgewiesen
- Daten gehören laut Datensatzbeschreibung ImmoScout24 und sind für Forschungszwecke vorgesehen

Bewertung: groß und für einen historischen Prototyp brauchbar, aber als alleinige Basis weder aktuell noch lizenzrechtlich ideal für ein öffentliches Produkt.

Quelle: https://www.kaggle.com/datasets/corrieaar/apartment-rental-offers-in-germany

### 2. Zensus 2022 - Miete nach Gebäudealter und Wohnungsgröße

- veröffentlicht am 01.12.2025
- 2.058.569 Datenzeilen
- 1.184.386 unterschiedliche bewohnte 100-m-Gitterzellen
- rund 184 MB unkomprimierte CSV-Daten
- Merkmale: räumliche Koordinaten, Gebäudealterklasse, Wohnungsgrößenklasse und durchschnittliche Nettokaltmiete je Quadratmeter
- keine fehlenden Zielwerte im geprüften Download
- 236.646 Werte sind mit `KLAMMERN` als statistisch relativ unsicher gekennzeichnet
- offene Datenlizenz Deutschland - Namensnennung - Version 2.0
- Geheimhaltung erfolgt über die Cell-Key-Methode; kleine Fallzahlen können dadurch relativ stärker abweichen

Bewertung: sehr starke, offene und deutschlandweite Big-Data-Basis. Es handelt sich um Bestandsmieten mit Stichtag 15.05.2022, nicht um heutige Angebotsmieten. Die Unsicherheitskennzeichnung muss als Feature beziehungsweise Filter berücksichtigt werden.

Reproduzierbarer Build im Projekt:

- 2.058.569 Modellzeilen
- 1.184.386 eindeutige 100-m-Gitterzellen
- 663 räumliche 25-km-Validierungsblöcke
- 19 geprüfte Ausgabespalten
- 22,58 MB komprimiertes Parquet
- keine Duplikate auf dem Zielgrain aus Gitterzelle, Gebäudealterklasse und Wohnungsgrößenklasse
- Kontextabdeckung je Merkmal zwischen 99,1 % und 99,8 %
- 11,5 % der Zielwerte sind amtlich als statistisch relativ unsicher gekennzeichnet

Die Rohdaten werden durch `scripts/download_data.py` heruntergeladen und per SHA-256 dokumentiert. `scripts/build_dataset.py` führt die validierten Joins aus und erzeugt den lokalen Build-Report.

Quellen:

- https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Zensus2022/_publikationen.html
- https://www.destatis.de/static/DE/zensus/gitterdaten/Durchschnittliche_Nettokaltmiete_nach_Gebaeudealter_und_Wohnungsgroe%C3%9Fe.zip
- http://www.govdata.de/dl-de/by-2-0

Verpflichtender Quellenhinweis: Statistische Ämter des Bundes und der Länder, Zensus 2022; eigene Verarbeitung.

### 3. GREIX-Mietpreisindex

- 18.468 veröffentlichte Zeitreihenbeobachtungen
- 37 Städte und Regionen plus deutschlandweiter GREIX-Aggregatwert
- monatliche, vierteljährliche und jährliche Werte ab 2012
- jüngster geprüfter Stand: März beziehungsweise Q1/2026
- Grundlage sind mehr als 60.000 Inserate pro Quartal aus über 100 Plattformen und Maklerwebsites
- hedonischer, qualitätsbereinigter Mietpreisindex mit rollierendem Zwei-Jahres-Fenster
- durchschnittliche, mediane sowie 25.- und 75.-Perzentil-Angebotsmieten

Bewertung: hervorragender aktueller Marktanker, aber kein offener Mikrodatensatz. Er eignet sich zur Zeitkorrektur, Marktspannendarstellung und Validierung, nicht als alleinige Big-Data-Trainingsbasis.

Quelle: https://www.kielinstitut.de/de/institut/forschungszentren/makrooekonomie/makrofinanzen/mietpreisindex/

Verpflichtender Quellenhinweis: Kiel Institut für Weltwirtschaft auf Basis der VALUE Marktdatenbank.

## Konkurrenzbefund

Der einfache Nutzen "faire Miete berechnen" ist nicht einzigartig. Bereits vorhanden sind unter anderem:

- Immowelt mit aktuellen regionalen Quadratmeterpreisen
- Immolyze mit fairer Miete aus Millionen Vergleichsdaten
- Destatis mit einem Zensus-Mietvergleich nach Ort, Gebäudealter und Wohnungsgröße
- kommunale Online-Mietspiegel
- Mietrechts-Apps mit Mietpreisbremse- und Vertragsprüfung
- Vermieterplattformen mit Marktvergleich und Vergleichsobjekten

Beispiele:

- https://www.immowelt.de/immobilienpreise/mietpreise/deutschland
- https://immolyze.de/
- https://service.destatis.de/DE/konferenzen/NIAM2026/mietvergleich.html
- https://www.offenburg.de/de/leben-in-offenburg/buergerservice/qualifizierter-mietspiegel-offenburg-2026/kostenloser-online-rechner-2026/

| Angebot | Bestandsmiete | aktuelle Angebotsmiete | persönliche Leistbarkeit | sichtbare Unsicherheit/Quellen | offene ML-Methodik |
|---|---:|---:|---:|---:|---:|
| Destatis Mietvergleich | ja | nein | nein | teilweise | nein |
| Immowelt Mietpreise | nein | ja | nein | teilweise | nein |
| Immolyze | nicht eindeutig | ja | teilweise | nicht offengelegt | nein |
| kommunale Mietspiegel | ja, rechtlicher Kontext | nein | nein | ja | lokal unterschiedlich |
| geplanter MietCheck | ja | ja | ja | ja | ja |

`Nicht eindeutig` und `nicht offengelegt` bedeuten, dass die jeweilige Information auf den geprüften öffentlichen Produktseiten nicht belastbar dokumentiert war. Sie werden nicht als Beleg für das Fehlen einer internen Funktion interpretiert.

## Vorläufiger USP

MietCheck soll die heute meist getrennten Perspektiven in einer transparenten Analyse verbinden:

- amtliche kleinräumige Bestandsmiete,
- aktuelle qualitätsbereinigte Angebotsmiete,
- persönliche Miete und Leistbarkeit,
- Umzugsaufschlag statt nur eines Marktpreises,
- sichtbare Unsicherheit, Datenalter und Quellen,
- erklärbares Modell statt intransparenter Zahl.

Der USP gilt erst als bestanden, wenn eine strukturierte Konkurrenzmatrix zeigt, dass kein geprüftes Konkurrenzprodukt dieselbe Kombination in einer frei zugänglichen, quellenoffenen Anwendung anbietet.

## Methodische Konsequenzen

- Zielgrößen und Begriffe Bestandsmiete, Angebotsmiete und rechtliche Vergleichsmiete dürfen nicht vermischt werden.
- Zensus-Zellen aus derselben räumlichen Umgebung dürfen nicht zufällig auf Training und Test verteilt werden.
- Die räumliche Generalisierung wird mit gruppierter beziehungsweise räumlicher Kreuzvalidierung geprüft.
- `KLAMMERN`-Werte werden gesondert analysiert; eine pauschale Entfernung ist vor der Sensitivitätsanalyse nicht zulässig.
- Zeitkorrekturen werden gegen veröffentlichte GREIX-Werte validiert.
- Ein Vorhersageintervall darf nicht erneut als pauschales `plus/minus MAE` umgesetzt werden.
- Jede Nutzeransicht nennt Datenstand, Regionsebene, Unsicherheit und Quelle.

## Offene Gates

1. Verfügbarkeit einer belastbaren Ortsauflösung für Nutzereingaben klären.
2. Zusätzliche Zensus-Rastermerkmale auf Prognosegewinn testen.
3. Abdeckung außerhalb der 37 GREIX-Regionen fachlich definieren.
4. Konkurrenzmatrix vollständig und reproduzierbar dokumentieren.
5. Endgültigen Produktnamen und öffentliche Zielgruppe festlegen.
