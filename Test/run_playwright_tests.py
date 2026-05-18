"""
Playwright 自动化测试运行脚本
提供多种测试执行模式
"""
import subprocess
import sys
import os
import shlex
from pathlib import Path


def run_command(command, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"\n{'='*60}")
        print(f"🚀 {description}")
        print(f"{'='*60}")
    
    print(f"执行命令: {command}\n")
    
    cmd_list = shlex.split(command, posix=False)
    result = subprocess.run(cmd_list, capture_output=False)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - 成功")
    else:
        print(f"\n❌ {description} - 失败")
    
    return result.returncode


def install_playwright():
    """安装 Playwright 和浏览器"""
    print("\n" + "="*60)
    print("📦 安装 Playwright")
    print("="*60)
    
    # 安装 playwright 包
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], capture_output=False)
    
    subprocess.run(["playwright", "install", "chromium"], capture_output=False)
    
    print("\n✅ Playwright 安装完成")


def run_all_tests():
    """运行所有 Playwright 测试"""
    tests = [
        ("test_virtual_pet_playwright.py", "虚拟宠物功能测试"),
        ("test_auth_playwright.py", "用户认证功能测试"),
        ("test_dashboard_playwright.py", "数据看板功能测试"),
    ]
    
    failed_tests = []
    
    for test_file, description in tests:
        test_path = f"Test/{test_file}"
        if not Path(test_path).exists():
            print(f"\n⚠️  跳过不存在的测试文件: {test_path}")
            continue
        
        cmd_list = ["pytest", test_path, "-v", "--tb=short", "-s"]
        result = subprocess.run(cmd_list, capture_output=False)
        returncode = result.returncode
        
        if returncode != 0:
            failed_tests.append(test_file)
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    if failed_tests:
        print(f"\n❌ 失败的测试: {', '.join(failed_tests)}")
        return 1
    else:
        print("\n✅ 所有测试通过！")
        return 0


def run_specific_test(test_name):
    """运行指定的测试"""
    test_mapping = {
        "pet": "test_virtual_pet_playwright.py",
        "auth": "test_auth_playwright.py",
        "dashboard": "test_dashboard_playwright.py",
    }
    
    if test_name not in test_mapping:
        print(f"\n❌ 未知的测试: {test_name}")
        print(f"可用的测试: {', '.join(test_mapping.keys())}")
        return 1
    
    test_file = test_mapping[test_name]
    test_path = f"Test/{test_file}"
    
    if not Path(test_path).exists():
        print(f"\n❌ 测试文件不存在: {test_path}")
        return 1
    
    cmd_list = ["pytest", test_path, "-v", "--tb=short", "-s", f"--html=Test/reports/{test_name}_test_report.html", "--self-contained-html"]
    return subprocess.run(cmd_list, capture_output=False).returncode


def run_with_headless_mode(headless=True):
    """以无头/有头模式运行测试"""
    os.environ["TEST_HEADLESS"] = str(headless).lower()
    
    mode = "无头模式" if headless else "有头模式（可见浏览器）"
    print(f"\n🔧 设置浏览器模式: {mode}")
    
    return run_all_tests()


def run_with_slow_mo(slow_mo=500):
    """以慢动作模式运行测试（便于观察）"""
    os.environ["TEST_SLOW_MO"] = str(slow_mo)
    
    print(f"\n🐌 设置慢动作模式: {slow_mo}ms")
    
    return run_all_tests()


def generate_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("📝 生成测试报告")
    print("="*60)
    
    # 检查报告目录
    reports_dir = Path("Test/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 列出所有 HTML 报告
    html_reports = list(reports_dir.glob("*_report.html"))
    
    if html_reports:
        print(f"\n找到 {len(html_reports)} 个测试报告:")
        for report in html_reports:
            print(f"  - {report.name}")
            print(f"    路径: {report.absolute()}")
    else:
        print("\n⚠️  未找到测试报告，请先运行测试")
    
    return 0


def show_help():
    """显示帮助信息"""
    help_text = """
╔═══════════════════════════════════════════════════════════╗
║         Playwright 自动化测试运行工具                      ║
╚═══════════════════════════════════════════════════════════╝

用法:
  python run_playwright_tests.py [选项]

选项:
  install          安装 Playwright 和浏览器
  all              运行所有测试（默认）
  pet              运行虚拟宠物测试
  auth             运行用户认证测试
  dashboard        运行数据看板测试
  headless         以无头模式运行所有测试
  visible          以可见浏览器模式运行所有测试
  slow             以慢动作模式运行（便于观察）
  report           查看测试报告
  help             显示此帮助信息

示例:
  python run_playwright_tests.py install     # 首次使用，安装依赖
  python run_playwright_tests.py all         # 运行所有测试
  python run_playwright_tests.py pet         # 只运行宠物测试
  python run_playwright_tests.py visible     # 可见浏览器模式运行
  python run_playwright_tests.py slow        # 慢动作模式运行

环境变数:
  TEST_BASE_URL      测试基础 URL (默认: http://localhost:5000)
  TEST_BROWSER       浏览器类型 (默认: chromium)
  TEST_HEADLESS      无头模式 (默认: true)
  TEST_SLOW_MO       慢动作延迟毫秒数 (默认: 0)
  TEST_TIMEOUT       超时时间毫秒数 (默认: 30000)

注意事项:
  1. 确保 Flask 应用正在运行 (python app.py)
  2. 首次使用需要运行 install 命令安装浏览器
  3. 测试报告保存在 Test/reports/ 目录
  4. 失败的测试会自动截图保存到 Test/reports/screenshots/

    """
    print(help_text)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认运行所有测试
        return run_all_tests()
    
    command = sys.argv[1].lower()
    
    commands = {
        "install": install_playwright,
        "all": run_all_tests,
        "pet": lambda: run_specific_test("pet"),
        "auth": lambda: run_specific_test("auth"),
        "dashboard": lambda: run_specific_test("dashboard"),
        "headless": lambda: run_with_headless_mode(True),
        "visible": lambda: run_with_headless_mode(False),
        "slow": lambda: run_with_slow_mo(500),
        "report": generate_report,
        "help": show_help,
    }
    
    if command in commands:
        return commands[command]()
    else:
        print(f"\n❌ 未知命令: {command}")
        show_help()
        return 1


if __name__ == "__main__":
    exit(main())
