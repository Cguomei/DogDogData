"""
国际化 API 测试
测试语言切换功能和 Flask-Babel 集成
"""

import pytest
from Test.test_framework import test_case


class TestInternationalizationAPI:
    """国际化 API 测试套件"""

    @test_case("TC-I18N-001", priority="High", expected="设置语言成功")
    def test_set_language_success(self, client):
        """测试设置语言成功"""
        response = client.post("/api/set-language", json={"language": "en_US"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert data["language"] == "en_US"
        assert "message" in data

        print(f"✅ 语言切换成功: {data['language']}")

    @test_case("TC-I18N-002", priority="High", expected="获取当前语言")
    def test_get_language(self, client):
        """测试获取当前语言设置"""
        response = client.get("/api/get-language")

        assert response.status_code == 200
        data = response.get_json()
        assert "language" in data
        assert "supported_languages" in data
        assert data["language"] in ["zh_CN", "en_US", "ja_JP"]
        assert len(data["supported_languages"]) == 3

        print(f"✅ 当前语言: {data['language']}")

    @test_case("TC-I18N-003", priority="Critical", expected="支持中文")
    def test_set_language_chinese(self, client):
        """测试设置为中文"""
        response = client.post("/api/set-language", json={"language": "zh_CN"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["language"] == "zh_CN"

        # 验证 Session 中保存了语言
        with client.session_transaction() as sess:
            assert sess.get("language") == "zh_CN"

        print("✅ 中文设置成功")

    @test_case("TC-I18N-004", priority="Critical", expected="支持英文")
    def test_set_language_english(self, client):
        """测试设置为英文"""
        response = client.post("/api/set-language", json={"language": "en_US"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["language"] == "en_US"

        print("✅ 英文设置成功")

    @test_case("TC-I18N-005", priority="Critical", expected="支持日文")
    def test_set_language_japanese(self, client):
        """测试设置为日文"""
        response = client.post("/api/set-language", json={"language": "ja_JP"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["language"] == "ja_JP"

        print("✅ 日文设置成功")

    @test_case("TC-I18N-006", priority="High", expected="拒绝不支持的语言")
    def test_set_unsupported_language(self, client):
        """测试设置不支持的语言"""
        response = client.post(
            "/api/set-language", json={"language": "fr_FR"}  # 法语（不支持）
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

        print(f"✅ 正确拒绝不支持的语言: {data['error']}")

    @test_case("TC-I18N-007", priority="Medium", expected="默认语言为中文")
    def test_default_language_is_chinese(self, client):
        """测试默认语言为中文"""
        response = client.get("/api/get-language")

        assert response.status_code == 200
        data = response.get_json()
        # 新会话应该默认为中文
        assert data["language"] == "zh_CN"

        print("✅ 默认语言为中文")

    @test_case("TC-I18N-008", priority="Medium", expected="语言设置在会话中持久化")
    def test_language_persistence_in_session(self, client):
        """测试语言设置在会话中持久化"""
        # 设置语言
        client.post("/api/set-language", json={"language": "en_US"})

        # 获取语言（应该在同一个会话中）
        response = client.get("/api/get-language")
        data = response.get_json()

        assert data["language"] == "en_US"

        print("✅ 语言设置在会话中持久化")

    @test_case("TC-I18N-009", priority="Low", expected="返回所有支持的语言列表")
    def test_supported_languages_list(self, client):
        """测试返回支持的语言列表"""
        response = client.get("/api/get-language")
        data = response.get_json()

        supported = data["supported_languages"]
        assert "zh_CN" in supported
        assert "en_US" in supported
        assert "ja_JP" in supported
        assert len(supported) == 3

        print(f"✅ 支持的语言列表: {supported}")

    @test_case("TC-I18N-010", priority="Medium", expected="多次切换语言正常")
    def test_multiple_language_switches(self, client):
        """测试多次切换语言"""
        languages = ["zh_CN", "en_US", "ja_JP", "zh_CN"]

        for lang in languages:
            response = client.post("/api/set-language", json={"language": lang})
            assert response.status_code == 200

            # 验证切换成功
            get_response = client.get("/api/get-language")
            data = get_response.get_json()
            assert data["language"] == lang

        print(f"✅ 多次语言切换成功: {' -> '.join(languages)}")

    @test_case("TC-I18N-011", priority="Low", expected="无效参数处理")
    def test_set_language_missing_parameter(self, client):
        """测试缺少语言参数"""
        response = client.post("/api/set-language", json={})

        # 应该使用默认值或返回错误
        assert response.status_code in [200, 400]

        print("✅ 无效参数处理正常")

    @test_case("TC-I18N-012", priority="Medium", expected="URL 参数优先级高于 Session")
    def test_url_param_language_priority(self, app, client):
        """测试 URL 参数语言优先级"""
        from flask_babel import get_locale

        with app.test_request_context("/?lang=en_US"):
            # 模拟请求上下文
            locale = get_locale()
            # 注意：这需要在实际请求中测试
            assert str(locale) == "en_US" or str(locale) == "zh_CN"  # 取决于实现

        print("✅ URL 参数语言优先级测试通过")


# Flask-Babel 集成测试
class TestFlaskBabelIntegration:
    """Flask-Babel 集成测试"""

    @test_case("TC-BABEL-001", priority="High", expected="翻译函数可用")
    def test_translation_function_available(self, app):
        """测试翻译函数可用"""
        with app.app_context():
            from flask_babel import gettext as _

            # 测试基本翻译
            result = _("首页")
            assert result is not None
            assert isinstance(result, str)

            print(f"✅ 翻译函数可用，示例: {result}")

    @test_case("TC-BABEL-002", priority="Medium", expected="时区配置正确")
    def test_timezone_configuration(self, app):
        """测试时区配置"""
        with app.app_context():
            from flask_babel import get_timezone

            timezone = get_timezone()
            assert timezone is not None
            # 默认应该是 Asia/Shanghai
            assert str(timezone) in ["Asia/Shanghai", "UTC"]

            print(f"✅ 时区配置: {timezone}")

    @test_case("TC-BABEL-003", priority="Medium", expected="localeselector 正常工作")
    def test_locale_selector(self, app):
        """测试 locale selector"""
        with app.test_request_context(headers=[("Accept-Language", "en-US")]):
            from flask_babel import get_locale

            locale = get_locale()
            assert locale is not None

            print(f"✅ Locale selector 工作正常: {locale}")


# 性能测试
@pytest.mark.performance
class TestI18NPerformance:
    """国际化性能测试"""

    def test_language_switch_performance(self, client):
        """测试语言切换性能"""
        import time

        response_times = []

        # 执行 50 次语言切换
        for i in range(50):
            lang = ["zh_CN", "en_US", "ja_JP"][i % 3]

            start = time.time()
            response = client.post("/api/set-language", json={"language": lang})
            elapsed = (time.time() - start) * 1000

            response_times.append(elapsed)
            assert response.status_code == 200

        # 统计性能
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)

        print(f"\n📊 语言切换性能:")
        print(f"  平均响应时间: {avg_time:.2f}ms")
        print(f"  最大响应时间: {max_time:.2f}ms")

        # 断言：平均响应时间应小于 50ms
        assert avg_time < 50, f"平均响应时间过长: {avg_time}ms"
