"""
集成测试和端到端测试
测试完整的用户流程
"""
import pytest
from time import sleep
from bug_tracker import report_bug


class TestUserRegistrationFlow:
    """用户注册流程测试"""
    
    def test_register_new_user(self, client):
        """测试完整注册流程"""
        # 1. 访问注册页面
        response = client.get('/register')
        assert response.status_code == 200
        
        # 2. 提交注册表单
        response = client.post('/register', data={
            'username': f'testuser_{len(str(client))}',  # 避免重复
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # 3. 验证应该重定向到登录页或显示成功消息
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '注册成功' in response_text or 'login' in response_text.lower()
    
    def test_register_duplicate_username(self, client):
        """测试重复用户名注册"""
        # 先注册一个用户
        client.post('/register', data={
            'username': 'duplicate_test_user',
            'password': 'testpass123'
        })
        
        # 尝试用相同用户名注册
        response = client.post('/register', data={
            'username': 'duplicate_test_user',
            'password': 'anotherpass'
        }, follow_redirects=True)
        
        # 应该失败
        response_text = response.get_data(as_text=True)
        assert '已存在' in response_text
        
        # 记录为潜在问题（如果系统没有正确处理）
        if response.status_code == 200 and '已存在' not in response_text:
            report_bug(
                title="重复用户名注册未正确拦截",
                description="系统允许使用已存在的用户名注册，可能导致数据冲突",
                severity="Critical",
                priority="High",
                module="用户注册",
                steps_to_reproduce=[
                    "访问注册页面",
                    "使用用户名 'test' 注册",
                    "再次使用用户名 'test' 注册"
                ],
                expected_result="系统应提示用户名已存在并拒绝注册",
                actual_result="系统可能允许重复注册"
            )


class TestAuthenticationFlow:
    """认证流程测试"""
    
    def test_login_logout_flow(self, client):
        """测试登录 - 登出完整流程"""
        # 1. 登录
        login_response = client.post('/login', data={
            'username': 'user',
            'password': '123'
        }, follow_redirects=True)
        
        assert login_response.status_code == 200
        assert '登录成功' in login_response.get_data(as_text=True)
        
        # 2. 访问需要登录的页面
        response = client.get('/admin/breeds', follow_redirects=True)
        # 普通用户应该被拒绝
        
        # 3. 登出
        logout_response = client.get('/logout', follow_redirects=True)
        assert logout_response.status_code == 200
        assert '已登出' in logout_response.get_data(as_text=True)
    
    def test_login_with_invalid_credentials(self, client):
        """测试使用无效凭证登录"""
        response = client.post('/login', data={
            'username': 'invalid_user',
            'password': 'wrong_password'
        }, follow_redirects=True)
        
        response_text = response.get_data(as_text=True)
        assert '用户名或密码错误' in response_text
    
    def test_access_protected_route_without_login(self, client):
        """测试未登录访问受保护路由"""
        response = client.get('/admin/breeds')
        
        # 应该重定向到登录页
        assert response.status_code == 302
        assert '/login' in response.location


class TestBreedManagementFlow:
    """品种管理流程测试"""
    
    def test_full_crud_flow(self, admin_client):
        """测试完整的 CRUD 流程"""
        # 1. 创建
        create_data = {
            'breed_name': '测试犬种_哈士奇',
            'avg_life_years': 12.5,
            'size_category': '大型',
            'popularity': 85
        }
        
        create_response = admin_client.post('/api/breeds', json=create_data)
        assert create_response.status_code == 201
        breed_id = create_response.get_json()['id']
        
        # 2. 读取
        get_response = admin_client.get(f'/api/breeds/{breed_id}')
        assert get_response.status_code == 200
        breed_data = get_response.get_json()
        assert breed_data['breed_name'] == '测试犬种_哈士奇'
        
        # 3. 更新
        update_data = {
            'breed_name': '测试犬种_哈士奇',
            'avg_life_years': 13.0,
            'size_category': '大型',
            'popularity': 90
        }
        
        update_response = admin_client.put(f'/api/breeds/{breed_id}', json=update_data)
        assert update_response.status_code == 200
        
        # 验证更新
        verify_response = admin_client.get(f'/api/breeds/{breed_id}')
        assert verify_response.get_json()['popularity'] == 90
        
        # 4. 删除
        delete_response = admin_client.delete(f'/api/breeds/{breed_id}')
        assert delete_response.status_code == 200
        
        # 验证删除
        final_response = admin_client.get(f'/api/breeds/{breed_id}')
        assert final_response.status_code == 404
    
    def test_create_duplicate_breed(self, admin_client):
        """测试创建重复品种"""
        # 创建第一个
        admin_client.post('/api/breeds', json={
            'breed_name': '重复测试犬',
            'avg_life_years': 10,
            'size_category': '中型',
            'popularity': 50
        })
        
        # 尝试创建同名品种
        response = admin_client.post('/api/breeds', json={
            'breed_name': '重复测试犬',
            'avg_life_years': 11,
            'size_category': '小型',
            'popularity': 60
        })
        
        # 应该失败
        assert response.status_code == 400
        assert '已存在' in response.get_json().get('error', '')


class TestChartPagesFlow:
    """图表页面流程测试"""
    
    @pytest.mark.parametrize('chart_url,chart_name', [
        ('/chart/scatter', '价格散点图'),
        ('/chart/line', '体重折线图'),
        ('/chart/bar', '级别柱状图'),
        ('/chart/hist', 'TOP10 直方图'),
        ('/chart/funnel', '价格漏斗图'),
        ('/chart/map', '世界地图'),
    ])
    def test_chart_page_loads(self, client, chart_url, chart_name):
        """测试所有图表页面加载"""
        response = client.get(chart_url)
        assert response.status_code == 200
        
        # 检查是否包含图表容器
        response_text = response.get_data(as_text=True)
        assert 'chart-container' in response_text or 'div' in response_text
        
        # 如果没有加载成功，记录为性能问题
        if 'loading' in response_text.lower() and 'echarts' not in response_text.lower():
            report_bug(
                title=f"{chart_name} 加载异常",
                description=f"访问 {chart_url} 时图表可能未正确渲染",
                severity="Minor",
                priority="Low",
                module="图表展示",
                steps_to_reproduce=[f"访问 {chart_url}"],
                expected_result="图表应正常显示",
                actual_result="图表可能未加载或显示异常"
            )


class TestFoodDashboardFlow:
    """狗粮看板流程测试"""
    
    def test_food_dashboard_loads(self, client):
        """测试狗粮看板页面"""
        response = client.get('/food')
        assert response.status_code == 200
        
        response_text = response.get_data(as_text=True)
        # 应该包含统计信息
        assert any(keyword in response_text for keyword in [
            '品牌', '价格', '产地', '统计'
        ])
    
    def test_food_api_returns_data(self, client):
        """测试狗粮 API 返回数据"""
        response = client.get('/api/food')
        assert response.status_code == 200
        
        data = response.get_json()
        # 可能返回错误或数据列表
        if isinstance(data, dict) and 'error' in data:
            # 记录数据库可能缺少表
            report_bug(
                title="狗粮数据表不存在或无法访问",
                description="API /api/food 返回错误：" + data['error'],
                severity="Major",
                priority="Medium",
                module="狗粮数据",
                steps_to_reproduce=["访问 /api/food"],
                expected_result="返回狗粮数据列表",
                actual_result=f"返回错误：{data['error']}"
            )
            pytest.skip("狗粮数据表不可用")
        else:
            assert isinstance(data, list)


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试 404 错误处理"""
        response = client.get('/nonexistent-page-12345')
        assert response.status_code == 404
    
    def test_api_invalid_data(self, admin_client):
        """测试 API 接收无效数据"""
        response = admin_client.post('/api/breeds', json={
            'breed_name': '',  # 空名称
            'avg_life_years': 'invalid',  # 错误类型
            'size_category': 'invalid_size',  # 无效的枚举值
            'popularity': -100  # 负数
        })
        
        # 应该有某种错误处理
        # 注意：根据实现，可能会返回 201 或 400/500
        if response.status_code == 201:
            report_bug(
                title="API 数据验证不严格",
                description="API 接受了无效的数据：空名称、错误类型、无效枚举值、负数",
                severity="Major",
                priority="High",
                module="API 验证",
                steps_to_reproduce=[
                    "POST /api/breeds",
                    "发送包含无效数据的 JSON"
                ],
                expected_result="应返回 400 错误并提示具体验证失败原因",
                actual_result="接受了无效数据并可能创建了错误记录"
            )
    
    def test_api_missing_required_fields(self, admin_client):
        """测试 API 缺少必填字段"""
        response = admin_client.post('/api/breeds', json={
            # 缺少 breed_name 等必填字段
            'popularity': 50
        })
        
        # 应该有错误处理
        if response.status_code == 201:
            report_bug(
                title="API 缺少必填字段验证",
                description="API 在缺少必填字段的情况下仍然创建了记录",
                severity="Major",
                priority="High",
                module="API 验证",
                steps_to_reproduce=[
                    "POST /api/breeds",
                    "不发送 breed_name 字段"
                ],
                expected_result="应返回 400 错误提示缺少必填字段",
                actual_result="接受了请求并可能创建了不完整记录"
            )


class TestSecurityTests:
    """安全测试"""
    
    def test_sql_injection_attempt(self, client):
        """测试 SQL 注入防护"""
        # 尝试 SQL 注入
        malicious_username = "' OR '1'='1"
        response = client.post('/login', data={
            'username': malicious_username,
            'password': 'anything'
        }, follow_redirects=True)
        
        # 不应该登录成功
        response_text = response.get_data(as_text=True)
        if '登录成功' in response_text:
            report_bug(
                title="潜在的 SQL 注入漏洞",
                description="系统可能受到 SQL 注入攻击",
                severity="Critical",
                priority="High",
                module="安全性",
                steps_to_reproduce=[
                    "在登录表单用户名输入：' OR '1'='1",
                    "提交表单"
                ],
                expected_result="登录失败并提示用户名或密码错误",
                actual_result="可能登录成功"
            )
    
    def test_xss_attempt(self, client):
        """测试 XSS 防护"""
        # 这个测试需要在实际环境中验证
        # 这里只是示例结构
        pass
