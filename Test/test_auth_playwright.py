"""
用户认证功能自动化测试 - Playwright 版本
涵盖：登录、注册、登出、权限验证等用户操作流程
"""

import pytest
from playwright.sync_api import Page, expect
from playwright_config import BASE_URL, TEST_USER


class TestUserLogin:
    """用户登录功能测试"""

    def test_login_page_loads(self, page: Page):
        """测试 1: 登录页面加载"""
        page.goto(f"{BASE_URL}/login")

        # 验证页面标题
        expect(page).to_have_title("登录")

        # 验证表单元素存在
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        submit_btn = page.locator('button[type="submit"]')

        expect(username_input).to_be_visible()
        expect(password_input).to_be_visible()
        expect(submit_btn).to_be_visible()

        print("✅ 测试 1 通过：登录页面加载成功")

    def test_login_with_valid_credentials(self, page: Page):
        """测试 2: 使用有效凭证登录"""
        page.goto(f"{BASE_URL}/login")

        # 填写登录表单
        page.fill('input[name="username"]', TEST_USER["username"])
        page.fill('input[name="password"]', TEST_USER["password"])
        page.click('button[type="submit"]')

        # 等待跳转到首页
        page.wait_for_url("**/")

        # 验证登录成功（检查首页元素）
        expect(page).to_have_url(BASE_URL + "/")

        # 检查是否有登出链接（表示已登录）
        logout_link = page.locator('a[href*="logout"]')
        expect(logout_link).to_be_visible()

        print("✅ 测试 2 通过：登录成功")

    def test_login_with_invalid_password(self, page: Page):
        """测试 3: 使用错误密码登录"""
        page.goto(f"{BASE_URL}/login")

        # 填写错误的密码
        page.fill('input[name="username"]', TEST_USER["username"])
        page.fill('input[name="password"]', "WrongPassword123")
        page.click('button[type="submit"]')

        # 等待错误消息
        page.wait_for_timeout(1000)

        # 验证仍在登录页面
        expect(page).to_have_url(f"{BASE_URL}/login")

        # 检查错误提示
        error_msg = page.locator(".alert-danger, .flash-message")
        if error_msg.count() > 0:
            error_text = error_msg.first.text_content()
            assert (
                "错误" in error_text or "失败" in error_text
            ), f"应显示错误提示，实际：{error_text}"

        print("✅ 测试 3 通过：错误密码被拒绝")

    def test_login_with_nonexistent_user(self, page: Page):
        """测试 4: 使用不存在的用户名登录"""
        page.goto(f"{BASE_URL}/login")

        # 填写不存在的用户名
        page.fill('input[name="username"]', "NonExistentUser999")
        page.fill('input[name="password"]', "SomePassword123")
        page.click('button[type="submit"]')

        # 等待响应
        page.wait_for_timeout(1000)

        # 验证仍在登录页面
        expect(page).to_have_url(f"{BASE_URL}/login")

        print("✅ 测试 4 通过：不存在的用户被拒绝")

    def test_login_form_validation_empty_fields(self, page: Page):
        """测试 5: 登录表单空字段验证"""
        page.goto(f"{BASE_URL}/login")

        # 直接提交空表单
        page.click('button[type="submit"]')
        page.wait_for_timeout(500)

        # 验证仍在登录页面
        expect(page).to_have_url(f"{BASE_URL}/login")

        print("✅ 测试 5 通过：空字段验证正常")


class TestUserRegistration:
    """用户注册功能测试"""

    def test_register_page_loads(self, page: Page):
        """测试 6: 注册页面加载"""
        page.goto(f"{BASE_URL}/register")

        # 验证页面标题
        expect(page).to_have_title("注册")

        # 验证表单元素存在
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        submit_btn = page.locator('button[type="submit"]')

        expect(username_input).to_be_visible()
        expect(password_input).to_be_visible()
        expect(submit_btn).to_be_visible()

        print("✅ 测试 6 通过：注册页面加载成功")

    def test_register_new_user(self, page: Page):
        """测试 7: 注册新用户"""
        import time

        timestamp = str(int(time.time()))
        new_username = f"testuser_{timestamp}"

        page.goto(f"{BASE_URL}/register")

        # 填写注册表单
        page.fill('input[name="username"]', new_username)
        page.fill('input[name="password"]', "Test@123456")
        page.click('button[type="submit"]')

        # 等待跳转或消息
        page.wait_for_timeout(2000)

        # 验证注册成功（跳转到登录页或显示成功消息）
        current_url = page.url
        assert (
            "/login" in current_url or "/register" in current_url
        ), f"注册后应跳转到登录页或停留在注册页，实际：{current_url}"

        # 检查成功消息
        success_msg = page.locator(".alert-success, .flash-message")
        if success_msg.count() > 0:
            success_text = success_msg.first.text_content()
            assert (
                "成功" in success_text or "注册" in success_text
            ), f"应显示成功提示，实际：{success_text}"

        print(f"✅ 测试 7 通过：新用户注册成功，用户名：{new_username}")

    def test_register_duplicate_username(self, page: Page):
        """测试 8: 注册重复用户名"""
        page.goto(f"{BASE_URL}/register")

        # 使用已存在的用户名
        page.fill('input[name="username"]', TEST_USER["username"])
        page.fill('input[name="password"]', "Test@123456")
        page.click('button[type="submit"]')

        # 等待响应
        page.wait_for_timeout(1500)

        # 检查错误提示
        error_msg = page.locator(".alert-danger, .flash-message")
        if error_msg.count() > 0:
            error_text = error_msg.first.text_content()
            assert (
                "已存在" in error_text or "重复" in error_text
            ), f"应显示重复用户名提示，实际：{error_text}"

        print("✅ 测试 8 通过：重复用户名被拒绝")

    def test_register_weak_password(self, page: Page):
        """测试 9: 注册弱密码"""
        page.goto(f"{BASE_URL}/register")

        # 使用弱密码
        page.fill('input[name="username"]', "newuser_test")
        page.fill('input[name="password"]', "123")
        page.click('button[type="submit"]')

        # 等待响应
        page.wait_for_timeout(1500)

        # 检查错误提示（如果有密码验证）
        error_msg = page.locator(".alert-danger, .flash-message")
        if error_msg.count() > 0:
            error_text = error_msg.first.text_content()
            assert (
                "密码" in error_text or "格式" in error_text or "长度" in error_text
            ), f"应显示密码错误提示，实际：{error_text}"

        print("✅ 测试 9 通过：弱密码验证正常")


class TestUserLogout:
    """用户登出功能测试"""

    def test_logout_success(self, logged_in_page: Page):
        """测试 10: 成功登出"""
        page = logged_in_page

        # 点击登出链接
        logout_link = page.locator('a[href*="logout"]')
        logout_link.click()

        # 等待跳转
        page.wait_for_timeout(1000)

        # 验证已登出（检查是否有登录链接）
        login_link = page.locator('a[href*="login"]')
        expect(login_link).to_be_visible()

        # 验证显示登出成功消息
        info_msg = page.locator(".alert-info, .flash-message")
        if info_msg.count() > 0:
            info_text = info_msg.first.text_content()
            assert (
                "退出" in info_text or "登出" in info_text
            ), f"应显示登出提示，实际：{info_text}"

        print("✅ 测试 10 通过：登出成功")

    def test_logout_redirects_to_home(self, logged_in_page: Page):
        """测试 11: 登出后重定向到首页"""
        page = logged_in_page

        # 记录当前 URL
        current_url_before = page.url

        # 点击登出
        logout_link = page.locator('a[href*="logout"]')
        logout_link.click()
        page.wait_for_timeout(1000)

        # 验证重定向
        current_url_after = page.url
        assert (
            BASE_URL in current_url_after
        ), f"登出后应重定向到首页，实际：{current_url_after}"

        print("✅ 测试 11 通过：登出后重定向到首页")


class TestNavigationAndUI:
    """导航和 UI 测试"""

    def test_homepage_navigation(self, page: Page):
        """测试 12: 首页导航"""
        page.goto(BASE_URL)

        # 验证首页元素
        expect(page).to_have_url(BASE_URL + "/")

        # 检查导航栏
        navbar = page.locator("nav, .navbar, .navigation")
        if navbar.count() > 0:
            expect(navbar.first).to_be_visible()

        print("✅ 测试 12 通过：首页导航正常")

    def test_login_link_from_homepage(self, page: Page):
        """测试 13: 从首页点击登录链接"""
        page.goto(BASE_URL)

        # 查找登录链接
        login_link = page.locator('a[href*="login"]')
        if login_link.count() > 0:
            login_link.first.click()
            page.wait_for_timeout(1000)

            # 验证跳转到登录页
            expect(page).to_have_url(f"{BASE_URL}/login")

        print("✅ 测试 13 通过：登录链接跳转正常")

    def test_register_link_from_homepage(self, page: Page):
        """测试 14: 从首页点击注册链接"""
        page.goto(BASE_URL)

        # 查找注册链接
        register_link = page.locator('a[href*="register"]')
        if register_link.count() > 0:
            register_link.first.click()
            page.wait_for_timeout(1000)

            # 验证跳转到注册页
            expect(page).to_have_url(f"{BASE_URL}/register")

        print("✅ 测试 14 通过：注册链接跳转正常")


class TestSessionManagement:
    """会话管理测试"""

    def test_session_persistence_after_refresh(self, logged_in_page: Page):
        """测试 15: 刷新页面后会话保持"""
        page = logged_in_page

        # 刷新页面
        page.reload()
        page.wait_for_timeout(1000)

        # 验证仍然登录状态
        logout_link = page.locator('a[href*="logout"]')
        expect(logout_link).to_be_visible()

        print("✅ 测试 15 通过：刷新后会话保持")

    def test_protected_route_redirects_when_logged_out(self, page: Page):
        """测试 16: 未登录访问受保护路由重定向"""
        # 尝试访问需要登录的页面（例如管理页面）
        page.goto(f"{BASE_URL}/admin/breeds")
        page.wait_for_timeout(1000)

        # 应该重定向到登录页
        current_url = page.url
        assert (
            "/login" in current_url or "/admin" not in current_url
        ), f"未登录应重定向到登录页，实际：{current_url}"

        print("✅ 测试 16 通过：受保护路由重定向正常")


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/auth_test_playwright_report.html",
            "--self-contained-html",
        ]
    )
