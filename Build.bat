@echo off
:: 本地构建脚本：类型检查 + 生成 dist/ 发布目录（需要 Node.js）
cd /d "%~dp0"

where npm >nul 2>nul
if errorlevel 1 (
    echo [Error] Node.js is required to build this project.
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

echo Type checking...
call npm run typecheck
if errorlevel 1 (
    echo [Error] Type check failed.
    pause
    exit /b 1
)

echo Building project...
call npm run build
if errorlevel 1 (
    echo [Error] Build failed.
    pause
    exit /b 1
)

echo.
echo Build finished. dist/ is ready.
echo Run Click Me.bat to serve it, then run tests:
echo   python tests/run_checks.py http://localhost:8000
echo   python tests/run_e2e.py  http://localhost:8000
pause