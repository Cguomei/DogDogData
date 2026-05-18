from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'admin' 或 'user'

    def set_password(self, password):
        """设置密码，并进行强度验证

        要求：
        - 至少 6 位
        """
        # 检查长度
        if len(password) < 6:
            raise ValueError("密码长度至少 6 位")

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    @staticmethod
    def validate_username(username):
        """验证用户名是否合法（只允许字母、数字、下划线、中文）"""
        if not username or len(username) < 3 or len(username) > 20:
            return False
        # 允许中文、字母、数字、下划线
        pattern = "^[\u4e00-\u9fa5a-zA-Z0-9_]+$"
        return bool(re.match(pattern, username))


class DogBreed(db.Model):
    __tablename__ = "dog_breeds"
    id = db.Column(db.Integer, primary_key=True)
    breed_name = db.Column(db.String(100), unique=True, nullable=False)
    avg_life_years = db.Column(db.Numeric(3, 1))
    size_category = db.Column(db.Enum("小型", "中型", "大型", "超大型"))
    popularity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<DogBreed {self.breed_name}>"
