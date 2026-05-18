"""
安全测试模块
测试常见的 Web 安全漏洞
"""

import pytest
import re
from Test.bug_tracker import report_bug


class TestSQLInjection:
    """SQL 注入测试"""

    def test_login_sql_injection(self, client):
        """测试登录接口的 SQL 注入防护"""
        payloads = [
            "' OR '1'='1",
            "admin' --",
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
        ]

        for payload in payloads:
            response = client.post(
                "/login",
                data={"username": payload, "password": "anything"},
                follow_redirects=True,
            )

            response_text = response.get_data(as_text=True)

            # 不应该成功登录
            if "登录成功" in response_text:
                report_bug(
                    title=f"SQL 注入漏洞 - 登录接口",
                    description=f"使用 payload '{payload}' 可能绕过认证",
                    severity="Critical",
                    priority="High",
                    module="安全性-SQL 注入",
                    steps_to_reproduce=[
                        "访问 /login",
                        f"用户名输入：{payload}",
                        "密码输入任意值",
                        "提交表单",
                    ],
                    expected_result="登录失败，提示用户名或密码错误",
                    actual_result="可能登录成功",
                )

    def test_api_breed_sql_injection(self, client):
        """测试品种 API 的 SQL 注入防护"""
        # 这个测试需要在已登录状态下进行
        # 先登录
        client.post("/login", data={"username": "admin", "password": "123456"})

        malicious_names = [
            "'; DROP TABLE dog_breeds; --",
            "' OR '1'='1",
            "1'; DELETE FROM dog_breeds WHERE '1'='1",
        ]

        for name in malicious_names:
            response = client.post(
                "/api/breeds",
                json={
                    "breed_name": name,
                    "avg_life_years": 10,
                    "size_category": "中型",
                    "popularity": 50,
                },
            )

            # 系统应该拒绝这些恶意输入
            if response.status_code == 201:
                report_bug(
                    title=f"API SQL 注入风险",
                    description=f"接受了潜在的 SQL 注入数据：{name}",
                    severity="Critical",
                    priority="High",
                    module="安全性-SQL 注入",
                    steps_to_reproduce=[
                        "登录为管理员",
                        f"POST /api/breeds，breed_name 使用：{name}",
                    ],
                    expected_result="应拒绝请求并返回错误",
                    actual_result="接受了恶意数据",
                )


class TestXSS:
    """跨站脚本攻击 (XSS) 测试"""

    def test_xss_in_breed_name(self, admin_client):
        """测试品种名称中的 XSS 攻击"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
        ]

        for payload in xss_payloads:
            response = admin_client.post(
                "/api/breeds",
                json={
                    "breed_name": payload,
                    "avg_life_years": 10,
                    "size_category": "中型",
                    "popularity": 50,
                },
            )

            # 获取品种列表查看是否存储了恶意脚本
            list_response = admin_client.get("/api/breeds")
            data = list_response.get_json()

            # 检查是否有 script 标签被原样保存
            for breed in data:
                if payload in breed.get("breed_name", ""):
                    report_bug(
                        title="XSS 漏洞 - 品种名称未过滤",
                        description=f"恶意脚本被存储：{payload}",
                        severity="Critical",
                        priority="High",
                        module="安全性-XSS",
                        steps_to_reproduce=[
                            "管理员添加品种",
                            f"品种名输入：{payload}",
                            "查看品种列表",
                        ],
                        expected_result="应过滤或转义 HTML/JavaScript 代码",
                        actual_result="恶意脚本被原样存储和显示",
                    )

    def test_xss_in_user_input(self, client):
        """测试用户输入的 XSS 防护"""
        # 注册时尝试 XSS
        xss_username = "<script>alert(document.cookie)</script>"

        response = client.post(
            "/register",
            data={"username": xss_username, "password": "testpass123"},
            follow_redirects=True,
        )

        # 检查响应中是否包含未转义的脚本
        response_text = response.get_data(as_text=True)
        if xss_username in response_text and "<script>" in response_text:
            report_bug(
                title="XSS 漏洞 - 用户名未转义",
                description="注册时的 XSS 攻击可能成功",
                severity="Major",
                priority="High",
                module="安全性-XSS",
                steps_to_reproduce=[
                    "访问 /register",
                    f"用户名输入：{xss_username}",
                    "提交注册",
                ],
                expected_result="应对特殊字符进行转义或过滤",
                actual_result="可能包含未转义的脚本",
            )


class TestCSRF:
    """跨站请求伪造 (CSRF) 测试"""

    def test_csrf_on_sensitive_operations(self, admin_client):
        """测试敏感操作是否有 CSRF 保护"""
        # 注意：Flask 默认不包含 CSRF 保护，需要 Flask-WTF

        # 尝试删除操作（应该有 CSRF token）
        # 先创建一个品种
        create_response = admin_client.post(
            "/api/breeds",
            json={
                "breed_name": "CSRF 测试犬",
                "avg_life_years": 10,
                "size_category": "中型",
                "popularity": 50,
            },
        )

        if create_response.status_code == 201:
            breed_id = create_response.get_json()["id"]

            # 直接发送 DELETE 请求（没有 CSRF token）
            delete_response = admin_client.delete(f"/api/breeds/{breed_id}")

            # 如果成功删除，说明缺少 CSRF 保护
            if delete_response.status_code == 200:
                report_bug(
                    title="缺少 CSRF 保护",
                    description="敏感操作（删除）没有 CSRF token 验证",
                    severity="Major",
                    priority="Medium",
                    module="安全性-CSRF",
                    steps_to_reproduce=[
                        "登录为管理员",
                        "直接发送 DELETE 请求到 /api/breeds/<id>",
                        "无需 CSRF token",
                    ],
                    expected_result="应要求 CSRF token 验证",
                    actual_result="请求成功执行",
                )


class TestAuthentication:
    """认证安全测试"""

    def test_brute_force_protection(self, client):
        """测试暴力破解防护"""
        # 尝试多次登录失败
        failed_attempts = 10

        for i in range(failed_attempts):
            response = client.post(
                "/login", data={"username": "admin", "password": f"wrong_password_{i}"}
            )

        # 检查是否有速率限制或账户锁定
        # 注意：这需要实际实现才能检测

        # 第 11 次尝试
        response = client.post(
            "/login", data={"username": "admin", "password": "another_wrong"}
        )

        # 理想情况下应该有某种限制机制
        print("\n建议：实现登录失败次数限制机制")

    def test_session_security(self, client):
        """测试会话安全性"""
        # 登录
        response = client.post("/login", data={"username": "user", "password": "123"})

        # 检查 session cookie 属性
        cookies = response.headers.getlist("Set-Cookie")

        has_secure_cookie = False
        has_httponly = False

        for cookie in cookies:
            if "session" in cookie.lower():
                has_secure_cookie = True
                if "httponly" in cookie.lower():
                    has_httponly = True

        if not has_httponly:
            report_bug(
                title="Session Cookie 缺少 HttpOnly 标志",
                description="Cookie 未设置 HttpOnly，可能被 JavaScript 访问",
                severity="Minor",
                priority="Low",
                module="安全性-会话",
                steps_to_reproduce=["登录后检查 Cookie 属性"],
                expected_result="Cookie 应设置 HttpOnly 和 Secure 标志",
                actual_result="可能缺少安全标志",
            )


class TestInformationDisclosure:
    """信息泄露测试"""

    def test_error_messages(self, client):
        """测试错误信息是否泄露敏感数据"""
        # 访问不存在的页面
        response = client.get("/nonexistent-page-12345")

        response_text = response.get_data(as_text=True)

        # 检查是否包含敏感信息
        sensitive_patterns = [
            r"SQLAlchemy",
            r"mysql\+pymysql",
            r"password.*:",
            r"DB_",
            r"traceback",
            r'File ".*\.py"',
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                report_bug(
                    title="错误信息泄露敏感数据",
                    description=f"错误页面包含敏感信息：{pattern}",
                    severity="Major",
                    priority="Medium",
                    module="安全性-信息泄露",
                    steps_to_reproduce=["访问不存在的页面"],
                    expected_result="显示友好的自定义错误页面，不泄露技术细节",
                    actual_result="可能显示堆栈跟踪或数据库信息",
                )

    def test_api_exposes_internal_ids(self, client):
        """测试 API 是否暴露内部 ID"""
        # 登录
        client.post("/login", data={"username": "admin", "password": "123456"})

        # 获取品种列表
        response = client.get("/api/breeds")
        data = response.get_json()

        if data and isinstance(data, list):
            for item in data:
                if "id" in item:
                    # 暴露内部 ID 可能被利用
                    print("\n提示：考虑使用 UUID 代替自增 ID")
                    break


class TestSecurityHeaders:
    """安全响应头测试"""

    def test_security_headers(self, client):
        """检查安全响应头"""
        response = client.get("/")

        headers_to_check = {
            "X-Frame-Options": "防止点击劫持",
            "X-Content-Type-Options": "防止 MIME 类型混淆",
            "X-XSS-Protection": "XSS 过滤器",
            "Strict-Transport-Security": "强制 HTTPS",
            "Content-Security-Policy": "内容安全策略",
        }

        missing_headers = []

        for header, purpose in headers_to_check.items():
            if header not in response.headers:
                missing_headers.append(f"{header} ({purpose})")

        if missing_headers:
            print(f"\n缺少以下安全响应头:")
            for header in missing_headers:
                print(f"  - {header}")

            report_bug(
                title="缺少安全响应头",
                description=f"缺少以下 HTTP 安全头：{', '.join(missing_headers)}",
                severity="Minor",
                priority="Low",
                module="安全性-响应头",
                steps_to_reproduce=["检查所有响应的 HTTP 头"],
                expected_result="应包含所有推荐的安全响应头",
                actual_result=f"缺少：{', '.join(missing_headers)}",
            )
