# 🧪 测试快速参考卡

## 🚀 一键运行测试

```bash
# ⭐ 推荐：全面测试（包含报告）
python Test/run_full_tests.py

# 包含UI测试
python Test/run_full_tests.py --ui

# 包含E2E测试  
python Test/run_full_tests.py --e2e

# 生成覆盖率报告
python Test/run_full_tests.py --coverage

# 全部测试
python Test/run_full_tests.py --all
```

## 📊 查看测试报告

### 可视化仪表盘（推荐）⭐
```bash
start Test\reports\test_dashboard_20260510.html
```

### HTML详细报告
```bash
start Test\reports\api_test_report_*.html
```

### Markdown报告
```bash
# 在VS Code或Markdown编辑器中打开
Test\reports\全面测试报告_20260510.md
Test\reports\测试完成总结.md
```

## 🔍 常用pytest命令

```bash
# 运行所有API测试
pytest Test/api_tests/ -v

# 运行特定模块
pytest Test/api_tests/test_ai_assistant.py -v

# 只运行失败的测试
pytest --lf

# 显示详细错误信息
pytest --tb=long

# 进入调试模式
pytest --pdb

# 并行执行（需要安装pytest-xdist）
pytest -n auto

# 生成HTML报告
pytest --html=report.html --self-contained-html

# 查看覆盖率
pytest --cov=routes --cov-report=html
```

## 📁 重要文件位置

```
Test/
├── run_full_tests.py          # ⭐ 全面测试脚本
├── reports/
│   ├── test_dashboard_*.html  # ⭐ 可视化仪表盘
│   ├── api_test_report_*.html # HTML测试报告
│   ├── 全面测试报告_*.md      # Markdown报告
│   └── 测试完成总结.md         # 总结文档
├── api_tests/                  # API测试
├── ui_tests/                   # UI测试
└── e2e_tests/                  # E2E测试
```

## 🎯 测试模块速查

| 模块 | 命令 | 测试数 |
|------|------|--------|
| AI助手 | `pytest Test/api_tests/test_ai_assistant.py` | 34 |
| 用户反馈 | `pytest Test/api_tests/test_feedback.py` | 17 |
| 数据分析 | `pytest Test/api_tests/test_data_analysis_api.py` | 18 |
| 国际化 | `pytest Test/api_tests/test_internationalization.py` | 15 |
| 品种管理 | `pytest Test/api_tests/test_breeds_api.py` | 14 |
| 系统监控 | `pytest Test/api_tests/test_monitoring.py` | 13 |

## 💡 故障排查

### 测试失败？
```bash
# 查看详细错误
pytest test_file.py -v --tb=long

# 只运行失败的测试
pytest --lf

# 跳过慢速测试
pytest -m "not slow"
```

### 数据库错误？
```bash
# 重新初始化测试数据库
python Test/init_test_db.py

# 检查数据库连接
python check_env.py
```

### 依赖问题？
```bash
# 更新测试依赖
pip install -r Test/requirements-test.txt

# 检查Python版本
python --version  # 需要 3.10+
```

## 📈 质量指标

**当前状态**: ✅ 优秀
- 测试通过率: **100%** (178/178)
- 执行时间: **~51秒**
- 警告数量: **26** (< 30)
- 代码覆盖率: **~75%** (目标85%)

## 🔗 相关链接

- 📖 [完整测试文档](Test/docs/)
- 📖 [Playwright指南](Test/PLAYWRIGHT_GUIDE.txt)
- 📖 [AI助手测试指南](Test/docs/AI助手测试指南.md)
- 📖 [测试覆盖矩阵](Test/TEST_COVERAGE_MATRIX.txt)

## 📞 快速帮助

```bash
# 查看所有可用选项
python Test/run_full_tests.py --help

# pytest帮助
pytest --help

# 查看已安装的插件
pytest --version
```

---

**最后更新**: 2026-05-10  
**状态**: ✅ 所有测试通过  
**下次运行**: 新功能开发后
