# 📜 脚本工具集

> 本文件夹包含所有临时脚本、工具程序和部署配置文件，不干扰主项目结构。

**最后更新**: 2026-04-13

---

## 📁 目录结构

```
scripts/
├── # 部署相关
├── config_demo.py              # 演示模式配置
├── seed_demo_data.py           # 演示数据初始化脚本
├── init_production.py          # 生产环境数据库初始化
├── start_demo.bat              # Windows 一键启动脚本
├── Procfile                    # 云平台启动配置
├── railway.toml                # Railway 部署配置
│
├── # 测试和验证工具
├── check_pet_html.py           # 宠物功能 HTML 检查
├── check_pet_implementation.py # 宠物功能实现检查
├── verify_pet.py               # 宠物功能验证
├── test_pet_2d5.py             # 2.5D 宠物测试
├── test_pet_automation.py      # 宠物自动化测试
├── test_optimized.py           # 优化测试
│
├── # 维护和修复工具
├── fix_color_import.py         # 颜色导入修复
├── force_clear_cache.py        # 强制清除缓存
├── generate_pet_sprites.py     # 生成宠物精灵图
└── restart_flask.bat           # Flask 重启脚本
```

---

## 🚀 快速开始

### 本地演示模式

```bash
# Windows 用户
start_demo.bat

# 或手动执行
python seed_demo_data.py
set FLASK_ENV=demo
python ../app.py
```

### 云部署准备

部署配置文件已准备好：
- `Procfile` - 云平台启动命令
- `railway.toml` - Railway 配置
- `config_demo.py` - 演示配置
- `init_production.py` - 生产初始化

详细部署指南请查看：`../docs/快速部署指南.md`

---

## 🛠️ 工具说明

### 部署工具

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `seed_demo_data.py` | 初始化演示数据 | 本地演示、测试环境 |
| `init_production.py` | 初始化生产数据库 | Railway/Render 部署 |
| `start_demo.bat` | 一键启动演示 | Windows 快速演示 |
| `config_demo.py` | 演示模式配置 | SQLite 数据库配置 |

### 测试工具

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `check_pet_html.py` | 检查宠物 HTML | 前端调试 |
| `verify_pet.py` | 验证宠物功能 | 功能测试 |
| `test_pet_2d5.py` | 2.5D 宠物测试 | 新版本测试 |
| `test_pet_automation.py` | 自动化测试 | 回归测试 |

### 维护工具

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `fix_color_import.py` | 修复颜色导入 | CSS 问题修复 |
| `force_clear_cache.py` | 强制清除缓存 | 缓存问题 |
| `generate_pet_sprites.py` | 生成精灵图 | 资源生成 |
| `restart_flask.bat` | 重启 Flask | 开发调试 |

---

## ⚠️ 注意事项

1. **这些脚本不纳入版本控制**
   - `scripts/` 已在 `.gitignore` 中
   - 仅用于本地开发和临时任务

2. **使用前确认路径**
   - 部分脚本可能需要调整相对路径
   - 确保在项目根目录运行

3. **演示数据可重置**
   ```bash
   python seed_demo_data.py --clear
   ```

4. **生产部署前检查**
   - 阅读 `../docs/部署检查清单.md`
   - 确保环境变量正确设置

---

## 📚 相关文档

- [快速部署指南](../docs/快速部署指南.md)
- [详细部署指南](../docs/部署指南.md)
- [部署检查清单](../docs/部署检查清单.md)
- [改造总结](../docs/部署改造总结.md)

---

*本文档由 AI 助手协助创建*
