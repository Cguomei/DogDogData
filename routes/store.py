from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models_store import Product, CartItem, Order, OrderItem, OrderStatus
from datetime import datetime

store_bp = Blueprint('store', __name__, url_prefix='/store')

PRODUCT_SEED = [
    {'name': '汪汪超爱吃狗粮（鸡肉味）', 'price': 29.90, 'image': 'product_01.png', 'stock': 120, 'description': '精选优质鸡肉，富含蛋白质，适合全犬种。'},
    {'name': '汪汪超爱吃狗粮（牛肉味）', 'price': 35.90, 'image': 'product_02.png', 'stock': 85, 'description': '澳洲进口牛肉，高蛋白低脂肪，增强肌肉。'},
    {'name': '汪汪超爱吃狗粮（三文鱼味）', 'price': 42.90, 'image': 'product_03.png', 'stock': 150, 'description': '深海三文鱼，富含Omega-3，美毛护肤。'},
    {'name': '汪汪超爱吃狗粮（羊肉味）', 'price': 38.90, 'image': 'product_04.png', 'stock': 95, 'description': '新西兰草饲羊肉，温和易消化，适合敏感肠胃。'},
    {'name': '汪汪超爱吃狗粮（鸭肉味）', 'price': 32.90, 'image': 'product_05.png', 'stock': 110, 'description': '低温烘焙鸭肉，清热去火，减少泪痕。'},
    {'name': '汪汪超爱吃狗粮（鱼肉味）', 'price': 39.90, 'image': 'product_06.png', 'stock': 75, 'description': '多种深海鱼配方，DHA助力大脑发育。'},
    {'name': '汪汪超爱吃狗粮（兔肉味）', 'price': 45.90, 'image': 'product_07.png', 'stock': 60, 'description': '高蛋白低胆固醇兔肉，控制体重首选。'},
    {'name': '汪汪超爱吃狗粮（鹿肉味）', 'price': 55.90, 'image': 'product_08.png', 'stock': 45, 'description': '稀有鹿肉配方，低敏高营养，尊享品质。'},
    {'name': '汪汪超爱吃狗粮（蔬菜味）', 'price': 25.90, 'image': 'product_09.png', 'stock': 200, 'description': '多种蔬菜搭配，膳食纤维丰富，均衡营养。'},
    {'name': '汪汪超爱吃狗粮（水果味）', 'price': 28.90, 'image': 'product_10.png', 'stock': 180, 'description': '天然水果添加，维生素丰富，狗狗超爱。'},
    {'name': '汪汪超爱吃狗粮（幼犬配方）', 'price': 49.90, 'image': 'product_11.png', 'stock': 90, 'description': '专为幼犬设计，钙磷比均衡，促进骨骼发育。'},
    {'name': '汪汪超爱吃狗粮（老年犬配方）', 'price': 52.90, 'image': 'product_12.png', 'stock': 70, 'description': '老年犬专属配方，关节保护，易消化吸收。'},
]

def seed_products():
    if Product.query.first() is None:
        for data in PRODUCT_SEED:
            p = Product(**data)
            db.session.add(p)
        db.session.commit()

@store_bp.route('/')
def product_list():
    products = Product.query.filter_by(is_active=True).all()
    return render_template('store_list.html', products=products)

@store_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('store_detail.html', product=product)


@store_bp.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    product = Product.query.get(product_id)
    if not product or not product.is_active:
        return jsonify({'success': False, 'error': '商品不存在'}), 404
    cart = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart:
        cart.quantity += quantity
    else:
        cart = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart)
    db.session.commit()
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': count})


@store_bp.route('/cart/update', methods=['POST'])
@login_required
def cart_update():
    data = request.get_json()
    cart = CartItem.query.filter_by(id=data.get('cart_id'), user_id=current_user.id).first()
    if not cart:
        return jsonify({'success': False, 'error': '购物车项不存在'}), 404
    qty = data.get('quantity', 1)
    if qty <= 0:
        db.session.delete(cart)
    else:
        cart.quantity = qty
    db.session.commit()
    return jsonify({'success': True})


@store_bp.route('/cart/remove', methods=['POST'])
@login_required
def cart_remove():
    data = request.get_json()
    cart = CartItem.query.filter_by(id=data.get('cart_id'), user_id=current_user.id).first()
    if cart:
        db.session.delete(cart)
        db.session.commit()
    return jsonify({'success': True})


@store_bp.route('/cart/count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})


@store_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(float(item.product.price) * item.quantity for item in items if item.product)
    return render_template('store_cart.html', items=items, total=total)


@store_bp.route('/checkout')
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('购物车是空的', 'warning')
        return redirect(url_for('store.cart'))
    total = sum(float(item.product.price) * item.quantity for item in items if item.product)
    return render_template('store_checkout.html', items=items, total=total)


@store_bp.route('/order/place', methods=['POST'])
@login_required
def place_order():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        return jsonify({'success': False, 'error': '购物车为空'}), 400
    total = sum(float(item.product.price) * item.quantity for item in items if item.product)
    order = Order(user_id=current_user.id, total_amount=total, status=OrderStatus.pending)
    db.session.add(order)
    db.session.flush()
    for cart in items:
        item = OrderItem(
            order_id=order.id,
            product_id=cart.product_id,
            product_name=cart.product.name,
            price=cart.product.price,
            quantity=cart.quantity
        )
        db.session.add(item)
        product = cart.product
        if product.stock >= cart.quantity:
            product.stock -= cart.quantity
        db.session.delete(cart)
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id, 'total': float(total)})


@store_bp.record_once
def on_load(state):
    with state.app.app_context():
        seed_products()
