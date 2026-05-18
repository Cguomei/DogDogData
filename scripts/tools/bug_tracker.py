#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bug追踪与进度管理工具
功能：
- 记录Bug信息
- 跟踪修复进度
- 生成Bug报告
- 支持CSV导出
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional


class BugTracker:
    """Bug追踪器"""

    # Bug状态
    STATUS_NEW = "待修复"
    STATUS_IN_PROGRESS = "修复中"
    STATUS_FIXED = "已修复"
    STATUS_CLOSED = "已关闭"
    STATUS_REOPENED = "重新打开"
    STATUS_WONT_FIX = "无需修复"

    # Bug优先级
    PRIORITY_CRITICAL = "严重"
    PRIORITY_HIGH = "高"
    PRIORITY_MEDIUM = "中"
    PRIORITY_LOW = "低"

    # Bug分类
    CATEGORY_UI = "界面问题"
    CATEGORY_API = "接口问题"
    CATEGORY_DATA = "数据问题"
    CATEGORY_PERFORMANCE = "性能问题"
    CATEGORY_SECURITY = "安全问题"
    CATEGORY_FEATURE = "功能缺失"

    def __init__(self, db_file: str = "bug_tracker.json"):
        """
        初始化Bug追踪器

        Args:
            db_file: Bug数据库文件路径
        """
        self.db_file = db_file
        self.bugs: List[Dict] = []
        self._load_data()

    def _load_data(self):
        """从文件加载Bug数据"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.bugs = json.load(f)
                print(f"✅ 已加载 {len(self.bugs)} 条Bug记录")
            except Exception as e:
                print(f"⚠️ 加载Bug数据失败: {e}")
                self.bugs = []
        else:
            self.bugs = []
            self._save_data()

    def _save_data(self):
        """保存Bug数据到文件"""
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.bugs, f, ensure_ascii=False, indent=2)

    def add_bug(
        self,
        title: str,
        description: str,
        category: str,
        priority: str = PRIORITY_MEDIUM,
        reporter: str = "系统",
        module: str = "",
        version: str = "",
        assignee: str = "",
        steps_to_reproduce: str = "",
        expected_result: str = "",
        actual_result: str = "",
    ) -> int:
        """
        添加新Bug

        Args:
            title: Bug标题
            description: Bug描述
            category: Bug分类
            priority: Bug优先级
            reporter: 报告人
            module: 所属模块
            version: 发现版本
            assignee: 指派人
            steps_to_reproduce: 复现步骤
            expected_result: 预期结果
            actual_result: 实际结果

        Returns:
            Bug ID
        """
        bug_id = len(self.bugs) + 1

        bug = {
            "id": bug_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": self.STATUS_NEW,
            "reporter": reporter,
            "module": module,
            "version": version,
            "assignee": assignee,
            "steps_to_reproduce": steps_to_reproduce,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fixed_at": None,
            "closed_at": None,
            "comments": [],
        }

        self.bugs.append(bug)
        self._save_data()

        print(f"✅ Bug #{bug_id} 已创建: {title}")
        return bug_id

    def update_bug_status(self, bug_id: int, status: str, comment: str = "") -> bool:
        """
        更新Bug状态

        Args:
            bug_id: Bug ID
            status: 新状态
            comment: 备注

        Returns:
            是否成功
        """
        bug = self._find_bug(bug_id)
        if not bug:
            print(f"❌ 未找到Bug #{bug_id}")
            return False

        old_status = bug["status"]
        bug["status"] = status
        bug["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 记录状态变更时间
        if status == self.STATUS_FIXED:
            bug["fixed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif status == self.STATUS_CLOSED:
            bug["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 添加备注
        if comment:
            bug["comments"].append(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": f"状态变更: {old_status} → {status} | {comment}",
                }
            )

        self._save_data()
        print(f"✅ Bug #{bug_id} 状态已更新: {old_status} → {status}")
        return True

    def update_bug_info(self, bug_id: int, **kwargs) -> bool:
        """
        更新Bug信息

        Args:
            bug_id: Bug ID
            **kwargs: 要更新的字段

        Returns:
            是否成功
        """
        bug = self._find_bug(bug_id)
        if not bug:
            print(f"❌ 未找到Bug #{bug_id}")
            return False

        for key, value in kwargs.items():
            if key in bug and key not in ["id", "created_at"]:
                bug[key] = value

        bug["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_data()

        print(f"✅ Bug #{bug_id} 信息已更新")
        return True

    def add_comment(self, bug_id: int, comment: str, author: str = "系统") -> bool:
        """
        添加评论

        Args:
            bug_id: Bug ID
            comment: 评论内容
            author: 评论人

        Returns:
            是否成功
        """
        bug = self._find_bug(bug_id)
        if not bug:
            print(f"❌ 未找到Bug #{bug_id}")
            return False

        bug["comments"].append(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "author": author,
                "content": comment,
            }
        )

        bug["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_data()

        print(f"✅ Bug #{bug_id} 已添加评论")
        return True

    def get_bug(self, bug_id: int) -> Optional[Dict]:
        """获取Bug详情"""
        return self._find_bug(bug_id)

    def list_bugs(
        self,
        status: str = None,
        priority: str = None,
        category: str = None,
        module: str = None,
    ) -> List[Dict]:
        """
        列出Bug（支持筛选）

        Args:
            status: 状态筛选
            priority: 优先级筛选
            category: 分类筛选
            module: 模块筛选

        Returns:
            Bug列表
        """
        filtered = self.bugs

        if status:
            filtered = [b for b in filtered if b["status"] == status]
        if priority:
            filtered = [b for b in filtered if b["priority"] == priority]
        if category:
            filtered = [b for b in filtered if b["category"] == category]
        if module:
            filtered = [b for b in filtered if b["module"] == module]

        return filtered

    def get_statistics(self) -> Dict:
        """获取Bug统计信息"""
        stats = {
            "total": len(self.bugs),
            "by_status": {},
            "by_priority": {},
            "by_category": {},
            "open_count": 0,
            "fixed_count": 0,
            "closed_count": 0,
        }

        for bug in self.bugs:
            # 按状态统计
            status = bug["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # 按优先级统计
            priority = bug["priority"]
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

            # 按分类统计
            category = bug["category"]
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            # 统计修复情况
            if bug["status"] in [
                self.STATUS_NEW,
                self.STATUS_IN_PROGRESS,
                self.STATUS_REOPENED,
            ]:
                stats["open_count"] += 1
            elif bug["status"] == self.STATUS_FIXED:
                stats["fixed_count"] += 1
            elif bug["status"] == self.STATUS_CLOSED:
                stats["closed_count"] += 1

        return stats

    def export_to_csv(self, output_file: str = "bug_report.csv") -> str:
        """
        导出Bug报告到CSV

        Args:
            output_file: 输出文件路径

        Returns:
            输出文件路径
        """
        if not self.bugs:
            print("⚠️ 没有Bug数据可导出")
            return ""

        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
            fieldnames = [
                "ID",
                "标题",
                "状态",
                "优先级",
                "分类",
                "模块",
                "版本",
                "报告人",
                "指派人",
                "创建时间",
                "更新时间",
                "修复时间",
                "关闭时间",
                "描述",
                "复现步骤",
                "预期结果",
                "实际结果",
                "备注数",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for bug in self.bugs:
                writer.writerow(
                    {
                        "ID": bug["id"],
                        "标题": bug["title"],
                        "状态": bug["status"],
                        "优先级": bug["priority"],
                        "分类": bug["category"],
                        "模块": bug["module"],
                        "版本": bug["version"],
                        "报告人": bug["reporter"],
                        "指派人": bug["assignee"],
                        "创建时间": bug["created_at"],
                        "更新时间": bug["updated_at"],
                        "修复时间": bug.get("fixed_at", ""),
                        "关闭时间": bug.get("closed_at", ""),
                        "描述": bug["description"],
                        "复现步骤": bug.get("steps_to_reproduce", ""),
                        "预期结果": bug.get("expected_result", ""),
                        "实际结果": bug.get("actual_result", ""),
                        "备注数": len(bug["comments"]),
                    }
                )

        print(f"✅ 已导出 {len(self.bugs)} 条Bug到 {output_file}")
        return output_file

    def print_report(self):
        """打印Bug报告"""
        if not self.bugs:
            print("\n📊 Bug报告")
            print("=" * 60)
            print("暂无Bug记录")
            return

        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("📊 Bug追踪报告")
        print("=" * 60)
        print(f"总Bug数: {stats['total']}")
        print(f"待修复: {stats['open_count']}")
        print(f"已修复: {stats['fixed_count']}")
        print(f"已关闭: {stats['closed_count']}")

        if stats["total"] > 0:
            fix_rate = (
                (stats["fixed_count"] + stats["closed_count"]) / stats["total"] * 100
            )
            print(f"修复率: {fix_rate:.1f}%")

        print("\n按状态分布:")
        for status, count in stats["by_status"].items():
            print(f"  {status}: {count}")

        print("\n按优先级分布:")
        for priority, count in stats["by_priority"].items():
            print(f"  {priority}: {count}")

        print("\n按分类分布:")
        for category, count in stats["by_category"].items():
            print(f"  {category}: {count}")

        print("=" * 60)

    def _find_bug(self, bug_id: int) -> Optional[Dict]:
        """查找Bug"""
        for bug in self.bugs:
            if bug["id"] == bug_id:
                return bug
        return None


def main():
    """命令行交互"""
    tracker = BugTracker()

    print("\n" + "=" * 60)
    print("🐛 Bug追踪工具")
    print("=" * 60)
    print("1. 添加Bug")
    print("2. 查看Bug列表")
    print("3. 更新Bug状态")
    print("4. 查看Bug详情")
    print("5. 查看统计报告")
    print("6. 导出CSV报告")
    print("7. 退出")
    print("=" * 60)

    while True:
        choice = input("\n请选择操作 (1-7): ").strip()

        if choice == "1":
            print("\n--- 添加新Bug ---")
            title = input("标题: ").strip()
            if not title:
                continue

            print("\n分类:")
            categories = [
                BugTracker.CATEGORY_UI,
                BugTracker.CATEGORY_API,
                BugTracker.CATEGORY_DATA,
                BugTracker.CATEGORY_PERFORMANCE,
                BugTracker.CATEGORY_SECURITY,
                BugTracker.CATEGORY_FEATURE,
            ]
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            cat_choice = input("选择分类 (1-6, 默认3): ").strip()
            category = (
                categories[int(cat_choice) - 1]
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= 6
                else BugTracker.CATEGORY_DATA
            )

            print("\n优先级:")
            priorities = [
                BugTracker.PRIORITY_CRITICAL,
                BugTracker.PRIORITY_HIGH,
                BugTracker.PRIORITY_MEDIUM,
                BugTracker.PRIORITY_LOW,
            ]
            for i, pri in enumerate(priorities, 1):
                print(f"  {i}. {pri}")
            pri_choice = input("选择优先级 (1-4, 默认3): ").strip()
            priority = (
                priorities[int(pri_choice) - 1]
                if pri_choice.isdigit() and 1 <= int(pri_choice) <= 4
                else BugTracker.PRIORITY_MEDIUM
            )

            description = input("描述: ").strip()
            module = input("所属模块 (可选): ").strip()
            version = input("发现版本 (可选): ").strip()
            steps = input("复现步骤 (可选): ").strip()

            bug_id = tracker.add_bug(
                title=title,
                description=description,
                category=category,
                priority=priority,
                module=module,
                version=version,
                steps_to_reproduce=steps,
            )

            print(f"\n✅ Bug #{bug_id} 创建成功！")

        elif choice == "2":
            print("\n--- Bug列表 ---")
            bugs = tracker.bugs

            if not bugs:
                print("暂无Bug记录")
                continue

            print(f"{'ID':<6}{'状态':<10}{'优先级':<8}{'标题':<40}{'模块':<15}")
            print("-" * 80)
            for bug in bugs[-20:]:  # 显示最近20条
                print(
                    f"#{bug['id']:<5}{bug['status']:<12}{bug['priority']:<10}{bug['title'][:40]:<42}{bug.get('module', ''):<15}"
                )

        elif choice == "3":
            bug_id = input("\n输入Bug ID: ").strip()
            if not bug_id.isdigit():
                continue

            bug_id = int(bug_id)
            bug = tracker.get_bug(bug_id)
            if not bug:
                print(f"❌ 未找到Bug #{bug_id}")
                continue

            print(f"\n当前状态: {bug['status']}")
            print("可选状态:")
            statuses = [
                BugTracker.STATUS_NEW,
                BugTracker.STATUS_IN_PROGRESS,
                BugTracker.STATUS_FIXED,
                BugTracker.STATUS_CLOSED,
                BugTracker.STATUS_REOPENED,
                BugTracker.STATUS_WONT_FIX,
            ]
            for i, status in enumerate(statuses, 1):
                print(f"  {i}. {status}")

            status_choice = input("选择新状态 (1-6): ").strip()
            if status_choice.isdigit() and 1 <= int(status_choice) <= 6:
                new_status = statuses[int(status_choice) - 1]
                comment = input("备注 (可选): ").strip()
                tracker.update_bug_status(bug_id, new_status, comment)

        elif choice == "4":
            bug_id = input("\n输入Bug ID: ").strip()
            if not bug_id.isdigit():
                continue

            bug_id = int(bug_id)
            bug = tracker.get_bug(bug_id)
            if not bug:
                print(f"❌ 未找到Bug #{bug_id}")
                continue

            print("\n" + "=" * 60)
            print(f"Bug #{bug['id']}: {bug['title']}")
            print("=" * 60)
            print(f"状态: {bug['status']}")
            print(f"优先级: {bug['priority']}")
            print(f"分类: {bug['category']}")
            print(f"模块: {bug.get('module', '')}")
            print(f"版本: {bug.get('version', '')}")
            print(f"报告人: {bug['reporter']}")
            print(f"指派人: {bug.get('assignee', '')}")
            print(f"\n描述:\n{bug['description']}")
            print(f"\n复现步骤:\n{bug.get('steps_to_reproduce', '')}")
            print(f"\n预期结果:\n{bug.get('expected_result', '')}")
            print(f"\n实际结果:\n{bug.get('actual_result', '')}")
            print(f"\n创建时间: {bug['created_at']}")
            print(f"更新时间: {bug['updated_at']}")

            if bug.get("comments"):
                print(f"\n评论 ({len(bug['comments'])}条):")
                for comment in bug["comments"]:
                    print(f"  [{comment['time']}] {comment['content']}")

            print("=" * 60)

        elif choice == "5":
            tracker.print_report()

        elif choice == "6":
            output_file = input("\n输出文件名 (默认: bug_report.csv): ").strip()
            if not output_file:
                output_file = "bug_report.csv"
            tracker.export_to_csv(output_file)

        elif choice == "7":
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
