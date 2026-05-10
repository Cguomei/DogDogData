"""
AI助手完整测试套件
运行所有AI相关的API和UI测试
"""
import subprocess
import sys
from pathlib import Path


def run_api_tests():
    """运行API测试"""
    print("\n" + "="*60)
    print("🧪 运行AI助手 API 测试")
    print("="*60 + "\n")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "Test/api_tests/test_ai_assistant.py",
        "-v",
        "--tb=short",
        "-x"  # 遇到第一个失败就停止
    ], cwd=Path(__file__).parent)
    
    return result.returncode == 0


def run_ui_tests():
    """运行UI测试（需要Playwright）"""
    print("\n" + "="*60)
    print("🎭 运行AI助手 UI 测试（Playwright）")
    print("="*60 + "\n")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "Test/ui_tests/test_ai_chat.py",
            "-v",
            "--tb=short",
            "-x",
            "--headed"  # 显示浏览器窗口
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️  Playwright未安装，跳过UI测试")
        print("   安装命令: pip install playwright && playwright install")
        return True  # 不算失败


def run_question_classifier_tests():
    """运行问题分类器单元测试"""
    print("\n" + "="*60)
    print("🔍 运行问题分类器单元测试")
    print("="*60 + "\n")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "Test/api_tests/test_ai_assistant.py::TestQuestionClassifier",
        "-v",
        "--tb=short"
    ], cwd=Path(__file__).parent)
    
    return result.returncode == 0


def main():
    """主函数"""
    print("\n" + "🚀 AI助手自动化测试套件")
    print("="*60)
    print("开始时间:", subprocess.check_output(["date"], shell=True).decode().strip())
    
    results = {
        "API测试": False,
        "UI测试": False,
        "分类器测试": False
    }
    
    # 1. 运行问题分类器测试（最快）
    results["分类器测试"] = run_question_classifier_tests()
    
    # 2. 运行API测试
    results["API测试"] = run_api_tests()
    
    # 3. 运行UI测试（可选）
    choice = input("\n是否运行UI测试？(y/n，需要浏览器): ").strip().lower()
    if choice == 'y':
        results["UI测试"] = run_ui_tests()
    else:
        print("⏭️  跳过UI测试")
        results["UI测试"] = None
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for test_name, passed in results.items():
        if passed is True:
            status = "✅ 通过"
        elif passed is False:
            status = "❌ 失败"
        else:
            status = "⏭️  跳过"
        print(f"{test_name:15} {status}")
    
    # 计算通过率
    total = sum(1 for v in results.values() if v is not None)
    passed = sum(1 for v in results.values() if v is True)
    
    if total > 0:
        rate = (passed / total) * 100
        print(f"\n总通过率: {passed}/{total} ({rate:.1f}%)")
    
    print("="*60)
    
    # 返回退出码
    if all(v in [True, None] for v in results.values()):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查日志")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
