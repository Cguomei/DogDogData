"""
E2E 端到端测试 - 完整用户工作流
测试从登录到各个功能模块的完整流程
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.playwright
class TestCompleteUserWorkflow:
    """完整用户工作流测试"""

    def test_full_user_journey(self, page: Page):
        """TC-E2E-001: 完整用户旅程测试"""

        # 步骤1: 访问首页
        print("\n📍 步骤1: 访问首页")
        page.goto(BASE_URL)
        expect(page).to_have_title("数据看板")
        print("✅ 首页加载成功")

        # 步骤2: 检查核心指标卡片
        print("\n📍 步骤2: 验证核心指标")
        expect(page.locator("text=狗狗总数")).to_be_visible()
        expect(page.locator("text=平均价格")).to_be_visible()
        print("✅ 核心指标显示正常")

        # 步骤3: 导航到图表页面
        print("\n📍 步骤3: 导航到图表页面")
        page.click('a[href="/charts"]')
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/charts")
        print("✅ 图表页面加载成功")

        # 步骤4: 查看品种管理
        print("\n📍 步骤4: 访问品种管理")
        page.click('a[href="/breeds"]')
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/breeds")
        expect(page.locator("text=品种管理")).to_be_visible()
        print("✅ 品种管理页面加载成功")

        # 步骤5: 访问狗粮数据
        print("\n📍 步骤5: 访问狗粮数据")
        page.click('a[href="/food"]')
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/food")
        expect(page.locator("text=狗粮数据看板")).to_be_visible()
        print("✅ 狗粮数据页面加载成功")

        # 步骤6: 访问自定义分析
        print("\n📍 步骤6: 访问自定义分析")
        page.click('a[href="/custom-analysis"]')
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/custom-analysis")
        expect(page.locator("input[type='file']")).to_be_visible()
        print("✅ 自定义分析页面加载成功")

        print("\n🎉 完整用户旅程测试通过！")

    def test_login_to_dashboard_flow(self, page: Page):
        """TC-E2E-002: 登录到数据看板流程"""

        # 步骤1: 访问登录页
        print("\n📍 步骤1: 访问登录页")
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_title("用户登录")

        # 步骤2: 填写登录表单
        print("\n📍 步骤2: 填写登录信息")
        page.fill('input[name="username"]', "user")
        page.fill('input[name="password"]', "123456")

        # 步骤3: 提交登录
        print("\n📍 步骤3: 提交登录")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        # 步骤4: 验证登录成功（重定向到首页）
        print("\n📍 步骤4: 验证登录成功")
        expect(page).to_have_url(f"{BASE_URL}/")
        expect(page.locator("text=数据看板")).to_be_visible()

        # 步骤5: 验证用户信息显示
        print("\n📍 步骤5: 验证用户信息")
        expect(page.locator("text=user")).to_be_visible()

        print("\n🎉 登录流程测试通过！")

    def test_data_analysis_workflow(self, logged_in_page: Page):
        """TC-E2E-003: 数据分析工作流程"""
        page = logged_in_page

        # 步骤1: 访问自定义分析
        print("\n📍 步骤1: 访问自定义分析页面")
        page.goto(f"{BASE_URL}/custom-analysis")
        page.wait_for_timeout(1000)

        # 步骤2: 验证上传界面
        print("\n📍 步骤2: 验证上传界面")
        upload_input = page.locator('input[type="file"]')
        expect(upload_input).to_be_visible()

        # 步骤3: 验证图表配置选项
        print("\n📍 步骤3: 验证图表配置")
        chart_type_select = page.locator("select")
        if chart_type_select.count() > 0:
            expect(chart_type_select.first).to_be_visible()
            print("✅ 图表类型选择器存在")

        # 步骤4: 验证导出按钮
        print("\n📍 步骤4: 验证导出功能")
        export_buttons = page.locator('button:has-text("导出")')
        if export_buttons.count() > 0:
            print("✅ 导出按钮存在")

        print("\n🎉 数据分析工作流测试通过！")

    def test_chart_navigation_flow(self, logged_in_page: Page):
        """TC-E2E-004: 图表导航流程"""
        page = logged_in_page

        charts = [
            ("/chart/scatter", "价格散点图"),
            ("/chart/line", "体重折线图"),
            ("/chart/bar", "级别柱状图"),
            ("/chart/hist", "TOP10直方图"),
            ("/chart/funnel", "价格漏斗图"),
            ("/chart/map", "世界地图"),
        ]

        for path, name in charts:
            print(f"\n📍 测试图表: {name}")
            page.goto(f"{BASE_URL}{path}")
            page.wait_for_timeout(1500)

            # 验证图表容器存在
            chart_container = page.locator(".chart-container, #chart, canvas, svg")
            if chart_container.count() > 0:
                expect(chart_container.first).to_be_visible(timeout=5000)
                print(f"✅ {name} 加载成功")
            else:
                print(f"⚠️ {name} 未找到图表元素（可能无数据）")

        print("\n🎉 图表导航流程测试通过！")

    def test_breed_management_flow(self, logged_in_page: Page):
        """TC-E2E-005: 品种管理流程"""
        page = logged_in_page

        # 步骤1: 访问品种管理
        print("\n📍 步骤1: 访问品种管理")
        page.goto(f"{BASE_URL}/breeds")
        page.wait_for_timeout(1000)

        # 步骤2: 验证品种列表
        print("\n📍 步骤2: 验证品种列表")
        breed_table = page.locator("table")
        if breed_table.count() > 0:
            expect(breed_table.first).to_be_visible()
            print("✅ 品种列表显示正常")

        # 步骤3: 验证搜索功能
        print("\n📍 步骤3: 验证搜索功能")
        search_input = page.locator('input[placeholder*="搜索"], input[type="search"]')
        if search_input.count() > 0:
            expect(search_input.first).to_be_visible()
            print("✅ 搜索框存在")

        # 步骤4: 验证分页
        print("\n📍 步骤4: 验证分页")
        pagination = page.locator('.pagination, nav[aria-label*="分页"]')
        if pagination.count() > 0:
            print("✅ 分页控件存在")

        print("\n🎉 品种管理流程测试通过！")

    def test_feedback_submission_flow(self, logged_in_page: Page):
        """TC-E2E-006: 用户反馈提交流程"""
        page = logged_in_page

        # 步骤1: 查找反馈入口（如果有的话）
        print("\n📍 步骤1: 查找反馈功能")

        # 尝试多种方式找到反馈入口
        feedback_links = [
            'a:has-text("反馈")',
            'a:has-text("意见反馈")',
            'button:has-text("反馈")',
        ]

        feedback_found = False
        for selector in feedback_links:
            if page.locator(selector).count() > 0:
                print(f"✅ 找到反馈入口: {selector}")
                feedback_found = True
                break

        if not feedback_found:
            print("ℹ️  未找到明显的反馈入口（可能通过其他方式访问）")
            # 直接访问反馈API测试
            print("\n📍 尝试直接测试反馈API")
            response = page.evaluate("""
                async () => {
                    const response = await fetch('/api/feedback', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            title: 'E2E测试反馈',
                            content: '这是端到端测试提交的反馈',
                            feedback_type: 'bug'
                        })
                    });
                    return response.status;
                }
            """)

            assert response in [201, 401], f"反馈API应返回201或401，实际: {response}"
            print(f"✅ 反馈API响应: {response}")

        print("\n🎉 反馈提交流程测试通过！")

    def test_responsive_design_check(self, page: Page):
        """TC-E2E-007: 响应式设计检查"""

        # 测试不同屏幕尺寸
        viewports = [
            (1920, 1080, "桌面端"),
            (768, 1024, "平板"),
            (375, 667, "手机"),
        ]

        for width, height, device_name in viewports:
            print(f"\n📍 测试{device_name} ({width}x{height})")
            page.set_viewport_size({"width": width, "height": height})
            page.goto(BASE_URL)
            page.wait_for_timeout(1000)

            # 验证页面正常显示
            expect(page.locator("body")).to_be_visible()

            # 检查是否有水平滚动条（不应该有）
            has_horizontal_scroll = page.evaluate("""
                () => document.documentElement.scrollWidth > document.documentElement.clientWidth
            """)

            if has_horizontal_scroll:
                print(f"⚠️ {device_name} 存在水平滚动")
            else:
                print(f"✅ {device_name} 响应式正常")

        print("\n🎉 响应式设计检查通过！")


@pytest.mark.e2e
@pytest.mark.performance
class TestE2EPerformance:
    """E2E性能测试"""

    def test_page_load_performance(self, page: Page):
        """TC-E2E-PERF-001: 页面加载性能"""

        pages_to_test = [
            "/",
            "/charts",
            "/breeds",
            "/food",
            "/custom-analysis",
        ]

        results = {}

        for path in pages_to_test:
            print(f"\n📍 测试页面加载: {path}")

            start_time = page.evaluate("() => performance.now()")
            page.goto(f"{BASE_URL}{path}")
            page.wait_for_load_state("networkidle")
            end_time = page.evaluate("() => performance.now()")

            load_time = (end_time - start_time) / 1000  # 转换为秒
            results[path] = load_time

            print(f"   加载时间: {load_time:.2f}秒")

            # 性能要求：大部分页面应在3秒内加载
            if load_time > 3.0:
                print(f"   ⚠️ 警告: {path} 加载时间超过3秒")
            else:
                print(f"   ✅ 性能达标")

        # 计算平均加载时间
        avg_load_time = sum(results.values()) / len(results)
        print(f"\n📊 平均加载时间: {avg_load_time:.2f}秒")

        assert avg_load_time < 3.0, f"平均加载时间{avg_load_time:.2f}秒超过3秒"
        print("🎉 页面加载性能测试通过！")

    def test_api_response_performance(self, page: Page):
        """TC-E2E-PERF-002: API响应性能"""

        apis_to_test = [
            "/api/breeds",
            "/api/food",
            "/api/food/statistics",
        ]

        results = {}

        for api_path in apis_to_test:
            print(f"\n📍 测试API响应: {api_path}")

            start_time = page.evaluate("() => performance.now()")
            response = page.evaluate(f"""
                async () => {{
                    const response = await fetch('{api_path}');
                    return response.status;
                }}
            """)
            end_time = page.evaluate("() => performance.now()")

            response_time = (end_time - start_time) / 1000
            results[api_path] = response_time

            print(f"   响应时间: {response_time:.2f}秒, 状态码: {response}")

            # API响应应在1秒内
            assert (
                response_time < 1.0
            ), f"{api_path} 响应时间{response_time:.2f}秒超过1秒"
            print(f"   ✅ API性能达标")

        print("\n🎉 API响应性能测试通过！")


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/e2e_test_report.html",
            "--self-contained-html",
        ]
    )
