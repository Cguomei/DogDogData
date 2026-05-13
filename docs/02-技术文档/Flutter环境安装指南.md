# Flutter 环境安装指南

## 📦 Windows系统安装Flutter

### 方法一：官方安装包（推荐）

#### Step 1: 下载Flutter SDK
1. 访问 https://flutter.dev/docs/get-started/install/windows
2. 下载最新稳定版 Flutter SDK
3. 解压到合适位置，例如：`C:\src\flutter`

**注意**：不要将Flutter安装在需要管理员权限的目录（如 `C:\Program Files`）

---

#### Step 2: 配置环境变量
1. 打开"系统属性" → "高级" → "环境变量"
2. 在"用户变量"中找到 `Path`
3. 点击"编辑" → "新建"
4. 添加：`C:\src\flutter\bin`
5. 点击"确定"保存

---

#### Step 3: 验证安装
打开新的命令行窗口，运行：
```bash
flutter --version
```

应该看到类似输出：
```
Flutter 3.x.x • channel stable • https://github.com/flutter/flutter.git
Framework • revision xxxxx • 2026-xx-xx
Engine • revision xxxxx
Tools • Dart 3.x.x • DevTools 2.x.x
```

---

#### Step 4: 运行Flutter Doctor
```bash
flutter doctor
```

这会检查您的环境并显示需要安装的组件。

---

### 方法二：使用Git克隆（备选）

```bash
git clone https://github.com/flutter/flutter.git -b stable C:\src\flutter
```

然后配置环境变量（同上）。

---

## 🔧 安装Android开发环境

### Step 1: 安装Android Studio
1. 下载：https://developer.android.com/studio
2. 安装时选择默认选项
3. 启动Android Studio，完成初始设置

---

### Step 2: 安装Android SDK
在Android Studio中：
1. 打开 `Settings` → `Appearance & Behavior` → `System Settings` → `Android SDK`
2. 勾选以下组件：
   - ✅ Android SDK Platform (最新稳定版)
   - ✅ Android SDK Platform-Tools
   - ✅ Android SDK Build-Tools
   - ✅ Android Emulator
3. 点击"Apply"安装

---

### Step 3: 配置Android SDK路径
```bash
flutter config --android-sdk C:\Users\YourName\AppData\Local\Android\Sdk
```

---

### Step 4: 接受Android许可证
```bash
flutter doctor --android-licenses
```

按 `y` 接受所有许可证。

---

## 📱 设置Android模拟器

### 方法一：通过Android Studio
1. 打开Android Studio
2. 点击 `Tools` → `Device Manager`
3. 点击"Create Device"
4. 选择设备（推荐：Pixel 5）
5. 选择系统镜像（推荐：API 33）
6. 完成创建

### 方法二：通过命令行
```bash
flutter emulators --create [--name xyz]
flutter emulators --launch <emulator_id>
```

---

## 💻 VS Code配置（推荐IDE）

### Step 1: 安装VS Code
下载：https://code.visualstudio.com/

---

### Step 2: 安装Flutter插件
1. 打开VS Code
2. 进入扩展市场（Ctrl+Shift+X）
3. 搜索"Flutter"
4. 点击安装（会自动安装Dart插件）

---

### Step 3: 配置Flutter路径
1. 打开VS Code设置（Ctrl+,）
2. 搜索"flutter sdk"
3. 设置 `Flutter: Sdk Path` 为：`C:\src\flutter`

---

## ✅ 最终验证

运行以下命令确保一切正常：

```bash
flutter doctor
```

理想输出应该是：
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.x.x, on Microsoft Windows ...)
[✓] Windows Version (Installed version of Windows is version 10 or higher)
[✓] Android toolchain - develop for Android devices (Android SDK version 34.0.0)
[✓] Chrome - develop for the web
[✓] Visual Studio - develop Windows apps (Visual Studio Community 2022 ...)
[✓] Android Studio (version 2023.1)
[✓] VS Code (version 1.x.x)
[✓] Connected device (3 available)
[✓] Network resources

• No issues found!
```

如果有红色❌或黄色⚠️警告，根据提示修复。

---

## 🚀 快速测试

创建一个测试项目验证环境：

```bash
flutter create test_app
cd test_app
flutter run
```

如果能看到模拟器上运行APP，说明环境配置成功！

---

## ⚠️ 常见问题

### 问题1: flutter命令找不到
**原因**: 环境变量未配置或配置错误  
**解决**: 重新配置Path环境变量，重启命令行

---

### 问题2: Android licenses not accepted
**解决**: 
```bash
flutter doctor --android-licenses
```

---

### 问题3: 模拟器无法启动
**原因**: BIOS未开启虚拟化  
**解决**: 
1. 重启电脑进入BIOS
2. 找到Virtualization Technology
3. 设置为Enabled
4. 保存重启

---

### 问题4: Gradle构建失败
**解决**: 
```bash
# 清理项目
flutter clean

# 删除.gradle缓存
rm -rf ~/.gradle/caches/

# 重新构建
flutter pub get
flutter run
```

---

### 问题5: 网络问题导致下载失败
**解决**: 配置国内镜像

在环境变量中添加：
```
PUB_HOSTED_URL=https://pub.flutter-io.cn
FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
```

---

## 📚 学习资源

### 官方文档
- Flutter官网: https://flutter.dev
- Dart语言: https://dart.dev
- Flutter中文网: https://flutterchina.club

### 视频教程
- B站Flutter教程: 搜索"Flutter入门"
- YouTube: Flutter Official Channel

### 书籍推荐
- 《Flutter实战》- wendux
- 《Flutter技术入门与实战》- 亢少军

---

## 🎯 下一步

环境安装完成后，继续执行：
1. ✅ Week 1 Day 2: 项目初始化
2. ✅ 创建Flutter项目
3. ✅ 配置依赖包

祝您安装顺利！🚀
