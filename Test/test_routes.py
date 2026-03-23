import pytest

# 最简单的“冒烟测试”，确保首页能打开
def test_index_page(client):
    """测试首页是否能正常访问。"""
    response = client.get('/')  # 模拟 GET 请求访问根路径
    assert response.status_code == 200  # 断言返回的状态码是 200
    # 可选：断言页面内容包含某些关键词，注意要用字节串
    # assert b"Welcome" in response.data

# 测试 /api/breeds 返回 JSON 数据是否正确
def test_get_breeds_api(client):
    response = client.get('/api/breeds')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    if data:
        assert 'breed_name' in data[0]


# 测试公开路由和登录保护的路由
def test_map_page(client):
    """地图页面应返回 200。"""
    response = client.get('/map')
    assert response.status_code == 200

def test_food_dashboard(client):
    """狗粮看板页面应返回 200。"""
    response = client.get('/food')
    assert response.status_code == 200

@pytest.mark.parametrize('endpoint', [
    '/chart/scatter',
    '/chart/line',
    '/chart/bar',
    '/chart/hist',
    '/chart/funnel',
    '/chart/map',
])
def test_chart_pages(client, endpoint):
    """所有图表页面应返回 200。"""
    response = client.get(endpoint)
    assert response.status_code == 200
    # 可选：检查响应是否包含 ECharts 容器
    assert b'chart-container' in response.data or b'echarts' in response.data

def test_admin_breeds_redirects_if_not_logged_in(client):
    """未登录访问 /admin/breeds 应重定向到登录页。"""
    response = client.get('/admin/breeds')
    assert response.status_code == 302
    assert '/login' in response.location

def test_admin_breeds_with_user(logged_in_client):
    """普通用户访问 /admin/breeds 应被拒绝（403 或重定向）。"""
    response = logged_in_client.get('/admin/breeds')
    # 根据你的实现，可能是 302 重定向到首页，或者 403
    assert response.status_code in (302, 403)
    if response.status_code == 302:
        assert response.location == '/' or 'index' in response.location

def test_admin_breeds_with_admin(admin_client):
    """管理员访问 /admin/breeds 应返回 200。普通用户访问 /admin/breeds 应被拒绝（403 或重定向）。"""
    response = admin_client.get('/admin/breeds')
    assert response.status_code == 200
    # assert b'品种管理' in response.data or b'admin_breeds' in response.data
    assert '品种管理' in response.get_data(as_text=True) or 'admin_breeds' in response.get_data(as_text=True)

    # 根据你的实现，可能是 302 重定向到首页，或者 403
    assert response.status_code in (302, 403)
    if response.status_code == 302:
        assert response.location == '/' or 'index' in response.location

def test_login_page_get(client):
    """GET /login 应返回登录表单。"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'password' in response.data

def test_login_success(client, login_user):
    """使用正确凭证登录应成功并重定向。"""
    response = login_user('user', '123')
    assert response.status_code == 200  # 因为 follow_redirects=True
    # assert b'登录成功' in response.data or b'index' in response.data
    assert '登录成功' in response.get_data(as_text=True) or 'admin_breeds' in response.get_data(as_text=True)

def test_login_fail(client, login_user):
    """使用错误密码登录应失败。"""
    response = login_user('user', 'wrongpass')
    assert '用户名或密码错误' in response.get_data(as_text=True)

def test_logout(logged_in_client):
    """登出后应重定向到首页。"""
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert '已登出' in response.get_data(as_text=True)
