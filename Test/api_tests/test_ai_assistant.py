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


class TestSessionManagement:
    """会话管理测试（V2新功能）"""
    
    def test_create_session(self, authenticated_api_client):
        """测试创建会话"""
        response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '测试会话'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'session_id' in data
        assert 'title' in data
        return data['session_id']
    
    def test_get_sessions(self, authenticated_api_client):
        """测试获取会话列表"""
        # 先创建一个会话
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '测试会话1'}
        )
        
        # 获取列表
        response = authenticated_api_client.get('/api/ai/sessions')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'sessions' in data
        assert len(data['sessions']) > 0
    
    def test_get_session_detail(self, authenticated_api_client):
        """测试获取会话详情"""
        # 先创建会话
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '测试会话详情'}
        )
        session_id = create_response.get_json()['session_id']
        
        # 获取详情
        response = authenticated_api_client.get(f'/api/ai/sessions/{session_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'session' in data
    
    def test_chat_with_session(self, authenticated_api_client):
        """测试带会话ID的聊天"""
        # 创建会话
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '聊天测试会话'}
        )
        session_id = create_response.get_json()['session_id']
        
        # 发送消息
        response = authenticated_api_client.post(
            '/api/ai/chat',
            json={
                'message': '泰迪有什么特点？',
                'session_id': session_id
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['session_id'] == session_id
        assert 'message_id' in data  # V2新增
    
    def test_get_messages(self, authenticated_api_client):
        """测试获取消息历史"""
        # 创建会话并发送消息
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '消息历史测试'}
        )
        session_id = create_response.get_json()['session_id']
        
        authenticated_api_client.post(
            '/api/ai/chat',
            json={
                'message': '测试消息',
                'session_id': session_id
            }
        )
        
        # 获取消息历史
        response = authenticated_api_client.get(f'/api/ai/sessions/{session_id}/messages')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'messages' in data
        assert data['message_count'] > 0
    
    def test_delete_session(self, authenticated_api_client):
        """测试删除会话"""
        # 创建会话
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '待删除会话'}
        )
        session_id = create_response.get_json()['session_id']
        
        # 删除会话
        response = authenticated_api_client.delete(f'/api/ai/sessions/{session_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


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


class TestFeedbackSystem:
    """用户反馈系统测试（V2新功能）"""
    
    def test_submit_like_feedback(self, authenticated_api_client):
        """测试点赞反馈"""
        # 先创建会话并发送消息
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '反馈测试'}
        )
        session_id = create_response.get_json()['session_id']
        
        chat_response = authenticated_api_client.post(
            '/api/ai/chat',
            json={
                'message': '测试问题',
                'session_id': session_id
            }
        )
        message_id = chat_response.get_json()['message_id']
        
        # 提交点赞反馈
        response = authenticated_api_client.post(
            '/api/ai/feedback',
            json={
                'message_id': message_id,
                'feedback': 'like'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_submit_dislike_feedback(self, authenticated_api_client):
        """测试点踩反馈"""
        # 先创建会话并发送消息
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '反馈测试2'}
        )
        session_id = create_response.get_json()['session_id']
        
        chat_response = authenticated_api_client.post(
            '/api/ai/chat',
            json={
                'message': '测试问题2',
                'session_id': session_id
            }
        )
        message_id = chat_response.get_json()['message_id']
        
        # 提交点踩反馈
        response = authenticated_api_client.post(
            '/api/ai/feedback',
            json={
                'message_id': message_id,
                'feedback': 'dislike',
                'comment': '回答不够详细'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_submit_feedback_invalid_type(self, authenticated_api_client):
        """测试无效反馈类型"""
        response = authenticated_api_client.post(
            '/api/ai/feedback',
            json={
                'message_id': 1,
                'feedback': 'invalid'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_submit_feedback_missing_fields(self, authenticated_api_client):
        """测试缺少必要字段"""
        response = authenticated_api_client.post(
            '/api/ai/feedback',
            json={
                'message_id': 1
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestAutoLearning:
    """自动学习功能测试（V2新功能）"""
    
    def test_manual_learn(self, authenticated_api_client):
        """测试手动学习"""
        response = authenticated_api_client.post(
            '/api/ai/learn',
            json={
                'question': '柯基的特点是什么？',
                'answer': '柯基是一种小型犬，腿短身长，性格活泼。',
                'category': 'breed_info'
            }
        )
        
        # 可能成功或失败（如果已存在）
        assert response.status_code in [200, 400]
        data = response.get_json()
        assert 'success' in data
    
    def test_manual_learn_missing_fields(self, authenticated_api_client):
        """测试手动学习缺少字段"""
        response = authenticated_api_client.post(
            '/api/ai/learn',
            json={
                'question': '测试问题'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestReportGeneration:
    """报告生成功能测试（P1新功能）"""
    
    def test_get_session_report(self, authenticated_api_client):
        """测试获取会话总结报告"""
        # 先创建一个会话
        create_response = authenticated_api_client.post(
            '/api/ai/sessions',
            json={'title': '测试会话'}
        )
        session_id = create_response.get_json()['session_id']
        
        # 发送一条消息
        chat_response = authenticated_api_client.post(
            '/api/ai/chat',
            json={
                'message': '金毛的价格是多少？',
                'session_id': session_id
            }
        )
        
        # 检查聊天是否成功
        assert chat_response.status_code == 200
        
        # 获取报告
        response = authenticated_api_client.get(f'/api/ai/report/session/{session_id}')
        
        # 应该返回200或400（如果没有消息）
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert 'total_messages' in data['data']
    
    def test_get_session_report_unauthorized(self, authenticated_api_client):
        """测试无权访问的会话报告"""
        # 尝试访问不存在的会话
        response = authenticated_api_client.get('/api/ai/report/session/999999')
        
        assert response.status_code in [403, 404]
    
    def test_get_purchase_report(self, authenticated_api_client):
        """测试获取选购建议报告"""
        response = authenticated_api_client.post(
            '/api/ai/report/purchase',
            json={
                'budget': 5000,
                'size': 'medium',
                'experience': 'beginner',
                'purpose': 'companion'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'html' in data
        # HTML可能包含成功信息或未找到提示
        assert ('宠物选购建议报告' in data['html'] or '抱歉' in data['html'])
    
    def test_get_purchase_report_missing_data(self, authenticated_api_client):
        """测试选购建议缺少数据"""
        response = authenticated_api_client.post(
            '/api/ai/report/purchase',
            json={}
        )
        
        # 应该返回空或默认结果，或者返回400错误
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.get_json()
            assert data['success'] is True
    
    def test_get_analysis_report(self, authenticated_api_client):
        """测试获取数据分析报告"""
        response = authenticated_api_client.get('/api/ai/report/analysis?time_range=30days')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'html' in data
        assert '数据分析报告' in data['html']
        assert '热门品种' in data['html']
    
    def test_get_analysis_report_7days(self, authenticated_api_client):
        """测试7天数据分析报告"""
        response = authenticated_api_client.get('/api/ai/report/analysis?time_range=7days')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'html' in data
    
    def test_get_analysis_report_90days(self, authenticated_api_client):
        """测试90天数据分析报告"""
        response = authenticated_api_client.get('/api/ai/report/analysis?time_range=90days')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'html' in data
    
    def test_get_analysis_report_unauthenticated(self, api_client):
        """测试未登录访问分析报告"""
        response = api_client.get('/api/ai/report/analysis')
        
        assert response.status_code in [302, 401]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
