"""测试数据工厂：快速创建数据库记录。"""

from uuid import uuid4
from models import User, DogBreed


def _unique(prefix="TEST"):
    return f"{prefix}_{uuid4().hex[:8]}"


def make_user(db, username=None, password="test123", role="user"):
    """创建测试用户（自动提交）。"""
    user = User(username=username or _unique("TU"))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def make_admin(db, username=None, password="test123"):
    """创建管理员用户。"""
    return make_user(db, username=username, role="admin", password=password)


def make_breed(
    db, breed_name=None, avg_life_years=12.0, size_category="中型", popularity=50
):
    """创建测试品种。"""
    breed = DogBreed(
        breed_name=breed_name or _unique("BREED"),
        avg_life_years=avg_life_years,
        size_category=size_category,
        popularity=popularity,
    )
    db.session.add(breed)
    db.session.commit()
    return breed
