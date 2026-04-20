@echo off
chcp 65001 >nul
echo ================================================================================
echo 自动化测试运行器
echo ================================================================================
echo.

:menu
echo 请选择要运行的测试类型：
echo.
echo [1] 运行所有测试（API + UI + E2E）
echo [2] 仅运行 API 测试
echo [3] 仅运行 UI 测试
echo [4] 仅运行 E2E 集成测试
echo [5] 运行冒烟测试（快速验证）
echo [6] 查看测试报告目录
echo [0] 退出
echo.
set /p choice=请输入选项 (0-6): 

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto run_api
if "%choice%"=="3" goto run_ui
if "%choice%"=="4" goto run_e2e
if "%choice%"=="5" goto run_smoke
if "%choice%"=="6" goto view_reports
if "%choice%"=="0" goto end
goto menu

:run_all
echo.
echo 正在运行所有测试...
python Test/run_comprehensive_tests.py all
pause
goto menu

:run_api
echo.
echo 正在运行 API 测试...
python Test/run_comprehensive_tests.py api
pause
goto menu

:run_ui
echo.
echo 正在运行 UI 测试...
python Test/run_comprehensive_tests.py ui
pause
goto menu

:run_e2e
echo.
echo 正在运行 E2E 集成测试...
python Test/run_comprehensive_tests.py e2e
pause
goto menu

:run_smoke
echo.
echo 正在运行冒烟测试...
python Test/run_comprehensive_tests.py smoke
pause
goto menu

:view_reports
echo.
echo 打开测试报告目录...
start Test\reports
pause
goto menu

:end
echo.
echo 感谢使用！
exit /b 0
