import os
import pytest
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（用于数据库密码等）
load_dotenv()

try:
    from app import create_app, db as _db
    from models import User
except ImportError as e:
    # 如果导入失败，提供更友好的错误信息
    print(f"导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    raise


@pytest.fixture(scope="session")
def app():
    """创建测试用的 Flask 应用实例（TestingConfig + 事务回滚隔离）。"""
    flask_app = create_app("testing")
    yield flask_app


@pytest.fixture
def client(app):
    """提供测试客户端，模拟请求。"""
    return app.test_client()


# 后续如果需要，可以添加更多 fixture，如数据库会话、模拟数据等
# 如果你之后要测前端，可以在这加上 Selenium 的 fixture [citation:8]
# 如果安装了 pytest-selenium-driver，可以直接在测试函数中使用 'driver' 参数


@pytest.fixture(scope="session")
def db(app):
    """提供数据库对象，并在测试会话开始时创建所有表，结束后删除。"""
    with app.app_context():
        _db.create_all()  # 创建表（如果使用测试库）
    yield _db
    # 不再 drop_all，避免外键约束问题
    # 测试数据通过 session fixture 的事务回滚自动清理


@pytest.fixture(scope="function", autouse=True)
def _app_context(app):
    """为每个测试函数自动推送应用上下文。"""
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()


@pytest.fixture(scope="function")
def session(db, request):
    """为每个测试函数创建一个独立的事务，测试结束后回滚，保证数据隔离。"""
    connection = db.engine.connect()
    transaction = connection.begin()

    # 使用 Flask-SQLAlchemy 3.x 的兼容方式
    options = dict(bind=connection)
    session = db._make_scoped_session(options=options)

    # 保存原始 db.session，用事务 session 替换
    original_session = db.session
    db.session = session

    def teardown():
        # 清理带有TEST_前缀的测试数据（使用事务 session，此时 db.session 仍指向它）
        try:
            from models import User, DogBreed

            # 删除测试用户
            test_users = User.query.filter(User.username.like("TEST_%")).all()
            for user in test_users:
                session.delete(user)

            # 删除测试品种
            test_breeds = DogBreed.query.filter(
                DogBreed.breed_name.like("TEST_%")
            ).all()
            for breed in test_breeds:
                session.delete(breed)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"⚠️ 清理测试数据时出错: {e}")

        transaction.rollback()
        connection.close()
        session.remove()
        # 最后恢复原始 db.session
        db.session = original_session

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def runner(app):
    """提供测试 CLI 运行器。"""
    return app.test_cli_runner()


@pytest.fixture(scope="session", autouse=True)
def create_test_users(app, db):
    """在测试会话开始前创建两个测试用户：普通用户 user/123456，管理员 admin/123456。"""
    with app.app_context():
        # 先清理无效的 chat_sessions（user_id 为 NULL 的记录）
        try:
            from sqlalchemy import text

            # 直接使用 SQL 删除无效记录，避免 ORM 的 autoflush 问题
            db.session.execute(text("DELETE FROM chat_sessions WHERE user_id IS NULL"))
            db.session.commit()
        except Exception as e:
            print(f"⚠️ 清理无效会话时出错: {e}")
            db.session.rollback()

        # 只在用户不存在时创建，避免 delete+recreate 的并发/事务问题
        if not User.query.filter_by(username="user").first():
            # noinspection PyArgumentList
            user = User(username="user")
            user.set_password("123456")  # 至少 6 位
            db.session.add(user)

        if not User.query.filter_by(username="admin").first():
            # noinspection PyArgumentList
            # 编辑器忽略此行检查
            admin = User(username="admin", role="admin")
            admin.set_password("123456")
            db.session.add(admin)

        db.session.commit()


def pytest_collection_modifyitems(items):
    """过滤掉 test_framework.py 中的 test_case 装饰器函数本身"""
    filtered_items = []
    for item in items:
        # 跳过名为 test_case 的顶层函数
        if item.name == "test_case":
            # 检查是否是顶层函数（不在类中）
            parent_name = (
                getattr(item.parent, "name", None)
                if hasattr(item, "parent") and item.parent
                else None
            )
            # 如果父级不是测试类，则跳过
            if not parent_name or not parent_name.startswith("Test"):
                continue
        filtered_items.append(item)
    items[:] = filtered_items


@pytest.fixture
def login_user(client):
    """返回一个函数，用于登录指定用户，并返回是否成功。"""

    def _login(username, password):
        return client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    return _login


@pytest.fixture
def logged_in_client(client, login_user):
    """返回一个已经以普通用户身份登录的客户端。"""
    login_user("user", "123456")
    return client


@pytest.fixture
def admin_client(client, login_user):
    """返回一个已经以管理员身份登录的客户端。"""
    login_user("admin", "123456")
    return client
