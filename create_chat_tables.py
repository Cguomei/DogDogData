"""创建对话历史表"""

import sys

sys.path.insert(0, ".")

from models import db
from app import app
from models_extended import ChatSession, ChatMessage

with app.app_context():
    db.create_all()
    print("Tables created successfully")
