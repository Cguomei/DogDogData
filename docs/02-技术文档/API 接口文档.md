# API 接口文档

## 基础信息

- **项目名称**: 狗狗数据分析系统 v2.4.0
- **Base URL**: `http://localhost:5000`
- **认证方式**: Session Cookie + JWT Token（API）
- **数据格式**: JSON
- **字符编码**: UTF-8
- **版本文本**: v2.4.0
- **更新日期**: 2026-03-24

---

## 认证接口

### 1. 用户注册

**接口**: `POST /register`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名，3-20 位，支持中文、字母、数字、下划线 |
| password | string | 是 | 密码，至少 6 位 |

**请求示例**:
```html
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="username" value="testuser">
    <input type="password" name="password" value="123456">
</form>
```

**响应**:
- 成功：重定向到登录页，flash 消息"注册成功，请登录"
- 失败：返回注册页，显示错误提示

**错误码**:
- 400: 用户名格式不合法/密码长度不足
- 409: 用户名已存在

---

### 2. 用户登录

**接口**: `POST /login`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```html
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="username" value="admin">
    <input type="password" name="password" value="123456">
</form>
```

**响应**:
- 成功：重定向到首页或之前访问的页面
- 失败：返回登录页，显示"用户名或密码错误"

**安全说明**:
- 不明确指出是用户名还是密码错误（防枚举攻击）
- 使用 ORM 参数化查询（防 SQL 注入）

---

### 3. 用户登出

**接口**: `GET /logout`

**认证要求**: 需要登录

**响应**:
- 成功：重定向到首页，显示"已登出"

---

## 品种管理接口

### 4. 获取所有品种

**接口**: `GET /api/breeds`

**认证要求**: 无需登录

**响应示例**:
```json
[
    {
        "id": 1,
        "breed_name": "哈士奇",
        "avg_life_years": 12.5,
        "size_category": "大型",
        "popularity": 95
    },
    {
        "id": 2,
        "breed_name": "泰迪",
        "avg_life_years": 14.0,
        "size_category": "小型",
        "popularity": 90
    }
]
```

---

### 5. 创建新品种

**接口**: `POST /api/breeds`

**认证要求**: 需要登录（管理员权限）

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| breed_name | string | 是 | 品种名称，2-100 字符，禁止 HTML 标签 |
| avg_life_years | number | 否 | 平均寿命，0-100 岁 |
| size_category | string | 否 | 体型类别：小型/中型/大型/超大型 |
| popularity | integer | 否 | 人气值，0-1000，默认 0 |

**请求示例**:
```json
{
    "breed_name": "边境牧羊犬",
    "avg_life_years": 14.5,
    "size_category": "中型",
    "popularity": 95
}
```

**成功响应** (201):
```json
{
    "message": "添加成功",
    "id": 123
}
```

**错误响应** (400):
```json
{
    "error": "品种名称为必填项"
}
```

```json
{
    "error": "品种名称不能包含 HTML 标签"
}
```

```json
{
    "error": "平均寿命必须在 0-100 岁之间"
}
```

```json
{
    "error": "体型类别必须是以下值之一：小型，中型，大型，超大型"
}
```

```json
{
    "error": "犬种 '边境牧羊犬' 已存在"
}
```

**验证规则**:
1. breed_name 必须是非空字符串，长度 2-100
2. 禁止包含 HTML 标签（防 XSS）
3. avg_life_years 必须是 0-100 的数字
4. size_category 必须是枚举值之一
5. popularity 必须是 0-1000 的整数
6. 品种名不能重复

---

### 6. 获取单个品种

**接口**: `GET /api/breeds/<id>`

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 品种 ID |

**响应示例**:
```json
{
    "id": 1,
    "breed_name": "哈士奇",
    "avg_life_years": 12.5,
    "size_category": "大型",
    "popularity": 95
}
```

**错误响应** (404):
```json
{
    "error": "未找到该品种"
}
```

---

### 7. 更新品种

**接口**: `PUT /api/breeds/<id>`

**认证要求**: 需要登录（管理员权限）

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 品种 ID |

**请求参数**: 同创建接口

**请求示例**:
```json
{
    "breed_name": "边境牧羊犬",
    "avg_life_years": 15.0,
    "size_category": "中型",
    "popularity": 98
}
```

**成功响应** (200):
```json
{
    "message": "更新成功"
}
```

**错误响应**: 同创建接口

**特殊说明**:
- 更新时会检查品种名是否与其他记录重复（排除当前记录）

---

### 8. 删除品种

**接口**: `DELETE /api/breeds/<id>`

**认证要求**: 需要登录（管理员权限）

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 品种 ID |

**成功响应** (200):
```json
{
    "message": "删除成功"
}
```

**错误响应** (404):
```json
{
    "error": "未找到该品种"
}
```

---

### 9. 批量导入品种

**接口**: `POST /api/breeds/import`

**认证要求**: 需要登录（管理员权限）

**请求参数**:
- Content-Type: `multipart/form-data`
- 文件字段：`file`

**支持的文件格式**:
- CSV (.csv)
- Excel (.xlsx, .xls)

**CSV 列要求**（支持中英文）:
- 品种名 / breed_name
- 平均寿命 / avg_life_years
- 体型 / size_category
- 人气值 / popularity

**CSV 示例**:
```csv
品种名，平均寿命，体型，人气值
哈士奇，12.5，大型，95
泰迪，14.0，小型，90
```

**成功响应** (200):
```json
{
    "success": 10,
    "fail": 2,
    "details": [
        "金毛：犬种 '金毛' 已存在",
        "边牧：数据库错误"
    ]
}
```

**错误响应** (400):
```json
{
    "error": "没有选择文件"
}
```

```json
{
    "error": "不支持的文件类型，请上传 CSV 或 Excel 文件"
}
```

```json
{
    "error": "文件中缺少必要的列（需要品种名、平均寿命、体型、人气值或其英文对应）"
}
```

---

## 狗粮数据接口

### 10. 获取狗粮统计数据

**接口**: `GET /api/food`

**认证要求**: 无需登录

**响应示例**:
```json
[
    {
        "name": "皇家狗粮",
        "price": "258.00",
        "origin": "法国"
    },
    {
        "name": "渴望",
        "price": "458.00",
        "origin": "加拿大"
    }
]
```

**错误响应** (500):
```json
{
    "error": "数据库连接失败"
}
```

---

## 图表接口

### 11. 价格散点图

**接口**: `GET /chart/scatter`

**响应**: HTML 格式的图表页面

---

### 12. 体重折线图

**接口**: `GET /chart/line`

**响应**: HTML 格式的图表页面

---

### 13. 级别柱状图

**接口**: `GET /chart/bar`

**响应**: HTML 格式的图表页面

---

### 14. TOP10 直方图

**接口**: `GET /chart/hist`

**响应**: HTML 格式的图表页面

---

### 15. 价格段漏斗图

**接口**: `GET /chart/funnel`

**响应**: HTML 格式的图表页面

---

### 16. 世界地图

**接口**: `GET /chart/map`

**响应**: HTML 格式的图表页面

**缓存策略**: 缓存 1 小时

---

## 错误处理

### 通用错误格式

```json
{
    "error": "错误描述信息"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复） |
| 500 | 服务器内部错误 |

---

## 安全说明

### CSRF 保护

- 所有表单提交必须包含 CSRF token
- API 接口（JSON）豁免 CSRF 验证
- CSRF token 有效期：1 小时

**获取 CSRF Token**:
```python
from flask_wtf.csrf import generate_csrf
token = generate_csrf()
```

**使用示例**:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### 认证要求

标记为"需要登录"的接口:
- 需要在请求中携带有效的 session cookie
- 未登录访问将返回 401 或重定向到登录页

### 权限要求

标记为"管理员权限"的接口:
- 需要用户的 role 字段为 'admin'
- 普通用户访问将返回 403

---

## 限流策略

### 建议配置（待实现）

- 登录接口：同一 IP 1 分钟内最多尝试 10 次
- API 接口：同一用户 1 小时内最多请求 1000 次
- 文件上传：单文件大小不超过 10MB

---

## 版本历史

### v1.0.0 (2026-03-23)
- ✅ 初始版本发布
- ✅ 完善输入验证规则
- ✅ 添加 CSRF 保护
- ✅ 增强错误处理

---

## 联系方式

- **技术支持**: dev-team@example.com
- **API 问题**: api-support@example.com

---

**文档版本**: 1.0  
**最后更新**: 2026-03-23
