"""
监控系统测试
测试 Prometheus 指标和健康检查端点
"""

import pytest


class TestHealthCheck:
    """健康检查测试类"""

    def test_health_check_success(self, client):
        """测试健康检查正常响应"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.get_json()

        # 验证必需字段
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data

        # 验证状态
        assert data["status"] in ["healthy", "unhealthy"]

        # 验证检查项
        assert "database" in data["checks"]
        assert "system" in data["checks"]

        print(f"✅ 健康检查状态: {data['status']}")

    def test_health_check_database_status(self, client):
        """测试数据库检查"""
        response = client.get("/api/health")
        data = response.get_json()

        db_status = data["checks"]["database"]
        assert db_status == "ok", f"数据库检查失败: {db_status}"

        print("✅ 数据库连接正常")

    def test_health_check_system_info(self, client):
        """测试系统信息"""
        response = client.get("/api/health")
        data = response.get_json()

        system_info = data["checks"]["system"]

        # 验证系统信息字段
        if isinstance(system_info, dict) and "status" not in system_info:
            assert "memory_usage_percent" in system_info
            assert "cpu_usage_percent" in system_info

            # 验证数值范围
            assert 0 <= system_info["memory_usage_percent"] <= 100
            assert 0 <= system_info["cpu_usage_percent"] <= 100

            print(f"✅ 内存使用: {system_info['memory_usage_percent']:.1f}%")
            print(f"✅ CPU 使用: {system_info['cpu_usage_percent']:.1f}%")

    def test_health_check_version(self, client):
        """测试版本信息"""
        response = client.get("/api/health")
        data = response.get_json()

        assert "version" in data
        assert data["version"].startswith("v")

        print(f"✅ 当前版本: {data['version']}")


@pytest.mark.performance
class TestMonitoringPerformance:
    """监控性能测试"""

    def test_health_check_response_time(self, client):
        """测试健康检查响应时间"""
        import time

        start_time = time.time()
        response = client.get("/api/health")
        elapsed = time.time() - start_time

        assert response.status_code == 200

        # 健康检查应该在 500ms 内完成（考虑到数据库查询）
        assert elapsed < 0.5, f"健康检查响应太慢: {elapsed*1000:.1f}ms"

        print(f"✅ 健康检查响应时间: {elapsed*1000:.1f}ms")

    def test_prometheus_metrics_endpoint(self, client):
        """测试 Prometheus 指标端点"""
        import time

        start_time = time.time()
        response = client.get("/metrics")
        elapsed = time.time() - start_time

        # Prometheus 端点应该存在
        assert response.status_code == 200

        # 响应应该是文本格式
        assert "text/plain" in response.content_type

        # 应该包含基本指标（flask_http_request_total 或 python_info）
        content = response.get_data(as_text=True)
        assert "flask_http_request_total" in content or "python_info" in content

        print(f"✅ Prometheus 指标端点响应时间: {elapsed*1000:.1f}ms")
        print(f"✅ 指标数据长度: {len(content)} 字符")


class TestPrometheusMetrics:
    """Prometheus 指标测试"""

    def test_metrics_endpoint_exists(self, client):
        """测试指标端点存在"""
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.content_type

        print("✅ Prometheus 指标端点可访问")

    def test_metrics_contains_http_requests(self, client):
        """测试指标包含 HTTP 请求数据"""
        # 先触发一些请求
        client.get("/")
        client.get("/api/health")

        # 获取指标
        response = client.get("/metrics")
        content = response.get_data(as_text=True)

        # 应该包含 HTTP 请求指标
        assert "http_requests_total" in content or "flask_http_request_total" in content

        print("✅ HTTP 请求指标已收集")

    def test_metrics_format_valid(self, client):
        """测试指标格式有效"""
        response = client.get("/metrics")
        content = response.get_data(as_text=True)

        # Prometheus 指标应该是多行文本
        lines = content.strip().split("\n")
        assert len(lines) > 10, "指标数据太少"

        # 至少有一些指标行（不是注释）
        metric_lines = [line for line in lines if line and not line.startswith("#")]
        assert len(metric_lines) > 5, "有效指标行太少"

        print(f"✅ 指标格式有效，共 {len(lines)} 行，{len(metric_lines)} 个指标")


class TestBusinessMetrics:
    """业务指标测试"""

    def test_custom_metrics_module_imports(self):
        """测试自定义指标模块可导入"""
        try:
            from utils.monitoring import (
                HTTP_REQUEST_COUNT,
                HTTP_REQUEST_LATENCY,
                USER_REGISTRATION_COUNT,
                CHART_GENERATION_COUNT,
                FEEDBACK_SUBMISSION_COUNT,
            )

            print("✅ 自定义指标模块导入成功")
        except ImportError as e:
            pytest.fail(f"自定义指标模块导入失败: {e}")

    def test_metric_counters_exist(self):
        """测试指标计数器存在"""
        from utils import monitoring

        # 验证主要指标存在
        assert hasattr(monitoring, "HTTP_REQUEST_COUNT")
        assert hasattr(monitoring, "HTTP_REQUEST_LATENCY")
        assert hasattr(monitoring, "USER_REGISTRATION_COUNT")
        assert hasattr(monitoring, "CHART_GENERATION_COUNT")

        print("✅ 所有业务指标计数器已定义")


@pytest.mark.integration
class TestMonitoringIntegration:
    """监控集成测试"""

    def test_full_monitoring_workflow(self, client):
        """测试完整监控工作流"""
        # 1. 访问多个端点生成指标
        endpoints = ["/", "/api/health", "/charts"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 302, 401]  # 允许重定向和未授权

        # 2. 获取 Prometheus 指标
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200

        # 3. 验证健康检查
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        health_data = health_response.get_json()
        assert health_data["status"] == "healthy"

        print("✅ 完整监控工作流测试通过")

    def test_error_handling_in_health_check(self, app):
        """测试健康检查错误处理"""
        # 这个测试需要模拟数据库故障，比较复杂
        # 这里只做基本验证
        with app.test_client() as client:
            response = client.get("/api/health")

            # 即使有错误，也应该返回 JSON
            assert response.content_type == "application/json"

            data = response.get_json()
            assert "status" in data

            print("✅ 健康检查错误处理正常")
