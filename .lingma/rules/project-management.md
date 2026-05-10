# 项目管理规范

> **版本**: v1.0  
> **最后更新**: 2026-05-10  
> **适用范围**: 狗狗数据分析系统全项目

## 📋 目录

- [核心原则](#核心原则)
- [长任务管理](#长任务管理)
- [工作流程](#工作流程)
- [代码规范](#代码规范)
- [测试规范](#测试规范)
- [Git 管理规范](#git-管理规范)
- [技术文档维护](#技术文档维护)
- [AI 助手交互规范](#ai-助手交互规范)
- [禁止行为](#禁止行为)
- [必须执行](#必须执行)

---

## 核心原则

### 1. 测试驱动开发（TDD）🔴🟢🔵

**核心理念**：先写测试，再写代码，最后重构

- **必须先写测试**：任何新功能开发前，先编写对应的测试用例
- **测试覆盖率要求**：
  - 新功能测试覆盖率 ≥ 80%
  - 核心业务逻辑覆盖率 ≥ 95%
  - API 接口覆盖率 100%
- **测试先行流程**：
  1. 🔴 **Red**：编写测试用例（预期失败）
  2. 🟢 **Green**：实现功能代码（使测试通过）
  3. 🔵 **Refactor**：重构优化（保持测试通过）
- **测试类型**：
  - 单元测试：测试单个函数/方法
  - 集成测试：测试模块间交互
  - API 测试：测试 HTTP 接口
  - UI/E2E 测试：测试用户界面和完整流程

### 2. 渐进式开发策略 📈

**核心理念**：MVP 优先，迭代完善

- **MVP（最小可行产品）优先**：先实现核心功能，再逐步完善
- **分阶段交付**：
  - **Phase 1 - MVP**（必须）：核心功能，能跑通主流程
  - **Phase 2 - Enhanced**（应该）：增强功能，提升用户体验
  - **Phase 3 - Optimized**（可以）：优化功能，性能和细节
- **避免过度设计**：
  - ❌ 不要提前实现未确认的需求
  - ❌ 不要为未来可能的场景做复杂设计
  - ✅ 只解决当前明确的问题
  - ✅ 保持代码简单清晰

### 3. 代码质量管理 💎

**核心理念**：质量第一，持续改进

- **提交前检查清单**：
  - [ ] 运行相关测试套件，全部通过
  - [ ] 确保无 lint 错误和警告
  - [ ] 代码审查（至少一人）
  - [ ] 更新相关文档
  - [ ] 检查敏感信息（密码、密钥等）
  
- **代码质量标准**：
  - **可读性**：变量命名清晰，函数职责单一
  - **可维护性**：模块化设计，低耦合高内聚
  - **可扩展性**：预留扩展点，但不提前实现
  - **性能**：避免明显的性能问题（N+1 查询等）
  
- **分支策略**：
  ```
  main          ← 稳定版本，随时可部署
    ↑
  develop       ← 开发分支，集成新功能
    ↑
  feature/*     ← 功能分支，开发新功能
    ↑
  hotfix/*      ← 紧急修复，直接基于 main
  ```

### 4. 文档同步更新 📝

**核心理念**：代码即文档，文档即契约

- **代码层面**：
  - 清晰的函数名和变量名
  - 必要的注释（Why，而非 What）
  - Docstring 描述函数用途、参数、返回值
  
- **项目文档**：
  - README.md：项目概述、安装、使用
  - CHANGELOG.md：版本变更记录
  - API 文档：接口定义、请求/响应示例
  - 技术文档：架构设计、关键技术决策
  
- **更新时机**：
  - 功能变更 → 更新 API 文档
  - 配置变更 → 更新 README
  - Bug 修复 → 更新 CHANGELOG
  - 架构调整 → 更新技术文档

---

## 长任务管理 📝

### 为什么需要任务清单？

对于复杂的功能开发或大型重构，必须使用任务清单来：
- ✅ 避免遗漏关键步骤
- ✅ 清晰跟踪进度
- ✅ 便于中断后恢复
- ✅ 提高代码质量
- ✅ 方便团队协作

### 任务清单模板

```markdown
## 任务：[任务名称]

**开始时间**：YYYY-MM-DD  
**预计完成**：YYYY-MM-DD  
**负责人**：[姓名]  
**优先级**：高/中/低

### 📋 任务分解

- [ ] **步骤 1**：[具体任务描述]
  - 子任务 1.1
  - 子任务 1.2
  
- [ ] **步骤 2**：[具体任务描述]
  - 子任务 2.1
  - 子任务 2.2
  
- [ ] **步骤 3**：[具体任务描述]

### 📊 当前进度

- 已完成：X/Y 步骤
- 当前正在：步骤 N
- 遇到的问题：[如有]

### 📝 备注

- 重要决策记录
- 技术难点说明
- 待确认事项
```

### 任务清单使用流程

#### 1. 任务开始前

**AI 应该**：
```
我理解您需要[任务描述]。这是一个较为复杂的任务，我将创建任务清单来确保每一步都正确执行。

📋 任务清单：

- [ ] 步骤 1：需求分析和方案设计
- [ ] 步骤 2：编写测试用例
- [ ] 步骤 3：实现核心功能
- [ ] 步骤 4：编写集成测试
- [ ] 步骤 5：性能优化
- [ ] 步骤 6：文档更新
- [ ] 步骤 7：最终测试验证

我将按照这个清单逐步执行，每完成一步都会向您汇报进度。

现在开始步骤 1...
```

#### 2. 执行过程中

**每完成一个步骤**：
```
✅ 步骤 1 已完成：需求分析和方案设计

完成内容：
- 确认了功能需求
- 设计了 API 接口
- 确定了技术方案

下一步：步骤 2 - 编写测试用例

当前进度：1/7 (14%)
```

#### 3. 遇到中断时

**如果对话中断或需要暂停**：
```
⏸️ 任务暂停

当前进度：3/7 (43%)
已完成：
- ✅ 步骤 1：需求分析
- ✅ 步骤 2：编写测试
- ✅ 步骤 3：实现核心功能

正在进行：步骤 4 - 编写集成测试

下次继续时，请告诉我"继续之前的任务"，我将从步骤 4 继续。
```

#### 4. 任务完成后

**总结报告**：
```
✨ 任务完成！

📊 最终进度：7/7 (100%)

完成内容总结：
1. ✅ 需求分析和方案设计
2. ✅ 编写测试用例（8个测试）
3. ✅ 实现核心功能
4. ✅ 编写集成测试
5. ✅ 性能优化（查询速度提升 50%）
6. ✅ 文档更新
7. ✅ 最终测试验证（所有测试通过）

📁 修改的文件：
- routes/xxx.py
- Test/test_xxx.py
- docs/API.md

📝 技术文档已更新：
- docs/features/xxx.md

🚀 下一步建议：
- 可以部署到测试环境
- 可以进行用户验收测试
```

### 长任务示例

#### 示例：开发完整的用户认证系统

```markdown
## 任务：开发用户认证系统

**开始时间**：2026-05-10  
**预计完成**：2026-05-12  
**优先级**：高

### 📋 任务分解

- [ ] **步骤 1**：需求分析和设计
  - [ ] 确定认证方式（JWT）
  - [ ] 设计数据库表结构
  - [ ] 设计 API 接口
  
- [ ] **步骤 2**：数据库迁移
  - [ ] 创建 users 表
  - [ ] 创建 sessions 表
  - [ ] 编写迁移脚本
  
- [ ] **步骤 3**：后端 API 开发
  - [ ] 注册 API
  - [ ] 登录 API
  - [ ] JWT token 生成和验证
  - [ ] 登出 API
  
- [ ] **步骤 4**：编写测试
  - [ ] 单元测试（模型层）
  - [ ] API 测试（注册、登录、登出）
  - [ ] 集成测试（完整流程）
  
- [ ] **步骤 5**：前端界面
  - [ ] 登录页面
  - [ ] 注册页面
  - [ ] 表单验证
  
- [ ] **步骤 6**：安全加固
  - [ ] 密码加密（bcrypt）
  - [ ] 防止暴力破解
  - [ ] CSRF 保护
  
- [ ] **步骤 7**：文档和部署
  - [ ] API 文档
  - [ ] 使用说明
  - [ ] 部署到测试环境

### 📊 进度跟踪

每次完成一个步骤，更新进度并汇报。
```

### AI 助手的责任

在执行长任务时，AI 必须：

1. **主动创建清单**：识别复杂任务，主动提出使用清单
2. **逐步执行**：严格按照清单顺序执行，不跳步
3. **实时汇报**：每完成一步立即汇报进度
4. **保存状态**：在中断前保存当前状态和进度
5. **快速恢复**：能够从中断处快速恢复
6. **完整总结**：任务完成后提供详细总结

--- 📝

**核心理念**：代码即文档，文档即契约

- **代码层面**：
  - 清晰的函数名和变量名
  - 必要的注释（Why，而非 What）
  - Docstring 描述函数用途、参数、返回值
  
- **项目文档**：
  - README.md：项目概述、安装、使用
  - CHANGELOG.md：版本变更记录
  - API 文档：接口定义、请求/响应示例
  - 技术文档：架构设计、关键技术决策
  
- **更新时机**：
  - 功能变更 → 更新 API 文档
  - 配置变更 → 更新 README
  - Bug 修复 → 更新 CHANGELOG
  - 架构调整 → 更新技术文档

---

## 工作流程

### 新功能开发流程 🚀

```
1. 需求分析 
   ↓
2. 方案设计（提供 2-3 个方案）
   ↓
3. 编写测试用例（🔴 Red）
   ↓
4. 实现功能代码（🟢 Green）
   ↓
5. 运行测试验证
   ↓
6. 重构优化（🔵 Refactor）
   ↓
7. 代码审查
   ↓
8. 合并部署
```

**每个步骤的详细说明**：

1. **需求分析**：
   - 明确功能目标
   - 确定输入/输出
   - 识别边界条件
   - 评估技术可行性

2. **方案设计**：
   - 提供 2-3 个可行方案
   - 分析各方案优缺点
   - 推荐最佳方案并说明理由
   - 等待用户确认

3. **编写测试**：
   - 正常场景测试
   - 边界条件测试
   - 异常情况测试
   - 性能测试（如需要）

4. **实现代码**：
   - 编写最少的代码使测试通过
   - 不要过度设计
   - 保持代码简洁

5. **测试验证**：
   - 运行单元测试
   - 运行集成测试
   - 运行 API 测试
   - 检查测试覆盖率

6. **重构优化**：
   - 改进代码结构
   - 提取重复代码
   - 优化命名
   - 添加注释

7. **代码审查**：
   - 自查代码质量
   - 邀请他人审查
   - 修复审查意见

8. **合并部署**：
   - 合并到 develop 分支
   - 运行完整测试套件
   - 部署到测试环境
   - 验证功能正常

### Bug 修复流程 🐛

```
1. 复现问题
   ↓
2. 定位原因
   ↓
3. 编写回归测试
   ↓
4. 修复代码
   ↓
5. 验证测试
   ↓
6. 代码审查
   ↓
7. 合并部署
```

**关键点**：
- 必须先编写回归测试，确保 Bug 不会再次出现
- 修复后运行相关测试，确保没有引入新问题
- 记录 Bug 原因和解决方案，便于后续参考

### 代码审查流程 👥

**审查清单**：
- [ ] 代码是否符合规范
- [ ] 测试是否充分
- [ ] 是否有潜在的性能问题
- [ ] 是否有安全隐患
- [ ] 文档是否更新
- [ ] 是否有硬编码的敏感信息

**审查原则**：
- 尊重作者，建设性反馈
- 关注代码，不针对人
- 提出建议，而非命令
- 及时响应，不拖延

---

## 代码规范

### Flask 项目结构 📁

```
project/
├── api/              # API 路由
├── routes/           # Web 路由
├── models.py         # 数据模型
├── models_extended.py # 扩展数据模型
├── utils/            # 工具函数
├── static/           # 静态资源
│   ├── css/
│   ├── js/
│   └── img/
├── templates/        # HTML 模板
├── Test/             # 测试文件
│   ├── api_tests/    # API 测试
│   ├── ui_tests/     # UI 测试
│   └── e2e_tests/    # E2E 测试
├── scripts/          # 脚本文件
├── docs/             # 文档
└── .env              # 环境变量
```

### 命名规范 🏷️

- **变量/函数**：snake_case（小写+下划线）
  ```python
  user_name = "John"
  def get_user_info():
      pass
  ```

- **类名**：PascalCase（大驼峰）
  ```python
  class UserProfile:
      pass
  ```

- **常量**：UPPER_CASE（大写+下划线）
  ```python
  MAX_RETRY_COUNT = 3
  API_BASE_URL = "https://api.example.com"
  ```

- **私有方法/变量**：前缀下划线
  ```python
  def _internal_helper():
      pass
  
  _private_var = "value"
  ```

### 注释规范 💬

- **Docstring**：所有公共函数/类必须有 docstring
  ```python
  def calculate_price(base_price: float, discount: float) -> float:
      """
      计算折后价格
      
      Args:
          base_price: 基础价格
          discount: 折扣率 (0-1)
      
      Returns:
          折后价格
      
      Raises:
          ValueError: 当折扣率不在 0-1 范围内时
      """
      if not 0 <= discount <= 1:
          raise ValueError("折扣率必须在 0-1 之间")
      return base_price * (1 - discount)
  ```

- **行内注释**：解释 Why，而非 What
  ```python
  # ❌ 不好：重复代码含义
  count = count + 1  # count 加 1
  
  # ✅ 好：解释原因
  count = count + 1  # 补偿索引偏移，因为列表从 0 开始
  ```

### 错误处理 ⚠️

- **使用具体的异常类型**
  ```python
  # ❌ 不好
  try:
      result = do_something()
  except Exception:
      pass
  
  # ✅ 好
  try:
      result = do_something()
  except ValueError as e:
      logger.error(f"参数错误: {e}")
      raise
  except DatabaseError as e:
      logger.error(f"数据库错误: {e}")
      rollback()
      raise
  ```

- **不要静默吞掉异常**
  ```python
  # ❌ 绝对禁止
  try:
      risky_operation()
  except:
      pass
  
  # ✅ 正确做法
  try:
      risky_operation()
  except SpecificError as e:
      logger.warning(f"操作失败: {e}")
      handle_error()
  ```

### 性能优化 ⚡

- **避免 N+1 查询**
  ```python
  # ❌ 不好：N+1 查询
  users = User.query.all()
  for user in users:
      print(user.profile.name)  # 每次循环都查询数据库
  
  # ✅ 好：使用 joinedload
  from sqlalchemy.orm import joinedload
  users = User.query.options(joinedload(User.profile)).all()
  for user in users:
      print(user.profile.name)  # 只查询一次
  ```

- **合理使用缓存**
  ```python
  from flask_caching import Cache
  cache = Cache()
  
  @cache.cached(timeout=300)
  def get_expensive_data():
      # 耗时操作
      return expensive_computation()
  ```

---

## 测试规范

### 测试文件组织 📂

```
Test/
├── test_models.py          # 模型单元测试
├── test_routes.py          # 路由单元测试
├── api_tests/
│   ├── test_auth.py        # 认证 API 测试
│   ├── test_breeds.py      # 品种 API 测试
│   └── test_dogs.py        # 狗狗 API 测试
├── ui_tests/
│   ├── test_login.py       # 登录页面测试
│   └── test_dashboard.py   # 仪表板测试
└── e2e_tests/
    └── test_full_flow.py   # 完整流程测试
```

### 测试命名规范 🏷️

- **测试函数命名**：`test_[功能]_[场景]_[预期结果]`
  ```python
  def test_search_dogs_by_breed_returns_matching_results():
      pass
  
  def test_search_dogs_with_invalid_breed_returns_empty_list():
      pass
  
  def test_create_user_with_duplicate_email_raises_error():
      pass
  ```

### 测试结构（AAA 模式）🔬

```python
def test_example():
    # Arrange（准备）
    user = User(username="test", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    
    # Act（执行）
    result = User.query.filter_by(username="test").first()
    
    # Assert（断言）
    assert result is not None
    assert result.email == "test@example.com"
```

### 测试覆盖率要求 📊

- **新功能**：≥ 80%
- **核心业务逻辑**：≥ 95%
- **API 接口**：100%
- **工具函数**：≥ 90%

**检查覆盖率**：
```bash
pytest Test/ --cov=. --cov-report=html
# 打开 htmlcov/index.html 查看报告
```

### Mock 和 Fixture 使用 🎭

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_redis():
    """Mock Redis 连接"""
    with patch('redis.Redis') as mock:
        mock.get.return_value = "test_value"
        yield mock

def test_api_with_mock(client, mock_redis):
    response = client.get('/api/data')
    assert response.status_code == 200
```

### 测试标记 🏷️

```python
import pytest

@pytest.mark.slow
def test_expensive_operation():
    # 耗时较长的测试
    pass

@pytest.mark.integration
def test_database_integration():
    # 集成测试
    pass

@pytest.mark.skip(reason="暂未实现")
def test_future_feature():
    pass

# 运行特定标记的测试
# pytest -m slow
# pytest -m integration
# pytest -m "not slow"
```

---

## Git 管理规范

### Commit Message 规范 📝

**格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**示例**：
```bash
# ✅ 好的 commit message
feat(auth): 添加 JWT 认证功能

- 实现 JWT token 生成和验证
- 添加登录和注册 API
- 编写相关测试用例

Closes #123

# ❌ 不好的 commit message
修改代码
更新
fix bug
```

**简化版（推荐日常使用）**：
```bash
git commit -m "v1.0.1"
git commit -m "v1.1.0"
git commit -m "v2.0.0"
```

### 分支命名规范 🌿

```
feature/user-auth          # 新功能
fix/login-bug             # Bug 修复
hotfix/critical-security  # 紧急修复
release/v1.0.0            # 发布版本
```

### 工作流程 💼

**日常开发**：
```bash
# 1. 从 develop 创建功能分支
git checkout develop
git pull
git checkout -b feature/new-feature

# 2. 开发和提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到远程
git push origin feature/new-feature

# 4. 创建 Pull Request
# 在 GitHub/GitLab 上创建 PR，请求合并到 develop

# 5. 代码审查通过后合并
```

**紧急修复**：
```bash
# 1. 从 main 创建 hotfix 分支
git checkout main
git pull
git checkout -b hotfix/urgent-fix

# 2. 修复并提交
git add .
git commit -m "fix: 修复紧急问题"

# 3. 合并到 main 和 develop
git checkout main
git merge hotfix/urgent-fix
git push

git checkout develop
git merge hotfix/urgent-fix
git push

# 4. 删除 hotfix 分支
git branch -d hotfix/urgent-fix
```

### 版本号规范 🔢

**语义化版本**：`MAJOR.MINOR.PATCH`

- **MAJOR**：不兼容的 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的问题修正

**示例**：
- `v1.0.0`：第一个稳定版本
- `v1.0.1`：Bug 修复
- `v1.1.0`：新增功能
- `v2.0.0`：重大变更

---

## 技术文档维护 📚

### 为什么需要技术文档？

技术文档是项目的"记忆系统"，确保：
- ✅ 新成员快速了解项目
- ✅ 中断后能快速恢复上下文
- ✅ 避免重复踩坑
- ✅ 知识传承和积累
- ✅ 便于维护和扩展

### 文档体系结构

```
docs/
├── README.md                    # 项目总览（根目录）
├── CHANGELOG.md                 # 版本变更记录
├── 01-产品文档/
│   ├── 需求分析.md
│   ├── 功能规格.md
│   └── 用户手册.md
├── 02-技术文档/
│   ├── 架构设计.md
│   ├── 数据库设计.md
│   ├── API 文档.md
│   └── 部署指南.md
├── 03-开发文档/
│   ├── 开发环境搭建.md
│   ├── 代码规范.md
│   ├── 测试指南.md
│   └── 常见问题.md
├── 04-特性文档/               # 每个重要功能的文档
│   ├── 用户认证.md
│   ├── 数据分析.md
│   └── AI助手.md
├── 05-运维文档/
│   ├── 监控告警.md
│   ├── 备份恢复.md
│   └── 性能优化.md
└── 99-培训资料/
    ├── 新手入门.md
    └── 最佳实践.md
```

### 文档更新时机

#### 1. 功能开发完成后

**必须更新的文档**：
- [ ] API 文档（如果有 API 变更）
- [ ] 功能说明文档（docs/04-特性文档/）
- [ ] CHANGELOG.md
- [ ] README.md（如果影响用户使用）

**示例**：
```markdown
## 新增：狗狗年龄计算器

**版本**：v1.2.0  
**日期**：2026-05-10  
**作者**：[姓名]

### 功能概述

根据狗狗的品种和实际年龄，计算等效人类年龄。

### 技术实现

- **API 端点**：`POST /api/dogs/calculate-age`
- **核心算法**：不同品种有不同的 aging rate
- **数据来源**：breeds 表的 aging_rate 字段

### 使用示例

```bash
curl -X POST http://localhost:5000/api/dogs/calculate-age \
  -H "Content-Type: application/json" \
  -d '{"actual_age": 3, "breed": "金毛"}'
```

### 注意事项

- aging rate 数据来自兽医研究
- 目前支持 50+ 品种
- 计算结果仅供参考

### 相关文件

- `routes/dogs.py` - API 实现
- `Test/api_tests/test_age_calculator.py` - 测试用例
- `models_extended.py` - Breed 模型
```

#### 2. Bug 修复后

**必须记录**：
- [ ] Bug 描述和原因
- [ ] 解决方案
- [ ] 影响的范围
- [ ] 如何避免类似问题

**示例**：
```markdown
## Bug 修复：登录页面移动端显示问题

**版本**：v1.1.1  
**日期**：2026-05-10  
**优先级**：高

### 问题描述

登录页面在移动端（宽度 < 768px）时，表单溢出屏幕。

### 原因分析

CSS 中未设置响应式布局，固定宽度导致溢出。

### 解决方案

添加媒体查询，在小屏幕下调整布局：

```css
@media (max-width: 768px) {
    .login-container {
        padding: 10px;
        width: 100%;
    }
}
```

### 影响范围

- 仅影响登录页面
- 不影响其他功能

### 回归测试

已添加移动端响应式测试：
- `Test/ui_tests/test_login_responsive.py`

### 预防措施

- 所有新页面必须包含响应式设计
- 添加移动端测试用例
```

#### 3. 架构调整后

**必须更新**：
- [ ] 架构设计文档
- [ ] 数据库设计文档
- [ ] 部署指南
- [ ] 相关的技术决策记录

### 文档模板

#### 功能文档模板

```markdown
# [功能名称]

## 概述

简要描述功能用途和价值。

## 技术实现

### 架构设计

- 使用的技术栈
- 模块划分
- 数据流向

### 核心代码

关键代码片段和说明。

### 数据库设计

相关的表结构和关系。

## API 接口

### 请求示例

```bash
curl ...
```

### 响应格式

```json
{
  "success": true,
  "data": {}
}
```

## 测试

- 单元测试：[文件路径]
- 集成测试：[文件路径]
- 测试覆盖率：XX%

## 注意事项

- 性能考虑
- 安全考虑
- 已知限制

## 相关文档

- [链接到相关文档]

## 更新历史

- 2026-05-10: 初始版本
- 2026-05-11: 添加缓存优化
```

#### 技术决策记录（ADR）模板

```markdown
# ADR-[编号]: [决策标题]

**日期**：YYYY-MM-DD  
**状态**：已接受/已废弃/进行中  
**决策者**：[姓名]

## 背景

描述需要做出决策的背景和问题。

## 决策

明确说明做出的决策。

## 理由

### 优点

- 优点 1
- 优点 2

### 缺点

- 缺点 1
- 缺点 2

## 替代方案

### 方案 A

描述和评估。

### 方案 B

描述和评估。

## 影响

- 对现有代码的影响
- 对性能的影响
- 对维护的影响

## 参考

- 相关链接
- 相关文档
```

### AI 助手的文档责任

#### 1. 每次完成任务后

AI 必须主动询问：
```
✨ 功能已完成！

📝 是否需要更新技术文档？

建议更新：
- docs/04-特性文档/[功能名].md
- CHANGELOG.md
- API 文档（如有变更）

我可以帮您：
1. 创建功能文档草稿
2. 更新 CHANGELOG
3. 生成 API 文档

您希望我做什么？
```

#### 2. 文档内容要求

每份文档必须包含：
- ✅ 清晰的标题和概述
- ✅ 技术实现细节
- ✅ 代码示例
- ✅ 使用示例
- ✅ 注意事项
- ✅ 更新日期和作者

#### 3. 文档质量标准

- **准确性**：与实际代码一致
- **完整性**：覆盖所有关键点
- **可读性**：清晰易懂，有示例
- **及时性**：代码变更后立即更新
- **一致性**：格式和风格统一

### 文档维护检查清单

#### 每周检查

- [ ] 是否有未文档化的新功能？
- [ ] CHANGELOG 是否最新？
- [ ] API 文档是否与代码同步？
- [ ] 是否有过时的文档需要更新？

#### 每月检查

- [ ] 文档结构是否合理？
- [ ] 是否有缺失的文档？
- [ ] 文档链接是否有效？
- [ ] 是否需要整理归档？

#### 版本发布前

- [ ] 所有新功能已文档化
- [ ] CHANGELOG 完整准确
- [ ] API 文档已更新
- [ ] 部署指南已验证
- [ ] 已知问题已记录

### 文档最佳实践

✅ **应该做的**：
- 代码和文档一起提交
- 使用 Markdown 格式
- 包含实际代码示例
- 定期审查和更新
- 使用图表辅助说明

❌ **不应该做的**：
- 不要写"显而易见"的内容
- 不要复制粘贴代码而不解释
- 不要使用过时的截图
- 不要忽略文档更新
- 不要写冗长无重点的文档

---

## AI 助手交互规范 🤖

### 标准交互流程

当用户提出需求时，AI 应该：

1. **确认理解** ✅
   - 复述需求确保理解正确
   - 澄清模糊的地方
   - 确认关键细节

2. **提供方案** 💡
   - 给出 2-3 个可行方案
   - 分析各方案优缺点
   - 推荐最佳方案并说明理由
   - 等待用户确认

3. **遵循流程** 📋
   - 按照 TDD 流程执行
   - 先写测试，再实现代码
   - 每步完成后验证

4. **主动测试** 🧪
   - 完成代码后主动运行测试
   - 展示测试结果
   - 如有失败，立即修复

5. **总结反馈** 📝
   - 总结所做的更改
   - 列出修改的文件
   - 提示后续步骤

### 对话示例

#### 场景 1：新功能开发

**用户**：添加一个狗狗年龄计算器功能

**AI 响应**：
```
我理解您需要添加狗狗年龄计算器功能。让我确认一下：

📋 需求确认：
- 输入：狗狗的实际年龄（年）和品种
- 处理：根据品种计算等效人类年龄
- 输出：等效人类年龄
- 不同品种的 aging rate 不同

对吗？

💡 实现方案：

方案 A：后端 API + 前端界面
- 优点：逻辑集中在后端，易于维护
- 缺点：需要前后端配合

方案 B：纯前端 JavaScript 计算
- 优点：响应快，无需后端
- 缺点：逻辑分散，难以统一维护

✅ 推荐方案 A，因为：
1. 可以统一管理不同品种的 aging rate
2. 便于后续扩展（如添加更多计算方式）
3. 符合项目架构

您希望用哪个方案？

🔴 第一步：编写测试

我将先创建测试用例...
```

```python
# Test/api_tests/test_age_calculator.py
def test_calculate_dog_age_golden_retriever():
    """测试金毛的年龄计算"""
    response = client.post('/api/dogs/calculate-age', json={
        'actual_age': 3,
        'breed': '金毛'
    })
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'human_age' in data
    # 金毛第1年=15岁，第2年=9岁，之后每年=5岁
    assert data['human_age'] == 15 + 9 + 5

def test_calculate_dog_age_with_invalid_breed():
    """测试无效品种的处理"""
    response = client.post('/api/dogs/calculate-age', json={
        'actual_age': 3,
        'breed': '不存在的品种'
    })
    
    assert response.status_code == 400
    assert 'error' in response.get_json()
```

```
现在运行测试确认失败...

$ pytest Test/api_tests/test_age_calculator.py -v

结果：测试失败（功能未实现）✅

🟢 第二步：实现功能

现在编写后端 API...
```

```python
# routes/dogs.py
@app.route('/api/dogs/calculate-age', methods=['POST'])
def calculate_dog_age():
    data = request.get_json()
    actual_age = data.get('actual_age')
    breed = data.get('breed')
    
    if not actual_age or not breed:
        return jsonify({'error': '请提供年龄和品种'}), 400
    
    # 获取品种的 aging rate
    breed_info = Breed.query.filter_by(name=breed).first()
    if not breed_info:
        return jsonify({'error': f'未找到品种: {breed}'}), 400
    
    # 计算人类年龄
    human_age = calculate_human_age(actual_age, breed_info.aging_rate)
    
    return jsonify({
        'actual_age': actual_age,
        'breed': breed,
        'human_age': human_age
    })

def calculate_human_age(actual_age, aging_rate):
    """计算等效人类年龄"""
    if actual_age <= 0:
        return 0
    
    # 简化计算：第一年 15 岁，第二年 9 岁，之后每年按 aging_rate
    if actual_age == 1:
        return 15
    elif actual_age == 2:
        return 24
    else:
        return 24 + (actual_age - 2) * aging_rate
```

```
运行测试验证...

$ pytest Test/api_tests/test_age_calculator.py -v

结果：测试通过 ✅

🔵 第三步：重构优化

让我优化代码，添加缓存和参数验证...

[优化代码]

再次运行测试...

$ pytest Test/api_tests/test_age_calculator.py -v

结果：测试仍然通过 ✅

📊 第四步：补充测试

添加边界测试和异常测试...

[添加更多测试用例]

运行完整测试套件...

$ pytest Test/ -v --tb=short

结果：所有测试通过 ✅

✨ 功能已完成！

📝 总结：
- ✅ 创建了年龄计算 API
- ✅ 编写了 8 个测试用例
- ✅ 测试覆盖率 100%
- ✅ 代码已优化
- ✅ 文档已更新

📁 修改的文件：
- routes/dogs.py
- Test/api_tests/test_age_calculator.py
- docs/API.md

🚀 下一步：
- 可以添加前端界面
- 可以添加更多品种的 aging rate
```

#### 场景 2：Bug 修复

**用户**：登录页面在移动端显示不正常

**AI 响应**：
```
我理解登录页面在移动端显示有问题。让我先复现问题。

🐛 问题定位：

1. 检查当前登录页面的 CSS
2. 在不同屏幕尺寸下测试
3. 找出具体的布局问题

发现：登录表单在宽度 < 768px 时溢出屏幕

🔴 第一步：编写回归测试

先编写测试确保 Bug 修复后不会再次出现...
```

```python
# Test/ui_tests/test_login_responsive.py
def test_login_page_responsive_on_mobile(page):
    """测试登录页面在移动端的响应式布局"""
    page.goto('/login')
    
    # 设置为移动端视口
    page.set_viewport_size({"width": 375, "height": 667})
    
    # 检查登录表单是否完全可见
    form = page.locator('#login-form')
    form_box = form.bounding_box()
    viewport = page.viewport_size
    
    assert form_box['x'] >= 0
    assert form_box['y'] >= 0
    assert form_box['x'] + form_box['width'] <= viewport['width']
```

```
🟢 第二步：修复 CSS

现在修复响应式布局问题...
```

```css
/* static/css/login.css */
@media (max-width: 768px) {
    .login-container {
        padding: 10px;
        width: 100%;
    }
    
    .login-form {
        max-width: 100%;
        padding: 15px;
    }
}
```

```
🧪 第三步：验证修复

运行测试验证修复...

$ pytest Test/ui_tests/test_login_responsive.py -v

结果：测试通过 ✅

在浏览器中手动测试不同屏幕尺寸...
✅ 375px (iPhone) - 正常
✅ 768px (iPad) - 正常
✅ 1024px (Desktop) - 正常

✨ Bug 已修复！

📝 总结：
- ✅ 定位了响应式布局问题
- ✅ 编写了回归测试
- ✅ 修复了 CSS
- ✅ 验证了多种屏幕尺寸

📁 修改的文件：
- static/css/login.css
- Test/ui_tests/test_login_responsive.py
```

---

## 禁止行为 🚫

### 绝对禁止

❌ **不要跳过测试直接实现功能**
- 任何新功能必须先写测试
- 没有测试的代码不得合并

❌ **不要在没有测试的情况下重构代码**
- 重构前必须有充分的测试覆盖
- 重构后所有测试必须通过

❌ **不要提交无法通过测试的代码**
- 提交前必须运行相关测试
- CI/CD 测试失败不得合并

❌ **不要忽略测试失败的警告**
- 测试失败必须立即修复
- 不得使用 `@pytest.mark.skip` 绕过失败测试

❌ **不要在 main 分支直接提交代码**
- main 分支只能通过 PR 合并
- 所有代码必须经过审查

❌ **不要硬编码敏感信息**
- 密码、密钥、API Token 等必须放在 `.env`
- `.env` 文件不得提交到版本控制

❌ **不要写魔法数字**
```python
# ❌ 不好
if age > 18:
    pass

# ✅ 好
LEGAL_AGE = 18
if age > LEGAL_AGE:
    pass
```

❌ **不要使用裸 except**
```python
# ❌ 绝对禁止
try:
    do_something()
except:
    pass

# ✅ 正确
try:
    do_something()
except SpecificError as e:
    logger.error(f"错误: {e}")
    handle_error()
```

❌ **不要在生产环境开启 Debug 模式**
```python
# ❌ 危险
app.run(debug=True)

# ✅ 安全
app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
```

---

## 必须执行 ✅

### 强制要求

✅ **新功能必须包含测试用例**
- 单元测试至少覆盖核心逻辑
- API 测试覆盖所有接口
- 测试覆盖率 ≥ 80%

✅ **修改代码后必须运行相关测试**
- 修改后立即运行受影响测试
- 确保没有引入回归问题
- 测试通过才能提交

✅ **测试失败时必须先修复再提交**
- 不得提交有失败测试的代码
- 如无法立即修复，应 revert 更改
- 记录失败原因和修复计划

✅ **重要决策必须记录在文档中**
- 架构决策记录在 docs/
- API 变更更新 API 文档
- Bug 修复记录在 CHANGELOG

✅ **敏感信息不得硬编码在代码中**
- 使用环境变量或配置文件
- `.env` 文件加入 `.gitignore`
- 使用 `.env.example` 提供模板

✅ **代码必须符合 PEP 8 规范**
- 使用 linter 检查代码风格
- 保持一致的缩进和命名
- 行长度不超过 79 字符

✅ **函数必须有 Docstring**
- 描述函数用途
- 说明参数和返回值
- 列出可能的异常

✅ **PR 必须包含以下内容**
- 清晰的标题和描述
- 相关的测试用例
- 更新的文档
- 至少一个审查者

---

## 项目特定规则

### Flask 项目规范

- **路由定义**：放在 `routes/` 目录
- **模型定义**：放在 `models.py` 或 `models_extended.py`
- **工具函数**：放在 `utils/` 目录
- **静态资源**：放在 `static/` 目录
- **模板文件**：放在 `templates/` 目录
- **API 路由**：放在 `api/` 目录

### 测试规范

- **API 测试**：`Test/api_tests/`
- **UI 测试**：`Test/ui_tests/`
- **E2E 测试**：`Test/e2e_tests/`
- **单元测试**：`Test/` 根目录
- **测试框架**：pytest
- **测试标记**：清晰标注测试类型

### 数据库规范

- **ORM**：使用 SQLAlchemy
- **迁移脚本**：放在 `migrations/` 目录
- **种子数据**：放在 `scripts/` 目录
- **原始 SQL**：仅在特殊情况下使用，必须注释说明原因
- **查询优化**：避免 N+1 查询，使用 eager loading

### 前端规范

- **JavaScript**：使用 ES6+ 语法
- **CSS**：使用 Bootstrap 5
- **组件化**：使用 Alpine.js 或 Vue.js
- **响应式**：支持移动端适配
- **性能**：懒加载、代码分割

---

## 检查清单

### 提交前检查 ✅

- [ ] 所有测试通过
- [ ] 代码符合规范
- [ ] 无 lint 错误
- [ ] 文档已更新
- [ ] 无敏感信息泄露
- [ ] Commit message 清晰
- [ ] 已自测功能正常

### 代码审查检查 ✅

- [ ] 代码逻辑清晰
- [ ] 测试充分
- [ ] 无性能问题
- [ ] 无安全隐患
- [ ] 符合项目规范
- [ ] 文档完整

### 发布前检查 ✅

- [ ] 所有测试通过
- [ ] 版本号已更新
- [ ] CHANGELOG 已更新
- [ ] 文档已更新
- [ ] 部署脚本已测试
- [ ] 回滚方案已准备

---

## 附录

### 常用命令

```bash
# 运行所有测试
pytest Test/ -v

# 运行特定测试
pytest Test/test_feature.py -v

# 运行带标记的测试
pytest -m slow
pytest -m integration

# 检查测试覆盖率
pytest --cov=. --cov-report=html

# 运行 lint
flake8 .
pylint .

# 格式化代码
black .
isort .

# 启动开发服务器
flask run

# 初始化数据库
python init_db.py
```

### 参考资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [pytest 官方文档](https://docs.pytest.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PEP 8 风格指南](https://peps.python.org/pep-0008/)
- [语义化版本](https://semver.org/)

---

**文档维护**：本规范由项目团队共同维护，欢迎提出改进建议。
