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
    
    # 1. 价格查询
    if any(keyword in question_lower for keyword in ['价格', '多少钱', '价位', '售价']):
        breed = extract_breed_name(question)
        return {
            'type': 'price_query',
            'params': {'breed': breed}
        }
    
    # 2. 品种信息查询
    elif any(keyword in question_lower for keyword in ['介绍', '特点', '习性', '寿命']):
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


def extract_breed_name(question: str) -> str:
    """提取品种名称（简化版）"""
    common_breeds = [
        '金毛', '泰迪', '柯基', '哈士奇', '拉布拉多', 
        '柴犬', '边境牧羊犬', '萨摩耶', '阿拉斯加', '贵宾',
        '比熊', '博美', '雪纳瑞', '斗牛犬', '约克夏'
    ]
    
    for breed in common_breeds:
        if breed in question:
            return breed
    
    return '未知品种'


def extract_multiple_breeds(question: str) -> list:
    """提取多个品种名称"""
    common_breeds = [
        '金毛', '泰迪', '柯基', '哈士奇', '拉布拉多',
        '柴犬', '边境牧羊犬', '萨摩耶', '阿拉斯加', '贵宾',
        '比熊', '博美', '雪纳瑞', '斗牛犬', '约克夏'
    ]
    
    found_breeds = [breed for breed in common_breeds if breed in question]
    return found_breeds[:2]  # 最多2个


# ===== 数据查询处理器 =====

def handle_price_query(params: dict) -> str:
    """处理价格查询"""
    breed = params.get('breed')
    
    if not breed or breed == '未知品种':
        logger.warning("价格查询: 未指定有效品种")
        return "请告诉我您想查询哪个品种的价格？例如：金毛、泰迪、柯基等"
    
    logger.info(f"价格查询: 品种={breed}")
    
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


def handle_breed_info(params: dict) -> str:
    """处理品种信息查询"""
    breed = params.get('breed')
    
    if not breed or breed == '未知品种':
        logger.warning("品种查询: 未指定有效品种")
        return "请告诉我您想了解哪个品种？例如：金毛、泰迪等"
    
    logger.info(f"品种查询: {breed}")
    
    # 查询数据库
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


def handle_recommendation(params: dict) -> str:
    """处理推荐问题"""
    # 使用本地模型生成个性化推荐
    prompt = """
    你是一个专业的宠物顾问。请根据用户的需求推荐适合的犬种。
    
    要求：
    1. 推荐3-5个品种
    2. 说明推荐理由
    3. 给出简要的养护建议
    4. 语气友好专业
    
    用户需求：适合新手养的狗狗
    """
    
    messages = [
        {"role": "system", "content": "你是宠物顾问专家"},
        {"role": "user", "content": prompt}
    ]
    
    return call_local_model(messages)


def handle_comparison(params: dict) -> str:
    """处理对比问题"""
    breeds = params.get('breeds', [])
    
    if len(breeds) < 2:
        return "请告诉我要对比哪两个品种？例如：金毛和泰迪"
    
    breed1, breed2 = breeds[0], breeds[1]
    
    # 调用本地模型进行对比分析
    prompt = f"""
    请对比以下两个犬种，从以下几个方面分析：
    1. 性格特点
    2. 体型大小
    3. 养护难度
    4. 适合人群
    5. 价格区间
    
    犬种：{breed1} vs {breed2}
    
    请用清晰的格式呈现对比结果，并给出选择建议。
    """
    
    messages = [
        {"role": "system", "content": "你是宠物对比分析专家"},
        {"role": "user", "content": prompt}
    ]
    
    return call_local_model(messages)


def handle_general_qa(question: str, context: list = None) -> str:
    """处理通用问答（支持上下文）"""
    messages = [
        {"role": "system", "content": "你是宠物知识专家，回答要简洁专业"}
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
    prompt = f"请介绍一下{breed}犬的特点，包括性格、体型、养护难度等。"
    
    messages = [
        {"role": "system", "content": "你是宠物专家"},
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


def auto_learn_from_answer(question: str, answer: str, question_type: str) -> bool:
    """
    自动学习：将模型的优质回答加入知识库
    
    Args:
        question: 用户问题
        answer: AI回答
        question_type: 问题类型
    
    Returns:
        是否成功加入知识库
    """
    try:
        from utils.knowledge_base import get_knowledge_base
        
        kb = get_knowledge_base()
        
        # 简单的质量判断：回答长度 > 50字符才考虑学习
        if len(answer) < 50:
            logger.info(f"回答过短，跳过学习: {len(answer)}字符")
            return False
        
        # 检查是否已存在类似问题
        existing = kb.search(question, question_type)
        if existing:
            logger.info(f"知识库已存在类似问题，跳过学习")
            return False
        
        # 提取关键词作为知识标题
        keywords = extract_keywords(question)
        title = f"{question_type}: {keywords}"
        
        # 添加到知识库
        success = kb.add_knowledge(
            title=title,
            question=question,
            answer=answer,
            category=question_type,
            confidence=0.7  # 自动学习的置信度较低
        )
        
        if success:
            logger.info(f"✅ 自动学习成功: {title}")
        else:
            logger.warning(f"⚠️ 自动学习失败")
        
        return success
    
    except Exception as e:
        logger.error(f"自动学习异常: {str(e)}")
        return False


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
@login_required
def ai_chat():
    """
    AI聊天接口（本地模型版）
    
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
        # 记录请求信息
        logger.info(f"[{request_id}] 收到AI聊天请求")
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
            session = ChatSession(
                user_id=current_user.id,
                title=user_message[:50]  # 用第一条消息作为标题
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
            logger.info(f"[{request_id}] 创建新会话: ID={session_id}")
        else:
            # 验证会话归属
            session = ChatSession.query.get(session_id)
            if not session or session.user_id != current_user.id:
                return jsonify({'error': '无权访问该会话'}), 403
        
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
            logger.info(f"[{request_id}] ✅ 知识库命中，直接使用")
            logger.info(f"[{request_id}] 生成回复成功，长度: {len(answer)}字符")
            logger.info(f"[{request_id}] 回复内容: {answer[:200]}...")
            
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
            except Exception as e:
                db.session.rollback()
                logger.error(f"[{request_id}] 保存对话历史失败: {str(e)}")
            
            return jsonify({
                'success': True,
                'answer': answer,
                'type': question_type,
                'source': 'knowledge_base',
                'session_id': session_id
            })
        else:
            logger.info(f"[{request_id}] 🔍 知识库未命中，调用模型")
        
        # Step 2: 根据类型处理（模型调用）
        answer = ""
        if question_type == 'price_query':
            logger.info(f"[{request_id}] 处理价格查询: {params.get('breed')}")
            answer = handle_price_query(params)
        elif question_type == 'breed_info':
            logger.info(f"[{request_id}] 处理品种信息: {params.get('breed')}")
            answer = handle_breed_info(params)
        elif question_type == 'recommendation':
            logger.info(f"[{request_id}] 处理推荐请求")
            answer = handle_recommendation(params)
        elif question_type == 'comparison':
            logger.info(f"[{request_id}] 处理对比请求: {params.get('breeds')}")
            answer = handle_comparison(params)
        else:  # general_qa
            logger.info(f"[{request_id}] 处理通用问答")
            # 获取上下文历史
            context = get_conversation_context(session_id, max_messages=10)
            answer = handle_general_qa(user_message, context)
        
        logger.info(f"[{request_id}] 生成回复成功，长度: {len(answer)}字符")
        logger.info(f"[{request_id}] 回复内容: {answer[:200]}...")
        
        # Step 3: 保存对话历史
        import time
        start_time = time.time()
        
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
            'session_id': session_id
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"[{request_id}] AI聊天错误: {str(e)}")
        logger.error(f"[{request_id}] 堆栈跟踪:\n{error_trace}")
        logger.error(f"[{request_id}] 请求数据: {data if 'data' in locals() else 'N/A'}")
        logger.error(f"[{request_id}] 用户: {current_user.username if current_user.is_authenticated else '未登录'}")
        
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@ai_bp.route('/ai-chat')
@login_required
def ai_chat_page():
    """AI聊天页面"""
    return render_template('ai_chat.html')


@ai_bp.route('/ai-knowledge')
@login_required
def knowledge_base_page():
    """知识库管理页面"""
    return render_template('knowledge_base.html')


@ai_bp.route('/api/ai/model/status')
@login_required
def model_status():
    """检查本地模型状态"""
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
@login_required
def knowledge_stats():
    """获取知识库统计信息"""
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
@login_required
def get_sessions():
    """获取当前用户的对话会话列表"""
    try:
        sessions = ChatSession.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(
            ChatSession.updated_at.desc()
        ).limit(50).all()  # 最多返回50个会话
        
        return jsonify({
            'success': True,
            'sessions': [s.to_dict() for s in sessions]
        })
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions', methods=['POST'])
@login_required
def create_session():
    """创建新的对话会话"""
    try:
        data = request.get_json()
        title = data.get('title', '新对话')
        
        session = ChatSession(
            user_id=current_user.id,
            title=title
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"创建新会话: ID={session.id}, 用户={current_user.username}")
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'title': session.title
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建会话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/ai/sessions/<int:session_id>')
@login_required
def get_session(session_id):
    """获取指定会话的详细信息"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # 权限检查
        if session.user_id != current_user.id:
            return jsonify({'error': '无权访问'}), 403
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
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
@login_required
def delete_session(session_id):
    """删除指定会话"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # 权限检查
        if session.user_id != current_user.id:
            return jsonify({'error': '无权访问'}), 403
        
        # 软删除（标记为非活跃）
        session.is_active = False
        db.session.commit()
        
        logger.info(f"删除会话: ID={session_id}, 用户={current_user.username}")
        
        return jsonify({
            'success': True,
            'message': '会话已删除'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除会话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
