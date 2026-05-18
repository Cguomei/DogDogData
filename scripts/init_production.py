"""
生产环境数据库初始化脚本
用于 Railway/Render 等云平台部署时自动初始化数据库
"""

import os
from app import create_app
from models import db, User, DogBreed
from werkzeug.security import generate_password_hash


def init_production_db():
    """初始化生产环境数据库"""
    print("=" * 60)
    print("🚀 生产环境数据库初始化")
    print("=" * 60)

    # 创建生产环境应用
    app = create_app("production")

    with app.app_context():
        try:
            # 创建所有表
            print("\n📝 创建数据表...")
            db.create_all()
            print("✓ 数据表创建成功")

            # 检查是否已有管理员账户
            admin = User.query.filter_by(username="admin").first()
            if not admin:
                print("\n👤 创建管理员账户...")

                # 从环境变量读取密码，默认 admin123
                admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

                admin = User(username="admin", role="admin")
                admin.set_password(admin_password)
                db.session.add(admin)
                print(f"✓ 管理员账户创建成功 (用户名: admin)")

                # 添加示例品种数据
                print("\n🐕 添加示例犬种数据...")
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
                ]

                for name, life, size, pop in breeds:
                    if not DogBreed.query.filter_by(breed_name=name).first():
                        breed = DogBreed(
                            breed_name=name,
                            avg_life_years=life,
                            size_category=size,
                            popularity=pop,
                        )
                        db.session.add(breed)
                        print(f"  ✓ {name}")

                db.session.commit()
                print("\n✅ 示例数据添加成功")
            else:
                print("\n⚠️  检测到已有管理员账户，跳过初始化")

            print("\n" + "=" * 60)
            print("✅ 生产数据库初始化完成！")
            print("=" * 60)
            print(f"\n📋 管理员账户:")
            print(f"  用户名: admin")
            print(f"  密码: {os.getenv('ADMIN_PASSWORD', 'admin123')}")
            print(f"\n💡 提示: 密码至少6位，建议首次登录后修改为更强密码")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            import traceback

            traceback.print_exc()
            raise


if __name__ == "__main__":
    init_production_db()
