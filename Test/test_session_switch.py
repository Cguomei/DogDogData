"""
测试会话切换和数据保存功能
"""
import requests
import json

BASE_URL = 'http://localhost:5000'


def login():
    """登录获取session"""
    session = requests.Session()
    response = session.get(f"{BASE_URL}/login")
    
    # 提取CSRF token
    import re
    match = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', response.text)
    csrf_token = match.group(1) if match else None
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'remember': False
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"✅ 登录状态: {response.status_code}")
    
    return session


def test_create_multiple_sessions(session):
    """测试创建多个会话"""
    print("\n=== 测试创建多个会话 ===")
    
    session_ids = []
    for i in range(3):
        response = session.post(f"{BASE_URL}/api/ai/sessions", json={
            'title': f'测试会话 {i+1}'
        })
        
        data = response.json()
        if data.get('success'):
            session_id = data['session_id']
            session_ids.append(session_id)
            print(f"✅ 创建会话 {i+1}: ID={session_id}")
        else:
            print(f"❌ 创建失败: {data.get('error')}")
    
    return session_ids


def test_send_messages_to_sessions(session, session_ids):
    """测试向不同会话发送消息"""
    print("\n=== 测试向会话发送消息 ===")
    
    messages = [
        "泰迪有什么特点？",
        "金毛的价格是多少？",
        "适合新手养的狗狗有哪些？"
    ]
    
    for i, session_id in enumerate(session_ids):
        response = session.post(f"{BASE_URL}/api/ai/chat", json={
            'message': messages[i],
            'session_id': session_id
        })
        
        data = response.json()
        if data.get('success'):
            print(f"✅ 会话 {session_id} 发送消息成功")
            print(f"   回答预览: {data['answer'][:50]}...")
        else:
            print(f"❌ 会话 {session_id} 发送失败: {data.get('error')}")


def test_get_session_messages(session, session_id):
    """测试获取指定会话的消息"""
    print(f"\n=== 测试获取会话 {session_id} 的消息 ===")
    
    response = session.get(f"{BASE_URL}/api/ai/sessions/{session_id}/messages")
    data = response.json()
    
    if data.get('success'):
        print(f"✅ 获取成功，共 {data['message_count']} 条消息")
        for msg in data['messages']:
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"   {role_icon} {content_preview}")
        return True
    else:
        print(f"❌ 获取失败: {data.get('error')}")
        return False


def test_switch_sessions(session, session_ids):
    """测试切换会话"""
    print("\n=== 测试切换会话 ===")
    
    for i, session_id in enumerate(session_ids):
        print(f"\n--- 切换到会话 {i+1} (ID={session_id}) ---")
        success = test_get_session_messages(session, session_id)
        if success:
            print(f"✅ 会话 {i+1} 切换成功")
        else:
            print(f"❌ 会话 {i+1} 切换失败")


def test_empty_session(session):
    """测试空会话的显示"""
    print("\n=== 测试空会话 ===")
    
    response = session.post(f"{BASE_URL}/api/ai/sessions", json={
        'title': '空会话测试'
    })
    
    data = response.json()
    if data.get('success'):
        empty_session_id = data['session_id']
        print(f"✅ 创建空会话: ID={empty_session_id}")
        
        # 获取空会话的消息
        response = session.get(f"{BASE_URL}/api/ai/sessions/{empty_session_id}/messages")
        data = response.json()
        
        if data.get('success'):
            print(f"✅ 空会话消息数: {data['message_count']}")
            if data['message_count'] == 0:
                print("✅ 空会话正确返回0条消息")
            else:
                print(f"⚠️  警告: 空会话应该有0条消息，实际有 {data['message_count']} 条")
        else:
            print(f"❌ 获取空会话消息失败: {data.get('error')}")
    else:
        print(f"❌ 创建空会话失败: {data.get('error')}")


def main():
    print("=" * 60)
    print("开始测试会话切换和数据保存功能")
    print("=" * 60)
    
    # 登录
    session = login()
    
    # 测试流程
    print("\n1. 创建多个会话")
    session_ids = test_create_multiple_sessions(session)
    
    if not session_ids:
        print("❌ 无法继续测试，会话创建失败")
        return
    
    print("\n2. 向各会话发送消息")
    test_send_messages_to_sessions(session, session_ids)
    
    print("\n3. 测试切换会话并加载消息")
    test_switch_sessions(session, session_ids)
    
    print("\n4. 测试空会话")
    test_empty_session(session)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("- 打开浏览器访问 http://localhost:5000/ai-chat")
    print("- 在左侧会话列表中点击不同的会话")
    print("- 观察是否有加载动画和通知提示")
    print("- 检查消息是否正确显示")
    print("- 创建新会话并发送消息，然后切换回来验证数据是否保存")


if __name__ == '__main__':
    main()
