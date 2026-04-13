"""
密码强度验证测试
测试密码必须为至少6位的要求
"""
import pytest
from models import User, db


class TestPasswordValidation:
    """密码验证测试类"""
    
    def test_password_too_short(self):
        """测试：密码长度不足6位应失败"""
        user = User(username='test_user')
        
        with pytest.raises(ValueError) as exc_info:
            user.set_password('12345')
        
        assert '密码长度至少 6 位' in str(exc_info.value)
    
    def test_password_exactly_6_chars(self):
        """测试：正好6位密码应成功"""
        user = User(username='test_user')
        
        # 应该不抛出异常
        user.set_password('abc123')
        
        # 验证密码已设置
        assert user.password_hash is not None
        assert len(user.password_hash) > 0
    
    def test_password_more_than_6_chars(self):
        """测试：超过6位密码应成功"""
        user = User(username='test_user')
        
        # 应该不抛出异常
        user.set_password('Test@123!')
        
        # 验证密码已设置
        assert user.password_hash is not None
    
    def test_password_with_letters_and_numbers(self):
        """测试：字母数字混合密码应成功"""
        user = User(username='test_user')
        
        # 应该不抛出异常
        user.set_password('Password123')
        
        assert user.password_hash is not None
    
    def test_password_with_special_chars(self):
        """测试：包含特殊字符的密码应成功"""
        user = User(username='test_user')
        
        # 应该不抛出异常
        user.set_password('Test@123!')
        
        assert user.password_hash is not None
    
    def test_password_all_digits(self):
        """测试：纯数字密码应成功"""
        user = User(username='test_user')
        
        # 应该不抛出异常
        user.set_password('123456')
        
        assert user.password_hash is not None
    
    def test_password_empty(self):
        """测试：空密码应失败"""
        user = User(username='test_user')
        
        with pytest.raises(ValueError) as exc_info:
            user.set_password('')
        
        assert '密码长度至少 6 位' in str(exc_info.value)
    
    def test_password_check_works(self):
        """测试：密码验证功能正常"""
        user = User(username='test_user')
        user.set_password('TestPass123')
        
        # 正确密码应返回 True
        assert user.check_password('TestPass123') is True
        
        # 错误密码应返回 False
        assert user.check_password('WrongPass') is False
    
    def test_password_different_users(self):
        """测试：不同用户的密码哈希不同"""
        user1 = User(username='user1')
        user2 = User(username='user2')
        
        user1.set_password('SamePass123')
        user2.set_password('SamePass123')
        
        # 即使密码相同，哈希值也应不同（因为盐值不同）
        assert user1.password_hash != user2.password_hash
        
        # 但都能正确验证
        assert user1.check_password('SamePass123') is True
        assert user2.check_password('SamePass123') is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
