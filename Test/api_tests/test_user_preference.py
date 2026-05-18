"""
用户偏好系统API测试
"""

import pytest


class TestUserPreference:
    """用户偏好系统测试（P1新功能）"""

    def test_get_preferences_default(self, authenticated_api_client):
        """测试默认偏好设置结构"""
        # 先设置为已知值，再验证返回结构完整
        authenticated_api_client.post(
            "/api/user/preferences",
            json={
                "preferred_size": "all",
                "experience_level": "beginner",
                "auto_save_chat": True,
            },
        )
        response = authenticated_api_client.get("/api/user/preferences")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        # 验证返回的值与设置的一致
        assert data["data"]["preferred_size"] == "all"
        assert data["data"]["experience_level"] == "beginner"
        assert data["data"]["auto_save_chat"] is True

    def test_update_preferences(self, authenticated_api_client):
        """测试更新偏好设置"""
        response = authenticated_api_client.post(
            "/api/user/preferences",
            json={
                "preferred_breeds": ["金毛", "哈士奇"],
                "preferred_size": "large",
                "budget_range": "3000-8000",
                "experience_level": "intermediate",
                "purpose": "companion",
                "response_style": "detailed",
                "price_alert_enabled": True,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "偏好设置已保存"
        assert data["data"]["preferred_size"] == "large"
        assert data["data"]["budget_range"] == "3000-8000"

    def test_update_preferences_invalid_size(self, authenticated_api_client):
        """测试更新偏好设置 - 无效体型"""
        response = authenticated_api_client.post(
            "/api/user/preferences", json={"preferred_size": "invalid"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_preferences_invalid_experience(self, authenticated_api_client):
        """测试更新偏好设置 - 无效经验等级"""
        response = authenticated_api_client.post(
            "/api/user/preferences", json={"experience_level": "expert"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_preferences_after_update(self, authenticated_api_client):
        """测试更新后获取偏好设置"""
        # 先更新
        authenticated_api_client.post(
            "/api/user/preferences",
            json={
                "preferred_size": "medium",
                "budget_range": "0-3000",
                "experience_level": "advanced",
            },
        )

        # 再获取
        response = authenticated_api_client.get("/api/user/preferences")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["preferred_size"] == "medium"
        assert data["data"]["budget_range"] == "0-3000"
        assert data["data"]["experience_level"] == "advanced"

    def test_get_personalized_recommendations(self, authenticated_api_client):
        """测试获取个性化推荐"""
        # 先设置偏好
        authenticated_api_client.post(
            "/api/user/preferences",
            json={"preferred_size": "medium", "budget_range": "3000-8000"},
        )

        # 获取推荐
        response = authenticated_api_client.get("/api/user/preferences/recommendations")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        # 可能返回空列表或推荐列表
        assert isinstance(data["data"], list)

    def test_get_preference_stats(self, authenticated_api_client):
        """测试获取偏好统计信息"""
        response = authenticated_api_client.get("/api/user/preferences/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert "favorite_count" in data["data"]
        assert "has_preference" in data["data"]
        assert "session_count" in data["data"]

    def test_update_partial_preferences(self, authenticated_api_client):
        """测试部分更新偏好设置"""
        # 先设置完整偏好
        authenticated_api_client.post(
            "/api/user/preferences",
            json={
                "preferred_size": "small",
                "budget_range": "0-3000",
                "experience_level": "beginner",
            },
        )

        # 只更新一个字段
        response = authenticated_api_client.post(
            "/api/user/preferences", json={"preferred_size": "large"}
        )

        assert response.status_code == 200

        # 验证其他字段保持不变
        get_response = authenticated_api_client.get("/api/user/preferences")
        data = get_response.get_json()
        assert data["data"]["preferred_size"] == "large"
        assert data["data"]["budget_range"] == "0-3000"  # 应该保持不变

    def test_preferences_require_authentication(self, api_client):
        """测试偏好接口需要认证"""
        response = api_client.get("/api/user/preferences")
        assert response.status_code == 401 or response.status_code == 302

        response = api_client.post("/api/user/preferences", json={})
        assert response.status_code == 401 or response.status_code == 302
