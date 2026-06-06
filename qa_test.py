"""
购物车完整流程测试 (QA)
"""
import requests, re, sys

BASE = 'http://localhost:5000'
session = requests.Session()
PASS = 0
FAIL = 0

def ok(desc, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [PASS]', desc)
    else:
        FAIL += 1
        print('  [FAIL]', desc, detail)

def get_csrf(page):
    idx = page.find('csrf_token')
    if idx < 0: return ''
    s = page.find('value="', idx) + 7
    e = page.find('"', s)
    return page[s:e]

# ═══ 1. 匿名用户 ═══
print('=== 1. Anonymous User ===')

store_html = session.get(BASE + '/store/', timeout=5).text
ok('Store page 200', store_html.find('store-card') > 0)
ok('12 products', store_html.count('store-card') >= 12)
ok('JPG images', 'product_01.jpg' in store_html)
ok('Cart badge in navbar', 'cart-badge-nav' in store_html)

r = session.get(BASE + '/store/cart/count', timeout=5)
ok('Cart count = 0', r.json() == {'count': 0})

pid_m = re.search(r'addToCart\((\d+)\)', store_html)
pid = int(pid_m.group(1)) if pid_m else 0
ok('Get product ID', pid > 0, 'pid=%d' % pid)

r = session.post(BASE + '/store/cart/add', json={'product_id': pid, 'quantity': 1}, timeout=5)
ok('Add cart (anon) 401', r.status_code == 401)
ok('Has redirect key', 'redirect' in r.json())

r = session.get(BASE + '/store/cart', allow_redirects=False, timeout=5)
ok('Cart page 302', r.status_code == 302)
r = session.get(BASE + '/store/checkout', allow_redirects=False, timeout=5)
ok('Checkout 302', r.status_code == 302)
r = session.get(BASE + '/store/orders', allow_redirects=False, timeout=5)
ok('Orders 302', r.status_code == 302)

# ═══ 2. Login ═══
print('=== 2. Login ===')

r = session.get(BASE + '/login', timeout=5)
csrf = get_csrf(r.text)
ok('Get CSRF token', len(csrf) > 10)

r = session.post(BASE + '/login',
    data={'username': 'user', 'password': '123456', 'csrf_token': csrf},
    allow_redirects=True, timeout=5)
ok('Login success', r.status_code == 200 and '/login' not in r.url)

store_html = session.get(BASE + '/store/', timeout=5).text
ok('Store after login', store_html.find('store-card') > 0)
pid_m = re.search(r'addToCart\((\d+)\)', store_html)
pid = int(pid_m.group(1)) if pid_m else 0
ok('Get product ID after login', pid > 0, 'pid=%d' % pid)

# ═══ 3. Product Detail ═══
print('=== 3. Product Detail ===')

r = session.get(BASE + '/store/%d' % pid, timeout=5)
ok('Detail page 200', r.status_code == 200)
ok('Quantity control', 'qty-input' in r.text)
ok('Add to cart button', 'addToCart' in r.text)
ok('Buy now button', 'buyNow' in r.text)

# ═══ 4. Cart ═══
print('=== 4. Cart ===')

r = session.post(BASE + '/store/cart/add', json={'product_id': pid, 'quantity': 2}, timeout=5)
j = r.json()
ok('Add item 1', j.get('success'), str(j))

pid2 = pid + 1
r = session.post(BASE + '/store/cart/add', json={'product_id': pid2, 'quantity': 1}, timeout=5)
j = r.json()
ok('Add item 2', j.get('success'), str(j))

r = session.post(BASE + '/store/cart/add', json={'product_id': pid, 'quantity': 1}, timeout=5)
j = r.json()
ok('Add same item (quantity+)', j.get('success'))

cart_html = session.get(BASE + '/store/cart', timeout=5).text
ok('Cart page 200', 'cart-item' in cart_html)
cart_ids = re.findall(r'updateQty\((\d+)', cart_html)
ok('Got cart IDs', len(cart_ids) >= 2, str(cart_ids))

if len(cart_ids) >= 2:
    cid = int(cart_ids[0])
    r = session.post(BASE + '/store/cart/update', json={'cart_id': cid, 'quantity': 5}, timeout=5)
    ok('Update qty', r.json().get('success'))

    cid2 = int(cart_ids[2])
    r = session.post(BASE + '/store/cart/remove', json={'cart_id': cid2}, timeout=5)
    ok('Remove item', r.json().get('success'))

# ═══ 5. Checkout ═══
print('=== 5. Checkout ===')

r = session.get(BASE + '/store/checkout', timeout=5)
ok('Checkout 200', r.status_code == 200)
ok('Has payment options', 'wechat' in r.text or 'alipay' in r.text)
ok('Has submit button', 'submitOrder' in r.text)

# ═══ 6. Place Order ═══
print('=== 6. Place Order ===')

r = session.post(BASE + '/store/order/place', timeout=5)
j = r.json()
ok('Order placed', j.get('success'), str(j))
oid = j.get('order_id', 0)
ok('Has order ID', oid > 0, 'oid=%d' % oid)
ok('Has total', float(j.get('total', 0)) > 0, 'total=%s' % j.get('total'))

# ═══ 7. Orders ═══
print('=== 7. Orders ===')

r = session.get(BASE + '/store/orders', timeout=5)
ok('Orders 200', r.status_code == 200)
ok('Has orders', 'order-card' in r.text or '#' + str(oid) in r.text)

# ═══ 8. Edge Cases ═══
print('=== 8. Edge Cases ===')

r = session.post(BASE + '/store/cart/add', json={'product_id': 99999, 'quantity': 1}, timeout=5)
ok('Non-existent product 404', r.status_code == 404)

cart_html = session.get(BASE + '/store/cart', timeout=5).text
for cid in re.findall(r'updateQty\((\d+)', cart_html):
    session.post(BASE + '/store/cart/remove', json={'cart_id': int(cid)}, timeout=5)
r = session.get(BASE + '/store/checkout', timeout=5)
ok('Empty cart checkout redirect', r.status_code in (200, 302))
# If 200, it should show empty state; if 302, it redirects to cart

session.get(BASE + '/auth/logout', timeout=5)
r = session.get(BASE + '/store/cart/count', timeout=5)
ok('Logout cart = 0', r.json() == {'count': 0})

# ═══ Results ═══
print('\n' + '=' * 40)
print('Results: %d PASS, %d FAIL, %d TOTAL' % (PASS, FAIL, PASS + FAIL))
if FAIL > 0:
    sys.exit(1)
print('ALL PASSED!')
