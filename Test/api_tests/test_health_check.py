"""
健康检查 API 测试
测试 /api/health 端点的功能和可靠性
"""

import pytest
from Test.test_framework import test_case, test_manager


class TestHealthCheckAPI:
    """健康检查 API 测试套件"""

    @test_case("TC-HEALTH-001", priority="Critical", expected="返回健康状态")
    def test_health_check_success(self, client):
        """测试健康检查接口正常响应"""
        response = client.get("/api/health")

        # 验证状态码
        assert response.status_code == 200

        # 验证 JSON 结构
        data = response.get_json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data

        # 验证状态值
        assert data["status"] in ["healthy", "unhealthy"]

        # 验证版本信息
        assert data["version"].startswith("v") and "." in data["version"]

        # 验证检查项（新版本包含 database 和 system）
        assert "database" in data["checks"]
        assert "system" in data["checks"]

        print(f"✅ 健康检查通过，状态: {data['status']}")

    @test_case("TC-HEALTH-002", priority="High", expected="数据库检查正常")
    def test_health_check_database_ok(self, client):
        """测试数据库连接检查正常"""
        response = client.get("/api/health")
        data = response.get_json()

        # 数据库应该正常
        assert data["checks"]["database"] == "ok"
        assert data["status"] == "healthy"

        print("✅ 数据库连接正常")

    @test_case("TC-HEALTH-003", priority="Medium", expected="时间戳格式正确")
    def test_health_check_timestamp_format(self, client):
        """测试时间戳格式符合 ISO 8601"""
        from datetime import datetime

        response = client.get("/api/health")
        data = response.get_json()

        # 验证时间戳格式
        timestamp = data["timestamp"]
        try:
            # 尝试解析 ISO 格式
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert dt is not None
        except ValueError:
            pytest.fail(f"时间戳格式错误: {timestamp}")

        print(f"✅ 时间戳格式正确: {timestamp}")

    @test_case("TC-HEALTH-004", priority="Medium", expected="无需认证")
    def test_health_check_no_auth_required(self, client):
        """测试健康检查接口无需认证（公开访问）"""
        # 未登录状态下访问
        response = client.get("/api/health")

        # 应该可以访问，不需要登录
        assert response.status_code == 200

        print("✅ 健康检查接口可公开访问")

    @test_case("TC-HEALTH-005", priority="Low", expected="响应时间短")
    def test_health_check_response_time(self, client):
        """测试健康检查接口响应时间在合理范围内"""
        import time

        start = time.time()
        response = client.get("/api/health")
        elapsed = (time.time() - start) * 1000  # 转换为毫秒

        # 响应时间应小于 500ms（考虑到数据库查询）
        assert elapsed < 500, f"响应时间过长: {elapsed}ms"
        assert response.status_code == 200

        print(f"✅ 响应时间: {elapsed:.2f}ms")

    @test_case("TC-HEALTH-006", priority="Medium", expected="Content-Type 正确")
    def test_health_check_content_type(self, client):
        """测试响应 Content-Type 为 application/json"""
        response = client.get("/api/health")

        assert "application/json" in response.content_type

        print("✅ Content-Type 正确")

    @test_case("TC-HEALTH-007", priority="Low", expected="支持 CORS（如配置）")
    def test_health_check_headers(self, client):
        """测试响应头包含必要的安全头"""
        response = client.get("/api/health")

        # 检查安全头（在 app.py 中配置）
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers

        print("✅ 安全响应头存在")

    @test_case("TC-HEALTH-008", priority="High", expected="高并发下稳定")
    def test_health_check_concurrent_requests(self, client):
        """测试健康检查在高并发下的稳定性"""
        import concurrent.futures

        def make_request(_):
            return client.get("/api/health")

        # 发送 50 个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            responses = [f.result() for f in futures]

        # 所有请求都应该成功
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 50, f"只有 {success_count}/50 个请求成功"

        print(f"✅ 并发测试通过: 50/50 请求成功")

    @test_case("TC-HEALTH-009", priority="Medium", expected="返回系统状态")
    def test_health_check_system_status(self, client):
        """测试系统状态检查"""
        response = client.get("/api/health")
        data = response.get_json()

        # 系统状态应该存在
        assert "system" in data["checks"]
        system_info = data["checks"]["system"]

        # 验证系统信息字段
        if isinstance(system_info, dict) and "status" not in system_info:
            assert "memory_usage_percent" in system_info
            assert "cpu_usage_percent" in system_info

        print("✅ 系统状态检查正常")

    @test_case("TC-HEALTH-010", priority="Low", expected="多次调用结果一致")
    def test_health_check_consistency(self, client):
        """测试多次调用结果一致性"""
        results = []

        for _ in range(5):
            response = client.get("/api/health")
            data = response.get_json()
            results.append(data["status"])

        # 所有结果应该一致
        assert all(status == results[0] for status in results), f"结果不一致: {results}"

        print(f"✅ 一致性测试通过: {results[0]}")


# 性能基准测试
@pytest.mark.performance
class TestHealthCheckPerformance:
    """健康检查性能测试"""

    def test_health_check_under_load(self, client):
        """测试健康检查在负载下的表现"""
        import statistics

        response_times = []

        # 发送 100 个请求
        for i in range(100):
            import time

            start = time.time()
            response = client.get("/api/health")
            elapsed = (time.time() - start) * 1000
            response_times.append(elapsed)

            assert response.status_code == 200

        # 统计指标
        avg_time = statistics.mean(response_times)
        p95_time = sorted(response_times)[94]  # 95 百分位
        max_time = max(response_times)

        print(f"\n📊 性能统计:")
        print(f"  平均响应时间: {avg_time:.2f}ms")
        print(f"  P95 响应时间: {p95_time:.2f}ms")
        print(f"  最大响应时间: {max_time:.2f}ms")

        # 断言：P95 应小于 200ms（考虑数据库查询开销）
        assert p95_time < 200, f"P95 响应时间超标: {p95_time}ms"
