"""
强制清除缓存并验证宠物功能
适用于浏览器缓存导致的 MIME 类型错误
"""
import requests
import webbrowser
import time
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def check_mime_type():
    """检查 JS 文件的 MIME 类型"""
    print_header("步骤 1: 检查 JS 文件 MIME 类型")
    
    try:
        r = requests.get('http://127.0.0.1:5000/static/js/pet.js', 
                        headers={'Cache-Control': 'no-cache'})
        content_type = r.headers.get('Content-Type', '')
        
        if 'application/javascript' in content_type:
            print(f"{Fore.GREEN}✅ JS 文件 MIME 类型正确{Style.RESET_ALL}")
            print(f"   Content-Type: {content_type}")
            return True
        else:
            print(f"{Fore.RED}❌ JS 文件 MIME 类型错误{Style.RESET_ALL}")
            print(f"   Content-Type: {content_type}")
            print(f"   应该是：application/javascript")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ 请求失败：{e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 请确保 Flask 应用正在运行{Style.RESET_ALL}")
        return False

def check_cache_headers():
    """检查页面缓存控制头"""
    print_header("步骤 2: 检查页面缓存控制")
    
    try:
        r = requests.get('http://127.0.0.1:5000/test-pet')
        cache_control = r.headers.get('Cache-Control', '')
        pragma = r.headers.get('Pragma', '')
        expires = r.headers.get('Expires', '')
        
        print(f"Cache-Control: {cache_control}")
        print(f"Pragma: {pragma}")
        print(f"Expires: {expires}")
        
        if 'no-cache' in cache_control and 'no-store' in cache_control:
            print(f"{Fore.GREEN}✅ 页面缓存已禁用{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  页面缓存未完全禁用{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ 请求失败：{e}{Style.RESET_ALL}")
        return False

def open_clear_cache_page():
    """打开清除缓存指南页面"""
    print_header("步骤 3: 打开清除缓存指南")
    
    url = 'http://127.0.0.1:5000/clear-cache'
    print(f"正在打开：{url}")
    webbrowser.open(url)
    print(f"{Fore.GREEN}✅ 已在浏览器中打开清除缓存指南{Style.RESET_ALL}")

def open_test_page():
    """打开测试页面"""
    print_header("步骤 4: 打开测试页面")
    
    url = 'http://127.0.0.1:5000/test-pet'
    print(f"正在打开：{url}")
    webbrowser.open(url)
    print(f"{Fore.GREEN}✅ 已在浏览器中打开测试页面{Style.RESET_ALL}")

def main():
    print_header("🔄 强制清除缓存验证工具 v2.5.2")
    
    # 检查应用是否运行
    print(f"{Fore.CYAN}🔍 检测 Flask 应用状态...{Style.RESET_ALL}")
    try:
        r = requests.get('http://127.0.0.1:5000/', timeout=3)
        print(f"{Fore.GREEN}✅ Flask 应用正在运行{Style.RESET_ALL}\n")
    except:
        print(f"{Fore.RED}❌ Flask 应用未运行{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 请先启动应用：python app.py{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 或双击运行：restart_flask.bat{Style.RESET_ALL}\n")
        input("按回车键退出...")
        return
    
    # 执行检查
    mime_ok = check_mime_type()
    cache_ok = check_cache_headers()
    
    if mime_ok and cache_ok:
        print_header("✅ 所有检查通过！")
        print(f"""
{Fore.GREEN}【下一步操作】{Style.RESET_ALL}

1. 按 Ctrl + Shift + Delete 清除浏览器缓存
   - 时间范围：全部时间
   - 勾选"缓存的图片和文件"
   - 点击"清除数据"

2. 强制刷新页面
   - Windows: Ctrl + Shift + R
   - Mac: Cmd + Shift + R

3. 如果还有问题，访问清除缓存指南页面：
   http://127.0.0.1:5000/clear-cache

4. 打开测试页面：
   http://127.0.0.1:5000/test-pet
""")
    else:
        print_header("⚠️ 发现问题")
        print(f"""
{Fore.YELLOW}【建议操作】{Style.RESET_ALL}

1. 立即访问清除缓存指南页面：
   http://127.0.0.1:5000/clear-cache

2. 按照页面上的步骤操作：
   - 关闭所有浏览器窗口
   - 清除浏览器缓存
   - 重启 Flask 应用
   - 重新打开测试页面

3. 或者手动操作：
   - 按 Ctrl + Shift + Delete
   - 清除"全部时间"的缓存
   - 强制刷新 Ctrl + Shift + R
""")
    
    # 自动打开测试页面
    choice = input("\n是否现在打开测试页面？(y/n): ").strip().lower()
    if choice == 'y':
        open_test_page()
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}完成！{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    input("按回车键退出...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  用户中断{Style.RESET_ALL}")
