@echo off
setlocal
rem ============================================================
rem  Levanta la copia local del Portal BI en este equipo.
rem
rem  Uso, desde esta carpeta:   .\iniciar_portal.cmd [puerto]   (o doble clic)
rem  (por default 8080)
rem
rem  No depende del usuario ni del equipo: todo es relativo a esta carpeta.
rem  La primera vez crea venv\ e instala las versiones fijas de
rem  requirements.txt (necesita internet); despues ya no instala nada.
rem  Solo escucha en 127.0.0.1: nadie mas en la red lo puede abrir.
rem ============================================================
cd /d "%~dp0"

set "PORTAL_PORT=%~1"
if "%PORTAL_PORT%"=="" set "PORTAL_PORT=8080"
set "PORTAL_HOST=127.0.0.1"

if not exist "app.py" (
  echo Esta no es la carpeta del portal: falta app.py. Corre el archivo desde la carpeta descomprimida.
  goto :fallo
)

rem -- Python: primero el lanzador py, luego python del PATH ----------
set "PY="
where py >nul 2>nul && py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && python -c "import sys" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo No encuentro Python 3 en este equipo. Instalalo desde el Portal de Empresa / Software Center y vuelve a correr esto.
  goto :fallo
)

rem -- venv: se crea una sola vez, dentro de esta carpeta ------------
if not exist "venv\Scripts\python.exe" (
  echo Primera vez en este equipo: creando venv e instalando dependencias...
  %PY% -m venv venv || goto :fallo
)
venv\Scripts\python.exe -c "import flask, waitress, flask_compress, dotenv" >nul 2>nul
if errorlevel 1 (
  venv\Scripts\python.exe -m pip install -q --disable-pip-version-check -r requirements.txt
  if errorlevel 1 (
    echo No se pudieron instalar las dependencias. Revisa la conexion a internet y vuelve a correrlo.
    goto :fallo
  )
)

rem -- Puerto libre --------------------------------------------------
netstat -ano | findstr /r /c:":%PORTAL_PORT% .*LISTENING" >nul
if not errorlevel 1 (
  echo El puerto %PORTAL_PORT% ya esta ocupado. Usa otro:  .\iniciar_portal.cmd 8090
  goto :fallo
)

echo.
echo Portal BI local -^> http://127.0.0.1:%PORTAL_PORT%/   (Ctrl+C para detenerlo)
echo Datos inventados: los tableros muestran la banda "Datos inventados".
echo.
rem El navegador abre unos segundos despues, cuando el servidor ya escucha.
start "" /min powershell -NoProfile -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:%PORTAL_PORT%/'"
venv\Scripts\python.exe servir.py
exit /b %errorlevel%

:fallo
echo.
pause
exit /b 1
