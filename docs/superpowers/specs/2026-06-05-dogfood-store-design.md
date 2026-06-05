# 狗粮商城 Demo 设计文档

## 概述

在现有 DogDogData Flask 项目中新建一个狗粮售卖 Demo 页面，实现常规电商模式（淘宝/JD风格）的核心功能：商品展示、购物车、用户系统。

## 技术方案

**方案：新建 Flask 蓝图**（推荐）

- 新建 `routes/store.py` 蓝图 + `models_store.py` 数据模型
- 复用现有 Flask + Bootstrap 5.3 + Flask-Login 架构
- 商品图片从 `img/` 复制到 `static/img/products/`，重命名为 `product_01.png` ~ `product_12.png`

## 数据模型 (models_store.py)

### Product 商品表

| 字段          | 类型          | 说明    |
| ----------- | ----------- | ----- |
| id          | Integer, PK | 主键    |
| name        | String(100) | 商品名称  |
| description | Text        | 商品描述  |
| price       | Float       | 价格    |
| image       | String(200) | 图片文件名 |
| stock       | Integer     | 库存数量  |
| is_active   | Boolean     | 是否上架  |
| created_at  | DateTime    | 创建时间  |

### CartItem 购物车表

| 字段         | 类型                       | 说明   |
| ---------- | ------------------------ | ---- |
| id         | Integer, PK              | 主键   |
| user_id    | Integer, FK → User.id    | 用户   |
| product_id | Integer, FK → Product.id | 商品   |
| quantity   | Integer                  | 数量   |
| created_at | DateTime                 | 创建时间 |

unique constraint: (user_id, product_id)

### Order 订单表

| 字段           | 类型                    | 说明                                           |
| ------------ | --------------------- | -------------------------------------------- |
| id           | Integer, PK           | 主键                                           |
| user_id      | Integer, FK → User.id | 用户                                           |
| total_amount | Float                 | 总金额                                          |
| status       | String(20)            | 状态: pending/paid/shipped/completed/cancelled |
| created_at   | DateTime              | 创建时间                                         |

### OrderItem 订单明细表

| 字段           | 类型                       | 说明   |
| ------------ | ------------------------ | ---- |
| id           | Integer, PK              | 主键   |
| order_id     | Integer, FK → Order.id   | 订单   |
| product_id   | Integer, FK → Product.id | 商品   |
| product_name | String(100)              | 快照名称 |
| price        | Float                    | 快照价格 |
| quantity     | Integer                  | 数量   |

## 路由 (routes/store.py)

| 路由                 | 方法   | 功能           | 登录要求 |
| ------------------ | ---- | ------------ | ---- |
| /store             | GET  | 商品列表页        | 否    |
| /store/\<id\>      | GET  | 商品详情页        | 否    |
| /store/cart        | GET  | 购物车页面        | 是    |
| /store/cart/add    | POST | 加入购物车 (AJAX) | 是    |
| /store/cart/update | POST | 修改数量 (AJAX)  | 是    |
| /store/cart/remove | POST | 删除商品 (AJAX)  | 是    |
| /store/checkout    | GET  | 结算页面         | 是    |
| /store/order/place | POST | 提交订单 (AJAX)  | 是    |
| /store/orders      | GET  | 我的订单列表       | 是    |

蓝图前缀: `/store`

## 页面模板

| 模板文件                | 说明                           |
| ------------------- | ---------------------------- |
| store_list.html     | 4列商品网格，每张卡片含图片+名称+价格+加入购物车按钮 |
| store_detail.html   | 左图右文，大图展示+数量选择+加入购物车         |
| store_cart.html     | 商品列表+数量调整+全选+结算按钮            |
| store_checkout.html | 收货信息+订单摘要+支付方式+提交订单          |
| store_orders.html   | 订单列表+状态+操作                   |

## 种子数据

12 种口味的狗粮，对应 12 张图片，价格随机 ¥19.90 ~ ¥899.90，质量100g-10kg,库存 50~200。

## 修改文件清单

**新建：**

- `models_store.py`
- `routes/store.py`
- `templates/store_list.html`
- `templates/store_detail.html`
- `templates/store_cart.html`
- `templates/store_checkout.html`
- `templates/store_orders.html`
- `static/CSS/store.css`

**修改：**

- `app.py` — 注册 store_bp
- `templates/base.html` — 导航栏加商城入口 + 购物车角标
- `routes/auth.py` — 登录后重定向回商店

## 用户交互流程

```
未登录用户: 浏览商品列表 → 查看详情 → 点击"加入购物车" → 跳转登录 → 登录后回到购物车
已登录用户: 浏览/搜索 → 加入购物车 → 购物车确认 → 结算 → 下单 → 查看订单
```
