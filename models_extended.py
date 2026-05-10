"""
扩展数据模型
包含用户扩展信息、APP Token、收藏等
"""
from models import db
from datetime import datetime
import uuid


class UserProfile(db.Model):
    """用户扩展信息表"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # 基本信息
    nickname = db.Column(db.String(80))  # 昵称
    avatar_url = db.Column(db.String(255))  # 头像 URL
    gender = db.Column(db.Enum('男', '女', '保密'), default='保密')
    phone = db.Column(db.String(20))  # 手机号（为 APP 预留）
    email = db.Column(db.String(120))  # 邮箱
    
    # 扩展信息
    bio = db.Column(db.Text)  # 个人简介
    location = db.Column(db.String(100))  # 所在地
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # 关联
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def to_dict(self):
        """转换为字典（为 API 准备）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'bio': self.bio,
            'location': self.location,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class AppToken(db.Model):
    """APP 访问 Token 表（为 APP 预留）"""
    __tablename__ = 'app_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Token 信息
    access_token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    refresh_token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    
    # Token 元数据
    device_id = db.Column(db.String(100))  # 设备 ID
    device_name = db.Column(db.String(100))  # 设备名称
    app_version = db.Column(db.String(20))  # APP 版本
    platform = db.Column(db.String(20))  # 平台：iOS/Android
    
    # Token 状态
    expires_at = db.Column(db.DateTime, nullable=False)  # 过期时间
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_used_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 关联
    user = db.relationship('User', backref=db.backref('tokens', lazy='dynamic'))
    
    @staticmethod
    def generate_token():
        """生成随机 Token"""
        return str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
    
    def to_dict(self):
        """转换为字典（不返回敏感信息）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'platform': self.platform,
            'app_version': self.app_version,
            'expires_at': self.expires_at.strftime('%Y-%m-%d %H:%M:%S') if self.expires_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_used_at': self.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_used_at else None
        }


class UserFavorite(db.Model):
    """用户收藏表（狗狗品种收藏）"""
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('dog_breeds.id'), nullable=False)
    
    # 备注
    note = db.Column(db.String(255))
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 唯一约束（同一用户不能重复收藏同一品种）
    __table_args__ = (
        db.UniqueConstraint('user_id', 'breed_id', name='unique_user_breed'),
    )
    
    # 关联
    user = db.relationship('User', backref=db.backref('favorites', lazy='dynamic'))
    breed = db.relationship('DogBreed', backref=db.backref('favorited_by', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'breed_id': self.breed_id,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'breed': self.breed.to_dict() if self.breed else None
        }


class UserActivityLog(db.Model):
    """用户活动日志表（用于分析和安全审计）"""
    __tablename__ = 'user_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 活动信息
    action_type = db.Column(db.String(50), nullable=False)  # 操作类型：login, view, create, update, delete
    target_type = db.Column(db.String(50))  # 目标类型：breed, food, user
    target_id = db.Column(db.Integer)  # 目标 ID
    
    # 请求信息
    ip_address = db.Column(db.String(45))  # IP 地址
    user_agent = db.Column(db.String(500))  # User-Agent
    request_method = db.Column(db.String(10))  # GET/POST/PUT/DELETE
    
    # 结果
    status_code = db.Column(db.Integer)  # HTTP 状态码
    error_message = db.Column(db.Text)  # 错误消息
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 索引（便于查询）
    __table_args__ = (
        db.Index('idx_user_action', 'user_id', 'action_type'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    # 关联
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'ip_address': self.ip_address,
            'request_method': self.request_method,
            'status_code': self.status_code,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Feedback(db.Model):
    """用户反馈表"""
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 反馈内容
    feedback_type = db.Column(
        db.Enum('bug', 'feature', 'improvement', 'other'),
        default='other',
        nullable=False
    )  # 反馈类型
    title = db.Column(db.String(200))  # 标题
    content = db.Column(db.Text, nullable=False)  # 详细内容
    
    # 附件
    screenshot_url = db.Column(db.String(500))  # 截图 URL
    attachment_url = db.Column(db.String(500))  # 附件 URL
    
    # 联系信息
    contact_email = db.Column(db.String(120))  # 联系邮箱
    contact_phone = db.Column(db.String(20))  # 联系电话
    
    # 状态
    status = db.Column(
        db.Enum('pending', 'processing', 'resolved', 'closed'),
        default='pending',
        nullable=False
    )  # 处理状态
    
    # 管理员回复
    admin_reply = db.Column(db.Text)  # 管理员回复
    replied_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 回复人 ID
    replied_at = db.Column(db.DateTime)  # 回复时间
    
    # 优先级
    priority = db.Column(
        db.Enum('low', 'medium', 'high', 'critical'),
        default='medium'
    )  # 优先级
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # 索引
    __table_args__ = (
        db.Index('idx_user_feedback', 'user_id', 'created_at'),
        db.Index('idx_status', 'status'),
        db.Index('idx_type', 'feedback_type'),
    )
    
    # 关联
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('feedbacks_submitted', lazy='dynamic'))
    replier = db.relationship('User', foreign_keys=[replied_by], backref=db.backref('feedbacks_replied', lazy='dynamic'))
    
    def to_dict(self, include_user=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'title': self.title,
            'content': self.content,
            'screenshot_url': self.screenshot_url,
            'attachment_url': self.attachment_url,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'priority': self.priority,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'replied_at': self.replied_at.strftime('%Y-%m-%d %H:%M:%S') if self.replied_at else None,
        }
        
        if include_user and self.user:
            data['username'] = self.user.username
        
        if self.replier:
            data['replied_by_name'] = self.replier.username
        
        return data


class UserEvent(db.Model):
    """用户事件埋点表"""
    __tablename__ = 'user_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 可为空（未登录用户）
    
    # 事件信息
    event_name = db.Column(db.String(100), nullable=False, index=True)  # 事件名称
    event_category = db.Column(db.String(50), index=True)  # 事件分类：page_view, click, api_call, error
    event_label = db.Column(db.String(200))  # 事件标签（额外描述）
    
    # 页面信息
    page_url = db.Column(db.String(500))  # 页面 URL
    page_title = db.Column(db.String(200))  # 页面标题
    referrer = db.Column(db.String(500))  # 来源页面
    
    # 设备信息
    device_type = db.Column(db.String(20))  # desktop, mobile, tablet
    browser = db.Column(db.String(50))  # Chrome, Firefox, Safari
    os = db.Column(db.String(50))  # Windows, macOS, iOS, Android
    screen_resolution = db.Column(db.String(20))  # 1920x1080
    
    # 位置信息
    ip_address = db.Column(db.String(45))  # IP 地址
    country = db.Column(db.String(50))  # 国家
    city = db.Column(db.String(100))  # 城市
    
    # 会话信息
    session_id = db.Column(db.String(100), index=True)  # 会话 ID
    
    # 自定义属性（JSON 格式）
    properties = db.Column(db.Text)  # JSON 字符串，存储额外属性
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    
    # 索引
    __table_args__ = (
        db.Index('idx_event_name_time', 'event_name', 'created_at'),
        db.Index('idx_user_session', 'user_id', 'session_id'),
        db.Index('idx_category', 'event_category'),
    )
    
    # 关联
    user = db.relationship('User', backref=db.backref('events', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典"""
        import json
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_name': self.event_name,
            'event_category': self.event_category,
            'event_label': self.event_label,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'referrer': self.referrer,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'screen_resolution': self.screen_resolution,
            'ip_address': self.ip_address,
            'country': self.country,
            'city': self.city,
            'session_id': self.session_id,
            'properties': json.loads(self.properties) if self.properties else {},
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


# 辅助函数
def get_user_profile(user_id):
    """获取用户资料"""
    return UserProfile.query.filter_by(user_id=user_id).first()


def create_app_token(user_id, device_info=None):
    """创建 APP Token"""
    from datetime import timedelta
    
    access_token = AppToken.generate_token()
    refresh_token = AppToken.generate_token()
    
    # 设置过期时间（access_token: 1 小时，refresh_token: 7 天）
    now = datetime.utcnow()
    access_expires = now + timedelta(hours=1)
    refresh_expires = now + timedelta(days=7)
    
    token = AppToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=access_expires,
        **device_info if device_info else {}
    )
    
    db.session.add(token)
    db.session.commit()
    
    return token


class ChatSession(db.Model):
    """AI对话会话表"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 会话信息
    title = db.Column(db.String(200))  # 会话标题（自动生成或用户设置）
    is_active = db.Column(db.Boolean, default=True)  # 是否活跃
    
    # 统计信息
    message_count = db.Column(db.Integer, default=0)  # 消息数量
    last_message_at = db.Column(db.DateTime)  # 最后消息时间
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # 索引
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
    )
    
    # 关联
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy='dynamic'))
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'is_active': self.is_active,
            'message_count': self.message_count,
            'last_message_at': self.last_message_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_message_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class ChatMessage(db.Model):
    """AI对话消息表"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # 消息内容
    role = db.Column(db.Enum('user', 'assistant', 'system'), nullable=False)  # 角色
    content = db.Column(db.Text, nullable=False)  # 消息内容
    
    # 元数据
    question_type = db.Column(db.String(50))  # 问题类型（price_query, breed_info等）
    source = db.Column(db.String(50))  # 来源：knowledge_base 或 model
    response_time = db.Column(db.Float)  # 响应时间（秒）
    
    # 反馈
    feedback = db.Column(db.Enum('like', 'dislike'))  # 用户反馈（可为NULL）
    feedback_comment = db.Column(db.Text)  # 反馈备注
    
    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 索引
    __table_args__ = (
        db.Index('idx_session_created', 'session_id', 'created_at'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'question_type': self.question_type,
            'source': self.source,
            'response_time': self.response_time,
            'feedback': self.feedback,
            'feedback_comment': self.feedback_comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
