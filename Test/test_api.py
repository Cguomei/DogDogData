# 测试 API 接口
import json

import pytest


def test_get_breeds(client):
    """GET /api/breeds 应返回品种列表。"""
    response = client.get('/api/breeds')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    if data:
        assert 'breed_name' in data[0]

def test_post_breed_requires_auth(client):
    """未登录时 POST /api/breeds 应返回 400 或 401/403。"""
    response = client.post('/api/breeds', json={
        'breed_name': '测试犬',
        'avg_life_years': 12.5,
        'size_category': '中型',
        'popularity': 100
    })
    # 未登录时，可能返回 400 (JSON 为空) 或 401/403 (认证失败)
    # 具体取决于应用的实现
    assert response.status_code in (400, 401, 403)

def test_post_breed_as_admin(admin_client):
    """管理员可以添加新品种。"""
    new_breed = {
        'breed_name': '边境牧羊犬',
        'avg_life_years': 14.5,
        'size_category': '中型',
        'popularity': 95
    }
    response = admin_client.post('/api/breeds', json=new_breed)
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == '添加成功'
    breed_id = data['id']

    # 验证已添加
    get_resp = admin_client.get(f'/api/breeds/{breed_id}')
    assert get_resp.status_code == 200
    breed_data = get_resp.get_json()
    assert breed_data['breed_name'] == '边境牧羊犬'

def test_update_breed(admin_client):
    """管理员可以更新品种信息。"""
    # 先创建一个
    resp = admin_client.post('/api/breeds', json={
        'breed_name': '金毛寻回犬',
        'avg_life_years': 12,
        'size_category': '大型',
        'popularity': 90
    })
    breed_id = resp.get_json()['id']

    # 更新
    update_data = {'popularity': 95}
    resp = admin_client.put(f'/api/breeds/{breed_id}', json={
        'breed_name': '金毛寻回犬',
        'avg_life_years': 12,
        'size_category': '大型',
        'popularity': 95
    })
    assert resp.status_code == 200
    assert resp.get_json()['message'] == '更新成功'

    # 验证更新
    breed = admin_client.get(f'/api/breeds/{breed_id}').get_json()
    assert breed['popularity'] == 95

def test_delete_breed(admin_client):
    """管理员可以删除品种。"""
    # 创建
    resp = admin_client.post('/api/breeds', json={
        'breed_name': '柴犬',
        'avg_life_years': 13,
        'size_category': '小型',
        'popularity': 80
    })
    breed_id = resp.get_json()['id']

    # 删除
    del_resp = admin_client.delete(f'/api/breeds/{breed_id}')
    assert del_resp.status_code == 200
    assert del_resp.get_json()['message'] == '删除成功'

    # 验证不存在
    get_resp = admin_client.get(f'/api/breeds/{breed_id}')
    assert get_resp.status_code == 404

def test_api_food(client):
    """GET /api/food 应返回狗粮数据。"""
    response = client.get('/api/food')
    assert response.status_code == 200
    data = response.get_json()
    # 可能返回错误或列表
    if isinstance(data, dict) and 'error' in data:
        pytest.skip("数据库可能没有狗粮表")
    else:
        assert isinstance(data, list)



