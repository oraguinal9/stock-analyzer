@echo off
chcp 65001 >nul
echo ============================================
echo   股票分析助手 - Web 版 - 启动脚本
echo ============================================
echo.

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo ============================================
echo   启动 Web 服务
echo ============================================
echo   访问地址：http://127.0.0.1:8000
echo ============================================
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
