import pytest
from models_store import Product, CartItem, Order, OrderItem


class TestProductModel:
    def test_create_product(self, db):
        p = Product(name='测试狗粮', price=29.9, image='product_01.png', stock=100)
        db.session.add(p)
        db.session.commit()
        assert p.id is not None
        assert p.name == '测试狗粮'
        assert p.is_active is True

    def test_product_defaults(self, db):
        p = Product(name='默认测试', price=19.9)
        db.session.add(p)
        db.session.commit()
        assert p.description == ''
        assert p.stock == 0
        assert p.is_active is True


class TestCartItemModel:
    def test_cart_unique_constraint(self, db, session):
        from models import User
        user = User.query.filter_by(username='user').first()
        p = Product(name='CartTest', price=10)
        db.session.add(p)
        db.session.commit()
        c1 = CartItem(user_id=user.id, product_id=p.id, quantity=1)
        db.session.add(c1)
        db.session.commit()
        c2 = CartItem(user_id=user.id, product_id=p.id, quantity=2)
        db.session.add(c2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


class TestOrderModel:
    def test_create_order_with_items(self, db):
        from models import User
        user = User.query.filter_by(username='user').first()
        p = Product(name='OrderTest', price=15.0)
        db.session.add(p)
        db.session.commit()
        order = Order(user_id=user.id, total_amount=30.0, status='pending')
        db.session.add(order)
        db.session.commit()
        item = OrderItem(order_id=order.id, product_id=p.id, product_name=p.name, price=p.price, quantity=2)
        db.session.add(item)
        db.session.commit()
        assert order.items.count() == 1
        assert order.total_amount == 30.0
