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
    # noinspection PyArgumentList
    user2 = User(username='uniqueuser')
    session.add(user1)
    session.commit()

    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_dog_breed_creation(session):
    """测试创建 DogBreed 记录。"""
    breed = DogBreed(
        breed_name='拉布拉多',
        avg_life_years=12.5,
        size_category='大型',
        popularity=100
    )
    session.add(breed)
    session.commit()

    saved = session.query(DogBreed).filter_by(breed_name='拉布拉多').first()
    assert saved is not None
    assert saved.avg_life_years == 12.5
    assert saved.size_category == '大型'