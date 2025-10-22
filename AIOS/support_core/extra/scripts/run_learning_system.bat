@echo off
echo Starting AIOS Learning System...
echo.
echo This will run the learning system in a proper interactive terminal.
echo.
cd /d "F:\AIOS_Clean"

REM Try PowerShell 7+ first, fallback to regular Python
"C:\Program Files\PowerShell\7\pwsh.exe" -Command "python aios_complete_learning_system.py" 2>nul
if errorlevel 1 (
    echo PowerShell 7+ not found, using regular Python...
    python aios_complete_learning_system.py
)
pause
