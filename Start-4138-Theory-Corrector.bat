@echo off
REM One-click launcher for the VA Form 21-4138 Theory Corrector.
REM Starts the local fill server and opens the tool in your browser.
title VA 21-4138 Theory Corrector
cd /d "%~dp0"

REM Prefer the Python launcher (py), fall back to python.
where py >nul 2>nul && (set "PY=py") || (set "PY=python")

REM Make sure Flask + PyMuPDF are present (quiet; only installs if missing).
%PY% -c "import flask, fitz" >nul 2>nul || (
    echo Installing required packages ^(first run only^)...
    %PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
)

echo.
echo   Starting the VA Form 21-4138 Theory Corrector...
echo   Your browser will open at http://127.0.0.1:4138/
echo   Keep this window open while you work. Close it to stop.
echo.
%PY% server.py

echo.
echo   Server stopped. You can close this window.
pause
