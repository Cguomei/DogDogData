"""
添加AI对话历史表的数据库迁移脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db
from app import create_app
from sqlalchemy import text


def upgrade():
    """执行升级"""
    app = create_app()

    with app.app_context():
        print("🔄 开始添加AI对话历史表...")

        # 创建 chat_sessions 表
        print("📝 创建 chat_sessions 表...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200),
                is_active BOOLEAN DEFAULT TRUE,
                message_count INTEGER DEFAULT 0,
                last_message_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_created (user_id, created_at),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))

        # 创建 chat_messages 表
        print("📝 创建 chat_messages 表...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                session_id INTEGER NOT NULL,
                role ENUM('user', 'assistant', 'system') NOT NULL,
                content TEXT NOT NULL,
                question_type VARCHAR(50),
                source VARCHAR(50),
                response_time FLOAT,
                feedback ENUM('like', 'dislike'),
                feedback_comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_created (session_id, created_at),
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))

        db.session.commit()
        print("✅ 数据库迁移完成！")
        print("   - chat_sessions 表已创建")
        print("   - chat_messages 表已创建")


def downgrade():
    """执行回滚"""
    app = create_app()

    with app.app_context():
        print("⚠️  开始回滚...")

        # 删除表（注意顺序）
        db.session.execute(text("DROP TABLE IF EXISTS chat_messages"))
        db.session.execute(text("DROP TABLE IF EXISTS chat_sessions"))

        db.session.commit()
        print("✅ 回滚完成！")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
