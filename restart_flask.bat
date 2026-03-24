@echo off
echo ========================================
echo 重启 Flask 应用（v2.5.1）
echo ========================================
echo.

REM 杀死所有 Python 进程
echo [1/3] 停止旧进程...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM 启动新进程
echo [2/3] 启动 Flask 应用...
cd /d D:\PycharmProjects\fastApiProject
start "Flask App" python app.py

REM 等待启动
echo [3/3] 等待应用启动...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ✅ Flask 应用已重启！
echo ========================================
echo.
echo 请访问：http://127.0.0.1:5000
echo 测试页面：http://127.0.0.1:5000/test-pet
echo.
echo 💡 重要提示：
echo 1. 按 Ctrl+Shift+R 强制刷新页面
echo 2. 或按 F12 -> Network -> Disable cache
echo.
pause
