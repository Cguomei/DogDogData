"""
测试数据库初始化工具
从 CSV 文件导入测试数据到测试数据库
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import DogBreed


def init_test_database_from_csv(csv_path=None):
    """从 CSV 文件初始化测试数据库"""

    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(__file__), "reports_archive", "test_dogs.csv"
        )

    print(f"📂 读取 CSV 文件: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"❌ CSV 文件不存在: {csv_path}")
        return False

    try:
        # 读取 CSV
        df = pd.read_csv(csv_path, encoding="utf-8")
        print(f"✅ 成功读取 {len(df)} 条记录")
        print(f"   列名: {df.columns.tolist()}")

        with app.app_context():
            # 清空现有测试数据（使用 DELETE FROM 避免外键问题）
            print("\n🗑️  清空现有测试数据...")
            from sqlalchemy import text

            db.session.execute(text("DELETE FROM dog_breeds"))
            db.session.commit()

            # 导入新数据（去重处理）
            print("📥 导入数据到数据库...")
            success_count = 0
            fail_count = 0
            duplicate_count = 0
            seen_breeds = set()  # 用于检测重复

            for index, row in df.iterrows():
                try:
                    breed_name = str(row["品种名"]).strip()

                    # 跳过空值或无效数据
                    if not breed_name or breed_name == "nan":
                        fail_count += 1
                        continue

                    # 检查是否重复
                    if breed_name in seen_breeds:
                        duplicate_count += 1
                        continue

                    seen_breeds.add(breed_name)

                    # 处理平均寿命字段（可能是"未知"等非数字）
                    avg_life = row["平均寿命"]
                    try:
                        avg_life_years = (
                            float(avg_life)
                            if pd.notna(avg_life) and str(avg_life) != "未知"
                            else 12.0
                        )
                    except (ValueError, TypeError):
                        avg_life_years = 12.0  # 默认值

                    breed = DogBreed(
                        breed_name=breed_name,
                        avg_life_years=avg_life_years,
                        size_category=str(row["体型"]),
                        popularity=int(row["人气值"]),
                    )
                    db.session.add(breed)
                    success_count += 1

                    if (index + 1) % 50 == 0:
                        print(f"   已处理 {index + 1}/{len(df)} 条记录")

                except Exception as e:
                    print(f"   ⚠️  第{index+1}条记录失败: {e}")
                    fail_count += 1

            db.session.commit()

            print(f"\n✅ 导入完成!")
            print(f"   成功: {success_count} 条")
            print(f"   重复跳过: {duplicate_count} 条")
            print(f"   失败: {fail_count} 条")

            # 验证数据
            total = DogBreed.query.count()
            print(f"   数据库中总计: {total} 条记录")

            return True

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("测试数据库初始化工具")
    print("=" * 70)

    # 检查是否使用测试数据库
    test_db_name = os.getenv("TEST_DB_NAME", "dog_test")
    db_uri = os.getenv("DATABASE_URI", "")

    print(f"\n⚙️  当前配置:")
    print(f"   测试数据库名: {test_db_name}")
    print(
        f"   数据库URI: {db_uri[:50]}..."
        if len(db_uri) > 50
        else f"   数据库URI: {db_uri}"
    )

    confirm = input("\n⚠️  这将清空测试数据库中的所有数据，是否继续? (y/n): ")

    if confirm.lower() == "y":
        success = init_test_database_from_csv()
        if success:
            print("\n✅ 测试数据库初始化成功!")
        else:
            print("\n❌ 测试数据库初始化失败!")
            sys.exit(1)
    else:
        print("\n❌ 操作已取消")
