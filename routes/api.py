from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import DogBreed, db
from sqlalchemy.exc import IntegrityError
import os
from datetime import datetime
import pandas as pd

api_bp = Blueprint('api', __name__)

# ===== 宠物日志保存 API =====
@api_bp.route('/api/save_pet_logs', methods=['POST'])
def save_pet_logs():
    """保存宠物日志到 log 文件夹"""
    try:
        # 确保 log 文件夹存在
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'log')
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

# ===== 自定义数据分析 =====
@api_bp.route('/custom-analysis')
def custom_analysis():
    """用户自定义数据分析页面"""
    return render_template('custom_analysis.html')

@api_bp.route('/api/upload-data', methods=['POST'])
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

@api_bp.route('/api/generate-chart', methods=['POST'])
def generate_chart():
    """API: 根据用户配置生成图表"""
    try:
        data = request.get_json()
        chart_type = data.get('chart_type')  # scatter, line, bar, pie
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        title = data.get('title', '自定义图表')
        upload_data = data.get('data', [])  # 前端传递的表格数据
        
        if not all([chart_type, x_column, y_column]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        if not upload_data or len(upload_data) == 0:
            return jsonify({'error': '没有数据可生成图表'}), 400
        
        # 将数据转换为DataFrame
        df = pd.DataFrame(upload_data)
        
        # 验证列是否存在
        if x_column not in df.columns or y_column not in df.columns:
            return jsonify({'error': f'列名不存在: {x_column} 或 {y_column}'}), 400
        
        # 提取数据
        x_data = df[x_column].tolist()
        y_data = df[y_column].tolist()
        
        # 过滤无效数据
        valid_pairs = [(x, y) for x, y in zip(x_data, y_data) 
                      if pd.notna(x) and pd.notna(y)]
        
        if len(valid_pairs) == 0:
            return jsonify({'error': '没有有效数据对'}), 400
        
        x_valid, y_valid = zip(*valid_pairs)
        
        # 根据图表类型生成 PyECharts 配置
        from pyecharts.charts import Scatter, Line, Bar, Pie
        from pyecharts import options as opts
        
        if chart_type == 'scatter':
            chart = (
                Scatter()
                .add_xaxis(list(x_valid))
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column)
                )
            )
        
        elif chart_type == 'line':
            chart = (
                Line()
                .add_xaxis(list(x_valid))
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column)
                )
            )
        
        elif chart_type == 'bar':
            chart = (
                Bar()
                .add_xaxis([str(x) for x in x_valid])
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column)
                )
            )
        
        elif chart_type == 'pie':
            # 饼图需要特殊处理
            pie_data = [[str(x), float(y)] for x, y in valid_pairs]
            chart = (
                Pie()
                .add(title, pie_data)
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
            )
        
        else:
            return jsonify({'error': f'不支持的图表类型: {chart_type}'}), 400
        
        # 渲染为 HTML
        chart_html = chart.render_embed()
        
        return jsonify({
            'success': True,
            'chart_html': chart_html,
            'message': f'图表已生成：{title}',
            'data_points': len(valid_pairs)
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成图表失败：{str(e)}'}), 500

# ===== 狗狗品种 API =====
@api_bp.route('/api/breeds')
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

@api_bp.route('/api/breeds/<int:id>')
def get_breed(id):
    breed = DogBreed.query.get_or_404(id)
    return jsonify({
        'id': breed.id,
        'breed_name': breed.breed_name,
        'avg_life_years': float(breed.avg_life_years) if breed.avg_life_years else None,
        'size_category': breed.size_category,
        'popularity': breed.popularity
    })

@api_bp.route('/api/breeds', methods=['POST'])
@login_required
def add_breed():
    """添加新的狗狗品种（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({'error': '权限不足，需要管理员权限'}), 403
    
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
        return jsonify({"error": "添加失败，可能是品种名称重复"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"添加失败：{str(e)}"}), 500

@api_bp.route('/api/breeds/<int:id>', methods=['PUT'])
@login_required
def update_breed(id):
    """更新狗狗品种信息（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({'error': '权限不足，需要管理员权限'}), 403
    
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失败：{str(e)}"}), 500

@api_bp.route('/api/breeds/<int:id>', methods=['DELETE'])
@login_required
def delete_breed(id):
    """删除狗狗品种（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({'error': '权限不足，需要管理员权限'}), 403
    
    breed = DogBreed.query.get_or_404(id)
    
    try:
        db.session.delete(breed)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除失败：{str(e)}"}), 500

# ===== 狗粮数据 API =====
@api_bp.route('/api/food')
def get_food():
    """获取狗粮列表数据"""
    from charts import get_dog_food_list
    food_list = get_dog_food_list()
    return jsonify(food_list)

# ===== 测试页面 =====
@api_bp.route('/test-pet')
def test_pet_page():
    """2.5D 宠物功能测试页面"""
    return render_template('test_pet.html')

@api_bp.route('/clear-cache')
def clear_cache_page():
    """清除缓存指南页面"""
    return render_template('clear_cache.html')

@api_bp.route('/api/restart', methods=['POST'])
def api_restart():
    """API: 重启应用（需要管理员权限）"""
    from flask_login import current_user
    
    # 添加管理员权限检查
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
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