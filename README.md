# 🐕 狗狗数据分析系统

一个基于 Flask 的 Web 应用，用于狗狗品种数据管理与分析，附带狗粮在线购买功能。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![pytest](https://img.shields.io/badge/pytest-8.x-purple)

## 功能模块

| 模块 | 说明 |
|------|------|
| 数据看板 | 8 项核心指标统计，产地分布、价格区间图表 |
| 图表分析 | 散点图、折线图、柱状图、直方图、漏斗图、世界地图 |
| 品种管理 | 狗狗品种的增删改查 |
| AI 对话 | 接入大模型，支持犬种咨询、价格查询、喂养建议 |
| 虚拟宠物 | 网页上的互动小宠物，可触摸、可喂食 |
| 狗粮商城 | 商品列表、购物车、结算支付（微信/支付宝/银行卡模拟） |
| 数据分析 | 上传 CSV/Excel，自动生成图表 |

## 页面截图

![首页](img/首页.png)

![AI助手](img/AI助手.png)

## 项目结构

```
DogDogData/
├── app.py                 # Flask 主入口
├── config.py              # 数据库等配置
├── models.py              # SQLAlchemy 数据模型
├── routes/
│   ├── main.py            # 页面路由
│   ├── auth.py            # 登录/注册
│   ├── api.py             # REST API（品种、狗粮、数据等）
│   └── analytics.py       # 数据分析路由
├── templates/             # Jinja2 页面模板
├── static/                # CSS / JS / 图片
├── Test/                  # 自动化测试
│   ├── api_tests/         # API 接口测试
│   ├── e2e_tests/         # E2E 端到端测试（Playwright）
│   ├── ui_tests/          # UI 功能测试
│   ├── conftest_ui.py     # pytest 夹具
│   ├── test_dog_food.py   # 狗粮数据测试
│   └── test_food_purchase.py  # 狗粮购买流程测试
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置数据库（MySQL）
# 编辑 config.py，填入数据库连接信息

# 3. 初始化数据库
python init_db.py

# 4. 启动服务
python app.py

# 5. 浏览器访问
# http://localhost:5000
```

## 🧪 自动化测试

项目包含 API 测试、E2E 测试和 UI 测试，使用 pytest 框架组织：

```bash
# 运行全部测试
cd Test
pytest

# 按模块运行
pytest api_tests/              # API 接口测试
pytest e2e_tests/              # E2E 端到端测试
pytest test_dog_food.py        # 狗粮数据测试
pytest test_food_purchase.py   # 狗粮购买流程测试
```

### 测试覆盖

| 类型 | 覆盖内容 | 工具 |
|------|----------|------|
| API 测试 | 认证、品种、狗粮、AI 对话、数据分析、收藏 | pytest + requests |
| E2E 测试 | 注册登录、品种管理、数据导入分析、狗粮购买支付 | Playwright / Selenium |
| UI 测试 | 图表渲染、组件交互、AI 对话界面 | Selenium |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask |
| 数据库 | MySQL + SQLAlchemy ORM |
| 前端 | Jinja2 模板 + Bootstrap 5 + Chart.js |
| 测试 | pytest + Selenium + Playwright |
| 图表 | PyECharts（服务端渲染） |

## 关于本项目

这个项目是在 AI 辅助下一步步搭建的。最初从数据库设计和登录功能开始，逐渐扩展了数据分析、AI 对话、虚拟宠物等模块。开发过程中一边学习 Flask 框架，一边编写自动化测试来验证功能。

对我而言，最有价值的收获是：
- 理解了 Web 应用的完整开发流程（路由 → 模板 → 数据库 → 部署）
- 掌握了 pytest 自动化测试框架的搭建和使用
- 学会了用 Selenium 和 Playwright 做 E2E 测试
- 积累了 API 测试和接口联调的经验