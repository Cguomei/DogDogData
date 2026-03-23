"""
用户认证模块测试用例
覆盖登录、注册、登出、权限控制等场景
"""
import pytest
from .test_framework import test_case, test_manager, TestResult
from models import User


class TestUserAuthentication:
    """用户认证测试类"""
    
    @test_case('TC-AUTH-001', priority='High', expected='注册成功，跳转到登录页面')
    def test_register_success(self, client, db):
        """用户注册 - 成功场景"""
        result = TestResult('TC-AUTH-001', 'test_register_success', '用户认证', 'High')
        result.expected_result = '注册成功，创建新用户'
        
        try:
            # 执行注册
            response = client.post('/register', data={
                'username': 'testuser001',
                'password': 'TestPass123!'
            }, follow_redirects=True)
            
            response_text = response.get_data(as_text=True)
            
            # 验证结果
            assert response.status_code == 200
            assert '登录' in response_text  # 应跳转到登录页面
            
            # 验证数据库中是否存在用户
            user = User.query.filter_by(username='testuser001').first()
            assert user is not None
            assert user.username == 'testuser001'
            
            result.status = 'PASS'
            result.actual_result = f'注册成功，用户 ID: {user.id}'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            result.actual_result = f'注册失败：{str(e)}'
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-002', priority='High', expected='注册失败，提示用户名已存在')
    def test_register_duplicate_username(self, client, db):
        """用户注册 - 重复用户名"""
        result = TestResult('TC-AUTH-002', 'test_register_duplicate', '用户认证', 'High')
        result.expected_result = '拒绝重复用户名'
        
        try:
            # 先创建一个用户
            user = User(username='duplicate_user')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # 尝试注册同名用户
            response = client.post('/register', data={
                'username': 'duplicate_user',
                'password': 'AnotherPass456'
            }, follow_redirects=True)
            
            response_text = response.get_data(as_text=True)
            
            # 应该失败
            assert '用户名已存在' in response_text or response.status_code != 200
            
            result.status = 'PASS'
            result.actual_result = '正确拒绝重复用户名'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-003', priority='Critical', expected='登录成功，跳转到首页')
    def test_login_success(self, client, db):
        """用户登录 - 成功场景"""
        result = TestResult('TC-AUTH-003', 'test_login_success', '用户认证', 'Critical')
        result.expected_result = '登录成功'
        
        try:
            # 创建测试用户
            user = User(username='login_test_user')
            user.set_password('correct_password')
            db.session.add(user)
            db.session.commit()
            
            # 执行登录
            response = client.post('/login', data={
                'username': 'login_test_user',
                'password': 'correct_password'
            }, follow_redirects=True)
            
            response_text = response.get_data(as_text=True)
            
            # 验证登录成功
            assert response.status_code == 200
            assert '首页' in response_text or '数据看板' in response_text
            
            result.status = 'PASS'
            result.actual_result = '登录成功，跳转到首页'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-004', priority='High', expected='登录失败，提示用户名或密码错误')
    def test_login_wrong_password(self, client, db):
        """用户登录 - 错误密码"""
        result = TestResult('TC-AUTH-004', 'test_login_wrong_password', '用户认证', 'High')
        result.expected_result = '登录失败'
        
        try:
            # 创建测试用户
            user = User(username='password_test_user')
            user.set_password('correct_password')
            db.session.add(user)
            db.session.commit()
            
            # 使用错误密码登录
            response = client.post('/login', data={
                'username': 'password_test_user',
                'password': 'wrong_password'
            }, follow_redirects=True)
            
            response_text = response.get_data(as_text=True)
            
            # 验证登录失败
            assert '用户名或密码错误' in response_text
            
            result.status = 'PASS'
            result.actual_result = '正确拒绝错误密码'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-005', priority='Medium', expected='登出成功，跳转到首页')
    def test_logout(self, logged_in_client):
        """用户登出"""
        result = TestResult('TC-AUTH-005', 'test_logout', '用户认证', 'Medium')
        result.expected_result = '登出成功'
        
        try:
            # 执行登出
            response = logged_in_client.get('/logout', follow_redirects=True)
            
            response_text = response.get_data(as_text=True)
            
            # 验证登出成功
            assert response.status_code == 200
            assert '已退出登录' in response_text or '登录' in response_text
            
            result.status = 'PASS'
            result.actual_result = '登出成功'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-006', priority='High', expected='重定向到登录页面')
    def test_access_protected_page_without_login(self, client):
        """访问受保护页面 - 未登录"""
        result = TestResult('TC-AUTH-006', 'test_access_protected', '用户认证', 'High')
        result.expected_result = '重定向到登录页'
        
        try:
            # 尝试直接访问管理页面
            response = client.get('/admin/breeds', follow_redirects=False)
            
            # 应该重定向
            assert response.status_code in [302, 401]
            
            result.status = 'PASS'
            result.actual_result = f'正确拦截未登录访问，状态码：{response.status_code}'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-AUTH-007', priority='Critical', expected='SQL 注入攻击失败')
    def test_sql_injection_login(self, client, db):
        """SQL 注入攻击 - 登录接口"""
        result = TestResult('TC-AUTH-007', 'test_sql_injection_login', '安全性', 'Critical')
        result.expected_result = 'SQL 注入攻击被阻止'
        
        try:
            # 创建测试用户
            user = User(username='admin')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            
            # SQL 注入 payload
            payloads = [
                "' OR '1'='1",
                "admin' --",
                "' OR 1=1 --"
            ]
            
            for payload in payloads:
                response = client.post('/login', data={
                    'username': payload,
                    'password': 'anything'
                }, follow_redirects=True)
                
                response_text = response.get_data(as_text=True)
                
                # 不应该成功登录
                assert '登录成功' not in response_text
                assert '用户名或密码错误' in response_text
            
            result.status = 'PASS'
            result.actual_result = '所有 SQL 注入 payload 均被阻止'
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = f'SQL 注入漏洞！Payload 可能绕过认证：{str(e)}'
            # 记录严重 Bug
            from bug_tracker import report_bug
            report_bug(
                title="SQL 注入漏洞 - 登录绕过",
                description=f"发现 SQL 注入漏洞，payload 可能绕过认证",
                severity="Critical",
                priority="High",
                module="安全性-认证",
                steps_to_reproduce=[
                    "访问 /login",
                    "使用 SQL 注入 payload 作为用户名",
                    "输入任意密码",
                    "提交表单"
                ],
                expected_result="应始终验证失败",
                actual_result=result.error_message
            )
            raise
        finally:
            test_manager.record_result(result)
