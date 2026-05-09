# 贡献指南 (Contributing)

感谢你对狗狗数据分析系统的关注！我们欢迎任何形式的贡献。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试要求](#测试要求)
- [文档要求](#文档要求)

---

## 行为准则

本项目采用开放和友好的社区原则：
- 尊重他人，保持专业
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 如何贡献

### 报告 Bug

1. 使用 GitHub Issues 报告 Bug
2. 包含详细的复现步骤
3. 提供环境信息（Python 版本、操作系统等）
4. 附上相关日志或截图

### 提出新功能

1. 先在 Issues 中讨论想法
2. 说明功能的价值和必要性
3. 等待项目维护者确认后再开始开发

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'vX.Y.Z'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 开发流程

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/Cguomei/FastApiProject.git
cd FastApiProject

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py
```

### 2. 开发功能

```bash
# 创建特性分支
git checkout -b feature/your-feature

# 开发功能
# ... 编写代码 ...

# 运行测试
python Test/run_comprehensive_tests.py api

# 提交代码
git add .
git commit -m "v4.6.0"

# 推送
git push origin feature/your-feature
```

### 3. 创建 Pull Request

- 提供清晰的功能描述
- 关联相关的 Issue
- 确保所有测试通过
- 更新相关文档

---

## 代码规范

### Python 代码
- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用 4 空格缩进
- 行长度不超过 88 字符
- 函数和类必须有文档字符串

### 命名规范
- 变量/函数：`snake_case`
- 类名：`PascalCase`
- 常量：`UPPER_CASE`
- 私有方法：`_leading_underscore`

### 注释规范
- 每个函数必须有 docstring
- 复杂逻辑需要注释说明
- 使用中文注释（项目主要语言）

---

## 提交规范

### Commit Message
- **简洁明了** - 只写版本号，如 `v4.6.0`
- **详细信息** - 写在 CHANGELOG.md 或版本文档中

**示例**：
```bash
# ✅ 正确
git commit -m "v4.6.0"

# ❌ 错误
git commit -m "feat: 添加 XXX 功能，修复 YYY 问题..."
```

### Git Tag
每次版本发布都要打标签：
```bash
git tag -a v4.6.0 -m "v4.6.0 - 功能简述"
git push origin v4.6.0
```

---

## 测试要求

### 必须通过的测试
- ✅ 所有新增功能必须有测试用例
- ✅ API 测试覆盖率 ≥ 80%
- ✅ 核心功能测试 100% 通过
- ✅ 无回归问题

### 运行测试
```bash
# 快速验证
python Test/run_comprehensive_tests.py smoke

# 完整测试
python Test/run_comprehensive_tests.py all

# 特定模块
pytest Test/api_tests/ -v
```

### 测试文件位置
- API 测试：`Test/api_tests/`
- UI 测试：`Test/ui_tests/`
- E2E 测试：`Test/e2e_tests/`

---

## 文档要求

### 必须更新的文档
- [ ] CHANGELOG.md - 记录变更
- [ ] docs/05-版本记录/ - 版本发布说明
- [ ] 相关技术文档 - 功能说明
- [ ] README.md - 如有必要

### 文档存放规范
- ✅ 放在 `docs/` 目录或其子目录
- ❌ 不要散落在项目根目录
- ✅ 使用清晰的文件名

### 文档格式
- 技术文档：Markdown (.md)
- 内部参考：文本 (.txt)
- 根据场景选择合适格式

---

## 审查清单

提交 Pull Request 前，请确认：

- [ ] 代码遵循 PEP 8 规范
- [ ] 所有测试通过
- [ ] 已添加新功能的测试用例
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 没有敏感信息泄露
- [ ] 提交信息简洁（只用版本号）
- [ ] 已创建版本标签

---

## 常见问题

### Q: 如何确定版本号？
A: 遵循语义化版本规范：
- 主版本号：不兼容的 API 修改
- 次版本号：向下兼容的功能新增
- 修订号：向下兼容的问题修正

### Q: 测试失败怎么办？
A: 
1. 查看错误信息
2. 本地调试修复
3. 再次运行测试
4. 确认通过后提交

### Q: 文档应该放在哪里？
A: 
- 项目文档：`docs/` 目录
- 测试文档：`Test/docs/` 目录
- 不要放在根目录

### Q: 多久能收到回复？
A: 我们会尽快审查，通常在 1-3 个工作日内。

---

## 联系方式

- **GitHub Issues**: [提交问题](https://github.com/Cguomei/FastApiProject/issues)
- **Email**: [项目邮箱]

---

## 致谢

感谢所有为本项目做出贡献的开发者！

---

*AI 助手：Lingma AI Assistant*
