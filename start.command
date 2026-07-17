#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "[MietCheck] Erzeuge lokale Python-Umgebung ..."
  python3 -m venv .venv
fi

echo "[MietCheck] Installiere oder aktualisiere Abhängigkeiten ..."
".venv/bin/python" -m pip install -r requirements.txt

echo "[MietCheck] Starte Streamlit unter http://localhost:8501"
".venv/bin/python" -m streamlit run app.py
