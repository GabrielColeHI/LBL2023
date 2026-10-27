@echo off
rem Rebuild the results dashboard and open it in the default browser.
cd /d "%~dp0..\.."
set PY=python
if exist ".venv\Scripts\python.exe" set PY=.venv\Scripts\python.exe
%PY% algorithm1\dashboard\build_dashboard.py || (pause & exit /b 1)
start "" "algorithm1\dashboard\dashboard.html"
