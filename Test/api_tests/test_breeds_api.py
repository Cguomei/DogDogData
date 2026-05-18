"""
狗狗品种管理 API 测试
涵盖：查询、新增、更新、删除品种的完整 CRUD 操作
"""

import pytest


class TestGetBreeds:
    """获取品种列表和详情测试"""

    def test_get_all_breeds(self, api_client, validator):
        """测试 1: 获取所有品种列表"""
        response = api_client.get("/api/breeds")
        validator.assert_success(response)

        data = response.get_json()
        assert isinstance(data, list), "返回数据应为列表"

        if len(data) > 0:
            validator.validate_breed_data(data[0])

        print(f"✅ 测试 1 通过：获取到 {len(data)} 个品种")

    def test_get_breed_by_id(self, api_client, validator):
        """测试 2: 根据 ID 获取单个品种"""
        # 先获取列表拿到一个有效 ID
        response = api_client.get("/api/breeds")
        breeds = response.get_json()

        if not breeds:
            pytest.skip("数据库中没有品种数据")

        breed_id = breeds[0]["id"]
        response = api_client.get(f"/api/breeds/{breed_id}")
        validator.assert_success(response)

        breed_data = response.get_json()
        validator.validate_breed_data(breed_data)
        assert breed_data["id"] == breed_id

        print(
            f"✅ 测试 2 通过：获取品种 ID={breed_id}, 名称={breed_data['breed_name']}"
        )

    def test_get_nonexistent_breed(self, api_client, validator):
        """测试 3: 获取不存在的品种（应返回 404）"""
        response = api_client.get("/api/breeds/99999")
        validator.assert_error(response, expected_status=404)

        print("✅ 测试 3 通过：不存在的品种返回 404")


class TestAddBreed:
    """新增品种测试"""

    def test_add_breed_without_auth(self, api_client, validator):
        """测试 4: 未登录时添加品种（应拒绝）"""
        new_breed = {
            "breed_name": "测试犬种",
            "avg_life_years": 12.5,
            "size_category": "中型",
            "popularity": 80,
        }
        response = api_client.post("/api/breeds", json=new_breed)
        # Flask 的 @login_required 会返回 302 重定向到登录页
        assert response.status_code in [
            302,
            401,
            403,
        ], f"未登录应返回 302/401/403，实际 {response.status_code}"

        print("✅ 测试 4 通过：未登录用户无法添加品种")

    def test_add_breed_as_normal_user(self, authenticated_api_client, validator):
        """测试 5: 普通用户添加品种（应拒绝 - 需要管理员权限）"""
        new_breed = {
            "breed_name": "测试犬种",
            "avg_life_years": 12.5,
            "size_category": "中型",
            "popularity": 80,
        }
        response = authenticated_api_client.post("/api/breeds", json=new_breed)
        assert (
            response.status_code == 403
        ), f"普通用户应返回 403，实际 {response.status_code}"

        print("✅ 测试 5 通过：普通用户无权限添加品种")

    def test_add_breed_as_admin(self, admin_api_client, validator):
        """测试 6: 管理员成功添加品种"""
        import time

        timestamp = str(int(time.time()))
        new_breed = {
            "breed_name": f"测试犬种_{timestamp}",
            "avg_life_years": 12.5,
            "size_category": "中型",
            "popularity": 80,
        }

        response = admin_api_client.post("/api/breeds", json=new_breed)
        validator.assert_success(response, expected_status=201)

        data = response.get_json()
        assert data["message"] == "添加成功"
        assert "id" in data

        print(f"✅ 测试 6 通过：管理员成功添加品种，ID={data['id']}")
        return data["id"]

    def test_add_breed_with_invalid_data(self, admin_api_client, validator):
        """测试 7: 添加品种 - 无效数据验证"""
        # 品种名称太短
        invalid_breed = {
            "breed_name": "A",
            "avg_life_years": 12.5,
            "size_category": "中型",
            "popularity": 80,
        }
        response = admin_api_client.post("/api/breeds", json=invalid_breed)
        validator.assert_error(response, expected_status=400)

        # 缺少必填字段
        response = admin_api_client.post("/api/breeds", json={})
        validator.assert_error(response, expected_status=400)

        print("✅ 测试 7 通过：无效数据被正确拒绝")

    def test_add_duplicate_breed(self, admin_api_client, validator):
        """测试 8: 添加重复品种名称（应拒绝）"""
        import time

        timestamp = str(int(time.time()))
        breed_name = f"重复测试犬_{timestamp}"

        # 第一次添加
        breed_data = {
            "breed_name": breed_name,
            "avg_life_years": 10,
            "size_category": "小型",
            "popularity": 50,
        }
        response1 = admin_api_client.post("/api/breeds", json=breed_data)
        validator.assert_success(response1, expected_status=201)

        # 第二次添加相同名称
        response2 = admin_api_client.post("/api/breeds", json=breed_data)
        validator.assert_error(response2, expected_status=400)

        print("✅ 测试 8 通过：重复品种名称被拒绝")


class TestUpdateBreed:
    """更新品种测试"""

    def test_update_breed_as_admin(self, admin_api_client, validator):
        """测试 9: 管理员更新品种信息"""
        # 先创建一个品种
        import time

        timestamp = str(int(time.time()))
        create_data = {
            "breed_name": f"待更新犬种_{timestamp}",
            "avg_life_years": 10,
            "size_category": "小型",
            "popularity": 50,
        }
        create_resp = admin_api_client.post("/api/breeds", json=create_data)
        breed_id = create_resp.get_json()["id"]

        # 更新品种
        update_data = {
            "breed_name": f"已更新犬种_{timestamp}",
            "avg_life_years": 15,
            "size_category": "大型",
            "popularity": 95,
        }
        response = admin_api_client.put(f"/api/breeds/{breed_id}", json=update_data)
        validator.assert_success(response)

        # 验证更新结果
        get_resp = admin_api_client.get(f"/api/breeds/{breed_id}")
        updated_breed = get_resp.get_json()
        assert updated_breed["breed_name"] == update_data["breed_name"]
        assert updated_breed["avg_life_years"] == update_data["avg_life_years"]
        assert updated_breed["popularity"] == update_data["popularity"]

        print(f"✅ 测试 9 通过：品种 ID={breed_id} 更新成功")

    def test_update_nonexistent_breed(self, admin_api_client, validator):
        """测试 10: 更新不存在的品种（应返回 404）"""
        update_data = {
            "breed_name": "测试",
            "avg_life_years": 10,
            "size_category": "小型",
            "popularity": 50,
        }
        response = admin_api_client.put("/api/breeds/99999", json=update_data)
        validator.assert_error(response, expected_status=404)

        print("✅ 测试 10 通过：更新不存在的品种返回 404")

    def test_update_breed_without_auth(self, api_client, validator):
        """测试 11: 未登录更新品种（应拒绝）"""
        update_data = {
            "breed_name": "测试",
            "avg_life_years": 10,
            "size_category": "小型",
            "popularity": 50,
        }
        response = api_client.put("/api/breeds/1", json=update_data)
        # Flask 的 @login_required 会返回 302 重定向到登录页
        assert response.status_code in [302, 401, 403]

        print("✅ 测试 11 通过：未登录用户无法更新品种")


class TestDeleteBreed:
    """删除品种测试"""

    def test_delete_breed_as_admin(self, admin_api_client, validator):
        """测试 12: 管理员删除品种"""
        # 先创建一个品种用于删除
        import time

        timestamp = str(int(time.time()))
        breed_data = {
            "breed_name": f"待删除犬种_{timestamp}",
            "avg_life_years": 10,
            "size_category": "小型",
            "popularity": 50,
        }
        create_resp = admin_api_client.post("/api/breeds", json=breed_data)
        breed_id = create_resp.get_json()["id"]

        # 删除品种
        response = admin_api_client.delete(f"/api/breeds/{breed_id}")
        validator.assert_success(response)
        assert response.get_json()["message"] == "删除成功"

        # 验证已删除
        get_resp = admin_api_client.get(f"/api/breeds/{breed_id}")
        validator.assert_error(get_resp, expected_status=404)

        print(f"✅ 测试 12 通过：品种 ID={breed_id} 删除成功")

    def test_delete_nonexistent_breed(self, admin_api_client, validator):
        """测试 13: 删除不存在的品种（应返回 404）"""
        response = admin_api_client.delete("/api/breeds/99999")
        validator.assert_error(response, expected_status=404)

        print("✅ 测试 13 通过：删除不存在的品种返回 404")

    def test_delete_breed_without_auth(self, api_client, validator):
        """测试 14: 未登录删除品种（应拒绝）"""
        response = api_client.delete("/api/breeds/1")
        # Flask 的 @login_required 会返回 302 重定向到登录页
        assert response.status_code in [302, 401, 403]

        print("✅ 测试 14 通过：未登录用户无法删除品种")


# 运行测试
if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",
            "--html=Test/reports/api_breeds_test_report.html",
            "--self-contained-html",
        ]
    )
