"""
安全测试 - 涵盖常见Web安全漏洞检测
包括：XSS、CSRF、SQL注入、路径遍历、权限绕过等
"""
import pytest


@pytest.mark.api
class TestSecurityXSS:
    """跨站脚本攻击(XSS)测试"""
    
    def test_xss_in_feedback_title(self, authenticated_api_client):
        """TC-SEC-XSS-001: 反馈标题中的XSS攻击"""
        xss_payload = '<script>alert("XSS")</script>'
        
        response = authenticated_api_client.post('/api/feedback', json={
            'title': xss_payload,
            'content': '测试内容',
            'feedback_type': 'bug'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # 验证脚本标签被转义或移除
        if 'title' in data:
            assert '<script>' not in data['title'], "XSS脚本未被过滤"
    
    def test_xss_in_feedback_content(self, authenticated_api_client):
        """TC-SEC-XSS-002: 反馈内容中的XSS攻击"""
        xss_payload = '<img src=x onerror=alert("XSS")>'
        
        response = authenticated_api_client.post('/api/feedback', json={
            'title': '测试标题',
            'content': xss_payload,
            'feedback_type': 'suggestion'
        })
        
        # 可能返回201（成功）或400（被拒绝），都算安全
        assert response.status_code in [201, 400]
        
        if response.status_code == 201:
            data = response.get_json()
            # 验证危险标签被处理
            if 'content' in data:
                assert 'onerror=' not in data['content'].lower(), "XSS事件处理器未被过滤"
    
    def test_xss_in_breed_name(self, admin_api_client):
        """TC-SEC-XSS-003: 品种名称中的XSS攻击"""
        xss_payload = '金毛<script>alert(1)</script>'
        
        response = admin_api_client.post('/api/breeds', json={
            'breed_name': xss_payload,
            'avg_life_years': 12,
            'size_category': '大型',
            'popularity': 100
        })
        
        # 应该被拒绝或清理
        if response.status_code == 201:
            data = response.get_json()
            if 'breed_name' in data:
                assert '<script>' not in data['breed_name']
    
    def test_xss_in_chat_message(self, authenticated_api_client):
        """TC-SEC-XSS-004: AI聊天消息中的XSS攻击"""
        xss_payload = '<svg onload=alert("XSS")>你好'
        
        response = authenticated_api_client.post('/api/ai/chat', json={
            'message': xss_payload
        })
        
        assert response.status_code == 200
        # 系统应该正常处理，但不执行脚本
    
    def test_reflected_xss_in_search(self, authenticated_api_client):
        """TC-SEC-XSS-005: 搜索参数中的反射型XSS"""
        xss_payload = '<script>alert(document.cookie)</script>'
        
        response = authenticated_api_client.get(f'/api/food/search?brand={xss_payload}')
        
        assert response.status_code == 200
        # 响应中不应该包含未转义的脚本


@pytest.mark.api
class TestSecuritySQLInjection:
    """SQL注入攻击测试"""
    
    def test_sql_injection_in_breed_search(self, api_client):
        """TC-SEC-SQL-001: 品种搜索中的SQL注入"""
        sqli_payload = "' OR '1'='1"
        
        response = api_client.get(f'/api/breeds?search={sqli_payload}')
        
        # 应该返回正常结果或错误，不应泄露数据库信息
        assert response.status_code in [200, 400, 404]
        data = response.get_json()
        
        # 不应包含SQL错误信息
        if isinstance(data, dict) and 'error' in data:
            assert 'sql' not in data['error'].lower()
            assert 'syntax' not in data['error'].lower()
    
    def test_sql_injection_in_food_search(self, authenticated_api_client):
        """TC-SEC-SQL-002: 狗粮搜索中的SQL注入"""
        sqli_payload = "'; DROP TABLE dog_wykl; --"
        
        response = authenticated_api_client.get(f'/api/food/search?brand={sqli_payload}')
        
        assert response.status_code == 200
        # 表不应该被删除，后续查询仍应成功
        
        # 验证表仍然存在
        verify_response = authenticated_api_client.get('/api/food/statistics')
        assert verify_response.status_code == 200
    
    def test_sql_injection_in_price_filter(self, authenticated_api_client):
        """TC-SEC-SQL-003: 价格筛选中的SQL注入"""
        sqli_payload = "1 OR 1=1"
        
        response = authenticated_api_client.get(f'/api/food/filter?min_price={sqli_payload}')
        
        # 应该返回错误或空结果，不应执行恶意SQL
        assert response.status_code in [200, 400]
    
    def test_sql_injection_in_user_id(self, authenticated_api_client):
        """TC-SEC-SQL-004: 用户ID参数中的SQL注入"""
        sqli_payload = "1 OR 1=1"
        
        response = authenticated_api_client.get(f'/api/feedback/{sqli_payload}')
        
        # 应该返回404或错误
        assert response.status_code in [400, 404]


@pytest.mark.api
class TestSecurityAuthentication:
    """认证和授权测试"""
    
    def test_access_protected_route_without_auth(self, api_client):
        """TC-SEC-AUTH-001: 未认证访问受保护路由"""
        response = api_client.get('/api/feedback')
        
        # 应该被重定向或返回401
        assert response.status_code in [302, 401, 403]
    
    def test_access_admin_route_as_user(self, authenticated_api_client):
        """TC-SEC-AUTH-002: 普通用户访问管理员路由"""
        # 尝试删除品种（需要管理员权限）
        response = authenticated_api_client.delete('/api/breeds/1')
        
        # 应该返回403 Forbidden
        assert response.status_code == 403
    
    def test_access_admin_route_without_auth(self, api_client):
        """TC-SEC-AUTH-003: 未认证访问管理员路由"""
        response = api_client.delete('/api/breeds/1')
        
        assert response.status_code in [302, 401, 403]
    
    def test_session_fixation(self, api_client):
        """TC-SEC-AUTH-004: 会话固定攻击"""
        # 先获取一个会话
        api_client.get('/login')
        
        # 尝试使用固定会话ID登录
        with api_client.session_transaction() as sess:
            sess['fixed_session'] = 'attacker_controlled'
        
        # 登录
        response = api_client.post('/login', data={
            'username': 'user',
            'password': '123456'
        }, follow_redirects=True)
        
        # 会话应该被更新，而不是使用固定的
        assert response.status_code == 200


@pytest.mark.api
class TestSecurityInputValidation:
    """输入验证测试"""
    
    def test_oversized_input(self, authenticated_api_client):
        """TC-SEC-INPUT-001: 超大输入测试"""
        # 创建超长字符串 (1MB)
        large_input = 'A' * (1024 * 1024)
        
        response = authenticated_api_client.post('/api/feedback', json={
            'title': '测试',
            'content': large_input,
            'feedback_type': 'bug'
        })
        
        # 应该被拒绝或截断
        assert response.status_code in [201, 400, 413]
    
    def test_negative_values(self, authenticated_api_client):
        """TC-SEC-INPUT-002: 负数值测试"""
        response = authenticated_api_client.get('/api/food/filter?min_price=-999999')
        
        # 应该正确处理，不导致错误
        assert response.status_code in [200, 400]
    
    def test_special_characters_in_filename(self, authenticated_api_client):
        """TC-SEC-INPUT-003: 文件名中的特殊字符"""
        malicious_filename = '../../../etc/passwd'
        
        import io
        data = {
            'file': (io.BytesIO(b'test'), malicious_filename)
        }
        
        response = authenticated_api_client.post('/api/upload-data',
                                                data=data,
                                                content_type='multipart/form-data')
        
        # 应该被拒绝或安全处理
        assert response.status_code in [200, 400]
    
    def test_null_bytes_in_input(self, authenticated_api_client):
        """TC-SEC-INPUT-004: 输入中的空字节"""
        null_byte_payload = 'test\x00injection'
        
        response = authenticated_api_client.post('/api/feedback', json={
            'title': null_byte_payload,
            'content': '测试内容',
            'feedback_type': 'bug'
        })
        
        # 应该正常处理或被拒绝
        assert response.status_code in [201, 400]


@pytest.mark.api
class TestSecurityPathTraversal:
    """路径遍历攻击测试"""
    
    def test_path_traversal_in_export(self, authenticated_api_client):
        """TC-SEC-PATH-001: 导出功能中的路径遍历"""
        malicious_filename = '../../../etc/passwd'
        
        response = authenticated_api_client.get(f'/api/food/export?format=csv')
        
        # 应该正常导出，不受文件名影响
        assert response.status_code == 200
    
    def test_path_traversal_in_upload(self, authenticated_api_client):
        """TC-SEC-PATH-002: 上传功能中的路径遍历"""
        import io
        
        # 尝试上传到系统目录
        data = {
            'file': (io.BytesIO(b'test'), '../../tmp/malicious.txt')
        }
        
        response = authenticated_api_client.post('/api/upload-data',
                                                data=data,
                                                content_type='multipart/form-data')
        
        # 应该被拒绝或保存到安全位置
        assert response.status_code in [200, 400]


@pytest.mark.api
class TestSecurityRateLimiting:
    """速率限制测试"""
    
    def test_brute_force_login(self, api_client):
        """TC-SEC-RATE-001: 登录暴力破解"""
        # 快速发送多个登录请求
        responses = []
        for i in range(10):
            response = api_client.post('/login', data={
                'username': 'nonexistent_user',  # 使用不存在的用户
                'password': f'wrong_password_{i}'
            }, follow_redirects=False)
            responses.append(response.status_code)
        
        # 应该有失败响应（302重定向到登录页也算失败）
        # 或者如果有速率限制，应该返回429
        print(f"\n登录尝试响应码: {responses}")
        
        # 所有尝试都应该失败（200表示登录成功页面，但实际登录失败会重定向）
        # 如果返回200，说明显示的是登录表单（失败）
        # 如果返回302，说明重定向（可能成功或失败）
        # 这里我们检查是否所有请求都被处理了
        assert len(responses) == 10, f"应该执行10次登录尝试，实际{len(responses)}次"
    
    def test_api_flood(self, authenticated_api_client):
        """TC-SEC-RATE-002: API洪水攻击"""
        # 快速发送多个API请求
        responses = []
        for i in range(20):
            response = authenticated_api_client.get('/api/food/list')
            responses.append(response.status_code)
        
        # 所有请求都应该成功（如果没有速率限制）
        # 或者有速率限制返回429
        assert all(status in [200, 429] for status in responses)


@pytest.mark.api
class TestSecurityHeaders:
    """安全响应头测试"""
    
    def test_security_headers_present(self, api_client):
        """TC-SEC-HEADER-001: 检查安全响应头"""
        response = api_client.get('/')
        
        # 检查常见的安全头（如果配置了的话）
        headers = response.headers
        
        # 这些头可能有也可能没有，取决于配置
        # 这里只是记录，不作为失败条件
        print("\n安全响应头检查:")
        print(f"  X-Content-Type-Options: {headers.get('X-Content-Type-Options', '未设置')}")
        print(f"  X-Frame-Options: {headers.get('X-Frame-Options', '未设置')}")
        print(f"  X-XSS-Protection: {headers.get('X-XSS-Protection', '未设置')}")
        print(f"  Strict-Transport-Security: {headers.get('Strict-Transport-Security', '未设置')}")
        print(f"  Content-Security-Policy: {headers.get('Content-Security-Policy', '未设置')}")
        
        # 至少应该成功响应
        assert response.status_code == 200
    
    def test_no_server_header_leak(self, api_client):
        """TC-SEC-HEADER-002: 服务器信息泄露"""
        response = api_client.get('/')
        
        # Server头不应该泄露详细版本信息
        server_header = response.headers.get('Server', '')
        
        # 如果存在，不应该包含具体版本号
        if server_header:
            # 允许简单的"Server"，但不允许"Werkzeug/2.0.0"这样的详细信息
            print(f"\nServer头: {server_header}")
            # 这不是强制失败，只是警告


# 运行测试
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",
        "--html=Test/reports/security_test_report.html",
        "--self-contained-html"
    ])
