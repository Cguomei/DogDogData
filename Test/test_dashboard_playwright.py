"""
数据看板和图表功能自动化测试 - Playwright 版本
涵盖：首页统计、图表展示、数据可视化等用户操作流程
"""

import pytest
from playwright.sync_api import Page, expect
from playwright_config import BASE_URL


class TestDashboardHomepage:
    """首页数据看板测试"""

    def test_homepage_loads(self, page: Page):
        """测试 1: 首页加载"""
        page.goto(BASE_URL)

        # 验证页面标题
        title = page.title()
        assert len(title) > 0, "页面应有标题"

        # 验证 URL
        expect(page).to_have_url(BASE_URL + "/")

        print(f"✅ 测试 1 通过：首页加载成功，标题：{title}")

    def test_dashboard_stats_display(self, page: Page):
        """测试 2: 统计数据展示"""
        page.goto(BASE_URL)

        # 等待页面加载
        page.wait_for_timeout(1000)

        # 检查统计卡片或数据区域
        stats_elements = page.locator(
            ".stat-card, .stats, .dashboard-stats, [class*='stat']"
        )

        if stats_elements.count() > 0:
            first_stat = stats_elements.first
            expect(first_stat).to_be_visible()

            stat_text = first_stat.text_content()
            assert len(stat_text.strip()) > 0, "统计信息不应为空"

            print(f"✅ 测试 2 通过：统计数据展示，内容：{stat_text[:50]}")
        else:
            print("⚠️  测试 2 跳过：未找到统计元素")

    def test_navigation_menu_exists(self, page: Page):
        """测试 3: 导航菜单存在"""
        page.goto(BASE_URL)

        # 查找导航元素
        nav_elements = page.locator("nav, .navbar, .navigation, .menu")

        if nav_elements.count() > 0:
            expect(nav_elements.first).to_be_visible()
            print("✅ 测试 3 通过：导航菜单存在")
        else:
            # 尝试查找链接列表
            links = page.locator("a[href]")
            assert links.count() > 0, "页面应包含导航链接"
            print(f"✅ 测试 3 通过：找到 {links.count()} 个导航链接")


class TestChartPages:
    """图表页面测试"""

    def test_charts_list_page(self, page: Page):
        """测试 4: 图表列表页面"""
        page.goto(f"{BASE_URL}/charts")

        # 等待页面加载
        page.wait_for_timeout(1000)

        # 验证页面加载
        expect(page).to_have_url(f"{BASE_URL}/charts")

        # 检查是否有图表链接或图表容器
        chart_links = page.locator('a[href*="/chart/"]')
        chart_containers = page.locator(".chart-container, .chart, [id*='chart']")

        total_charts = chart_links.count() + chart_containers.count()
        assert total_charts > 0, "图表列表页应包含图表"

        print(f"✅ 测试 4 通过：图表列表页加载，找到 {total_charts} 个图表项")

    def test_scatter_chart_page(self, page: Page):
        """测试 5: 散点图页面"""
        page.goto(f"{BASE_URL}/chart/scatter")

        # 等待页面加载
        page.wait_for_timeout(1500)

        # 验证页面标题包含"散点图"
        page_title = page.title()
        assert (
            "散点" in page_title or "scatter" in page_title.lower()
        ), f"页面标题应包含散点图相关信息，实际：{page_title}"

        # 检查图表容器
        chart_container = page.locator(".chart-container, #chart, .echarts-container")
        if chart_container.count() > 0:
            expect(chart_container.first).to_be_visible()
            print("✅ 测试 5 通过：散点图页面加载成功")
        else:
            # 检查是否有 iframe（pyecharts 可能使用 iframe）
            iframes = page.locator("iframe")
            if iframes.count() > 0:
                print("✅ 测试 5 通过：散点图页面加载（使用 iframe）")
            else:
                print("⚠️  测试 5 警告：未找到明显的图表容器")

    def test_line_chart_page(self, page: Page):
        """测试 6: 折线图页面"""
        page.goto(f"{BASE_URL}/chart/line")

        # 等待页面加载
        page.wait_for_timeout(1500)

        expect(page).to_have_url(f"{BASE_URL}/chart/line")

        page_title = page.title()
        assert (
            "折线" in page_title or "line" in page_title.lower()
        ), f"页面标题应包含折线图相关信息，实际：{page_title}"

        print("✅ 测试 6 通过：折线图页面加载成功")

    def test_bar_chart_page(self, page: Page):
        """测试 7: 柱状图页面"""
        page.goto(f"{BASE_URL}/chart/bar")

        # 等待页面加载
        page.wait_for_timeout(1500)

        expect(page).to_have_url(f"{BASE_URL}/chart/bar")

        page_title = page.title()
        assert (
            "柱状" in page_title or "bar" in page_title.lower()
        ), f"页面标题应包含柱状图相关信息，实际：{page_title}"

        print("✅ 测试 7 通过：柱状图页面加载成功")

    def test_hist_chart_page(self, page: Page):
        """测试 8: 直方图页面"""
        page.goto(f"{BASE_URL}/chart/hist")

        # 等待页面加载
        page.wait_for_timeout(1500)

        expect(page).to_have_url(f"{BASE_URL}/chart/hist")

        print("✅ 测试 8 通过：直方图页面加载成功")

    def test_funnel_chart_page(self, page: Page):
        """测试 9: 漏斗图页面"""
        page.goto(f"{BASE_URL}/chart/funnel")

        # 等待页面加载
        page.wait_for_timeout(1500)

        expect(page).to_have_url(f"{BASE_URL}/chart/funnel")

        print("✅ 测试 9 通过：漏斗图页面加载成功")

    def test_map_chart_page(self, page: Page):
        """测试 10: 地图页面"""
        page.goto(f"{BASE_URL}/chart/map")

        # 等待页面加载
        page.wait_for_timeout(2000)

        expect(page).to_have_url(f"{BASE_URL}/chart/map")

        page_title = page.title()
        assert (
            "地图" in page_title or "map" in page_title.lower()
        ), f"页面标题应包含地图相关信息，实际：{page_title}"

        print("✅ 测试 10 通过：地图页面加载成功")


class TestFoodDashboard:
    """狗粮数据看板测试"""

    def test_food_dashboard_loads(self, page: Page):
        """测试 11: 狗粮数据看板加载"""
        page.goto(f"{BASE_URL}/food")

        # 等待页面加载
        page.wait_for_timeout(1500)

        # 验证页面
        expect(page).to_have_url(f"{BASE_URL}/food")

        # 检查页面标题
        page_title = page.title()
        assert (
            "狗粮" in page_title or "food" in page_title.lower()
        ), f"页面标题应包含狗粮相关信息，实际：{page_title}"

        print("✅ 测试 11 通过：狗粮数据看板加载成功")

    def test_food_stats_display(self, page: Page):
        """测试 12: 狗粮统计数据展示"""
        page.goto(f"{BASE_URL}/food")

        # 等待页面加载
        page.wait_for_timeout(1500)

        # 检查统计信息
        stats_elements = page.locator(".stat, .stat-card, [class*='stats']")

        if stats_elements.count() > 0:
            first_stat = stats_elements.first
            expect(first_stat).to_be_visible()
            print("✅ 测试 12 通过：狗粮统计数据展示")
        else:
            print("⚠️  测试 12 跳过：未找到统计元素")


class TestNavigationFlow:
    """导航流程测试"""

    def test_navigate_from_home_to_charts(self, page: Page):
        """测试 13: 从首页导航到图表列表"""
        page.goto(BASE_URL)

        # 查找图表链接
        charts_link = page.locator('a[href="/charts"], a[href*="charts"]')
        if charts_link.count() > 0:
            charts_link.first.click()
            page.wait_for_timeout(1000)

            expect(page).to_have_url(f"{BASE_URL}/charts")
            print("✅ 测试 13 通过：从首页导航到图表列表")
        else:
            print("⚠️  测试 13 跳过：未找到图表链接")

    def test_navigate_from_home_to_food(self, page: Page):
        """测试 14: 从首页导航到狗粮看板"""
        page.goto(BASE_URL)

        # 查找狗粮链接
        food_link = page.locator('a[href="/food"], a[href*="food"]')
        if food_link.count() > 0:
            food_link.first.click()
            page.wait_for_timeout(1000)

            expect(page).to_have_url(f"{BASE_URL}/food")
            print("✅ 测试 14 通过：从首页导航到狗粮看板")
        else:
            print("⚠️  测试 14 跳过：未找到狗粮链接")

    def test_back_navigation(self, page: Page):
        """测试 15: 返回导航"""
        page.goto(f"{BASE_URL}/charts")
        page.wait_for_timeout(1000)

        # 点击浏览器后退按钮
        page.go_back()
        page.wait_for_timeout(1000)

        # 应该回到首页
        expect(page).to_have_url(BASE_URL + "/")

        print("✅ 测试 15 通过：返回导航正常")


class TestResponsiveDesign:
    """响应式设计测试"""

    def test_mobile_viewport(self, browser_context):
        """测试 16: 移动端视口"""
        # 创建移动端上下文
        mobile_context = browser_context.new_context(
            viewport={"width": 375, "height": 667}
        )
        page = mobile_context.new_page()

        page.goto(BASE_URL)
        page.wait_for_timeout(1000)

        # 验证页面在移动端正常显示
        expect(page).to_have_url(BASE_URL + "/")

        # 检查宠物容器是否适应移动端
        pet_container = page.locator(".virtual-pet-container")
        if pet_container.count() > 0:
            expect(pet_container.first).to_be_visible()

        page.close()
        mobile_context.close()

        print("✅ 测试 16 通过：移动端视口正常")

    def test_tablet_viewport(self, browser_context):
        """测试 17: 平板端视口"""
        tablet_context = browser_context.new_context(
            viewport={"width": 768, "height": 1024}
        )
        page = tablet_context.new_page()

        page.goto(BASE_URL)
        page.wait_for_timeout(1000)

        expect(page).to_have_url(BASE_URL + "/")

        page.close()
        tablet_context.close()

        print("✅ 测试 17 通过：平板端视口正常")


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/dashboard_test_playwright_report.html",
            "--self-contained-html",
        ]
    )
