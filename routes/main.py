from flask import Blueprint, render_template
from charts import get_dashboard_stats_from_summary
from charts import get_price_scatter, get_weight_line, get_level_bar, get_shop_top10_hist, get_price_funnel, get_world_map

main_bp = Blueprint('main', __name__)

# ===== 首页和数据看板 =====
@main_bp.route('/')
def index():
    stats = get_dashboard_stats_from_summary()
    return render_template('index.html', stats=stats)

# ===== 图表列表页面 =====
@main_bp.route('/charts')
def charts_list():
    """图表列表页面"""
    return render_template('charts_list.html')

# ===== 品种管理页面 =====
@main_bp.route('/admin/breeds')
def admin_breeds():
    """品种管理页面（仅管理员可访问）"""
    from flask_login import login_required, current_user
    from flask import flash, redirect, url_for
    
    @login_required
    def admin_breeds_protected():
        if not current_user.is_admin():
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('main.index'))
        return render_template('admin_breeds.html')
    
    return admin_breeds_protected()

# ===== 图表页面 =====
@main_bp.route('/map')
def show_map():
    map_html = get_world_map()
    return map_html

@main_bp.route('/chart/scatter')
def scatter():
    chart_html = get_price_scatter()
    return render_template('chart_page.html', chart_html=chart_html, chart_title='价格散点图')

@main_bp.route('/chart/line')
def line():
    chart_html = get_weight_line()
    return render_template('chart_page.html', chart_html=chart_html, chart_title='体重折线图')

@main_bp.route('/chart/bar')
def bar():
    chart_html = get_level_bar()
    return render_template('chart_page.html', chart_html=chart_html, chart_title='级别柱状图')

@main_bp.route('/chart/hist')
def hist():
    chart_html = get_shop_top10_hist()
    return render_template('chart_page.html', chart_html=chart_html, chart_title='狗狗 + 店铺 TOP10 直方图')

@main_bp.route('/chart/funnel')
def funnel():
    chart_html = get_price_funnel()
    return render_template('chart_page.html', chart_html=chart_html, chart_title='价格段漏斗图')

@main_bp.route('/chart/map')
def world_map():
    from flask_caching import cache
    
    @cache.cached(timeout=3600)
    def cached_world_map():
        chart_html = get_world_map()
        return render_template('chart_page.html', chart_html=chart_html, chart_title='世界地图（狗狗家乡分布）')
    
    return cached_world_map()