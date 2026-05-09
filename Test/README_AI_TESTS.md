# 🤖 AI智能助手 - 测试文档索引

## 📁 文件结构

```
Test/
├── api_tests/
│   └── test_ai_assistant.py          # API接口测试（21个测试）
├── ui_tests/
│   └── test_ai_chat.py               # UI界面测试（10个测试）
├── docs/
│   └── AI助手测试指南.md              # 详细测试指南
├── reports/
│   └── AI助手测试总结_20260509.md    # 测试总结报告
└── run_ai_tests.py                   # 一键运行测试脚本
```

---

## 🚀 快速开始

### 方式1: 使用一键脚本（推荐）

```bash
python Test/run_ai_tests.py
```

这个脚本会：
- ✅ 自动检查Flask是否运行
- ✅ 按顺序执行所有测试
- ✅ 显示实时测试结果
- ✅ 生成统计报告
- ✅ 可选生成HTML报告

### 方式2: 手动运行

#### 只运行问题分类器测试（无需Flask）
```bash
pytest Test/api_tests/test_ai_assistant.py::TestQuestionClassifier -v
```

#### 运行所有API测试（需要Flask运行）
```bash
pytest Test/api_tests/test_ai_assistant.py -v
```

#### 运行UI测试（需要Playwright）
```bash
pytest Test/ui_tests/test_ai_chat.py -v --headed
```

#### 生成HTML报告
```bash
pytest Test/api_tests/test_ai_assistant.py -v \
  --html=reports/ai_test_report.html \
  --self-contained-html
```

---

## 📊 测试覆盖

### API测试 (test_ai_assistant.py)

#### TestAIAssistant 类 - 15个测试
- ✅ 模型状态检查（已登录/未登录）
- ✅ 聊天功能（5种问题类型）
- ✅ 错误处理（空消息、超长消息等）
- ✅ 权限控制
- ✅ 页面访问
- ✅ 日志查看

#### TestQuestionClassifier 类 - 6个测试
- ✅ 价格查询分类
- ✅ 品种信息分类
- ✅ 推荐分类
- ✅ 对比分类
- ✅ 品种名称提取
- ✅ 多品种提取

**当前状态**: 6/21 通过（分类器部分）

### UI测试 (test_ai_chat.py) - 10个测试
- ⏳ 页面加载
- ⏳ 模型状态显示
- ⏳ 发送消息
- ⏳ 快捷问题按钮
- ⏳ 打字指示器
- ⏳ 消息格式化
- ⏳ 回车键发送
- ⏳ 空消息处理
- ⏳ 自动滚动
- ⏳ 欢迎消息

**当前状态**: 待运行

---

## 📖 详细文档

### 1. [AI助手测试指南.md](docs/AI助手测试指南.md)
包含：
- 完整的测试命令
- 前置条件说明
- 调试技巧
- 常见问题解答
- CI/CD集成示例
- 最佳实践

### 2. [AI助手测试总结_20260509.md](reports/AI助手测试总结_20260509.md)
包含：
- 测试统计
- 已修复的问题
- 质量指标
- 下一步计划

---

## 🔧 前置条件

### API测试
```bash
# 1. 安装依赖
pip install pytest pytest-flask pytest-html

# 2. 启动Flask应用
python app.py

# 3. 确保数据库已初始化
python init_db.py
```

### UI测试
```bash
# 1. 安装Playwright
pip install playwright

# 2. 安装浏览器
playwright install chromium

# 3. 启动Flask应用
python app.py
```

---

## 🎯 测试目标

### MVP阶段（当前）
- [x] 问题分类器测试
- [ ] 完整API测试
- [ ] 基础UI测试
- [ ] 错误处理测试

### V2阶段
- [ ] 性能测试
- [ ] 安全测试
- [ ] 边界情况测试
- [ ] 80%+代码覆盖率

### V3阶段
- [ ] E2E测试
- [ ] 自动化CI/CD
- [ ] 混沌工程测试
- [ ] 压力测试

---

## 📈 测试进度

```
问题分类器测试: ████████████████████ 100% (6/6)
API功能测试:    ███░░░░░░░░░░░░░░░░░  29% (6/21)
UI界面测试:     ░░░░░░░░░░░░░░░░░░░░   0% (0/10)
总体进度:       █████░░░░░░░░░░░░░░░  16% (6/37)
```

---

## 💡 提示

### 提高测试速度
```bash
# 并行运行测试
pytest Test/api_tests/test_ai_assistant.py -n auto

# 只运行失败的测试
pytest Test/api_tests/test_ai_assistant.py --lf

# 跳过慢速测试
pytest Test/api_tests/test_ai_assistant.py -m "not slow"
```

### 调试测试
```bash
# 查看详细输出
pytest Test/api_tests/test_ai_assistant.py -v -s

# 进入调试模式
pytest Test/api_tests/test_ai_assistant.py --pdb

# 只运行特定测试
pytest Test/api_tests/test_ai_assistant.py::TestAIAssistant::test_chat_price_query -v
```

### 生成覆盖率报告
```bash
pytest Test/api_tests/test_ai_assistant.py \
  --cov=routes.ai_assistant \
  --cov-report=html \
  --cov-report=term-missing

# 打开报告
start htmlcov/index.html  # Windows
```

---

## 🐛 常见问题

### Q: 测试导入失败？
**A**: 确保在项目根目录运行，并且已安装所有依赖。

### Q: API测试返回401？
**A**: 确保Flask正在运行，并且admin用户存在。

### Q: UI测试找不到元素？
**A**: 增加等待时间或使用更稳定的选择器。

### Q: 如何查看日志？
**A**: 查看 `log/ai_assistant.log` 文件。

---

## 📞 支持

如有问题，请查看：
1. [AI助手测试指南.md](docs/AI助手测试指南.md) - 详细文档
2. Flask终端输出 - 运行时日志
3. `log/ai_assistant.log` - AI助手日志

---

**最后更新**: 2026-05-09  
**维护者**: AI助手开发团队
