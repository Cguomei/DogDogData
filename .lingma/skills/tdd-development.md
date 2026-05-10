---
name: tdd-development
description: 测试驱动开发（TDD）工作流程，确保代码质量和测试覆盖率
version: 1.0.0
tags: [testing, tdd, quality, workflow]
---

# 测试驱动开发（TDD）工作流程

## 何时使用

- 开发新功能时
- 修复 Bug 时
- 重构现有代码时
- 用户明确要求遵循 TDD 流程时

## 核心原则

**红-绿-重构循环**：
1. 🔴 **Red（红）**：编写失败的测试
2. 🟢 **Green（绿）**：编写最少的代码使测试通过
3. 🔵 **Refactor（重构）**：优化代码，保持测试通过

## 执行步骤

### 步骤 1：理解需求并设计测试

当用户提出需求时：

1. **确认需求理解**
   ```
   "我理解您需要[功能描述]。让我确认一下关键点：
   - 输入：...
   - 处理：...
   - 输出：...
   
   对吗？"
   ```

2. **设计测试用例**
   - 正常场景测试
   - 边界条件测试
   - 异常情况测试
   - 性能测试（如需要）

### 步骤 2：编写测试（Red 阶段）

1. **创建测试文件**（如果不存在）
   - API 测试：`Test/api_tests/test_[feature].py`
   - UI 测试：`Test/ui_tests/test_[feature].py`
   - 单元测试：`Test/test_[feature].py`

2. **编写测试代码**
   ```python
   def test_feature_name():
       # Arrange（准备）
       # Act（执行）
       # Assert（断言）
   ```

3. **运行测试确认失败**
   ```bash
   pytest Test/test_[feature].py -v
   ```
   预期结果：测试失败（因为功能还未实现）

### 步骤 3：实现功能（Green 阶段）

1. **编写最少的代码使测试通过**
   - 不要过度设计
   - 只实现让测试通过的代码
   - 可以硬编码返回值（后续再优化）

2. **运行测试验证**
   ```bash
   pytest Test/test_[feature].py -v
   ```
   预期结果：所有测试通过 ✅

### 步骤 4：重构优化（Refactor 阶段）

1. **优化代码结构**
   - 提取重复代码
   - 改进命名
   - 简化逻辑
   - 添加注释

2. **确保测试仍然通过**
   ```bash
   pytest Test/test_[feature].py -v
   ```

3. **检查代码质量**
   - 运行 lint 工具
   - 检查复杂度
   - 审查可读性

### 步骤 5：补充测试

1. **添加边界测试**
2. **添加异常测试**
3. **添加集成测试**
4. **运行完整测试套件**
   ```bash
   pytest Test/ -v --tb=short
   ```

## 示例对话

### 场景：用户要求添加狗狗搜索功能

**用户**：添加一个按品种搜索狗狗的功能

**AI 响应**：

```
我理解您需要添加按品种搜索狗狗的功能。让我确认一下：
- 用户可以通过品种名称搜索
- 支持模糊匹配
- 返回匹配的狗狗列表
- 如果没有匹配结果，返回空列表

对吗？

我将按照 TDD 流程实现：

**第一步：编写测试**

让我先创建测试用例...
```

```python
# Test/api_tests/test_dog_search.py
def test_search_by_breed():
    """测试按品种搜索狗狗"""
    # Arrange
    client = app.test_client()
    
    # Act
    response = client.get('/api/dogs/search?breed=金毛')
    data = response.get_json()
    
    # Assert
    assert response.status_code == 200
    assert 'dogs' in data
    assert len(data['dogs']) > 0
    assert all(dog['breed'] == '金毛' for dog in data['dogs'])

def test_search_no_results():
    """测试搜索无结果的情况"""
    # Arrange
    client = app.test_client()
    
    # Act
    response = client.get('/api/dogs/search?breed=不存在的品种')
    data = response.get_json()
    
    # Assert
    assert response.status_code == 200
    assert len(data['dogs']) == 0
```

```
现在运行测试确认失败...

$ pytest Test/api_tests/test_dog_search.py -v

预期结果：测试失败（功能未实现）✅

**第二步：实现功能**

现在编写后端 API...
```

```python
# routes/dogs.py
@app.route('/api/dogs/search')
def search_dogs():
    breed = request.args.get('breed', '')
    
    if not breed:
        return jsonify({'error': '请提供品种名称'}), 400
    
    dogs = Dog.query.filter(Dog.breed.like(f'%{breed}%')).all()
    
    return jsonify({
        'dogs': [dog.to_dict() for dog in dogs]
    })
```

```
运行测试验证...

$ pytest Test/api_tests/test_dog_search.py -v

结果：测试通过 ✅

**第三步：重构优化**

让我优化代码，添加参数验证和错误处理...

[优化代码]

再次运行测试...

$ pytest Test/api_tests/test_dog_search.py -v

结果：测试仍然通过 ✅

**第四步：补充测试**

添加更多边界测试...

[添加测试用例]

运行完整测试套件...

$ pytest Test/ -v --tb=short

结果：所有测试通过 ✅

功能已完成！总结：
- ✅ 创建了搜索 API
- ✅ 编写了 5 个测试用例
- ✅ 测试覆盖率 100%
- ✅ 代码已优化
```

## 注意事项

### ✅ 应该做的

- 始终先写测试
- 保持测试简单清晰
- 测试命名要有意义
- 覆盖边界情况
- 运行测试后再提交代码

### ❌ 不应该做的

- 不要跳过测试直接写代码
- 不要写过于复杂的测试
- 不要忽略失败的测试
- 不要在测试中使用魔法数字
- 不要提交未通过测试的代码

## 常见问题

### Q: 测试太难写了怎么办？

A: 从简单的测试开始，先测试主要流程，再逐步添加边界测试。

### Q: 重构后测试失败了怎么办？

A: 检查重构是否改变了功能行为。如果是意外改变，修复代码；如果是预期的，更新测试。

### Q: 什么时候可以不遵循 TDD？

A: 
- 快速原型验证
- 一次性脚本
- 探索性编程

但在正式项目中，强烈建议始终遵循 TDD。

## 相关资源

- pytest 文档：https://docs.pytest.org/
- TDD 最佳实践
- 项目测试规范：`.lingma/rules/project-management.md`
