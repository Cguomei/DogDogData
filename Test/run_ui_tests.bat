@echo off
chcp 65001 >nul
echo ========================================
echo   UI/E2E 测试执行脚本
echo ========================================
echo.

REM 检查Flask应用是否运行
echo [1/3] 检查Flask应用状态...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flask应用未运行！
    echo.
    echo 请先启动Flask应用：
    echo    python app.py
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)
echo ✅ Flask应用正在运行
echo.

REM 选择测试类型
echo [2/3] 选择测试类型：
echo    1. UI测试 (41个用例)
echo    2. E2E测试 (9个用例)
echo    3. 全部测试
echo.
set /p choice="请输入选项 (1/2/3): "

echo.
echo [3/3] 开始执行测试...
echo ========================================
echo.

if "%choice%"=="1" (
    echo 执行UI测试...
    python -m pytest Test/ui_tests/ -v --tb=short --headed --html=Test/reports/ui_test_report.html --self-contained-html
) else if "%choice%"=="2" (
    echo 执行E2E测试...
    python -m pytest Test/e2e_tests/ -v --tb=short --headed --html=Test/reports/e2e_test_report.html --self-contained-html
) else if "%choice%"=="3" (
    echo 执行UI + E2E测试...
    python -m pytest Test/ui_tests/ Test/e2e_tests/ -v --tb=short --headed --html=Test/reports/ui_e2e_test_report.html --self-contained-html
) else (
    echo 无效选项，执行UI测试...
    python -m pytest Test/ui_tests/ -v --tb=short --headed
)

echo.
echo ========================================
echo 测试完成！
echo 报告位置: Test/reports/
echo ========================================
echo.
pause
