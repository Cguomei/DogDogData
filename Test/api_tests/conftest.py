"""
API 测试基础配置
提供共享的 fixtures、认证辅助函数等
"""

import pytest
import json
from routes import api


@pytest.fixture
def api_client(client):
    """提供 API 测试客户端"""
    return client


@pytest.fixture
def authenticated_api_client(logged_in_client):
    """提供已认证的 API 客户端（普通用户）"""
    return logged_in_client


@pytest.fixture
def admin_api_client(admin_client):
    """提供管理员认证的 API 客户端"""
    return admin_client


class APIResponseValidator:
    """API 响应验证工具类"""

    @staticmethod
    def assert_success(response, expected_status=200):
        """断言 API 调用成功"""
        assert (
            response.status_code == expected_status
        ), f"期望状态码 {expected_status}，实际 {response.status_code}\n响应: {response.get_data(as_text=True)}"

    @staticmethod
    def assert_error(response, expected_status=400):
        """断言 API 调用失败"""
        assert (
            response.status_code == expected_status
        ), f"期望错误状态码 {expected_status}，实际 {response.status_code}"

    @staticmethod
    def validate_breed_data(breed_data, expected_fields=None):
        """验证品种数据结构"""
        if expected_fields is None:
            expected_fields = [
                "id",
                "breed_name",
                "avg_life_years",
                "size_category",
                "popularity",
            ]

        for field in expected_fields:
            assert field in breed_data, f"品种数据缺少字段: {field}"

    @staticmethod
    def validate_chart_response(response_data):
        """验证图表生成响应"""
        assert "success" in response_data, "响应缺少 success 字段"
        assert response_data["success"] is True, "图表生成失败"
        assert "chart_html" in response_data, "响应缺少 chart_html 字段"
        assert len(response_data["chart_html"]) > 0, "图表 HTML 为空"


@pytest.fixture
def validator():
    """提供响应验证工具"""
    return APIResponseValidator()
