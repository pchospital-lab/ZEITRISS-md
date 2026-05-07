@echo off
REM ZEITRISS - Windows-Launcher.
REM
REM Doppelklickbar. Findet Python (py / python3 / python) und startet den
REM plattform-unabhängigen Python-Launcher scripts\zeitriss.py.
REM
REM Falls Python fehlt: Hinweis mit Download-Link, dann Pause.

setlocal
cd /d "%~dp0"

REM Windows Installer legt meist den "py"-Launcher an.
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%~dp0scripts\zeitriss.py" %*
    goto :end
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3 "%~dp0scripts\zeitriss.py" %*
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%~dp0scripts\zeitriss.py" %*
    goto :end
)

echo.
echo   Python wurde nicht gefunden.
echo.
echo   ZEITRISS braucht Python 3 (kostenlos, einmalige Installation).
echo   Download: https://www.python.org/downloads/
echo.
echo   WICHTIG im Installer: "Add python.exe to PATH" anhaken!
echo.
pause
exit /b 1

:end
endlocal
