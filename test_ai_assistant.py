"""
AI助手快速测试脚本
用于验证本地模型连接和基本功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:5000"
TEST_USER = {
    'username': 'admin',
    'password': 'admin123'
}

def login():
    """登录获取session"""
    session = requests.Session()
    
    # 先访问登录页面获取CSRF token
    response = session.get(f"{BASE_URL}/login")
    
    if response.status_code != 200:
        print(f"❌ 访问登录页面失败: {response.status_code}")
        return None
    
    # 从 HTML中提取CSRF token
    try:
        import re
        # 尝试从 meta标签获取
        match = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
        else:
            # 尝试从 form中获取
            match = re.search(r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
            else:
                csrf_token = None
        
        print(f"CSRF Token: {csrf_token[:20] + '...' if csrf_token else 'None'}")
    except Exception as e:
        print(f"⚠️ 提取CSRF token失败: {e}")
        csrf_token = None
    
    # 准备登录数据
    login_data = {
        'username': TEST_USER['username'],
        'password': TEST_USER['password'],
        'remember': False
    }
    
    # 如果有CSRF token，添加到表单数据
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    # 尝试登录
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    if response.status_code in [200, 302]:
        print("✅ 登录成功")
        return session
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        return None

def test_model_status(session):
    """测试模型状态"""
    print("\n📡 测试模型状态...")
    response = session.get(f"{BASE_URL}/api/ai/model/status")
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容前200字符: {response.text[:200]}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"状态: {data['status']}")
            print(f"类型: {data['type']}")
            print(f"URL: {data['url']}")
            return data['status'] == 'online'
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_chat(session, message):
    """测试聊天功能"""
    print(f"\n💬 发送消息: {message}")
    response = session.post(
        f"{BASE_URL}/api/ai/chat",
        json={'message': message},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 回复类型: {data['type']}")
            print(f"回复内容:\n{data['answer'][:200]}...")
            return True
        else:
            print(f"❌ 错误: {data['error']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)
        return False

def main():
    print("=" * 60)
    print("AI助手测试脚本")
    print("=" * 60)
    
    # Step 1: 登录
    session = login()
    if not session:
        return
    
    # Step 2: 检查模型状态
    model_online = test_model_status(session)
    
    if not model_online:
        print("\n⚠️ 模型未在线，请确保:")
        print("1. Ollama/LM Studio 已启动")
        print("2. 模型已下载并加载")
        print("3. .env 配置正确")
        return
    
    # Step 3: 测试不同类型的问题
    test_cases = [
        "金毛的价格是多少？",
        "泰迪有什么特点？",
        "适合新手养的狗狗",
    ]
    
    print("\n" + "=" * 60)
    print("开始测试各种问题类型")
    print("=" * 60)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n[测试 {i}/{len(test_cases)}]")
        test_chat(session, message)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("- 访问 http://localhost:5000/ai-chat 查看聊天界面")
    print("- 需要先登录才能使用")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
