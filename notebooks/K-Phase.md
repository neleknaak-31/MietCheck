# K-Phase · Knowledge Transfer

## 1. Ziel

Die K-Phase übersetzt das räumlich validierte Zensusmodell in die Streamlit-App **MietCheck**. Der Erkenntnisgewinn ist nicht „die eine richtige Miete“, sondern die methodisch saubere Trennung von Bestandsanker 2022, aktuellem GREIX-Angebotsmarkt und persönlicher Mietbelastung.

## 2. Architektur der Streamlit-Anwendung

1. Versioniertes HGB-Modell und Metadaten erzeugen regionale Bestandsprofile.
2. GREIX liefert aktuelle Angebotsmediane und Interquartilsabstände.
3. `src/app_logic.py` berechnet Umzugsaufschlag und persönliche Belastung.
4. `app.py` stellt Ergebnisse, Zeitbezug, Quellen, Unsicherheit und Grenzen interaktiv dar.
5. Die Laufzeit-App benötigt weder Rohdaten noch Trainingsmatrix oder MLflow-Server.

## 3. UI/UX und Nutzerführung

- **Dein Mietbild:** Region, Fläche, Baualter, persönliche Kaltmiete und Einkommen
- **Drei getrennte Werte:** eigene Miete, ML-Bestandsanker, GREIX-Angebotsmedian
- **Marktverlauf:** Quartalszeitreihe plus Markt-IQR
- **Methodik & Quellen:** Datenstand, Spatial Holdout, Modellvergleich, Coverage und Disclaimer
- **Responsiv:** klare Karten, wenige Farben und dieselbe visuelle Sprache wie die Präsentation

## 4. Toolentwicklung und Datenintegration

Öffentliche Downloads werden automatisiert bezogen, per SHA-256 dokumentiert und in Rohdaten, Trainingsmatrix, Reports und kleine App-Datenprodukte getrennt. GitHub Actions führt Ruff, Pytest, Datenverträge, Modellgates und Docker-Build aus. MLflow protokolliert A¹, A³ und das finale C/K-Artefakt; die Registry markiert den Champion.

## 5. ML-Integration

Der `HistGradientBoostingRegressor` nutzt 15 räumliche, wohnungsbezogene und qualitätsbezogene Merkmale. Er benötigt keinen `StandardScaler`; skalierte Pipelines wurden in A¹ korrekt für Ridge, LinearSVR, RBF-SVR und MLP verwendet. Split Conformal Prediction liefert kategoriespezifische Modellbänder. Das Modellartefakt, Metadaten und Evaluation sind über ein SHA-256-Manifest verbunden.

## 6. App-Screenshots für Präsentation und Dokumentation

- `reports/streamlit_overview.png` – Eingaben, drei Mietrealitäten und Umzugsaufschlag
- `reports/streamlit_market.png` – aktueller Markt und Zeitreihe
- `reports/streamlit_method.png` – Methodik, Quellen, Modellgüte und Grenzen

Die Präsentation führt ohne Live-Demo durch Q, U, A, C und K. Die Screenshots sind belastbarer als ein Netzwerk-abhängiger Live-Ablauf und entsprechen dem Prüfhinweis.

## 7. Ergebnis und Produktnutzen

MietCheck basiert auf 2.058.569 Modellzeilen und aktuellen GREIX-Daten bis 2026-Q1. Der finale räumliche Test-MAE beträgt 1,413 €/m², eine Verbesserung von 38,3 % gegenüber dem Kategorienmedian. Die empirische 90-%-Intervall-Coverage liegt bei 86,8 % und wird sichtbar kommuniziert.

Der USP ist die quelloffene Verbindung aus **kleinräumigem ML-Bestandsanker, aktuellem Angebotsmarkt, persönlicher Belastung und getrennten Unsicherheiten**. Die App bleibt bis zur gemeinsamen Endabnahme privat; Repository, Methode und Artefakte sind öffentlich nachvollziehbar.

## 8. Grenzen und verantwortungsvolle Nutzung

Kein Mietspiegel, keine Rechtsberatung, keine adressgenaue Angebotsprognose. Persönliche Eingaben werden nicht gespeichert. Regionen ohne GREIX-Abdeckung erhalten keine erfundenen aktuellen Marktwerte.

---

**Reproduzierbarkeit:** `README.md`, `docs/DATA_CARD.md`, `docs/MODEL_CARD.md`, `docs/RISK_AND_ETHICS.md`, `reports/` und die ausgeführten Phasen-Notebooks bilden die vollständige Nachweiskette.
