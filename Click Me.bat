@echo off
:: 切换到脚本所在目录
cd /d "%~dp0"
echo Starting Tarot...
:: 先启动服务器（--directory 指定src为根目录）
start /b python -m http.server 8000 --bind 127.0.0.1 --directory src
:: 短暂延迟确保服务器启动完成
timeout /t 1 /nobreak >nul
:: 自动打开浏览器访问本地服务器
start http://localhost:8000