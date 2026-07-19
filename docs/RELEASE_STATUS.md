# MietCheck – Release-Status

Stand: 19. Juli 2026

## Aktueller Zustand

| Oberfläche | Status | Beleg |
|---|---|---|
| GitHub-Repository | öffentlich | `https://github.com/neleknaak-31/MietCheck` |
| Streamlit-Deployment | deployt, aber private Abnahme | Dashboard-Einstellung `Only specific people can view this app` |
| App-Adresse | reserviert | `https://mietcheck.streamlit.app/` |
| Öffentliche Produktfreigabe | noch nicht erteilt | finales Release-Gate in `REQUIREMENTS_CHECKLIST.md` |

Die private Streamlit-Sichtbarkeit ist beabsichtigt. Sie verhindert, dass die
App während der gemeinsamen fachlichen und visuellen Prüfung bereits allgemein
zugänglich oder über Streamlit auffindbar ist. Das öffentliche Repository bleibt
davon unabhängig verfügbar.

## Freigabegate für die öffentliche App

Die Streamlit-App wird erst öffentlich geschaltet, wenn alle folgenden Punkte
erfüllt und durch die Projekteigentümerin ausdrücklich freigegeben sind:

1. lokaler Testlauf, Ruff-Prüfung und ML-Release-Gates sind erfolgreich;
2. GitHub Actions ist auf dem veröffentlichten `main`-Stand grün;
3. App-Inhalte, Datenstände, Quellen, Grenzen und Screenshots sind synchron;
4. Präsentation, Handout, Sprechskript und Demo-Runbook sind final geprüft;
5. Name, Matrikelnummer, prüfende Person und Abgabetermin sind eingetragen;
6. die Projekteigentümerin bestätigt die öffentliche Veröffentlichung.

## Prüfung unmittelbar nach der Freigabe

1. Im Streamlit-Dashboard `This app is public and searchable` auswählen und
   speichern.
2. `https://mietcheck.streamlit.app/` in einer nicht angemeldeten Sitzung
   öffnen.
3. Startansicht, Marktverlauf und Methodik-Tab vollständig prüfen.
4. Den anonymen Produktions-Smoke-Test dokumentieren.
5. Den Streamlit-Punkt in `REQUIREMENTS_CHECKLIST.md` auf `ERFÜLLT` setzen und
   diesen Release-Status aktualisieren.
