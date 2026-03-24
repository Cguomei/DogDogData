"""
2.5D 宠物功能自动化测试脚本
测试范围：资源加载、DOM 结构、动画效果、交互功能
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json


class PetTestSuite:
    """宠物功能测试套件"""
    
    def __init__(self, base_url='http://127.0.0.1:5000'):
        self.base_url = base_url
        self.results = []
        
    def setup_driver(self):
        """配置浏览器驱动"""
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 注释掉无头模式，改用有头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-software-rasterizer')
        return webdriver.Chrome(options=chrome_options)
    
    def test_resource_loading(self):
        """测试 1: 资源文件加载"""
        print("\n📦 测试 1: 资源文件加载")
        driver = self.setup_driver()
        
        try:
            # 测试精灵图文件
            sprite_files = [
                '/static/img/pet_sprites/eat_cycle.png',
                '/static/img/pet_sprites/pet_cycle.png',
                '/static/img/pet_sprites/eating_rotation.png',
                '/static/img/pet_sprites/petting_smooth.png'
            ]
            
            loaded_count = 0
            for sprite_url in sprite_files:
                driver.get(f'{self.base_url}{sprite_url}')
                # 检查是否 404
                if '404' not in driver.current_url:
                    loaded_count += 1
            
            success = loaded_count == len(sprite_files)
            self.results.append(('资源加载', success, f'{loaded_count}/{len(sprite_files)}'))
            print(f"  {'✅' if success else '❌'} 精灵图：{loaded_count}/{len(sprite_files)}")
            
            return success
        finally:
            driver.quit()
    
    def test_pet_container_creation(self):
        """测试 2: 宠物容器创建"""
        print("\n🏗️ 测试 2: 宠物容器创建")
        driver = self.setup_driver()
        
        try:
            driver.get(self.base_url)
            time.sleep(3)  # 增加等待时间（包括 500ms 延迟 + 加载时间）
            
            # 检查容器
            try:
                container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'virtual-pet-container'))
                )
                self.results.append(('容器创建', True, '成功'))
                print("  ✅ 宠物容器已创建")
                return True
            except Exception as e:
                # 获取页面源码调试
                source = driver.page_source
                has_script = 'pet.js' in source
                has_init = 'VirtualPet' in source
                print(f"     页面包含 pet.js: {has_script}")
                print(f"     页面包含初始化：{has_init}")
                print(f"     错误：{e}")
                self.results.append(('容器创建', False, f'未找到 (JS: {has_script}, Init: {has_init})'))
                print("  ❌ 宠物容器未创建")
                return False
        finally:
            driver.quit()
    
    def test_pet_body_structure(self):
        """测试 3: 宠物 DOM 结构"""
        print("\n🔍 测试 3: 宠物 DOM 结构")
        driver = self.setup_driver()
        
        try:
            driver.get(self.base_url)
            time.sleep(2)
            
            checks = {
                'pet-body-2d5': False,
                'pet-sprite': False,
                'pet-shadow': False,
                'pet-bubble': False
            }
            
            for class_name in checks.keys():
                try:
                    element = driver.find_element(By.CLASS_NAME, class_name)
                    checks[class_name] = True
                except:
                    pass
            
            success_count = sum(checks.values())
            total = len(checks)
            
            for name, found in checks.items():
                print(f"  {'✅' if found else '❌'} {name}: {'存在' if found else '缺失'}")
            
            self.results.append(('DOM 结构', success_count == total, f'{success_count}/{total}'))
            return success_count == total
        finally:
            driver.quit()
    
    def test_css_animation(self):
        """测试 4: CSS 动画效果"""
        print("\n🎬 测试 4: CSS 动画效果")
        driver = self.setup_driver()
        
        try:
            driver.get(self.base_url)
            time.sleep(2)
            
            try:
                pet_body = driver.find_element(By.CLASS_NAME, 'pet-body-2d5')
                animation = pet_body.value_of_css_property('animation')
                
                has_animation = animation and animation != 'none'
                self.results.append(('CSS 动画', has_animation, animation[:50] if has_animation else '无'))
                print(f"  {'✅' if has_animation else '❌'} 动画状态：{'运行中' if has_animation else '未启动'}")
                return has_animation
            except Exception as e:
                self.results.append(('CSS 动画', False, str(e)))
                print(f"  ❌ 动画检测失败：{e}")
                return False
        finally:
            driver.quit()
    
    def test_mouse_interaction(self):
        """测试 5: 鼠标交互（2.5D 旋转）"""
        print("\n🖱️ 测试 5: 鼠标交互（2.5D 旋转）")
        driver = self.setup_driver()
        
        try:
            driver.get(self.base_url)
            time.sleep(2)
            
            actions = ActionChains(driver)
            body = driver.find_element(By.TAG_NAME, 'body')
            
            # 移动到中心
            actions.move_to_element_with_offset(body, 960, 540).perform()
            time.sleep(1)
            
            # 移动到左上角
            actions.move_to_element_with_offset(body, 100, 100).perform()
            time.sleep(1)
            
            # 检查是否有 transform 变化
            pet_body = driver.find_element(By.CLASS_NAME, 'pet-body-2d5')
            style = pet_body.get_attribute('style')
            
            has_transform = style and ('transform' in style or 'rotate' in style)
            self.results.append(('鼠标交互', has_transform, '有旋转' if has_transform else '无变化'))
            print(f"  {'✅' if has_transform else '❌'} 2.5D 旋转：{'正常' if has_transform else '失效'}")
            return has_transform
        finally:
            driver.quit()
    
    def test_sprite_background(self):
        """测试 6: 精灵图背景设置"""
        print("\n🖼️ 测试 6: 精灵图背景设置")
        driver = self.setup_driver()
        
        try:
            driver.get(self.base_url)
            time.sleep(2)
            
            try:
                pet_sprite = driver.find_element(By.CLASS_NAME, 'pet-sprite')
                bg_image = pet_sprite.value_of_css_property('background-image')
                
                has_bg = bg_image and bg_image != 'none'
                self.results.append(('精灵图背景', has_bg, bg_image[:60] if has_bg else '无'))
                print(f"  {'✅' if has_bg else '❌'} 背景图：{'已设置' if has_bg else '未设置'}")
                return has_bg
            except Exception as e:
                self.results.append(('精灵图背景', False, str(e)))
                print(f"  ❌ 背景检测失败：{e}")
                return False
        finally:
            driver.quit()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 开始 2.5D 宠物功能自动化测试")
        print("=" * 70)
        
        tests = [
            self.test_resource_loading,
            self.test_pet_container_creation,
            self.test_pet_body_structure,
            self.test_css_animation,
            self.test_mouse_interaction,
            self.test_sprite_background
        ]
        
        passed = 0
        failed = 0
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"  ❌ 测试异常：{e}")
        
        # 输出总结
        print("\n" + "=" * 70)
        print("📊 测试结果总结")
        print("=" * 70)
        print(f"✅ 通过：{passed}/{len(tests)}")
        print(f"❌ 失败：{failed}/{len(tests)}")
        print(f"📈 通过率：{passed/len(tests)*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, success, detail in self.results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}: {detail}")
        
        print("=" * 70)
        
        return failed == 0


if __name__ == '__main__':
    suite = PetTestSuite()
    success = suite.run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！宠物功能正常")
    else:
        print("\n❌ 部分测试失败，请检查修复")
        print("\n💡 建议手动访问 http://127.0.0.1:5000/test-pet 进行验证")
