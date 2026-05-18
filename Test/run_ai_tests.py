"""
AI助手测试运行脚本
一键运行所有AI相关测试
"""

import subprocess
import sys
import os
import shlex


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"命令: {cmd}\n")

    cmd_list = shlex.split(cmd, posix=False)
    result = subprocess.run(cmd_list, capture_output=False)

    if result.returncode == 0:
        print(f"✅ {description} - 通过")
    else:
        print(f"❌ {description} - 失败")

    return result.returncode


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🤖 AI智能助手 - 自动化测试套件")
    print("=" * 60)

    # 检查Flask是否运行
    print("\n📋 前置检查...")
    try:
        import requests

        response = requests.get("http://localhost:5000/", timeout=2)
        print("✅ Flask应用正在运行")
        flask_running = True
    except:
        print("⚠️  Flask应用未运行，部分测试将跳过")
        print("   提示: 先运行 'python app.py' 启动应用")
        flask_running = False

    # 测试结果统计
    total_tests = 0
    passed_tests = 0

    # 1. 问题分类器测试（不需要Flask）
    print("\n" + "=" * 60)
    print("第1步: 问题分类器测试")
    print("=" * 60)

    cmd = "pytest Test/api_tests/test_ai_assistant.py::TestQuestionClassifier -v --tb=short"
    result = run_command(cmd, "问题分类器测试")

    if result == 0:
        passed_tests += 6
        total_tests += 6
    else:
        total_tests += 6

    # 2. API功能测试（需要Flask）
    if flask_running:
        print("\n" + "=" * 60)
        print("第2步: API功能测试")
        print("=" * 60)

        cmd = (
            "pytest Test/api_tests/test_ai_assistant.py::TestAIAssistant -v --tb=short"
        )
        result = run_command(cmd, "API功能测试")

        if result == 0:
            passed_tests += 15
            total_tests += 15
        else:
            total_tests += 15
    else:
        print("\n⏭️  跳过API功能测试（Flask未运行）")

    # 3. UI测试（可选）
    ui_choice = input("\n是否运行UI测试？(y/n，需要Playwright): ").strip().lower()

    if ui_choice == "y":
        print("\n" + "=" * 60)
        print("第3步: UI界面测试")
        print("=" * 60)

        cmd = "pytest Test/ui_tests/test_ai_chat.py -v --tb=short --headed"
        result = run_command(cmd, "UI界面测试")

        if result == 0:
            passed_tests += 10
            total_tests += 10
        else:
            total_tests += 10
    else:
        print("\n⏭️  跳过UI测试")

    # 4. 生成报告
    report_choice = input("\n是否生成HTML测试报告？(y/n): ").strip().lower()

    if report_choice == "y":
        print("\n" + "=" * 60)
        print("第4步: 生成测试报告")
        print("=" * 60)

        cmd = "pytest Test/api_tests/test_ai_assistant.py -v --html=reports/ai_test_report.html --self-contained-html"
        run_command(cmd, "生成HTML报告")

        print(f"\n📄 报告已生成: reports/ai_test_report.html")

    # 5. 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    if total_tests > 0:
        pass_rate = (passed_tests / total_tests) * 100
        print(f"\n总测试数: {total_tests}")
        print(f"通过数量: {passed_tests}")
        print(f"通过率: {pass_rate:.1f}%")

        if pass_rate >= 90:
            print("\n🎉 优秀！测试通过率很高")
        elif pass_rate >= 70:
            print("\n✅ 良好！大部分测试通过")
        elif pass_rate >= 50:
            print("\n⚠️  一般！需要修复一些测试")
        else:
            print("\n❌ 需要改进！很多测试失败")
    else:
        print("\n⚠️  没有执行任何测试")

    print("\n" + "=" * 60)
    print("感谢使用AI助手测试套件！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试运行出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
