@echo off
:: 给最终用户/朋友的启动脚本（需要 Python；零额外依赖，无需 Node.js）
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
:: 启动器：自动探测端口（8000 被占用则顺延）、退出无残留、自动打开浏览器
python server\serve.py --dir dist --open
pause