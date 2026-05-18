"""
配置管理模块
集中管理应用配置，支持多环境切换
"""

import os
import secrets
import warnings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """基础配置类"""

    # Flask 核心配置 — 生产环境务必从环境变量设置
    _secret_key = os.getenv("SECRET_KEY")
    if _secret_key:
        SECRET_KEY = _secret_key
    else:
        SECRET_KEY = secrets.token_hex(32)
        warnings.warn(
            "SECRET_KEY 未设置，已自动生成随机密钥。"
            "生产环境必须通过环境变量 SECRET_KEY 设置固定值！",
            RuntimeWarning,
        )

    # 数据库配置
    DB_USER = os.getenv("DB_USER", "doguser")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "dog")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 开发环境可设为 True 用于调试 SQL

    # JSON 配置
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    # CSRF 配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 小时
    WTF_CSRF_SSL_STRICT = True

    # 缓存配置
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 3600  # 默认缓存 1 小时

    # 上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大 16MB
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

    # 分页配置
    ITEMS_PER_PAGE = 20
    MAX_PAGE_SIZE = 100

    # API 配置
    API_RATE_LIMIT = {
        "default": "100/hour",  # 默认限流
        "auth": "10/minute",  # 认证接口限流
    }

    # JWT 配置（为 APP 预留）
    _jwt_secret = os.getenv("JWT_SECRET_KEY")
    if _jwt_secret:
        JWT_SECRET_KEY = _jwt_secret
    else:
        JWT_SECRET_KEY = secrets.token_hex(32)
        warnings.warn(
            "JWT_SECRET_KEY 未设置，已自动生成随机密钥。"
            "生产环境必须通过环境变量 JWT_SECRET_KEY 设置固定值！",
            RuntimeWarning,
        )
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 小时
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7  # 7 天

    # 国际化配置 (Flask-Babel)
    BABEL_DEFAULT_LOCALE = "zh_CN"
    BABEL_DEFAULT_TIMEZONE = "Asia/Shanghai"
    BABEL_SUPPORTED_LOCALES = ["zh_CN", "en_US", "ja_JP"]

    # 安全配置
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # HTTPS 环境下设为 True
    SESSION_COOKIE_SAMESITE = "Lax"

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = "WARNING"

    # 从环境变量读取数据库 URL（Railway/Render 等云平台提供）
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # Railway/Heroku 使用 postgres:// 前缀，需要替换为 postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL


class TestingConfig(Config):
    """测试环境配置（事务回滚隔离，无需独立数据库）"""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False


# 配置字典
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name=None):
    """根据环境变量获取配置"""
    env = config_name or os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
