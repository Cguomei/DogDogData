"""
数据模型测试用例
测试数据库模型的完整性约束、验证逻辑等
"""
import pytest
from Test.test_framework import test_case, test_manager, TestResult
from models import User, DogBreed


class TestUserModel:
    """用户模型测试类"""
    
    @test_case('TC-MODEL-USER-001', priority='High', expected='密码正确加密')
    def test_password_hashing(self, app, db, session):
        """测试密码加密"""
        result = TestResult('TC-MODEL-USER-001', 'test_password_hash', '模型 - 用户', 'High')
        result.expected_result = '密码被哈希加密存储'

        try:
            with app.app_context():
                user = User(username='TEST_password_test')
                user.set_password('plain_password')
                db.session.add(user)
                db.session.commit()
                
                # 验证密码是否被加密
                assert user.password_hash != 'plain_password'
                assert len(user.password_hash) > 20  # 哈希值应该较长
                
                # 验证密码检查
                assert user.check_password('plain_password') == True
                assert user.check_password('wrong_password') == False
                
                result.status = 'PASS'
                result.actual_result = "密码加密正常"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-MODEL-USER-002', priority='High', expected='用户名验证通过')
    def test_username_validation_valid(self, app):
        """测试用户名验证 - 有效输入"""
        result = TestResult('TC-MODEL-USER-002', 'test_username_valid', '模型 - 用户', 'High')
        result.expected_result = '接受有效的用户名'
        
        try:
            valid_usernames = [
                'user123',
                'test_user',
                '张三丰',
                '用户_001',
                'TestUser2026'
            ]
            
            for username in valid_usernames:
                is_valid = User.validate_username(username)
                assert is_valid == True, f"用户名 {username} 应该有效"
            
            result.status = 'PASS'
            result.actual_result = f"所有有效用户名均通过验证"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-MODEL-USER-003', priority='High', expected='拒绝无效用户名')
    def test_username_validation_invalid(self, app):
        """测试用户名验证 - 无效输入"""
        result = TestResult('TC-MODEL-USER-003', 'test_username_invalid', '模型 - 用户', 'High')
        result.expected_result = '拒绝无效的用户名'
        
        try:
            invalid_usernames = [
                'ab',  # 太短
                'a',   # 太短
                'user@name',  # 特殊字符
                'user#name',  # 特殊字符
                'user name',  # 空格
                '用户名!',  # 感叹号
            ]
            
            for username in invalid_usernames:
                is_valid = User.validate_username(username)
                assert is_valid == False, f"用户名 {username} 应该无效"
            
            result.status = 'PASS'
            result.actual_result = "所有无效用户名均被拒绝"
            
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-MODEL-USER-004', priority='Medium', expected='管理员权限判断正确')
    def test_is_admin(self, app, db, session):
        """测试管理员权限判断"""
        result = TestResult('TC-MODEL-USER-004', 'test_is_admin', '模型 - 用户', 'Medium')
        result.expected_result = '正确识别管理员'

        try:
            with app.app_context():
                # 创建普通用户
                user1 = User(username='TEST_normal_user')
                user1.set_password('123456')
                db.session.add(user1)

                # 创建管理员
                user2 = User(username='TEST_admin_user', role='admin')
                user2.set_password('123456')
                db.session.add(user2)
                db.session.commit()
                
                assert user1.is_admin() == False
                assert user2.is_admin() == True
                
                result.status = 'PASS'
                result.actual_result = "管理员权限判断正确"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestDogBreedModel:
    """品种模型测试类"""
    
    @test_case('TC-MODEL-BREED-001', priority='Medium', expected='创建品种成功')
    def test_create_breed(self, app, db, session):
        """创建品种记录"""
        result = TestResult('TC-MODEL-BREED-001', 'test_create_breed', '模型 - 品种', 'Medium')
        result.expected_result = '成功创建品种记录'

        try:
            with app.app_context():
                breed = DogBreed(
                    breed_name='TEST_测试犬种',
                    avg_life_years=12.5,
                    size_category='中型',
                    popularity=80
                )
                db.session.add(breed)
                db.session.commit()
                
                assert breed.id is not None
                assert breed.breed_name == 'TEST_测试犬种'
                assert float(breed.avg_life_years) == 12.5
                
                result.status = 'PASS'
                result.actual_result = f"品种创建成功，ID: {breed.id}"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-MODEL-BREED-002', priority='Low', expected='可选字段可以为空')
    def test_optional_fields_null(self, app, db, session):
        """测试可选字段为空"""
        result = TestResult('TC-MODEL-BREED-002', 'test_breed_null_fields', '模型 - 品种', 'Low')
        result.expected_result = '平均寿命、体型、人气值可以为空'

        try:
            with app.app_context():
                breed = DogBreed(
                    breed_name='TEST_极简犬种'
                    # 其他字段都不填
                )
                db.session.add(breed)
                db.session.commit()
                
                assert breed.avg_life_years is None
                assert breed.size_category is None
                assert breed.popularity == 0  # 默认值
                
                result.status = 'PASS'
                result.actual_result = "可选字段处理正确"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-MODEL-BREED-003', priority='Medium', expected='品种字符串表示正确')
    def test_breed_repr(self, app, db, session):
        """测试品种的字符串表示"""
        result = TestResult('TC-MODEL-BREED-003', 'test_breed_repr', '模型 - 品种', 'Medium')
        result.expected_result = '__repr__返回正确的格式'

        try:
            with app.app_context():
                breed = DogBreed(breed_name='TEST_repr 测试犬')
                db.session.add(breed)
                db.session.commit()
                
                repr_str = repr(breed)
                assert 'repr 测试犬' in repr_str
                assert 'DogBreed' in repr_str
                
                result.status = 'PASS'
                result.actual_result = f"__repr__返回：{repr_str}"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)


class TestDataIntegrity:
    """数据完整性测试"""
    
    @test_case('TC-INTEGRITY-001', priority='High', expected='用户名唯一性约束生效')
    def test_username_uniqueness(self, app, db, session):
        """测试用户名唯一性"""
        result = TestResult('TC-INTEGRITY-001', 'test_username_unique', '数据完整性', 'High')
        result.expected_result = '拒绝重复用户名'

        try:
            with app.app_context():
                from sqlalchemy.exc import IntegrityError

                user1 = User(username='TEST_unique_test')
                user1.set_password('123456')
                db.session.add(user1)
                db.session.commit()
                
                # 尝试创建同名用户
                user2 = User(username='TEST_unique_test')
                user2.set_password('123456')
                db.session.add(user2)
                
                # 应该抛出完整性错误
                with pytest.raises(IntegrityError):
                    db.session.commit()
                
                db.session.rollback()
                
                result.status = 'PASS'
                result.actual_result = "用户名唯一性约束正常工作"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
    
    @test_case('TC-INTEGRITY-002', priority='High', expected='品种名唯一性约束生效')
    def test_breed_name_uniqueness(self, app, db, session):
        """测试品种名唯一性"""
        result = TestResult('TC-INTEGRITY-002', 'test_breed_name_unique', '数据完整性', 'High')
        result.expected_result = '拒绝重复品种名'

        try:
            with app.app_context():
                from sqlalchemy.exc import IntegrityError

                breed1 = DogBreed(breed_name='TEST_唯一测试犬')
                db.session.add(breed1)
                db.session.commit()
                
                # 尝试创建同名品种
                breed2 = DogBreed(breed_name='TEST_唯一测试犬')
                db.session.add(breed2)
                
                # 应该抛出完整性错误
                with pytest.raises(IntegrityError):
                    db.session.commit()
                
                db.session.rollback()
                
                result.status = 'PASS'
                result.actual_result = "品种名唯一性约束正常工作"
                
        except AssertionError as e:
            result.status = 'FAIL'
            result.error_message = str(e)
            raise
        finally:
            test_manager.record_result(result)
