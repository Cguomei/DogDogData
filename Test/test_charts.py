from charts import (
    get_price_scatter,
    get_weight_line,
    get_level_bar,
    get_shop_top10_hist,
    get_price_funnel,
    get_world_map
)


# 测试 charts.py 里的函数是否返回有效的 HTML 字符串
def test_price_scatter_returns_html():
    html = get_price_scatter()
    assert html.startswith('<div id="')
    assert 'pyecharts' in html or 'echarts' in html  # 简单检查

# 测试图表生成函数是否返回有效的 HTML 字符串
def test_price_scatter_returns_string():
    html = get_price_scatter()
    assert isinstance(html, str)
    assert html.startswith('<div') or html.startswith('<!DOCTYPE')

def test_weight_line_returns_string():
    html = get_weight_line()
    assert isinstance(html, str)

def test_level_bar_returns_string():
    html = get_level_bar()
    assert isinstance(html, str)

def test_shop_top10_hist_returns_string():
    html = get_shop_top10_hist()
    assert isinstance(html, str)

def test_price_funnel_returns_string():
    html = get_price_funnel()
    assert isinstance(html, str)

def test_world_map_returns_string():
    html = get_world_map()
    assert isinstance(html, str)
    # 可以检查是否包含地图容器的标记
    assert 'echarts' in html or 'Map' in html




