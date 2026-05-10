"""
Playwright 测试基础 Fixture
提供浏览器、页面、登录等通用功能
"""
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, expect
from pathlib import Path
import shutil
from playwright_config import (
    BASE_URL, 
    SCREENSHOT_DIR, 
    VIDEO_DIR, 
    TRACE_DIR,
    TEST_USER,
    ADMIN_USER
)


@pytest.fixture(scope="session")
def browser():
    """会话级别的浏览器实例"""
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    
    # 使用chromium浏览器
    browser = playwright.chromium.launch(
        headless=False,  # 显示浏览器窗口
        slow_mo=0
    )
    
    yield browser
    
    browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def context(browser):
    """函数级别的浏览器上下文"""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        locale="zh-CN",
        timezone_id="Asia/Shanghai"
    )
    
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """函数级别的页面对象，每个测试使用新页面"""
    page = context.new_page()
    page.set_default_timeout(30000)
    
    yield page
    
    # 测试结束后关闭页面
    page.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page):
    """已登录的页面 fixture"""
    page.goto(f"{BASE_URL}/login")
    
    # 填写登录表单
    page.fill('input[name="username"]', TEST_USER["username"])
    page.fill('input[name="password"]', TEST_USER["password"])
    page.click('button[type="submit"]')
    
    # 等待登录成功（跳转到首页）
    page.wait_for_url("**/")
    
    yield page


@pytest.fixture(scope="function")
def admin_page(page: Page):
    """管理员登录的页面 fixture"""
    page.goto(f"{BASE_URL}/login")
    
    # 填写管理员登录表单
    page.fill('input[name="username"]', ADMIN_USER["username"])
    page.fill('input[name="password"]', ADMIN_USER["password"])
    page.click('button[type="submit"]')
    
    # 等待登录成功
    page.wait_for_url("**/")
    
    yield page


@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(page: Page, request):
    """测试失败时自动截图"""
    yield
    
    # 如果测试失败，截取屏幕快照
    if request.node.rep_call.failed:
        screenshot_path = f"{SCREENSHOT_DIR}/{request.node.name}.png"
        Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 测试失败截图已保存: {screenshot_path}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """捕获测试结果用于截图"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


class PlaywrightHelpers:
    """Playwright 辅助方法类"""
    
    @staticmethod
    def wait_for_element(page: Page, selector: str, timeout: int = 10000):
        """等待元素出现"""
        return page.wait_for_selector(selector, timeout=timeout)
    
    @staticmethod
    def click_and_wait(page: Page, selector: str, wait_time: float = 1.0):
        """点击元素并等待"""
        page.click(selector)
        page.wait_for_timeout(wait_time * 1000)
    
    @staticmethod
    def fill_and_submit(page: Page, form_selector: str, data: dict):
        """填充表单并提交"""
        for field, value in data.items():
            page.fill(f'{form_selector} [name="{field}"]', str(value))
        page.click(f'{form_selector} button[type="submit"]')
    
    @staticmethod
    def assert_element_visible(page: Page, selector: str, message: str = ""):
        """断言元素可见"""
        element = page.locator(selector)
        assert element.is_visible(), message or f"元素 {selector} 不可见"
    
    @staticmethod
    def assert_text_contains(page: Page, selector: str, expected_text: str):
        """断言元素包含指定文本"""
        element = page.locator(selector)
        actual_text = element.text_content()
        assert expected_text in actual_text, \
            f"期望包含 '{expected_text}'，实际: '{actual_text}'"
    
    @staticmethod
    def take_screenshot(page: Page, name: str):
        """截取屏幕快照"""
        Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
        path = f"{SCREENSHOT_DIR}/{name}.png"
        page.screenshot(path=path, full_page=True)
        return path


@pytest.fixture
def helpers():
    """提供辅助方法"""
    return PlaywrightHelpers()
