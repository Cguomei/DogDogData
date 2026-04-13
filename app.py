"""
狗狗数据分析系统 - 主应用入口
重构版本：模块化、规范化、易维护
"""
import os
from flask import Flask, request
from flask_caching import Cache
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# 导入本地模块
from config import get_config
from models import db, User
from errors import register_error_handlers
from charts import update_dashboard_summary

# 导入路由模块
from routes.main import main_bp
from routes.auth import auth_bp
from routes.api import api_bp

# 加载环境变量
load_dotenv()

# 初始化扩展
login_manager = LoginManager()
cache = Cache()
scheduler = APScheduler()

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
        try:
            from config_demo import DemoConfig
        except ImportError:
            # 如果 config_demo 在 scripts 目录中
            import sys
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from config_demo import DemoConfig
        app.config.from_object(DemoConfig)
    else:
        app.config.from_object(get_config())
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    scheduler.init_app(app)
    
    # CSRF 保护（API 路由可禁用）
    csrf = CSRFProtect(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 安全响应头和缓存控制
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 禁用所有页面的缓存（开发模式）
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
    
    # 为API路由添加CSRF豁免
    csrf.exempt(api_bp)
    
    # 启动定时任务
    start_scheduler(app)
    
    return app


def start_scheduler(app):
    """启动定时任务"""
    global _scheduler_started
    
    # 如果调度器已经启动，跳过
    if _scheduler_started:
        return
    
    try:
        with app.app_context():
            # 检查调度器是否已经在运行
            if not scheduler.running:
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
        # 如果调度器启动失败，记录错误但不中断应用启动
        print(f"调度器启动警告: {e}")


# 创建应用实例（仅在非测试环境中自动创建）
if not os.getenv('TESTING'):
    app = create_app()
else:
    app = None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
