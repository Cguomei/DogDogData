import pytest
from sqlalchemy.exc import IntegrityError
from models import User
from models_store import Product, CartItem, Order, OrderItem, OrderStatus


class TestProductModel:
    def test_create_product(self, db, session):
        p = Product(name='TEST_狗粮', price=29.9, image='product_01.jpg', stock=100)
        session.add(p)
        session.commit()
        assert p.id is not None
        assert p.name == 'TEST_狗粮'
        assert p.is_active is True

    def test_product_defaults(self, db, session):
        p = Product(name='TEST_默认', price=19.9)
        session.add(p)
        session.commit()
        assert p.description == ''
        assert p.stock == 0
        assert p.is_active is True


class TestCartItemModel:
    def test_cart_unique_constraint(self, db, session):
        user = User.query.filter_by(username='user').first()
        p = Product(name='TEST_Cart', price=10)
        session.add(p)
        session.commit()
        c1 = CartItem(user_id=user.id, product_id=p.id, quantity=1)
        session.add(c1)
        session.commit()
        c2 = CartItem(user_id=user.id, product_id=p.id, quantity=2)
        session.add(c2)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


class TestOrderModel:
    def test_create_order_with_items(self, db, session):
        user = User.query.filter_by(username='user').first()
        p = Product(name='TEST_Order', price=15.0)
        session.add(p)
        session.commit()
        order = Order(user_id=user.id, total_amount=30.0, status=OrderStatus.pending)
        session.add(order)
        session.commit()
        item = OrderItem(order_id=order.id, product_id=p.id, product_name=p.name, price=p.price, quantity=2)
        session.add(item)
        session.commit()
        assert order.items.count() == 1
        assert order.total_amount == 30.0


class TestStoreRoutes:
    def test_product_list_public(self, client):
        resp = client.get('/store/')
        assert resp.status_code == 200

    def test_product_detail(self, client, db):
        from models_store import Product
        p = Product.query.first()
        if not p:
            p = Product(name='TEST_Route', price=10.0)
            db.session.add(p)
            db.session.commit()
        resp = client.get(f'/store/{p.id}')
        assert resp.status_code == 200

    def test_cart_requires_login(self, client):
        resp = client.get('/store/cart')
        assert resp.status_code == 302

    def test_cart_add_requires_login(self, client):
        resp = client.post('/store/cart/add', json={'product_id': 1, 'quantity': 1})
        assert resp.status_code in (302, 401)

    def test_checkout_requires_login(self, client):
        resp = client.get('/store/checkout')
        assert resp.status_code == 302

    def test_orders_requires_login(self, client):
        resp = client.get('/store/orders')
        assert resp.status_code == 302
