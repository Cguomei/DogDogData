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
