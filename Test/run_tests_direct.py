"""
直接导入并运行测试用例
完全绕过 pytest 命令行和 allure 插件
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from importlib import import_module


class TestRunner:
    """简单的测试运行器"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def run_test(self, test_module, test_class, test_method):
        """运行单个测试方法"""
        try:
            # 导入模块
            module = import_module(test_module)
            # 获取类
            cls = getattr(module, test_class)
            # 获取方法
            method = getattr(cls, test_method)

            # 创建实例并运行
            instance = cls()
            method()

            return {
                "status": "PASS",
                "test": f"{test_module}.{test_class}.{test_method}",
                "error": None,
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "test": f"{test_module}.{test_class}.{test_method}",
                "error": str(e),
            }

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("🧪 狗狗数据分析系统 - 测试执行")
        print("=" * 80)
        print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self.start_time = datetime.now()

        # 定义要运行的测试
        tests_to_run = [
            # 认证测试
            ("Test.test_auth", "TestUserAuthentication", "test_register_success"),
            ("Test.test_auth", "TestUserAuthentication", "test_login_success"),
            ("Test.test_auth", "TestUserAuthentication", "test_logout"),
            # 品种管理测试
            ("Test.test_breed", "TestBreedManagement", "test_get_breeds_list"),
        ]

        total = len(tests_to_run)
        passed = 0
        failed = 0

        for i, (module, cls, method) in enumerate(tests_to_run, 1):
            print(f"[{i}/{total}] 运行 {module}.{cls}.{method}...", end=" ")
            result = self.run_test(module, cls, method)
            self.results.append(result)

            if result["status"] == "PASS":
                print("✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL: {result['error']}")
                failed += 1

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        print()
        print("=" * 80)
        print(f"总计：{total} | ✅ 通过：{passed} | ❌ 失败：{failed}")
        print(f"耗时：{duration:.2f}秒")
        print("=" * 80)

        return passed == total

    def save_report(self):
        """保存测试报告"""
        report_dir = Path("Test/reports")
        report_dir.mkdir(exist_ok=True)

        report = {
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r["status"] == "PASS"),
                "failed": sum(1 for r in self.results if r["status"] == "FAIL"),
                "duration": (
                    (self.end_time - self.start_time).total_seconds()
                    if self.end_time
                    else 0
                ),
            },
            "results": self.results,
            "timestamp": datetime.now().isoformat(),
        }

        report_file = (
            report_dir / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 测试报告已保存：{report_file}")

        # 生成 HTML 报告
        html_file = (
            report_dir / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        )
        self.generate_html(report, html_file)
        print(f"📄 HTML 报告已保存：{html_file}")

    def generate_html(self, report, filename):
        """生成简单的 HTML 报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>测试报告 - {report['timestamp'][:10]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .summary {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .pass {{ color: #28a745; font-weight: bold; }}
        .fail {{ color: #dc3545; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 测试报告</h1>
        
        <div class="summary">
            <h2>摘要</h2>
            <p><strong>总测试数:</strong> {report['summary']['total']}</p>
            <p><strong class="pass">✅ 通过:</strong> {report['summary']['passed']}</p>
            <p><strong class="fail">❌ 失败:</strong> {report['summary']['failed']}</p>
            <p><strong>耗时:</strong> {report['summary']['duration']:.2f}秒</p>
            <p><strong>生成时间:</strong> {report['timestamp']}</p>
        </div>
        
        <h2>测试结果详情</h2>
        <table>
            <tr>
                <th>#</th>
                <th>测试名称</th>
                <th>状态</th>
                <th>错误信息</th>
            </tr>
"""

        for i, result in enumerate(report["results"], 1):
            status_class = "pass" if result["status"] == "PASS" else "fail"
            status_icon = "✅" if result["status"] == "PASS" else "❌"

            html += f"""
            <tr>
                <td>{i}</td>
                <td>{result['test']}</td>
                <td class="{status_class}">{status_icon} {result['status']}</td>
                <td>{result.get('error', '-') or '-'}</td>
            </tr>
"""

        html += """
        </table>
    </div>
</body>
</html>
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    runner.save_report()
    sys.exit(0 if success else 1)
