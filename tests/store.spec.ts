import { test, expect, Page } from '@playwright/test';

const BASE = 'http://localhost:5000';
const USER = { username: 'user', password: '123456' };

test.beforeEach(async ({ page }) => {
  await page.route('**/*', route => {
    const url = route.request().url();
    if (url.includes('cdn.jsdelivr.net') || url.includes('code.jquery.com') || url.includes('cdn.datatables.net')) {
      route.fulfill({ body: '' });
    } else {
      route.continue();
    }
  }).catch(() => {});
});

async function login(page: Page) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#username', { state: 'attached', timeout: 3000 }).catch(() => {});
  if (!page.url().includes('/login')) return;
  await page.fill('#username', USER.username);
  await page.fill('#password', USER.password);
  await page.click('button[type="submit"]', { force: true });
  await page.waitForSelector('nav.navbar', { timeout: 10000 });
}

async function addToCart(page: Page, productId: number) {
  const resp = await page.request.post(BASE + '/store/cart/add', {
    data: { product_id: productId, quantity: 1 }
  });
  expect(resp.status()).toBe(200);
}

async function cartCount(page: Page): Promise<number> {
  const resp = await page.request.get(BASE + '/store/cart/count');
  const data = await resp.json();
  return data.count;
}

async function emptyCart(page: Page) {
  // remove all items via API instead of UI (avoids navigation conflicts)
  let count = await cartCount(page);
  for (let i = 0; i < 20 && count > 0; i++) {
    const html = await page.goto('/store/cart', { waitUntil: 'domcontentloaded' }).catch(() => null);
    if (!html) { break; }
    const cartIdBtn = page.locator('.btn-outline-danger').first();
    const onclick = await cartIdBtn.getAttribute('onclick').catch(() => null);
    if (!onclick) break;
    const cartId = parseInt(onclick.match(/\d+/)![0]);
    const resp = await page.request.post(BASE + '/store/cart/remove', { data: { cart_id: cartId } });
    if (!resp.ok()) break;
    count = await cartCount(page);
  }
}

test.describe.serial('Store E2E', () => {

  test('01 - Anonymous: see products, cannot add to cart', async ({ page }) => {
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('.store-card')).toHaveCount(12);
    await expect(page.locator('#cart-badge-nav')).toHaveText('0');

    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/store/cart/add')),
      page.locator('.btn-add-cart').first().click(),
    ]);
    expect(resp.status()).toBe(401);
  });

  test('02 - Anonymous: cart/checkout/orders redirect to login', async ({ page }) => {
    await page.goto('/store/cart', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/login/);
    await page.goto('/store/checkout', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/login/);
    await page.goto('/store/orders', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/login/);
  });

  test('03 - Login flow', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await page.fill('#username', USER.username);
    await page.fill('#password', USER.password);
    await page.click('button[type="submit"]', { force: true });
    await page.waitForSelector('nav.navbar', { timeout: 10000 });
  });

  test('04 - Add to cart and verify badge', async ({ page }) => {
    await login(page);
    await emptyCart(page);
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    // extract product IDs from store page
    const pidBtns = page.locator('.btn-add-cart');
    const onclick0 = await pidBtns.nth(0).getAttribute('onclick');
    const onclick1 = await pidBtns.nth(1).getAttribute('onclick');
    const pid0 = parseInt(onclick0?.match(/\d+/)![0] || '0');
    const pid1 = parseInt(onclick1?.match(/\d+/)![0] || '0');
    expect(pid0).toBeGreaterThan(0);
    expect(pid1).toBeGreaterThan(0);

    await addToCart(page, pid0);
    expect(await cartCount(page)).toBe(1);
    await addToCart(page, pid0);
    expect(await cartCount(page)).toBe(2);
    await addToCart(page, pid1);
    expect(await cartCount(page)).toBe(3);
  });

  test('05 - Cart page: quantity update via +/-', async ({ page }) => {
    await login(page);
    await emptyCart(page);
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    const pidBtns = page.locator('.btn-add-cart');
    const onclick0 = await pidBtns.nth(0).getAttribute('onclick');
    const pid0 = parseInt(onclick0?.match(/\d+/)![0] || '0');
    await addToCart(page, pid0);
    await addToCart(page, pid0); // same product, merges → qty 2
    expect(await cartCount(page)).toBe(2);

    await page.goto('/store/cart', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('.cart-item')).toHaveCount(1);

    // click + button to increase quantity (last .store-qty-btn is the + button)
    const [updResp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/store/cart/update')),
      page.locator('.store-qty-btn').last().click(),
    ]);
    expect(updResp.status()).toBe(200);

    // verify quantity increased after page reload from updateQty
    await page.goto('/store/cart', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('#cart-wrap')).toContainText('3'); // qty became 3
  });

  test('06 - Remove item from cart', async ({ page }) => {
    await login(page);
    // ensure at least 1 item in cart
    let count = await cartCount(page);
    if (count < 1) {
      await page.goto('/store/', { waitUntil: 'domcontentloaded' });
      const pid0 = parseInt((await page.locator('.btn-add-cart').nth(0).getAttribute('onclick'))?.match(/\d+/)![0] || '0');
      await addToCart(page, pid0);
      count = await cartCount(page);
    }

    const before = count;

    // Get cart item IDs from the page
    await page.goto('/store/cart', { waitUntil: 'domcontentloaded' });
    const itemCount = await page.locator('.cart-item').count();
    expect(itemCount).toBeGreaterThanOrEqual(1);

    // Get the first cart item ID from the onclick attribute
    const firstBtn = page.locator('.btn-outline-danger').first();
    const onclick = await firstBtn.getAttribute('onclick');
    const cartId = parseInt(onclick?.match(/\d+/)![0] || '0');
    expect(cartId).toBeGreaterThan(0);

    // Remove via API directly (bypasses confirm dialog)
    const resp = await page.request.post(BASE + '/store/cart/remove', {
      data: { cart_id: cartId }
    });
    const body = await resp.json();
    expect(body.success).toBe(true);

    await page.goto('/store/cart', { waitUntil: 'domcontentloaded' });
    const after = await page.locator('.cart-item').count();
    expect(after).toBe(itemCount - 1);
  });

  test('07 - Place order flow', async ({ page }) => {
    await login(page);
    let beforeCount = await cartCount(page);
    if (beforeCount < 1) {
      await page.goto('/store/', { waitUntil: 'domcontentloaded' });
      const pid0 = parseInt((await page.locator('.btn-add-cart').nth(0).getAttribute('onclick'))?.match(/\d+/)![0] || '0');
      await addToCart(page, pid0);
      beforeCount = await cartCount(page);
    }

    await page.goto('/store/checkout', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('.checkout-wrap')).toBeVisible();

    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/store/order/place')),
      page.locator('button:has-text("提交订单")').click(),
    ]);
    expect(resp.status()).toBe(200);

    await page.waitForURL(/\/store\/orders/);
  });

  test('08 - Empty cart checkout redirects', async ({ page }) => {
    await login(page);
    await emptyCart(page);
    await page.goto('/store/checkout', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/store\/cart/);
  });

  test('09 - Product detail page', async ({ page }) => {
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    await page.locator('.store-card a').first().click();
    await expect(page.locator('.btn-add-cart-lg')).toBeVisible();
    await expect(page.locator('#qty-input')).toBeVisible();
    await expect(page.locator('.btn-buy-now')).toBeVisible();
  });

  test('10 - Non-existent product returns 404', async ({ page }) => {
    const resp = await page.goto('/store/99999', { waitUntil: 'domcontentloaded' });
    expect(resp?.status()).toBe(404);
  });

  test('11 - Logout resets cart badge to 0', async ({ page }) => {
    await login(page);
    await emptyCart(page);
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    const pid0 = parseInt((await page.locator('.btn-add-cart').nth(0).getAttribute('onclick'))?.match(/\d+/)![0] || '0');
    await addToCart(page, pid0);

    // verify cart count via page-level fetch (shares cookies with page)
    const countBefore = await page.evaluate(async () => {
      const r = await fetch('/store/cart/count');
      const d = await r.json();
      return d.count;
    });
    expect(countBefore).toBe(1);

    // logout
    await page.goto('/auth/logout', { waitUntil: 'domcontentloaded' });
    // after logout, should be redirected to home page
    if (!page.url().includes('/login')) {
      // if we're not on login page, logout succeeded
    }

    // The page.evaluate fetch might still use old cookies.
    // Instead, navigate back to store and check badge text
    await page.goto('/store/', { waitUntil: 'domcontentloaded' });
    const badgeText = await page.locator('#cart-badge-nav').textContent();
    expect(badgeText).toBe('0');
  });

  test('12 - Order list shows placed orders', async ({ page }) => {
    await login(page);
    await page.goto('/store/orders', { waitUntil: 'domcontentloaded' });

    const orders = page.locator('.order-card');
    const count = await orders.count();
    expect(count).toBeGreaterThanOrEqual(1);

    if (count > 0) {
      await expect(orders.first().locator('.status-label')).toBeVisible();
    }
  });
});
