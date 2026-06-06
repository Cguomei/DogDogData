# 🐕 狗狗数据分析系统

[![Version](https://img.shields.io/badge/version-5.2.0-blue)](https://github.com/Cguomei/DogDogData/releases/tag/v5.2.0)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![pytest](https://img.shields.io/badge/pytest-8.x-purple)

一个基于 Flask 的 Web 应用，用于狗狗品种数据管理与分析，附带狗粮在线商城。

## 功能模块

| 模块 | 说明 |
|------|------|
| 数据看板 | 8 项核心指标统计，产地分布、价格区间图表 |
| 图表分析 | 散点图、折线图、柱状图、直方图、漏斗图、世界地图 |
| 品种管理 | 狗狗品种的增删改查 |
| AI 对话 | 接入大模型，支持犬种咨询、价格查询、喂养建议 |
| 虚拟宠物 | 网页上的互动小宠物，可触摸、可喂食 |
| 狗粮商城 | 商品列表、购物车、结算、订单管理（35 款商品） |
| 商品管理 | 管理员专用后台：商品 CRUD + 图片上传 |
| 数据分析 | 上传 CSV/Excel，自动生成图表 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
cp .env.example .env       # 编辑 .env 填入 MySQL 连接信息

# 2. 初始化数据库 + 种子数据
python init_db.py
python scripts/seed_demo_data.py      # 可选：演示数据

# 3. 启动服务
python app.py

# 4. 浏览器访问
# http://localhost:5000
```

默认测试账号：`user` / `123456` 管理员：`admin` / `123456`

## 项目结构

```
DogDogData/
├── app.py                 # Flask 主入口（__version__ = "5.2.0"）
├── config.py              # 数据库等配置
├── models.py              # SQLAlchemy 核心模型（User, DogBreed）
├── models_store.py        # 商城模型（Product, CartItem, Order, OrderItem）
├── routes/
│   ├── main.py            # 页面路由（首页、图表等）
│   ├── auth.py            # 登录/注册
│   ├── api.py             # REST API
│   ├── store.py           # 商城蓝图（商品/购物车/订单）
│   ├── store_admin.py     # 商品管理蓝图（Admin 专用）
│   └── ...                # AI 助手、反馈、分析等
├── templates/             # Jinja2 页面模板（含商城/管理模板）
├── static/                # CSS / JS / 图片 / 商品图片
├── Test/                  # Python 自动化测试（pytest）
│   ├── test_store.py      # 商城路由测试（10 项）
│   ├── qa_test.py         # 集成测试（37 项）
│   ├── test_auth.py       # 认证测试
│   └── ...                # API、模型、E2E 等
├── tests/                 # Playwright TypeScript E2E
│   └── store.spec.ts      # 商城 E2E 测试（12 项）
├── run.py                 # 统一测试运行器
├── .coveragerc            # 覆盖率配置（fail_under=70）
├── pytest.ini             # pytest 配置
└── requirements.txt
```

## 🧪 测试

使用统一运行器 `run.py`：

```bash
# 商城测试
python run.py --type store

# API 测试
python run.py --type api

# P0 核心测试
python run.py --type p0

# E2E 测试（需要运行中的服务器）
npx playwright test

# 全部测试
python run.py --type all

# 测试 + 覆盖率报告
python run.py --type all --cov --html
```

### 测试统计（v5.2.0）

| 类型 | 数量 | 工具 |
|------|------|------|
| 商城单元测试 | 10 | pytest |
| 集成测试 | 37 | pytest |
| Playwright E2E | 12 | Playwright |
| **总计** | **59 项全部通过** | |

## 狗粮商城

35 款狗粮商品，完整购物流程：

- **商品浏览**：响应式 4 列网格，图片懒加载
- **购物车**：AJAX 增删改，导航栏角标实时更新
- **结算下单**：库存自动扣减，订单状态跟踪
- **商品管理**：管理员后台，支持图片上传自动压缩

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask + Flask-Login + Flask-Babel |
| 数据库 | MySQL 8.0 + SQLAlchemy 2.0 ORM |
| 前端 | Jinja2 + Bootstrap 5.3 + CSS Grid |
| 测试 | pytest + Playwright + coverage |
| 图表 | PyECharts 服务端渲染 |
| 监控 | Prometheus + Grafana（Docker Compose） |
| 定时任务 | APScheduler（6 小时间隔汇总） |

## 关于本项目

这个项目是在 AI 辅助下一步步搭建的。最初从数据库设计和登录功能开始，逐渐扩展了数据分析、AI 对话、虚拟宠物、狗粮商城等模块。开发过程中一边学习 Flask 框架，一边编写自动化测试来验证功能。

对我而言，最有价值的收获是：
- 理解了 Web 应用的完整开发流程（路由 → 模板 → 数据库 → 部署）
- 掌握了 pytest 自动化测试框架的搭建和使用
- 学会了用 Playwright 做 E2E 测试
- 积累了 API 测试和接口联调的经验

## 版本历史

完整版本记录见 [CHANGELOG](docs/05-版本记录/CHANGELOG.md)。