"""
测试覆盖率统计与报告生成工具
自动分析测试用例覆盖情况，生成详细报告
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path


class TestCoverageAnalyzer:
    """测试覆盖率分析器"""

    def __init__(self, test_dir="."):
        self.test_dir = Path(test_dir)
        if not self.test_dir.exists():
            # 如果在 Test 目录下运行，使用上级目录
            self.test_dir = Path.cwd()
        self.test_files = []
        self.test_cases = []
        self.coverage_stats = {}

    def find_test_files(self):
        """查找所有测试文件"""
        pattern = re.compile(r"test_.*\.py$")
        self.test_files = [
            f for f in self.test_dir.glob("*.py") if pattern.match(f.name)
        ]
        print(f"找到 {len(self.test_files)} 个测试文件")
        return self.test_files

    def extract_test_cases(self):
        """从测试文件中提取测试用例信息"""
        test_case_pattern = re.compile(
            r'@test_case\([\'"]([^\'"]+)[\'"],\s*priority=[\'"]([^\'"]+)[\'"].*?\)\s*\n\s*def\s+(test_[^\(]+)',
            re.MULTILINE | re.DOTALL,
        )

        pytest_test_pattern = re.compile(r"def\s+(test_[^\(\s]+)\s*\(", re.MULTILINE)

        for test_file in self.test_files:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取装饰器标记的测试用例
            matches = test_case_pattern.findall(content)
            for match in matches:
                case_id, priority, func_name = match
                self.test_cases.append(
                    {
                        "file": test_file.name,
                        "case_id": case_id,
                        "priority": priority,
                        "function": func_name,
                        "type": "decorated",
                    }
                )

            # 提取 pytest 风格的测试函数
            pytest_matches = pytest_test_pattern.findall(content)
            for func_name in pytest_matches:
                # 避免重复
                if not any(tc["function"] == func_name for tc in self.test_cases):
                    self.test_cases.append(
                        {
                            "file": test_file.name,
                            "case_id": f"PYTEST-{func_name}",
                            "priority": "Medium",
                            "function": func_name,
                            "type": "pytest",
                        }
                    )

        print(f"提取到 {len(self.test_cases)} 个测试用例")
        return self.test_cases

    def analyze_module_coverage(self):
        """分析各模块的测试覆盖情况"""
        modules = {
            "用户认证": ["test_auth.py"],
            "品种管理": ["test_breed.py", "test_api.py"],
            "图表功能": ["test_charts.py"],
            "路由页面": ["test_routes.py", "test_routes_extended.py"],
            "数据模型": ["test_models.py", "test_models_extended.py"],
            "安全性": ["test_security.py"],
            "自定义分析": ["test_custom_analysis.py"],
            "虚拟宠物": ["test_virtual_pet.py", "test_virtual_pet_selenium.py"],
            "性能测试": ["test_performance.py"],
            "集成测试": ["test_integration.py"],
        }

        coverage_report = {}

        for module, files in modules.items():
            module_tests = [
                tc for tc in self.test_cases if any(tc["file"] == f for f in files)
            ]

            p0_count = len([t for t in module_tests if t["priority"] == "Critical"])
            p1_count = len([t for t in module_tests if t["priority"] == "High"])
            p2_count = len([t for t in module_tests if t["priority"] == "Medium"])
            p3_count = len([t for t in module_tests if t["priority"] == "Low"])

            coverage_report[module] = {
                "total": len(module_tests),
                "p0_critical": p0_count,
                "p1_high": p1_count,
                "p2_medium": p2_count,
                "p3_low": p3_count,
                "files": files,
            }

        self.coverage_stats = coverage_report
        return coverage_report

    def generate_text_report(self, output_file=None):
        """生成文本格式的报告"""
        if not self.test_cases:
            self.extract_test_cases()

        if not self.coverage_stats:
            self.analyze_module_coverage()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_file is None:
            output_file = self.test_dir / "reports" / f"test_coverage_{timestamp}.txt"

        # 确保 reports 目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("测试用例覆盖分析报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试目录：{self.test_dir.absolute()}\n\n")

            # 总体统计
            f.write("-" * 80 + "\n")
            f.write("一、总体统计\n")
            f.write("-" * 80 + "\n")
            f.write(f"测试文件数量：{len(self.test_files)}\n")
            f.write(f"测试用例总数：{len(self.test_cases)}\n\n")

            # 按优先级统计
            priority_counts = {}
            for tc in self.test_cases:
                priority = tc["priority"]
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            f.write("按优先级分布:\n")
            for priority in ["Critical", "High", "Medium", "Low"]:
                count = priority_counts.get(priority, 0)
                percentage = (
                    (count / len(self.test_cases) * 100) if self.test_cases else 0
                )
                f.write(f"  {priority}: {count} ({percentage:.1f}%)\n")

            f.write("\n")

            # 模块覆盖详情
            f.write("-" * 80 + "\n")
            f.write("二、模块覆盖详情\n")
            f.write("-" * 80 + "\n\n")

            total_coverage = 0
            for module, stats in self.coverage_stats.items():
                f.write(f"【{module}】\n")
                f.write(f"  测试文件：{', '.join(stats['files'])}\n")
                f.write(f"  测试用例：{stats['total']} 个\n")
                f.write(f"    - P0/Critical: {stats['p0_critical']} 个\n")
                f.write(f"    - P1/High: {stats['p1_high']} 个\n")
                f.write(f"    - P2/Medium: {stats['p2_medium']} 个\n")
                f.write(f"    - P3/Low: {stats['p3_low']} 个\n")

                # 计算覆盖率（基于优先级权重）
                weighted_score = (
                    stats["p0_critical"] * 1.0
                    + stats["p1_high"] * 0.8
                    + stats["p2_medium"] * 0.6
                    + stats["p3_low"] * 0.4
                )
                max_score = stats["total"]  # 假设每个用例都是 Critical
                coverage_rate = (
                    (weighted_score / max_score * 100) if max_score > 0 else 0
                )

                f.write(f"  加权覆盖率：{coverage_rate:.1f}%\n\n")
                total_coverage += coverage_rate

            avg_coverage = (
                total_coverage / len(self.coverage_stats) if self.coverage_stats else 0
            )
            f.write("-" * 80 + "\n")
            f.write(f"平均加权覆盖率：{avg_coverage:.1f}%\n")
            f.write("-" * 80 + "\n\n")

            # 测试用例清单
            f.write("-" * 80 + "\n")
            f.write("三、测试用例详细清单\n")
            f.write("-" * 80 + "\n\n")

            current_file = None
            for tc in sorted(self.test_cases, key=lambda x: (x["file"], x["case_id"])):
                if tc["file"] != current_file:
                    current_file = tc["file"]
                    f.write(f"\n📁 {current_file}:\n")
                    f.write("-" * 40 + "\n")

                icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
                f.write(
                    f"  {icon.get(tc['priority'], '⚪')} {tc['case_id']} - {tc['function']} [{tc['priority']}]\n"
                )

            f.write("\n" + "=" * 80 + "\n")
            f.write("报告结束\n")
            f.write("=" * 80 + "\n")

        print(f"报告已生成：{output_file}")
        return output_file

    def generate_json_report(self, output_file=None):
        """生成 JSON 格式的报告"""
        if not self.test_cases:
            self.extract_test_cases()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_file is None:
            output_file = self.test_dir / "reports" / f"test_coverage_{timestamp}.json"

        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_files": len(self.test_files),
                "total_cases": len(self.test_cases),
                "by_priority": {},
            },
            "modules": self.coverage_stats,
            "test_cases": self.test_cases,
        }

        # 按优先级统计
        for priority in ["Critical", "High", "Medium", "Low"]:
            count = len([tc for tc in self.test_cases if tc["priority"] == priority])
            report_data["summary"]["by_priority"][priority] = count

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"JSON 报告已生成：{output_file}")
        return output_file


def main():
    """主函数"""
    print("=" * 60)
    print("测试覆盖率分析工具")
    print("=" * 60)
    print()

    analyzer = TestCoverageAnalyzer()
    analyzer.find_test_files()
    analyzer.extract_test_cases()
    analyzer.analyze_module_coverage()

    # 生成文本报告
    txt_report = analyzer.generate_text_report()

    # 生成 JSON 报告
    json_report = analyzer.generate_json_report()

    print()
    print("=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"文本报告：{txt_report}")
    print(f"JSON 报告：{json_report}")
    print()

    # 打印简要统计
    print("📊 覆盖率统计:")
    for module, stats in analyzer.coverage_stats.items():
        if stats["total"] > 0:
            print(f"  ✓ {module}: {stats['total']} 个测试用例")

    return analyzer


if __name__ == "__main__":
    main()
