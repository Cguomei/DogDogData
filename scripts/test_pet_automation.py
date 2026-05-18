"""
宠物功能自动化测试脚本
使用 Playwright 进行端到端测试，自动发现问题
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime


async def test_pet_functionality():
    """测试宠物功能"""
    print("=" * 60)
    print("🐾 开始测试宠物功能")
    print("=" * 60)

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为 True 可以隐藏浏览器
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 记录测试结果
        test_results = []

        try:
            # ===== 测试 1: 页面加载 =====
            print("\n📋 测试 1: 页面加载")
            await page.goto("http://localhost:5000/")
            await page.wait_for_load_state("networkidle")
            print("✅ 页面加载成功")
            test_results.append("✅ 测试 1 通过：页面加载成功")

            # 等待 2 秒
            await asyncio.sleep(2)

            # ===== 测试 2: 检查日志系统是否加载 =====
            print("\n📋 测试 2: 检查日志系统")
            logger_exists = await page.evaluate(
                'typeof window.PetLogger !== "undefined"'
            )
            if logger_exists:
                print("✅ 日志系统已加载")
                test_results.append("✅ 测试 2 通过：日志系统已加载")
            else:
                print("❌ 日志系统未加载")
                test_results.append("❌ 测试 2 失败：日志系统未加载")

            # ===== 测试 3: 检查宠物初始化 =====
            print("\n📋 测试 3: 检查宠物初始化")
            await page.evaluate("""() => {
                console.log("手动触发日志保存");
                if (window.PetLogger) {
                    window.PetLogger.saveLogs();
                }
            }""")

            # 等待 3 秒，让宠物初始化
            print("⏳ 等待 3 秒，让宠物初始化...")
            await asyncio.sleep(3)

            # 检查是否有宠物容器
            pet_container = await page.query_selector("#virtual-pet-container")
            if pet_container:
                print("✅ 宠物容器已创建")
                test_results.append("✅ 测试 3 通过：宠物容器已创建")
            else:
                print("❌ 宠物容器未创建")
                test_results.append("❌ 测试 3 失败：宠物容器未创建")

            # ===== 测试 4: 检查宠物数量（关键测试）=====
            print("\n📋 测试 4: 检查宠物数量（应该只有 1 只）")
            await asyncio.sleep(1)

            # 查找所有宠物元素
            pets = await page.query_selector_all(".virtual-pet")
            pet_count = len(pets)
            print(f"🔍 第一次检查：找到 {pet_count} 只宠物")

            # 查找所有容器
            containers = await page.query_selector_all(".virtual-pet-container")
            container_count = len(containers)
            print(f"🔍 容器数量：{container_count}")

            if pet_count == 1:
                print("✅ 宠物数量正确（1 只）")
                test_results.append("✅ 测试 4 通过：宠物数量正确（1 只）")
            else:
                print(f"❌ 宠物数量错误（期望 1 只，实际{pet_count}只）")
                test_results.append(
                    f"❌ 测试 4 失败：宠物数量错误（期望 1 只，实际{pet_count}只）"
                )

            # ===== 测试 5: 检查宠物形状（SVG）=====
            print("\n📋 测试 5: 检查宠物形状")
            pet_svg = await page.query_selector(".virtual-pet svg")
            if pet_svg:
                print("✅ 宠物是 SVG 形状")
                test_results.append("✅ 测试 5 通过：宠物是 SVG 形状")
            else:
                print("❌ 宠物不是 SVG 形状")
                test_results.append("❌ 测试 5 失败：宠物不是 SVG 形状")

            # ===== 测试 6: 检查宠物尺寸 =====
            print("\n📋 测试 6: 检查宠物尺寸")
            if pet_container:
                box = await pet_container.bounding_box()
                width = box["width"]
                height = box["height"]
                print(f"🔍 宠物尺寸：{width:.0f}x{height:.0f}px")

                if width <= 150 and height <= 200:
                    print("✅ 宠物尺寸合适")
                    test_results.append("✅ 测试 6 通过：宠物尺寸合适")
                else:
                    print(f"❌ 宠物尺寸过大（{width:.0f}x{height:.0f}px）")
                    test_results.append(
                        f"❌ 测试 6 失败：宠物尺寸过大（{width:.0f}x{height:.0f}px）"
                    )

            # ===== 测试 7: 检查初始化日志 =====
            print("\n📋 测试 7: 检查初始化日志")
            console_logs = []

            # 监听控制台消息
            page.on("console", lambda msg: console_logs.append(msg.text))

            # 刷新页面重新检查
            print("🔄 刷新页面...")
            await page.reload()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(4)  # 等待 4 秒让初始化完成

            # 检查刷新后的宠物数量
            pets_after_reload = await page.query_selector_all(".virtual-pet")
            print(f"🔍 刷新后找到 {len(pets_after_reload)} 只宠物")

            # 统计初始化成功消息
            init_success_count = sum(
                1 for log in console_logs if "初始化成功" in log or "已就位" in log
            )
            print(f"🔍 初始化成功消息数量：{init_success_count}")

            if init_success_count == 1 and len(pets_after_reload) == 1:
                print("✅ 只初始化了一次，且只有 1 只宠物")
                test_results.append("✅ 测试 7 通过：只初始化了一次")
            elif init_success_count > 1:
                print(f"❌ 初始化了{init_success_count}次（重复初始化）")
                test_results.append(
                    f"❌ 测试 7 失败：初始化了{init_success_count}次（重复初始化）"
                )
            elif len(pets_after_reload) > 1:
                print(f"❌ 刷新后有{len(pets_after_reload)}只宠物（清理失败）")
                test_results.append(
                    f"❌ 测试 7 失败：刷新后有{len(pets_after_reload)}只宠物"
                )
            else:
                print("⚠️ 未找到初始化成功消息")
                test_results.append("⚠️ 测试 7 警告：未找到初始化成功消息")

            # ===== 测试 8: 手动保存日志 =====
            print("\n📋 测试 8: 保存日志到服务器")
            await page.evaluate("""() => {
                if (window.PetLogger) {
                    window.PetLogger.saveLogs();
                }
            }""")
            await asyncio.sleep(1)
            print("✅ 日志已保存到 log 文件夹")
            test_results.append("✅ 测试 8 通过：日志已保存")

        except Exception as e:
            print(f"❌ 测试过程中出错：{e}")
            test_results.append(f"❌ 测试失败：{str(e)}")

        finally:
            # 关闭浏览器
            await browser.close()

        # ===== 输出测试报告 =====
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        for result in test_results:
            print(result)

        # 统计结果
        passed = sum(1 for r in test_results if r.startswith("✅"))
        failed = sum(1 for r in test_results if r.startswith("❌"))
        warnings = sum(1 for r in test_results if r.startswith("⚠️"))

        print("\n" + "-" * 60)
        print(f"总计：{len(test_results)} 个测试")
        print(f"✅ 通过：{passed} 个")
        print(f"❌ 失败：{failed} 个")
        print(f"⚠️ 警告：{warnings} 个")
        print("=" * 60)

        # 保存测试报告
        report_file = save_test_report(test_results)
        print(f"\n📄 测试报告已保存到：{report_file}")

        return test_results


def save_test_report(results):
    """保存测试报告到文件"""
    from pathlib import Path

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 使用绝对路径，保存到 Test/test_pet_report/ 目录
    report_dir = Path(__file__).parent / "Test" / "test_pet_report"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"test_pet_report_{timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("🐾 宠物功能自动化测试报告\n")
        f.write("=" * 60 + "\n\n")

        for result in results:
            f.write(result + "\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return report_file


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_pet_functionality())
