@echo off
:: Developer entry: Rich launcher (build freshness check, run panel)
:: Requires uv; the friend-facing Click Me.bat stays zero-dependency.
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo [Error] uv is required for the Rich launcher.
    echo Install it from https://docs.astral.sh/uv/
    pause
    exit /b 1
)

echo Starting Rich launcher...
uv run python launcher.py
pause