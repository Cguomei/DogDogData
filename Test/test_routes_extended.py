"""
路由测试补充用例
覆盖所有页面路由和重定向逻辑
"""
import pytest
from Test.test_framework import test_case, test_manager, TestResult


class TestPageRoutes:
    """页面路由测试类"""
    
    @test_case('TC-ROUTE-001', priority='High', expected='首页正常访问')
    def test_index_page(self, client):
        """访问首页"""
        result = TestResult('TC-ROUTE-001', 'test_index', '路由', 'High')
        result.expected_result = '返回首页 HTML'
        
        try:
            response = client.get('/')
            assert response.status_code == 200
            # 使用 decode 处理 bytes 以避免中文字符问题
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '数据看板' in html_content or '首页' in html_content
            
            result.status = 'PASS'
            result.actual_result = "首页访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-002', priority='Medium', expected='图表列表页正常访问')
    def test_charts_list_page(self, client):
        """访问图表列表页"""
        result = TestResult('TC-ROUTE-002', 'test_charts_list', '路由', 'Medium')
        result.expected_result = '返回图表列表 HTML'
        
        try:
            response = client.get('/charts')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '图表' in html_content
            
            result.status = 'PASS'
            result.actual_result = "图表列表页访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-003', priority='Medium', expected='登录页正常访问')
    def test_login_page(self, client):
        """访问登录页"""
        result = TestResult('TC-ROUTE-003', 'test_login_page', '路由', 'Medium')
        result.expected_result = '返回登录表单 HTML'
        
        try:
            response = client.get('/login')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '登录' in html_content
            assert '用户名' in html_content
            assert '密码' in html_content
            
            result.status = 'PASS'
            result.actual_result = "登录页访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-004', priority='Medium', expected='注册页正常访问')
    def test_register_page(self, client):
        """访问注册页"""
        result = TestResult('TC-ROUTE-004', 'test_register_page', '路由', 'Medium')
        result.expected_result = '返回注册表单 HTML'
        
        try:
            response = client.get('/register')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '注册' in html_content
            
            result.status = 'PASS'
            result.actual_result = "注册页访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-005', priority='High', expected='品种管理页需要权限')
    def test_admin_breeds_page_requires_auth(self, client):
        """品种管理页面 - 未登录"""
        result = TestResult('TC-ROUTE-005', 'test_admin_page_auth', '路由', 'High')
        result.expected_result = '重定向到登录页'
        
        try:
            response = client.get('/admin/breeds', follow_redirects=False)
            assert response.status_code == 302  # 重定向
            
            result.status = 'PASS'
            result.actual_result = f"未登录被重定向，状态码：{response.status_code}"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-006', priority='Medium', expected='价格散点图页正常访问')
    def test_scatter_chart_page(self, client):
        """价格散点图页面"""
        result = TestResult('TC-ROUTE-006', 'test_scatter_page', '路由', 'Medium')
        result.expected_result = '返回包含图表的 HTML'
        
        try:
            response = client.get('/chart/scatter')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '价格散点图' in html_content
            
            result.status = 'PASS'
            result.actual_result = "散点图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-007', priority='Medium', expected='体重折线图页正常访问')
    def test_line_chart_page(self, client):
        """体重折线图页面"""
        result = TestResult('TC-ROUTE-007', 'test_line_page', '路由', 'Medium')
        result.expected_result = '返回包含图表的 HTML'
        
        try:
            response = client.get('/chart/line')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '体重折线图' in html_content
            
            result.status = 'PASS'
            result.actual_result = "折线图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-008', priority='Medium', expected='级别柱状图页正常访问')
    def test_bar_chart_page(self, client):
        """级别柱状图页面"""
        result = TestResult('TC-ROUTE-008', 'test_bar_page', '路由', 'Medium')
        result.expected_result = '返回包含图表的 HTML'
        
        try:
            response = client.get('/chart/bar')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '级别柱状图' in html_content
            
            result.status = 'PASS'
            result.actual_result = "柱状图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-009', priority='Medium', expected='TOP10 直方图页正常访问')
    def test_hist_chart_page(self, client):
        """TOP10 直方图页面"""
        result = TestResult('TC-ROUTE-009', 'test_hist_page', '路由', 'Medium')
        result.expected_result = '返回包含图表的 HTML'
        
        try:
            response = client.get('/chart/hist')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert 'TOP10' in html_content or '直方图' in html_content
            
            result.status = 'PASS'
            result.actual_result = "直方图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-010', priority='Medium', expected='价格段漏斗图页正常访问')
    def test_funnel_chart_page(self, client):
        """价格段漏斗图页面"""
        result = TestResult('TC-ROUTE-010', 'test_funnel_page', '路由', 'Medium')
        result.expected_result = '返回包含图表的 HTML'
        
        try:
            response = client.get('/chart/funnel')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '漏斗图' in html_content
            
            result.status = 'PASS'
            result.actual_result = "漏斗图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-011', priority='Medium', expected='世界地图页正常访问')
    def test_map_chart_page(self, client):
        """世界地图页面"""
        result = TestResult('TC-ROUTE-011', 'test_map_page', '路由', 'Medium')
        result.expected_result = '返回包含地图的 HTML'
        
        try:
            response = client.get('/chart/map')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '地图' in html_content or 'Map' in html_content
            
            result.status = 'PASS'
            result.actual_result = "地图页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-012', priority='Low', expected='测试宠物页面正常访问')
    def test_test_pet_page(self, client):
        """测试宠物页面"""
        result = TestResult('TC-ROUTE-012', 'test_test_pet_page', '路由', 'Low')
        result.expected_result = '返回测试页面 HTML'
        
        try:
            response = client.get('/test-pet')
            assert response.status_code == 200
            
            result.status = 'PASS'
            result.actual_result = "测试宠物页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-ROUTE-013', priority='Low', expected='清除缓存页面正常访问')
    def test_clear_cache_page(self, client):
        """清除缓存指南页面"""
        result = TestResult('TC-ROUTE-013', 'test_clear_cache_page', '路由', 'Low')
        result.expected_result = '返回指南页面 HTML'
        
        try:
            response = client.get('/clear-cache')
            assert response.status_code == 200
            html_content = response.data.decode('utf-8', errors='ignore')
            assert '缓存' in html_content
            
            result.status = 'PASS'
            result.actual_result = "清除缓存页面访问正常"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestRedirects:
    """重定向逻辑测试"""
    
    @test_case('TC-REDIRECT-001', priority='Medium', expected='登录后重定向到首页')
    def test_redirect_after_login(self, client, db, session):
        """登录成功后重定向"""
        result = TestResult('TC-REDIRECT-001', 'test_login_redirect', '重定向', 'Medium')
        result.expected_result = '重定向到首页'
        
        try:
            from models import User
            user = User(username='TEST_redirect_test')
            user.set_password('123456')
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/login', data={
                'username': 'TEST_redirect_test',
                'password': '123456'
            }, follow_redirects=False)
            
            # 应该重定向
            assert response.status_code == 302
            
            result.status = 'PASS'
            result.actual_result = "登录成功重定向"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-REDIRECT-002', priority='Medium', expected='登出后重定向到首页')
    def test_redirect_after_logout(self, logged_in_client):
        """登出后重定向"""
        result = TestResult('TC-REDIRECT-002', 'test_logout_redirect', '重定向', 'Medium')
        result.expected_result = '重定向到首页'
        
        try:
            response = logged_in_client.get('/logout', follow_redirects=False)
            assert response.status_code == 302
            
            result.status = 'PASS'
            result.actual_result = "登出成功重定向"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
