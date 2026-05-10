# 小工具使用说明

本文件夹包含项目中使用的各种实用工具。

## 📋 工具列表

### 1. Bug追踪器 (bug_tracker.py)

**功能**：记录和管理项目Bug，跟踪修复进度

**使用方法**：
```bash
python scripts/tools/bug_tracker.py
```

**交互菜单**：
1. 添加Bug - 记录新Bug信息
2. 查看Bug列表 - 浏览所有Bug
3. 更新Bug状态 - 修改Bug状态（待修复/修复中/已修复等）
4. 查看Bug详情 - 查看详细信息和评论
5. 查看统计报告 - 生成Bug统计报告
6. 导出CSV报告 - 导出Excel可读格式
7. 退出

**数据存储**：
- Bug数据保存在 `bug_tracker.json`
- 导出报告保存在 `reports/` 目录

**示例**：
```python
from scripts.tools.bug_tracker import BugTracker

tracker = BugTracker()

# 添加Bug
tracker.add_bug(
    title="图表下载错误",
    description="所有图表下载的都是品种数据",
    category=BugTracker.CATEGORY_DATA,
    priority=BugTracker.PRIORITY_HIGH,
    module="图表模块",
    version="v4.8.0"
)

# 更新状态
tracker.update_bug_status(1, BugTracker.STATUS_FIXED, "已修复")

# 查看统计
tracker.print_report()

# 导出报告
tracker.export_to_csv("reports/bug_report.csv")
```

---

## 📁 文件结构

```
scripts/tools/
├── bug_tracker.py          # Bug追踪工具
└── bug_tracker.json        # Bug数据库（自动生成）
```

---

## 🔧 开发规范

### 添加工具时请遵守：

1. **位置**：所有小工具统一放在 `scripts/tools/` 目录
2. **命名**：使用下划线命名法，如 `bug_tracker.py`
3. **文档**：每个工具需要有说明文档或使用示例
4. **依赖**：尽量减少外部依赖，优先使用标准库
5. **数据文件**：工具生成的数据文件也放在tools目录

### 文档规范：

1. **工具文档** → `docs/06-工具文档/`
2. **版本记录** → `docs/05-版本记录/`
3. **产品文档** → `docs/01-产品文档/`
4. **技术文档** → `docs/02-技术文档/`
5. **测试文档** → `docs/03-测试文档/`
6. **部署运维** → `docs/04-部署运维/`
7. **培训资料** → `docs/99-培训资料/`

---

## ⚠️ 注意事项

- ❌ 不要在根目录创建新文件（除README、配置文件外）
- ❌ 不要随意创建.md文档（放到对应文档目录）
- ✅ 工具统一放在 `scripts/tools/`
- ✅ 文档统一放在 `docs/` 对应子目录
- ✅ 遵循项目管理规则，保持项目结构清晰

---

## 📊 当前工具统计

| 工具 | 位置 | 状态 |
|------|------|------|
| Bug追踪器 | scripts/tools/bug_tracker.py | ✅ 可用 |

---

*最后更新：2026-05-10*
