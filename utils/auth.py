"""
API 认证模块
支持 Session 和 JWT Token 两种认证方式（为 APP 预留）
"""
from functools import wraps
from flask import request, jsonify, g, current_app
from models import User
import jwt
from datetime import datetime, timedelta


def token_required(f):
    """
    JWT Token 验证装饰器（为 APP 预留）
    用法：@app.route('/api/protected')
         @token_required
         def protected():
             return jsonify({'message': 'Success'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从 Header 中获取 Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Token 格式错误'
                }), 401
        
        # 如果没有 Token，尝试从 URL 参数获取（不推荐）
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': '缺少 Token'
            }), 401
        
        try:
            # 验证 Token
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # 获取用户
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 401
            
            # 将用户存入全局上下文
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token 已过期'
            }), 401
        
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': '无效的 Token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def _get_jwt_secret():
    """安全获取 JWT_SECRET_KEY，避免在应用上下文外调用时崩溃。"""
    try:
        return current_app.config['JWT_SECRET_KEY']
    except RuntimeError:
        raise RuntimeError(
            "generate_token / refresh_access_token 必须在 Flask 应用上下文中调用"
        )


def generate_token(user_id, expires_in=3600):
    """
    生成 JWT Token（为 APP 预留）
    
    Args:
        user_id: 用户 ID
        expires_in: 过期时间（秒），默认 1 小时
        
    Returns:
        access_token, refresh_token
    """
    secret = _get_jwt_secret()
    
    # Access Token
    access_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    access_token = jwt.encode(
        access_payload,
        secret,
        algorithm='HS256'
    )
    
    # Refresh Token（7 天有效期）
    refresh_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    refresh_token = jwt.encode(
        refresh_payload,
        secret,
        algorithm='HS256'
    )
    
    return access_token, refresh_token


def refresh_access_token(refresh_token_str):
    """
    使用 Refresh Token 刷新 Access Token（为 APP 预留）
    
    Args:
        refresh_token_str: Refresh Token
        
    Returns:
        new_access_token 或 None
    """
    try:
        data = jwt.decode(
            refresh_token_str,
            _get_jwt_secret(),
            algorithms=['HS256']
        )
        
        # 检查是否是 refresh token
        if data.get('type') != 'refresh':
            return None
        
        # 生成新的 access token
        return generate_token(data['user_id'])[0]
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required_api(f):
    """
    登录验证装饰器（兼容 Session 和 Token）
    优先使用 Token，如果没有 Token 则使用 Session
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 先尝试 Token 认证
        if 'Authorization' in request.headers or request.args.get('token'):
            return token_required(f)(*args, **kwargs)
        
        # 否则使用 Session 认证
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        g.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated



