"""
优化后的项目测试脚本
测试新的路由结构和模块化设计
"""

import sys
import os

# 设置测试环境变量，避免自动创建应用实例
os.environ["TESTING"] = "1"


def test_imports():
    """测试所有模块是否可以正常导入"""
    print("测试模块导入...")
    try:
        # 测试核心模块
        from app import app, db, create_app

        print("✓ app 模块导入成功")

        # 测试路由模块
        from routes.main import main_bp
        from routes.auth import auth_bp
        from routes.api import api_bp

        print("✓ 路由模块导入成功")

        # 测试模型
        from models import User, DogBreed

        print("✓ 模型模块导入成功")

        # 测试配置
        from config import get_config, Config

        print("✓ 配置模块导入成功")

        # 测试图表
        from charts import get_dashboard_stats_from_summary

        print("✓ 图表模块导入成功")

        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


# 全局应用实例，避免多次创建
_app_instance = None


def get_app_instance():
    """获取应用实例（单例模式）"""
    global _app_instance
    if _app_instance is None:
        from app import create_app

        _app_instance = create_app()
    return _app_instance


def test_app_creation():
    """测试应用创建"""
    print("\n测试应用创建...")
    try:
        app = get_app_instance()
        print("✓ 应用创建成功")

        # 测试蓝图注册
        blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"✓ 注册的蓝图: {blueprints}")

        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.rule} -> {rule.endpoint}")
        print(f"✓ 总路由数: {len(routes)}")

        return True
    except Exception as e:
        print(f"✗ 应用创建失败: {e}")
        return False


def test_route_structure():
    """测试路由结构"""
    print("\n测试路由结构...")
    try:
        app = get_app_instance()

        # 检查主要路由
        main_routes = [
            "/",
            "/charts",
            "/admin/breeds",
            "/map",
            "/chart/scatter",
            "/chart/line",
            "/chart/bar",
            "/chart/hist",
            "/chart/funnel",
            "/chart/map",
        ]
        auth_routes = ["/login", "/logout", "/register"]
        api_routes = [
            "/api/breeds",
            "/api/food",
            "/api/save_pet_logs",
            "/custom-analysis",
            "/api/upload-data",
            "/api/generate-chart",
            "/test-pet",
            "/clear-cache",
            "/api/restart",
        ]

        all_routes = [rule.rule for rule in app.url_map.iter_rules()]

        print("检查主要路由:")
        for route in main_routes:
            if route in all_routes:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} (未找到)")

        for route in auth_routes:
            if route in all_routes:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} (未找到)")

        for route in api_routes:
            if route in all_routes:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} (未找到)")

        return True
    except Exception as e:
        print(f"✗ 路由结构测试失败: {e}")
        return False


def test_blueprint_organization():
    """测试蓝图组织"""
    print("\n测试蓝图组织...")
    try:
        app = get_app_instance()

        # 检查蓝图
        blueprints = {}
        for rule in app.url_map.iter_rules():
            blueprint_name = (
                rule.endpoint.split(".")[0] if "." in rule.endpoint else "default"
            )
            if blueprint_name not in blueprints:
                blueprints[blueprint_name] = []
            blueprints[blueprint_name].append(rule.rule)

        print("蓝图路由分布:")
        for bp_name, routes in blueprints.items():
            print(f"  {bp_name}: {len(routes)} 条路由")
            if len(routes) <= 5:  # 只显示前5条
                for route in routes:
                    print(f"    - {route}")

        return True
    except Exception as e:
        print(f"✗ 蓝图组织测试失败: {e}")
        return False


def test_requirements():
    """测试 requirements.txt"""
    print("\n测试 requirements.txt...")
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否有重复依赖
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("#")
        ]
        duplicates = []
        seen = set()
        for line in lines:
            package = line.split("==")[0].strip()
            if package in seen:
                duplicates.append(package)
            seen.add(package)

        if duplicates:
            print(f"✗ 发现重复依赖: {duplicates}")
            return False
        else:
            print("✓ 没有重复依赖")

        # 检查分类
        categories = [
            "核心依赖",
            "数据库",
            "数据处理",
            "数据可视化",
            "安全",
            "测试",
            "工具",
        ]
        found_categories = [cat for cat in categories if cat in content]
        print(f"✓ 依赖分类: {', '.join(found_categories)}")

        return True
    except Exception as e:
        print(f"✗ requirements.txt 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("优化后项目测试")
    print("=" * 70)

    tests = [
        ("模块导入", test_imports),
        ("应用创建", test_app_creation),
        ("路由结构", test_route_structure),
        ("蓝图组织", test_blueprint_organization),
        ("依赖管理", test_requirements),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n总计: {total} | 通过: {passed} | 失败: {total - passed}")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
