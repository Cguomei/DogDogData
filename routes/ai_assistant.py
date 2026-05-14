"""
AI智能助手路由模块
支持本地模型（Ollama/LM Studio等）+ 本地知识库
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db
from sqlalchemy import text
import requests
import json
import os
import logging
from datetime import datetime

# 导入知识库
from utils.knowledge_base import get_knowledge_base

# 导入对话历史模型
from models_extended import ChatSession, ChatMessage

# 导入图表模块
import charts

# 配置日志
logger = logging.getLogger('ai_assistant')
logger.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler('log/ai_assistant.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建格式化器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# 添加处理器到logger
if not logger.handlers:
    logger.addHandler(file_handler)

ai_bp = Blueprint('ai_assistant', __name__)

# ===== 本地模型配置 =====
LOCAL_MODEL_CONFIG = {
    # Ollama 配置
    'ollama': {
        'base_url': os.getenv('LOCAL_MODEL_URL', 'http://localhost:11434'),
        'model': os.getenv('LOCAL_MODEL_NAME', 'qwen2.5:1.5b'),  # 默认使用 qwen2.5:1.5b
        'api_endpoint': '/api/chat'
    },
    # LM Studio 配置
    'lmstudio': {
        'base_url': os.getenv('LOCAL_MODEL_URL', 'http://localhost:1234'),
        'model': os.getenv('LOCAL_MODEL_NAME', 'local-model'),
        'api_endpoint': '/v1/chat/completions'
    }
}

# 当前使用的模型类型（可在.env中配置）
MODEL_TYPE = os.getenv('MODEL_TYPE', 'ollama')  # 'ollama' 或 'lmstudio'


def call_local_model(messages: list, temperature: float = 0.7) -> str:
    """
    调用本地模型
    
    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        temperature: 温度参数
    
    Returns:
        模型回复文本
    """
    config = LOCAL_MODEL_CONFIG.get(MODEL_TYPE)
    if not config:
        logger.error(f"不支持的模型类型: {MODEL_TYPE}")
        raise ValueError(f"不支持的模型类型: {MODEL_TYPE}")
    
    base_url = config['base_url']
    model = config['model']
    endpoint = config['api_endpoint']
    
    logger.info(f"调用本地模型: {MODEL_TYPE}, 模型: {model}")
    logger.info(f"API地址: {base_url}{endpoint}")
    
    try:
        if MODEL_TYPE == 'ollama':
            # Ollama API
            url = f"{base_url}{endpoint}"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "temperature": temperature
            }
            
            logger.debug(f"Ollama请求payload: {json.dumps(payload, ensure_ascii=False)[:500]}...")
            
            response = requests.post(url, json=payload, timeout=30)
            logger.info(f"Ollama响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Ollama返回错误: {response.status_code}")
                logger.error(f"响应内容: {response.text[:500]}")
                return f"❌ 模型调用失败 (HTTP {response.status_code})"
            
            result = response.json()
            logger.debug(f"Ollama响应: {json.dumps(result, ensure_ascii=False)[:500]}...")
            
            content = result.get('message', {}).get('content', '')
            logger.info(f"Ollama回复长度: {len(content)}字符")
            return content
        
        elif MODEL_TYPE == 'lmstudio':
            # LM Studio API (OpenAI兼容)
            url = f"{base_url}{endpoint}"
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1000
            }
            
            logger.debug(f"LM Studio请求payload: {json.dumps(payload, ensure_ascii=False)[:500]}...")
            
            response = requests.post(url, json=payload, timeout=30)
            logger.info(f"LM Studio响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"LM Studio返回错误: {response.status_code}")
                logger.error(f"响应内容: {response.text[:500]}")
                return f"❌ 模型调用失败 (HTTP {response.status_code})"
            
            result = response.json()
            logger.debug(f"LM Studio响应: {json.dumps(result, ensure_ascii=False)[:500]}...")
            
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.info(f"LM Studio回复长度: {len(content)}字符")
            return content
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"无法连接到模型服务: {base_url}")
        logger.error(f"错误详情: {str(e)}")
        return "❌ 无法连接到本地模型服务，请确保模型已启动"
    except requests.exceptions.Timeout as e:
        logger.error(f"模型请求超时 (30秒)")
        logger.error(f"错误详情: {str(e)}")
        return "⏰ 请求超时，请稍后重试"
    except Exception as e:
        import traceback
        logger.error(f"模型调用异常: {str(e)}")
        logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        return f"❌ 模型调用失败: {str(e)}"


# ===== 问题分类器（基于规则）=====
def classify_question(question: str) -> dict:
    """
    简单的问题分类器
    返回：{'type': 'price_query', 'params': {...}}
    """
    question_lower = question.lower()
    
    # 0. 图表生成请求（优先级最高）
    chart_keywords = ['图表', '图', '统计图', '散点图', '折线图', '柱状图', '漏斗图', '地图', '可视化']
    if any(keyword in question_lower for keyword in chart_keywords):
        chart_type = detect_chart_type(question)
        return {
            'type': 'chart_generation',
            'params': {'chart_type': chart_type}
        }
    
    # 1. 价格查询
    if any(keyword in question_lower for keyword in ['价格', '多少钱', '价位', '售价']):
        breed = extract_breed_name(question)
        return {
            'type': 'price_query',
            'params': {'breed': breed}
        }
    
    # 2. 品种信息查询（扩展关键词）
    elif any(keyword in question_lower for keyword in ['介绍', '特点', '习性', '寿命', '性格', '怎么样', '如何']):
        breed = extract_breed_name(question)
        return {
            'type': 'breed_info',
            'params': {'breed': breed}
        }
    
    # 3. 推荐问题
    elif any(keyword in question_lower for keyword in ['推荐', '适合', '新手', '第一次养']):
        return {
            'type': 'recommendation',
            'params': {}
        }
    
    # 4. 对比问题
    elif '对比' in question_lower or 'vs' in question_lower or ('和' in question_lower and len(question) < 30):
        breeds = extract_multiple_breeds(question)
        return {
            'type': 'comparison',
            'params': {'breeds': breeds}
        }
    
    # 5. 默认：通用问答
    else:
        return {
            'type': 'general_qa',
            'params': {}
        }


def detect_chart_type(question: str) -> str:
    """
    检测用户想要的图表类型
    
    Args:
        question: 用户问题
    
    Returns:
        图表类型字符串
    """
    question_lower = question.lower()
    
    # 价格散点图
    if any(kw in question_lower for kw in ['价格.*散点', '散点.*价格', '价格分布']):
        return 'price_scatter'
    
    # 体重折线图
    if any(kw in question_lower for kw in ['体重', '重量']):
        return 'weight_line'
    
    # 体型分布柱状图
    if any(kw in question_lower for kw in ['体型', '大小', '小型', '中型', '大型']):
        return 'level_bar'
    
    # 店铺TOP10
    if any(kw in question_lower for kw in ['店铺', '商家', 'top', '排行']):
        return 'shop_top10'
    
    # 价格漏斗图
    if any(kw in question_lower for kw in ['漏斗', '价格段', '价格区间']):
        return 'price_funnel'
    
    # 世界地图
    if any(kw in question_lower for kw in ['地图', '产地', '家乡', '来源']):
        return 'world_map'
    
    # 默认返回价格散点图
    return 'price_scatter'


def extract_breed_name(question: str) -> str:
    """提取品种名称（增强版）"""
    common_breeds = [
        # 热门品种
        '金毛', '泰迪', '柯基', '哈士奇', '拉布拉多', 
        '柴犬', '边境牧羊犬', '萨摩耶', '阿拉斯加', '贵宾',
        '比熊', '博美', '雪纳瑞', '斗牛犬', '约克夏',
        # 其他常见品种
        '法国斗牛犬', '英国斗牛犬', '德国牧羊犬', '罗威纳',
        '杜宾', '吉娃娃', '马尔济斯', '西施犬', '巴哥犬',
        '松狮', '秋田犬', '大白熊', '藏獒', '中华田园犬'
    ]
    
    for breed in common_breeds:
        if breed in question:
            return breed
    
    return '未知品种'


def extract_multiple_breeds(question: str) -> list:
    """提取多个品种名称（增强版）"""
    common_breeds = [
        # 热门品种
        '金毛', '泰迪', '柯基', '哈士奇', '拉布拉多',
        '柴犬', '边境牧羊犬', '萨摩耶', '阿拉斯加', '贵宾',
        '比熊', '博美', '雪纳瑞', '斗牛犬', '约克夏',
        # 其他常见品种
        '法国斗牛犬', '英国斗牛犬', '德国牧羊犬', '罗威纳',
        '杜宾', '吉娃娃', '马尔济斯', '西施犬', '巴哥犬',
        '松狮', '秋田犬', '大白熊', '藏獒', '中华田园犬'
    ]
    
    found_breeds = [breed for breed in common_breeds if breed in question]
    return found_breeds[:2]  # 最多2个


# ===== 数据查询处理器 =====

def handle_price_query(params: dict, context: list = None) -> str:
    """处理价格查询（支持上下文）"""
    breed = params.get('breed')
    
    if not breed or breed == '未知品种':
        logger.warning("价格查询: 未指定有效品种")
        return "请告诉我您想查询哪个品种的价格？例如：金毛、泰迪、柯基等"
    
    logger.info(f"价格查询: 品种={breed}")
    
    # 如果有上下文，使用模型进行更智能的回答
    if context and len(context) > 0:
        # 构建包含上下文的提示
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-4:]])
        prompt = f"""
        你是一个宠物数据顾问。用户询问价格信息。
        
        对话历史：
        {context_text}
        
        当前问题：查询{breed}的价格
        
        请先给出价格数据，然后结合上下文提供更个性化的建议。
        """
        
        messages = [
            {"role": "system", "content": "你是宠物数据专家"},
            {"role": "user", "content": prompt}
        ]
        
        return call_local_model(messages)
    
    # 无上下文时，直接查询数据库
    # 查询数据库 - jd_dogs表使用dog_name字段
    sql = text("""
        SELECT 
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            COUNT(*) as count
        FROM jd_dogs
        WHERE dog_name LIKE :breed
    """)
    
    try:
        result = db.session.execute(sql, {'breed': f'%{breed}%'}).fetchone()
        logger.info(f"价格查询结果: {result}")
        
        if not result or result.count == 0:
            logger.warning(f"价格查询: 未找到'{breed}'的数据")
            return f"抱歉，暂时没有找到'{breed}'的价格数据。"
        
        # 格式化回答
        answer = f"📊 **{breed}价格信息**\n\n"
        answer += f"• 平均价格：¥{result.avg_price:.0f}\n"
        answer += f"• 最低价格：¥{result.min_price:.0f}\n"
        answer += f"• 最高价格：¥{result.max_price:.0f}\n"
        answer += f"• 数据条数：{result.count}条\n\n"
        answer += f"💡 提示：价格会因地区、血统、年龄等因素有所差异。"
        
        logger.info(f"价格查询成功: {breed}, 平均价格=¥{result.avg_price:.0f}")
        return answer
    
    except Exception as e:
        logger.error(f"价格查询失败: {str(e)}", exc_info=True)
        return f"查询出错：{str(e)}"


def handle_breed_info(params: dict, context: list = None) -> str:
    """处理品种信息查询（支持上下文）"""
    breed = params.get('breed')
    
    if not breed or breed == '未知品种':
        logger.warning("品种查询: 未指定有效品种")
        return "请告诉我您想了解哪个品种？例如：金毛、泰迪等"
    
    logger.info(f"品种查询: {breed}")
    
    # 如果有上下文，使用模型进行更智能的回答
    if context and len(context) > 0:
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-4:]])
        prompt = f"""
        你是一个宠物专家。用户询问品种信息。
        
        对话历史：
        {context_text}
        
        当前问题：了解{breed}的特点
        
        请结合上下文，提供个性化的品种介绍和养护建议。
        """
        
        messages = [
            {"role": "system", "content": "你是宠物专家"},
            {"role": "user", "content": prompt}
        ]
        
        return call_local_model(messages)
    
    # 无上下文时，查询数据库
    sql = text("""
        SELECT breed_name, avg_life_years, size_category, popularity
        FROM dog_breeds
        WHERE breed_name LIKE :breed
    """)
    
    try:
        result = db.session.execute(sql, {'breed': f'%{breed}%'}).fetchone()
        logger.info(f"品种查询结果: {result}")
        
        if not result:
            logger.info(f"品种'{breed}'不在数据库中，调用模型获取信息")
            # 如果数据库没有，调用本地模型获取通用知识
            return get_breed_info_from_model(breed)
        
        # 格式化回答
        answer = f"🐕 **{result.breed_name}品种介绍**\n\n"
        answer += f"• 体型：{result.size_category or '未知'}\n"
        answer += f"• 平均寿命：{result.avg_life_years or '未知'}年\n"
        answer += f"• 人气指数：{result.popularity or '未知'}\n\n"
        answer += f"💡 想了解更多养护知识吗？可以继续问我！"
        
        logger.info(f"品种查询成功: {breed}")
        return answer
    
    except Exception as e:
        logger.error(f"品种查询失败: {str(e)}", exc_info=True)
        return f"查询出错：{str(e)}"


def handle_recommendation(params: dict, context: list = None) -> str:
    """处理推荐问题（支持上下文）"""
    # 构建基础提示
    base_prompt = """
    你是一个专业的宠物顾问。请根据用户的需求推荐适合的犬种。
    
    要求：
    1. 推荐3-5个品种
    2. 说明推荐理由
    3. 给出简要的养护建议
    4. 语气友好专业
    """
    
    # 如果有上下文，添加上下文信息
    if context and len(context) > 0:
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-6:]])
        full_prompt = f"""
        {base_prompt}
        
        对话历史：
        {context_text}
        
        请结合用户的偏好和历史对话，提供个性化的推荐。
        """
    else:
        full_prompt = f"""
        {base_prompt}
        
        用户需求：适合新手养的狗狗
        """
    
    messages = [
        {"role": "system", "content": "你是宠物顾问专家"},
        {"role": "user", "content": full_prompt}
    ]
    
    return call_local_model(messages)


def handle_comparison(params: dict, context: list = None) -> str:
    """处理对比问题（支持上下文）"""
    breeds = params.get('breeds', [])
    
    if len(breeds) < 2:
        return "请告诉我要对比哪两个品种？例如：金毛和泰迪"
    
    breed1, breed2 = breeds[0], breeds[1]
    
    # 构建基础提示
    base_prompt = f"""
    请对比以下两个犬种，从以下几个方面分析：
    1. 性格特点
    2. 体型大小
    3. 养护难度
    4. 适合人群
    5. 价格区间
    
    犬种：{breed1} vs {breed2}
    
    请用清晰的格式呈现对比结果，并给出选择建议。
    """
    
    # 如果有上下文，添加上下文信息
    if context and len(context) > 0:
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-4:]])
        full_prompt = f"""
        {base_prompt}
        
        对话历史：
        {context_text}
        
        请结合上下文，提供更精准的对比分析。
        """
    else:
        full_prompt = base_prompt
    
    messages = [
        {"role": "system", "content": "你是宠物对比分析专家"},
        {"role": "user", "content": full_prompt}
    ]
    
    return call_local_model(messages)


def handle_chart_generation(params: dict, context: list = None) -> str:
    """
    处理图表生成请求
    
    Args:
        params: 参数 {'chart_type': 'price_scatter', 'breed': '金毛'}
        context: 对话上下文
    
    Returns:
        HTML字符串或错误消息
    """
    chart_type = params.get('chart_type', '')
    breed = params.get('breed', '')
    
    logger.info(f"图表生成请求: type={chart_type}, breed={breed}")
    
    try:
        # 根据图表类型调用对应的函数
        if chart_type == 'price_scatter':
            # 价格散点图
            html = charts.get_price_scatter()
            return f"""
            <div class="chart-container">
                <h3>📊 狗狗价格散点图</h3>
                {html}
                <p style="margin-top: 10px; color: #666;">💡 提示：横轴为价格，纵轴为该价格的狗狗数量</p>
            </div>
            """
        
        elif chart_type == 'weight_line':
            # 体重折线图
            html = charts.get_weight_line()
            return f"""
            <div class="chart-container">
                <h3>📈 狗狗体重分布图</h3>
                {html}
            </div>
            """
        
        elif chart_type == 'level_bar':
            # 体型分布柱状图
            html = charts.get_level_bar()
            return f"""
            <div class="chart-container">
                <h3>📊 体型分布分析 - TOP20 犬种</h3>
                {html}
            </div>
            """
        
        elif chart_type == 'shop_top10':
            # 店铺TOP10直方图
            html = charts.get_shop_top10_hist()
            return f"""
            <div class="chart-container">
                <h3>📊 售卖前10种宠物狗 + 店铺TOP10</h3>
                {html}
            </div>
            """
        
        elif chart_type == 'price_funnel':
            # 价格漏斗图
            html = charts.get_price_funnel()
            return f"""
            <div class="chart-container">
                <h3>🔻 狗狗价格段漏斗图</h3>
                {html}
            </div>
            """
        
        elif chart_type == 'world_map':
            # 世界地图
            html = charts.get_world_map()
            return f"""
            <div class="chart-container">
                <h3>🌍 世界地图 - 狗狗家乡分布</h3>
                {html}
            </div>
            """
        
        else:
            return f"❌ 不支持的图表类型: {chart_type}。支持的类型包括：price_scatter, weight_line, level_bar, shop_top10, price_funnel, world_map"
    
    except Exception as e:
        logger.error(f"图表生成失败: {str(e)}")
        return f"❌ 图表生成失败: {str(e)}"


def handle_general_qa(question: str, context: list = None) -> str:
    """处理通用问答（支持上下文）"""
    # 构建更专业的system prompt
    system_prompt = """你是宠物知识专家，拥有丰富的狗狗养护、训练、健康等专业知识。

回答要求：
1. 专业准确：基于科学知识和实践经验
2. 结构清晰：使用列表、分段等方式组织内容
3. 实用性强：给出可操作的建议
4. 语气友好：亲切自然，易于理解
5. 长度适中：100-300字为宜
6. 安全第一：涉及健康问题时提醒咨询兽医

请根据用户问题提供专业、实用的回答。"""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 如果有上下文，添加到消息中
    if context and len(context) > 0:
        messages.extend(context)
        logger.info(f"使用上下文对话，历史消息数: {len(context)}")
    
    # 添加当前问题
    messages.append({"role": "user", "content": question})
    
    return call_local_model(messages)


def get_breed_info_from_model(breed: str) -> str:
    """从本地模型获取品种信息（当数据库没有时）"""
    prompt = f"""请详细介绍{breed}犬，包括以下方面：

1. **基本特征**：体型、毛色、寿命等
2. **性格特点**：温顺度、活跃度、智商等
3. **养护要点**：运动需求、梳理频率、饮食建议
4. **训练建议**：难易程度、注意事项
5. **适合人群**：新手/有经验、家庭/单身等

请用清晰的结构呈现，语气友好专业。"""
    
    messages = [
        {"role": "system", "content": "你是宠物专家，提供专业、详细的品种介绍"},
        {"role": "user", "content": prompt}
    ]
    
    return call_local_model(messages)


def get_conversation_context(session_id: int, max_messages: int = 10) -> list:
    """
    获取会话的上下文历史
    
    Args:
        session_id: 会话ID
        max_messages: 最多返回的消息数量（默认10条，即5轮对话）
    
    Returns:
        消息列表，格式为 [{"role": "user/assistant", "content": "..."}]
    """
    try:
        # 获取最近的消息（按时间倒序）
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(max_messages).all()
        
        # 反转列表，使其按时间正序
        messages.reverse()
        
        # 转换为模型需要的格式
        context = []
        for msg in messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.info(f"获取会话 {session_id} 的上下文: {len(context)}条消息")
        return context
    
    except Exception as e:
        logger.error(f"获取上下文失败: {str(e)}")
        return []


def auto_learn_from_answer(question: str, answer: str, question_type: str, feedback_score: float = None) -> bool:
    """
    自动学习：将模型的优质回答加入知识库（增强版）
    
    Args:
        question: 用户问题
        answer: AI回答
        question_type: 问题类型
        feedback_score: 用户反馈分数（1-5），None表示无反馈
    
    Returns:
        是否成功加入知识库
    """
    try:
        from utils.knowledge_base import get_knowledge_base
        
        kb = get_knowledge_base()
        
        # ===== 优化1: 更严格的质量判断 =====
        
        # 1.1 回答长度检查（至少80字符）
        if len(answer) < 80:
            logger.info(f"回答过短，跳过学习: {len(answer)}字符")
            return False
        
        # 1.2 避免学习明显的错误回答
        error_indicators = ['抱歉', '无法回答', '不知道', '不清楚', '暂时没']
        if any(indicator in answer for indicator in error_indicators):
            logger.info(f"回答包含错误指示词，跳过学习")
            return False
        
        # 1.3 如果有用户反馈，优先使用反馈分数
        if feedback_score is not None:
            if feedback_score < 3:  # 低于3分不学习
                logger.info(f"用户反馈分数低 ({feedback_score})，跳过学习")
                return False
            confidence = 0.5 + (feedback_score - 3) * 0.1  # 3分=0.5, 4分=0.6, 5分=0.7
        else:
            # 无反馈时，基于回答质量估算置信度
            confidence = _estimate_answer_confidence(answer, question_type)
        
        # ===== 优化2: 智能去重检查 =====
        
        # 2.1 检查是否已存在类似问题
        existing = kb.search(question, question_type)
        if existing:
            # 如果新回答质量更高，可以考虑更新
            existing_confidence = existing.get('confidence', 0.5)
            if confidence > existing_confidence + 0.1:  # 新回答明显更好
                logger.info(f"发现更优质的回答，准备更新知识库")
                # TODO: 可以实现更新逻辑
            else:
                logger.info(f"知识库已存在类似或更优回答，跳过学习")
                return False
        
        # ===== 优化3: 改进关键词提取 =====
        
        # 3.1 提取更准确的关键词
        keywords = extract_keywords_enhanced(question, question_type)
        title = f"{question_type}: {keywords}"
        
        # ===== 优化4: 添加元数据 =====
        
        metadata = {
            'learned_at': datetime.now().isoformat(),
            'question_type': question_type,
            'answer_length': len(answer),
            'confidence_source': 'user_feedback' if feedback_score else 'auto_estimate',
            'requires_review': confidence < 0.6  # 低置信度需要人工审核
        }
        
        # ===== 优化5: 添加到知识库 =====
        
        # 生成知识键
        key = f"{question_type}: {keywords}"
        
        # 构建知识条目
        knowledge_item = {
            "question_patterns": [question],
            "answer": answer,
            "category": question_type,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "source": "auto_learning",
            **metadata
        }
        
        success = kb.add_knowledge(key, knowledge_item)
        
        if success:
            logger.info(f"✅ 自动学习成功: {title} (置信度: {confidence:.2f})")
            if metadata['requires_review']:
                logger.warning(f"⚠️ 该知识需要人工审核")
        else:
            logger.warning(f"⚠️ 自动学习失败")
        
        return success
    
    except Exception as e:
        logger.error(f"自动学习异常: {str(e)}")
        return False


def _estimate_answer_confidence(answer: str, question_type: str) -> float:
    """
    估算回答的置信度（基于启发式规则）
    
    Args:
        answer: AI回答
        question_type: 问题类型
    
    Returns:
        置信度分数 (0.5-0.9)
    """
    confidence = 0.5  # 基础置信度
    
    # 1. 回答长度加分（适中最好）
    if 100 <= len(answer) <= 500:
        confidence += 0.1
    elif len(answer) > 500:
        confidence += 0.15
    
    # 2. 包含结构化信息加分
    structure_indicators = ['•', '-', '*', '1.', '2.', '首先', '其次', '最后']
    if any(indicator in answer for indicator in structure_indicators):
        confidence += 0.1
    
    # 3. 包含专业术语加分
    professional_terms = {
        'breed_info': ['性格', '体型', '养护', '寿命', '特点'],
        'price_query': ['价格', '¥', '元', '平均', '区间'],
        'recommendation': ['推荐', '适合', '建议', '考虑'],
        'comparison': ['对比', '差异', '优势', '劣势']
    }
    
    terms = professional_terms.get(question_type, [])
    term_count = sum(1 for term in terms if term in answer)
    if term_count >= 2:
        confidence += 0.1
    
    # 4. 限制最高置信度
    return min(confidence, 0.85)


def extract_keywords_enhanced(text: str, question_type: str, max_keywords: int = 5) -> str:
    """
    增强的关键词提取（针对不同类型优化）
    
    Args:
        text: 输入文本
        question_type: 问题类型
        max_keywords: 最多提取的关键词数量
    
    Returns:
        关键词字符串
    """
    import re
    
    # 通用停用词
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', 
                  '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', 
                  '着', '没有', '看', '好', '自己', '这', '那', '什么', '怎么', '吗', '呢'}
    
    # 针对不同类型的特殊处理
    if question_type == 'price_query':
        # 价格查询：重点提取品种名
        breed_pattern = r'([\u4e00-\u9fa5]{2,4})(?:犬|狗|品种)?'
        breeds = re.findall(breed_pattern, text)
        if breeds:
            return breeds[0]  # 返回第一个品种名
    
    elif question_type == 'breed_info':
        # 品种信息：提取品种名+关键特征
        breed_pattern = r'([\u4e00-\u9fa5]{2,4})(?:犬|狗)?'
        breeds = re.findall(breed_pattern, text)
        if breeds:
            return breeds[0]
    
    # 通用提取
    words = re.findall(r'[\w]+', text)
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    
    # 返回前N个关键词
    return ' '.join(keywords[:max_keywords])


def extract_keywords(text: str, max_keywords: int = 3) -> str:
    """
    从文本中提取关键词（简化版）
    
    Args:
        text: 输入文本
        max_keywords: 最多提取的关键词数量
    
    Returns:
        关键词字符串
    """
    # 简单的关键词提取：去除停用词，取前几个有意义的词
    stop_words = ['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
    
    # 分词（简单按空格和标点分割）
    import re
    words = re.findall(r'[\w]+', text)
    
    # 过滤停用词和短词
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    
    # 返回前N个关键词
    return ' '.join(keywords[:max_keywords])


# ===== API接口 =====

@ai_bp.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """
    AI聊天接口（本地模型版）- 支持游客模式
    
    请求格式：
    {
        "message": "金毛的价格是多少？"
    }
    
    返回格式：
    {
        "success": true,
        "answer": "金毛的平均价格是...",
        "type": "price_query"
    }
    """
    request_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
    
    try:
        # 检查用户状态（登录或游客）
        is_guest = not current_user.is_authenticated
        
        if is_guest:
            logger.info(f"[{request_id}] 🚶 收到游客AI聊天请求")
            logger.info(f"[{request_id}] IP地址: {request.remote_addr}")
        else:
            logger.info(f"[{request_id}] 👤 收到AI聊天请求")
            logger.info(f"[{request_id}] 用户: {current_user.username} (ID: {current_user.id})")
        
        data = request.get_json()
        logger.info(f"[{request_id}] 请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        if not data or 'message' not in data:
            logger.error(f"[{request_id}] 错误: 缺少message字段")
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400
        
        user_message = data['message'].strip()
        logger.info(f"[{request_id}] 用户消息: {user_message[:100]}")
        
        if not user_message:
            logger.warning(f"[{request_id}] 错误: 消息为空")
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
        
        if len(user_message) > 1000:
            logger.warning(f"[{request_id}] 错误: 消息过长 ({len(user_message)}字符)")
            return jsonify({
                'success': False,
                'error': '消息过长（最多1000字符）'
            }), 400
        
        # Step 0: 获取或创建会话
        session_id = data.get('session_id')
        if not session_id:
            # 自动创建新会话
            # 游客使用guest用户，登录用户使用实际ID
            if is_guest:
                # 动态获取或创建guest用户
                from models import User
                from werkzeug.security import generate_password_hash
                
                guest_user = User.query.filter_by(username='guest').first()
                if not guest_user:
                    # 如果guest用户不存在，创建它
                    guest_user = User(
                        username='guest',
                        password_hash=generate_password_hash('guest'),
                        role='guest'
                    )
                    db.session.add(guest_user)
                    db.session.commit()
                    logger.info(f"[{request_id}] 创建guest用户: ID={guest_user.id}")
                
                user_id_for_session = guest_user.id
            else:
                user_id_for_session = current_user.id
            
            session = ChatSession(
                user_id=user_id_for_session,
                title=user_message[:50]  # 用第一条消息作为标题
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
            logger.info(f"[{request_id}] 创建新会话: ID={session_id} (游客: {is_guest})")
        else:
            # 验证会话归属
            session = ChatSession.query.get(session_id)
            if not session:
                return jsonify({'error': '会话不存在'}), 404
            
            # 如果是登录用户，验证会话归属
            if not is_guest and session.user_id != current_user.id:
                return jsonify({'error': '无权访问该会话'}), 403
            
            # 游客只能访问自己创建的会话（通过localStorage中的sessionId）
            # 这里不做严格验证，因为游客没有身份标识
        
        # Step 1: 问题分类
        classification = classify_question(user_message)
        question_type = classification['type']
        params = classification['params']
        logger.info(f"[{request_id}] 问题类型: {question_type}, 参数: {params}")
        
        # Step 1.5: 优先查询知识库
        kb = get_knowledge_base()
        kb_result = kb.search(user_message, question_type)
        
        if kb_result:
            # 知识库命中，直接返回
            answer = kb_result['answer']
            category = kb_result.get('category', '未知')
            logger.info(f"[{request_id}] ✅ 知识库命中，类别: {category}")
            logger.info(f"[{request_id}] 生成回复成功，长度: {len(answer)}字符")
            logger.info(f"[{request_id}] 回复内容: {answer[:200]}...")
            
            # 在回答中添加知识库来源提示
            source_hint = f"\n\n📚 *来自知识库 ({category})*"
            answer_with_source = answer + source_hint
            
            # 保存对话历史（知识库命中）
            try:
                user_msg = ChatMessage(
                    session_id=session_id,
                    role='user',
                    content=user_message,
                    question_type=question_type
                )
                db.session.add(user_msg)
                
                ai_msg = ChatMessage(
                    session_id=session_id,
                    role='assistant',
                    content=answer,
                    question_type=question_type,
                    source='knowledge_base'
                )
                db.session.add(ai_msg)
                
                session.message_count += 2
                session.last_message_at = datetime.now()
                session.updated_at = datetime.now()
                
                db.session.commit()
                
                # 获取AI消息的ID
                message_id = ai_msg.id
            except Exception as e:
                db.session.rollback()
                logger.error(f"[{request_id}] 保存对话历史失败: {str(e)}")
                message_id = None
            
            return jsonify({
                'success': True,
                'answer': answer_with_source,
                'type': question_type,
                'source': 'knowledge_base',
                'session_id': session_id,
                'message_id': message_id
            })
        else:
            logger.info(f"[{request_id}] 🔍 知识库未命中，调用模型")
            # 在回答中添加提示，告知用户使用了模型生成
            answer_suffix = "\n\n💡 *本回答由AI模型生成，仅供参考*"
        
        # Step 2: 根据类型处理（模型调用）
        # 获取会话上下文（支持所有问题类型）
        context = get_conversation_context(session_id, max_messages=10)
        
        answer = ""
        if question_type == 'chart_generation':
            logger.info(f"[{request_id}] 处理图表生成: {params.get('chart_type')}")
            answer = handle_chart_generation(params, context)
        elif question_type == 'price_query':
            logger.info(f"[{request_id}] 处理价格查询: {params.get('breed')}")
            answer = handle_price_query(params, context)
        elif question_type == 'breed_info':
            logger.info(f"[{request_id}] 处理品种信息: {params.get('breed')}")
            answer = handle_breed_info(params, context)
        elif question_type == 'recommendation':
            logger.info(f"[{request_id}] 处理推荐请求")
            answer = handle_recommendation(params, context)
        elif question_type == 'comparison':
            logger.info(f"[{request_id}] 处理对比请求: {params.get('breeds')}")
            answer = handle_comparison(params, context)
        else:  # general_qa
            logger.info(f"[{request_id}] 处理通用问答")
            answer = handle_general_qa(user_message, context)
        
        # 添加模型生成提示
        answer += answer_suffix
        
        logger.info(f"[{request_id}] 生成回复成功，长度: {len(answer)}字符")
        logger.info(f"[{request_id}] 回复内容: {answer[:200]}...")
        
        # Step 3: 保存对话历史
        import time
        start_time = time.time()
        message_id = None  # 初始化message_id
        
        try:
            # 保存用户消息
            user_msg = ChatMessage(
                session_id=session_id,
                role='user',
                content=user_message,
                question_type=question_type
            )
            db.session.add(user_msg)
            
            # 保存AI回复
            ai_msg = ChatMessage(
                session_id=session_id,
                role='assistant',
                content=answer,
                question_type=question_type,
                source=data.get('source', 'model')
            )
            db.session.add(ai_msg)
            
            # 更新会话统计
            session.message_count += 2
            session.last_message_at = datetime.now()
            session.updated_at = datetime.now()
            
            db.session.commit()
            
            response_time = time.time() - start_time
            logger.info(f"[{request_id}] 保存对话历史完成 (耗时: {response_time:.3f}s)")
            
            # 获取AI消息的ID
            message_id = ai_msg.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{request_id}] 保存对话历史失败: {str(e)}")
        
        # Step 4: 自动学习（仅对模型生成的回答）
        if data.get('source', 'model') == 'model':
            try:
                learn_success = auto_learn_from_answer(user_message, answer, question_type)
                if learn_success:
                    logger.info(f"[{request_id}] 🎓 自动学习成功，知识已加入库")
            except Exception as e:
                logger.error(f"[{request_id}] 自动学习异常: {str(e)}")
        
        return jsonify({
            'success': True,
            'answer': answer,
            'type': question_type,
            'session_id': session_id,
            'message_id': message_id  # 添加消息ID
        })
    
    except Exception as e:
        import traceback
        import sys
        
        # 获取详细的错误信息
        error_type = type(e).__name__
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # 记录详细错误日志
        logger.error(f"\n{'='*80}")
        logger.error(f"[{request_id}] ❌ AI聊天发生错误")
        logger.error(f"{'='*80}")
        logger.error(f"错误类型: {error_type}")
        logger.error(f"错误消息: {error_msg}")
        logger.error(f"请求用户: {current_user.username if current_user.is_authenticated else '未登录'} (ID: {current_user.id if current_user.is_authenticated else 'N/A'})")
        logger.error(f"请求数据: {json.dumps(data, ensure_ascii=False) if 'data' in locals() and data else 'N/A'}")
        logger.error(f"会话ID: {session_id if 'session_id' in locals() else 'N/A'}")
        logger.error(f"问题类型: {question_type if 'question_type' in locals() else 'N/A'}")
        logger.error(f"Python版本: {sys.version}")
        logger.error(f"\n堆栈跟踪:\n{error_trace}")
        logger.error(f"{'='*80}\n")
        
        # 根据错误类型返回不同的提示
        error_response = {
            'success': False,
            'error_type': error_type,
            'request_id': request_id  # 返回请求ID便于追踪
        }
        
        # 常见错误的友好提示
        if 'ConnectionError' in error_type or 'connection' in error_msg.lower():
            error_response['error'] = '无法连接到AI模型服务，请检查模型是否启动'
            error_response['suggestion'] = '请确保Ollama服务正在运行：ollama serve'
        elif 'Timeout' in error_type or 'timeout' in error_msg.lower():
            error_response['error'] = 'AI模型响应超时，请稍后重试'
            error_response['suggestion'] = '模型可能正在处理其他请求，请稍等片刻再试'
        elif 'Database' in error_type or 'database' in error_msg.lower() or 'sql' in error_msg.lower():
            error_response['error'] = '数据库操作失败，请联系管理员'
            error_response['suggestion'] = '系统已记录错误，技术人员会尽快处理'
        elif 'Permission' in error_type or 'permission' in error_msg.lower():
            error_response['error'] = '权限不足，请重新登录'
            error_response['suggestion'] = '您的会话可能已过期，请刷新页面重新登录'
        else:
            error_response['error'] = f'服务器内部错误 ({error_type})'
            error_response['suggestion'] = '系统已记录错误详情，请稍后重试或联系管理员'
        
        return jsonify(error_response), 500


@ai_bp.route('/ai-chat')
def ai_chat_page():
    """AI聊天页面 - 支持游客访问"""
    return render_template('ai_chat.html')


@ai_bp.route('/ai-knowledge')
@login_required
def knowledge_base_page():
    """知识库管理页面"""
    return render_template('knowledge_base.html')


@ai_bp.route('/api/ai/model/status')
def model_status():
    """检查本地模型状态 - 支持游客"""
    try:
        config = LOCAL_MODEL_CONFIG.get(MODEL_TYPE)
        base_url = config['base_url']
        
        if MODEL_TYPE == 'ollama':
            # 检查Ollama服务
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return jsonify({
                    'status': 'online',
                    'type': MODEL_TYPE,
                    'url': base_url,
                    'available_models': [m['name'] for m in models]
                })
        elif MODEL_TYPE == 'lmstudio':
            # 检查LM Studio服务
            response = requests.get(f"{base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                return jsonify({
                    'status': 'online',
                    'type': MODEL_TYPE,
                    'url': base_url
                })
        
        return jsonify({
            'status': 'offline',
            'type': MODEL_TYPE,
            'url': base_url,
            'message': '模型服务未启动'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'type': MODEL_TYPE,
            'error': str(e)
        })


@ai_bp.route('/api/ai/knowledge/stats')
def knowledge_stats():
    """获取知识库统计信息 - 支持游客"""
    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"获取知识库统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/learn', methods=['POST'])
@login_required
def manual_learn():
    """
    手动学习：将指定的问答对加入知识库
    
    请求格式：
    {
        "question": "问题",
        "answer": "回答",
        "category": "breed_info"
    }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['question', 'answer', 'category']):
            return jsonify({
                'success': False,
                'error': '缺少必要字段'
            }), 400
        
        question = data['question']
        answer = data['answer']
        category = data['category']
        
        # 调用自动学习函数
        success = auto_learn_from_answer(question, answer, category)
        
        if success:
            return jsonify({
                'success': True,
                'message': '学习成功，知识已加入库'
            })
        else:
            return jsonify({
                'success': False,
                'message': '学习失败，可能已存在类似知识'
            }), 400
    
    except Exception as e:
        logger.error(f"手动学习失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 对话历史 API =====

@ai_bp.route('/api/ai/sessions')
def get_sessions():
    """获取当前用户的对话会话列表 - 支持游客"""
    try:
        # 检查用户状态
        is_guest = not current_user.is_authenticated
        
        if is_guest:
            # 动态获取guest用户ID
            from models import User
            guest_user = User.query.filter_by(username='guest').first()
            if not guest_user:
                # 如果不存在，返回空列表
                return jsonify({
                    'success': True,
                    'sessions': [],
                    'is_guest': True
                })
            
            # 游客：返回guest用户的会话
            sessions = ChatSession.query.filter_by(
                user_id=guest_user.id,
                is_active=True
            ).order_by(
                ChatSession.updated_at.desc()
            ).limit(20).all()  # 游客最多20个会话
        else:
            # 登录用户：返回自己的会话
            sessions = ChatSession.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).order_by(
                ChatSession.updated_at.desc()
            ).limit(50).all()  # 最多返回50个会话
        
        return jsonify({
            'success': True,
            'sessions': [s.to_dict() for s in sessions],
            'is_guest': is_guest
        })
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions', methods=['POST'])
def create_session():
    """创建新的对话会话 - 支持游客"""
    try:
        # 检查用户状态
        is_guest = not current_user.is_authenticated
        
        data = request.get_json()
        title = data.get('title', '新对话')
        
        # 游客使用guest用户ID，动态获取
        if is_guest:
            from models import User
            guest_user = User.query.filter_by(username='guest').first()
            if not guest_user:
                # 如果不存在，创建它
                from werkzeug.security import generate_password_hash
                guest_user = User(
                    username='guest',
                    password_hash=generate_password_hash('guest'),
                    role='guest'
                )
                db.session.add(guest_user)
                db.session.commit()
            user_id_for_session = guest_user.id
        else:
            user_id_for_session = current_user.id
        
        session = ChatSession(
            user_id=user_id_for_session,
            title=title
        )
        
        db.session.add(session)
        db.session.commit()
        
        if is_guest:
            logger.info(f"游客创建新会话: ID={session.id}")
        else:
            logger.info(f"创建新会话: ID={session.id}, 用户={current_user.username}")
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'title': session.title,
            'is_guest': is_guest
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建会话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions/<int:session_id>')
def get_session(session_id):
    """获取指定会话的详细信息 - 支持游客"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # 检查用户状态
        is_guest = not current_user.is_authenticated
        
        # 如果是登录用户，验证会话归属
        if not is_guest and session.user_id != current_user.id:
            return jsonify({'error': '无权访问'}), 403
        
        # 游客可以访问guest用户的会话
        if is_guest:
            from models import User
            guest_user = User.query.filter_by(username='guest').first()
            if guest_user and session.user_id != guest_user.id:
                return jsonify({'error': '无权访问'}), 403
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'is_guest': is_guest
        })
    except Exception as e:
        logger.error(f"获取会话详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions/<int:session_id>/messages')
@login_required
def get_messages(session_id):
    """获取指定会话的消息历史"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # 权限检查
        if session.user_id != current_user.id:
            return jsonify({'error': '无权访问'}), 403
        
        # 获取消息（按时间排序）
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message_count': len(messages),
            'messages': [m.to_dict() for m in messages]
        })
    except Exception as e:
        logger.error(f"获取消息历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除指定会话(硬删除+级联删除消息)"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # 权限检查：支持游客(user_id=None)和登录用户
        if session.user_id is not None:
            # 登录用户的会话，需要验证权限
            try:
                if not current_user.is_authenticated or session.user_id != current_user.id:
                    return jsonify({'error': '无权访问'}), 403
            except Exception:
                # 未登录用户无法访问登录用户的会话
                return jsonify({'error': '请先登录'}), 401
        # 游客会话(user_id=None)，允许删除
        
        # 先删除该会话下的所有消息
        deleted_messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).delete()
        
        # 再删除会话本身
        db.session.delete(session)
        db.session.commit()
        
        username = current_user.username if current_user.is_authenticated else '游客'
        logger.info(f"删除会话: ID={session_id}, 用户={username}, 删除消息数={deleted_messages}")
        
        return jsonify({
            'success': True,
            'message': '会话已删除',
            'deleted_messages_count': deleted_messages
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除会话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """
    提交用户反馈（点赞/点踩）
    
    请求格式：
    {
        "message_id": 123,
        "feedback": "like" 或 "dislike",
        "comment": "可选的备注"
    }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['message_id', 'feedback']):
            return jsonify({
                'success': False,
                'error': '缺少必要字段'
            }), 400
        
        message_id = data['message_id']
        feedback = data['feedback']  # 'like' or 'dislike'
        comment = data.get('comment', '')
        
        # 验证feedback值
        if feedback not in ['like', 'dislike']:
            return jsonify({
                'success': False,
                'error': 'feedback必须是like或dislike'
            }), 400
        
        # 查询消息
        message = ChatMessage.query.get_or_404(message_id)
        
        # 验证会话归属
        session = ChatSession.query.get(message.session_id)
        if session.user_id != current_user.id:
            return jsonify({'error': '无权访问'}), 403
        
        # 更新反馈
        message.feedback = feedback
        message.feedback_comment = comment
        db.session.commit()
        
        logger.info(f"用户 {current_user.username} 对消息 {message_id} 提交反馈: {feedback}")
        
        return jsonify({
            'success': True,
            'message': '反馈提交成功'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"提交反馈失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 报告生成模块 =====

def generate_session_summary(session_id: int) -> dict:
    """
    生成会话总结报告
    
    Args:
        session_id: 会话ID
    
    Returns:
        包含总结信息的字典
    """
    try:
        # 获取会话信息
        session = ChatSession.query.get(session_id)
        if not session:
            return {'error': '会话不存在'}
        
        # 获取所有消息
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).all()
        
        if not messages:
            return {'error': '会话中没有消息'}
        
        # 统计信息
        user_messages = [m for m in messages if m.role == 'user']
        ai_messages = [m for m in messages if m.role == 'assistant']
        
        # 问题类型统计
        question_types = {}
        for msg in messages:
            if msg.question_type:
                question_types[msg.question_type] = question_types.get(msg.question_type, 0) + 1
        
        # 提取关键话题（从用户消息中提取品种名）
        topics = set()
        for msg in user_messages:
            breeds = extract_multiple_breeds(msg.content)
            topics.update(breeds)
        
        summary = {
            'session_id': session_id,
            'title': session.title,
            'created_at': session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_message_at': session.last_message_at.strftime('%Y-%m-%d %H:%M:%S') if session.last_message_at else None,
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'duration_minutes': round((session.last_message_at - session.created_at).total_seconds() / 60, 1) if session.last_message_at and session.created_at else 0,
            'question_types': question_types,
            'topics': list(topics),
            'feedback_stats': {
                'like': sum(1 for m in ai_messages if m.feedback == 'like'),
                'dislike': sum(1 for m in ai_messages if m.feedback == 'dislike'),
                'no_feedback': sum(1 for m in ai_messages if m.feedback is None)
            }
        }
        
        logger.info(f"生成会话 {session_id} 的总结报告")
        return summary
    
    except Exception as e:
        logger.error(f"生成会话总结失败: {str(e)}")
        return {'error': str(e)}


def generate_purchase_recommendation(user_preferences: dict) -> str:
    """
    生成宠物选购建议报告
    
    Args:
        user_preferences: 用户偏好 {'budget': 5000, 'size': 'medium', 'experience': 'beginner'}
    
    Returns:
        HTML格式的建议报告
    """
    budget = user_preferences.get('budget', 0)
    size = user_preferences.get('size', '')  # small, medium, large
    experience = user_preferences.get('experience', '')  # beginner, intermediate, advanced
    purpose = user_preferences.get('purpose', '')  # companion, guard, show
    
    # 构建查询条件
    conditions = []
    params = {}
    
    if budget > 0:
        conditions.append("price <= :budget")
        params['budget'] = budget
    
    if size:
        size_map = {
            'small': ['小型', '小'],
            'medium': ['中型', '中'],
            'large': ['大型', '大']
        }
        size_keywords = size_map.get(size, [])
        if size_keywords:
            size_condition = " OR ".join([f"pet_level LIKE :size{i}" for i in range(len(size_keywords))])
            conditions.append(f"({size_condition})")
            for i, kw in enumerate(size_keywords):
                params[f'size{i}'] = f'%{kw}%'
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # 查询符合条件的狗狗
    sql = text(f"""
        SELECT 
            dog_name,
            price,
            pet_level,
            size,
            COUNT(*) as count
        FROM jd_dogs
        WHERE {where_clause}
        GROUP BY dog_name, price, pet_level, size
        ORDER BY price ASC
        LIMIT 10
    """)
    
    try:
        results = db.session.execute(sql, params).fetchall()
        
        if not results:
            return "抱歉，没有找到符合您条件的狗狗。请尝试调整筛选条件。"
        
        # 生成HTML报告
        html = f"""
        <div class="report-container" style="padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h2 style="color: #2c3e50;">🐕 宠物选购建议报告</h2>
            <hr>
            
            <div style="margin-bottom: 20px;">
                <h3 style="color: #34495e;">📋 您的需求</h3>
                <ul style="list-style: none; padding-left: 0;">
                    <li>💰 预算：¥{budget if budget > 0 else '不限'}</li>
                    <li>📏 体型：{size if size else '不限'}</li>
                    <li>🎓 经验：{experience if experience else '不限'}</li>
                    <li>🎯 用途：{purpose if purpose else '不限'}</li>
                </ul>
            </div>
            
            <div>
                <h3 style="color: #34495e;">✅ 推荐品种（TOP 10）</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #3498db; color: white;">
                            <th style="padding: 10px; text-align: left;">品种</th>
                            <th style="padding: 10px; text-align: right;">平均价格</th>
                            <th style="padding: 10px; text-align: center;">体型</th>
                            <th style="padding: 10px; text-align: center;">体型分类</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for row in results:
            html += f"""
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px;"><strong>{row.dog_name}</strong></td>
                            <td style="padding: 10px; text-align: right;">¥{row.price:.0f}</td>
                            <td style="padding: 10px; text-align: center;">{row.pet_level or '未知'}</td>
                            <td style="padding: 10px; text-align: center;">{row.size or '未知'}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #e8f4f8; border-left: 4px solid #3498db; border-radius: 5px;">
                <h4 style="color: #2c3e50; margin-top: 0;">💡 温馨提示</h4>
                <ul style="margin-bottom: 0;">
                    <li>价格仅供参考，实际价格会因地区、血统、年龄等因素有所差异</li>
                    <li>建议实地考察，选择正规犬舍或宠物店</li>
                    <li>新手建议选择性格温顺、易训练的品种</li>
                    <li>养宠前请充分考虑时间、精力和经济能力</li>
                </ul>
            </div>
        </div>
        """
        
        logger.info(f"生成选购建议报告: 预算={budget}, 体型={size}")
        return html
    
    except Exception as e:
        logger.error(f"生成选购建议失败: {str(e)}")
        return f"❌ 生成报告失败: {str(e)}"


def generate_data_analysis_report(time_range: str = '30days') -> str:
    """
    生成数据分析报告
    
    Args:
        time_range: 时间范围 ('7days', '30days', '90days')
    
    Returns:
        HTML格式的数据分析报告
    """
    # 解析时间范围
    days_map = {
        '7days': 7,
        '30days': 30,
        '90days': 90
    }
    days = days_map.get(time_range, 30)
    
    try:
        # 统计数据
        # 1. 热门品种TOP10
        top_breeds_sql = text("""
            SELECT 
                dog_name,
                COUNT(*) as count,
                AVG(price) as avg_price
            FROM jd_dogs
            GROUP BY dog_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_breeds = db.session.execute(top_breeds_sql).fetchall()
        
        # 2. 价格分布
        price_dist_sql = text("""
            SELECT 
                CASE 
                    WHEN price < 1000 THEN '0-1000'
                    WHEN price < 3000 THEN '1000-3000'
                    WHEN price < 5000 THEN '3000-5000'
                    WHEN price < 10000 THEN '5000-10000'
                    ELSE '10000+'
                END as price_range,
                COUNT(*) as count
            FROM jd_dogs
            GROUP BY price_range
            ORDER BY price_range
        """)
        price_dist = db.session.execute(price_dist_sql).fetchall()
        
        # 3. 总体统计
        total_stats_sql = text("""
            SELECT 
                COUNT(*) as total_count,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                COUNT(DISTINCT dog_name) as breed_count
            FROM jd_dogs
        """)
        total_stats = db.session.execute(total_stats_sql).fetchone()
        
        # 生成HTML报告
        html = f"""
        <div class="report-container" style="padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h2 style="color: #2c3e50;">📊 数据分析报告</h2>
            <p style="color: #7f8c8d;">统计周期：最近{days}天 | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 24px; font-weight: bold; color: #3498db;">{total_stats.total_count}</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">总数据量</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 24px; font-weight: bold; color: #2ecc71;">¥{total_stats.avg_price:.0f}</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">平均价格</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">{total_stats.breed_count}</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">品种数量</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 24px; font-weight: bold; color: #f39c12;">¥{total_stats.min_price:.0f} - ¥{total_stats.max_price:.0f}</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">价格区间</div>
                </div>
            </div>
            
            <div style="margin-bottom: 30px;">
                <h3 style="color: #34495e;">🏆 热门品种 TOP 10</h3>
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #3498db; color: white;">
                            <th style="padding: 12px; text-align: left;">排名</th>
                            <th style="padding: 12px; text-align: left;">品种</th>
                            <th style="padding: 12px; text-align: right;">数量</th>
                            <th style="padding: 12px; text-align: right;">平均价格</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for idx, row in enumerate(top_breeds, 1):
            medal = ['🥇', '🥈', '🥉'][idx-1] if idx <= 3 else f'{idx}.'
            html += f"""
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px;">{medal}</td>
                            <td style="padding: 12px;"><strong>{row.dog_name}</strong></td>
                            <td style="padding: 12px; text-align: right;">{row.count}</td>
                            <td style="padding: 12px; text-align: right;">¥{row.avg_price:.0f}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div>
                <h3 style="color: #34495e;">💰 价格分布</h3>
                <div style="background: white; padding: 20px; border-radius: 8px;">
        """
        
        for row in price_dist:
            percentage = (row.count / total_stats.total_count * 100) if total_stats.total_count > 0 else 0
            html += f"""
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="font-weight: bold;">{row.price_range}元</span>
                            <span>{row.count}条 ({percentage:.1f}%)</span>
                        </div>
                        <div style="background: #ecf0f1; border-radius: 10px; height: 20px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #3498db, #2ecc71); width: {percentage}%; height: 100%; transition: width 0.3s;"></div>
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px;">
                <h4 style="color: #856404; margin-top: 0;">📝 数据洞察</h4>
                <ul style="margin-bottom: 0; color: #856404;">
                    <li>数据基于京东商城宠物狗销售记录</li>
                    <li>价格受季节、促销活动等因素影响会有波动</li>
                    <li>建议结合多个维度进行综合分析</li>
                </ul>
            </div>
        </div>
        """
        
        logger.info(f"生成数据分析报告: 时间范围={time_range}")
        return html
    
    except Exception as e:
        logger.error(f"生成数据分析报告失败: {str(e)}")
        return f"❌ 生成报告失败: {str(e)}"


@ai_bp.route('/api/ai/report/session/<int:session_id>', methods=['GET'])
@login_required
def get_session_report(session_id):
    """
    获取会话总结报告
    
    Args:
        session_id: 会话ID
    
    Returns:
        JSON格式的会话总结
    """
    try:
        # 验证会话归属
        session = ChatSession.query.get(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({'error': '无权访问该会话'}), 403
        
        summary = generate_session_summary(session_id)
        
        if 'error' in summary:
            return jsonify({'success': False, 'error': summary['error']}), 400
        
        return jsonify({
            'success': True,
            'data': summary
        })
    
    except Exception as e:
        logger.error(f"获取会话报告失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/report/purchase', methods=['POST'])
@login_required
def get_purchase_report():
    """
    获取宠物选购建议报告
    
    Request Body:
    {
        "budget": 5000,
        "size": "medium",
        "experience": "beginner",
        "purpose": "companion"
    }
    
    Returns:
        HTML格式的选购建议
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '缺少请求数据'}), 400
        
        report_html = generate_purchase_recommendation(data)
        
        return jsonify({
            'success': True,
            'html': report_html
        })
    
    except Exception as e:
        logger.error(f"生成选购建议报告失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/report/analysis', methods=['GET'])
@login_required
def get_analysis_report():
    """
    获取数据分析报告
    
    Query Params:
        time_range: 时间范围 (7days, 30days, 90days)
    
    Returns:
        HTML格式的数据分析报告
    """
    try:
        time_range = request.args.get('time_range', '30days')
        
        report_html = generate_data_analysis_report(time_range)
        
        return jsonify({
            'success': True,
            'html': report_html
        })
    
    except Exception as e:
        logger.error(f"生成数据分析报告失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
