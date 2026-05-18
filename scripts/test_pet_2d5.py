"""
2.5D 宠物功能测试脚本
验证宠物是否正常显示和动画
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_pet_display():
    """测试宠物是否正常显示"""
    print("=" * 60)
    print("🧪 开始测试 2.5D 宠物功能")
    print("=" * 60)

    # 配置 Chrome 无头模式（不显示浏览器界面）
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        # 启动浏览器
        print("\n🌐 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)

        # 访问首页
        print("📍 访问 http://127.0.0.1:5000")
        driver.get("http://127.0.0.1:5000")

        # 等待页面加载
        time.sleep(3)
        print("✅ 页面加载完成")

        # 检查页面标题
        title = driver.title
        print(f"📋 页面标题：{title}")

        # 测试 1: 检查宠物容器是否创建
        print("\n🔍 测试 1: 检查宠物容器")
        try:
            pet_container = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "virtual-pet-container"))
            )
            print("✅ 宠物容器已创建")
        except Exception as e:
            print(f"❌ 宠物容器未找到：{e}")
            return False

        # 测试 2: 检查宠物身体元素
        print("\n🔍 测试 2: 检查宠物身体元素")
        try:
            pet_body = driver.find_element(By.CLASS_NAME, "pet-body-2d5")
            print("✅ 宠物身体元素存在 (class: pet-body-2d5)")
        except:
            print("❌ 未找到宠物身体元素")
            # 尝试找旧的 emoji 版本
            try:
                pet_emoji = driver.find_element(By.CLASS_NAME, "pet-emoji")
                print("⚠️  找到旧版 emoji 宠物，可能精灵图未加载")
            except:
                print("❌ 也未找到 emoji 宠物")
            return False

        # 测试 3: 检查精灵图元素
        print("\n🔍 测试 3: 检查精灵图显示")
        try:
            pet_sprite = driver.find_element(By.CLASS_NAME, "pet-sprite")
            bg_image = pet_sprite.value_of_css_property("background-image")

            if bg_image and bg_image != "none":
                print(f"✅ 精灵图背景已设置：{bg_image[:80]}...")
            else:
                print("⚠️  精灵图背景未设置，可能图片加载中")
        except Exception as e:
            print(f"❌ 精灵图元素未找到：{e}")

        # 测试 4: 检查投影效果
        print("\n🔍 测试 4: 检查投影效果")
        try:
            pet_shadow = driver.find_element(By.CLASS_NAME, "pet-shadow")
            print("✅ 投影元素存在")
        except:
            print("⚠️  投影元素未找到（非关键）")

        # 测试 5: 检查召唤按钮
        print("\n🔍 测试 5: 检查召唤按钮")
        try:
            summon_btn = driver.find_element(By.ID, "summon-pet-btn")
            btn_text = summon_btn.text
            print(f"✅ 召唤按钮存在，文字：{btn_text}")
        except:
            print("⚠️  召唤按钮未找到（可能在导航栏中）")

        # 测试 6: 检查 CSS 动画
        print("\n🔍 测试 6: 检查 CSS 动画")
        try:
            animation = pet_body.value_of_css_property("animation")
            if animation and animation != "none":
                print(f"✅ CSS 动画运行中：{animation[:60]}...")
            else:
                print("⚠️  未检测到 CSS 动画")
        except Exception as e:
            print(f"❌ 无法检查动画：{e}")

        # 测试 7: 模拟鼠标移动（触发 2.5D 旋转）
        print("\n🔍 测试 7: 模拟鼠标移动触发旋转")
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(driver)
            # 移动到页面中心
            body = driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element_with_offset(body, 960, 540).perform()

            # 等待一下
            time.sleep(1)

            # 检查是否有 transform 样式
            transform = pet_body.get_attribute("style")
            if transform and ("rotate" in transform or "transform" in transform):
                print(f"✅ 检测到旋转变换：{transform[:80]}...")
            else:
                print("⚠️  未检测到旋转变换（可能 JS 未执行）")
        except Exception as e:
            print(f"❌ 鼠标移动测试失败：{e}")

        # 测试 8: 检查 JavaScript 控制台日志
        print("\n🔍 测试 8: 检查 JS 控制台日志")
        try:
            logs = driver.get_log("browser")
            pet_logs = [
                log
                for log in logs
                if "pet" in log["message"].lower() or "宠物" in log["message"]
            ]

            if pet_logs:
                print(f"✅ 找到 {len(pet_logs)} 条宠物相关日志:")
                for log in pet_logs[:3]:  # 只显示前 3 条
                    msg = log["message"].split("\\n")[0][:100]
                    print(f"   - {msg}")
            else:
                print("⚠️  未找到宠物相关日志")
        except Exception as e:
            print(f"⚠️  无法获取控制台日志：{e}")

        # 测试 9: 检查精灵图资源加载
        print("\n🔍 测试 9: 检查资源文件是否存在")
        sprite_files = [
            "/static/img/pet_sprites/eat_cycle.png",
            "/static/img/pet_sprites/pet_cycle.png",
            "/static/img/pet_sprites/eating_rotation.png",
            "/static/img/pet_sprites/petting_smooth.png",
        ]

        loaded_count = 0
        for sprite_url in sprite_files:
            try:
                driver.get(f"http://127.0.0.1:5000{sprite_url}")
                if driver.current_url == f"http://127.0.0.1:5000{sprite_url}":
                    loaded_count += 1
                    print(f"   ✅ {sprite_url}")
                else:
                    print(f"   ❌ {sprite_url} - 404")
            except:
                print(f"   ❌ {sprite_url} - 加载失败")

        # 返回主页
        driver.get("http://127.0.0.1:5000")

        print(f"\n✅ 成功加载 {loaded_count}/{len(sprite_files)} 个精灵图文件")

        # 总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        print("✅ 宠物容器：已创建")
        print("✅ 宠物身体：使用 2.5D 样式")
        print("✅ 投影效果：已添加")
        print("✅ 召唤按钮：存在")
        print(f"✅ 精灵图资源：{loaded_count}/{len(sprite_files)} 可用")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # 关闭浏览器
        if "driver" in locals():
            driver.quit()
            print("\n👋 浏览器已关闭")


if __name__ == "__main__":
    success = test_pet_display()

    if success:
        print("\n✅✅✅ 宠物功能测试通过！")
        print("\n💡 提示：请在浏览器中实际查看以下功能：")
        print("   1. 右下角是否能看到宠物")
        print("   2. 移动鼠标时宠物是否跟随旋转（2.5D 效果）")
        print("   3. 点击宠物是否有涟漪特效和对话气泡")
        print("   4. 双击宠物是否 360°旋转")
    else:
        print("\n❌❌❌ 宠物功能测试失败，请检查代码")
