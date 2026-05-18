# 狗狗数据分析系统 — 技术架构文档

## 系统架构

```
┌───────── Port 5000 ─────────┐    ┌───────── Port 8000 ─────────┐
│     Flask App (app.py)      │    │   FastAPI Pilot (实验)      │
│  ┌───────────────────────┐  │    │  ┌──────────────────────┐  │
│  │  10 Blueprints        │  │    │  │ routes_fastapi/      │  │
│  │  routes/*.py          │  │    │  │ SQLite (demo.db)     │  │
│  ├───────────────────────┤  │    │  │ v5.0.0-alpha         │  │
│  │  MySQL 8.0 (PyMySQL)  │  │    │  └──────────────────────┘  │
│  │  SQLAlchemy 2.0 ORM   │  │    └──────────┬────────────────┘
│  ├───────────────────────┤  │               │ /api/v1 proxy
│  │  Jinja2 + Alpine.js   │  │    ┌──────────▼────────────────┐
│  │  PyECharts 图表       │  │    │ Vue 3 + Element Plus      │
│  ├───────────────────────┤  │    │ Vite dev server :3000     │
│  │  APScheduler 6h 定时  │  │    └───────────────────────────┘
│  ├───────────────────────┤  │
│  │  Flask-Babel i18n     │  │    ┌───────────────────────────┐
│  │  Prometheus 监控      │  │    │ Prometheus :9090          │
│  └───────────────────────┘  │    │ Grafana   :3000 (监控)    │
└─────────────────────────────┘    │ Node Exp. :9100           │
                                    └───────────────────────────┘
```

## 项目结构

```
fastApiProject/
├── app.py                # Flask 应用工厂（create_app）
├── config.py             # 多环境配置（dev/prod/testing）
├── models.py             # 核心模型（User, DogBreed）
├── models_extended.py    # 扩展模型（14 表）
├── conftest.py           # Pytest 全局 Fixture
├── routes/               # 10 个蓝图
│   ├── main.py           #   首页/图表页面
│   ├── auth.py           #   登录/注册/登出
│   ├── api.py            #   通用 API + 品种 CRUD
│   ├── feedback.py       #   用户反馈
│   ├── analytics.py      #   用户行为分析
│   ├── ai_assistant.py   #   AI 智能助手
│   ├── ai_log_viewer.py  #   AI 日志查看
│   ├── pet_api.py        #   Live2D 宠物交互
│   ├── user_preference.py#   用户偏好
│   └── alert_system.py   #   价格/品种告警
├── utils/
│   └── auth.py           # JWT Token + login_required_api
├── charts.py             # 图表数据（PyMySQL 直连）
├── errors.py             # 全局错误处理器
├── templates/            # Jinja2 模板（20 个）
├── static/               # 静态资源（CSS/JS/图片）
├── Test/                 # Python 测试（pytest）
│   ├── test_auth.py
│   ├── test_api.py
│   ├── test_models_extended.py
│   └── factories.py      # 测试数据工厂
├── tests/                # Playwright TS 测试
├── frontend/             # Vue 3 前端（独立部署）
├── migrations/           # Alembic 迁移
└── scripts/              # 工具脚本
```

## 数据模型（22 表）

### 核心表（models.py）

| 表 | 说明 | 关键字段 |
|----|------|---------|
| `users` | 用户 | id, username, password_hash, role |
| `dog_breeds` | 品种 | id, breed_name(unique), avg_life_years, size_category, popularity |

### 扩展表（models_extended.py）

| 表 | 说明 | 关系 |
|----|------|------|
| `user_profiles` | 用户扩展信息 | FK→users |
| `app_tokens` | 移动端 Token | FK→users |
| `user_favorites` | 收藏品种 | FK→users, FK→dog_breeds |
| `user_preferences` | 偏好设置 | FK→users |
| `user_activity_logs` | 操作审计 | FK→users |
| `feedbacks` | 反馈 | FK→users, FK→admin(replied_by) |
| `user_events` | 行为事件 | FK→users |
| `chat_sessions` | AI 对话会话 | FK→users |
| `chat_messages` | AI 对话消息 | FK→chat_sessions |
| `price_alerts` | 价格告警 | FK→users |
| `breed_alerts` | 品种告警 | FK→users |
| `alert_notifications` | 告警通知 | FK→users |

## 认证体系

### Session 认证（主要）
- Flask-Login 管理用户会话
- CSRF 保护：4 个 HTML 蓝图启用，6 个 API 蓝图豁免
- 登录页面 `/login`，未登录重定向

### JWT Token 认证（为 APP 预留）
- `utils/auth.py` 提供 `token_required` / `login_required_api` 装饰器
- Access Token：1 小时有效期
- Refresh Token：7 天有效期
- `login_required_api` 兼容 Session + Token 双模式

## API 路由概览

| 模块 | 路由数 | 前缀 |
|------|--------|------|
| main | 12 | `/`, `/charts/*`, `/admin/*` |
| auth | 3 | `/login`, `/logout`, `/register` |
| api | 30+ | `/api/*` |
| feedback | 8 | `/api/feedback/*` |
| analytics | 5 | `/api/analytics/*` |
| ai_assistant | 15 | `/api/ai/*`, `/ai-chat` |
| ai_log_viewer | 4 | `/api/ai/logs/*` |
| pet_api | 5 | `/api/pet/*` |
| user_preference | 4 | `/api/user/preferences/*` |
| alert_system | 12 | `/api/alerts/*` |

## 定时任务

APScheduler 在 `app.py:start_scheduler()` 中注册，每 6 小时执行一次 `update_dashboard_summary()`。使用 `_scheduler_started` 全局标志防止 Flask reloader 下重复启动。

## 测试策略

- **框架**：pytest 8.4 + 自定义 `@test_case` 装饰器 + `TestResult` 报告
- **配置**：`TestingConfig`（MySQL 同库，事务回滚隔离）
- **隔离**：`session` fixture 为每个测试函数创建独立事务，结束后回滚
- **数据约定**：测试数据以 `TEST_` 为前缀，teardown 自动清理
- **测试用户**：`user/123456`（普通）、`admin/123456`（管理员），自动创建
- **运行**：`pytest`（默认 Test/ 目录）
- **覆盖**：22 核心测例覆盖 model 验证、auth 流程、API CRUD

## 部署

```bash
# 本地开发
cp .env.example .env        # 配置 MySQL 连接
python init_db.py           # 建库 + 初始数据
python app.py               # Flask :5000

# 生产部署
gunicorn -w 4 'app:create_app("production")' -b 0.0.0.0:5000

# 监控
docker-compose -f docker-compose.monitoring.yml up -d

# 数据库迁移
flask db upgrade            # 应用新迁移
flask db migrate -m "描述"  # 生成新迁移
```

## 关键配置

| 环境变量 | 用途 | 默认值 |
|----------|------|--------|
| `SECRET_KEY` | Flask 密钥 | 自动生成（生产必设） |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 自动生成（生产必设） |
| `DB_USER` / `DB_PASSWORD` | MySQL 凭据 | doguser / 123456 |
| `DB_HOST` / `DB_NAME` | MySQL 地址/库 | localhost / dog |
| `FLASK_ENV` | 运行环境 | development |
| `DATABASE_URL` | 生产数据库 URL（PostgreSQL 兼容） | — |
| `LOG_LEVEL` | 日志级别 | INFO |
