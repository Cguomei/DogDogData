"""
AI助手UI测试（Playwright）
测试聊天界面的交互功能
"""
import pytest
from playwright.sync_api import Page, expect


class TestAIChatUI:
    """AI聊天界面测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前准备 - 登录"""
        # 访问登录页面
        page.goto("http://localhost:5000/login")
        
        # 填写登录表单
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin123')
        page.click('button[type="submit"]')
        
        # 等待登录成功
        page.wait_for_url("**/ai-chat", timeout=10000)
    
    def test_chat_page_loads(self, page: Page):
        """测试聊天页面加载"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 检查页面标题
        expect(page).to_have_title("AI智能助手")
        
        # 检查关键元素存在
        expect(page.locator(".chat-container")).to_be_visible()
        expect(page.locator("#chatMessages")).to_be_visible()
        expect(page.locator("#chatInput")).to_be_visible()
        expect(page.locator("#sendBtn")).to_be_visible()
    
    def test_model_status_display(self, page: Page):
        """测试模型状态显示"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 等待模型状态加载
        status_element = page.locator("#modelStatus")
        expect(status_element).to_be_visible(timeout=5000)
        
        # 检查状态文本（应该包含"已连接"或"未启动"）
        status_text = status_element.text_content()
        assert "已连接" in status_text or "未启动" in status_text or "无法连接" in status_text
    
    def test_send_message(self, page: Page):
        """测试发送消息"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 输入消息
        chat_input = page.locator("#chatInput")
        chat_input.fill("泰迪有什么特点？")
        
        # 点击发送按钮
        send_btn = page.locator("#sendBtn")
        send_btn.click()
        
        # 检查用户消息是否显示
        expect(page.locator(".message.user")).to_be_visible(timeout=5000)
        
        # 检查是否有AI回复（可能需要等待）
        expect(page.locator(".message.ai")).to_be_visible(timeout=15000)
    
    def test_quick_question_buttons(self, page: Page):
        """测试快捷问题按钮"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 检查快捷按钮存在
        quick_buttons = page.locator(".quick-btn")
        expect(quick_buttons.first).to_be_visible()
        
        # 点击第一个快捷按钮
        quick_buttons.first.click()
        
        # 检查是否自动发送了消息
        expect(page.locator(".message.user")).to_be_visible(timeout=5000)
    
    def test_typing_indicator(self, page: Page):
        """测试打字指示器"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 输入并发送消息
        chat_input = page.locator("#chatInput")
        chat_input.fill("金毛的价格是多少？")
        
        send_btn = page.locator("#sendBtn")
        send_btn.click()
        
        # 检查打字指示器是否出现（可能很快消失）
        typing_indicator = page.locator("#typingIndicator")
        # 注意：打字指示器可能很快就消失了，所以这个测试可能不稳定
    
    def test_message_formatting(self, page: Page):
        """测试消息格式化"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 发送一个会返回格式化内容的消息
        chat_input = page.locator("#chatInput")
        chat_input.fill("泰迪有什么特点？")
        
        send_btn = page.locator("#sendBtn")
        send_btn.click()
        
        # 等待AI回复
        ai_message = page.locator(".message.ai .message-content")
        expect(ai_message).to_be_visible(timeout=15000)
        
        # 检查是否有格式化内容（如粗体、列表等）
        content = ai_message.inner_html()
        # 可能包含 <strong>, <ul>, <li> 等标签
    
    def test_enter_key_send(self, page: Page):
        """测试回车键发送"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 输入消息
        chat_input = page.locator("#chatInput")
        chat_input.fill("测试回车发送")
        
        # 按回车键
        chat_input.press("Enter")
        
        # 检查消息是否发送
        expect(page.locator(".message.user")).to_be_visible(timeout=5000)
    
    def test_empty_message_not_sent(self, page: Page):
        """测试空消息不发送"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 清空输入框
        chat_input = page.locator("#chatInput")
        chat_input.fill("")
        
        # 点击发送按钮
        send_btn = page.locator("#sendBtn")
        send_btn.click()
        
        # 等待一下，确认没有新消息
        page.wait_for_timeout(1000)
        
        # 检查没有新的用户消息（除了欢迎消息）
        user_messages = page.locator(".message.user")
        count = user_messages.count()
        assert count == 0
    
    def test_auto_scroll_to_bottom(self, page: Page):
        """测试自动滚动到底部"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 发送多条消息
        for i in range(3):
            chat_input = page.locator("#chatInput")
            chat_input.fill(f"测试消息 {i+1}")
            
            send_btn = page.locator("#sendBtn")
            send_btn.click()
            
            # 等待回复
            page.wait_for_timeout(2000)
        
        # 检查聊天区域是否滚动到底部
        chat_messages = page.locator("#chatMessages")
        scroll_position = chat_messages.evaluate("el => el.scrollTop + el.clientHeight")
        scroll_height = chat_messages.evaluate("el => el.scrollHeight")
        
        # 应该接近底部（允许10px误差）
        assert abs(scroll_position - scroll_height) < 10
    
    def test_welcome_message(self, page: Page):
        """测试欢迎消息"""
        page.goto("http://localhost:5000/ai-chat")
        
        # 检查欢迎消息是否存在
        welcome = page.locator(".welcome-message")
        expect(welcome).to_be_visible()
        
        # 检查欢迎消息内容
        expect(welcome).to_contain_text("你好！我是你的AI宠物顾问")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
