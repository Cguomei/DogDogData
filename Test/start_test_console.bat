@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   🧪 智能测试控制台 - 启动器
echo ============================================================
echo.

cd /d "%~dp0.."

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/3] 检查依赖包...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask未安装，正在安装...
    pip install flask flask-cors
) else (
    echo ✅ Flask已安装
)

python -c "import flask_cors" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask-CORS未安装，正在安装...
    pip install flask-cors
) else (
    echo ✅ Flask-CORS已安装
)

echo.
echo [3/3] 启动测试控制台服务...
echo.
echo ============================================================
echo   🌐 服务即将启动
echo   📍 访问地址: http://localhost:5555
echo   💡 按 Ctrl+C 停止服务
echo ============================================================
echo.

python Test\test_server.py

pause
