"""
网页小宠物功能自动化测试 - Selenium 版本
（当 playwright 安装失败时使用此版本）
涵盖：UI 交互、状态管理、基础功能等
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


class TestVirtualPetSelenium:
    """虚拟宠物功能测试类（Selenium 版本）"""

    @pytest.fixture(scope="function")
    def driver(self):
        """浏览器 fixture"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    @pytest.fixture(scope="function")
    def pet_page(self, driver):
        """访问首页并等待宠物加载"""
        driver.get("http://localhost:5000/")
        # 等待宠物容器出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".virtual-pet-container"))
        )
        return driver

    def test_pet_initialization(self, pet_page):
        """测试 1: 宠物初始化"""
        # 检查宠物容器是否存在
        container = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet-container")
        assert container.is_displayed(), "宠物容器应该可见"

        # 检查宠物身体是否存在
        pet_body = pet_page.find_element(By.CSS_SELECTOR, ".pet-body")
        assert pet_body.is_displayed(), "宠物身体应该可见"

        # 检查宠物 emoji 是否显示
        pet_emoji = pet_page.find_element(By.CSS_SELECTOR, ".pet-emoji")
        emoji_text = pet_emoji.text
        assert emoji_text == "🐶", f"期望显示🐶，实际显示：{emoji_text}"

        # 检查状态条是否存在
        status_bars = pet_page.find_elements(By.CSS_SELECTOR, ".status-bar")
        assert len(status_bars) == 2, f"应该有 2 个状态条，实际{len(status_bars)}个"

        print("✅ 测试 1 通过：宠物初始化成功")

    def test_pet_click_interaction(self, pet_page):
        """测试 2: 点击互动"""
        from selenium.webdriver.common.action_chains import ActionChains

        # 点击宠物身体
        pet_body = pet_page.find_element(By.CSS_SELECTOR, ".pet-body")
        ActionChains(pet_page).move_to_element(pet_body).click().perform()

        # 等待动画类出现
        time.sleep(0.5)
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        classes = pet_element.get_attribute("class")
        assert "animate-bounce" in classes, "应该播放弹跳动画"

        # 等待对话气泡显示
        time.sleep(1.5)
        bubble = pet_page.find_element(By.CSS_SELECTOR, ".pet-bubble.show")
        assert bubble.is_displayed(), "对话气泡应该显示"

        bubble_text = bubble.text
        assert len(bubble_text) > 0, "对话内容不应为空"
        print(f"✅ 测试 2 通过：点击互动成功，对话内容：{bubble_text}")

    def test_action_buttons_visibility(self, pet_page):
        """测试 3: 动作按钮悬停显示"""
        from selenium.webdriver.common.action_chains import ActionChains

        # 鼠标悬停在宠物上
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        ActionChains(pet_page).move_to_element(pet_element).perform()
        time.sleep(0.5)

        # 检查所有动作按钮
        action_buttons = pet_page.find_elements(By.CSS_SELECTOR, ".action-btn")
        assert (
            len(action_buttons) == 4
        ), f"应该有 4 个动作按钮，实际{len(action_buttons)}个"

        # 验证每个按钮的 emoji
        expected_emojis = ["🍖", "🎾", "❤️", "💤"]
        for i, button in enumerate(action_buttons):
            emoji = button.text
            assert (
                emoji == expected_emojis[i]
            ), f"按钮{i}期望{expected_emojis[i]}，实际{emoji}"

        print("✅ 测试 3 通过：动作按钮显示正确")

    def test_feed_action(self, pet_page):
        """测试 4: 喂食功能"""
        from selenium.webdriver.common.action_chains import ActionChains

        # 悬停显示按钮
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        ActionChains(pet_page).move_to_element(pet_element).perform()
        time.sleep(0.3)

        # 点击喂食按钮
        feed_btn = pet_page.find_element(
            By.CSS_SELECTOR, '.action-btn[data-action="feed"]'
        )
        feed_btn.click()

        # 等待动画
        time.sleep(1.2)

        # 检查对话气泡
        bubble = pet_page.find_element(By.CSS_SELECTOR, ".pet-bubble.show")
        assert bubble.is_displayed(), "对话气泡应该显示"

        # 验证对话内容包含吃的相关词汇
        bubble_text = bubble.text
        feed_keywords = ["好吃", "美味", "嗷呜", "还要"]
        has_keyword = any(keyword in bubble_text for keyword in feed_keywords)
        assert has_keyword, f"喂食对话应包含吃的词汇，实际：{bubble_text}"

        print(f"✅ 测试 4 通过：喂食功能正常，对话：{bubble_text}")

    def test_status_bar_exists(self, pet_page):
        """测试 5: 状态条存在"""
        # 检查饥饿度状态条
        hunger_bar = pet_page.find_element(By.CSS_SELECTOR, ".hunger-bar .status-fill")
        assert hunger_bar.is_displayed(), "饥饿度状态条应该显示"

        # 检查活力值状态条
        energy_bar = pet_page.find_element(By.CSS_SELECTOR, ".energy-bar .status-fill")
        assert energy_bar.is_displayed(), "活力值状态条应该显示"

        # 检查宽度属性
        hunger_style = hunger_bar.get_attribute("style")
        assert "width:" in hunger_style, "状态条应该有宽度样式"

        print("✅ 测试 5 通过：状态条存在且正常")

    def test_sleep_button(self, pet_page):
        """测试 6: 睡眠按钮功能"""
        from selenium.webdriver.common.action_chains import ActionChains

        # 悬停显示按钮
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        ActionChains(pet_page).move_to_element(pet_element).perform()
        time.sleep(0.3)

        # 点击睡觉按钮
        sleep_btn = pet_page.find_element(
            By.CSS_SELECTOR, '.action-btn[data-action="sleep"]'
        )
        sleep_btn.click()

        # 等待动画
        time.sleep(1.2)

        # 检查宠物是否进入睡眠状态
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        classes = pet_element.get_attribute("class")
        assert "sleeping" in classes, "宠物应该进入睡眠状态"

        print("✅ 测试 6 通过：睡眠切换功能正常")

    def test_summon_button_appears(self, pet_page):
        """测试 7: 召唤按钮出现"""
        # 通过 JavaScript 触发隐藏
        pet_page.execute_script("""
            if (window.virtualPet) {
                window.virtualPet.hide();
            }
        """)

        time.sleep(1)

        # 检查召唤按钮是否出现
        summon_btn = pet_page.find_element(By.ID, "summon-pet-btn")
        assert summon_btn.is_displayed(), "召唤按钮应该显示"

        # 验证按钮内容
        btn_text = summon_btn.text
        assert "🐶" in btn_text, "召唤按钮应该包含🐶 emoji"

        print("✅ 测试 7 通过：召唤按钮出现")

    def test_local_storage(self, pet_page):
        """测试 8: localStorage 存储"""
        # 与宠物互动
        pet_body = pet_page.find_element(By.CSS_SELECTOR, ".pet-body")
        pet_body.click()
        time.sleep(1)

        # 检查 localStorage
        storage = pet_page.execute_script(
            "return localStorage.getItem('virtualPetState');"
        )
        assert storage is not None, "localStorage 应该保存宠物状态"

        state_data = json.loads(storage)
        assert "hunger" in state_data, "状态应包含饥饿度"
        assert "energy" in state_data, "状态应包含活力值"
        assert "affection" in state_data, "状态应包含亲密度"

        print(f"✅ 测试 8 通过：状态持久化正常")

    def test_pet_name_display(self, pet_page):
        """测试 9: 宠物名称显示"""
        pet_name = pet_page.find_element(By.CSS_SELECTOR, ".pet-name")
        name_text = pet_name.text
        assert len(name_text) > 0, "宠物名称不应为空"
        print(f"✅ 测试 9 通过：宠物名称显示：{name_text}")

    def test_mouse_hover(self, pet_page):
        """测试 10: 鼠标悬停事件"""
        from selenium.webdriver.common.action_chains import ActionChains

        # 鼠标悬停
        pet_element = pet_page.find_element(By.CSS_SELECTOR, ".virtual-pet")
        ActionChains(pet_page).move_to_element(pet_element).perform()

        # 等待对话气泡显示
        time.sleep(0.5)

        # 检查对话气泡
        bubble = pet_page.find_element(By.CSS_SELECTOR, ".pet-bubble.show")
        assert bubble.is_displayed(), "对话气泡应该显示"

        # 验证对话内容
        bubble_text = bubble.text
        assert "玩" in bubble_text, f"悬停对话应包含'玩'，实际：{bubble_text}"

        print(f"✅ 测试 10 通过：鼠标悬停事件正常，对话：{bubble_text}")


# 性能测试类
class TestPetPerformanceSelenium:
    """宠物性能测试（Selenium 版本）"""

    @pytest.fixture(scope="function")
    def driver(self):
        """浏览器 fixture"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def test_load_time(self, driver):
        """测试 11: 加载时间"""
        start_time = time.time()
        driver.get("http://localhost:5000/")

        # 等待宠物容器出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".virtual-pet-container"))
        )
        end_time = time.time()

        load_time = end_time - start_time
        print(f"✅ 测试 11 通过：宠物加载时间：{load_time:.2f}秒")

        # 断言：加载时间应小于 3 秒
        assert load_time < 3.0, f"加载时间过长：{load_time}秒"


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/pet_test_selenium_report.html",
            "--self-contained-html",
        ]
    )
