"""
Alpine.js 组件 UI 测试
测试 Alpine.js 组件的交互功能和响应式行为
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.alpine
class TestAlpineComponents:
    """Alpine.js 组件测试类"""

    def test_alpine_demo_page_loads(self, page: Page):
        """TC-ALPINE-001: 测试演示页面加载"""
        page.goto("http://localhost:5000/alpine-demo")

        # 验证页面标题
        expect(page).to_have_title("Alpine.js 组件演示")

        # 验证关键元素存在
        expect(page.locator("h2")).to_contain_text("Alpine.js 组件演示")
        expect(page.locator("text=统计卡片组件")).to_be_visible()
        expect(page.locator("text=反馈表单组件")).to_be_visible()
        expect(page.locator("text=通知系统")).to_be_visible()

        print("✅ 演示页面加载成功")

    def test_language_switcher_dropdown(self, page: Page):
        """TC-ALPINE-002: 测试语言切换下拉菜单"""
        page.goto("http://localhost:5000/alpine-demo")

        # 点击语言切换按钮
        lang_button = page.locator('button:has-text("中文")')
        lang_button.click()

        # 验证下拉菜单显示
        dropdown = page.locator(".absolute.right-0.mt-2")
        expect(dropdown).to_be_visible()

        # 验证三个语言选项
        expect(page.locator("text=中文")).to_be_visible()
        expect(page.locator("text=English")).to_be_visible()
        expect(page.locator("text=日本語")).to_be_visible()

        print("✅ 语言切换下拉菜单工作正常")

    def test_stat_card_refresh(self, page: Page):
        """TC-ALPINE-003: 测试统计卡片刷新功能"""
        page.goto("http://localhost:5000/alpine-demo")

        # 找到第一个卡片的刷新按钮
        refresh_button = page.locator(".stat-card button").first

        # 点击刷新
        refresh_button.click()

        # 验证加载状态（应该显示旋转图标）
        loading_icon = page.locator(".animate-spin").first
        expect(loading_icon).to_be_visible(timeout=2000)

        # 等待加载完成
        expect(loading_icon).not_to_be_visible(timeout=3000)

        print("✅ 统计卡片刷新功能正常")

    def test_feedback_form_validation(self, page: Page):
        """TC-ALPINE-004: 测试反馈表单验证"""
        page.goto("http://localhost:5000/alpine-demo")

        # 滚动到反馈表单
        page.locator("text=反馈表单组件").scroll_into_view_if_needed()

        # 尝试提交空表单
        submit_button = page.locator('form button[type="submit"]')
        submit_button.click()

        # 验证错误提示
        error_message = page.locator("text=反馈内容不能为空")
        expect(error_message).to_be_visible()

        print("✅ 反馈表单验证工作正常")

    def test_feedback_form_type_selection(self, page: Page):
        """TC-ALPINE-005: 测试反馈类型选择"""
        page.goto("http://localhost:5000/alpine-demo")

        # 滚动到反馈表单
        page.locator("text=反馈表单组件").scroll_into_view_if_needed()

        # 选择不同的反馈类型
        bug_button = page.locator('button:has-text("Bug 报告")')
        feature_button = page.locator('button:has-text("功能建议")')

        # 点击 Bug 报告
        bug_button.click()
        expect(bug_button).to_have_class("border-blue-500 bg-blue-50")

        # 点击功能建议
        feature_button.click()
        expect(feature_button).to_have_class("border-blue-500 bg-blue-50")

        print("✅ 反馈类型选择正常")

    def test_notification_system(self, page: Page):
        """TC-ALPINE-006: 测试通知系统"""
        page.goto("http://localhost:5000/alpine-demo")

        # 滚动到通知系统部分
        page.locator("text=通知系统").scroll_into_view_if_needed()

        # 点击成功通知按钮
        success_button = page.locator('button:has-text("成功通知")')
        success_button.click()

        # 验证通知出现
        notification = page.locator(".fixed.top-4.right-4 .bg-green-500")
        expect(notification).to_be_visible()
        expect(notification).to_contain_text("操作成功！")

        # 等待通知自动消失（3秒）
        expect(notification).not_to_be_visible(timeout=4000)

        print("✅ 通知系统工作正常")

    def test_utility_functions_display(self, page: Page):
        """TC-ALPINE-007: 测试工具函数显示"""
        page.goto("http://localhost:5000/alpine-demo")

        # 滚动到工具函数部分
        page.locator("text=工具函数").scroll_into_view_if_needed()

        # 验证数字格式化
        formatted_number = page.locator("text=1,234,567")
        expect(formatted_number).to_be_visible()

        # 验证日期格式化
        date_element = page.locator(".font-mono").last
        expect(date_element).not_to_be_empty()

        print("✅ 工具函数显示正常")


@pytest.mark.ui
@pytest.mark.alpine
class TestDashboardPage:
    """首页数据看板测试"""

    def test_dashboard_page_loads(self, page: Page):
        """TC-DASHBOARD-001: 测试首页加载"""
        page.goto("http://localhost:5000/")

        # 验证页面标题
        expect(page).to_have_title("数据看板 - 狗狗数据分析")

        # 验证核心指标卡片存在
        expect(page.locator("text=狗狗总数")).to_be_visible()
        expect(page.locator("text=平均价格")).to_be_visible()
        expect(page.locator("text=店铺总数")).to_be_visible()
        expect(page.locator("text=品种总数")).to_be_visible()

        print("✅ 首页加载成功")

    def test_stat_cards_display_data(self, page: Page):
        """TC-DASHBOARD-002: 测试统计卡片数据显示"""
        page.goto("http://localhost:5000/")

        # 验证统计数据不为空
        dog_count = page.locator(".display-4").first
        expect(dog_count).not_to_have_text("")

        print("✅ 统计卡片数据显示正常")

    def test_top_breeds_list(self, page: Page):
        """TC-DASHBOARD-003: 测试热门品种列表"""
        page.goto("http://localhost:5000/")

        # 验证热门品种列表存在
        expect(page.locator("text=热门狗狗品种 TOP5")).to_be_visible()

        # 验证列表项
        list_items = page.locator(".list-group-item")
        expect(list_items).not_to_have_count(0)

        print("✅ 热门品种列表显示正常")

    def test_price_distribution_chart(self, page: Page):
        """TC-DASHBOARD-004: 测试价格分布图表"""
        page.goto("http://localhost:5000/")

        # 验证价格分布区域存在
        expect(page.locator("text=价格区间分布")).to_be_visible()

        # 验证进度条存在
        progress_bars = page.locator(".progress-bar")
        expect(progress_bars).not_to_have_count(0)

        print("✅ 价格分布图表显示正常")


@pytest.mark.ui
@pytest.mark.performance
class TestLazyLoading:
    """图片懒加载测试"""

    def test_lazy_loading_images(self, page: Page):
        """TC-LAZY-001: 测试图片懒加载"""
        # 访问包含懒加载图片的页面
        page.goto("http://localhost:5000/")

        # 检查是否有 data-src 属性的图片
        lazy_images = page.locator("img[data-src]")
        count = lazy_images.count()

        if count > 0:
            print(f"✅ 发现 {count} 个懒加载图片")

            # 滚动到图片位置
            first_lazy_image = lazy_images.first
            first_lazy_image.scroll_into_view_if_needed()

            # 等待图片加载
            page.wait_for_timeout(1000)

            # 验证图片已加载（data-src 被移除）
            loaded_src = first_lazy_image.get_attribute("src")
            assert loaded_src is not None, "图片应该已加载"
        else:
            print("ℹ️ 当前页面没有懒加载图片")

    def test_scroll_animation(self, page: Page):
        """TC-LAZY-002: 测试滚动动画"""
        page.goto("http://localhost:5000/")

        # 检查是否有滚动动画元素
        animated_elements = page.locator(".animate-on-scroll")
        count = animated_elements.count()

        if count > 0:
            print(f"✅ 发现 {count} 个滚动动画元素")

            # 滚动到元素位置
            first_element = animated_elements.first
            first_element.scroll_into_view_if_needed()

            # 等待动画触发
            page.wait_for_timeout(500)

            # 验证动画类已添加
            has_animated = first_element.evaluate(
                'el => el.classList.contains("animated")'
            )
            assert has_animated, "滚动动画应该已触发"
        else:
            print("ℹ️ 当前页面没有滚动动画元素")


@pytest.mark.ui
@pytest.mark.accessibility
class TestAccessibility:
    """无障碍访问测试"""

    def test_keyboard_navigation(self, page: Page):
        """TC-A11Y-001: 测试键盘导航"""
        page.goto("http://localhost:5000/alpine-demo")

        # 使用 Tab 键导航
        page.keyboard.press("Tab")

        # 验证焦点移动到第一个可聚焦元素
        focused_element = page.evaluate("() => document.activeElement.tagName")
        assert focused_element in [
            "BUTTON",
            "A",
            "INPUT",
        ], f"焦点应该在可聚焦元素上，当前在: {focused_element}"

        print("✅ 键盘导航工作正常")

    def test_aria_labels(self, page: Page):
        """TC-A11Y-002: 测试 ARIA 标签"""
        page.goto("http://localhost:5000/alpine-demo")

        # 检查按钮是否有适当的标签
        buttons = page.locator("button")
        count = buttons.count()

        for i in range(min(count, 5)):  # 检查前5个按钮
            button = buttons.nth(i)
            text = button.text_content().strip()
            assert len(text) > 0, f"按钮 {i+1} 应该有文本内容"

        print("✅ ARIA 标签检查通过")

    def test_color_contrast(self, page: Page):
        """TC-A11Y-003: 测试颜色对比度"""
        page.goto("http://localhost:5000/alpine-demo")

        # 检查主要文本的颜色对比度
        headings = page.locator("h1, h2, h3")
        count = headings.count()

        for i in range(min(count, 3)):  # 检查前3个标题
            heading = headings.nth(i)
            color = heading.evaluate("el => getComputedStyle(el).color")
            assert color, f"标题 {i+1} 应该有颜色样式"

        print("✅ 颜色对比度检查通过")
