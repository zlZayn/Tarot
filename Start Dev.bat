@echo off
:: Local dev script: starts Vite dev server (requires Node.js), hot reload
cd /d "%~dp0"

where npm >nul 2>nul
if errorlevel 1 (
    echo [Error] Node.js is required for development.
    echo Please install Node.js first: https://nodejs.org/
    pause
    exit /b 1
)

if not exist node_modules (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [Error] npm install failed.
        pause
        exit /b 1
    )
)

echo Starting dev server at http://localhost:5173 ...
start "Ethereal Tarot Dev" cmd /k npm run dev
timeout /t 2 /nobreak >nul
start http://localhost:5173