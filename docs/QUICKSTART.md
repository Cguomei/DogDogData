# 快速开始指南

## 🚀 5 分钟快速启动项目

### 前置要求
- Python 3.8+
- MySQL 8.0+
- Git（可选）

---

## 方式一：一键启动（推荐）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
编辑 `.env` 文件（已存在，无需创建）:
```env
DB_HOST=localhost
DB_USER=doguser
DB_PASSWORD=123456
DB_NAME=dog
SECRET_KEY=your-secret-key-here
```

### 3. 初始化数据库
```bash
python init_db.py
```

看到以下提示表示成功：
```
✅ 数据库初始化完成！

默认账户:
  管理员：admin / admin123
  测试用户：test / test123
```

### 4. 启动应用
```bash
python app.py
```

### 5. 访问系统
浏览器打开：http://localhost:5000

**登录**:
- 管理员账号：admin / admin123
- 测试账号：test / test123

---

## 方式二：使用虚拟环境（生产环境推荐）

### Windows
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动应用
python app.py
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

---

## 验证安装

### 检查清单
- [ ] 数据库 `dog` 已创建
- [ ] 用户 `doguser` 已创建并授权
- [ ] 所有表已创建（users, dog_breeds, dashboard_summary 等）
- [ ] 默认数据已插入（10 个狗狗品种）
- [ ] 应用启动在 http://localhost:5000

### 功能测试
1. **登录测试**
   - 访问 http://localhost:5000/login
   - 使用 admin/admin123 登录
   - 应成功跳转到首页

2. **数据看板**
   - 首页应显示 8 项核心指标
   - 图表正常加载

3. **品种管理**
   - 访问 http://localhost:5000/admin/breeds
   - 应能看到 10 个示例品种
   - 尝试添加、编辑、删除操作

4. **API 测试**
   ```bash
   # 获取品种列表
   curl http://localhost:5000/api/breeds
   
   # 添加品种（需要先登录获取 Cookie）
   curl -X POST http://localhost:5000/api/breeds \
     -H "Content-Type: application/json" \
     -d '{"breed_name":"新品种","popularity":50}'
   ```

---

## 常见问题

### Q1: 数据库连接失败
**错误**: `Can't connect to MySQL server`

**解决**:
1. 确认 MySQL 服务已启动
2. 检查 `.env` 文件中的数据库配置
3. 尝试用 root 用户连接：
   ```bash
   mysql -u root -p
   ```

### Q2: 找不到模块
**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### Q3: CSRF Token 错误
**错误**: `CSRF token missing`

**解决**:
- 清除浏览器缓存和 Cookie
- 确保表单中包含 `{{ form.hidden_tag() }}`
- 检查 `SECRET_KEY` 配置

### Q4: 端口被占用
**错误**: `Address already in use`

**解决**:
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

或修改端口：
```python
app.run(host='0.0.0.0', port=5001)
```

---

## 开发工具推荐

### IDE
- **PyCharm** - Python 专业开发工具
- **VS Code** - 轻量级编辑器

### 数据库管理
- **MySQL Workbench** - 官方图形化工具
- **Navicat** - 强大的数据库管理工具
- **DBeaver** - 免费开源的数据库工具

### API 测试
- **Postman** - API 调试工具
- **curl** - 命令行 HTTP 客户端
- **HTTPie** - 现代化的 CLI HTTP 客户端

---

## 下一步

### 1. 阅读完整文档
- [开发文档](docs/开发文档_重构版.md)
- [重构总结](REFACTOR_SUMMARY.md)

### 2. 自定义配置
编辑 `config.py` 调整：
- 数据库连接
- 缓存策略
- JWT 密钥
- 日志级别

### 3. 扩展功能
参考 `api/routes.py` 添加新的 API 接口

### 4. 部署到生产环境
- 使用 Gunicorn 作为 WSGI 服务器
- Nginx 反向代理
- HTTPS 加密传输

---

## 技术支持

遇到问题？
1. 查看 [开发文档](docs/开发文档_重构版.md)
2. 检查日志文件 `logs/app.log`
3. 提交 Issue 或联系开发团队

---

**祝开发愉快！** 🎉
