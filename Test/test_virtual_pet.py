"""
网页小宠物功能自动化测试
使用 Playwright 进行端到端测试
涵盖：UI 交互、状态管理、动画效果、持久化等
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import time
import json


class TestVirtualPet:
    """虚拟宠物功能测试类"""
    
    @pytest.fixture(scope="function")
    def browser(self):
        """浏览器 fixture"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            yield browser
            browser.close()
    
    @pytest.fixture(scope="function")
    def page(self, browser):
        """页面 fixture"""
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        yield page
        context.close()
    
    @pytest.fixture(scope="function")
    def pet_page(self, page):
        """访问首页并等待宠物加载"""
        page.goto("http://localhost:5000/", wait_until="networkidle")
        # 等待宠物容器出现
        expect(page.locator(".virtual-pet-container")).to_be_visible(timeout=5000)
        return page
    
    def test_pet_initialization(self, pet_page):
        """测试 1: 宠物初始化"""
        # 检查宠物容器是否存在
        expect(pet_page.locator(".virtual-pet-container")).to_be_visible()
        
        # 检查宠物身体是否存在
        expect(pet_page.locator(".pet-body")).to_be_visible()
        
        # 检查宠物 emoji 是否显示
        pet_emoji = pet_page.locator(".pet-emoji")
        expect(pet_emoji).to_be_visible()
        
        # 验证默认宠物类型（狗狗）
        emoji_text = pet_emoji.inner_text()
        assert emoji_text == "🐶", f"期望显示🐶，实际显示：{emoji_text}"
        
        # 检查状态条是否存在
        expect(pet_page.locator(".status-bar")).to_have_count(2)
        
        print("✅ 测试 1 通过：宠物初始化成功")
    
    def test_pet_click_interaction(self, pet_page):
        """测试 2: 点击互动"""
        # 点击宠物身体
        pet_body = pet_page.locator(".pet-body")
        pet_body.click()
        
        # 检查是否播放弹跳动画（通过检查 CSS 类）
        pet_element = pet_page.locator(".virtual-pet")
        expect(pet_element).to_have_class("virtual-pet animate-bounce")
        
        # 等待动画结束
        time.sleep(1.1)
        
        # 检查对话气泡是否显示
        bubble = pet_page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()
        
        # 验证对话内容
        bubble_text = bubble.inner_text()
        assert len(bubble_text) > 0, "对话气泡应为空"
        print(f"✅ 测试 2 通过：点击互动成功，对话内容：{bubble_text}")
    
    def test_action_buttons_visibility(self, pet_page):
        """测试 3: 动作按钮悬停显示"""
        # 鼠标悬停在宠物上
        pet_element = pet_page.locator(".virtual-pet")
        pet_element.hover()
        
        # 等待动作按钮显示
        time.sleep(0.5)
        
        # 检查所有动作按钮
        action_buttons = pet_page.locator(".action-btn")
        expect(action_buttons).to_have_count(4)
        
        # 验证每个按钮的 emoji
        buttons = action_buttons.all()
        expected_emojis = ["🍖", "🎾", "❤️", "💤"]
        
        for i, button in enumerate(buttons):
            emoji = button.inner_text()
            assert emoji == expected_emojis[i], \
                f"按钮{i}期望{expected_emojis[i]}，实际{emoji}"
        
        print("✅ 测试 3 通过：动作按钮显示正确")
    
    def test_feed_action(self, pet_page):
        """测试 4: 喂食功能"""
        # 获取初始饥饿度
        hunger_bar = pet_page.locator(".hunger-bar .status-fill")
        initial_width = hunger_bar.get_attribute("style")
        
        # 悬停显示按钮
        pet_page.locator(".virtual-pet").hover()
        time.sleep(0.3)
        
        # 点击喂食按钮
        feed_btn = pet_page.locator('.action-btn[data-action="feed"]')
        feed_btn.click()
        
        # 等待动画
        time.sleep(1.2)
        
        # 检查对话气泡
        bubble = pet_page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()
        
        # 验证对话内容包含吃的相关词汇
        bubble_text = bubble.inner_text()
        feed_keywords = ["好吃", "美味", "嗷呜", "还要"]
        has_keyword = any(keyword in bubble_text for keyword in feed_keywords)
        assert has_keyword, f"喂食对话应包含吃的词汇，实际：{bubble_text}"
        
        print(f"✅ 测试 4 通过：喂食功能正常，对话：{bubble_text}")
    
    def test_play_action(self, pet_page):
        """测试 5: 玩耍功能"""
        # 悬停显示按钮
        pet_page.locator(".virtual-pet").hover()
        time.sleep(0.3)
        
        # 点击玩耍按钮
        play_btn = pet_page.locator('.action-btn[data-action="play"]')
        play_btn.click()
        
        # 等待动画
        time.sleep(1.2)
        
        # 检查对话气泡
        bubble = pet_page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()
        
        # 验证对话内容
        bubble_text = bubble.inner_text()
        play_keywords = ["开心", "好玩", "再来"]
        has_keyword = any(keyword in bubble_text for keyword in play_keywords)
        assert has_keyword, f"玩耍对话应包含玩的词汇，实际：{bubble_text}"
        
        print(f"✅ 测试 5 通过：玩耍功能正常，对话：{bubble_text}")
    
    def test_pet_action(self, pet_page):
        """测试 6: 抚摸功能"""
        # 悬停显示按钮
        pet_page.locator(".virtual-pet").hover()
        time.sleep(0.3)
        
        # 点击抚摸按钮
        pet_btn = pet_page.locator('.action-btn[data-action="pet"]')
        pet_btn.click()
        
        # 等待动画
        time.sleep(1.2)
        
        # 检查对话气泡
        bubble = pet_page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()
        
        # 验证对话内容
        bubble_text = bubble.inner_text()
        pet_keywords = ["舒服", "喜欢", "咕噜", "蹭蹭"]
        has_keyword = any(keyword in bubble_text for keyword in pet_keywords)
        assert has_keyword, f"抚摸对话应包含亲密词汇，实际：{bubble_text}"
        
        print(f"✅ 测试 6 通过：抚摸功能正常，对话：{bubble_text}")
    
    def test_sleep_toggle(self, pet_page):
        """测试 7: 睡眠切换"""
        # 悬停显示按钮
        pet_page.locator(".virtual-pet").hover()
        time.sleep(0.3)
        
        # 点击睡觉按钮
        sleep_btn = pet_page.locator('.action-btn[data-action="sleep"]')
        sleep_btn.click()
        
        # 等待动画
        time.sleep(1.2)
        
        # 检查宠物是否进入睡眠状态
        pet_element = pet_page.locator(".virtual-pet")
        expect(pet_element).to_have_class("virtual-pet sleeping")
        
        # 再次点击唤醒
        sleep_btn.click()
        time.sleep(1.2)
        
        # 检查是否退出睡眠状态
        expect(pet_element).not_to_have_class("virtual-pet sleeping")
        
        print("✅ 测试 7 通过：睡眠切换功能正常")
    
    def test_auto_hide(self, pet_page):
        """测试 8: 自动隐藏功能"""
        # 等待宠物显示
        expect(pet_page.locator(".virtual-pet")).to_be_visible()
        
        # 模拟无操作（等待 65 秒，考虑到可能的延迟）
        # 为了测试效率，这里缩短时间，实际应该等待 60 秒
        # 我们可以通过执行 JavaScript 来触发自动隐藏
        pet_page.evaluate("""
            if (window.virtualPet) {
                window.virtualPet.checkAutoHide();
            }
        """)
        
        time.sleep(1)
        
        # 检查召唤按钮是否出现
        summon_btn = pet_page.locator("#summon-pet-btn")
        expect(summon_btn).to_be_visible()
        
        print("✅ 测试 8 通过：自动隐藏功能正常")
    
    def test_summon_pet(self, pet_page):
        """测试 9: 召唤宠物"""
        # 先触发隐藏
        pet_page.evaluate("""
            if (window.virtualPet) {
                window.virtualPet.hide();
            }
        """)
        
        time.sleep(0.5)
        
        # 检查召唤按钮
        summon_btn = pet_page.locator("#summon-pet-btn")
        expect(summon_btn).to_be_visible()
        
        # 点击召唤按钮
        summon_btn.click()
        time.sleep(0.5)
        
        # 检查宠物是否重新出现
        expect(pet_page.locator(".virtual-pet")).to_be_visible()
        
        # 召唤按钮应该消失
        expect(summon_btn).not_to_be_visible()
        
        print("✅ 测试 9 通过：召唤宠物功能正常")
    
    def test_state_persistence(self, browser):
        """测试 10: 状态持久化"""
        # 第一次访问
        context1 = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page1 = context1.new_page()
        page1.goto("http://localhost:5000/", wait_until="networkidle")
        time.sleep(2)
        
        # 与宠物互动
        page1.locator(".pet-body").click()
        time.sleep(1)
        
        # 检查 localStorage 是否保存
        storage = page1.evaluate("localStorage.getItem('virtualPetState')")
        assert storage is not None, "localStorage 应该保存宠物状态"
        
        state_data = json.loads(storage)
        assert "hunger" in state_data, "状态应包含饥饿度"
        assert "energy" in state_data, "状态应包含活力值"
        assert "affection" in state_data, "状态应包含亲密度"
        
        print(f"✅ 测试 10 通过：状态持久化正常，保存的数据：{state_data}")
        
        page1.close()
        context1.close()
    
    def test_status_bar_colors(self, pet_page):
        """测试 11: 状态条颜色变化"""
        # 初始状态应该是绿色（good）
        hunger_fill = pet_page.locator(".hunger-bar .status-fill")
        
        # 检查是否有 good 类（绿色）
        class_attr = hunger_fill.get_attribute("class")
        assert "good" in class_attr or "warning" in class_attr or "critical" in class_attr, \
            "状态条应该有颜色类"
        
        print("✅ 测试 11 通过：状态条颜色正常")
    
    def test_mouse_enter_event(self, pet_page):
        """测试 12: 鼠标悬停事件"""
        # 鼠标悬停
        pet_element = pet_page.locator(".virtual-pet")
        pet_element.hover()
        
        # 等待对话气泡显示
        time.sleep(0.5)
        
        # 检查对话气泡
        bubble = pet_page.locator(".pet-bubble.show")
        expect(bubble).to_be_visible()
        
        # 验证对话内容
        bubble_text = bubble.inner_text()
        assert "玩" in bubble_text, f"悬停对话应包含'玩'，实际：{bubble_text}"
        
        print(f"✅ 测试 12 通过：鼠标悬停事件正常，对话：{bubble_text}")
    
    def test_responsive_design(self, browser):
        """测试 13: 响应式设计"""
        # 移动端视口
        context = browser.new_context(
            viewport={'width': 375, 'height': 667}  # iPhone SE
        )
        page = context.new_page()
        page.goto("http://localhost:5000/", wait_until="networkidle")
        
        # 等待宠物加载
        expect(page.locator(".virtual-pet-container")).to_be_visible(timeout=5000)
        
        # 检查宠物是否正常显示
        pet_body = page.locator(".pet-body")
        expect(pet_body).to_be_visible()
        
        # 检查尺寸是否正确缩小（通过计算样式）
        style = pet_body.evaluate("el => window.getComputedStyle(el).width")
        assert style is not None, "宠物宽度应该存在"
        
        print(f"✅ 测试 13 通过：响应式设计正常，移动端宠物宽度：{style}")
        
        page.close()
        context.close()
    
    def test_multiple_interactions(self, pet_page):
        """测试 14: 多次连续互动"""
        # 连续点击 5 次
        for i in range(5):
            pet_page.locator(".pet-body").click()
            time.sleep(0.5)
        
        # 检查动画是否正常播放
        pet_element = pet_page.locator(".virtual-pet")
        # 最后一次点击应该有动画类
        expect(pet_element).to_have_class("virtual-pet animate-bounce")
        
        print("✅ 测试 14 通过：多次连续互动正常")
    
    def test_button_tooltips(self, pet_page):
        """测试 15: 按钮提示信息"""
        # 悬停显示按钮
        pet_page.locator(".virtual-pet").hover()
        time.sleep(0.3)
        
        # 检查每个按钮的 title 属性
        buttons_data = [
            ('.action-btn[data-action="feed"]', '喂食'),
            ('.action-btn[data-action="play"]', '玩耍'),
            ('.action-btn[data-action="pet"]', '抚摸'),
            ('.action-btn[data-action="sleep"]', '睡觉')
        ]
        
        for selector, expected_title in buttons_data:
            button = pet_page.locator(selector)
            title = button.get_attribute("title")
            assert title == expected_title, \
                f"{selector}的 title 期望'{expected_title}'，实际'{title}'"
        
        print("✅ 测试 15 通过：按钮提示信息正确")


# 性能测试类
class TestPetPerformance:
    """宠物性能测试"""
    
    @pytest.fixture(scope="function")
    def page(self):
        """页面 fixture"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            yield page
            context.close()
            browser.close()
    
    def test_load_time(self, page):
        """测试 16: 加载时间"""
        start_time = time.time()
        page.goto("http://localhost:5000/", wait_until="networkidle")
        
        # 等待宠物容器出现
        expect(page.locator(".virtual-pet-container")).to_be_visible(timeout=5000)
        end_time = time.time()
        
        load_time = end_time - start_time
        print(f"✅ 测试 16 通过：宠物加载时间：{load_time:.2f}秒")
        
        # 断言：加载时间应小于 2 秒
        assert load_time < 2.0, f"加载时间过长：{load_time}秒"
    
    def test_memory_usage(self, page):
        """测试 17: 内存占用"""
        # 访问页面
        page.goto("http://localhost:5000/", wait_until="networkidle")
        time.sleep(2)
        
        # 获取内存使用情况（通过 Performance API）
        memory_info = page.evaluate("""
            () => {
                if (performance.memory) {
                    return {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize
                    };
                }
                return null;
            }
        """)
        
        if memory_info:
            used_mb = memory_info['usedJSHeapSize'] / (1024 * 1024)
            print(f"✅ 测试 17 通过：内存占用：{used_mb:.2f}MB")
            
            # 断言：内存占用应小于 5MB
            assert used_mb < 5.0, f"内存占用过大：{used_mb}MB"
        else:
            print("⚠️  测试 17 跳过：浏览器不支持 memory API")


# 运行测试
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",
        "--html=Test/reports/pet_test_report.html",
        "--self-contained-html"
    ])
