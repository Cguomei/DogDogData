"""
演示模式配置
使用 SQLite 数据库，无需外部依赖，适合快速展示和部署
"""
import os
from config import Config


class DemoConfig(Config):
    """演示环境配置 - 使用 SQLite"""
    
    DEBUG = False  # 生产环境关闭调试
    
    # 使用 SQLite 数据库（文件存储在项目中）
    basedir = os.path.abspath(os.path.dirname(__file__))  # 项目根目录
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "demo.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # 禁用 CSRF（简化演示）
    WTF_CSRF_ENABLED = False
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 5分钟缓存
    
    # 安全配置（演示环境放宽）
    SESSION_COOKIE_SECURE = False
    
    # 日志级别
    LOG_LEVEL = 'INFO'


def get_demo_config():
    """获取演示配置"""
    return DemoConfig
