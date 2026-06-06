import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PIL import Image
from app import create_app
from models import db
from models_store import Product

BASE = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE, 'img', '高端狗粮')
DST_DIR = os.path.join(BASE, 'static', 'img', 'products')

app = create_app()
with app.app_context():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))])
    print(f'Found {len(files)} images')

    flavors = [
        '澳洲和牛配方', '帝王三文鱼', '黑松露鸡肉', '加拿大火鸡',
        '伊比利亚猪肉', '阿拉斯加鳕鱼', '法式鸭胸', '日本和牛',
        '地中海鱼贝', '瑞士奶酪蔬菜', '挪威三文鱼', '安格斯牛肉',
        '新西兰羊排', '北海道扇贝', '意大利松露', '西班牙海鲜',
        '美国野牛', '智利银鳕鱼', '丹麦猪肉', '苏格兰鹿肉',
        '加勒比海鱼', '德国猪肘', '澳洲袋鼠肉'
    ]

    os.makedirs(DST_DIR, exist_ok=True)
    count = 0
    for i, fname in enumerate(files):
        src = os.path.join(SRC_DIR, fname)
        ts = f'batch_{i+1:02d}'
        dst_name = f'product_batch_{ts}.jpg'
        dst = os.path.join(DST_DIR, dst_name)

        img = Image.open(src)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        w, h = img.size
        max_size = 600
        if w > max_size or h > max_size:
            ratio = max_size / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        img.save(dst, 'JPEG', quality=80)

        flavor = flavors[i] if i < len(flavors) else f'精选配方{i+1}'
        price = round(random.uniform(39, 199), 1)
        stock = random.randint(30, 300)
        p = Product(
            name=f'汪汪超爱吃狗粮（{flavor}）',
            price=price,
            stock=stock,
            image=dst_name,
            description=f'精选{flavor}食材，为爱犬提供高端营养体验。'
        )
        db.session.add(p)
        count += 1

    db.session.commit()
    print(f'Imported {count} products')
    print('Done!')
