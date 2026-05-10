"""
Live2D 宠物智能交互 API
提供实时数据、时间问候、页面感知等功能
"""
from flask import Blueprint, jsonify
from datetime import datetime
import random

pet_api_bp = Blueprint('pet_api', __name__)


@pet_api_bp.route('/api/pet/greeting')
def get_greeting():
    """根据时间获取问候语"""
    hour = datetime.now().hour
    
    if hour < 6:
        return jsonify({
            'greeting': '夜深了，早点休息吧~ 🌙',
            'mood': 'sleepy'
        })
    elif hour < 9:
        return jsonify({
            'greeting': '早上好！新的一天开始啦~ ☀️',
            'mood': 'happy'
        })
    elif hour < 12:
        return jsonify({
            'greeting': '上午好！工作效率如何？ 💪',
            'mood': 'energetic'
        })
    elif hour < 14:
        return jsonify({
            'greeting': '中午好！记得休息一下哦~ 🍱',
            'mood': 'relaxed'
        })
    elif hour < 18:
        return jsonify({
            'greeting': '下午好！继续加油！ 📊',
            'mood': 'focused'
        })
    else:
        return jsonify({
            'greeting': '晚上好！今天辛苦了~ 🌟',
            'mood': 'tired'
        })


@pet_api_bp.route('/api/pet/data-summary')
def get_data_summary():
    """获取数据摘要（用于宠物对话）"""
    try:
        from charts import get_dog_food_stats, get_breed_distribution
        
        # 获取统计数据
        food_stats = get_dog_food_stats()
        breed_dist = get_breed_distribution()
        
        total_brands = food_stats.get('total_brands', 0)
        avg_price = food_stats.get('avg_price', 0)
        total_breeds = len(breed_dist) if isinstance(breed_dist, list) else 0
        
        # 生成有趣的对话
        messages = [
            f"你知道吗？目前有 {total_brands} 个狗粮品牌呢！",
            f"平均价格是 {avg_price} 元，你觉得贵吗？",
            f"我们记录了 {total_breeds} 种狗狗品种哦~",
            "数据每天都在增长，主人真棒！📈",
            "要不要看看最新的分析报告？"
        ]
        
        return jsonify({
            'success': True,
            'message': random.choice(messages),
            'stats': {
                'total_brands': total_brands,
                'avg_price': avg_price,
                'total_breeds': total_breeds
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '数据加载中...',
            'error': str(e)
        })


@pet_api_bp.route('/api/pet/page-tip/<page_name>')
def get_page_tip(page_name):
    """根据页面名称获取提示"""
    tips = {
        'home': [
            '欢迎回来！今天要分析什么数据呢？',
            '数据看板已就绪，开始探索吧！',
            '有什么可以帮助你的吗？'
        ],
        'charts': [
            '图表可以帮你发现数据规律哦~',
            '试试不同的图表类型吧！',
            '数据可视化让分析更简单！'
        ],
        'breeds': [
            '品种管理很重要呢！',
            '每个品种都有独特的特点~',
            '记得定期更新品种信息哦！'
        ],
        'food': [
            '狗粮数据很丰富呢！',
            '价格区间分布很有趣~',
            '要不要导出数据分析一下？'
        ],
        'custom-analysis': [
            '自定义分析功能很强大！',
            '上传数据后可以进行深度分析~',
            '试试不同的图表配置吧！'
        ],
        'ai-chat': [
            'AI助手可以回答各种问题哦~',
            '试试问它数据分析的问题！',
            '我是团团，它是AI，我们都很厉害！'
        ]
    }
    
    page_tips = tips.get(page_name, ['需要帮助吗？'])
    
    return jsonify({
        'tip': random.choice(page_tips),
        'page': page_name
    })


@pet_api_bp.route('/api/pet/interaction', methods=['POST'])
def record_interaction():
    """记录用户互动"""
    from flask import request
    
    data = request.get_json()
    action = data.get('action', 'unknown')
    
    # 这里可以记录到数据库或日志
    # 暂时只返回响应
    
    responses = {
        'feed': ['好吃！谢谢主人~ 🍖', '汪汪！好开心！', '能量满满！'],
        'pet': ['好舒服~ ❤️', '最喜欢主人了！', '蹭蹭~'],
        'play': ['真好玩！再来一次！ 🎾', '好开心呀！', '运动让我更健康！'],
        'click': ['嘿嘿~', '找我玩吗？', '我在呢！']
    }
    
    message = random.choice(responses.get(action, ['...']))
    
    return jsonify({
        'success': True,
        'message': message,
        'action': action
    })


@pet_api_bp.route('/api/pet/weather')
def get_weather_tip():
    """获取天气相关提示（模拟）"""
    # 实际项目中可以接入真实天气API
    weather_tips = [
        {'weather': 'sunny', 'tip': '今天天气真好，心情也变好了呢~ ☀️'},
        {'weather': 'rainy', 'tip': '下雨天适合在家分析数据哦~ 🌧️'},
        {'weather': 'cloudy', 'tip': '阴天也要保持好心情~ ☁️'},
    ]
    
    # 随机返回（实际应该根据真实天气）
    return jsonify(random.choice(weather_tips))
