@echo off
chcp 65001 >nul
echo ========================================
echo   狗狗数据分析系统 - 演示模式启动器
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [成功] 依赖包已安装
)

echo.
echo [2/3] 初始化演示数据...
python seed_demo_data.py
if errorlevel 1 (
    echo [错误] 数据初始化失败
    pause
    exit /b 1
)

echo.
echo [3/3] 启动应用...
echo.
echo ========================================
echo   应用启动中...
echo   访问地址: http://localhost:5000
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

set FLASK_ENV=demo
python app.py

pause
