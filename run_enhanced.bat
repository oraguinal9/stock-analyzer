@echo off
chcp 65001 >nul
echo ============================================================
echo   📈 股票分析助手 - Web 版（增强版）
echo ============================================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查并安装依赖
echo ⏳ 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖...
    pip install -r requirements.txt
)

:: 智能端口检测
set PORT=8000
:check_port
netstat -ano | findstr :%PORT% | findstr LISTENING >nul
if not errorlevel 1 (
    echo ⚠️  端口 %PORT% 被占用，尝试下一个端口...
    set /a PORT+=1
    if %PORT% GTR 8010 (
        echo ❌ 错误：无法找到可用端口（8000-8010）
        pause
        exit /b 1
    )
    goto check_port
)

echo ✅ 使用端口：%PORT%
echo.
echo ============================================================
echo   🚀 启动服务...
echo ============================================================
echo.
echo 访问地址：http://127.0.0.1:%PORT%
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port %PORT% --reload

pause
