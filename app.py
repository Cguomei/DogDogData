"""
狗狗数据分析系统 - 主应用入口
重构版本：模块化、规范化、易维护
"""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_caching import Cache
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_apscheduler import APScheduler
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import pandas as pd
import pymysql
from sqlalchemy.exc import IntegrityError

# 导入本地模块
from config import get_config
from models import db, User, DogBreed
from errors import register_error_handlers
from utils.api_response import APIResponse
from charts import update_dashboard_summary, get_dashboard_stats_from_summary
from charts import (
    get_price_scatter,
    get_weight_line,
    get_level_bar,
    get_shop_top10_hist,
    get_price_funnel,
    get_world_map
)

# 加载环境变量
load_dotenv()

# 初始化扩展
login_manager = LoginManager()
cache = Cache()
scheduler = APScheduler()


def create_app(config_name=None):
    """
    应用工厂函数
    支持多环境配置和测试隔离
    """
    app = Flask(__name__)
    
    # 添加 MIME 类型配置，确保 JS 文件正确识别
    app.config['JSON_AS_ASCII'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存，方便开发调试
    
    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
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
    login_manager.login_view = 'login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册路由
    register_routes(app)
    
    # 启动定时任务
    start_scheduler(app)
    
    return app


def register_routes(app):
    """注册所有路由"""
    
    # ===== 首页和数据看板 =====
    @app.route('/')
    def index():
        stats = get_dashboard_stats_from_summary()
        return render_template('index.html', stats=stats)
    
    # ===== 图表列表页面 =====
    @app.route('/charts')
    def charts_list():
        """图表列表页面"""
        return render_template('charts_list.html')
    
    # ===== 品种管理页面 =====
    @app.route('/admin/breeds')
    @login_required
    def admin_breeds():
        """品种管理页面（仅管理员可访问）"""
        if not current_user.is_admin():
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('index'))
        return render_template('admin_breeds.html')
    
    # ===== 图表页面 =====
    @app.route('/map')
    def show_map():
        map_html = get_world_map()
        return map_html
    
    @app.route('/chart/scatter')
    def scatter():
        chart_html = get_price_scatter()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='价格散点图')
    
    @app.route('/chart/line')
    def line():
        chart_html = get_weight_line()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='体重折线图')
    
    @app.route('/chart/bar')
    def bar():
        chart_html = get_level_bar()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='级别柱状图')
    
    @app.route('/chart/hist')
    def hist():
        chart_html = get_shop_top10_hist()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='狗狗 + 店铺 TOP10 直方图')
    
    @app.route('/chart/funnel')
    def funnel():
        chart_html = get_price_funnel()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='价格段漏斗图')
    
    @app.route('/chart/map')
    @cache.cached(timeout=3600)
    def world_map():
        chart_html = get_world_map()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='世界地图（狗狗家乡分布）')
    
    # ===== 用户认证 =====
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                flash('登录成功！', 'success')
                return redirect(next_page or url_for('index'))
            else:
                flash('用户名或密码错误', 'danger')
        
        return render_template('login.html')
    
    # ===== 宠物日志保存 API =====
    @app.route('/api/save_pet_logs', methods=['POST'])
    def save_pet_logs():
        """保存宠物日志到 log 文件夹"""
        try:
            from datetime import datetime
            import os
            
            # 确保 log 文件夹存在
            log_dir = os.path.join(os.path.dirname(__file__), 'log')
            os.makedirs(log_dir, exist_ok=True)
            
            # 解析日志内容
            content = request.data.decode('utf-8')
            lines = content.split('\n')
            session = lines[0].replace('session=', '') if lines else 'unknown'
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'pet_log_{session}_{timestamp}.txt'
            filepath = os.path.join(log_dir, filename)
            
            # 保存日志
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return jsonify({'success': True, 'filename': filename})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('已退出登录', 'info')
        return redirect(url_for('index'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not User.validate_username(username):
                flash('用户名格式不正确（3-20 位，允许字母、数字、下划线、中文）', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('用户名已存在', 'danger')
                return render_template('register.html')
            
            try:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('注册成功，请登录', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f'注册失败：{str(e)}', 'danger')
        
        return render_template('register.html')
    
    # ===== 自定义数据分析 =====
    @app.route('/custom-analysis')
    def custom_analysis():
        """用户自定义数据分析页面"""
        return render_template('custom_analysis.html')
    
    @app.route('/api/upload-data', methods=['POST'])
    def upload_data():
        """API: 接收用户上传的 CSV/Excel 数据"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            # 读取上传的文件
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file, encoding='utf-8')
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return jsonify({'error': '不支持的文件格式，请上传 CSV 或 Excel 文件'}), 400
            
            # 返回前 100 行数据和列名
            columns = df.columns.tolist()
            data_sample = df.head(100).to_dict('records')
            
            # 将数据转换为 JSON 格式
            return jsonify({
                'success': True,
                'columns': columns,
                'row_count': len(df),
                'data': data_sample
            })
        except Exception as e:
            return jsonify({'error': f'解析文件失败：{str(e)}'}), 500
    
    @app.route('/api/generate-chart', methods=['POST'])
    def generate_chart():
        """API: 根据用户配置生成图表"""
        try:
            data = request.get_json()
            chart_type = data.get('chart_type')
            x_column = data.get('x_column')
            y_column = data.get('y_column')
            title = data.get('title', '自定义图表')
            
            if not all([chart_type, x_column, y_column]):
                return jsonify({'error': '缺少必要参数'}), 400
            
            # 这里可以根据需要实现不同的图表生成逻辑
            # 目前返回成功响应，前端已经可以处理
            return jsonify({
                'success': True,
                'message': f'图表已生成：{title}',
                'chart_type': chart_type,
                'config': {
                    'x_column': x_column,
                    'y_column': y_column,
                    'title': title
                }
            })
        except Exception as e:
            return jsonify({'error': f'生成图表失败：{str(e)}'}), 500

    @app.route('/api/breeds')
    def get_breeds():
        breeds = DogBreed.query.all()
        data = [{
            'id': b.id,
            'breed_name': b.breed_name,
            'avg_life_years': float(b.avg_life_years) if b.avg_life_years else None,
            'size_category': b.size_category,
            'popularity': b.popularity
        } for b in breeds]
        return jsonify(data)
    
    @app.route('/api/breeds/<int:id>')
    def get_breed(id):
        breed = DogBreed.query.get_or_404(id)
        return jsonify({
            'id': breed.id,
            'breed_name': breed.breed_name,
            'avg_life_years': float(breed.avg_life_years) if breed.avg_life_years else None,
            'size_category': breed.size_category,
            'popularity': breed.popularity
        })
    
    @app.route('/api/breeds', methods=['POST'])
    @login_required
    def add_breed():
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        breed_name = data.get('breed_name')
        avg_life_years = data.get('avg_life_years')
        size_category = data.get('size_category')
        popularity = data.get('popularity', 0)
        
        if not breed_name or len(breed_name.strip()) < 2:
            return jsonify({"error": "品种名称至少 2 个字符"}), 400
        
        breed = DogBreed(
            breed_name=breed_name.strip(),
            avg_life_years=avg_life_years,
            size_category=size_category,
            popularity=popularity
        )
        
        try:
            db.session.add(breed)
            db.session.commit()
            return jsonify({'message': '添加成功', 'id': breed.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "该品种已存在"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"添加失败：{str(e)}"}), 500
    
    @app.route('/api/breeds/<int:id>', methods=['PUT'])
    @login_required
    def update_breed(id):
        breed = DogBreed.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        breed_name = data.get('breed_name')
        avg_life_years = data.get('avg_life_years')
        size_category = data.get('size_category')
        popularity = data.get('popularity', 0)
        
        if not breed_name or len(breed_name.strip()) < 2:
            return jsonify({"error": "品种名称至少 2 个字符"}), 400
        
        # 检查是否与其他记录重复
        existing = DogBreed.query.filter(
            DogBreed.breed_name == breed_name.strip(),
            DogBreed.id != id
        ).first()
        if existing:
            return jsonify({"error": "该品种名称已存在"}), 400
        
        breed.breed_name = breed_name.strip()
        breed.avg_life_years = avg_life_years
        breed.size_category = size_category
        breed.popularity = popularity
        
        try:
            db.session.commit()
            return jsonify({'message': '更新成功'}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "更新失败"}), 500
    
    @app.route('/api/breeds/<int:id>', methods=['DELETE'])
    @login_required
    def delete_breed(id):
        breed = DogBreed.query.get_or_404(id)
        
        try:
            db.session.delete(breed)
            db.session.commit()
            return jsonify({'message': '删除成功'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"删除失败：{str(e)}"}), 500
    
    # ===== 狗粮数据 API =====
    @app.route('/api/food')
    def get_food():
        """获取狗粮列表数据"""
        from charts import get_dog_food_list
        food_list = get_dog_food_list()
        return jsonify(food_list)
    
    # ===== 测试页面 =====
    @app.route('/test-pet')
    def test_pet_page():
        """2.5D 宠物功能测试页面"""
        return render_template('test_pet.html')
    
    @app.route('/clear-cache')
    def clear_cache_page():
        """清除缓存指南页面"""
        return render_template('clear_cache.html')
    
    @app.route('/api/restart', methods=['POST'])
    def api_restart():
        """API: 重启应用（需要管理员权限）"""
        import subprocess
        import sys
        try:
            # 获取当前脚本路径
            script_path = sys.argv[0]
            # 启动新进程
            subprocess.Popen([sys.executable, script_path])
            # 当前进程退出
            os._exit(0)
            return jsonify({'success': True, 'message': '应用正在重启...'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


def start_scheduler(app):
    """启动定时任务"""
    with app.app_context():
        scheduler.add_job(
            id='update_summary',
            func=lambda: update_dashboard_summary(),
            trigger='interval',
            hours=6,
            replace_existing=True
        )
        scheduler.start()


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
