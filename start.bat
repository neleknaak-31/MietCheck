@echo off
setlocal
cd /d "%~dp0"
title MietCheck

if not exist ".venv\Scripts\python.exe" (
  echo [MietCheck] Erzeuge lokale Python-Umgebung ...
  python -m venv .venv || exit /b 1
)

echo [MietCheck] Installiere oder aktualisiere Abhaengigkeiten ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1

echo [MietCheck] Starte Streamlit unter http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
endlocal
