"""
最简测试执行器 - 不依赖任何外部框架
直接运行测试方法并生成报告
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_simple_tests():
    """运行简单的测试"""
    print("=" * 80)
    print("🧪 狗狗数据分析系统 - 简单测试")
    print("=" * 80)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # 测试 1: 导入 app 模块
    print("[1/5] 测试导入 app 模块...", end=" ")
    try:
        from app import app

        print("✅ PASS")
        results.append({"test": "导入 app 模块", "status": "PASS", "error": None})
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append({"test": "导入 app 模块", "status": "FAIL", "error": str(e)})

    # 测试 2: 导入 models
    print("[2/5] 测试导入 models...", end=" ")
    try:
        from models import User, DogBreed

        print("✅ PASS")
        results.append({"test": "导入 models", "status": "PASS", "error": None})
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append({"test": "导入 models", "status": "FAIL", "error": str(e)})

    # 测试 3: 导入 conftest fixtures
    print("[3/5] 测试导入 conftest...", end=" ")
    try:
        from Test import conftest

        print("✅ PASS")
        results.append({"test": "导入 conftest", "status": "PASS", "error": None})
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append({"test": "导入 conftest", "status": "FAIL", "error": str(e)})

    # 测试 4: 检查数据库配置
    print("[4/5] 测试数据库配置...", end=" ")
    try:
        from dotenv import load_dotenv

        load_dotenv()
        db_user = os.getenv("DB_USER", "doguser")
        db_password = os.getenv("DB_PASSWORD", "123456")
        if db_user and db_password:
            print("✅ PASS")
            results.append({"test": "数据库配置", "status": "PASS", "error": None})
        else:
            print("❌ FAIL: 缺少数据库配置")
            results.append(
                {"test": "数据库配置", "status": "FAIL", "error": "配置为空"}
            )
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append({"test": "数据库配置", "status": "FAIL", "error": str(e)})

    # 测试 5: 检查测试文件存在性
    print("[5/5] 检查测试文件...", end=" ")
    test_files = ["Test/test_auth.py", "Test/test_breed.py", "Test/test_framework.py"]
    all_exist = True
    missing = []
    for f in test_files:
        if not Path(f).exists():
            all_exist = False
            missing.append(f)

    if all_exist:
        print("✅ PASS")
        results.append({"test": "测试文件检查", "status": "PASS", "error": None})
    else:
        print(f"❌ FAIL: 缺少 {missing}")
        results.append(
            {"test": "测试文件检查", "status": "FAIL", "error": f"缺少：{missing}"}
        )

    # 统计结果
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    print()
    print("=" * 80)
    print(f"总计：{total} | ✅ 通过：{passed} | ❌ 失败：{failed}")
    print("=" * 80)

    # 保存报告
    save_report(results)

    return passed == total


def save_report(results):
    """保存测试报告"""
    report_dir = Path("Test/reports")
    report_dir.mkdir(exist_ok=True)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    report = {
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/len(results)*100):.1f}%" if results else "0%",
        },
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }

    # JSON 报告
    json_file = (
        report_dir / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON 报告已保存：{json_file}")

    # HTML 报告
    html_file = (
        report_dir / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    )
    generate_html(report, html_file)
    print(f"📄 HTML 报告已保存：{html_file}")


def generate_html(report, filename):
    """生成 HTML 报告"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>测试报告 - {report['timestamp'][:10]}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .summary-item {{ text-align: center; }}
        .summary-value {{ font-size: 2em; font-weight: bold; }}
        .summary-label {{ font-size: 0.9em; opacity: 0.9; }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e9ecef; }}
        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .icon {{ font-size: 1.2em; margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 测试报告</h1>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value">{report['summary']['total']}</div>
                <div class="summary-label">总测试数</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" style="color: #28a745;">{report['summary']['passed']}</div>
                <div class="summary-label">✅ 通过</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" style="color: #dc3545;">{report['summary']['failed']}</div>
                <div class="summary-label">❌ 失败</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{report['summary']['pass_rate']}</div>
                <div class="summary-label">通过率</div>
            </div>
        </div>
        
        <h2>测试结果详情</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>测试项目</th>
                    <th>状态</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
"""

    for i, result in enumerate(report["results"], 1):
        status_class = "status-pass" if result["status"] == "PASS" else "status-fail"
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        error_text = result.get("error", "") or "-"

        html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{result['test']}</td>
                    <td class="{status_class}"><span class="icon">{status_icon}</span> {result['status']}</td>
                    <td>{error_text}</td>
                </tr>
"""

    html += (
        """
            </tbody>
        </table>
        
        <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
            报告生成时间："""
        + report["timestamp"]
        + """
        </p>
    </div>
</body>
</html>
"""
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
