"""
测试数据管理工具
提供唯一的测试数据生成和清理功能
"""

import time
import random
from datetime import datetime


class TestDataGenerator:
    """测试数据生成器 - 确保数据唯一性"""

    def __init__(self):
        self.timestamp = int(time.time())
        self.random_suffix = random.randint(1000, 9999)

    def generate_unique_username(self, base_name="test_user"):
        """生成唯一的用户名"""
        return f"{base_name}_{self.timestamp}_{self.random_suffix}"

    def generate_unique_breed_name(self, base_name="测试犬种"):
        """生成唯一的品种名称"""
        return f"{base_name}_{self.timestamp}_{self.random_suffix}"

    def generate_test_user_data(self, username=None):
        """生成测试用户数据"""
        if username is None:
            username = self.generate_unique_username()

        return {"username": username, "password": "TestPass123!", "role": "user"}

    def generate_test_admin_data(self, username=None):
        """生成测试管理员数据"""
        if username is None:
            username = self.generate_unique_username("admin")

        return {"username": username, "password": "AdminPass456!", "role": "admin"}

    def generate_test_breed_data(self, breed_name=None):
        """生成测试品种数据"""
        if breed_name is None:
            breed_name = self.generate_unique_breed_name()

        sizes = ["小型", "中型", "大型"]

        return {
            "breed_name": breed_name,
            "avg_life_years": round(random.uniform(8.0, 16.0), 1),
            "size_category": random.choice(sizes),
            "popularity": random.randint(50, 200),
        }

    def generate_multiple_breeds(self, count=5):
        """生成多个测试品种"""
        breeds = []
        for i in range(count):
            breed_name = self.generate_unique_breed_name(f"品种{i+1}")
            breeds.append(self.generate_test_breed_data(breed_name))
        return breeds


class TestDatabaseCleaner:
    """测试数据库清理器"""

    @staticmethod
    def cleanup_test_users(db, username_pattern="test_"):
        """清理测试用户"""
        from models import User

        test_users = User.query.filter(User.username.like(f"{username_pattern}%")).all()
        for user in test_users:
            db.session.delete(user)
        db.session.commit()
        return len(test_users)

    @staticmethod
    def cleanup_test_breeds(db, breed_name_pattern="测试犬种"):
        """清理测试品种"""
        from models import DogBreed

        test_breeds = DogBreed.query.filter(
            DogBreed.breed_name.like(f"{breed_name_pattern}%")
        ).all()
        for breed in test_breeds:
            db.session.delete(breed)
        db.session.commit()
        return len(test_breeds)

    @staticmethod
    def cleanup_all_test_data(db):
        """清理所有测试数据"""
        users_cleaned = TestDatabaseCleaner.cleanup_test_users(db)
        breeds_cleaned = TestDatabaseCleaner.cleanup_test_breeds(db)
        return {"users_deleted": users_cleaned, "breeds_deleted": breeds_cleaned}


# 全局实例
test_data_gen = TestDataGenerator()
test_db_cleaner = TestDatabaseCleaner()
