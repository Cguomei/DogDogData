"""
AI智能助手API测试
测试AI助手的核心功能
"""
import pytest
import json


class TestAIAssistant:
    """AI助手API测试类"""
    
    def test_model_status_authenticated(self, authenticated_api_client):
        """测试模型状态检查（已登录）"""
        response = authenticated_api_client.get('/api/ai/model/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'type' in data
        assert 'url' in data
    
    def test_model_status_unauthenticated(self, api_client):
        """测试模型状态检查（未登录）"""
        response = api_client.get('/api/ai/model/status')
        
        # 应该重定向到登录页
        assert response.status_code in [302, 401]
    
    def test_chat_price_query(self, authenticated_api_client):
        """测试价格查询"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': '金毛的价格是多少？'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'answer' in data
        assert 'type' in data
        assert data['type'] == 'price_query'
    
    def test_chat_breed_info(self, authenticated_api_client):
        """测试品种信息查询"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': '泰迪有什么特点？'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['type'] == 'breed_info'
    
    def test_chat_recommendation(self, authenticated_api_client):
        """测试推荐功能"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': '适合新手养的狗狗'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['type'] == 'recommendation'
    
    def test_chat_comparison(self, authenticated_api_client):
        """测试对比功能"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': '金毛和泰迪对比'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['type'] == 'comparison'
    
    def test_chat_general_qa(self, authenticated_api_client):
        """测试通用问答"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': '怎么训练狗狗定点排便？'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['type'] == 'general_qa'
    
    def test_chat_empty_message(self, authenticated_api_client):
        """测试空消息"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': ''}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_chat_missing_message(self, authenticated_api_client):
        """测试缺少消息字段"""
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_chat_message_too_long(self, authenticated_api_client):
        """测试消息过长"""
        long_message = "测试" * 501  # 超过1000字符
        
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={'message': long_message}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_chat_unauthenticated(self, api_client):
        """测试未登录访问"""
        response = api_client.post(
            '/api/ai/chat',
            json={'message': '测试'}
        )
        
        # 应该重定向到登录页
        assert response.status_code in [302, 401]
    
    def test_chat_page_authenticated(self, authenticated_api_client):
        """测试聊天页面访问（已登录）"""
        response = authenticated_api_client.get('/ai-chat')
        
        assert response.status_code == 200
        assert b'ai-chat' in response.data or b'AI' in response.data
    
    def test_chat_page_unauthenticated(self, api_client):
        """测试聊天页面访问（未登录）"""
        response = api_client.get('/ai-chat')
        
        # 应该重定向到登录页
        assert response.status_code in [302, 401]
    
    def test_logs_page_admin(self, admin_api_client):
        """测试日志查看页面（管理员）"""
        response = admin_api_client.get('/ai-logs')
        
        # 如果是admin用户，应该能访问
        # 注意：需要根据实际用户角色调整
        assert response.status_code in [200, 403]
    
    def test_logs_api_recent(self, admin_api_client):
        """测试获取最近日志API"""
        response = admin_api_client.get('/api/ai/logs/recent?lines=10')
        
        # 需要管理员权限
        assert response.status_code in [200, 403]
    
    def test_logs_api_errors(self, admin_api_client):
        """测试获取错误日志API"""
        response = admin_api_client.get('/api/ai/logs/errors')
        
        # 需要管理员权限
        assert response.status_code in [200, 403]


class TestQuestionClassifier:
    """问题分类器测试"""
    
    def test_classify_price_query(self):
        """测试价格查询分类"""
        from routes.ai_assistant import classify_question
        
        result = classify_question("金毛多少钱？")
        assert result['type'] == 'price_query'
        assert result['params']['breed'] == '金毛'
    
    def test_classify_breed_info(self):
        """测试品种信息查询分类"""
        from routes.ai_assistant import classify_question
        
        result = classify_question("泰迪的特点是什么？")
        assert result['type'] == 'breed_info'
    
    def test_classify_recommendation(self):
        """测试推荐分类"""
        from routes.ai_assistant import classify_question
        
        result = classify_question("适合新手的狗狗")
        assert result['type'] == 'recommendation'
    
    def test_classify_comparison(self):
        """测试对比分类"""
        from routes.ai_assistant import classify_question
        
        result = classify_question("金毛和泰迪哪个更好")
        assert result['type'] == 'comparison'
    
    def test_extract_breed_name(self):
        """测试品种名称提取"""
        from routes.ai_assistant import extract_breed_name
        
        assert extract_breed_name("金毛的价格") == "金毛"
        assert extract_breed_name("我想了解泰迪") == "泰迪"
    
    def test_extract_multiple_breeds(self):
        """测试多个品种提取"""
        from routes.ai_assistant import extract_multiple_breeds
        
        breeds = extract_multiple_breeds("金毛和泰迪对比")
        assert len(breeds) >= 2
        assert '金毛' in breeds
        assert '泰迪' in breeds


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
