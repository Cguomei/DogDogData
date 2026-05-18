"""
数据库初始化脚本
用于创建数据库、用户和初始数据
"""

import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# 从环境变量读取配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "dog")


def create_database():
    """创建数据库和用户"""
    print("正在连接 MySQL...")

    try:
        # 连接到 MySQL（不需要指定数据库）
        connection = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, charset="utf8mb4"
        )

        cursor = connection.cursor()

        # 创建数据库
        print(f"创建数据库 {DB_NAME}...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )

        # 创建用户并授权（如果使用的是 root 用户，可以跳过这一步）
        new_user = "doguser"
        new_password = "123456"

        print(f"创建用户 {new_user}...")
        try:
            cursor.execute(
                f"CREATE USER IF NOT EXISTS '{new_user}'@'%' IDENTIFIED BY '{new_password}'"
            )
            cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{new_user}'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            print(f"用户 {new_user} 创建成功并已授权")
        except Exception as e:
            print(f"创建用户时出错（可能已存在）: {e}")

        cursor.close()
        connection.close()

        print("数据库创建完成！")

    except pymysql.Error as e:
        print(f"MySQL 错误：{e}")
        return False

    return True


def init_tables():
    """初始化数据表"""
    print("\n正在初始化数据表...")

    try:
        # 使用新的数据库配置
        db_user = os.getenv("DB_USER", "doguser")
        db_password = os.getenv("DB_PASSWORD", "123456")

        connection = pymysql.connect(
            host=DB_HOST,
            user=db_user,
            password=db_password,
            database=DB_NAME,
            charset="utf8mb4",
        )

        cursor = connection.cursor()

        # 创建 users 表
        print("创建 users 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 创建 dog_breeds 表
        print("创建 dog_breeds 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dog_breeds (
                id INT AUTO_INCREMENT PRIMARY KEY,
                breed_name VARCHAR(100) UNIQUE NOT NULL,
                avg_life_years DECIMAL(3,1),
                size_category ENUM('小型', '中型', '大型', '超大型'),
                popularity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 创建 dashboard_summary 表
        print("创建 dashboard_summary 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_summary (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stat_key VARCHAR(100) UNIQUE NOT NULL,
                stat_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 创建 dog_food_data 表
        print("创建 dog_food_data 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dog_food_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                brand VARCHAR(100),
                product_name VARCHAR(200),
                price DECIMAL(10,2),
                weight VARCHAR(50),
                level VARCHAR(50),
                shop_name VARCHAR(100),
                origin VARCHAR(100),
                ingredient_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 创建扩展表（来自 models_extended.py）
        print("创建 user_profiles 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                nickname VARCHAR(80),
                avatar_url VARCHAR(255),
                gender ENUM('男', '女', '保密') DEFAULT '保密',
                phone VARCHAR(20),
                email VARCHAR(120),
                bio TEXT,
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        print("创建 app_tokens 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                access_token VARCHAR(500) UNIQUE NOT NULL,
                refresh_token VARCHAR(500) UNIQUE NOT NULL,
                device_id VARCHAR(100),
                device_name VARCHAR(100),
                app_version VARCHAR(20),
                platform VARCHAR(20),
                expires_at DATETIME NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_access_token (access_token),
                INDEX idx_refresh_token (refresh_token)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        print("创建 user_favorites 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                breed_id INT NOT NULL,
                note VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_breed (user_id, breed_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (breed_id) REFERENCES dog_breeds(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        print("创建 user_activity_logs 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action_type VARCHAR(50) NOT NULL,
                target_type VARCHAR(50),
                target_id INT,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                request_method VARCHAR(10),
                status_code INT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_action (user_id, action_type),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 插入默认数据
        print("\n插入默认数据...")

        # 默认管理员账户
        from werkzeug.security import generate_password_hash

        admin_pwd = generate_password_hash("admin123")

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE username=username
        """,
            ("admin", admin_pwd, "admin"),
        )

        # 默认测试账户
        test_pwd = generate_password_hash("test123")
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE username=username
        """,
            ("test", test_pwd, "user"),
        )

        # 示例狗狗品种数据
        sample_breeds = [
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

        for breed in sample_breeds:
            cursor.execute(
                """
                INSERT INTO dog_breeds (breed_name, avg_life_years, size_category, popularity)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE breed_name=breed_name
            """,
                breed,
            )

        connection.commit()

        print("\n✅ 数据库初始化完成！")
        print("\n默认账户:")
        print("  管理员：admin / admin123")
        print("  测试用户：test / test123")
        print(f"\n数据库信息:")
        print(f"  主机：{DB_HOST}")
        print(f"  数据库名：{DB_NAME}")
        print(f"  用户：doguser / 123456")

        cursor.close()
        connection.close()

    except pymysql.Error as e:
        print(f"MySQL 错误：{e}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)

    if create_database():
        if init_tables():
            print("\n🎉 所有操作完成！")
        else:
            print("\n❌ 初始化表失败")
    else:
        print("\n❌ 创建数据库失败")
