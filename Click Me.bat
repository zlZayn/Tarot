@echo off
:: Launcher for end users / friends: serves dist/ (requires Python only)
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python is required to run this app.
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "dist\index.html" (
    echo [Error] dist folder not found or incomplete.
    echo This package must include the dist folder. Ask the developer for a full release.
    pause
    exit /b 1
)

echo Starting Ethereal Tarot...
:: serve.py picks a free port (8000 -> 8001 ...), exits clean, opens the browser
python server\serve.py --dir dist --open
pause