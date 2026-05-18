"""
环境检查脚本 - 快速验证AI助手运行环境
"""

import sys
import os


def check_python_version():
    """检查Python版本"""
    print("📌 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor} (需要3.8+)")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n📌 检查依赖包...")

    required_packages = ["flask", "sqlalchemy", "pymysql", "requests", "flask_login"]

    all_ok = True
    for package in required_packages:
        try:
            mod = __import__(package)
            version = getattr(mod, "__version__", "unknown")
            print(f"✅ {package:20s} {version}")
        except ImportError:
            print(f"❌ {package:20s} 未安装")
            all_ok = False

    return all_ok


def check_env_config():
    """检查环境变量配置"""
    print("\n📌 检查.env配置...")

    from dotenv import load_dotenv

    load_dotenv()

    required_vars = [
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
        "MODEL_TYPE",
        "LOCAL_MODEL_URL",
        "LOCAL_MODEL_NAME",
    ]

    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if "PASSWORD" in var or "SECRET" in var:
                display_value = "*" * 6
            else:
                display_value = value
            print(f"✅ {var:25s} = {display_value}")
        else:
            print(f"❌ {var:25s} 未配置")
            all_ok = False

    return all_ok


def check_routes_file():
    """检查路由文件是否存在"""
    print("\n📌 检查项目文件...")

    files_to_check = [
        "routes/ai_assistant.py",
        "templates/ai_chat.html",
        "test_ai_assistant.py",
        ".env",
    ]

    all_ok = True
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {file_path:35s} ({size:,} bytes)")
        else:
            print(f"❌ {file_path:35s} 不存在")
            all_ok = False

    return all_ok


def check_ollama_connection():
    """检查Ollama连接"""
    print("\n📌 检查本地模型服务...")

    import requests

    model_type = os.getenv("MODEL_TYPE", "ollama")
    base_url = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434")

    try:
        if model_type == "ollama":
            response = requests.get(f"{base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama服务在线")
                print(f"   可用模型: {len(models)}个")
                for model in models[:3]:  # 显示前3个
                    print(f"   - {model['name']}")
                return True
            else:
                print(f"⚠️ Ollama响应异常: {response.status_code}")
                return False
        elif model_type == "lmstudio":
            response = requests.get(f"{base_url}/v1/models", timeout=3)
            if response.status_code == 200:
                print(f"✅ LM Studio服务在线")
                return True
            else:
                print(f"⚠️ LM Studio响应异常: {response.status_code}")
                return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到{model_type}服务")
        print(f"   URL: {base_url}")
        print(f"\n💡 提示:")
        if model_type == "ollama":
            print(f"   1. 启动Ollama: ollama serve")
            print(f"   2. 下载模型: ollama pull qwen2.5:7b")
            print(f"   3. 运行模型: ollama run qwen2.5:7b")
        else:
            print(f"   1. 打开LM Studio")
            print(f"   2. 加载模型")
            print(f"   3. 启动Local Server")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def check_flask_app():
    """检查Flask应用是否可以导入"""
    print("\n📌 检查Flask应用...")

    try:
        from app import create_app

        app = create_app()
        print(f"✅ Flask应用可以正常创建")

        # 检查蓝图是否注册
        blueprints = list(app.blueprints.keys())
        if "ai_assistant" in blueprints:
            print(f"✅ AI助手蓝图已注册")
            return True
        else:
            print(f"❌ AI助手蓝图未注册")
            print(f"   已注册的蓝图: {blueprints}")
            return False
    except Exception as e:
        print(f"❌ Flask应用创建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("AI智能助手 - 环境检查")
    print("=" * 70)

    results = []

    # 执行各项检查
    results.append(("Python版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("环境配置", check_env_config()))
    results.append(("项目文件", check_routes_file()))
    results.append(("模型服务", check_ollama_connection()))
    results.append(("Flask应用", check_flask_app()))

    # 总结
    print("\n" + "=" * 70)
    print("检查结果总结")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15s} {status}")

    print("\n" + "-" * 70)
    print(f"总计: {passed}/{total} 项通过")

    if passed == total:
        print("\n🎉 所有检查通过！可以开始使用了！")
        print("\n下一步:")
        print("1. 启动Flask应用: python app.py")
        print("2. 访问聊天页面: http://localhost:5000/ai-chat")
        print("3. 运行测试脚本: python test_ai_assistant.py")
    else:
        print("\n⚠️ 存在未通过的检查项，请先解决上述问题")

    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n检查中断")
    except Exception as e:
        print(f"\n❌ 检查出错: {e}")
        import traceback

        traceback.print_exc()
