# 🐕 狗狗数据分析系统

> 基于 Flask 的数据可视化平台 | 重构版 v2.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

![](img/首页.png)

---

## 📖 项目简介

狗狗数据分析系统是一个功能完善的数据可视化平台，提供：

- 📊 **数据看板** - 8 项核心指标实时展示
- 📈 **6 种图表** - 散点图、折线图、柱状图、直方图、漏斗图、地图
- 🔐 **用户认证** - Session + JWT Token 双重支持
- 🎯 **品种管理** - 完整的 CRUD 操作
- ⭐ **收藏功能** - 用户收藏系统
- 📱 **APP Ready** - 标准 RESTful API 接口

---

## ✨ 重构亮点（v2.0）

### 🎯 代码质量
- ✅ 代码量减少 **55%**（732→327 行）
- ✅ 消除重复代码
- ✅ 统一编码风格
- ✅ 增强可读性

### 🏗️ 架构优化
- ✅ 应用工厂模式
- ✅ 模块化设计
- ✅ 职责分离清晰
- ✅ 易于测试和维护

### 🔒 安全性增强
- ✅ 统一错误处理
- ✅ CSRF 保护
- ✅ XSS 防护
- ✅ SQL 注入防护

### 📱 APP 支持
- ✅ JWT Token 认证
- ✅ RESTful API
- ✅ 标准响应格式
- ✅ 设备管理支持

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_db.py
```

### 3. 启动应用
```bash
python app.py
```

### 4. 访问系统
浏览器打开：http://localhost:5000

**默认账户**:
- 管理员：`admin / admin123`
- 测试用户：`test / test123`

📖 **详细教程**: [QUICKSTART.md](QUICKSTART.md)

---

## 📁 项目结构

```
fastApiProject/
├── api/                      # API 蓝图模块
│   ├── __init__.py
│   └── routes.py            # RESTful API 定义
├── utils/                    # 工具类
│   ├── __init__.py
│   ├── api_response.py      # API 响应助手
│   └── auth.py              # JWT 认证装饰器
├── templates/                # HTML 模板
├── static/CSS/               # 样式文件
├── docs/                     # 文档目录
│   ├── API 接口文档.md
│   └── 开发文档_重构版.md
├── config.py                 # 配置管理
├── models.py                 # 基础数据模型
├── models_extended.py        # 扩展数据模型
├── charts.py                 # 图表生成
├── map_utils.py              # 地图工具
├── errors.py                 # 错误处理
├── init_db.py                # 数据库初始化
├── app.py                    # 主应用入口
├── requirements.txt          # 依赖包
├── .env                      # 环境变量
├── QUICKSTART.md             # 快速开始指南
└── REFACTOR_SUMMARY.md       # 重构总结
```

---

## 🛠️ 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 开发语言 |
| Flask | 3.1.3 | Web 框架 |
| SQLAlchemy | 2.0.48 | ORM 框架 |
| PyMySQL | 1.1.2 | MySQL 驱动 |
| Flask-Login | 0.6.3 | 用户认证 |
| Flask-Caching | 2.3.1 | 缓存管理 |
| PyJWT | 2.10.1 | JWT Token |
| PyECharts | 2.1.0 | 数据可视化 |
| Pandas | 2.3.3 | 数据处理 |

### 数据库
- MySQL 8.0+
- 字符集：utf8mb4
- 存储引擎：InnoDB

---

## 📺 功能展示

### 首页数据看板
![](img/首页.png)

- 8 项核心指标卡片
- 实时数据更新
- 快捷导航入口

### 图表展示
- **价格散点图** - 分析价格分布
- **体重折线图** - 趋势变化展示
- **级别柱状图** - 对比分析
- **TOP10 直方图** - 热门排行
- **价格漏斗图** - 转化分析
- **世界地图** - 地域分布

### 品种管理
- 列表展示（分页）
- 添加/编辑/删除
- 搜索筛选
- 数据验证

---

## 🔧 配置说明

### 环境变量（.env）
```env
# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_HOST=localhost
DB_USER=doguser
DB_PASSWORD=123456
DB_NAME=dog

# JWT 配置
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
```

### 生产环境配置
编辑 `config.py`:
```python
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'
```

---

## 📚 文档索引

### 新手入门
1. [快速开始](QUICKSTART.md) - 5 分钟上手
2. [开发文档](docs/开发文档_重构版.md) - 完整技术文档
3. [重构总结](REFACTOR_SUMMARY.md) - 了解改进之处

### API 文档
- [API 接口文档](docs/API 接口文档.md) - 16 个接口详解

### 产品文档（产品经理编制）
- 产品需求文档
- 产品原型设计
- 业务流程文档
- 验收标准文档
- 项目计划文档

👉 所有产品文档位于 `项目说明/` 目录

---

## 🧪 测试

### 运行测试
```bash
# 所有测试
pytest

# 特定测试
pytest tests/test_api.py

# 查看覆盖率
pytest --cov=app tests/
```

### 测试报告
测试报告位于 `Test/reports/` 目录

---

## 📦 部署

### 使用 Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 👥 团队

- 开发负责人：[Your Name]
- 产品经理：[PM Name]
- 联系方式：[email@example.com]

---

## 🎉 致谢

感谢以下开源项目：
- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PyECharts](https://pyecharts.org/)
- [Pandas](https://pandas.pydata.org/)

---

## 📈 项目状态

- ✅ **v2.0 重构完成** (2026-03-23)
- 🚧 单元测试开发中
- 📱 APP 接口已就绪
- ☁️ 云部署规划中

---

**Made with ❤️ by the Development Team**