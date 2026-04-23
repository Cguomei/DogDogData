from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import DogBreed, db
from sqlalchemy.exc import IntegrityError
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import text

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
    """API: 接收用户上传的 CSV/Excel 数据（含质量校验）"""
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
        
        # ===== 数据质量校验 =====
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'issues': []
        }
        
        # 1. 空值检测
        null_counts = df.isnull().sum()
        for col, null_count in null_counts.items():
            null_ratio = null_count / len(df) * 100
            if null_ratio > 30:
                quality_report['issues'].append({
                    'type': 'high_null_ratio',
                    'column': col,
                    'message': f'列 "{col}" 空值比例过高: {null_ratio:.1f}%',
                    'severity': 'warning'
                })
        
        # 2. 数据类型检测
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # 检查是否有非数字值
                non_numeric = df[col][pd.to_numeric(df[col], errors='coerce').isna()].count()
                if non_numeric > 0:
                    quality_report['issues'].append({
                        'type': 'non_numeric_in_numeric_column',
                        'column': col,
                        'message': f'数值列 "{col}" 中有 {non_numeric} 个非数字值',
                        'severity': 'error'
                    })
        
        # 3. 异常值检测（示例：检测负数）
        for col in df.select_dtypes(include=['number']).columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                quality_report['issues'].append({
                    'type': 'negative_values',
                    'column': col,
                    'message': f'列 "{col}" 中有 {negative_count} 个负数值',
                    'severity': 'warning'
                })
        
        # 4. 重复值检测
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            quality_report['issues'].append({
                'type': 'duplicate_rows',
                'message': f'发现 {duplicate_count} 行完全重复的数据',
                'severity': 'info'
            })
        
        # 返回前 100 行数据和校验报告
        columns = df.columns.tolist()
        data_sample = df.head(100).to_dict('records')
        
        return jsonify({
            'success': True,
            'columns': columns,
            'row_count': len(df),
            'data': data_sample,
            'quality_report': quality_report
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

# ===== 数据导出 API =====
@api_bp.route('/api/export-data', methods=['POST'])
def export_data():
    """导出数据为 Excel 或 CSV"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'excel')  # excel 或 csv
        table_data = data.get('data', [])
        filename = data.get('filename', 'data')
        
        if not table_data:
            return jsonify({'error': '没有数据可导出'}), 400
        
        df = pd.DataFrame(table_data)
        
        import io
        from flask import send_file
        
        if export_format == 'csv':
            # 导出 CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_buffer.seek(0)
            
            return send_file(
                io.BytesIO(csv_buffer.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
        
        else:  # excel
            # 导出 Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            excel_buffer.seek(0)
            
            return send_file(
                excel_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{filename}.xlsx'
            )
    
    except Exception as e:
        return jsonify({'error': f'导出失败：{str(e)}'}), 500

# ===== 测试页面 =====
@api_bp.route('/test-pet')
def test_pet_page():
    """2.5D 宠物功能测试页面"""
    return render_template('test_pet.html')

@api_bp.route('/clear-cache')
def clear_cache_page():
    """清除缓存指南页面"""
    return render_template('clear_cache.html')

@api_bp.route('/test-pet-alpine')
def test_pet_alpine_page():
    """Alpine.js 宠物组件测试页面"""
    return render_template('test_pet_alpine.html')

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

# ===== 健康检查 API =====
@api_bp.route('/api/health')
def health_check():
    """健康检查接口（供监控系统调用）"""
    try:
        # 检查数据库连接
        db.session.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # 构建响应
    health_data = {
        'status': 'healthy' if db_status == 'ok' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': 'v4.5.3',
        'checks': {
            'database': db_status,
            'cache': 'ok'  # 简化版本，后续可扩展
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

# ===== 国际化 API =====
@api_bp.route('/api/set-language', methods=['POST'])
def set_language():
    """设置用户语言偏好"""
    from flask import session
    
    data = request.get_json()
    lang = data.get('language', 'zh_CN')
    
    # 验证语言代码
    supported_languages = ['zh_CN', 'en_US', 'ja_JP']
    if lang not in supported_languages:
        return jsonify({'error': f'不支持的语言: {lang}'}), 400
    
    # 保存到 Session
    session['language'] = lang
    
    return jsonify({
        'success': True,
        'message': f'语言已切换为 {lang}',
        'language': lang
    }), 200

@api_bp.route('/api/get-language')
def get_language():
    """获取当前语言设置"""
    from flask import session
    
    current_lang = session.get('language', 'zh_CN')
    
    return jsonify({
        'language': current_lang,
        'supported_languages': ['zh_CN', 'en_US', 'ja_JP']
    }), 200

@api_bp.route('/api/dashboard/stats')
def get_dashboard_stats():
    """获取首页统计数据（用于 Alpine.js 动态刷新）"""
    try:
        from charts import get_dashboard_stats_from_summary
        stats = get_dashboard_stats_from_summary()
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': f'获取统计数据失败: {str(e)}'}), 500

@api_bp.route('/api/chart/<chart_type>/data')
def get_chart_data(chart_type):
    """获取图表数据（用于 Alpine.js 动态渲染）"""
    try:
        # 这里应该根据 chart_type 返回对应的数据
        # 示例实现
        chart_data_map = {
            'scatter': {'x_data': [1, 2, 3], 'y_data': [4, 5, 6]},
            'line': {'x_data': [1, 2, 3], 'y_data': [4, 5, 6]},
            'bar': {'x_data': ['A', 'B', 'C'], 'y_data': [10, 20, 30]},
        }
        
        data = chart_data_map.get(chart_type, {'x_data': [], 'y_data': []})
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': f'获取图表数据失败: {str(e)}'}), 500

@api_bp.route('/api/charts/list')
def get_charts_list():
    """获取图表列表（用于图表列表页面）"""
    try:
        charts = [
            {
                'id': 'scatter',
                'title': '价格散点图',
                'description': '展示狗狗价格分布情况',
                'category': 'basic',
                'icon': '📈'
            },
            {
                'id': 'line',
                'title': '体重折线图',
                'description': '展示狗狗体重趋势',
                'category': 'basic',
                'icon': '📉'
            },
            {
                'id': 'bar',
                'title': '级别柱状图',
                'description': '展示不同级别的狗狗数量',
                'category': 'basic',
                'icon': '📊'
            },
            {
                'id': 'hist',
                'title': 'TOP10 直方图',
                'description': '热门狗狗品种和店铺排行',
                'category': 'advanced',
                'icon': '🏆'
            },
            {
                'id': 'funnel',
                'title': '价格漏斗图',
                'description': '价格区间转化分析',
                'category': 'advanced',
                'icon': '🔍'
            },
            {
                'id': 'map',
                'title': '世界地图',
                'description': '狗狗家乡分布地图',
                'category': 'map',
                'icon': '🗺️'
            }
        ]
        
        return jsonify(charts), 200
    except Exception as e:
        return jsonify({'error': f'获取图表列表失败: {str(e)}'}), 500