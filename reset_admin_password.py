"""
重置admin密码
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User

app = create_app()
app.config['TESTING'] = '1'

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"找到admin用户，ID: {admin.id}")
        admin.set_password('admin123')
        db.session.commit()
        print("✅ 密码已重置为: admin123")
        
        # 验证密码
        if admin.check_password('admin123'):
            print("✅ 密码验证成功")
        else:
            print("❌ 密码验证失败")
    else:
        print("❌ 未找到admin用户")
