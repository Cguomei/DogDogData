"""
宠物功能快速检查脚本
直接检查代码和日志，不依赖浏览器
"""
import os
from datetime import datetime

def check_pet_implementation():
    """检查宠物功能实现"""
    print("=" * 60)
    print("🔍 检查宠物功能实现")
    print("=" * 60)
    
    results = []
    
    # ===== 检查 1: 检查日志系统文件 =====
    print("\n📋 检查 1: 日志系统文件")
    logger_file = r'static\JS\pet-logger.js'
    if os.path.exists(logger_file):
        print(f"✅ 文件存在：{logger_file}")
        results.append("✅ 日志系统文件存在")
        
        # 读取文件内容检查关键代码
        with open(logger_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'saveLogs' in content and '/api/save_pet_logs' in content:
                print("✅ 日志保存功能已实现")
                results.append("✅ 日志保存功能已实现")
            else:
                print("❌ 日志保存功能未实现")
                results.append("❌ 日志保存功能未实现")
    else:
        print(f"❌ 文件不存在：{logger_file}")
        results.append("❌ 日志系统文件不存在")
    
    # ===== 检查 2: 检查宠物脚本 =====
    print("\n📋 检查 2: 宠物脚本")
    pet_js_file = r'static\JS\pet.js'
    if os.path.exists(pet_js_file):
        print(f"✅ 文件存在：{pet_js_file}")
        results.append("✅ 宠物脚本文件存在")
        
        # 检查关键代码
        with open(pet_js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否使用 SVG
            if 'svg' in content.lower() or 'SVG' in content:
                print("✅ 使用 SVG 绘制宠物")
                results.append("✅ 使用 SVG 绘制宠物")
            else:
                print("⚠️ 可能未使用 SVG")
                results.append("⚠️ 可能未使用 SVG")
            
            # 检查单例模式
            if 'petInitDone' in content or 'petInitializing' in content:
                print("✅ 实现了单例模式")
                results.append("✅ 实现了单例模式")
            else:
                print("❌ 未实现单例模式")
                results.append("❌ 未实现单例模式")
    else:
        print(f"❌ 文件不存在：{pet_js_file}")
        results.append("❌ 宠物脚本文件不存在")
    
    # ===== 检查 3: 检查 base.html =====
    print("\n📋 检查 3: base.html 配置")
    base_html_file = r'templates\base.html'
    if os.path.exists(base_html_file):
        print(f"✅ 文件存在：{base_html_file}")
        results.append("✅ base.html 文件存在")
        
        with open(base_html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否加载日志系统
            if 'pet-logger.js' in content:
                print("✅ 加载了日志系统")
                results.append("✅ 加载了日志系统")
            else:
                print("❌ 未加载日志系统")
                results.append("❌ 未加载日志系统")
            
            # 检查是否加载宠物脚本
            if 'pet.js' in content:
                print("✅ 加载了宠物脚本")
                results.append("✅ 加载了宠物脚本")
            else:
                print("❌ 未加载宠物脚本")
                results.append("❌ 未加载宠物脚本")
            
            # 检查初始化代码
            if 'new VirtualPet' in content:
                print("✅ 有初始化代码")
                results.append("✅ 有初始化代码")
            else:
                print("❌ 没有初始化代码")
                results.append("❌ 没有初始化代码")
    else:
        print(f"❌ 文件不存在：{base_html_file}")
        results.append("❌ base.html 文件不存在")
    
    # ===== 检查 4: 检查后端 API =====
    print("\n📋 检查 4: 后端日志 API")
    app_py_file = r'app.py'
    if os.path.exists(app_py_file):
        with open(app_py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if '/api/save_pet_logs' in content:
                print("✅ 日志 API 已实现")
                results.append("✅ 日志 API 已实现")
            else:
                print("❌ 日志 API 未实现")
                results.append("❌ 日志 API 未实现")
    else:
        print(f"❌ 文件不存在：{app_py_file}")
        results.append("❌ app.py 文件不存在")
    
    # ===== 检查 5: 检查 log 文件夹 =====
    print("\n📋 检查 5: log 文件夹")
    log_dir = r'log'
    if os.path.exists(log_dir):
        print(f"✅ 文件夹存在：{log_dir}")
        results.append("✅ log 文件夹存在")
        
        # 列出日志文件
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
        if log_files:
            print(f"✅ 找到 {len(log_files)} 个日志文件:")
            for f in log_files[-3:]:  # 只显示最近 3 个
                print(f"   - {f}")
            results.append(f"✅ 找到 {len(log_files)} 个日志文件")
        else:
            print("⚠️ log 文件夹中没有日志文件（正常，需要运行后才会生成）")
            results.append("⚠️ log 文件夹中没有日志文件")
    else:
        print(f"❌ 文件夹不存在：{log_dir}")
        results.append("❌ log 文件夹不存在")
    
    # ===== 检查 6: 检查 CSS 文件 =====
    print("\n📋 检查 6: CSS 样式")
    pet_css_file = r'static\CSS\pet.css'
    if os.path.exists(pet_css_file):
        print(f"✅ 文件存在：{pet_css_file}")
        results.append("✅ CSS 文件存在")
        
        with open(pet_css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查尺寸
            if 'width: 100px' in content or 'width:100px' in content:
                print("✅ 宠物尺寸设置为 100px")
                results.append("✅ 宠物尺寸合适")
            elif 'width' in content:
                print("⚠️ 宠物尺寸可能不合适")
                results.append("⚠️ 宠物尺寸可能不合适")
    else:
        print(f"❌ 文件不存在：{pet_css_file}")
        results.append("❌ CSS 文件不存在")
    
    # ===== 输出总结 =====
    print("\n" + "=" * 60)
    print("📊 检查总结")
    print("=" * 60)
    
    for result in results:
        print(result)
    
    # 统计
    passed = sum(1 for r in results if r.startswith('✅'))
    failed = sum(1 for r in results if r.startswith('❌'))
    warnings = sum(1 for r in results if r.startswith('⚠️'))
    
    print("\n" + "-" * 60)
    print(f"总计：{len(results)} 项检查")
    print(f"✅ 通过：{passed} 项")
    print(f"❌ 失败：{failed} 项")
    print(f"⚠️ 警告：{warnings} 项")
    print("=" * 60)
    
    # 保存检查报告
    from pathlib import Path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 使用绝对路径，保存到 Test/test_pet_report/ 目录
    report_dir = Path(__file__).parent / 'Test' / 'test_pet_report'
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f'pet_check_report_{timestamp}.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("🔍 宠物功能实现检查报告\n")
        f.write("=" * 60 + "\n\n")
        
        for result in results:
            f.write(result + "\n")
        
        f.write("\n" + "-" * 60 + "\n")
        f.write(f"总计：{len(results)} 项检查\n")
        f.write(f"✅ 通过：{passed} 项\n")
        f.write(f"❌ 失败：{failed} 项\n")
        f.write(f"⚠️ 警告：{warnings} 项\n")
        f.write("=" * 60 + "\n")
        f.write(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n📄 检查报告已保存到：{report_file}")
    
    return results

if __name__ == '__main__':
    check_pet_implementation()
