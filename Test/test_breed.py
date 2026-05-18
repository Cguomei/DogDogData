"""
品种管理模块测试用例
覆盖 CRUD 操作、权限控制、数据验证等场景
"""

import pytest
import time
from .test_framework import test_case, test_manager, TestResult
from models import DogBreed

# 生成唯一的时间戳后缀
TIMESTAMP = int(time.time())
TEST_PREFIX = "TEST_"


class TestBreedManagement:
    """品种管理测试类"""

    @test_case("TC-BREED-001", priority="High", expected="添加品种成功")
    def test_add_breed_success(self, admin_client, db):
        """添加品种 - 成功场景"""
        result = TestResult(
            "TC-BREED-001", "test_add_breed_success", "品种管理", "High"
        )
        result.expected_result = "成功添加新品种"

        try:
            # 使用时间戳保证唯一性
            unique_breed_name = f"{TEST_PREFIX}哈士奇_{TIMESTAMP}"
            breed_data = {
                "breed_name": unique_breed_name,
                "avg_life_years": 12.5,
                "size_category": "大型",
                "popularity": 85,
            }

            response = admin_client.post("/api/breeds", json=breed_data)

            assert response.status_code == 201
            data = response.get_json()
            assert data["message"] == "添加成功"
            assert "id" in data

            # 验证数据库
            breed = DogBreed.query.get(data["id"])
            assert breed is not None
            assert breed.breed_name == unique_breed_name
            assert float(breed.avg_life_years) == 12.5

            result.status = "PASS"
            result.actual_result = f'添加成功，品种 ID: {data["id"]}'

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-002", priority="High", expected="拒绝重复名称")
    def test_add_breed_duplicate(self, admin_client, db):
        """添加品种 - 重复名称"""
        result = TestResult(
            "TC-BREED-002", "test_add_breed_duplicate", "品种管理", "High"
        )
        result.expected_result = "拒绝重复的品种名"

        try:
            # 先创建一个品种（使用时间戳保证唯一性）
            unique_breed_name = f"{TEST_PREFIX}金毛_{TIMESTAMP}"
            breed = DogBreed(
                breed_name=unique_breed_name,
                avg_life_years=12,
                size_category="大型",
                popularity=90,
            )
            db.session.add(breed)
            db.session.commit()

            # 尝试添加同名品种
            response = admin_client.post(
                "/api/breeds",
                json={
                    "breed_name": unique_breed_name,
                    "avg_life_years": 13,
                    "size_category": "中型",
                    "popularity": 80,
                },
            )

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data

            result.status = "PASS"
            result.actual_result = "正确拒绝重复名称"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-003", priority="Medium", expected="拒绝缺少必填字段")
    def test_add_breed_missing_fields(self, admin_client):
        """添加品种 - 缺少必填字段"""
        result = TestResult(
            "TC-BREED-003", "test_add_breed_missing", "品种管理", "Medium"
        )
        result.expected_result = "拒绝缺少必填字段的请求"

        try:
            # 不填品种名
            response = admin_client.post(
                "/api/breeds",
                json={"avg_life_years": 12, "size_category": "大型", "popularity": 80},
            )

            assert response.status_code == 400

            result.status = "PASS"
            result.actual_result = "正确拒绝缺少必填字段的请求"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-004", priority="Medium", expected="返回品种列表")
    def test_get_breeds_list(self, client, db):
        """获取品种列表"""
        result = TestResult(
            "TC-BREED-004", "test_get_breeds_list", "品种管理", "Medium"
        )
        result.expected_result = "返回 JSON 格式的品种列表"

        try:
            # 添加测试数据（使用时间戳保证唯一性）
            breeds = [
                DogBreed(
                    breed_name=f"{TEST_PREFIX}品种A_{TIMESTAMP}",
                    avg_life_years=10,
                    size_category="小型",
                    popularity=50,
                ),
                DogBreed(
                    breed_name=f"{TEST_PREFIX}品种B_{TIMESTAMP}",
                    avg_life_years=12,
                    size_category="中型",
                    popularity=60,
                ),
                DogBreed(
                    breed_name=f"{TEST_PREFIX}品种C_{TIMESTAMP}",
                    avg_life_years=14,
                    size_category="大型",
                    popularity=70,
                ),
            ]
            for b in breeds:
                db.session.add(b)
            db.session.commit()

            response = client.get("/api/breeds")

            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) >= 3

            # 验证字段
            for breed in data:
                assert "breed_name" in breed
                assert "avg_life_years" in breed
                assert "size_category" in breed
                assert "popularity" in breed

            result.status = "PASS"
            result.actual_result = f"返回 {len(data)} 个品种"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-005", priority="High", expected="更新品种信息成功")
    def test_update_breed(self, admin_client, db):
        """更新品种信息"""
        result = TestResult("TC-BREED-005", "test_update_breed", "品种管理", "High")
        result.expected_result = "更新成功"

        try:
            # 创建测试品种（使用时间戳保证唯一性）
            unique_breed_name = f"{TEST_PREFIX}泰迪_{TIMESTAMP}"
            breed = DogBreed(
                breed_name=unique_breed_name,
                avg_life_years=15,
                size_category="小型",
                popularity=70,
            )
            db.session.add(breed)
            db.session.commit()
            breed_id = breed.id

            # 更新
            response = admin_client.put(
                f"/api/breeds/{breed_id}",
                json={
                    "breed_name": unique_breed_name,
                    "avg_life_years": 16,
                    "size_category": "小型",
                    "popularity": 75,
                },
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["message"] == "更新成功"

            # 验证更新
            updated_breed = DogBreed.query.get(breed_id)
            assert float(updated_breed.avg_life_years) == 16
            assert updated_breed.popularity == 75

            result.status = "PASS"
            result.actual_result = "更新成功，数据已变更"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-006", priority="High", expected="删除品种成功")
    def test_delete_breed(self, admin_client, db):
        """删除品种"""
        result = TestResult("TC-BREED-006", "test_delete_breed", "品种管理", "High")
        result.expected_result = "删除成功"

        try:
            # 创建测试品种
            breed = DogBreed(
                breed_name="临时犬种",
                avg_life_years=10,
                size_category="中型",
                popularity=50,
            )
            db.session.add(breed)
            db.session.commit()
            breed_id = breed.id

            # 删除
            response = admin_client.delete(f"/api/breeds/{breed_id}")

            assert response.status_code == 200
            data = response.get_json()
            assert data["message"] == "删除成功"

            # 验证已删除
            deleted_breed = DogBreed.query.get(breed_id)
            assert deleted_breed is None

            result.status = "PASS"
            result.actual_result = "删除成功，数据库中记录已移除"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-007", priority="High", expected="非管理员拒绝访问")
    def test_non_admin_cannot_add_breed(self, logged_in_client):
        """非管理员添加品种 - 权限控制"""
        result = TestResult("TC-BREED-007", "test_non_admin_add", "品种管理", "High")
        result.expected_result = "普通用户无权限添加品种"

        try:
            response = logged_in_client.post(
                "/api/breeds",
                json={
                    "breed_name": "未授权犬种",
                    "avg_life_years": 10,
                    "size_category": "小型",
                    "popularity": 50,
                },
            )

            # 应该返回 403 或需要更高权限
            assert response.status_code in [403, 401]

            result.status = "PASS"
            result.actual_result = f"正确拦截，状态码：{response.status_code}"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)

    @test_case("TC-BREED-008", priority="Medium", expected="验证品种名称长度")
    def test_breed_name_validation(self, admin_client):
        """品种名称验证"""
        result = TestResult(
            "TC-BREED-008", "test_breed_name_validation", "品种管理", "Medium"
        )
        result.expected_result = "拒绝过短或过长的品种名"

        try:
            # 过短的名称
            response = admin_client.post(
                "/api/breeds",
                json={
                    "breed_name": "A",  # 只有 1 个字符
                    "avg_life_years": 10,
                    "size_category": "小型",
                    "popularity": 50,
                },
            )

            assert response.status_code == 400

            result.status = "PASS"
            result.actual_result = "正确验证品种名称长度"

        except AssertionError as e:
            result.status = "FAIL"
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
