# Flutter APP开发详细计划

## 📋 项目信息

- **项目名称**: 狗狗数据助手 (Dog Data Assistant)
- **技术栈**: Flutter 3.x + Dart
- **后端API**: Flask (已有)
- **预计工期**: 6周
- **开始日期**: 2026-05-12
- **目标完成**: 2026-06-22

---

## 🗓️ Week 1: 基础搭建

### 目标
完成Flutter环境配置、项目初始化、核心基础设施搭建

### 任务清单

#### Day 1: 环境准备
- [ ] 安装Flutter SDK (3.x)
- [ ] 配置Android Studio / VS Code
- [ ] 安装Android模拟器 / iOS模拟器
- [ ] 运行 `flutter doctor` 确保环境正常
- [ ] 学习Dart语言基础（变量、函数、类、异步）

**学习资源**:
- https://flutter.dev/docs/get-started/install
- https://dart.dev/guides/language/language-tour

**验收标准**: 
- ✅ flutter doctor无错误
- ✅ 能运行hello world示例

---

#### Day 2: 项目初始化
- [ ] 创建Flutter项目: `flutter create dog_app`
- [ ] 建立目录结构（参考产品文档4.2节）
- [ ] 配置pubspec.yaml依赖
- [ ] 创建.gitignore
- [ ] 编写README.md

**依赖包**:
```yaml
dependencies:
  flutter:
    sdk: flutter
  # 网络请求
  dio: ^5.4.0
  # 状态管理
  provider: ^6.1.1
  # 路由
  go_router: ^12.0.0
  # 本地存储
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  # UI组件
  fluttertoast: ^8.2.4
  cached_network_image: ^3.3.0
  # 图表
  fl_chart: ^0.66.0
  # 工具
  intl: ^0.19.0
  logger: ^2.0.2+1
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  mockito: ^5.4.4
```

**验收标准**:
- ✅ 项目能正常运行
- ✅ 目录结构完整
- ✅ Git仓库初始化

---

#### Day 3: 配置与工具类
- [ ] 创建API配置 (api_config.dart)
- [ ] 创建主题配置 (theme_config.dart)
- [ ] 封装HTTP客户端 (http_client.dart)
- [ ] 创建日志工具 (logger.dart)
- [ ] 创建验证工具 (validators.dart)
- [ ] 创建日期格式化工具 (date_formatter.dart)

**代码示例 - api_config.dart**:
```dart
class ApiConfig {
  static const String baseUrl = 'http://192.168.1.100:5000';
  
  // 认证
  static const String login = '$baseUrl/login';
  static const String register = '$baseUrl/register';
  
  // AI助手
  static const String chat = '$baseUrl/api/ai/chat';
  static const String sessions = '$baseUrl/api/ai/sessions';
  
  // 预警
  static const String alerts = '$baseUrl/api/alerts';
  
  // 偏好
  static const String preferences = '$baseUrl/api/user/preferences';
}
```

**验收标准**:
- ✅ 所有工具类可正常使用
- ✅ API地址可配置

---

#### Day 4: 数据模型
- [ ] 创建User模型
- [ ] 创建Breed模型
- [ ] 创建ChatMessage模型
- [ ] 创建Alert模型
- [ ] 创建Notification模型
- [ ] 实现fromJson/toJson方法

**代码示例 - user.dart**:
```dart
class User {
  final int id;
  final String username;
  final String? email;
  final String? avatar;
  
  User({
    required this.id,
    required this.username,
    this.email,
    this.avatar,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      avatar: json['avatar'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'avatar': avatar,
    };
  }
}
```

**验收标准**:
- ✅ 所有模型类创建完成
- ✅ JSON序列化正常

---

#### Day 5: 服务层
- [ ] 封装AuthService（登录、注册、Token管理）
- [ ] 封装ApiService（通用API调用）
- [ ] 封装StorageService（本地存储）
- [ ] 实现Token自动刷新机制
- [ ] 实现请求拦截器

**验收标准**:
- ✅ 能成功调用登录API
- ✅ Token正确保存和读取
- ✅ 请求拦截器正常工作

---

#### Day 6: 路由与导航
- [ ] 配置go_router路由
- [ ] 定义所有页面路由
- [ ] 实现路由守卫（需要登录的页面）
- [ ] 测试页面跳转

**代码示例 - app_router.dart**:
```dart
final router = GoRouter(
  routes: [
    GoRoute(
      path: '/login',
      builder: (context, state) => LoginScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => HomeScreen(),
    ),
    // ... 其他路由
  ],
);
```

**验收标准**:
- ✅ 所有页面可正常跳转
- ✅ 未登录用户无法访问受保护页面

---

#### Day 7: 登录/注册页面
- [ ] 设计登录页面UI
- [ ] 实现登录功能
- [ ] 设计注册页面UI
- [ ] 实现注册功能
- [ ] 表单验证
- [ ] 错误提示
- [ ] 加载状态

**UI要求**:
- 简洁美观
- 输入框有图标
- 密码可见性切换
- 记住我选项
- 忘记密码链接（暂不实现）

**验收标准**:
- ✅ 能成功登录
- ✅ 表单验证正常
- ✅ 错误提示友好

---

### Week 1 交付物
- ✅ 完整的Flutter项目脚手架
- ✅ 可运行的登录/注册功能
- ✅ 基础架构代码
- ✅ 开发环境配置文档

---

## 🗓️ Week 2: 首页与图表

### 目标
实现首页数据看板和图表展示功能

### 任务清单

#### Day 8-9: 首页布局
- [ ] 设计首页Tab导航（BottomNavigationBar）
- [ ] 创建首页框架
- [ ] 实现8个指标卡片
- [ ] 下拉刷新功能
- [ ] 快捷导航按钮
- [ ] 热门品种列表

**UI组件**:
- 渐变色卡片
- 数字动画
- 网格布局
- ListView

**验收标准**:
- ✅ 首页布局美观
- ✅ 数据正确显示
- ✅ 下拉刷新正常

---

#### Day 10-11: 图表页面
- [ ] 创建图表列表页
- [ ] 集成fl_chart库
- [ ] 实现价格散点图
- [ ] 实现体重折线图
- [ ] 实现体型分布柱状图

**技术要点**:
- fl_chart基本用法
- 自定义图表样式
- 触摸交互
- 数据格式化

**验收标准**:
- ✅ 3种图表正常显示
- ✅ 交互流畅
- ✅ 样式美观

---

#### Day 12-13: 更多图表
- [ ] 实现店铺TOP10直方图
- [ ] 实现价格漏斗图
- [ ] 实现世界地图（简化版）
- [ ] 图表详情页
- [ ] 图表导出功能（可选）

**验收标准**:
- ✅ 6种图表全部实现
- ✅ 图表详情可查看

---

#### Day 14: 优化与测试
- [ ] 性能优化
- [ ] UI细节调整
- [ ] 编写Widget测试
- [ ] Bug修复

---

### Week 2 交付物
- ✅ 完整的首页功能
- ✅ 6种数据图表
- ✅ 流畅的用户体验

---

## 🗓️ Week 3: AI助手

### 目标
实现AI智能助手的完整功能

### 任务清单

#### Day 15-16: 聊天界面
- [ ] 设计聊天UI（类似微信）
- [ ] 实现消息列表
- [ ] 实现消息气泡
- [ ] 输入框组件
- [ ] 发送消息功能
- [ ] 滚动到底部

**UI组件**:
- ListView.builder
- CustomPaint（消息气泡）
- TextField
- IconButton

**验收标准**:
- ✅ 聊天界面美观
- ✅ 消息发送正常
- ✅ 自动滚动

---

#### Day 17-18: 会话管理
- [ ] 创建会话列表页
- [ ] 新建会话
- [ ] 切换会话
- [ ] 删除会话
- [ ] 会话标题自动生成
- [ ] 最近会话置顶

**验收标准**:
- ✅ 会话CRUD正常
- ✅ 切换流畅

---

#### Day 19-20: 高级功能
- [ ] 上下文记忆（10轮对话）
- [ ] 快速问题模板
- [ ] 图表在对话中显示
- [ ] 报告生成
- [ ] 收藏回答
- [ ] 反馈机制

**验收标准**:
- ✅ 所有高级功能可用
- ✅ 用户体验良好

---

#### Day 21: 测试与优化
- [ ] Widget测试
- [ ] 性能优化
- [ ] Bug修复

---

### Week 3 交付物
- ✅ 完整的AI助手功能
- ✅ 流畅的聊天体验
- ✅ 会话管理完善

---

## 🗓️ Week 4: 预警与个人中心

### 目标
实现P1级别的重要功能

### 任务清单

#### Day 22-23: 价格预警
- [ ] 创建预警页面
- [ ] 创建预警表单
- [ ] 实现预警CRUD
- [ ] 预警列表展示
- [ ] 预警触发逻辑

**验收标准**:
- ✅ 预警功能完整
- ✅ 数据同步正常

---

#### Day 24: 通知中心
- [ ] 通知列表页
- [ ] 未读标记
- [ ] 标记已读
- [ ] 批量操作
- [ ] 通知详情

**验收标准**:
- ✅ 通知管理正常

---

#### Day 25-26: 用户偏好
- [ ] 偏好设置页面
- [ ] 体型选择器
- [ ] 预算滑块
- [ ] 经验等级选择
- [ ] 个性化推荐列表
- [ ] 收藏管理

**验收标准**:
- ✅ 偏好设置保存
- ✅ 推荐准确

---

#### Day 27: 个人中心
- [ ] 个人信息页
- [ ] 头像上传
- [ ] 修改密码
- [ ] 使用统计
- [ ] 关于页面
- [ ] 意见反馈
- [ ] 清除缓存

**验收标准**:
- ✅ 个人中心功能完整

---

#### Day 28: 测试
- [ ] 集成测试
- [ ] Bug修复

---

### Week 4 交付物
- ✅ 预警系统完整
- ✅ 个人中心完善
- ✅ RC版本可用

---

## 🗓️ Week 5: 优化与测试

### 目标
性能优化、全面测试、Bug修复

### 任务清单

#### Day 29-30: 性能优化
- [ ] 启动速度优化
- [ ] 内存占用优化
- [ ] 图片缓存优化
- [ ] 列表渲染优化
- [ ] 网络请求优化

**优化手段**:
- 懒加载
- 图片压缩
- 数据分页
- 缓存策略

**验收标准**:
- ✅ 启动时间 < 3秒
- ✅ 内存 < 100MB
- ✅ FPS ≥ 55

---

#### Day 31-32: 单元测试
- [ ] 模型测试
- [ ] 服务层测试
- [ ] 工具类测试
- [ ] 目标覆盖率70%

---

#### Day 33-34: Widget测试
- [ ] 页面渲染测试
- [ ] 交互测试
- [ ] 状态变化测试
- [ ] 目标覆盖率50%

---

#### Day 35: 集成测试
- [ ] 登录流程测试
- [ ] 聊天流程测试
- [ ] 预警创建测试
- [ ] 异常场景测试

---

### Week 5 交付物
- ✅ 性能达标
- ✅ 测试覆盖率达标
- ✅ Bug修复完成
- ✅ Release版本稳定

---

## 🗓️ Week 6: 打包发布

### 目标
打包APP，编写文档，正式发布

### 任务清单

#### Day 36-37: Android打包
- [ ] 配置Android签名
- [ ] 生成APK
- [ ] 测试APK安装
- [ ] 兼容性测试

---

#### Day 38: iOS打包（如有Mac）
- [ ] 配置iOS证书
- [ ] 生成IPA
- [ ] TestFlight测试

---

#### Day 39-40: 文档编写
- [ ] 用户手册
- [ ] 开发者文档
- [ ] API对接说明
- [ ] 常见问题FAQ

---

#### Day 41: 演示材料
- [ ] 录制演示视频
- [ ] 截图制作
- [ ] PPT准备

---

#### Day 42: 最终整理
- [ ] GitHub仓库整理
- [ ] README完善
- [ ] 代码审查
- [ ] 发布Release

---

### Week 6 交付物
- ✅ Android APK
- ✅ 完整文档
- ✅ 演示视频
- ✅ GitHub仓库

---

## 📊 进度跟踪表

| 周次 | 计划任务 | 实际完成 | 进度 | 备注 |
|------|---------|---------|------|------|
| Week 1 | 基础搭建 | | | |
| Week 2 | 首页与图表 | | | |
| Week 3 | AI助手 | | | |
| Week 4 | 预警与个人中心 | | | |
| Week 5 | 优化与测试 | | | |
| Week 6 | 打包发布 | | | |

---

## ⚠️ 注意事项

1. **每日站立会议**（自我回顾）
   - 昨天完成了什么？
   - 今天计划做什么？
   - 遇到什么问题？

2. **代码规范**
   - 遵循Dart官方规范
   - 使用flutter_lints
   - 定期代码审查

3. **Git提交**
   - 小步提交
   - 清晰的commit message
   - 分支管理（main, develop, feature/*）

4. **学习方式**
   - 遇到问题先查官方文档
   - 善用Stack Overflow
   - 记录学习笔记

---

**计划制定者**: AI Assistant  
**制定日期**: 2026-05-11  
**版本**: v1.0
