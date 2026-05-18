"""
演示数据种子脚本
为演示模式生成默认数据,无需手动配置数据库
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask

# 添加项目根目录到路径
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_demo import DemoConfig
from models import db, User, DogBreed
from models_extended import UserProfile, UserFavorite


def create_app():
    """创建简单的 Flask 应用用于数据初始化"""
    app = Flask(__name__)
    app.config.from_object(DemoConfig)
    db.init_app(app)
    return app


def seed_users():
    """创建默认用户"""
    print("📝 创建默认用户...")

    users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "demo", "password": "demo123", "role": "user"},
        {"username": "test", "password": "test123", "role": "user"},
    ]

    for user_data in users:
        if not User.query.filter_by(username=user_data["username"]).first():
            user = User(username=user_data["username"], role=user_data["role"])
            user.set_password(user_data["password"])
            db.session.add(user)
            print(f"  ✓ 创建用户: {user_data['username']}")

    db.session.commit()


def seed_dog_breeds():
    """创建狗狗品种数据"""
    print("🐕 创建狗狗品种数据...")

    breeds = [
        ("金毛寻回犬", 12.5, "大型", 95),
        ("拉布拉多", 11.5, "大型", 90),
        ("哈士奇", 13.0, "中型", 85),
        ("萨摩耶", 12.0, "中型", 80),
        ("柴犬", 14.5, "小型", 75),
        ("泰迪", 15.0, "小型", 70),
        ("比熊", 14.0, "小型", 65),
        ("边境牧羊犬", 13.5, "中型", 60),
        ("阿拉斯加", 12.0, "超大型", 55),
        ("柯基", 13.0, "小型", 50),
        ("德国牧羊犬", 11.0, "大型", 45),
        ("法国斗牛犬", 11.5, "小型", 40),
        ("博美犬", 15.0, "小型", 35),
        ("雪纳瑞", 14.0, "小型", 30),
        ("巴哥犬", 13.5, "小型", 25),
        ("吉娃娃", 16.0, "小型", 20),
        ("杜宾犬", 11.0, "大型", 18),
        ("罗威纳", 10.5, "大型", 15),
        ("松狮犬", 12.5, "中型", 12),
        ("秋田犬", 12.0, "大型", 10),
    ]

    for breed_data in breeds:
        if not DogBreed.query.filter_by(breed_name=breed_data[0]).first():
            breed = DogBreed(
                breed_name=breed_data[0],
                avg_life_years=breed_data[1],
                size_category=breed_data[2],
                popularity=breed_data[3],
            )
            db.session.add(breed)
            print(f"  ✓ 添加品种: {breed_data[0]}")

    db.session.commit()


def seed_user_profiles():
    """创建用户资料"""
    print("👤 创建用户资料...")

    admin = User.query.filter_by(username="admin").first()
    demo = User.query.filter_by(username="demo").first()

    if admin and not UserProfile.query.filter_by(user_id=admin.id).first():
        profile = UserProfile(
            user_id=admin.id,
            nickname="系统管理员",
            gender="保密",
            email="admin@demo.com",
            bio="这是一个演示账户,用于展示系统管理功能",
            location="北京",
        )
        db.session.add(profile)
        print("  ✓ 创建管理员资料")

    if demo and not UserProfile.query.filter_by(user_id=demo.id).first():
        profile = UserProfile(
            user_id=demo.id,
            nickname="演示用户",
            gender="男",
            email="demo@example.com",
            bio="热爱狗狗的铲屎官,喜欢研究各种犬种",
            location="上海",
        )
        db.session.add(profile)
        print("  ✓ 创建演示用户资料")

    db.session.commit()


def seed_favorites():
    """创建收藏数据"""
    print("⭐ 创建收藏数据...")

    demo_user = User.query.filter_by(username="demo").first()
    if not demo_user:
        return

    favorite_breeds = ["金毛寻回犬", "柴犬", "柯基", "哈士奇"]

    for breed_name in favorite_breeds:
        breed = DogBreed.query.filter_by(breed_name=breed_name).first()
        if (
            breed
            and not UserFavorite.query.filter_by(
                user_id=demo_user.id, breed_id=breed.id
            ).first()
        ):
            favorite = UserFavorite(
                user_id=demo_user.id, breed_id=breed.id, note=f"很喜欢{breed_name}"
            )
            db.session.add(favorite)
            print(f"  ✓ 收藏: {breed_name}")

    db.session.commit()


def seed_dashboard_summary():
    """创建仪表盘汇总数据"""
    print("📊 创建仪表盘数据...")

    from charts import update_dashboard_summary

    try:
        update_dashboard_summary()
        print("  ✓ 更新仪表盘统计数据")
    except Exception as e:
        print(f"  ⚠ 仪表盘数据更新警告: {e}")


def clear_database():
    """清空数据库(谨慎使用)"""
    print("⚠️  清空现有数据...")
    db.drop_all()
    db.create_all()
    print("  ✓ 数据库已重置")


def init_demo_data(clear=False):
    """初始化演示数据"""
    print("=" * 60)
    print("🌟 狗狗数据分析系统 - 演示数据初始化")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()

        # 如果需要,先清空数据库
        if clear:
            clear_database()

        # 检查是否已有数据
        user_count = User.query.count()
        if user_count > 0 and not clear:
            print("\n⚠️  检测到已有数据")
            response = input("是否覆盖现有数据?(y/n): ")
            if response.lower() != "y":
                print("取消操作")
                return

        # 执行数据种子
        seed_users()
        seed_dog_breeds()
        seed_user_profiles()
        seed_favorites()
        seed_dashboard_summary()

        print("\n" + "=" * 60)
        print("✅ 演示数据初始化完成!")
        print("=" * 60)
        print("\n📋 可用账户:")
        print("  👑 管理员: admin / admin123")
        print("  👤 演示用户: demo / demo123")
        print("  🧪 测试用户: test / test123")
        print("\n🎯 下一步:")
        print("  运行: python app.py")
        print("  访问: http://localhost:5000")
        print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="初始化演示数据")
    parser.add_argument("--clear", action="store_true", help="清空现有数据后重新初始化")

    args = parser.parse_args()
    init_demo_data(clear=args.clear)
