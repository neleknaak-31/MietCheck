# MietCheck – Screenshot-Runbook

## Prüfungsformat

Die Präsentation benötigt **keine Live-Demo**. Die K-Phase wird mit drei
verifizierten Screenshots gezeigt:

1. `reports/streamlit_overview.png` – persönliches Mietbild und Umzugsaufschlag
2. `reports/streamlit_market.png` – GREIX-Marktverlauf und Markt-IQR
3. `reports/streamlit_method.png` – Pipeline, Modellvergleich, MLOps und Grenzen

Damit bleibt der Vortrag unabhängig von Netzwerk, Streamlit-Login und
Cloud-Verfügbarkeit. Die private App muss für die Präsentation nicht öffentlich
geschaltet werden.

## Screenshot-Prüflauf vor dem Vortrag

1. App lokal oder privat in Streamlit öffnen.
2. Berlin, 70 m², Baujahr 1985, Kaltmiete 850 €, Haushaltsnetto 3.200 € setzen.
3. Alle drei Tabs auf 1440 × 900 oder größer bei 100 % Zoom prüfen.
4. Sicherstellen, dass Datenstand 2026-Q1, 7-Kandidaten-Vergleich, 36 Tests und
   86,8-%-Coverage sichtbar beziehungsweise dokumentiert sind.
5. Screenshots in Präsentation und PDF visuell auf Lesbarkeit kontrollieren.

## Erzählung auf den K-Folien

- **Dein Mietbild:** persönliche Miete, ML-Bestandsanker und GREIX-Angebot
  bleiben getrennt; der Umzugsaufschlag ist ein deskriptiver Vergleich.
- **Marktverlauf:** Median und Markt-IQR zeigen aktuelle Angebotsstreuung; sie
  sind nicht das Modellband.
- **Methodik & Quellen:** Spatial Holdout, StandardScaler bei
  skalenempfindlichen Kandidaten, sieben Hauptkandidaten, finale Testgüte,
  Coverage und Disclaimer sind Teil des Produkts.

## Sprachliche Leitplanken

- Sagen: „Bestandsanker“, „Angebotsmedian“, „deskriptiver Vergleich“,
  „Modellband“, „empirische Coverage“.
- Nicht sagen: „zulässige Miete“, „exakte Marktmiete“, „amtlicher Mietspiegel“,
  „garantiertes 90-%-Intervall“.

## Optionaler App-Fallback bei Rückfragen

Falls der Professor nach dem Vortrag ausdrücklich Interaktion sehen möchte,
kann die App lokal mit `streamlit run app.py` geöffnet werden. Dies ist ein
optionaler Rückfragen-Fallback, kein Teil des geplanten Vortrags.

## Technischer Kurzcheck

```powershell
python -m pytest -q
python -m ruff check .
streamlit run app.py
```

Erwartung: 36 Tests erfolgreich, keine Ruff-Fehler und App ohne
Browser-/Requestfehler.
