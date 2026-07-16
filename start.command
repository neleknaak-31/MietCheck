#!/bin/bash
# MietCheck starten (Doppelklick auf macOS)
cd "$(dirname "$0")"
echo "🏠 Starte MietCheck …"
if [ ! -f models/mietcheck_model.joblib ]; then
  echo "→ Modell fehlt, führe Datenphase + Training aus …"
  python3 src/data_prep.py && python3 src/train.py
fi
streamlit run app.py
