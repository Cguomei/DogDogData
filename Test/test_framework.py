"""
专业测试执行框架
包含完整的测试用例管理、缺陷跟踪和报告生成
"""

import pytest
import json
import time
from datetime import datetime
from pathlib import Path


class TestResult:
    """测试结果记录"""

    def __init__(self, test_id, test_name, module, priority):
        self.test_id = test_id
        self.test_name = test_name
        self.module = module
        self.priority = priority
        self.status = "PENDING"  # PENDING, PASS, FAIL, SKIP
        self.execution_time = 0
        self.error_message = None
        self.actual_result = None
        self.expected_result = None
        self.steps_executed = []
        self.screenshot_path = None
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "module": self.module,
            "priority": self.priority,
            "status": self.status,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "actual_result": self.actual_result,
            "expected_result": self.expected_result,
            "timestamp": self.timestamp.isoformat(),
        }


class TestExecutionManager:
    """测试执行管理器"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        # 使用绝对路径，避免从不同目录运行时出错
        self.report_dir = Path(__file__).parent / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def start_test_run(self):
        self.start_time = datetime.now()
        print(f"\n{'='*80}")
        print(f"测试执行开始：{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

    def end_test_run(self):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time

        print(f"\n{'='*80}")
        print(f"测试执行完成：{self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时：{duration.total_seconds():.2f}秒")
        print(f"{'='*80}\n")

    def record_result(self, result: TestResult):
        self.results.append(result)

        # 打印结果
        status_icon = (
            "✅"
            if result.status == "PASS"
            else "❌" if result.status == "FAIL" else "⏭️"
        )
        print(
            f"{status_icon} [{result.test_id}] {result.test_name} - {result.status} ({result.execution_time:.3f}s)"
        )

        if result.status == "FAIL" and result.error_message:
            print(f"   错误：{result.error_message}")

    def generate_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        pending = sum(1 for r in self.results if r.status == "PENDING")

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pending": pending,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "duration": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time
                else 0
            ),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }

        return summary

    def save_report(self):
        """保存测试报告"""
        summary = self.generate_summary()

        report = {
            "summary": summary,
            "results": [r.to_dict() for r in self.results],
            "generated_at": datetime.now().isoformat(),
        }

        # 保存 JSON 报告
        report_file = (
            self.report_dir
            / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 测试报告已保存：{report_file}")

        # 打印摘要
        print(f"\n{'='*80}")
        print("测试执行摘要")
        print(f"{'='*80}")
        print(f"总测试数：{summary['total']}")
        print(f"✅ 通过：{summary['passed']}")
        print(f"❌ 失败：{summary['failed']}")
        print(f"⏭️ 跳过：{summary['skipped']}")
        print(f"⏳ 待执行：{summary['pending']}")
        print(f"通过率：{summary['pass_rate']}")
        print(f"耗时：{summary['duration']:.2f}秒")
        print(f"{'='*80}\n")

        return report_file


# 全局测试管理器实例
test_manager = TestExecutionManager()


# Pytest hooks
def pytest_configure(config):
    """pytest 配置完成后调用"""
    test_manager.start_test_run()


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时调用"""
    test_manager.end_test_run()
    test_manager.save_report()


@pytest.fixture(scope="function")
def test_context(request):
    """提供测试上下文"""
    # 获取测试用例元数据
    test_id = getattr(request.function, "__test_id__", "UNKNOWN")
    priority = getattr(request.function, "__priority__", "Medium")
    module = getattr(request.function, "__module__", "Unknown")

    result = TestResult(
        test_id=test_id,
        test_name=request.function.__name__,
        module=module,
        priority=priority,
    )

    start_time = time.time()

    yield result

    end_time = time.time()
    result.execution_time = end_time - start_time

    # 记录结果
    test_manager.record_result(result)


def test_case(test_id, priority="Medium", expected=None):
    """
    测试用例装饰器
    用法:
        @test_case('TC-AUTH-001', priority='High', expected='登录成功')
        def test_login_success(...):
            ...
    """

    def decorator(func):
        func.__test_id = test_id
        func.__priority = priority
        func.__expected = expected
        # 不再设置 __test__ = False，因为这是用于测试方法的装饰器
        return func

    return decorator
