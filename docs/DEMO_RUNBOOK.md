# MietCheck – Demo-Runbook

## Vor dem Vortrag

1. App lokal starten: `streamlit run app.py` oder `start.bat`.
2. Browser auf 100 % Zoom und 1440 × 900 oder größer einstellen.
3. Region **Berlin**, Wohnfläche **70 m²**, Baujahr **1985**, aktuelle Kaltmiete **850 €**, Haushaltsnetto **3.200 €** einstellen.
4. Die Tabs **Dein Mietbild**, **Marktverlauf** sowie **Methodik & Quellen** einmal öffnen, damit alle Komponenten geladen sind.
5. Präsentation und App in zwei direkt erreichbaren Fenstern bereithalten.

## Live-Demo in 90 Sekunden

1. **Szenario zeigen – 15 Sekunden:** Berlin, 70 m², Baujahr 1985. Darauf hinweisen, dass Eingaben lokal im Browser bleiben.
2. **Drei Werte erklären – 25 Sekunden:** persönliche Vertragsmiete, ML-Bestandsanker 2022, GREIX-Angebotsmarkt 2026-Q1. Nicht als einen gemeinsamen „richtigen“ Wert formulieren.
3. **Umzugsaufschlag – 15 Sekunden:** 113 % beziehungsweise rund 576 € monatlich bei 70 m². Als deskriptiven Marktvergleich bezeichnen.
4. **Interaktion – 15 Sekunden:** Wohnfläche auf 90 m² ändern oder eine andere abgedeckte Region wählen. Zeigen, dass Monatswerte und persönliche Belastung sofort reagieren.
5. **Transparenz – 20 Sekunden:** Tab **Methodik & Quellen** öffnen und Datenstand, räumlichen Test, Modellvergleich sowie 86,8-%-Coverage zeigen.

## Sprachliche Leitplanken

- Sagen: „Bestandsanker“, „Angebotsmedian“, „deskriptiver Vergleich“, „Modellband“.
- Nicht sagen: „zulässige Miete“, „exakte Marktmiete“, „amtlicher Mietspiegel“, „garantiertes 90-%-Intervall“.

## Offline-Fallback

Wenn die App nicht startet oder das Netz ausfällt:

1. Auf Folie 10 bleiben; sie enthält das geprüfte Berlin-Szenario.
2. Die drei Werte und den Umzugsaufschlag anhand des Screenshots erklären.
3. Bei Detailfragen die statischen Screenshots in `reports/streamlit_overview.png`, `reports/streamlit_market.png` und `reports/streamlit_method.png` öffnen.
4. Reproduzierbarkeit anhand der ausgeführten Notebooks und JSON-Berichte im Repository belegen.

## Technischer Kurzcheck

```powershell
python -m pytest -q
python -m ruff check .
streamlit run app.py
```

Erwartung: 34 Tests erfolgreich; keine Ruff-Fehler; App ohne Browser- oder Requestfehler.
