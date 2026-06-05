"""
狗粮购买流程测试 — API + E2E（Selenium）

测试覆盖：
- API 正常下单 / 空购物车 / 各支付方式
- E2E 完整购买流程：选商品 → 加购 → 结算 → 填信息 → 支付 → 验证成功
"""

import pytest
import json
import time


class TestFoodOrderAPI:
    """下单 API 测试"""

    def test_place_order_success(self, authenticated_api_client):
        """TC-FOOD-ORDER-001：正常下单，返回订单号和金额"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [
                {"name": "皇家狗粮", "price": "198.00", "quantity": 2},
                {"name": "冠能鸡肉", "price": "158.00", "quantity": 1}
            ],
            "payment_method": "微信支付",
            "customer": {"name": "测试用户", "phone": "13800138000", "address": "深圳宝安"}
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["order_id"].startswith("FD")
        assert data["total"] == 554.0  # 198*2 + 158
        assert data["payment_method"] == "微信支付"

    def test_place_order_empty_cart(self, authenticated_api_client):
        """TC-FOOD-ORDER-002：空购物车下单，返回错误"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [],
            "payment_method": "微信支付"
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_place_order_alipay(self, authenticated_api_client):
        """TC-FOOD-ORDER-003：支付宝支付"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [{"name": "幼犬粮", "price": "88.00", "quantity": 1}],
            "payment_method": "支付宝"
        })
        assert resp.status_code == 200
        assert resp.get_json()["payment_method"] == "支付宝"

    def test_place_order_card(self, authenticated_api_client):
        """TC-FOOD-ORDER-004：银行卡支付"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [{"name": "进口狗粮", "price": "258.00", "quantity": 3}],
            "payment_method": "银行卡"
        })
        assert resp.status_code == 200
        assert resp.get_json()["payment_method"] == "银行卡"

    def test_place_order_no_customer(self, authenticated_api_client):
        """TC-FOOD-ORDER-005：无客户信息也能下单（模拟游客）"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [{"name": "测试粮", "price": "50.00", "quantity": 1}],
            "payment_method": "微信支付"
        })
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    def test_order_total_calculation(self, authenticated_api_client):
        """TC-FOOD-ORDER-006：验证金额计算准确性"""
        resp = authenticated_api_client.post("/api/food/order", json={
            "items": [
                {"name": "A粮", "price": "100.50", "quantity": 2},
                {"name": "B粮", "price": "50.25", "quantity": 4}
            ]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 402.0  # 100.50*2 + 50.25*4


@pytest.mark.e2e
class TestFoodPurchaseE2E:
    """E2E 端到端购买流程测试（需 Flask 服务运行中）"""

    def test_full_purchase_flow(self, selenium_driver, base_url):
        """TC-FOOD-E2E-001：完整购买流程"""
        driver = selenium_driver
        driver.get(f"{base_url}/food")

        time.sleep(1)

        # 1. 点击"加入购物车"（第一个商品）
        btns = driver.find_elements("class name", "add-to-cart-btn")
        assert len(btns) > 0, "没有找到加购按钮"
        btns[0].click()

        # 2. 验证购物车显示
        time.sleep(0.5)
        cart_count = driver.find_element("id", "cart-count")
        assert cart_count.text == "1", f"购物车应为1，实际: {cart_count.text}"

        # 3. 再加一个
        if len(btns) > 1:
            btns[1].click()
            time.sleep(0.5)
            assert cart_count.text == "2"

        # 4. 点"去结算"
        checkout_btn = driver.find_element("id", "checkout-btn")
        assert checkout_btn.is_enabled()
        checkout_btn.click()
        time.sleep(0.5)

        # 5. 填写收货信息
        driver.find_element("id", "customer-name").send_keys("陈慧")
        driver.find_element("id", "customer-phone").send_keys("17673953143")
        driver.find_element("id", "customer-address").send_keys("深圳市宝安区")

        # 6. 选择支付宝
        driver.find_element("id", "pay-alipay").click()

        # 7. 确认支付
        driver.find_element("id", "submit-order-btn").click()
        time.sleep(1)

        # 8. 验证成功提示
        success_msg = driver.find_element("id", "checkout-success")
        assert success_msg.is_displayed(), "未显示成功提示"
        assert "下单成功" in success_msg.text
        assert "FD" in success_msg.text

    def test_checkout_empty_cart(self, selenium_driver, base_url):
        """TC-FOOD-E2E-002：空购物车时结算按钮禁用"""
        driver = selenium_driver
        driver.get(f"{base_url}/food")
        time.sleep(1)

        checkout_btn = driver.find_element("id", "checkout-btn")
        assert not checkout_btn.is_enabled(), "空购物车时结算按钮应禁用"

    def test_checkout_missing_customer_info(self, selenium_driver, base_url):
        """TC-FOOD-E2E-003：缺收货信息时显示错误"""
        driver = selenium_driver
        driver.get(f"{base_url}/food")
        time.sleep(1)

        btns = driver.find_elements("class name", "add-to-cart-btn")
        if btns:
            btns[0].click()
        time.sleep(0.5)

        driver.find_element("id", "checkout-btn").click()
        time.sleep(0.5)

        # 不填任何信息，直接提交
        driver.find_element("id", "submit-order-btn").click()
        time.sleep(0.5)

        error = driver.find_element("id", "checkout-error")
        assert error.is_displayed()
        assert "请填写" in error.text