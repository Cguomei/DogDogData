"""简单数据库迁移 - 创建user_preferences表"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'doguser',
    'password': '123456',
    'database': 'dog',
    'charset': 'utf8mb4'
}

def create_table():
    """创建用户偏好表"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'user_preferences'")
        if cursor.fetchone():
            print("⚠️  user_preferences 表已存在")
            return
        
        # 创建表
        print("📊 创建 user_preferences 表...")
        cursor.execute("""
            CREATE TABLE user_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                
                -- 宠物偏好
                preferred_breeds TEXT,
                preferred_size VARCHAR(20),
                budget_range VARCHAR(50),
                
                -- 经验水平
                experience_level VARCHAR(20) DEFAULT 'beginner',
                
                -- 用途偏好
                purpose VARCHAR(50),
                
                -- 其他偏好
                max_age INT,
                gender_preference VARCHAR(10),
                
                -- AI助手偏好
                response_style VARCHAR(20) DEFAULT 'concise',
                auto_save_chat BOOLEAN DEFAULT TRUE,
                
                -- 通知偏好
                price_alert_enabled BOOLEAN DEFAULT FALSE,
                new_breed_alert_enabled BOOLEAN DEFAULT FALSE,
                
                -- 时间戳
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        print("✅ user_preferences 表创建成功")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 创建失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    create_table()
    print("\n🎉 迁移完成！")
