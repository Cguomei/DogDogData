"""
UI测试的conftest - 使用pytest-playwright内置fixtures
"""
# pytest-playwright插件已经提供了page, context, browser等fixtures
# 我们只需要添加登录相关的fixture

import pytest
from playwright.sync_api import Page, expect
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright_config import BASE_URL, TEST_USER, ADMIN_USER


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
