"""
简单测试执行脚本
绕过有问题的 allure 插件，直接运行测试并生成报告
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def run_tests():
    """运行所有测试"""
    print("=" * 80)
    print("🧪 狗狗数据分析系统 - 自动化测试执行")
    print("=" * 80)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 构建 pytest 命令（不使用 allure）
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "Test/test_auth.py",
        "Test/test_breed.py",
        "-v",
        "--tb=short",
        "--strict-markers",
        f'--html=Test/reports/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html',
        "--self-contained-html",
    ]

    print(f"执行命令：{' '.join(cmd)}")
    print("-" * 80)
    print()

    try:
        # 执行测试
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

        # 打印输出
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        print()
        print("=" * 80)
        if result.returncode == 0:
            print("✅ 所有测试通过！")
        else:
            print(f"❌ 测试失败，退出码：{result.returncode}")
        print("=" * 80)

        return result.returncode

    except Exception as e:
        print(f"❌ 执行失败：{str(e)}")
        return 1


def generate_simple_report():
    """生成简单的 JSON 报告"""
    report_dir = Path("Test/reports")
    report_dir.mkdir(exist_ok=True)

    report = {
        "summary": {
            "note": "测试执行完成，详细结果请查看 HTML 报告",
            "timestamp": datetime.now().isoformat(),
        }
    }

    report_file = (
        report_dir / f'test_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📄 测试摘要已保存：{report_file}")


if __name__ == "__main__":
    exit_code = run_tests()
    generate_simple_report()
    sys.exit(exit_code)
