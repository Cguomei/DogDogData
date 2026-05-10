# AI助手自动化测试指南

**版本**: v4.7.5  
**更新时间**: 2026-05-09

---

## 📋 测试概览

AI助手功能包含完整的自动化测试套件，覆盖：
- ✅ **API测试**: 31个测试用例
- ✅ **UI测试**: 16个测试用例（Playwright）
- ✅ **单元测试**: 6个问题分类器测试

**总计**: 53个测试用例

---

## 🚀 快速开始

### 方式1: 运行完整测试套件

```bash
python Test/run_ai_full_tests.py
```

这会依次运行：
1. 问题分类器单元测试
2. API集成测试
3. UI端到端测试（可选）

### 方式2: 单独运行API测试

```bash
pytest Test/api_tests/test_ai_assistant.py -v
```

### 方式3: 单独运行UI测试

```bash
pytest Test/ui_tests/test_ai_chat.py -v --headed
```

### 方式4: 运行特定测试类

```bash
# 会话管理测试
pytest Test/api_tests/test_ai_assistant.py::TestSessionManagement -v

# 反馈系统测试
pytest Test/api_tests/test_ai_assistant.py::TestFeedbackSystem -v

# 自动学习测试
pytest Test/api_tests/test_ai_assistant.py::TestAutoLearning -v
```

---

## 📊 测试覆盖范围

### API测试 (31个用例)

#### TestAIAssistant (16个)
- ✅ 模型状态检查（已登录/未登录）
- ✅ 价格查询
- ✅ 品种信息查询
- ✅ 推荐功能
- ✅ 对比功能
- ✅ 通用问答
- ✅ 空消息处理
- ✅ 消息过长处理
- ✅ 权限控制

#### TestSessionManagement (6个) - V2新增
- ✅ 创建会话
- ✅ 获取会话列表
- ✅ 获取会话详情
- ✅ 带会话ID聊天
- ✅ 获取消息历史
- ✅ 删除会话

#### TestFeedbackSystem (4个) - V2新增
- ✅ 点赞反馈
- ✅ 点踩反馈
- ✅ 无效反馈类型
- ✅ 缺少必要字段

#### TestAutoLearning (2个) - V2新增
- ✅ 手动学习
- ✅ 缺少字段验证

#### TestQuestionClassifier (6个)
- ✅ 价格查询分类
- ✅ 品种信息分类
- ✅ 推荐分类
- ✅ 对比分类
- ✅ 品种名称提取
- ✅ 多品种提取

### UI测试 (16个用例)

#### TestAIChatUI (16个)
- ✅ 页面加载
- ✅ 模型状态显示
- ✅ 发送消息
- ✅ 快捷问题按钮
- ✅ 打字指示器
- ✅ 消息格式化
- ✅ 回车键发送
- ✅ 空消息不发送
- ✅ 自动滚动
- ✅ 欢迎消息
- ✅ 会话侧边栏显示 - V2新增
- ✅ 创建新会话 - V2新增
- ✅ 会话列表显示 - V2新增
- ✅ 反馈按钮出现 - V2新增
- ✅ 提交点赞反馈 - V2新增
- ✅ 上下文对话 - V2新增

---

## 🔧 环境要求

### 必需依赖

```bash
pip install pytest flask pytest-flask
```

### UI测试额外依赖

```bash
pip install playwright
playwright install
```

---

## 📝 测试前置条件

### 1. 启动Flask应用

```bash
python app.py
```

确保应用在 `http://localhost:5000` 运行。

### 2. 准备测试数据

测试会自动使用以下账号：
- **用户名**: admin
- **密码**: admin123

如果密码不同，需要修改测试文件中的登录凭据。

### 3. 启动本地模型（可选）

如果要测试真实的AI回复，需要启动Ollama或LM Studio：

```bash
# Ollama
ollama pull qwen2.5:1.5b
ollama serve
```

如果不启动模型，测试会使用知识库的默认回答。

---

## 🎯 测试执行流程

### 完整测试流程

```
1. 问题分类器测试 (最快，~5秒)
   └─ 纯Python代码，无需HTTP请求

2. API测试 (~30秒)
   ├─ 创建测试会话
   ├─ 发送测试消息
   ├─ 验证响应格式
   └─ 清理测试数据

3. UI测试 (~2分钟，可选)
   ├─ 打开浏览器
   ├─ 自动登录
   ├─ 执行交互操作
   └─ 验证页面元素
```

### 预期输出

```
🚀 AI助手自动化测试套件
============================================================
开始时间: Sat May  9 22:30:00 2026

============================================================
🔍 运行问题分类器单元测试
============================================================
...
6 passed in 0.12s

============================================================
🧪 运行AI助手 API 测试
============================================================
...
31 passed in 28.45s

是否运行UI测试？(y/n，需要浏览器): y

============================================================
🎭 运行AI助手 UI 测试（Playwright）
============================================================
...
16 passed in 125.30s

============================================================
📊 测试总结
============================================================
API测试           ✅ 通过
UI测试           ✅ 通过
分类器测试        ✅ 通过

总通过率: 3/3 (100.0%)
============================================================

🎉 所有测试通过！
```

---

## ⚠️ 常见问题

### 1. 测试失败：401 Unauthorized

**原因**: 登录凭据错误

**解决**: 修改测试文件中的用户名和密码
```python
page.fill('input[name="username"]', 'admin')
page.fill('input[name="password"]', '你的密码')
```

### 2. UI测试超时

**原因**: Flask应用未启动或模型响应慢

**解决**:
- 确认Flask应用正在运行
- 增加超时时间：`timeout=30000`

### 3. Playwright未找到

**原因**: 未安装Playwright

**解决**:
```bash
pip install playwright
playwright install chromium
```

### 4. 数据库冲突

**原因**: 多个测试同时写入数据库

**解决**: 使用事务回滚或清理测试数据
```python
@pytest.fixture(autouse=True)
def cleanup():
    yield
    db.session.rollback()
```

---

## 📈 测试统计

### 代码覆盖率

```bash
pytest Test/api_tests/test_ai_assistant.py --cov=routes.ai_assistant --cov-report=html
```

生成HTML报告后，打开 `htmlcov/index.html` 查看。

### 性能指标

| 测试类型 | 用例数 | 平均耗时 | 总耗时 |
|---------|--------|----------|--------|
| 分类器测试 | 6 | 0.02s | 0.12s |
| API测试 | 31 | 0.92s | 28.45s |
| UI测试 | 16 | 7.83s | 125.30s |
| **总计** | **53** | - | **~154s** |

---

## 🔍 调试技巧

### 1. 查看详细日志

```bash
pytest Test/api_tests/test_ai_assistant.py -v -s
```

`-s` 参数会显示print输出。

### 2. 只运行失败的测试

```bash
pytest Test/api_tests/test_ai_assistant.py --lf
```

### 3. 逐步执行UI测试

```bash
pytest Test/ui_tests/test_ai_chat.py::TestAIChatUI::test_send_message --headed --slowmo=1000
```

`--slowmo=1000` 让每个操作延迟1秒，便于观察。

### 4. 截图调试

在UI测试中添加：
```python
page.screenshot(path='debug.png')
```

---

## 📚 相关文件

- `Test/api_tests/test_ai_assistant.py` - API测试
- `Test/ui_tests/test_ai_chat.py` - UI测试
- `Test/run_ai_full_tests.py` - 完整测试运行器
- `Test/conftest.py` - 测试配置和fixtures
- `routes/ai_assistant.py` - 被测代码

---

## 🎯 最佳实践

1. **每次提交前运行测试**
   ```bash
   python Test/run_ai_full_tests.py
   ```

2. **优先运行快速测试**
   ```bash
   pytest Test/api_tests/test_ai_assistant.py::TestQuestionClassifier -v
   ```

3. **定期更新测试用例**
   - 新功能必须添加测试
   - Bug修复后添加回归测试

4. **保持测试独立性**
   - 每个测试应该能独立运行
   - 使用fixtures管理测试数据

5. **监控测试性能**
   - 单个测试不超过5秒
   - 整个套件不超过3分钟

---

## 🚦 CI/CD集成

### GitHub Actions示例

```yaml
name: AI Assistant Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest playwright
        playwright install
    
    - name: Start Flask app
      run: python app.py &
      env:
        FLASK_ENV: testing
    
    - name: Run tests
      run: python Test/run_ai_full_tests.py
```

---

**最后更新**: 2026-05-09  
**维护者**: AI助手开发团队
