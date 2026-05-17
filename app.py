"""
狗狗数据分析系统 - 主应用入口
重构版本：模块化、规范化、易维护
"""
import os
from flask import Flask, request
from flask_caching import Cache
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 导入本地模块
from config import get_config
from models import db, User
from errors import register_error_handlers
from charts import update_dashboard_summary

# 导入路由模块
from routes.main import main_bp
from routes.auth import auth_bp
from routes.api import api_bp
from routes.feedback import feedback_bp
from routes.analytics import analytics_bp
from routes.ai_assistant import ai_bp
from routes.ai_log_viewer import log_viewer_bp
from routes.pet_api import pet_api_bp
from routes.user_preference import preference_bp
from routes.alert_system import alert_bp

# 加载环境变量
load_dotenv()

# 初始化扩展
login_manager = LoginManager()
cache = Cache()
scheduler = APScheduler()
babel = Babel()
metrics = PrometheusMetrics(app=None)  # 稍后在 create_app 中初始化

# 标记调度器是否已启动
_scheduler_started = False


def create_app(config_name=None):
    """
    应用工厂函数
    支持多环境配置和测试隔离
    
    参数:
        config_name: 配置名称 ('development', 'production', 'testing', 'demo')
    """
    app = Flask(__name__)
    
    # 添加 MIME 类型配置，确保 JS 文件正确识别
    app.config['JSON_AS_ASCII'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存，方便开发调试
    
    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # 特殊处理演示模式
    if config_name == 'demo':
        from config_demo import DemoConfig
        app.config.from_object(DemoConfig)
    else:
        app.config.from_object(get_config(config_name))
    
    # 初始化扩展
    db.init_app(app)
    Migrate(app, db)  # 数据库迁移（Alembic）
    login_manager.init_app(app)
    cache.init_app(app)

    # 只在首次初始化scheduler
    if not scheduler.running:
        scheduler.init_app(app)
    
    # 设置 localeselector (Flask-Babel 4.0+ 使用新 API)
    def get_locale():
        # 1. 从 URL 参数获取
        lang = request.args.get('lang')
        if lang in app.config.get('BABEL_SUPPORTED_LOCALES', []):
            return lang
        
        # 2. 从 Session 获取
        from flask import session
        lang = session.get('language')
        if lang in app.config.get('BABEL_SUPPORTED_LOCALES', []):
            return lang
        
        # 3. 从请求头获取
        return request.accept_languages.best_match(
            app.config.get('BABEL_SUPPORTED_LOCALES', ['zh_CN'])
        ) or app.config['BABEL_DEFAULT_LOCALE']
    
    babel.init_app(app, locale_selector=get_locale)
    
    # 初始化 Prometheus 监控
    metrics.init_app(app)
    
    # CSRF 保护（API 路由可禁用）
    csrf = CSRFProtect(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 安全响应头和智能缓存控制
    @app.after_request
    def add_security_and_cache_headers(response):
        """添加安全响应头和智能缓存控制"""
        # 安全头
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 智能缓存策略
        path = request.path
        
        # 1. 静态资源缓存1小时（带版本号，可长期缓存）
        if path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=3600, immutable'
            response.headers['Expires'] = (datetime.utcnow() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 2. API数据缓存5分钟
        elif path.startswith('/api/') and request.method == 'GET':
            response.headers['Cache-Control'] = 'public, max-age=300'
            response.headers['Vary'] = 'Accept-Encoding'
        
        # 3. 图表页面缓存10分钟
        elif path.startswith('/chart/'):
            response.headers['Cache-Control'] = 'public, max-age=600'
        
        # 4. HTML页面不缓存（确保登录状态等实时性）
        else:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # 确保 JS 和 CSS 文件的 MIME 类型正确（必须在最后执行）
    @app.after_request
    def ensure_correct_mime_type(response):
        if request.path.endswith('.js'):
            response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        elif request.path.endswith('.css'):
            response.headers['Content-Type'] = 'text/css; charset=utf-8'
        return response
    
    # 登录管理器配置
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册路由蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(log_viewer_bp)
    app.register_blueprint(pet_api_bp)
    app.register_blueprint(preference_bp)
    app.register_blueprint(alert_bp)
    
    # 为API路由添加CSRF豁免
    csrf.exempt(api_bp)
    csrf.exempt(feedback_bp)
    csrf.exempt(analytics_bp)
    csrf.exempt(ai_bp)
    csrf.exempt(log_viewer_bp)
    csrf.exempt(pet_api_bp)
    
    # 启动定时任务
    start_scheduler(app)
    
    return app


def start_scheduler(app):
    """启动定时任务"""
    global _scheduler_started

    # 如果调度器已经在运行，跳过
    if scheduler.running:
        return

    try:
        with app.app_context():
            scheduler.add_job(
                id='update_summary',
                func=lambda: update_dashboard_summary(),
                trigger='interval',
                hours=6,
                replace_existing=True
            )
            scheduler.start()
            _scheduler_started = True
    except Exception as e:
        print(f"调度器启动警告: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
