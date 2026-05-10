# AI智能助手 - 数据获取与开发计划

## 文档信息

| 项目 | 值 |
|------|-----|
| **版本** | v1.0 |
| **创建日期** | 2026-05-09 |
| **目标** | 明确数据来源 + 4天开发计划 |

---

## 一、数据现状分析

### 1.1 现有数据库表

根据代码分析，当前系统已有以下核心表：

```sql
-- 1. users (用户表) ✅ 已有
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. dog_breeds (品种表) ✅ 已有
CREATE TABLE dog_breeds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    breed_name VARCHAR(100) UNIQUE NOT NULL,
    avg_life_years DECIMAL(3,1),
    size_category ENUM('小型', '中型', '大型', '超大型'),
    popularity INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. jd_dogs (狗狗数据表) ✅ 已有（核心数据源）
-- 包含字段（从charts.py推断）：
-- - dog_name: 品种名
-- - price: 价格
-- - size: 体型（小型犬/中型犬/大型犬）
-- - shop_name: 店铺名
-- - location: 地区
-- - pet_level: 宠物级/血统级
-- - blood_level: 血统等级
-- - weight: 体重
-- - created_at: 创建时间

-- 4. dog_wykl (狗粮数据表) ✅ 已有
-- 包含字段：
-- - brand: 品牌
-- - product_name: 产品名
-- - price: 价格
-- - origin: 产地

-- 5. dashboard_summary (汇总数据表) ✅ 已有
CREATE TABLE dashboard_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_key VARCHAR(100) UNIQUE NOT NULL,
    stat_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 1.2 数据量评估

```python
# 从测试代码推断的数据量
估计数据量：
- jd_dogs: 1000-5000条记录
- dog_breeds: 50-100个品种
- dog_wykl: 200-500条狗粮记录
- users: 10-50个用户（测试环境）
```

---

## 二、AI助手需要的数据

### 2.1 必需数据清单

| 数据类型 | 来源表 | 用途 | 是否已有 |
|---------|--------|------|---------|
| **品种价格** | jd_dogs | 回答"XX多少钱" | ✅ 已有 |
| **品种信息** | dog_breeds | 回答"XX特点" | ✅ 已有 |
| **品种列表** | dog_breeds | 推荐功能 | ✅ 已有 |
| **体型分类** | dog_breeds/jd_dogs | 筛选推荐 | ✅ 已有 |
| **寿命数据** | dog_breeds | 养护建议 | ✅ 已有 |
| **人气指数** | dog_breeds | 热门排行 | ✅ 已有 |
| **地域分布** | jd_dogs | 地区价格差异 | ✅ 已有 |
| **店铺信息** | jd_dogs | 购买渠道 | ✅ 已有 |

### 2.2 缺失数据（可选增强）

| 数据类型 | 用途 | 优先级 | 获取方式 |
|---------|------|--------|---------|
| 养护知识 | 回答"怎么养" | P1 | OpenAI生成 |
| 训练技巧 | 回答"怎么训练" | P2 | OpenAI生成 |
| 疾病信息 | 健康咨询 | P2 | OpenAI生成 |
| 用户偏好 | 个性化推荐 | P3 | 后续收集 |

**结论**：✅ **MVP阶段不需要额外数据！** 现有数据库完全够用。

---

## 三、数据获取方案

### 方案A：直接使用现有数据（✅ 推荐）

**优点**：
- ✅ 零成本
- ✅ 立即可用
- ✅ 无需爬虫
- ✅ 数据质量可控

**实现**：
```python
# 直接从MySQL查询
def get_breed_price(breed_name):
    sql = """
        SELECT AVG(price), MIN(price), MAX(price), COUNT(*)
        FROM jd_dogs
        WHERE dog_name LIKE %s
    """
    return db.session.execute(sql, [f'%{breed_name}%'])
```

---

### 方案B：补充公开数据（可选）

如果需要更丰富的知识库，可以：

#### B1. 爬取宠物网站数据

```python
"""
简单爬虫示例（仅用于学习）
目标：百度百科-狗狗品种介绍
"""
import requests
from bs4 import BeautifulSoup

def crawl_breed_info(breed_name):
    """爬取品种介绍"""
    url = f"https://baike.baidu.com/item/{breed_name}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取简介
    intro = soup.find('div', class_='lemma-summary')
    if intro:
        return intro.get_text().strip()
    
    return None

# 使用示例
info = crawl_breed_info('金毛寻回犬')
print(info)
```

**注意**：
- ⚠️ 遵守robots.txt
- ⚠️ 控制爬取频率
- ⚠️ 仅用于个人学习

#### B2. 使用开放API

```python
"""
调用第三方宠物API（如果有）
示例：聚合数据、阿里云市场等
"""
import requests

def get_breed_from_api(breed_name):
    """从API获取品种信息"""
    api_url = "https://api.example.com/pet/breed"
    params = {
        'key': 'your_api_key',
        'name': breed_name
    }
    
    response = requests.get(api_url, params=params)
    return response.json()
```

---

### 方案C：人工录入知识库（推荐用于专业知识）

创建一个简单的JSON文件存储养护知识：

```json
// data/pet_knowledge.json
{
  "金毛": {
    "性格": "温顺友善，聪明忠诚",
    "运动需求": "每天至少1小时户外活动",
    "饮食建议": "优质狗粮+适量肉类，避免过量",
    "常见问题": ["掉毛较多", "需要定期梳毛", "易肥胖"],
    "训练难度": "容易训练，智商排名第4"
  },
  "泰迪": {
    "性格": "活泼聪明，粘人",
    "运动需求": "每天30分钟即可",
    "饮食建议": "小型犬专用粮，注意牙齿健康",
    "常见问题": ["需要定期美容", "易有泪痕", "叫声较大"],
    "训练难度": "非常聪明，易于训练"
  }
}
```

加载方式：
```python
import json

def load_knowledge_base():
    with open('data/pet_knowledge.json', 'r', encoding='utf-8') as f:
        return json.load(f)

knowledge = load_knowledge_base()
print(knowledge['金毛']['性格'])
```

---

## 四、4天开发计划

### 📅 Day 1：后端基础（8小时）

#### 上午（4小时）：环境准备 + 路由搭建

**任务清单**：
- [ ] 安装OpenAI SDK
- [ ] 配置环境变量（API Key）
- [ ] 创建 `routes/ai_assistant.py`
- [ ] 注册蓝图到 `app.py`
- [ ] 编写问题分类器（基于规则）

**代码实现**：

```bash
# Step 1: 安装依赖
pip install openai==0.28.0

# Step 2: 配置.env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

```python
# routes/ai_assistant.py（基础框架）
from flask import Blueprint, request, jsonify
from flask_login import login_required
import openai
import os

ai_bp = Blueprint('ai_assistant', __name__)

# 配置API
openai.api_key = os.getenv('OPENAI_API_KEY')

@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI聊天接口"""
    data = request.get_json()
    message = data.get('message', '')
    
    # TODO: 实现问题分类和处理
    
    return jsonify({
        'success': True,
        'answer': 'Hello World'
    })

@ai_bp.route('/ai-chat')
@login_required
def ai_chat_page():
    """聊天页面"""
    from flask import render_template
    return render_template('ai_chat.html')
```

```python
# app.py 中添加
from routes.ai_assistant import ai_bp
app.register_blueprint(ai_bp)
```

#### 下午（4小时）：数据查询处理器

**任务清单**：
- [ ] 实现价格查询函数
- [ ] 实现品种信息查询
- [ ] 实现推荐功能
- [ ] 实现对比功能
- [ ] 单元测试

**代码实现**：

```python
# routes/ai_assistant.py 续

def classify_question(question):
    """问题分类器"""
    # 见MVP文档中的完整实现
    pass

def handle_price_query(params):
    """处理价格查询"""
    breed = params.get('breed')
    
    sql = text("""
        SELECT AVG(price), MIN(price), MAX(price), COUNT(*)
        FROM jd_dogs d
        JOIN dog_breeds b ON d.breed_name = b.breed_name
        WHERE b.breed_name LIKE :breed
    """)
    
    result = db.session.execute(sql, {'breed': f'%{breed}%'}).fetchone()
    
    if not result or result[3] == 0:
        return f"抱歉，没有找到'{breed}'的价格数据"
    
    return f"""📊 **{breed}价格信息**

• 平均价格：¥{result[0]:.0f}
• 最低价格：¥{result[1]:.0f}
• 最高价格：¥{result[2]:.0f}
• 数据条数：{result[3]}条

💡 价格会因地区、血统等因素有所差异。"""

def handle_recommendation(params):
    """处理推荐问题"""
    prompt = "你是宠物顾问，请推荐3-5个适合新手的犬种..."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是宠物专家"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content

# ... 其他处理器
```

**测试**：
```bash
# 启动应用
python app.py

# 访问测试
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "金毛的价格是多少？"}'
```

---

### 📅 Day 2：前端界面（8小时）

#### 上午（4小时）：HTML页面搭建

**任务清单**：
- [ ] 创建 `templates/ai_chat.html`
- [ ] 设计聊天界面布局
- [ ] 实现消息气泡样式
- [ ] 添加快捷问题按钮

**代码实现**：
复制MVP文档中的完整HTML代码（已提供）

#### 下午（4小时）：JavaScript交互

**任务清单**：
- [ ] 实现消息发送功能
- [ ] 实现API调用
- [ ] 添加Loading动画
- [ ] 实现Markdown渲染
- [ ] 响应式优化

**关键代码**：
```javascript
// 已在HTML中内联实现
async function sendMessage() {
    const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: userInput})
    });
    
    const data = await response.json();
    displayMessage(data.answer, 'ai');
}
```

**测试**：
- 浏览器访问 `http://localhost:5000/ai-chat`
- 测试发送消息
- 测试快捷按钮
- 检查移动端显示

---

### 📅 Day 3：功能完善（8小时）

#### 上午（4小时）：错误处理 + 优化

**任务清单**：
- [ ] 添加输入验证
- [ ] 添加错误提示
- [ ] 优化响应格式
- [ ] 添加日志记录
- [ ] 性能优化

**代码实现**：

```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    try:
        data = request.get_json()
        
        # 输入验证
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400
        
        message = data['message'].strip()
        
        if len(message) > 1000:
            return jsonify({
                'success': False,
                'error': '消息过长（最多1000字符）'
            }), 400
        
        logger.info(f"收到用户消息: {message[:50]}...")
        
        # 处理逻辑...
        
    except Exception as e:
        logger.error(f"AI聊天错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
```

#### 下午（4小时）：测试用例编写

**任务清单**：
- [ ] 编写单元测试
- [ ] 测试5种问题类型
- [ ] 边界条件测试
- [ ] 性能测试
- [ ] 修复Bug

**测试代码**：

```python
# Test/test_ai_assistant.py
import pytest
from app import create_app
from models import db, User

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture
def logged_in_client(client):
    # 登录测试用户
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    return client

class TestAIAssistant:
    """AI助手测试类"""
    
    def test_price_query(self, logged_in_client):
        """测试价格查询"""
        response = logged_in_client.post('/api/ai/chat', json={
            'message': '金毛的价格是多少？'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert '价格' in data['answer']
    
    def test_recommendation(self, logged_in_client):
        """测试推荐功能"""
        response = logged_in_client.post('/api/ai/chat', json={
            'message': '适合新手养的狗狗'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert len(data['answer']) > 50
    
    def test_empty_message(self, logged_in_client):
        """测试空消息"""
        response = logged_in_client.post('/api/ai/chat', json={
            'message': ''
        })
        
        assert response.status_code == 400
    
    def test_unauthorized(self, client):
        """测试未登录访问"""
        response = client.post('/api/ai/chat', json={
            'message': '测试'
        })
        
        assert response.status_code == 401  # 或302重定向
```

运行测试：
```bash
pytest Test/test_ai_assistant.py -v
```

---

### 📅 Day 4：部署准备（8小时）

#### 上午（4小时）：文档 + 配置

**任务清单**：
- [ ] 编写使用说明
- [ ] 更新README
- [ ] 配置生产环境
- [ ] 设置监控
- [ ] 备份策略

**文档编写**：

```markdown
# AI智能助手使用说明

## 快速开始

1. 确保已配置OpenAI API Key
2. 访问 http://your-domain/ai-chat
3. 输入问题或点击快捷按钮

## 支持的问题类型

1. 价格查询："金毛多少钱？"
2. 品种介绍："泰迪有什么特点？"
3. 推荐建议："适合新手的狗狗"
4. 品种对比："金毛和泰迪对比"
5. 通用问答："怎么训练狗狗？"

## 注意事项

- 需要登录才能使用
- 每小时最多100次请求
- 单次消息不超过1000字符
```

#### 下午（4小时）：上线前检查

**任务清单**：
- [ ] 安全审计
- [ ] 性能测试
- [ ] 压力测试
- [ ] 灰度发布
- [ ] 收集反馈

**检查清单**：

```python
# scripts/check_ai_ready.py
"""
AI助手上线前检查脚本
"""
import os
import sys

def check_environment():
    """检查环境配置"""
    checks = []
    
    # 1. API Key配置
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        checks.append(("✅ OpenAI API Key", "已配置"))
    else:
        checks.append(("❌ OpenAI API Key", "未配置或格式错误"))
    
    # 2. 数据库连接
    try:
        from models import db
        db.session.execute("SELECT 1")
        checks.append(("✅ 数据库连接", "正常"))
    except:
        checks.append(("❌ 数据库连接", "失败"))
    
    # 3. 路由注册
    from app import create_app
    app = create_app()
    if 'ai_assistant' in app.blueprints:
        checks.append(("✅ AI蓝图注册", "成功"))
    else:
        checks.append(("❌ AI蓝图注册", "失败"))
    
    # 打印结果
    print("\n=== AI助手上线前检查 ===\n")
    for item, status in checks:
        print(f"{item}: {status}")
    
    # 判断是否通过
    all_passed = all("✅" in item for item, _ in checks)
    
    if all_passed:
        print("\n🎉 所有检查通过，可以上线！")
        return 0
    else:
        print("\n⚠️ 存在未通过项，请修复后重试")
        return 1

if __name__ == '__main__':
    sys.exit(check_environment())
```

运行检查：
```bash
python scripts/check_ai_ready.py
```

---

## 五、验收标准

### 功能验收

| 测试项 | 预期结果 | 状态 |
|--------|---------|------|
| 价格查询 | 返回准确价格数据 | ☐ |
| 品种介绍 | 返回品种详细信息 | ☐ |
| 推荐功能 | 返回3-5个推荐品种 | ☐ |
| 品种对比 | 返回对比表格 | ☐ |
| 通用问答 | AI正常回答 | ☐ |
| 错误处理 | 友好错误提示 | ☐ |
| 移动端适配 | 正常显示和操作 | ☐ |

### 性能验收

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| 响应时间（P95） | < 3秒 | ☐ |
| 并发用户 | 50人 | ☐ |
| API成功率 | > 99% | ☐ |
| 页面加载时间 | < 2秒 | ☐ |

### 代码质量

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 单元测试覆盖率 | > 70% | ☐ |
| 代码规范 | PEP8 | ☐ |
| 无高危漏洞 | 安全扫描通过 | ☐ |
| 文档完整 | README + 注释 | ☐ |

---

## 六、风险控制

### 潜在风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| OpenAI API不可用 | 低 | 高 | 备用API Key、降级为固定回复 |
| 数据库查询慢 | 中 | 中 | 添加索引、查询缓存 |
| 并发过高 | 低 | 中 | 限流、队列处理 |
| API费用超支 | 中 | 中 | 设置预算告警、用量监控 |
| 用户滥用 | 低 | 低 | IP限流、频率控制 |

### 应急预案

```python
# 降级策略
def ai_chat_fallback(message):
    """当OpenAI不可用时的降级方案"""
    
    fallback_responses = {
        '价格': '抱歉，暂时无法查询价格，请稍后重试',
        '推荐': '建议您考虑金毛、泰迪、柯基等常见品种',
        'default': '抱歉，服务暂时不可用，请稍后重试'
    }
    
    for keyword, response in fallback_responses.items():
        if keyword in message:
            return response
    
    return fallback_responses['default']
```

---

## 七、后续迭代计划

### Phase 2（1个月后）

- [ ] 多轮对话上下文
- [ ] 图表联动展示
- [ ] 用户历史记录
- [ ] 常见问题缓存
- [ ] 用户反馈系统

### Phase 3（3个月后）

- [ ] RAG知识库
- [ ] 意图识别优化（ML模型）
- [ ] 个性化推荐算法
- [ ] 报告生成功能
- [ ] 语音交互

### Phase 4（6个月后）

- [ ] 实时流式输出
- [ ] 多语言支持
- [ ] 移动端APP
- [ ] 开放API平台
- [ ] 商业化订阅

---

## 八、资源清单

### 人力资源

| 角色 | 投入时间 | 职责 |
|------|---------|------|
| 后端开发 | 2天 | API开发、数据处理 |
| 前端开发 | 1天 | 页面开发、交互实现 |
| 测试工程师 | 0.5天 | 测试用例、Bug修复 |
| 产品经理 | 0.5天 | 需求确认、验收测试 |

### 技术资源

| 资源 | 规格 | 费用 |
|------|------|------|
| OpenAI API | GPT-3.5-turbo | ¥500-2000/月 |
| 服务器 | 现有Flask服务器 | ¥0 |
| 数据库 | 现有MySQL | ¥0 |
| 域名 | 现有域名 | ¥0 |

### 时间资源

```
总工期：4个工作日
├── Day 1: 后端基础（8h）
├── Day 2: 前端界面（8h）
├── Day 3: 功能完善（8h）
└── Day 4: 部署准备（8h）
```

---

## 九、总结

### 核心优势

✅ **数据现成**：无需爬取，直接用现有数据库  
✅ **开发快速**：4天完成MVP  
✅ **成本低廉**：仅需OpenAI API费用  
✅ **可扩展**：后续可逐步升级  

### 关键成功因素

1. **复用现有数据**：jd_dogs + dog_breeds表完全够用
2. **简化技术栈**：Flask + 原生JS，无需学习新框架
3. **快速迭代**：先上线再优化，收集真实反馈
4. **成本控制**：使用GPT-3.5-turbo，设置预算限制

### 下一步行动

1. ✅ 申请OpenAI API Key
2. ✅ 按照4天计划执行
3. ✅ 第4天结束时进行验收
4. ✅ 收集首批用户反馈
5. ✅ 决定是否继续投入Phase 2

---

**准备好了吗？让我们开始吧！** 🚀
