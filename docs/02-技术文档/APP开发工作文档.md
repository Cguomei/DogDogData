# 狗狗数据助手 - APP开发工作文档

## 📱 项目概述

**项目名称**: 狗狗数据助手 (Dog Data Assistant)  
**技术栈**: Flutter 3.x + Dart  
**后端服务**: Flask API (已部署)  
**当前版本**: v4.9.11  
**文档版本**: v1.0  
**更新日期**: 2026-05-12  

---

## 🎯 核心功能模块

### 1. 用户认证系统
- ✅ 用户注册/登录
- ✅ Session认证（Cookie）
- ✅ Token管理
- ⚠️ **游客模式**: AI助手支持未登录使用

### 2. 数据看板（首页）
- 8个关键指标卡片
- 热门品种列表
- 快捷导航
- 下拉刷新

### 3. 数据可视化
- 价格散点图
- 体重折线图
- 体型分布柱状图
- 店铺TOP10直方图
- 价格漏斗图
- 世界地图（简化版）

### 4. AI智能助手
- 💬 多轮对话（上下文记忆10轮）
- 📝 会话管理（创建、切换、删除）
- 🎨 图表在对话中展示
- 📚 知识库集成（自动标注来源）
- 👤 **游客模式**: 无需登录即可使用

### 5. 预警系统
- 价格预警设置
- 品种预警
- 通知中心
- 触发提醒

### 6. 个人中心
- 个人信息管理
- 偏好设置
- 收藏管理
- 使用统计

---

## 🔌 API对接指南

### 基础配置

```dart
// lib/config/api_config.dart
class ApiConfig {
  // 开发环境
  static const String baseUrl = 'http://192.168.1.100:5000';
  
  // 生产环境（替换为实际域名）
  // static const String baseUrl = 'https://api.yourdomain.com';
  
  // 超时时间
  static const int connectTimeout = 5000; // 5秒
  static const int receiveTimeout = 30000; // 30秒
}
```

### 网络请求封装

```dart
// lib/services/http_client.dart
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class HttpClient {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: ApiConfig.connectTimeout,
    receiveTimeout: ApiConfig.receiveTimeout,
    headers: {
      'Content-Type': 'application/json',
    },
  ));

  // 添加请求拦截器 - 自动携带Cookie
  static Future<void> init() async {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // 从本地存储获取session cookie
        final prefs = await SharedPreferences.getInstance();
        final sessionId = prefs.getString('session_id');
        
        if (sessionId != null) {
          options.headers['Cookie'] = 'session=$sessionId';
        }
        
        return handler.next(options);
      },
      onResponse: (response, handler) async {
        // 保存新的session cookie
        final setCookie = response.headers['set-cookie'];
        if (setCookie != null && setCookie.isNotEmpty) {
          final sessionId = _extractSessionId(setCookie.first);
          if (sessionId != null) {
            final prefs = await SharedPreferences.getInstance();
            await prefs.setString('session_id', sessionId);
          }
        }
        
        return handler.next(response);
      },
      onError: (error, handler) {
        // 错误处理
        print('Request error: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  static String? _extractSessionId(String cookie) {
    final match = RegExp(r'session=([^;]+)').firstMatch(cookie);
    return match?.group(1);
  }

  // GET请求
  static Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }

  // POST请求
  static Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }

  // PUT请求
  static Future<Response> put(String path, {dynamic data}) {
    return _dio.put(path, data: data);
  }

  // DELETE请求
  static Future<Response> delete(String path) {
    return _dio.delete(path);
  }
}
```

---

## 📡 核心API接口

### 1. 用户认证

#### 1.1 用户注册
```dart
// POST /register
Future<bool> register(String username, String password) async {
  try {
    final response = await HttpClient.post('/register', data: {
      'username': username,
      'password': password,
    });
    
    return response.statusCode == 200;
  } catch (e) {
    print('注册失败: $e');
    return false;
  }
}
```

#### 1.2 用户登录
```dart
// POST /login
Future<Map<String, dynamic>> login(String username, String password) async {
  try {
    final response = await HttpClient.post('/login', data: {
      'username': username,
      'password': password,
    });
    
    if (response.statusCode == 200) {
      // Session cookie会自动保存
      return {'success': true};
    } else {
      return {'success': false, 'error': '用户名或密码错误'};
    }
  } catch (e) {
    return {'success': false, 'error': '网络错误'};
  }
}
```

#### 1.3 用户登出
```dart
// GET /logout
Future<void> logout() async {
  try {
    await HttpClient.get('/logout');
    
    // 清除本地session
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('session_id');
  } catch (e) {
    print('登出失败: $e');
  }
}
```

---

### 2. 品种数据

#### 2.1 获取所有品种
```dart
// GET /api/breeds
Future<List<Breed>> getBreeds() async {
  try {
    final response = await HttpClient.get('/api/breeds');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data;
      return data.map((json) => Breed.fromJson(json)).toList();
    }
    
    return [];
  } catch (e) {
    print('获取品种失败: $e');
    return [];
  }
}
```

**数据模型**:
```dart
// lib/models/breed.dart
class Breed {
  final int id;
  final String breedName;
  final double? avgLifeYears;
  final String? sizeCategory;
  final int? popularity;

  Breed({
    required this.id,
    required this.breedName,
    this.avgLifeYears,
    this.sizeCategory,
    this.popularity,
  });

  factory Breed.fromJson(Map<String, dynamic> json) {
    return Breed(
      id: json['id'],
      breedName: json['breed_name'],
      avgLifeYears: json['avg_life_years']?.toDouble(),
      sizeCategory: json['size_category'],
      popularity: json['popularity'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'breed_name': breedName,
      'avg_life_years': avgLifeYears,
      'size_category': sizeCategory,
      'popularity': popularity,
    };
  }
}
```

---

### 3. AI智能助手 ⭐核心功能

#### 3.1 发送消息（支持游客模式）
```dart
// POST /api/ai/chat
Future<Map<String, dynamic>> sendMessage({
  required String message,
  String? sessionId,
  bool chartNeeded = false,
}) async {
  try {
    final data = {
      'message': message,
      'chart_needed': chartNeeded,
    };
    
    if (sessionId != null) {
      data['session_id'] = sessionId;
    }
    
    final response = await HttpClient.post('/api/ai/chat', data: data);
    
    if (response.statusCode == 200) {
      return {
        'success': true,
        'answer': response.data['answer'],
        'sessionId': response.data['session_id'],
        'messageId': response.data['message_id'],
        'type': response.data['type'],
        'source': response.data['source'], // 'knowledge_base' or 'model'
      };
    } else {
      return {
        'success': false,
        'error': response.data['error'] ?? '服务器错误',
        'suggestion': response.data['suggestion'], // 错误建议
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': '网络错误: $e',
    };
  }
}
```

**重要说明**:
- ✅ **游客模式**: 未登录用户也可以使用，session会自动创建
- ✅ **自动会话**: 首次对话不传session_id，后端会自动创建
- ✅ **上下文记忆**: 后端自动维护10轮对话历史
- ✅ **知识库优先**: 优先从知识库回答，命中率更高
- ⚠️ **游客会话隔离**: 前端通过localStorage隔离，但数据库层面共享guest账户

#### 3.2 获取会话列表
```dart
// GET /api/ai/sessions
Future<List<ChatSession>> getSessions() async {
  try {
    final response = await HttpClient.get('/api/ai/sessions');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data['sessions'];
      final bool isGuest = response.data['is_guest'] ?? false;
      
      return data.map((json) => ChatSession.fromJson(json)).toList();
    }
    
    return [];
  } catch (e) {
    print('获取会话列表失败: $e');
    return [];
  }
}
```

**数据模型**:
```dart
// lib/models/chat_session.dart
class ChatSession {
  final int id;
  final String title;
  final int messageCount;
  final DateTime createdAt;
  final DateTime updatedAt;

  ChatSession({
    required this.id,
    required this.title,
    required this.messageCount,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      id: json['id'],
      title: json['title'],
      messageCount: json['message_count'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
```

#### 3.3 创建新会话
```dart
// POST /api/ai/sessions
Future<int?> createSession(String title) async {
  try {
    final response = await HttpClient.post('/api/ai/sessions', data: {
      'title': title,
    });
    
    if (response.statusCode == 201) {
      return response.data['session_id'];
    }
    
    return null;
  } catch (e) {
    print('创建会话失败: $e');
    return null;
  }
}
```

#### 3.4 获取会话详情（含消息历史）
```dart
// GET /api/ai/sessions/<sessionId>
Future<Map<String, dynamic>> getSessionDetail(int sessionId) async {
  try {
    final response = await HttpClient.get('/api/ai/sessions/$sessionId');
    
    if (response.statusCode == 200) {
      return {
        'success': true,
        'session': response.data['session'],
        'messages': response.data['messages'],
      };
    } else {
      return {
        'success': false,
        'error': '会话不存在',
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': '网络错误',
    };
  }
}
```

#### 3.5 检查模型状态
```dart
// GET /api/ai/model/status
Future<Map<String, dynamic>> checkModelStatus() async {
  try {
    final response = await HttpClient.get('/api/ai/model/status');
    
    if (response.statusCode == 200) {
      return {
        'status': response.data['status'], // 'online' or 'offline'
        'type': response.data['type'], // 'ollama' or 'lmstudio'
        'availableModels': response.data['available_models'],
      };
    }
    
    return {'status': 'error'};
  } catch (e) {
    return {'status': 'error', 'error': e.toString()};
  }
}
```

---

### 4. 图表数据

#### 4.1 获取图表数据
```dart
// 注意：当前图表是HTML页面，需要改为JSON API
// 建议后端新增以下接口：

// GET /api/charts/scatter - 价格散点图
// GET /api/charts/line - 体重折线图
// GET /api/charts/bar - 体型分布
// GET /api/charts/hist - TOP10直方图
// GET /api/charts/funnel - 价格漏斗
// GET /api/charts/map - 世界地图

// 临时方案：解析HTML或使用WebView展示
Future<String> getChartHtml(String chartType) async {
  try {
    final response = await HttpClient.get('/chart/$chartType');
    return response.data; // HTML字符串
  } catch (e) {
    return '';
  }
}
```

**⚠️ 待优化**: 建议后端提供纯JSON格式的图表数据API，方便Flutter渲染

---

### 5. 预警系统

#### 5.1 创建价格预警
```dart
// POST /api/alerts
Future<bool> createPriceAlert({
  required int breedId,
  required double targetPrice,
  required String alertType, // 'price_drop' or 'price_rise'
}) async {
  try {
    final response = await HttpClient.post('/api/alerts', data: {
      'breed_id': breedId,
      'target_price': targetPrice,
      'alert_type': alertType,
    });
    
    return response.statusCode == 201;
  } catch (e) {
    print('创建预警失败: $e');
    return false;
  }
}
```

#### 5.2 获取预警列表
```dart
// GET /api/alerts
Future<List<Alert>> getAlerts() async {
  try {
    final response = await HttpClient.get('/api/alerts');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data;
      return data.map((json) => Alert.fromJson(json)).toList();
    }
    
    return [];
  } catch (e) {
    print('获取预警列表失败: $e');
    return [];
  }
}
```

---

## 🎨 UI组件推荐

### 1. 聊天界面
```dart
// 推荐包: flutter_chat_ui
dependencies:
  flutter_chat_ui: ^1.6.9

// 使用示例
import 'package:flutter_chat_ui/flutter_chat_ui.dart';

Chat(
  messages: messages,
  onSendPressed: (text) {
    sendMessage(text);
  },
  user: User(id: 'user'),
  showUserAvatars: true,
  showUserNames: true,
)
```

### 2. 图表展示
```dart
// 推荐包: fl_chart
dependencies:
  fl_chart: ^0.66.0

// 散点图示例
ScatterChart(
  ScatterChartData(
    scatterSpots: [
      ScatterSpot(x: 1, y: 2500),
      ScatterSpot(x: 2, y: 3500),
    ],
  ),
)
```

### 3. 下拉刷新
```dart
RefreshIndicator(
  onRefresh: () async {
    await loadData();
  },
  child: ListView.builder(...),
)
```

### 4. Toast提示
```dart
// 推荐包: fluttertoast
dependencies:
  fluttertoast: ^8.2.4

Fluttertoast.showToast(
  msg: "操作成功",
  toastLength: Toast.LENGTH_SHORT,
  gravity: ToastGravity.BOTTOM,
);
```

---

## 🔐 安全注意事项

### 1. Session管理
```dart
// 不要在代码中硬编码敏感信息
// 使用环境变量或配置文件

// ❌ 错误做法
const String apiKey = 'your-secret-key';

// ✅ 正确做法
import 'package:flutter_dotenv/flutter_dotenv.dart';
final String apiKey = dotenv.env['API_KEY'] ?? '';
```

### 2. HTTPS
- ⚠️ **开发环境**: 可以使用HTTP
- ✅ **生产环境**: 必须使用HTTPS
- 配置Android `network_security_config.xml`允许明文传输（仅开发）

### 3. 数据存储
```dart
// 敏感数据加密存储
import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';

// 初始化加密盒子
await Hive.initFlutter();
final key = Hive.generateSecureKey();
await Hive.openBox('secure_box', encryptionCipher: HiveAesCipher(key));

// 存储Token
final box = Hive.box('secure_box');
box.put('session_id', encryptedSessionId);
```

---

## 📱 平台适配

### Android配置

**AndroidManifest.xml**:
```xml
<!-- 网络权限 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- 允许明文传输（仅开发环境） -->
<application
    android:usesCleartextTraffic="true"
    ...>
```

### iOS配置

**Info.plist**:
```xml
<!-- 允许HTTP请求（仅开发环境） -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

---

## 🧪 测试策略

### 1. 单元测试
```dart
// test/models/breed_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:dog_app/models/breed.dart';

void main() {
  test('Breed fromJson should work', () {
    final json = {
      'id': 1,
      'breed_name': '金毛',
      'avg_life_years': 12.5,
    };
    
    final breed = Breed.fromJson(json);
    
    expect(breed.id, 1);
    expect(breed.breedName, '金毛');
    expect(breed.avgLifeYears, 12.5);
  });
}
```

### 2. Widget测试
```dart
// test/widgets/chat_message_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('ChatMessage displays correctly', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChatMessage(
          text: 'Hello',
          isMe: true,
        ),
      ),
    );
    
    expect(find.text('Hello'), findsOneWidget);
  });
}
```

### 3. 集成测试
```dart
// integration_test/login_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Login flow', (tester) async {
    await tester.pumpWidget(MyApp());
    
    // 输入用户名密码
    await tester.enterText(find.byType(TextField).at(0), 'testuser');
    await tester.enterText(find.byType(TextField).at(1), '123456');
    
    // 点击登录
    await tester.tap(find.text('登录'));
    await tester.pumpAndSettle();
    
    // 验证跳转
    expect(find.text('首页'), findsOneWidget);
  });
}
```

---

## 🚀 部署流程

### 1. Android打包

```bash
# 生成密钥库
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload

# 配置android/key.properties
storePassword=<password>
keyPassword=<password>
keyAlias=upload
storeFile=<path-to-keystore>

# 构建APK
flutter build apk --release

# 构建AppBundle（推荐）
flutter build appbundle --release
```

### 2. iOS打包（需要Mac）

```bash
# 构建IPA
flutter build ios --release

# 打开Xcode进行签名和发布
open ios/Runner.xcworkspace
```

### 3. 版本号管理

**pubspec.yaml**:
```yaml
version: 1.0.0+1  # version+build_number
```

---

## 📚 学习资源

### 官方文档
- Flutter: https://flutter.dev/docs
- Dart: https://dart.dev/guides
- Dio: https://pub.dev/packages/dio
- Provider: https://pub.dev/packages/provider

### 视频教程
- B站: "Flutter从入门到实战"
- YouTube: "Flutter Official Channel"

### 社区
- Stack Overflow: #flutter
- Reddit: r/FlutterDev
- 掘金: Flutter标签

---

## ⚠️ 常见问题

### Q1: 如何处理跨域问题？
**A**: Flask后端已配置CORS，移动端不受跨域限制。

### Q2: 游客模式的会话会丢失吗？
**A**: 
- 前端: 使用localStorage/session持久化，关闭APP后仍保留
- 后端: 所有游客共享guest账户，会话存储在数据库
- ⚠️ 不同设备之间会话不互通

### Q3: 图表如何展示？
**A**: 
- 方案1（推荐）: 后端提供JSON数据，Flutter用fl_chart渲染
- 方案2（临时）: 使用WebView加载HTML图表页面

### Q4: 如何实现推送通知？
**A**: 
- 使用Firebase Cloud Messaging (FCM)
- 后端触发预警时调用FCM API
- APP接收并显示通知

### Q5: 性能优化建议？
**A**:
- 图片使用cached_network_image缓存
- 列表使用ListView.builder懒加载
- 大数据分页加载
- 避免频繁setState，使用Provider状态管理

---

## 📞 技术支持

**后端API负责人**: dev-team@example.com  
**Flutter技术问题**: Stack Overflow #flutter  
**项目文档**: docs/ 目录  

---

## 📝 更新日志

### v1.0 (2026-05-12)
- ✅ 初始版本
- ✅ 完整的API对接指南
- ✅ 游客模式说明
- ✅ 安全注意事项
- ✅ 部署流程

---

**文档维护者**: AI Assistant  
**最后更新**: 2026-05-12  
**项目版本**: v4.9.11
