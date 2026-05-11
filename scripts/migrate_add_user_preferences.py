"""
数据库迁移脚本 - 添加用户偏好表
版本: v4.9.1
日期: 2026-05-11
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from models_extended import UserPreference

def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        print("🔄 开始数据库迁移...")
        
        try:
            # 检查表是否已存在
            inspector = db.inspect(db.engine)
            if 'user_preferences' in inspector.get_table_names():
                print("⚠️  user_preferences 表已存在，跳过创建")
                return
            
            # 创建表
            print("📊 创建 user_preferences 表...")
            UserPreference.__table__.create(db.engine)
            print("✅ user_preferences 表创建成功")
            
            # 为现有用户创建默认偏好
            from models import User
            users = User.query.all()
            print(f"👥 为 {len(users)} 个用户创建默认偏好...")
            
            for user in users:
                if not UserPreference.query.filter_by(user_id=user.id).first():
                    preference = UserPreference(
                        user_id=user.id,
                        preferred_size='all',
                        experience_level='beginner',
                        response_style='concise',
                        auto_save_chat=True,
                        price_alert_enabled=False,
                        new_breed_alert_enabled=False
                    )
                    db.session.add(preference)
            
            db.session.commit()
            print(f"✅ 成功为 {len(users)} 个用户创建默认偏好")
            
            print("\n🎉 数据库迁移完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    migrate()
