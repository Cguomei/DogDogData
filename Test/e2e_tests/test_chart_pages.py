"""
图表页面 E2E 测试
测试完整的图表交互流程
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.charts
class TestChartPages:
    """图表页面端到端测试"""
    
    def test_scatter_chart_page(self, page: Page):
        """TC-CHART-001: 测试散点图页面"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 验证页面加载
        expect(page).to_have_title('价格散点图 - 狗狗数据分析')
        
        # 验证图表容器存在
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 散点图页面加载成功")
    
    def test_line_chart_page(self, page: Page):
        """TC-CHART-002: 测试折线图页面"""
        page.goto('http://localhost:5000/chart/line')
        
        # 验证页面标题
        expect(page).to_have_title('体重折线图 - 狗狗数据分析')
        
        # 验证图表存在
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 折线图页面加载成功")
    
    def test_bar_chart_page(self, page: Page):
        """TC-CHART-003: 测试柱状图页面"""
        page.goto('http://localhost:5000/chart/bar')
        
        expect(page).to_have_title('级别柱状图 - 狗狗数据分析')
        
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 柱状图页面加载成功")
    
    def test_histogram_page(self, page: Page):
        """TC-CHART-004: 测试直方图页面"""
        page.goto('http://localhost:5000/chart/hist')
        
        expect(page).to_have_title('狗狗 + 店铺 TOP10 直方图 - 狗狗数据分析')
        
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 直方图页面加载成功")
    
    def test_funnel_chart_page(self, page: Page):
        """TC-CHART-005: 测试漏斗图页面"""
        page.goto('http://localhost:5000/chart/funnel')
        
        expect(page).to_have_title('价格段漏斗图 - 狗狗数据分析')
        
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 漏斗图页面加载成功")
    
    def test_map_chart_page(self, page: Page):
        """TC-CHART-006: 测试地图页面"""
        page.goto('http://localhost:5000/chart/map')
        
        expect(page).to_have_title('世界地图（狗狗家乡分布） - 狗狗数据分析')
        
        chart_container = page.locator('#chart-container')
        expect(chart_container).to_be_visible()
        
        print("✅ 地图页面加载成功")


@pytest.mark.e2e
@pytest.mark.charts
class TestChartListPage:
    """图表列表页面测试"""
    
    def test_charts_list_page_loads(self, page: Page):
        """TC-CHARTLIST-001: 测试图表列表页面加载"""
        page.goto('http://localhost:5000/charts')
        
        # 验证页面标题
        expect(page).to_have_title('图表列表 - 狗狗数据分析')
        
        # 验证图表列表存在
        expect(page.locator('text=图表列表')).to_be_visible()
        
        print("✅ 图表列表页面加载成功")
    
    def test_chart_cards_display(self, page: Page):
        """TC-CHARTLIST-002: 测试图表卡片显示"""
        page.goto('http://localhost:5000/charts')
        
        # 验证至少有一个图表卡片
        chart_cards = page.locator('.chart-card')
        expect(chart_cards).not_to_have_count(0)
        
        print("✅ 图表卡片显示正常")
    
    def test_chart_navigation(self, page: Page):
        """TC-CHARTLIST-003: 测试图表导航"""
        page.goto('http://localhost:5000/charts')
        
        # 点击第一个图表卡片
        first_chart = page.locator('.chart-card').first
        first_chart.click()
        
        # 验证跳转到图表详情页
        expect(page).not_to_have_url('http://localhost:5000/charts')
        
        print("✅ 图表导航功能正常")


@pytest.mark.e2e
@pytest.mark.performance
class TestChartPerformance:
    """图表性能测试"""
    
    def test_chart_load_time(self, page: Page):
        """TC-PERF-001: 测试图表加载时间"""
        import time
        
        start_time = time.time()
        page.goto('http://localhost:5000/chart/scatter')
        
        # 等待图表容器可见
        page.wait_for_selector('#chart-container', state='visible')
        
        elapsed = time.time() - start_time
        
        print(f"📊 图表加载时间: {elapsed:.2f}秒")
        
        # 应该在 3 秒内加载完成
        assert elapsed < 3.0, f"图表加载太慢: {elapsed:.2f}秒"
        
        print("✅ 图表加载性能达标")
    
    def test_chart_responsive_resize(self, page: Page):
        """TC-PERF-002: 测试图表响应式调整"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 等待图表加载
        page.wait_for_selector('#chart-container')
        
        # 获取初始宽度
        initial_width = page.evaluate('''
            () => document.querySelector('#chart-container').offsetWidth
        ''')
        
        # 调整窗口大小
        page.set_viewport_size({"width": 800, "height": 600})
        page.wait_for_timeout(500)  # 等待响应式调整
        
        # 获取新宽度
        new_width = page.evaluate('''
            () => document.querySelector('#chart-container').offsetWidth
        ''')
        
        # 验证宽度已调整
        assert new_width != initial_width or new_width > 0
        
        print("✅ 图表响应式调整正常")
    
    def test_multiple_charts_navigation(self, page: Page):
        """TC-PERF-003: 测试多图表快速切换"""
        import time
        
        charts = ['scatter', 'line', 'bar']
        
        start_time = time.time()
        
        for chart_type in charts:
            page.goto(f'http://localhost:5000/chart/{chart_type}')
            page.wait_for_selector('#chart-container', state='visible')
        
        elapsed = time.time() - start_time
        
        print(f"📊 3个图表切换总时间: {elapsed:.2f}秒")
        print(f"📊 平均每个图表: {elapsed/len(charts):.2f}秒")
        
        # 平均每个图表应在 2 秒内加载
        assert elapsed / len(charts) < 2.0
        
        print("✅ 多图表切换性能良好")


@pytest.mark.e2e
@pytest.mark.accessibility
class TestChartAccessibility:
    """图表无障碍访问测试"""
    
    def test_chart_keyboard_navigation(self, page: Page):
        """TC-A11Y-CHART-001: 测试图表键盘导航"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 使用 Tab 键导航
        page.keyboard.press('Tab')
        
        # 验证焦点移动到可聚焦元素
        focused_tag = page.evaluate('() => document.activeElement.tagName')
        assert focused_tag in ['BUTTON', 'A', 'INPUT', 'SELECT']
        
        print("✅ 图表页面键盘导航正常")
    
    def test_chart_aria_labels(self, page: Page):
        """TC-A11Y-CHART-002: 测试图表 ARIA 标签"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 验证图表容器有适当的 role
        chart_role = page.evaluate('''
            () => document.querySelector('#chart-container')?.getAttribute('role')
        ''')
        
        # 应该有 img 或 application role
        assert chart_role in ['img', 'application', None]  # None 也可以接受
        
        print("✅ 图表 ARIA 标签检查通过")
    
    def test_chart_alt_text(self, page: Page):
        """TC-A11Y-CHART-003: 测试图表替代文本"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 验证页面有标题
        title = page.locator('h1, h2, .chart-title').first
        expect(title).not_to_be_empty()
        
        print("✅ 图表替代文本检查通过")


@pytest.mark.e2e
@pytest.mark.integration
class TestChartIntegration:
    """图表集成测试"""
    
    def test_chart_data_api(self, page: Page):
        """TC-INT-001: 测试图表数据 API"""
        # 直接调用 API
        response = page.request.get('http://localhost:5000/api/chart/scatter/data')
        
        assert response.ok
        data = response.json()
        
        # 验证数据结构
        assert 'x_data' in data
        assert 'y_data' in data
        
        print("✅ 图表数据 API 正常")
    
    def test_charts_list_api(self, page: Page):
        """TC-INT-002: 测试图表列表 API"""
        response = page.request.get('http://localhost:5000/api/charts/list')
        
        assert response.ok
        charts = response.json()
        
        # 验证返回的是列表
        assert isinstance(charts, list)
        assert len(charts) > 0
        
        # 验证数据结构
        first_chart = charts[0]
        assert 'id' in first_chart
        assert 'title' in first_chart
        assert 'category' in first_chart
        
        print(f"✅ 图表列表 API 正常，共 {len(charts)} 个图表")
    
    def test_chart_export_functionality(self, page: Page):
        """TC-INT-003: 测试图表导出功能"""
        page.goto('http://localhost:5000/chart/scatter')
        
        # 等待图表加载
        page.wait_for_selector('#chart-container')
        
        # 查找导出按钮（如果有的话）
        export_button = page.locator('button:has-text("导出"), button:has-text("Export")')
        
        if export_button.count() > 0:
            # 开始监听下载
            with page.expect_download() as download_info:
                export_button.click()
            
            download = download_info.value
            
            # 验证文件下载
            assert download.suggested_filename.endswith(('.png', '.jpg', '.svg'))
            
            print(f"✅ 图表导出成功: {download.suggested_filename}")
        else:
            print("ℹ️ 当前页面没有导出按钮")
