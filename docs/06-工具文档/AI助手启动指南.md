# AI智能助手 - 快速启动指南

## 📋 已完成的工作

✅ **后端代码**
- `routes/ai_assistant.py` - AI助手路由模块
- 支持Ollama和LM Studio本地模型
- 5种问题类型处理（价格查询、品种信息、推荐、对比、通用问答）
- 数据库集成查询

✅ **前端页面**
- `templates/ai_chat.html` - 聊天界面
- 响应式设计
- 快捷问题按钮
- 模型状态显示

✅ **配置**
- `.env` - 添加AI助手配置
- `app.py` - 注册AI蓝图

✅ **测试工具**
- `test_ai_assistant.py` - 自动化测试脚本

---

## 🚀 启动步骤

### Step 1: 确保本地模型已启动

#### 如果使用 Ollama：

```bash
# 1. 启动Ollama服务
ollama serve

# 2. 下载并运行模型（在另一个终端）
ollama run qwen2.5:7b

# 或者使用其他模型
ollama run llama3.2:3b
ollama run chatglm4:9b
```

**验证Ollama是否运行：**
```bash
curl http://localhost:11434/api/tags
```

#### 如果使用 LM Studio：

1. 打开LM Studio
2. 加载一个模型
3. 启动Local Server（默认端口1234）

**验证LM Studio是否运行：**
```bash
curl http://localhost:1234/v1/models
```

---

### Step 2: 配置环境变量

编辑 `.env` 文件，确认以下配置：

```env
# AI助手配置（本地模型）
MODEL_TYPE=ollama  # 或 lmstudio
LOCAL_MODEL_URL=http://localhost:11434  # Ollama默认地址
LOCAL_MODEL_NAME=qwen2.5:7b  # 你使用的模型名称
```

**重要**：`LOCAL_MODEL_NAME` 必须与你实际运行的模型名称一致！

查看Ollama已安装的模型：
```bash
ollama list
```

---

### Step 3: 启动Flask应用

```bash
# 在项目根目录
python app.py
```

看到以下输出表示成功：
```
 * Running on http://127.0.0.1:5000
```

---

### Step 4: 访问AI助手

浏览器打开：
```
http://localhost:5000/ai-chat
```

**需要先登录！**
- 用户名：admin
- 密码：admin123

---

## 🧪 测试

### 方法1：使用测试脚本

```bash
python test_ai_assistant.py
```

这会自动：
1. 登录系统
2. 检查模型状态
3. 发送3个测试问题
4. 显示回复结果

### 方法2：手动测试

1. 访问 http://localhost:5000/ai-chat
2. 登录后
3. 尝试以下问题：
   - "金毛的价格是多少？"
   - "泰迪有什么特点？"
   - "适合新手养的狗狗"
   - "金毛和泰迪对比"

---

## 🔧 常见问题

### Q1: 提示"无法连接到本地模型服务"

**原因**：Ollama/LM Studio未启动

**解决**：
```bash
# Ollama
ollama serve

# 或在后台运行
ollama serve &
```

### Q2: 模型响应很慢

**原因**：
- 模型太大
- CPU运行（无GPU加速）
- 首次加载需要时间

**解决**：
- 使用较小的模型（如qwen2.5:1.5b）
- 等待首次加载完成
- 考虑使用GPU加速

### Q3: 回复质量不好

**原因**：小模型能力有限

**解决**：
- 尝试更大的模型（7b或以上）
- 优化prompt
- 切换到更强大的模型

### Q4: 中文回复乱码

**原因**：模型不支持中文

**解决**：
- 使用支持中文的模型：
  - qwen2.5系列 ✅
  - chatglm4 ✅
  - yi系列 ✅
  - llama3（中文较弱）⚠️

---

## 📊 支持的模型推荐

### Ollama模型

| 模型 | 大小 | 中文支持 | 速度 | 推荐度 |
|------|------|---------|------|--------|
| qwen2.5:1.5b | 1GB | ✅ 优秀 | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| qwen2.5:7b | 4GB | ✅ 优秀 | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| chatglm4:9b | 6GB | ✅ 优秀 | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| llama3.2:3b | 2GB | ⚠️ 一般 | ⚡⚡⚡ | ⭐⭐⭐ |
| yi:6b | 4GB | ✅ 良好 | ⚡⚡ | ⭐⭐⭐⭐ |

### 安装模型示例

```bash
# 推荐：通义千问2.5（7B版本）
ollama pull qwen2.5:7b

# 轻量级：通义千问2.5（1.5B版本）
ollama pull qwen2.5:1.5b

# 智谱GLM4
ollama pull chatglm4:9b
```

---

## 🎯 下一步开发计划

### Day 1 下午任务（今天）
- [x] 创建后端路由
- [x] 创建前端页面
- [x] 配置环境变量
- [ ] **测试基本功能** ← 你现在在这里
- [ ] 修复发现的问题

### Day 2 任务
- [ ] 优化问题分类器
- [ ] 添加更多数据查询
- [ ] 改进回复格式
- [ ] 添加错误处理

### Day 3 任务
- [ ] 编写单元测试
- [ ] 性能优化
- [ ] 用户体验改进

### Day 4 任务
- [ ] 文档完善
- [ ] 部署准备
- [ ] 上线检查

---

## 💡 使用技巧

### 1. 提高响应速度

```env
# .env 中使用小模型
LOCAL_MODEL_NAME=qwen2.5:1.5b
```

### 2. 改善回复质量

```env
# .env 中使用大模型
LOCAL_MODEL_NAME=qwen2.5:7b
```

### 3. 调试模式

在 `routes/ai_assistant.py` 中添加日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. 自定义快捷问题

编辑 `templates/ai_chat.html`，修改这部分：

```html
<button class="quick-btn" onclick="sendQuickQuestion('你的问题')">按钮文字</button>
```

---

## 📞 需要帮助？

如果遇到问题：

1. 检查Ollama是否运行：`curl http://localhost:11434/api/tags`
2. 查看Flask日志输出
3. 运行测试脚本：`python test_ai_assistant.py`
4. 检查浏览器控制台错误

---

**祝你使用愉快！** 🎉
