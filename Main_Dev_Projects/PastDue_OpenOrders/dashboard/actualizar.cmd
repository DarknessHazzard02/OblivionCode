@echo off
rem Made by: Hazzard
rem Recalcula el tablero con el corte del dia y lo abre en http://127.0.0.1:8766/
rem La carpeta de las fuentes sale de config.local.json; sin ese archivo usa los datos inventados.
cd /d "%~dp0"
python generar_datos.py
if errorlevel 1 (
  echo.
  echo No se pudo generar el tablero. Revisa el mensaje de arriba.
  pause
  exit /b 1
)
start "" http://127.0.0.1:8766/
python -m http.server 8766 --bind 127.0.0.1
