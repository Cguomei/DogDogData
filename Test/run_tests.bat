@echo off
chcp 65001 >nul
echo ================================================
echo FastApi 项目自动化测试
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)

echo [信息] Python 版本检查通过
echo.

REM 创建报告目录
if not exist Test\reports mkdir Test\reports

echo [信息] 开始运行测试...
echo.

REM 运行测试并生成报告
python -m pytest Test/ ^
    -v ^
    --tb=short ^
    --html=Test/reports/report_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.html ^
    --self-contained-html ^
    --junitxml=Test/reports/junit_report.xml ^
    -s

if errorlevel 1 (
    echo.
    echo [警告] 部分测试失败
) else (
    echo.
    echo [成功] 所有测试通过！
)

echo.
echo ================================================
echo 测试完成，报告已保存到：
echo   Test/reports/
echo ================================================
echo.
echo 按任意键查看 Bug 统计...
pause >nul

REM 显示 Bug 统计
python -c "from bug_tracker import bug_tracker; print(bug_tracker.generate_report())"

echo.
echo 按任意键退出...
pause >nul
