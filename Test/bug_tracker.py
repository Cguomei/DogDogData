"""
Bug 记录和跟踪模块
用于记录测试过程中发现的 bug，并生成 bug 报告
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Bug:
    """Bug 数据类"""
    id: str
    title: str
    description: str
    severity: str  # Critical, Major, Minor, Trivial
    priority: str  # High, Medium, Low
    module: str  # 所属模块
    steps_to_reproduce: List[str]
    expected_result: str
    actual_result: str
    created_at: str
    status: str = "Open"  # Open, In Progress, Fixed, Closed, Won't Fix
    assigned_to: str = ""
    notes: str = ""


class BugTracker:
    """Bug 跟踪器"""
    
    def __init__(self, report_dir: str = "Test/reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.bugs: List[Bug] = []
        self.load_bugs()
    
    def load_bugs(self):
        """从文件加载已有的 bugs"""
        bug_file = self.report_dir / "bugs.json"
        if bug_file.exists():
            try:
                with open(bug_file, 'r', encoding='utf-8') as f:
                    bugs_data = json.load(f)
                    self.bugs = [Bug(**bug) for bug in bugs_data]
            except Exception as e:
                print(f"加载 bug 文件失败：{e}")
    
    def save_bugs(self):
        """保存 bugs 到文件"""
        bug_file = self.report_dir / "bugs.json"
        with open(bug_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(bug) for bug in self.bugs], f, ensure_ascii=False, indent=2)
    
    def add_bug(
        self,
        title: str,
        description: str,
        severity: str = "Major",
        priority: str = "Medium",
        module: str = "General",
        steps_to_reproduce: List[str] = None,
        expected_result: str = "",
        actual_result: str = "",
        assigned_to: str = ""
    ) -> Bug:
        """添加一个新的 bug"""
        bug_id = f"BUG-{len(self.bugs) + 1:04d}"
        bug = Bug(
            id=bug_id,
            title=title,
            description=description,
            severity=severity,
            priority=priority,
            module=module,
            steps_to_reproduce=steps_to_reproduce or [],
            expected_result=expected_result,
            actual_result=actual_result,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            assigned_to=assigned_to
        )
        self.bugs.append(bug)
        self.save_bugs()
        return bug
    
    def update_bug_status(self, bug_id: str, status: str, notes: str = ""):
        """更新 bug 状态"""
        for bug in self.bugs:
            if bug.id == bug_id:
                bug.status = status
                if notes:
                    bug.notes += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notes}"
                self.save_bugs()
                return True
        return False
    
    def get_bugs_by_status(self, status: str) -> List[Bug]:
        """按状态获取 bugs"""
        return [bug for bug in self.bugs if bug.status == status]
    
    def get_bugs_by_severity(self, severity: str) -> List[Bug]:
        """按严重程度获取 bugs"""
        return [bug for bug in self.bugs if bug.severity == severity]
    
    def generate_report(self) -> str:
        """生成 bug 统计报告"""
        report_lines = [
            "=" * 70,
            "BUG 跟踪报告",
            "=" * 70,
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"总 Bug 数：{len(self.bugs)}",
            "",
            "按状态统计:",
        ]
        
        # 按状态统计
        status_count = {}
        for bug in self.bugs:
            status_count[bug.status] = status_count.get(bug.status, 0) + 1
        
        for status, count in status_count.items():
            report_lines.append(f"  {status}: {count}")
        
        report_lines.extend([
            "",
            "按严重程度统计:",
        ])
        
        # 按严重程度统计
        severity_count = {}
        for bug in self.bugs:
            severity_count[bug.severity] = severity_count.get(bug.severity, 0) + 1
        
        for severity, count in severity_count.items():
            report_lines.append(f"  {severity}: {count}")
        
        report_lines.extend([
            "",
            "按模块统计:",
        ])
        
        # 按模块统计
        module_count = {}
        for bug in self.bugs:
            module_count[bug.module] = module_count.get(bug.module, 0) + 1
        
        for module, count in module_count.items():
            report_lines.append(f"  {module}: {count}")
        
        report_lines.extend([
            "",
            "=" * 70,
            "未解决的 Bug 列表:",
            "=" * 70,
        ])
        
        # 列出所有未解决的 bug
        open_bugs = self.get_bugs_by_status("Open")
        for bug in open_bugs:
            report_lines.extend([
                f"\n[{bug.id}] {bug.title}",
                f"  严重程度：{bug.severity}",
                f"  优先级：{bug.priority}",
                f"  模块：{bug.module}",
                f"  创建时间：{bug.created_at}",
                f"  描述：{bug.description}",
            ])
        
        report_text = "\n".join(report_lines)
        
        # 保存到文件
        report_file = self.report_dir / "bug_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text


# 全局实例
bug_tracker = BugTracker()


def report_bug(
    title: str,
    description: str,
    severity: str = "Major",
    priority: str = "Medium",
    module: str = "General",
    steps_to_reproduce: List[str] = None,
    expected_result: str = "",
    actual_result: str = ""
):
    """便捷函数：报告一个 bug"""
    bug = bug_tracker.add_bug(
        title=title,
        description=description,
        severity=severity,
        priority=priority,
        module=module,
        steps_to_reproduce=steps_to_reproduce,
        expected_result=expected_result,
        actual_result=actual_result
    )
    print(f"\n🐛 发现 Bug: {bug.id} - {bug.title}")
    return bug
