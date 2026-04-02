import os
import pytest
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（用于数据库密码等）
load_dotenv()

try:
    from app import app as flask_app
    from app import db as _db
    from models import User
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
except ImportError as e:
    # 如果导入失败，提供更友好的错误信息
    print(f"导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    raise

@pytest.fixture(scope='session')
def app():
    """创建测试用的 Flask 应用实例，使用独立的测试数据库配置。"""
    # 从环境变量读取数据库配置，但可以指定一个测试数据库（例如 dog_test）
    # 如果不想创建测试数据库，可以保留原库，但下面的事务回滚机制会保证数据不被污染
    test_db_name = os.getenv('TEST_DB_NAME', 'dog_test')  # 建议新建一个测试库
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '123456')}@{os.getenv('DB_HOST', 'localhost')}/{test_db_name}",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        # 如果你不想新建库，可以注释掉上面两行，使用原库但依赖事务回滚
    })
    yield flask_app

@pytest.fixture
def client(app):
    """提供测试客户端，模拟请求。"""
    return app.test_client()

# 后续如果需要，可以添加更多 fixture，如数据库会话、模拟数据等
# 如果你之后要测前端，可以在这加上 Selenium 的 fixture [citation:8]
# 如果安装了 pytest-selenium-driver，可以直接在测试函数中使用 'driver' 参数

@pytest.fixture(scope='session')
def db(app):
    """提供数据库对象，并在测试会话开始时创建所有表，结束后删除。"""
    with app.app_context():
        _db.create_all()  # 创建表（如果使用测试库）
    yield _db
    # 不再 drop_all，避免外键约束问题
    # 测试数据通过 session fixture 的事务回滚自动清理

@pytest.fixture(scope='function')
def session(db, request):
    """为每个测试函数创建一个独立的事务，测试结束后回滚，保证数据隔离。"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # 使用 Flask-SQLAlchemy 3.x 的兼容方式
    options = dict(bind=connection)
    session = db._make_scoped_session(options=options)
    
    # 用 session 替换全局 db.session
    db.session = session
    
    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()
    
    request.addfinalizer(teardown)
    return session

@pytest.fixture
def runner(app):
    """提供测试 CLI 运行器。"""
    return app.test_cli_runner()

@pytest.fixture(scope='session', autouse=True)
def create_test_users(app, db):
    """在测试会话开始前创建两个测试用户：普通用户 user/123456，管理员 admin/123456。"""
    with app.app_context():
        # 如果用户已存在则跳过（适用于多次运行测试）
        if not User.query.filter_by(username='user').first():
            # noinspection PyArgumentList
            user = User(username='user')
            user.set_password('123456')  # 至少 6 位
            db.session.add(user)
        if not User.query.filter_by(username='admin').first():
            # noinspection PyArgumentList
            # 编辑器忽略此行检查
            admin = User(username='admin', role='admin')
            admin.set_password('123456')
            db.session.add(admin)
        db.session.commit()

@pytest.fixture
def login_user(client):
    """返回一个函数，用于登录指定用户，并返回是否成功。"""
    def _login(username, password):
        return client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    return _login

@pytest.fixture
def logged_in_client(client, login_user):
    """返回一个已经以普通用户身份登录的客户端。"""
    login_user('user', '123456')
    return client

@pytest.fixture
def admin_client(client, login_user):
    """返回一个已经以管理员身份登录的客户端。"""
    login_user('admin', '123456')
    return client
