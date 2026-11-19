@echo off
rem Rerun every T01 check, then rebuild and open the dashboard.
rem Double-click to run everything (about 12 minutes), or run one step from a terminal:
rem   run_all.bat tests ^| ising ^| petz ^| localpetz ^| scaling ^| dashboard
rem Outputs go to algorithm1\results\student-smoke\ and student-scaling\, never the study folders.
setlocal enabledelayedexpansion
cd /d "%~dp0..\..\.."
set PYTHONUTF8=1
set PY=python
if exist ".venv\Scripts\python.exe" set PY="%CD%\.venv\Scripts\python.exe"
set SMOKE=algorithm1\results\student-smoke
set ONLY=%~1
set SUMMARY=

call :step tests "Test suite (about 2 min)"
call :step ising "Ising Algorithm 1 figures (about 1 min)"
call :step petz "Ising Petz circuit counts (under 1 min)"
call :step localpetz "Local Petz bath figures and CNOT counts (about 7 min)"
call :step scaling "Image-size scaling benchmark (about 1 min)"
call :step dashboard "Rebuild dashboard"

echo.
echo ==================== Summary ====================
for %%s in (!SUMMARY!) do echo   %%~s
echo.
if "%ONLY%"=="" start "" "algorithm1\dashboard\dashboard.html"
if "%ONLY%"=="dashboard" start "" "algorithm1\dashboard\dashboard.html"
pause
goto :eof

:step
if not "%ONLY%"=="" if not "%ONLY%"=="%~1" exit /b 0
echo.
echo ==================== %~2 ====================
call :run_%~1
if errorlevel 1 (set SUMMARY=!SUMMARY! "FAILED  %~2") else (set SUMMARY=!SUMMARY! "ok      %~2")
exit /b 0

:run_tests
pushd algorithm1
%PY% -m pytest -q
set RC=%errorlevel%
popd
exit /b %RC%

:run_ising
%PY% algorithm1\python\run_ising_algorithm1.py --output %SMOKE%\ising-algorithm1 || exit /b 1
%PY% algorithm1\python\plot_ising_algorithm1.py --input %SMOKE%\ising-algorithm1
exit /b %errorlevel%

:run_petz
%PY% algorithm1\python\run_ising_petz.py artifacts --output %SMOKE%\ising-petz
exit /b %errorlevel%

:run_localpetz
%PY% algorithm1\python\run_local_petz.py dense --output %SMOKE%\local-petz || exit /b 1
echo Compare these CNOT counts with the table in algorithm1\local-petz.md (around line 100):
%PY% algorithm1\python\run_local_petz.py resources --output %SMOKE%\local-petz || exit /b 1
%PY% algorithm1\python\plot_local_petz.py --input %SMOKE%\local-petz
exit /b %errorlevel%

:run_scaling
rem Add options here for a longer run, e.g. --burn 4000 --samples 8000 --chains 4 --noise 60
%PY% algorithm1\python\benchmark_sizes.py
exit /b %errorlevel%

:run_dashboard
%PY% algorithm1\dashboard\build_dashboard.py
exit /b %errorlevel%
