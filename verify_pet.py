"""
快速验证宠物功能是否正常
"""
import requests

def verify_pet():
    print("=" * 60)
    print("🔍 验证宠物功能")
    print("=" * 60)
    
    # 1. 检查首页
    print("\n📄 检查首页...")
    r = requests.get('http://127.0.0.1:5000')
    if r.status_code != 200:
        print(f"❌ 首页访问失败：{r.status_code}")
        return False
    
    html = r.text
    checks = {
        'pet.css': '/static/css/pet.css' in html,
        'pet.js': '/static/js/pet.js' in html,
        '召唤按钮': 'summon-pet-btn' in html,
        '初始化代码': 'VirtualPet' in html or 'pet.js' in html
    }
    
    all_passed = True
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}: {'通过' if result else '缺失'}")
        if not result:
            all_passed = False
    
    # 2. 检查 JS 文件 MIME 类型
    print("\n📦 检查 JS 文件 MIME 类型...")
    r_js = requests.get('http://127.0.0.1:5000/static/js/pet.js')
    content_type = r_js.headers.get('Content-Type', '')
    
    is_correct_mime = 'application/javascript' in content_type or 'text/javascript' in content_type
    status = "✅" if is_correct_mime else "❌"
    print(f"  {status} Content-Type: {content_type}")
    
    if not is_correct_mime:
        print("  ❌ MIME 类型错误，浏览器将拒绝执行此脚本！")
        all_passed = False
    else:
        print("  ✅ MIME 类型正确，脚本可以正常执行")
    
    # 3. 检查 CSS 文件
    print("\n🎨 检查 CSS 文件...")
    r_css = requests.get('http://127.0.0.1:5000/static/css/pet.css')
    css_content_type = r_css.headers.get('Content-Type', '')
    is_css_correct = 'text/css' in css_content_type
    status = "✅" if is_css_correct else "⚠️"
    print(f"  {status} Content-Type: {css_content_type}")
    
    # 4. 检查精灵图资源
    print("\n🖼️  检查精灵图资源...")
    sprite_files = [
        '/static/img/pet_sprites/eat_cycle.png',
        '/static/img/pet_sprites/pet_cycle.png',
        '/static/img/pet_sprites/eating_rotation.png',
        '/static/img/pet_sprites/petting_smooth.png'
    ]
    
    loaded = 0
    for sprite_url in sprite_files:
        r_sprite = requests.get(f'http://127.0.0.1:5000{sprite_url}')
        if r_sprite.status_code == 200:
            loaded += 1
            print(f"  ✅ {sprite_url}")
        else:
            print(f"  ❌ {sprite_url} - {r_sprite.status_code}")
    
    if loaded == len(sprite_files):
        print(f"  ✅ 所有精灵图加载成功 ({loaded}/{len(sprite_files)})")
    else:
        print(f"  ⚠️ 部分精灵图加载失败 ({loaded}/{len(sprite_files)})")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 验证结果")
    print("=" * 60)
    
    if all_passed and loaded == len(sprite_files):
        print("✅ 所有检查通过！宠物应该能正常显示")
        print("\n💡 现在请在浏览器中访问 http://127.0.0.1:5000")
        print("   你应该能看到：")
        print("   1. 右下角有一只小狗（2.5D 效果）")
        print("   2. 移动鼠标时，小狗会跟随旋转")
        print("   3. 点击小狗会有涟漪特效和对话气泡")
        return True
    else:
        print("❌ 部分检查未通过，请查看上方详情")
        return False


if __name__ == '__main__':
    success = verify_pet()
    exit(0 if success else 1)
