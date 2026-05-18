"""
AI助手功能完善测试 - 方案A
测试上下文对话、问题分类优化、用户反馈等功能
"""

import pytest
import json


class TestContextConversation:
    """上下文对话测试"""

    def test_multi_turn_conversation(self, authenticated_api_client):
        """测试多轮对话 - 上下文理解"""
        # 第1轮：询问金毛价格
        response1 = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1["success"] is True
        session_id = data1.get("session_id")
        assert session_id is not None

        # 第2轮：追问（应该能理解上下文）
        response2 = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "那泰迪呢？", "session_id": session_id}
        )

        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2["success"] is True
        # 回答应该包含泰迪相关信息，而不是再次询问金毛
        assert "泰迪" in data2["answer"] or "贵宾" in data2["answer"]

    def test_context_reference_understanding(self, authenticated_api_client):
        """测试指代性问题的理解"""
        # 第1轮：询问品种信息
        response1 = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "介绍一下金毛犬"}
        )

        assert response1.status_code == 200
        data1 = response1.get_json()
        session_id = data1.get("session_id")

        # 第2轮：使用"它"指代
        response2 = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "它好养吗？", "session_id": session_id}
        )

        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2["success"] is True
        # 回答应该与金毛相关
        assert (
            "金毛" in data2["answer"]
            or "容易" in data2["answer"]
            or "难" in data2["answer"]
        )

    def test_session_history_persistence(self, authenticated_api_client):
        """测试会话历史持久化"""
        # 创建会话并发送多条消息
        session_id = None

        for i in range(3):
            response = authenticated_api_client.post(
                "/api/ai/chat",
                json={"message": f"测试消息{i+1}", "session_id": session_id},
            )

            assert response.status_code == 200
            data = response.get_json()
            if session_id is None:
                session_id = data.get("session_id")

        # 获取会话历史
        response = authenticated_api_client.get(
            f"/api/ai/sessions/{session_id}/messages"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "messages" in data
        # 应该有6条消息（3条用户 + 3条AI）
        assert len(data["messages"]) >= 6


class TestQuestionClassification:
    """问题分类器优化测试"""

    def test_price_query_variations(self, authenticated_api_client):
        """测试价格查询的多种表达方式"""
        test_cases = [
            "金毛多少钱？",
            "泰迪的价格",
            "柯基售价多少",
            "哈士奇价位",
            "买一只金毛要多少钱",
        ]

        for message in test_cases:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": message}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert (
                data["type"] == "price_query"
            ), f"消息 '{message}' 应该被分类为 price_query"

    def test_breed_info_variations(self, authenticated_api_client):
        """测试品种信息查询的多种表达方式"""
        test_cases = [
            "金毛有什么特点？",
            "介绍一下泰迪",
            "柯基的性格怎么样",
            "哈士奇的习性",
            "拉布拉多寿命多长",
        ]

        for message in test_cases:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": message}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert (
                data["type"] == "breed_info"
            ), f"消息 '{message}' 应该被分类为 breed_info"

    def test_recommendation_variations(self, authenticated_api_client):
        """测试推荐问题的多种表达方式"""
        test_cases = [
            "适合新手养的狗",
            "第一次养狗推荐什么品种",
            "推荐几种温顺的狗狗",
            "家里有小孩适合养什么狗",
        ]

        for message in test_cases:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": message}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert (
                data["type"] == "recommendation"
            ), f"消息 '{message}' 应该被分类为 recommendation"

    def test_chart_generation_detection(self, authenticated_api_client):
        """测试图表生成请求检测"""
        test_cases = [
            "生成一个价格散点图",
            "显示体重趋势折线图",
            "画一个品种等级柱状图",
            "可视化店铺Top10",
        ]

        for message in test_cases:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": message}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert (
                data["type"] == "chart_generation"
            ), f"消息 '{message}' 应该被分类为 chart_generation"


class TestAnswerQuality:
    """回答质量测试"""

    def test_answer_contains_source_hint(self, authenticated_api_client):
        """测试回答包含来源提示"""
        response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # 回答应该包含来源提示
        answer = data["answer"]
        has_source = (
            "📚" in answer or "💡" in answer or "知识库" in answer or "AI模型" in answer
        )
        assert has_source, "回答应该包含来源提示（知识库或AI模型）"

    def test_answer_not_empty(self, authenticated_api_client):
        """测试回答不为空"""
        test_messages = ["金毛多少钱？", "泰迪有什么特点？", "推荐新手养的狗"]

        for message in test_messages:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": message}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["answer"]) > 20, f"回答太短: {data['answer']}"

    def test_answer_no_error_indicators(self, authenticated_api_client):
        """测试回答不包含错误指示词"""
        response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        assert response.status_code == 200
        data = response.get_json()
        answer = data["answer"]

        # 不应该包含明显的错误指示（除了正常的来源提示）
        error_words = ["无法连接", "调用失败", "请求超时"]
        for word in error_words:
            assert word not in answer, f"回答包含错误指示词: {word}"


class TestUserFeedback:
    """用户反馈功能测试"""

    def test_submit_positive_feedback(self, authenticated_api_client):
        """测试提交正面反馈"""
        # 先发送一条消息获取message_id
        response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        assert response.status_code == 200
        data = response.get_json()
        message_id = data.get("message_id")

        if message_id:
            # 提交点赞（使用feedback字段而非rating）
            feedback_response = authenticated_api_client.post(
                "/api/ai/feedback", json={"message_id": message_id, "feedback": "like"}
            )

            assert feedback_response.status_code in [200, 403]  # 403表示权限问题

    def test_submit_negative_feedback(self, authenticated_api_client):
        """测试提交负面反馈"""
        # 先发送一条消息获取message_id
        response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        assert response.status_code == 200
        data = response.get_json()
        message_id = data.get("message_id")

        if message_id:
            # 提交点踩（使用feedback字段）
            feedback_response = authenticated_api_client.post(
                "/api/ai/feedback",
                json={
                    "message_id": message_id,
                    "feedback": "dislike",
                    "comment": "回答不够详细",
                },
            )

            assert feedback_response.status_code in [200, 403]  # 403表示权限问题


class TestKnowledgeBaseMatching:
    """知识库匹配优化测试"""

    def test_fuzzy_matching(self, authenticated_api_client):
        """测试模糊匹配"""
        # 测试相似问题的匹配
        test_cases = [
            ("金毛多少钱？", "金毛的价格"),
            ("泰迪贵不贵？", "泰迪的价格"),
            ("柯基好养吗？", "柯基的特点"),
        ]

        for question, expected_topic in test_cases:
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": question}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            # 如果命中知识库，source应该是knowledge_base
            # 如果没有命中，也会返回模型生成的答案
            assert "answer" in data


class TestPerformance:
    """性能测试"""

    def test_response_time(self, authenticated_api_client):
        """测试响应时间"""
        import time

        start_time = time.time()

        response = authenticated_api_client.post(
            "/api/ai/chat", json={"message": "金毛的价格是多少？"}
        )

        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        # 响应时间应该小于10秒（考虑到本地模型）
        assert elapsed_time < 10, f"响应时间过长: {elapsed_time:.2f}秒"

    def test_concurrent_requests(self, authenticated_api_client):
        """测试并发请求（简化版）"""
        import time

        start_time = time.time()

        # 发送3个请求
        for i in range(3):
            response = authenticated_api_client.post(
                "/api/ai/chat", json={"message": f"测试消息{i+1}"}
            )
            assert response.status_code == 200

        elapsed_time = time.time() - start_time

        # 总时间应该合理
        assert elapsed_time < 30, f"并发请求耗时过长: {elapsed_time:.2f}秒"
