@echo off
:: 本地开发脚本：启动 Vite 开发服务器（需要 Node.js），改代码自动刷新
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