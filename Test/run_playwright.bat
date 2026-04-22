@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo   Playwright 自动化测试 - 一键启动脚本
echo ================================================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [步骤 1/4] 检查 Flask 应用是否运行...
echo.
echo 提示: 请确保在另一个窗口中已运行: python app.py
echo.
pause

echo.
echo [步骤 2/4] 安装 Playwright 依赖...
pip install playwright pytest-playwright -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装完成

echo.
echo [步骤 3/4] 安装 Chromium 浏览器...
playwright install chromium
if errorlevel 1 (
    echo [错误] 浏览器安装失败
    pause
    exit /b 1
)
echo ✓ 浏览器安装完成

echo.
echo [步骤 4/4] 选择测试模式:
echo.
echo   1. 运行所有测试（无头模式 - 快速）
echo   2. 运行所有测试（可见浏览器 - 便于观察）
echo   3. 只运行虚拟宠物测试
echo   4. 只运行用户认证测试
echo   5. 只运行数据看板测试
echo   6. 慢动作模式（每步延迟 500ms）
echo   7. 查看帮助文档
echo.
set /p choice=请输入选项 (1-7): 

echo.
if "%choice%"=="1" (
    echo 正在运行所有测试（无头模式）...
    python Test\run_playwright_tests.py all
) else if "%choice%"=="2" (
    echo 正在运行所有测试（可见浏览器）...
    set TEST_HEADLESS=false
    python Test\run_playwright_tests.py all
) else if "%choice%"=="3" (
    echo 正在运行虚拟宠物测试...
    python Test\run_playwright_tests.py pet
) else if "%choice%"=="4" (
    echo 正在运行用户认证测试...
    python Test\run_playwright_tests.py auth
) else if "%choice%"=="5" (
    echo 正在运行数据看板测试...
    python Test\run_playwright_tests.py dashboard
) else if "%choice%"=="6" (
    echo 正在以慢动作模式运行...
    python Test\run_playwright_tests.py slow
) else if "%choice%"=="7" (
    python Test\run_playwright_tests.py help
    pause
    exit /b 0
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   测试完成！
echo ================================================================================
echo.
echo 测试报告位置: Test\reports\*.html
echo 失败截图位置: Test\reports\screenshots\*.png
echo.
echo 按任意键查看报告目录...
pause >nul

explorer Test\reports

echo.
echo 感谢使用 Playwright 自动化测试框架！
echo.
pause
