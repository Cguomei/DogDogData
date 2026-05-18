"""
用户反馈 API 测试
测试反馈提交、查询、管理等功能
"""

import pytest
from Test.test_framework import test_case


class TestFeedbackAPI:
    """用户反馈 API 测试套件"""

    @test_case("TC-FEEDBACK-001", priority="High", expected="提交反馈成功")
    def test_submit_feedback_success(self, client, create_test_users):
        """测试提交反馈成功"""
        # 登录用户
        response = client.post(
            "/login",
            data={"username": "user", "password": "123456"},
            follow_redirects=True,
        )

        # 验证登录成功
        assert response.status_code == 200

        # 提交反馈
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "title": "测试反馈标题",
                "content": "这是一个测试反馈内容，用于验证反馈功能。",
                "priority": "medium",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] == True
        assert "message" in data
        assert "feedback_id" in data

        print(f"✅ 反馈提交成功，ID: {data['feedback_id']}")

    @test_case("TC-FEEDBACK-002", priority="High", expected="获取反馈列表")
    def test_get_feedback_list(self, client, create_test_users):
        """测试获取反馈列表"""
        # 提交一个反馈
        client.post("/login", data={"username": "user", "password": "123456"})

        client.post(
            "/api/feedback",
            json={"feedback_type": "bug", "title": "测试反馈", "content": "测试内容"},
        )

        # 获取列表
        response = client.get("/api/feedback")
        assert response.status_code == 200

        data = response.get_json()
        assert "feedbacks" in data
        assert len(data["feedbacks"]) >= 1

        print(f"✅ 反馈列表获取成功，共 {len(data['feedbacks'])} 条")

    @test_case("TC-FEEDBACK-003", priority="Critical", expected="反馈类型验证")
    def test_feedback_type_validation(self, client, create_test_users):
        """测试反馈类型验证"""
        client.post("/login", data={"username": "user", "password": "123456"})

        valid_types = ["bug", "feature", "improvement", "other"]
        for feedback_type in valid_types:
            response = client.post(
                "/api/feedback",
                json={
                    "feedback_type": feedback_type,
                    "content": f"测试{feedback_type}类型反馈",
                },
            )
            assert response.status_code == 201, f"类型 {feedback_type} 应该有效"

        # 测试无效类型
        response = client.post(
            "/api/feedback",
            json={"feedback_type": "invalid_type", "content": "测试无效类型"},
        )
        assert response.status_code == 400

        print("✅ 反馈类型验证正常")

    @test_case("TC-FEEDBACK-004", priority="High", expected="内容验证")
    def test_feedback_content_validation(self, client, create_test_users):
        """测试反馈内容验证"""
        client.post("/login", data={"username": "user", "password": "123456"})

        # 测试空内容
        response = client.post(
            "/api/feedback", json={"feedback_type": "bug", "content": ""}
        )
        assert response.status_code == 400

        # 测试正常内容
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "content": "这是一个有效的反馈内容，包含足够的字符数。",
            },
        )
        assert response.status_code == 201

        print("✅ 反馈内容验证正常")

    @test_case("TC-FEEDBACK-005", priority="Medium", expected="优先级验证")
    def test_feedback_priority_validation(self, client, create_test_users):
        """测试反馈优先级验证"""
        client.post("/login", data={"username": "user", "password": "123456"})

        valid_priorities = ["low", "medium", "high", "critical"]
        for priority in valid_priorities:
            response = client.post(
                "/api/feedback",
                json={
                    "feedback_type": "bug",
                    "content": f"测试{priority}优先级",
                    "priority": priority,
                },
            )
            assert response.status_code == 201, f"优先级 {priority} 应该有效"

        # 测试无效优先级
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "content": "测试无效优先级",
                "priority": "invalid_priority",
            },
        )
        assert response.status_code == 400

        print("✅ 反馈优先级验证正常")

    @test_case("TC-FEEDBACK-006", priority="High", expected="需要登录")
    def test_feedback_requires_login(self, client):
        """测试反馈提交需要登录"""
        response = client.post(
            "/api/feedback",
            json={"feedback_type": "bug", "content": "未登录用户的反馈"},
        )

        # Flask 的 @login_required 会返回 302 重定向到登录页
        assert response.status_code in [302, 401, 403]

        print("✅ 反馈提交需要登录验证正常")

    @test_case("TC-FEEDBACK-007", priority="Medium", expected="获取单个反馈")
    def test_get_single_feedback(self, client, create_test_users):
        """测试获取单个反馈详情"""
        # 登录并创建反馈
        client.post("/login", data={"username": "user", "password": "123456"})

        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "title": "详细反馈",
                "content": "反馈详细内容",
            },
        )

        feedback_id = response.get_json()["feedback_id"]

        # 获取单个反馈
        response = client.get(f"/api/feedback/{feedback_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["feedback"]["id"] == feedback_id
        assert data["feedback"]["feedback_type"] == "bug"

        print(f"✅ 单个反馈获取成功，ID: {feedback_id}")

    @test_case("TC-FEEDBACK-008", priority="Low", expected="状态默认值")
    def test_feedback_status_default(self, client, create_test_users):
        """测试反馈状态默认值"""
        client.post("/login", data={"username": "user", "password": "123456"})

        response = client.post(
            "/api/feedback", json={"feedback_type": "bug", "content": "测试状态默认值"}
        )

        feedback_id = response.get_json()["feedback_id"]

        # 获取反馈详情
        response = client.get(f"/api/feedback/{feedback_id}")
        data = response.get_json()

        assert data["feedback"]["status"] == "pending"

        print("✅ 反馈状态默认值为 pending")

    @test_case("TC-FEEDBACK-009", priority="Medium", expected="联系信息可选")
    def test_optional_contact_info(self, client, create_test_users):
        """测试联系信息为可选项"""
        client.post("/login", data={"username": "user", "password": "123456"})

        # 仅提供必要信息
        response = client.post(
            "/api/feedback",
            json={"feedback_type": "improvement", "content": "没有联系信息的反馈"},
        )
        assert response.status_code == 201

        # 提供邮箱
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "feature",
                "content": "有邮箱的反馈",
                "contact_email": "test@example.com",
            },
        )
        assert response.status_code == 201

        # 提供手机号
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "content": "有手机号的反馈",
                "contact_phone": "13800138000",
            },
        )
        assert response.status_code == 201

        print("✅ 联系信息为可选项验证正常")

    @test_case("TC-FEEDBACK-010", priority="Low", expected="标题可选")
    def test_optional_title(self, client, create_test_users):
        """测试标题为可选项"""
        client.post("/login", data={"username": "user", "password": "123456"})

        response = client.post(
            "/api/feedback",
            json={"feedback_type": "bug", "content": "没有标题的反馈内容"},
        )
        assert response.status_code == 201

        print("✅ 标题为可选项验证正常")

    @test_case("TC-FEEDBACK-011", priority="High", expected="分页查询")
    def test_feedback_pagination(self, client, create_test_users):
        """测试反馈分页查询"""
        client.post("/login", data={"username": "user", "password": "123456"})

        # 创建多个反馈
        for i in range(15):
            client.post(
                "/api/feedback",
                json={
                    "feedback_type": "bug",
                    "title": f"测试反馈 {i}",
                    "content": f"反馈内容 {i}",
                },
            )

        # 查询第一页（默认 10 条）
        response = client.get("/api/feedback?page=1&per_page=10")
        data = response.get_json()

        assert "feedbacks" in data
        assert "pagination" in data
        assert len(data["feedbacks"]) == 10
        assert data["pagination"]["total"] >= 15
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["pages"] >= 1

        print(
            f"✅ 分页查询正常，第1页 {len(data['feedbacks'])} 条，总共 {data['pagination']['total']} 条"
        )

    @test_case("TC-FEEDBACK-012", priority="Medium", expected="类型筛选")
    def test_feedback_type_filter(self, client, create_test_users):
        """测试反馈类型筛选"""
        client.post("/login", data={"username": "user", "password": "123456"})

        # 创建不同类型反馈
        client.post(
            "/api/feedback", json={"feedback_type": "bug", "content": "BUG 反馈"}
        )
        client.post(
            "/api/feedback", json={"feedback_type": "feature", "content": "功能建议"}
        )

        # 筛选 BUG 类型
        response = client.get("/api/feedback?type=bug")
        data = response.get_json()

        for feedback in data["feedbacks"]:
            assert feedback["feedback_type"] == "bug"

        print("✅ 类型筛选正常")

    @test_case("TC-FEEDBACK-013", priority="Medium", expected="状态筛选")
    def test_feedback_status_filter(self, client, create_test_users):
        """测试反馈状态筛选"""
        client.post("/login", data={"username": "user", "password": "123456"})

        # 创建反馈
        response = client.post(
            "/api/feedback", json={"feedback_type": "bug", "content": "待处理反馈"}
        )

        # 筛选 pending 状态
        response = client.get("/api/feedback?status=pending")
        data = response.get_json()

        for feedback in data["feedbacks"]:
            assert feedback["status"] == "pending"

        print("✅ 状态筛选正常")

    @test_case("TC-FEEDBACK-014", priority="High", expected="管理员权限管理反馈")
    def test_admin_manage_feedback(self, client, create_test_users):
        """测试管理员权限管理反馈"""
        # 使用管理员登录
        client.post("/login", data={"username": "admin", "password": "123456"})

        # 创建普通用户反馈
        client.post("/login", data={"username": "user", "password": "123456"})
        response = client.post(
            "/api/feedback",
            json={"feedback_type": "bug", "content": "需要管理员处理的反馈"},
        )
        feedback_id = response.get_json()["feedback_id"]

        # 管理员登录
        client.post("/login", data={"username": "admin", "password": "123456"})

        # 更新反馈状态（使用正确的路由）
        response = client.put(
            f"/api/feedback/{feedback_id}/status", json={"status": "processing"}
        )

        assert response.status_code == 200

        # 验证更新成功
        response = client.get(f"/api/feedback/{feedback_id}")
        data = response.get_json()
        assert data["feedback"]["status"] == "processing"

        print("✅ 管理员权限管理反馈正常")

    @test_case("TC-FEEDBACK-015", priority="Low", expected="时间戳自动更新")
    def test_feedback_timestamps(self, client, create_test_users):
        """测试反馈时间戳自动更新"""
        client.post("/login", data={"username": "user", "password": "123456"})

        response = client.post(
            "/api/feedback", json={"feedback_type": "bug", "content": "测试时间戳"}
        )

        feedback_id = response.get_json()["feedback_id"]

        response = client.get(f"/api/feedback/{feedback_id}")
        data = response.get_json()

        feedback = data["feedback"]
        assert "created_at" in feedback
        assert "updated_at" in feedback
        assert feedback["created_at"] is not None
        assert feedback["updated_at"] is not None

        print("✅ 时间戳自动更新正常")


# 性能测试
@pytest.mark.performance
class TestFeedbackPerformance:
    """反馈性能测试"""

    def test_feedback_bulk_create_performance(self, client, create_test_users):
        """测试批量创建反馈的性能"""
        import time

        client.post("/login", data={"username": "user", "password": "123456"})

        start_time = time.time()

        # 批量创建 50 个反馈
        for i in range(50):
            response = client.post(
                "/api/feedback",
                json={
                    "feedback_type": "bug",
                    "title": f"性能测试反馈 {i}",
                    "content": f"性能测试内容 {i}",
                },
            )
            assert response.status_code == 201

        elapsed = time.time() - start_time

        print(f"\n📊 批量创建性能:")
        print(f"  50 个反馈创建时间: {elapsed:.2f}秒")
        print(f"  平均每个反馈: {(elapsed/50)*1000:.1f}ms")

        # 应该在 5 秒内完成
        assert elapsed < 5.0, f"批量创建太慢: {elapsed:.2f}秒"

    def test_feedback_list_performance(self, client, create_test_users):
        """测试反馈列表查询性能"""
        import time

        client.post("/login", data={"username": "user", "password": "123456"})

        # 先创建一些反馈数据
        for i in range(20):
            client.post(
                "/api/feedback",
                json={
                    "feedback_type": "bug",
                    "title": f"列表性能测试 {i}",
                    "content": f"内容 {i}",
                },
            )

        start_time = time.time()

        # 查询反馈列表
        response = client.get("/api/feedback?page=1&per_page=20")
        assert response.status_code == 200

        elapsed = time.time() - start_time

        print(f"\n📊 列表查询性能:")
        print(f"  查询 20 条反馈: {elapsed*1000:.1f}ms")

        # 应该在 500ms 内完成
        assert elapsed < 0.5, f"列表查询太慢: {elapsed:.2f}秒"
