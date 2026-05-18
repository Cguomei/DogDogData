"""
智能预警系统API测试
"""

import pytest


class TestPriceAlert:
    """价格预警测试"""

    def test_create_price_alert(self, authenticated_api_client):
        """测试创建价格预警"""
        response = authenticated_api_client.post(
            "/api/alerts/price",
            json={
                "breed_name": "金毛",
                "target_price": 3000,
                "condition": "below",
                "notify_email": True,
                "notify_in_app": True,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["breed_name"] == "金毛"
        assert data["data"]["target_price"] == 3000

    def test_get_price_alerts(self, authenticated_api_client):
        """测试获取价格预警列表"""
        # 先创建一个
        authenticated_api_client.post(
            "/api/alerts/price",
            json={"breed_name": "哈士奇", "target_price": 5000, "condition": "above"},
        )

        # 获取列表
        response = authenticated_api_client.get("/api/alerts/price")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_update_price_alert(self, authenticated_api_client):
        """测试更新价格预警"""
        # 先创建
        create_resp = authenticated_api_client.post(
            "/api/alerts/price",
            json={"breed_name": "柯基", "target_price": 2000, "condition": "below"},
        )
        alert_id = create_resp.get_json()["data"]["id"]

        # 更新
        response = authenticated_api_client.put(
            f"/api/alerts/price/{alert_id}", json={"target_price": 2500}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["target_price"] == 2500

    def test_delete_price_alert(self, authenticated_api_client):
        """测试删除价格预警"""
        # 先创建
        create_resp = authenticated_api_client.post(
            "/api/alerts/price",
            json={"breed_name": "泰迪", "target_price": 1500, "condition": "below"},
        )
        alert_id = create_resp.get_json()["data"]["id"]

        # 删除
        response = authenticated_api_client.delete(f"/api/alerts/price/{alert_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


class TestBreedAlert:
    """品种提醒测试"""

    def test_create_breed_alert(self, authenticated_api_client):
        """测试创建品种提醒"""
        response = authenticated_api_client.post(
            "/api/alerts/breed",
            json={
                "alert_type": "new_breed",
                "filters": {"sizes": ["small"]},
                "notify_email": True,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["alert_type"] == "new_breed"

    def test_get_breed_alerts(self, authenticated_api_client):
        """测试获取品种提醒列表"""
        response = authenticated_api_client.get("/api/alerts/breed")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data


class TestNotifications:
    """通知管理测试"""

    def test_get_notifications(self, authenticated_api_client):
        """测试获取通知列表"""
        response = authenticated_api_client.get("/api/alerts/notifications")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data

    def test_get_unread_count(self, authenticated_api_client):
        """测试获取未读数量"""
        response = authenticated_api_client.get(
            "/api/alerts/notifications/unread-count"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "unread_count" in data["data"]

    def test_mark_all_read(self, authenticated_api_client):
        """测试标记所有为已读"""
        response = authenticated_api_client.post("/api/alerts/notifications/read-all")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


class TestAlertAuth:
    """预警系统权限测试"""

    def test_price_alert_requires_auth(self, api_client):
        """测试价格预警需要认证"""
        response = api_client.post("/api/alerts/price", json={})
        assert response.status_code in [401, 302]

    def test_breed_alert_requires_auth(self, api_client):
        """测试品种提醒需要认证"""
        response = api_client.get("/api/alerts/breed")
        assert response.status_code in [401, 302]
