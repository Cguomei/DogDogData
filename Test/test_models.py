# 测试数据库模型
import pytest
from models import User, DogBreed
from sqlalchemy.exc import IntegrityError

def test_user_password_hashing(session):
    """测试用户密码哈希和验证。"""
    # noinspection PyArgumentList
    user = User(username='testuser')
    user.set_password('secret')
    assert user.check_password('secret') is True
    assert user.check_password('wrong') is False

def test_user_unique_username(session):
    """测试用户名唯一约束。"""
    # noinspection PyArgumentList
    user1 = User(username='uniqueuser')
    user1.set_password('password1')  # 设置密码
    # noinspection PyArgumentList
    user2 = User(username='uniqueuser')
    user2.set_password('password2')  # 设置密码
    session.add(user1)
    session.commit()

    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_dog_breed_creation(session):
    """测试创建 DogBreed 记录。"""
    import time
    unique_name = f'拉布拉多_{int(time.time())}'  # 使用时间戳确保唯一性
    
    breed = DogBreed(
        breed_name=unique_name,
        avg_life_years=12.5,
        size_category='大型',
        popularity=100
    )
    session.add(breed)
    session.commit()

    saved = session.query(DogBreed).filter_by(breed_name=unique_name).first()
    assert saved is not None
    # 允许一定范围的浮点数误差
    assert abs(saved.avg_life_years - 12.5) < 0.1
    assert saved.size_category == '大型'
    assert saved.popularity == 100