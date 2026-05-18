"""
虚拟宠物功能自动化测试 - Playwright 版本
涵盖：UI 交互、状态管理、动作按钮、数据持久化等
"""

import pytest
from playwright.sync_api import Page, expect
from playwright_config import BASE_URL


class TestVirtualPetInitialization:
    """虚拟宠物初始化测试"""

    def test_pet_container_exists(self, page: Page):
        """测试 1: 宠物容器存在"""
        page.goto(BASE_URL)

        # 等待宠物容器加载
        pet_container = page.locator(".virtual-pet-container")
        expect(pet_container).to_be_visible(timeout=10000)

        print("✅ 测试 1 通过：宠物容器存在且可见")

    def test_pet_body_visible(self, page: Page):
        """测试 2: 宠物身体可见"""
        page.goto(BASE_URL)

        pet_body = page.locator(".pet-body")
        expect(pet_body).to_be_visible()

        print("✅ 测试 2 通过：宠物身体可见")

    def test_pet_emoji_display(self, page: Page):
        """测试 3: 宠物 Emoji 显示正确"""
        page.goto(BASE_URL)

        pet_emoji = page.locator(".pet-emoji")
        emoji_text = pet_emoji.text_content()
        assert emoji_text == "🐶", f"期望显示🐶，实际显示：{emoji_text}"

        print("✅ 测试 3 通过：宠物 Emoji 显示正确")

    def test_status_bars_exist(self, page: Page):
        """测试 4: 状态条存在"""
        page.goto(BASE_URL)

        # 检查饥饿度状态条
        hunger_bar = page.locator(".hunger-bar .status-fill")
        expect(hunger_bar).to_be_visible()

        # 检查活力值状态条
        energy_bar = page.locator(".energy-bar .status-fill")
        expect(energy_bar).to_be_visible()

        # 验证状态条数量
        status_bars = page.locator(".status-bar")
        assert (
            status_bars.count() == 2
        ), f"应该有 2 个状态条，实际{status_bars.count()}个"

        print("✅ 测试 4 通过：状态条存在且正确")

    def test_pet_name_display(self, page: Page):
        """测试 5: 宠物名称显示"""
        page.goto(BASE_URL)

        pet_name = page.locator(".pet-name")
        name_text = pet_name.text_content()
        assert len(name_text.strip()) > 0, "宠物名称不应为空"

        print(f"✅ 测试 5 通过：宠物名称显示：{name_text}")


class TestPetInteraction:
    """宠物互动功能测试"""

    def test_click_pet_animation(self, page: Page):
        """测试 6: 点击宠物触发动画"""
        page.goto(BASE_URL)

        # 点击宠物身体
        pet_body = page.locator(".pet-body")
        pet_body.click()

        # 等待动画类出现
        page.wait_for_timeout(500)
        pet_element = page.locator(".virtual-pet")
        classes = pet_element.get_attribute("class")
        assert "animate-bounce" in classes, "应该播放弹跳动画"

        print("✅ 测试 6 通过：点击触发动画")

    def test_click_pet_dialog(self, page: Page):
        """测试 7: 点击宠物显示对话气泡"""
        page.goto(BASE_URL)

        # 点击宠物
        pet_body = page.locator(".pet-body")
        pet_body.click()

        # 等待对话气泡显示
        page.wait_for_timeout(1500)
        bubble = page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()

        bubble_text = bubble.text_content()
        assert len(bubble_text.strip()) > 0, "对话内容不应为空"

        print(f"✅ 测试 7 通过：点击显示对话，内容：{bubble_text}")

    def test_hover_show_action_buttons(self, page: Page):
        """测试 8: 悬停显示动作按钮"""
        page.goto(BASE_URL)

        # 鼠标悬停在宠物上
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(500)

        # 检查所有动作按钮
        action_buttons = page.locator(".action-btn")
        assert (
            action_buttons.count() == 4
        ), f"应该有 4 个动作按钮，实际{action_buttons.count()}个"

        # 验证每个按钮的 emoji
        expected_emojis = ["🍖", "🎾", "❤️", "💤"]
        for i in range(4):
            button = action_buttons.nth(i)
            emoji = button.text_content()
            assert (
                emoji == expected_emojis[i]
            ), f"按钮{i}期望{expected_emojis[i]}，实际{emoji}"

        print("✅ 测试 8 通过：悬停显示 4 个动作按钮")

    def test_feed_action(self, page: Page):
        """测试 9: 喂食功能"""
        page.goto(BASE_URL)

        # 悬停显示按钮
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(300)

        # 点击喂食按钮
        feed_btn = page.locator('.action-btn[data-action="feed"]')
        feed_btn.click()

        # 等待动画和对话
        page.wait_for_timeout(1200)

        # 检查对话气泡
        bubble = page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()

        # 验证对话内容包含吃的相关词汇
        bubble_text = bubble.text_content()
        feed_keywords = ["好吃", "美味", "嗷呜", "还要"]
        has_keyword = any(keyword in bubble_text for keyword in feed_keywords)
        assert has_keyword, f"喂食对话应包含吃的词汇，实际：{bubble_text}"

        print(f"✅ 测试 9 通过：喂食功能正常，对话：{bubble_text}")

    def test_play_action(self, page: Page):
        """测试 10: 玩耍功能"""
        page.goto(BASE_URL)

        # 悬停显示按钮
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(300)

        # 点击玩耍按钮
        play_btn = page.locator('.action-btn[data-action="play"]')
        play_btn.click()

        # 等待动画
        page.wait_for_timeout(1200)

        # 检查对话气泡
        bubble = page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()

        bubble_text = bubble.text_content()
        play_keywords = ["玩", "开心", "快乐", "球"]
        has_keyword = any(keyword in bubble_text for keyword in play_keywords)
        assert has_keyword, f"玩耍对话应包含玩的词汇，实际：{bubble_text}"

        print(f"✅ 测试 10 通过：玩耍功能正常，对话：{bubble_text}")

    def test_love_action(self, page: Page):
        """测试 11: 爱心功能"""
        page.goto(BASE_URL)

        # 悬停显示按钮
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(300)

        # 点击爱心按钮
        love_btn = page.locator('.action-btn[data-action="love"]')
        love_btn.click()

        # 等待动画
        page.wait_for_timeout(1200)

        # 检查对话气泡
        bubble = page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()

        print("✅ 测试 11 通过：爱心功能正常")

    def test_sleep_action(self, page: Page):
        """测试 12: 睡眠功能"""
        page.goto(BASE_URL)

        # 悬停显示按钮
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(300)

        # 点击睡觉按钮
        sleep_btn = page.locator('.action-btn[data-action="sleep"]')
        sleep_btn.click()

        # 等待动画
        page.wait_for_timeout(1200)

        # 检查宠物是否进入睡眠状态
        pet_element = page.locator(".virtual-pet")
        classes = pet_element.get_attribute("class")
        assert "sleeping" in classes, "宠物应该进入睡眠状态"

        print("✅ 测试 12 通过：睡眠切换功能正常")


class TestPetStateManagement:
    """宠物状态管理测试"""

    def test_local_storage_persistence(self, page: Page):
        """测试 13: localStorage 状态持久化"""
        page.goto(BASE_URL)

        # 与宠物互动
        pet_body = page.locator(".pet-body")
        pet_body.click()
        page.wait_for_timeout(1000)

        # 检查 localStorage
        storage = page.evaluate("() => localStorage.getItem('virtualPetState')")
        assert storage is not None, "localStorage 应该保存宠物状态"

        import json

        state_data = json.loads(storage)
        assert "hunger" in state_data, "状态应包含饥饿度"
        assert "energy" in state_data, "状态应包含活力值"
        assert "affection" in state_data, "状态应包含亲密度"

        print(f"✅ 测试 13 通过：状态持久化正常，数据：{state_data}")

    def test_summon_button_appears(self, page: Page):
        """测试 14: 召唤按钮出现"""
        page.goto(BASE_URL)

        # 通过 JavaScript 触发隐藏
        page.evaluate("""
            if (window.virtualPet) {
                window.virtualPet.hide();
            }
        """)

        page.wait_for_timeout(1000)

        # 检查召唤按钮是否出现
        summon_btn = page.locator("#summon-pet-btn")
        expect(summon_btn).to_be_visible()

        # 验证按钮内容
        btn_text = summon_btn.text_content()
        assert "🐶" in btn_text, "召唤按钮应该包含🐶 emoji"

        print("✅ 测试 14 通过：召唤按钮出现")

    def test_summon_pet(self, page: Page):
        """测试 15: 召唤宠物"""
        page.goto(BASE_URL)

        # 先隐藏宠物
        page.evaluate("""
            if (window.virtualPet) {
                window.virtualPet.hide();
            }
        """)
        page.wait_for_timeout(500)

        # 点击召唤按钮
        summon_btn = page.locator("#summon-pet-btn")
        summon_btn.click()
        page.wait_for_timeout(1000)

        # 检查宠物容器重新出现
        pet_container = page.locator(".virtual-pet-container")
        expect(pet_container).to_be_visible()

        print("✅ 测试 15 通过：召唤宠物成功")


class TestPetMouseEvents:
    """宠物鼠标事件测试"""

    def test_mouse_hover_event(self, page: Page):
        """测试 16: 鼠标悬停事件"""
        page.goto(BASE_URL)

        # 鼠标悬停
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(500)

        # 检查对话气泡
        bubble = page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()

        # 验证对话内容
        bubble_text = bubble.text_content()
        assert "玩" in bubble_text, f"悬停对话应包含'玩'，实际：{bubble_text}"

        print(f"✅ 测试 16 通过：鼠标悬停事件正常，对话：{bubble_text}")

    def test_mouse_leave_event(self, page: Page):
        """测试 17: 鼠标离开事件"""
        page.goto(BASE_URL)

        # 先悬停
        pet_element = page.locator(".virtual-pet")
        pet_element.hover()
        page.wait_for_timeout(500)

        # 鼠标移开（移动到页面其他位置）
        page.mouse.move(0, 0)
        page.wait_for_timeout(500)

        # 检查对话气泡是否隐藏
        bubble = page.locator(".pet-bubble")
        # 气泡应该隐藏或不存在
        is_visible = bubble.is_visible()
        assert (
            not is_visible
            or bubble.get_attribute("class")
            and "show" not in bubble.get_attribute("class")
        ), "鼠标移开后对话气泡应该隐藏"

        print("✅ 测试 17 通过：鼠标离开事件正常")


class TestPetPerformance:
    """宠物性能测试"""

    def test_page_load_time(self, page: Page):
        """测试 18: 页面加载时间"""
        import time

        start_time = time.time()
        page.goto(BASE_URL)

        # 等待宠物容器出现
        pet_container = page.locator(".virtual-pet-container")
        expect(pet_container).to_be_visible(timeout=10000)
        end_time = time.time()

        load_time = end_time - start_time
        print(f"✅ 测试 18 通过：页面加载时间：{load_time:.2f}秒")

        # 断言：加载时间应小于 3 秒
        assert load_time < 3.0, f"加载时间过长：{load_time}秒"

    def test_interaction_response_time(self, page: Page):
        """测试 19: 交互响应时间"""
        import time

        page.goto(BASE_URL)

        # 等待宠物加载
        pet_body = page.locator(".pet-body")
        expect(pet_body).to_be_visible()

        # 测量点击响应时间
        start_time = time.time()
        pet_body.click()

        # 等待动画类出现
        page.wait_for_selector(".virtual-pet.animate-bounce", timeout=5000)
        end_time = time.time()

        response_time = end_time - start_time
        print(f"✅ 测试 19 通过：交互响应时间：{response_time*1000:.0f}毫秒")

        # 断言：响应时间应小于 500 毫秒
        assert response_time < 0.5, f"响应时间过长：{response_time*1000}毫秒"


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/pet_test_playwright_report.html",
            "--self-contained-html",
        ]
    )
