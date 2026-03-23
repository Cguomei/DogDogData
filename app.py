import os
from http.client import responses

import pandas as pd
import requests
from werkzeug.utils import secure_filename
import pymysql, charts
from flask import Flask, render_template, request, jsonify
from charts import get_dashboard_stats
from flask_caching import Cache
from models import db
from models import DogBreed
from charts import get_dog_food_stats
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from flask_apscheduler import APScheduler
from charts import update_dashboard_summary
from dotenv import load_dotenv
load_dotenv()  # 这行会加载 .env 文件中的变量到环境变量
# 从 charts.py 导入所有图表生成函数
from charts import (
    get_price_scatter,  # 价格散点图
    get_weight_line,  # 体重折线图
    get_level_bar,  # 级别柱状图
    get_shop_top10_hist,  # 狗狗+店铺TOP10直方图
    get_price_funnel,  # 价格段漏斗图
    get_world_map  # 狗狗家乡世界地图
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 请改为一个随机字符串，用于加密 session

# app.py mysql 配置
# app.config['DB_HOST'] = 'localhost'
# app.config['DB_USER'] = 'root'
# app.config['DB_PASSWORD'] = '123456'
# app.config['DB_NAME'] = 'dog'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/dog'
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'dog')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

db.init_app(app)
app.config['JSON_AS_ASCII'] = False

with app.app_context():
    db.create_all()   # 会自动创建表（如果表不存在）




# ... 其他配置
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未登录时跳转到的视图
login_manager.login_message = '请先登录'

from charts import get_dashboard_stats_from_summary

@app.route('/')
def index():
    stats = get_dashboard_stats_from_summary()
    return render_template('index.html', stats=stats)

# @app.route('/')
# def index():
#     stats = get_dashboard_stats()
#     return render_template('index.html', stats=stats)


@app.route('/map')
def show_map():
    # 获取地图 HTML
    map_html = get_world_map()
    # 直接返回 HTML 内容，Flask 会自动识别为 text/html
    return map_html


# @app.route('/chart/scatter')
# def scatter():
#     """价格散点图"""
#     return get_price_scatter()
# # app.py 需要修改的部分（以价格散点图为例）
# from flask import render_template

@app.route('/chart/scatter')
def scatter():
    chart_html = get_price_scatter()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='价格散点图')

@app.route('/chart/line')
def line():
    """体重折线图"""
    chart_html = get_weight_line()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='体重折线图')

@app.route('/chart/bar')
def bar():
    """级别柱状图"""
    chart_html = get_level_bar()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='级别柱状图')

@app.route('/chart/hist')
def hist():
    """狗狗+店铺TOP10直方图"""
    chart_html = get_shop_top10_hist()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='狗狗+店铺TOP10直方图')


@app.route('/chart/funnel')
def funnel():
    """价格段漏斗图"""
    chart_html = get_price_funnel()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='价格段漏斗图')

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@app.route('/chart/map')
@cache.cached(timeout=3600)  # 缓存1小时
def world_map():
    """世界地图（狗狗家乡分布）"""
    chart_html = get_world_map()
    return render_template('chart_page.html',
                           chart_html=chart_html,
                           chart_title='世界地图（狗狗家乡分布）')

# 404 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404

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

@app.route('/api/breeds', methods=['POST'])
def add_breed():
    data = request.get_json()

    # 提取前端传来的数据（使用 get 避免 KeyError）
    breed_name = data.get('breed_name')
    avg_life_years = data.get('avg_life_years')
    size_category = data.get('size_category')
    popularity = data.get('popularity', 0)  # 默认 0

    # 1. 先检查是否已存在（提升用户体验）
    existing_breed = DogBreed.query.filter_by(breed_name=breed_name).first()
    if existing_breed:
        return jsonify({"error": f"犬种 '{breed_name}' 已存在"}), 400

    # 2. 创建新对象
    new_breed = DogBreed(
        breed_name=breed_name,
        avg_life_years=avg_life_years,
        size_category=size_category,
        popularity=popularity
    )
    db.session.add(new_breed)

    # 3. 提交，并捕获可能的唯一性异常（应对并发）
    try:
        db.session.commit()
        return jsonify({"message": "添加成功", "id": new_breed.id}), 201
    except IntegrityError as e:
        db.session.rollback()
        # 检查是否真的是唯一约束冲突
        if 'Duplicate entry' in str(e):
            return jsonify({"error": f"犬种 '{breed_name}' 已存在"}), 400
        else:
            # 其他完整性错误（如外键、NOT NULL等）
            return jsonify({"error": "数据库错误，请检查输入数据"}), 500

#
# @app.route('/api/breeds', methods=['POST'])
# def add_breed():
#     data = request.get_json()
#     new_breed = DogBreed(
#         breed_name=data['breed_name'],
#         avg_life_years=data.get('avg_life_years'),
#         size_category=data.get('size_category'),
#         popularity=data.get('popularity', 0)
#     )
#     db.session.add(new_breed)
#     db.session.commit()
#     return jsonify({'message': '添加成功', 'id': new_breed.id}), 201
#
# @app.route('/api/breeds', methods=['POST'])
# def add_breed():
#     data = request.get_json()
#     breed_name = data.get('breed_name')
#
#     # 1. 检查是否已存在
#     existing_breed = DogBreed.query.filter_by(breed_name=breed_name).first()
#     if existing_breed:
#         # 返回友好的错误提示，HTTP 400 表示客户端请求错误
#         return jsonify({"error": f"犬种 '{breed_name}' 已存在"}), 400
#
#     # 2. 不存在则创建新记录
#     new_breed = DogBreed(
#         breed_name=breed_name,
#         avg_life_years=data.get('avg_life_years'),
#         size_category=data.get('size_category'),
#         popularity=data.get('popularity')
#     )
#     db.session.add(new_breed)
#     db.session.commit()
#
#     return jsonify({"message": "添加成功", "id": new_breed.id}), 201
#
# from sqlalchemy.exc import IntegrityError
# from flask import jsonify, request
#
# @app.route('/api/breeds', methods=['POST'])
# def add_breed():
#     data = request.get_json()
#     new_breed = DogBreed(
#         breed_name=data.get('breed_name'),
#         # ... 其他字段
#     )
#     db.session.add(new_breed)
#
#     try:
#         db.session.commit()
#         return jsonify({"message": "添加成功", "id": new_breed.id}), 201
#     except IntegrityError as e:
#         db.session.rollback()  # 发生错误后必须回滚会话
#         # 可以进一步检查错误信息，确认是唯一约束冲突
#         if 'Duplicate entry' in str(e):
#             return jsonify({"error": f"犬种 '{new_breed.breed_name}' 已存在"}), 400
#         else:
#             # 其他类型的完整性错误
#             return jsonify({"error": "数据库错误"}), 500

# 获取单个品种（用于编辑时回填）

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

# 更新品种
@app.route('/api/breeds/<int:id>', methods=['PUT'])
def update_breed(id):
    breed = DogBreed.query.get_or_404(id)
    data = request.get_json()
    breed.breed_name = data['breed_name']
    breed.avg_life_years = data.get('avg_life_years')
    breed.size_category = data.get('size_category')
    breed.popularity = data.get('popularity', 0)
    db.session.commit()
    return jsonify({'message': '更新成功'})


# 删除品种
@app.route('/api/breeds/<int:id>', methods=['DELETE'])
def delete_breed(id):
    breed = DogBreed.query.get_or_404(id)
    db.session.delete(breed)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@app.route('/food')
def food_dashboard():
    stats = get_dog_food_stats()
    return render_template('food.html', stats=stats)

@app.route('/api/food')
def api_food():
    # 返回原始狗粮数据用于前端表格（可选）
    try:
        con = pymysql.connect(**charts.DB_CONFIG)
        cur = con.cursor()
        cur.execute("SELECT food_name, price, origin FROM dog_wykl LIMIT 100")
        data = cur.fetchall()
        con.close()
        return jsonify([{'name': row[0], 'price': row[1], 'origin': row[2]} for row in data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/breeds/import', methods=['POST'])
def import_breeds():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 保存到临时文件或直接读取
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'文件解析失败: {str(e)}'}), 400

        # 检查必要列
        required_columns = ['品种名', '平均寿命', '体型', '人气值']
        # 允许列名有别名，如 breed_name, avg_life_years, size_category, popularity
        # 这里简单处理：期望列名与数据库字段对应，或提供映射
        # 我们假设 CSV 列名可能是中文或英文，需要映射。
        # 可以定义一个映射字典：
        column_map = {
            '品种名': 'breed_name',
            '平均寿命': 'avg_life_years',
            '体型': 'size_category',
            '人气值': 'popularity',
            'breed_name': 'breed_name',
            'avg_life_years': 'avg_life_years',
            'size_category': 'size_category',
            'popularity': 'popularity'
        }
        # 找出存在的列
        present_cols = [col for col in column_map.keys() if col in df.columns]
        if not present_cols:
            return jsonify({'error': '文件中缺少必要的列（需要品种名、平均寿命、体型、人气值或其英文对应）'}), 400

        # 提取数据
        records = []
        errors = []
        for idx, row in df.iterrows():
            try:
                record = {}
                for col in present_cols:
                    db_col = column_map[col]
                    val = row[col]
                    if pd.isna(val):
                        val = None
                    # 类型处理
                    if db_col == 'avg_life_years' and val is not None:
                        try:
                            val = float(val)
                        except:
                            val = None
                    if db_col == 'popularity' and val is not None:
                        try:
                            val = int(val)
                        except:
                            val = 0
                    record[db_col] = val
                # 确保必须有品种名
                if not record.get('breed_name'):
                    errors.append(f"第{idx+2}行缺少品种名")
                    continue
                records.append(record)
            except Exception as e:
                errors.append(f"第{idx+2}行解析失败: {str(e)}")

        if not records:
            return jsonify({'error': '没有有效数据可导入', 'details': errors}), 400

        # 批量插入
        success_count = 0
        fail_count = 0
        fail_details = []
        for rec in records:
            try:
                breed = DogBreed(
                    breed_name=rec['breed_name'],
                    avg_life_years=rec.get('avg_life_years'),
                    size_category=rec.get('size_category'),
                    popularity=rec.get('popularity', 0)
                )
                db.session.add(breed)
                db.session.commit()  # 每次提交一条，避免因唯一约束中断全部
                success_count += 1
            except Exception as e:
                db.session.rollback()
                fail_count += 1
                fail_details.append(f"{rec.get('breed_name')}: {str(e)}")

        return jsonify({
            'success': success_count,
            'fail': fail_count,
            'details': fail_details
        })
    else:
        return jsonify({'error': '不支持的文件类型，请上传 CSV 或 Excel 文件'}), 400

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        # 创建新用户
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('登录成功', 'success')
                # 跳转到用户之前尝试访问的页面，或首页
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('用户名或密码错误', 'danger')
        except Exception as e:
            print("错误：",e)
    return render_template('login.html')

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('index'))

# 需要登录才能访问的路由上添加 @login_required 装饰器。例如，品种管理页面只有管理员能访问：
@app.route('/admin/breeds', methods=['GET', 'POST'])
@login_required
def admin_breeds():
    print(f"=== Request received: method={request.method}, path={request.path} ===")
    print("Headers:", dict(request.headers))
    print("Raw data:", request.get_data(as_text=True))
    # 权限检查（所有方法共享）
    if not current_user.is_admin():
        print("User is not admin, redirecting")
        flash('无权限访问', 'danger')
        return redirect(url_for('index'))

    # 处理 POST 请求（创建新品种）
    if request.method == 'POST':
        # 获取 JSON 数据
        print("Processing POST request")
        data = request.get_json()
        print("Parsed JSON:", data)
        if not data:
            print("Invalid JSON, returning 400")
            return jsonify({"error": "Invalid JSON"}), 400

        # 提取字段
        breed_name = data.get('breed_name')
        avg_life = data.get('avg_life_years')
        size_category = data.get('size_category')
        popularity = data.get('popularity')
        print(f"Extracted: breed={breed_name}, avg_life={avg_life}, size={size_category}, popularity={popularity}")

        # 处理 avg_life_years：非数值转 None
        if avg_life is not None:
            try:
                avg_life = float(avg_life)
            except (ValueError, TypeError):
                avg_life = None

        # 创建新记录
        new_breed = DogBreed(
            breed_name=breed_name,
            avg_life_years=avg_life,
            size_category=size_category,
            popularity=popularity
        )
        db.session.add(new_breed)
        try:
            db.session.commit()
            print("Commit successful, breed created")
        except Exception as e:
            print(f"Commit failed: {e}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        return jsonify({"message": "Breed created", "id": new_breed.id}), 201

    # GET 请求：渲染管理页面
    print("GET request, rendering template")
    return render_template('admin_breeds.html')

# @app.route('/create-admin')
# def create_admin():
#     from models import User
#     admin = User(username='admin', role='admin')
#     admin.set_password('123456')
#     db.session.add(admin)
#     db.session.commit()
#     return "管理员创建成功"

# ======= 使用 Flask-APScheduler 设置定时任务自动更新汇总表 ======
scheduler = APScheduler()
def scheduled_update():
    with app.app_context():
        update_dashboard_summary()
        print("定时汇总更新完成")

scheduler.add_job(id='update_summary', func=scheduled_update, trigger='interval', hours=6)  # 每6小时更新一次
scheduler.start()


if __name__ == '__main__':
    # 启动 Flask 开发服务器
    app.run(debug=True)