"""
AI助手问题修复测试
测试游客访问和删除会话功能
"""

import pytest


class TestGuestAccess:
    """游客访问测试"""

    def test_guest_can_access_ai_chat_page(self, api_client):
        """测试游客可以访问AI聊天页面"""
        response = api_client.get("/ai-chat")

        # 游客应该能访问(不重定向到登录页)
        assert response.status_code == 200

    def test_guest_can_send_message(self, api_client):
        """测试游客可以发送消息"""
        response = api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        # 游客应该能发送消息
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "session_id" in data

    def test_guest_can_view_sessions(self, api_client):
        """测试游客可以查看自己的会话列表"""
        # 先创建一个会话
        create_response = api_client.post("/api/ai/chat", json={"message": "测试消息"})

        assert create_response.status_code == 200
        session_id = create_response.get_json().get("session_id")

        # 获取会话列表
        response = api_client.get("/api/ai/sessions")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "sessions" in data


class TestDeleteSession:
    """删除会话功能测试"""

    def test_delete_session_authenticated(self, authenticated_api_client):
        """测试登录用户删除自己的会话"""
        # 先创建一个会话
        create_response = authenticated_api_client.post(
            "/api/ai/sessions", json={"title": "测试会话"}
        )

        assert create_response.status_code == 201
        session_id = create_response.get_json().get("session_id")

        # 删除会话
        delete_response = authenticated_api_client.delete(
            f"/api/ai/sessions/{session_id}"
        )

        assert delete_response.status_code == 200
        data = delete_response.get_json()
        assert data["success"] is True

        # 验证会话已删除
        get_response = authenticated_api_client.get(f"/api/ai/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_cascade_messages(self, authenticated_api_client):
        """测试删除会话时级联删除消息"""
        # 创建会话并发送消息
        chat_response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "测试消息1"}
        )

        assert chat_response.status_code == 200
        session_id = chat_response.get_json().get("session_id")

        # 再发送一条消息
        authenticated_api_client.post(
            "/api/ai/chat", json={"message": "测试消息2", "session_id": session_id}
        )

        # 删除会话
        delete_response = authenticated_api_client.delete(
            f"/api/ai/sessions/{session_id}"
        )

        assert delete_response.status_code == 200

        # 验证消息也被删除
        messages_response = authenticated_api_client.get(
            f"/api/ai/sessions/{session_id}/messages"
        )
        assert messages_response.status_code == 404

    def test_delete_session_unauthorized(self, authenticated_api_client, api_client):
        """测试不能删除别人的会话"""
        # 用户A创建会话
        create_response = authenticated_api_client.post(
            "/api/ai/sessions", json={"title": "用户A的会话"}
        )

        assert create_response.status_code == 201
        session_id = create_response.get_json().get("session_id")

        # 用户B(未登录)尝试删除
        delete_response = api_client.delete(f"/api/ai/sessions/{session_id}")

        # 应该拒绝(401或403)
        assert delete_response.status_code in [401, 403]

    def test_delete_nonexistent_session(self, authenticated_api_client):
        """测试删除不存在的会话"""
        delete_response = authenticated_api_client.delete("/api/ai/sessions/999999")

        assert delete_response.status_code == 404

    def test_guest_delete_own_session(self, api_client):
        """测试游客可以删除自己的会话"""
        # 游客创建会话
        create_response = api_client.post("/api/ai/chat", json={"message": "游客测试"})

        assert create_response.status_code == 200
        session_id = create_response.get_json().get("session_id")

        # 游客删除会话
        delete_response = api_client.delete(f"/api/ai/sessions/{session_id}")

        # 游客应该能删除自己的会话
        assert delete_response.status_code == 200
        data = delete_response.get_json()
        assert data["success"] is True
