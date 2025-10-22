@echo off
echo AIOS PowerShell Setup
echo ====================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - Good!
) else (
    echo WARNING: Not running as administrator
    echo Some features may not work properly
    echo.
)

echo Installing AIOS PowerShell wrapper...
echo.

REM Run the PowerShell setup script
powershell -ExecutionPolicy Bypass -File "setup_aios_powershell.ps1"

if %errorLevel% == 0 (
    echo.
    echo ✅ Installation completed successfully!
    echo.
    echo To start using AIOS PowerShell commands:
    echo 1. Restart PowerShell, or
    echo 2. Run: . $PROFILE
    echo.
    echo Then try: aios
) else (
    echo.
    echo ❌ Installation failed with error code: %errorLevel%
    echo Please check the error messages above.
)

pause
