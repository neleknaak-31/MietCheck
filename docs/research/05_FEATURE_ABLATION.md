# Räumliche Feature-Ablation

Stand: 16. Juli 2026

## Ziel

Die Ablation prüft, ob jede Merkmalsgruppe einen messbaren zusätzlichen Beitrag zur Vorhersage in unbekannten Regionen leistet. Alle Stufen verwenden das gewählte HGB-Modell, dieselben 300.000 Entwicklungszeilen und dieselben drei räumlichen Folds. Kalibrierungs- und Testpartition bleiben ungenutzt.

## Ergebnisse

| Merkmalsstufe | Features | MAE €/m² | R² | Verbesserung zur Vorstufe | Verbesserung zu Kategorien |
|---|---:|---:|---:|---:|---:|
| Gebäudealter + Wohnungsgröße | 2 | 1,6452 | 0,044 | – | – |
| + räumlicher Standort | 4 | 1,3506 | 0,291 | **17,9 %** | 17,9 % |
| + numerischer Kontext | 10 | 1,3154 | 0,321 | 2,6 % | 20,1 % |
| + Datenqualitätskennzeichen | 15 | **1,2940** | **0,336** | 1,6 % | **21,3 %** |

Numerischer Kontext umfasst Bevölkerung, durchschnittliche Haushaltsgröße, Eigentümerquote, Leerstandsquote, durchschnittliche Wohnfläche und Wohnungszahl. Die fünf Qualitätskennzeichen zeigen amtlich markierte Unsicherheit in den unabhängigen Kontextquellen an; das Unsicherheitskennzeichen der Zielmiete bleibt wegen Leakage ausgeschlossen.

## Entscheidung

Alle 15 Features werden beibehalten. Der Standort ist erwartungsgemäß die stärkste Merkmalsgruppe, aber Kontext und Datenqualitätskennzeichen verbessern jeden der drei Raum-Folds konsistent. Damit sind sie keine rein dekorativen App-Angaben, sondern tragen nachweisbar zur Generalisierung bei.

Die Zusatzgewinne sind kleiner als der Standorteffekt und werden entsprechend zurückhaltend kommuniziert. Ein kausaler Effekt lässt sich aus der prädiktiven Ablation nicht ableiten.

Reproduktion: `python scripts/feature_ablation.py`

Maschinenlesbarer Bericht: `reports/feature_ablation.json`
