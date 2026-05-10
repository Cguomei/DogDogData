"""
Playwright 自动化测试配置
包含浏览器配置、基础 URL、超时设置等
"""
import os

# 基础配置
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5000")
BROWSER_TYPE = os.getenv("TEST_BROWSER", "chromium")  # chromium, firefox, webkit
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"  # 默认显示浏览器窗口
SLOW_MO = int(os.getenv("TEST_SLOW_MO", "0"))  # 慢动作模式（毫秒）
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30000"))  # 默认超时 30 秒

# 截图配置
SCREENSHOT_DIR = "Test/reports/screenshots"
VIDEO_DIR = "Test/reports/videos"
TRACE_DIR = "Test/reports/traces"

# 测试用户配置
TEST_USER = {
    "username": os.getenv("TEST_USERNAME", "testuser"),
    "password": os.getenv("TEST_PASSWORD", "Test@123456")
}

ADMIN_USER = {
    "username": os.getenv("ADMIN_USERNAME", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "Admin@123456")
}


def get_browser_context(playwright_instance):
    """获取浏览器上下文配置"""
    if BROWSER_TYPE == "firefox":
        browser = playwright_instance.firefox.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )
    elif BROWSER_TYPE == "webkit":
        browser = playwright_instance.webkit.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )
    else:
        browser = playwright_instance.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        locale="zh-CN",
        timezone_id="Asia/Shanghai"
    )
    
    return browser, context
