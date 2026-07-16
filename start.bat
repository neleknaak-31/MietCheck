@echo off
REM ============================================================
REM  MietCheck starten (Windows) - einfach doppelklicken
REM ============================================================
cd /d "%~dp0"
title MietCheck

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo   [!] Python wurde nicht gefunden.
  echo   Bitte Python 3.9+ von https://www.python.org/downloads/ installieren
  echo   und beim Setup den Haken "Add Python to PATH" setzen.
  echo.
  pause
  exit /b
)

echo.
echo   Installiere benoetigte Pakete (nur beim ersten Mal, dauert 1-2 Min.) ...
python -m pip install -r requirements.txt

echo.
echo   Starte MietCheck ... es oeffnet sich der Browser.
echo   Zum Beenden dieses Fenster schliessen oder Strg+C druecken.
echo.
python -m streamlit run app.py

pause
