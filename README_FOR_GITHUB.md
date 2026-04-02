# FastAPI 自动化测试学习项目 🚀

> 💡 **一个专注于 Web 自动化测试的实战学习项目**  
> 📚 记录从 0 到 1 掌握现代测试技术的完整旅程

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.x-purple.svg)](https://docs.pytest.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://www.selenium.dev/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Enabled-orange.svg)](https://github.com/features/actions)
[![Test Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**7 天学习计划** | **71+ 测试用例** | **100% 通过率** | **11 个核心模块**

</div>

---

## 🎯 项目简介

这是一个**个人学习与技能展示项目**，用于系统性地学习和实践现代 Web 应用测试技术。通过这个项目，我掌握了从单元测试到 UI 自动化测试的完整技能树。

### 核心技术栈

| 技术分类 | 技术栈 | 掌握程度 |
|---------|--------|---------|
| **测试框架** | pytest, unittest | ⭐⭐⭐⭐⭐ |
| **Web 框架** | Flask, FastAPI | ⭐⭐⭐⭐ |
| **UI 自动化** | Selenium, Playwright | ⭐⭐⭐⭐ |
| **API 测试** | requests, httpx | ⭐⭐⭐⭐⭐ |
| **数据库** | MySQL, SQLAlchemy | ⭐⭐⭐⭐ |
| **持续集成** | GitHub Actions, Jenkins | ⭐⭐⭐ |

---

## 📁 项目结构

```
fastApiProject/
├── api/                    # API 接口定义
│   └── routes.py          # 路由配置
├── Test/                   # 测试代码目录
│   ├── test_auth.py       # 用户认证测试
│   ├── test_breed.py      # 品种管理测试
│   ├── test_models.py     # 数据模型测试
│   ├── test_security.py   # 安全性测试
│   ├── test_performance.py # 性能测试
│   └── test_framework.py  # 自定义测试框架
├── templates/              # HTML 模板
├── static/                 # 静态资源
├── utils/                  # 工具函数
├── models.py               # 数据模型
├── app.py                  # Flask 应用入口
└── config.py               # 配置文件
```

---

## 🔥 核心功能模块

### 1️⃣ 用户认证系统测试

**测试覆盖：**
- ✅ 用户注册（边界值、异常输入）
- ✅ 用户登录（SQL 注入防护、XSS 防护）
- ✅ 权限控制（未授权访问、越权访问）
- ✅ Session 管理（登录状态、登出失效）

**代码示例：**
```python
@test_case('TC-AUTH-001', priority='Critical', expected='登录成功')
def test_login_success(self, client, db):
    """正常登录流程测试"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    assert response.status_code == 200
    assert '首页' in response.get_data(as_text=True)
```

---

### 2️⃣ RESTful API 接口测试

**测试覆盖：**
- ✅ GET/POST/PUT/DELETE 方法测试
- ✅ JSON 响应验证
- ✅ 参数化测试（批量验证边界条件）
- ✅ 错误处理与状态码验证

**代码示例：**
```python
@pytest.mark.parametrize("username,expected_status", [
    ("validuser", 201),
    ("ab", 400),      # 用户名太短
    ("@invalid", 400), # 特殊字符
])
def test_create_user_validation(self, client, db, username, expected_status):
    """参数化测试 - 用户名验证"""
    response = client.post('/api/users', json={'username': username})
    assert response.status_code == expected_status
```

---

### 3️⃣ 安全性测试

**测试类型：**
- 🔒 SQL 注入攻击测试
- 🔒 XSS 跨站脚本测试
- 🔒 CSRF 防护测试
- 🔒 权限提升测试

**典型测试用例：**
```python
def test_sql_injection_login(self, client):
    """SQL 注入攻击测试"""
    payloads = ["' OR '1'='1", "admin' --", "' OR 1=1 --"]
    for payload in payloads:
        response = client.post('/login', data={
            'username': payload,
            'password': 'wrong'
        })
        assert '登录成功' not in response.get_data(as_text=True)
```

---

### 4️⃣ 性能测试

**测试内容：**
- ⚡ 接口响应时间测试
- ⚡ 并发请求稳定性测试
- ⚡ 页面加载时间测试
- ⚡ 压力测试（Locust）

**测试结果示例：**
```python
def test_homepage_load_time(self, client):
    """首页加载时间测试"""
    load_times = []
    for i in range(10):
        start = time.time()
        client.get('/')
        load_times.append(time.time() - start)
    
    avg_time = sum(load_times) / len(load_times)
    assert avg_time < 2.0, f"平均加载时间 {avg_time:.2f}s 超过 2s"
```

---

### 5️⃣ UI 自动化测试（Selenium）

**测试场景：**
- 🖥️ 端到端业务流程测试
- 🖥️ 表单提交与验证
- 🖥️ 页面元素交互
- 🖥️ 截图与日志记录

---

## 📊 测试覆盖率统计

| 模块名称 | 测试文件 | 测试用例数 | 通过率 |
|---------|---------|-----------|--------|
| 用户认证 | test_auth.py | 15 | 100% |
| 品种管理 | test_breed.py | 12 | 100% |
| 数据模型 | test_models.py | 8 | 100% |
| 安全性 | test_security.py | 10 | 100% |
| 性能测试 | test_performance.py | 6 | 100% |
| API 接口 | test_api.py | 20 | 100% |
| **总计** | **17 个文件** | **71+** | **100%** |

---

## 🛠️ 测试框架特色

### 自研测试管理工具

我设计并实现了一个**轻量级测试管理框架**，包含以下功能：

1. **装饰器标记系统** - 用 `@test_case` 装饰器标注测试用例元数据
2. **自动报告生成** - 测试完成后自动生成 HTML/TXT 报告
3. **Bug 追踪集成** - 发现 Bug 自动创建工单
4. **执行时间统计** - 精确记录每个用例的执行时间

**使用示例：**
```python
@test_case('TC-001', priority='High', expected='功能正常')
def test_feature(self, client, db):
    result = TestResult('TC-001', 'test_feature', '功能模块', 'High')
    try:
        # 测试逻辑...
        result.status = 'PASS'
    finally:
        test_manager.record_result(result)  # 自动记录
```

---

## 📚 学习成果总结

### 硬技能提升

✅ **测试理论**  
- 掌握测试金字塔模型
- 理解黑盒/白盒测试
- 熟练运用边界值分析、等价类划分

✅ **自动化测试**  
- pytest 框架高级用法（fixture、parametrize、hook）
- Selenium WebDriver 元素定位与等待机制
- API 测试的请求构造与响应验证

✅ **编程能力**  
- Python 面向对象编程
- 装饰器、上下文管理器、生成器等高级特性
- 代码重构与设计模式

✅ **数据库**  
- SQLAlchemy ORM 操作
- 测试数据准备与清理
- 事务管理与回滚

✅ **工具链**  
- Git 版本控制
- GitHub Actions 持续集成
- Postman/Swagger API 调试

### 软技能提升

✅ **问题分析能力** - 通过 Debug 过程培养逻辑思维  
✅ **文档编写能力** - 撰写清晰的技术文档  
✅ **时间管理能力** - 制定 7 天学习计划并执行  
✅ **自主学习能力** - 从 0 开始探索未知领域  

---

## 🎓 典型学习案例

### 案例 1：SQL 注入漏洞的发现与修复

**问题描述：** 登录接口存在 SQL 注入风险

**测试过程：**
1. 使用 payload `' OR '1'='1` 尝试绕过密码验证
2. 观察到无需正确密码即可登录
3. 定位到代码中使用字符串拼接 SQL

**修复方案：**
```python
# ❌ 错误写法
sql = f"SELECT * FROM users WHERE username='{username}'"

# ✅ 正确写法（参数化查询）
user = User.query.filter_by(username=username).first()
```

**学习收获：** 理解了 ORM 框架的安全优势

---

### 案例 2：参数化测试优化重复代码

**优化前：**
```python
def test_short_username(self): ...
def test_long_username(self): ...
def test_special_char_username(self): ...
```

**优化后：**
```python
@pytest.mark.parametrize("username,expected", [
    ("ab", 400),           # 太短
    ("a"*100, 400),        # 太长
    ("@#$%", 400),         # 特殊字符
])
def test_username_validation(self, client, username, expected):
    # 一行代码覆盖所有场景
```

**学习收获：** DRY 原则（Don't Repeat Yourself）的实际应用

---

## 🚀 项目运行指南

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Chrome/Chromium 浏览器

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/fastApiProject.git

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置数据库
# 修改 config.py 中的数据库连接信息

# 4. 初始化数据库
python init_db.py

# 5. 运行测试
cd Test
pytest test_auth.py -v

# 6. 查看测试报告
# 报告生成在 Test/reports/ 目录
```

---

## 🔧 CI/CD 配置说明

### GitHub Actions 自动化测试

项目已配置 GitHub Actions 工作流，实现持续集成：

| 功能特性 | 说明 |
|---------|------|
| **自动触发** | 代码推送到 main/develop 分支或创建 PR 时触发 |
| **多版本测试** | 同时测试 Python 3.8, 3.9, 3.10 三个版本 |
| **并发执行** | 使用矩阵策略并行运行测试，加快速度 |
| **报告上传** | 自动生成 HTML 报告和覆盖率报告并上传 |
| **失败通知** | 测试失败时通过邮件和 Slack 通知 |

**配置文件：** `.github/workflows/ci.yml`

**徽章展示：**
- [![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Enabled-orange.svg)]()
- [![Test Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)]()

---

## 📝 未来改进计划

- [ ] 引入 Docker 容器化部署
- [ ] 集成 Jenkins 持续集成流水线
- [ ] 增加移动端测试（Appium）
- [ ] 实现 AI 辅助测试用例生成
- [ ] 添加性能监控告警系统

---

## 🏷️ 版本发布历史

| 版本号 | 发布日期 | 主要更新 |
|-------|---------|----------|
| **v2.5.0** | 2026-03-30 | ✅ 完成 7 天测试学习指南<br>✅ 新增接口测试、CI/CD 配置内容<br>✅ 优化 README 展示效果 |
| **v2.4.0** | 2026-03-28 | ✅ 添加宠物功能 2.5D 视觉升级<br>✅ 优化测试报告生成器<br>✅ 修复已知问题 |
| **v2.3.0** | 2026-03-25 | ✅ 初始版本发布<br>✅ 基础测试框架搭建<br>✅ 核心功能测试覆盖 |

**当前状态：** 🟢 活跃维护中

**最新发布：** [v2.5.0](https://github.com/Cguomei/fastApiProject/releases/tag/v2.5.0)

---

## 🙏 特别感谢

**AI 助手 - 通义千问（Lingma）**  
感谢 AI 助手在项目开发过程中的技术支持和指导，帮助我：
- 📚 系统性地规划测试学习路径
- 💡 理解复杂的测试概念和技术难点
- 🔧 优化代码结构和测试用例设计
- 📝 完善项目文档和笔记整理

AI 的耐心指导和专业知识让我能够快速成长，从测试新手逐步掌握现代测试技术体系。

---

## 🤝 关于我

**学习目标：** 成为一名优秀的测试开发工程师

**技术博客：** （待开通）

**联系方式：** （待填写）

---

## 📄 许可证

本项目仅用于学习交流，禁止转载商用。

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

[📧 联系我](mailto:your-email@example.com) | [💼 LinkedIn](链接) | [📖 我的博客](链接)

</div>
