import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user
from models import db
from models_store import Product
from werkzeug.utils import secure_filename
from PIL import Image

store_admin_bp = Blueprint('store_admin', __name__, url_prefix='/store/admin')

ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
PRODUCT_IMG_DIR = 'static/img/products'


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('需要管理员权限', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def save_product_image(file):
    if not file or not file.filename:
        return None
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        flash('不支持的图片格式，支持 JPG/PNG/GIF/WebP', 'danger')
        return None
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f'product_{ts}.jpg'
    save_dir = os.path.join(current_app.root_path, PRODUCT_IMG_DIR)
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    img = Image.open(file)
    if img.mode == 'RGBA' or img.mode == 'P':
        img = img.convert('RGB')
    max_size = 600
    w, h = img.size
    if w > max_size or h > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    img.save(path, 'JPEG', quality=80)
    return filename


@store_admin_bp.route('/products')
@admin_required
def product_list():
    q = Product.query
    price_min = request.args.get('price_min', '').strip()
    price_max = request.args.get('price_max', '').strip()
    stock_min = request.args.get('stock_min', '').strip()
    stock_max = request.args.get('stock_max', '').strip()
    try:
        if price_min: q = q.filter(Product.price >= float(price_min))
        if price_max: q = q.filter(Product.price <= float(price_max))
        if stock_min: q = q.filter(Product.stock >= int(stock_min))
        if stock_max: q = q.filter(Product.stock <= int(stock_max))
    except ValueError:
        pass
    products = q.order_by(Product.created_at.desc()).all()
    return render_template('store_admin_list.html', products=products,
                           price_min=price_min, price_max=price_max,
                           stock_min=stock_min, stock_max=stock_max)


@store_admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def product_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '0').strip()
        desc = request.form.get('description', '').strip()
        if not name or not price:
            flash('商品名称和价格不能为空', 'danger')
            return render_template('store_admin_form.html', product=None)
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('价格或库存格式错误', 'danger')
            return render_template('store_admin_form.html', product=None)
        image = save_product_image(request.files.get('image'))
        p = Product(name=name, price=price, stock=stock, description=desc, image=image or '')
        db.session.add(p)
        db.session.commit()
        flash(f'商品「{name}」已上架', 'success')
        return redirect(url_for('store_admin.product_list'))
    return render_template('store_admin_form.html', product=None)


@store_admin_bp.route('/products/<int:pid>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(pid):
    p = Product.query.get_or_404(pid)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '0').strip()
        desc = request.form.get('description', '').strip()
        if not name or not price:
            flash('商品名称和价格不能为空', 'danger')
            return render_template('store_admin_form.html', product=p)
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('价格或库存格式错误', 'danger')
            return render_template('store_admin_form.html', product=p)
        uploaded = save_product_image(request.files.get('image'))
        if uploaded:
            old_img = p.image
            if old_img:
                old_path = os.path.join(current_app.root_path, PRODUCT_IMG_DIR, old_img)
                if os.path.exists(old_path):
                    os.remove(old_path)
            p.image = uploaded
        p.name = name
        p.price = price
        p.stock = stock
        p.description = desc
        db.session.commit()
        flash(f'商品「{name}」已更新', 'success')
        return redirect(url_for('store_admin.product_list'))
    return render_template('store_admin_form.html', product=p)


@store_admin_bp.route('/products/<int:pid>/delete', methods=['POST'])
@admin_required
def product_delete(pid):
    p = Product.query.get_or_404(pid)
    if p.image:
        img_path = os.path.join(current_app.root_path, PRODUCT_IMG_DIR, p.image)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(p)
    db.session.commit()
    flash('商品已删除', 'success')
    return redirect(url_for('store_admin.product_list'))
