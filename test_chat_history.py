"""
测试对话历史API
"""
import requests

BASE_URL = 'http://localhost:5000'

# 登录获取session
def login():
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
    print(f"登录状态: {response.status_code}")
    
    return session


def test_create_session(session):
    """测试创建会话"""
    print("\n=== 测试创建会话 ===")
    
    response = session.post(f"{BASE_URL}/api/ai/sessions", json={
        'title': '测试会话'
    })
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {data}")
    
    if data.get('success'):
        print(f"✅ 会话创建成功: ID={data['session_id']}")
        return data['session_id']
    else:
        print(f"❌ 失败: {data.get('error')}")
        return None


def test_get_sessions(session):
    """测试获取会话列表"""
    print("\n=== 测试获取会话列表 ===")
    
    response = session.get(f"{BASE_URL}/api/ai/sessions")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"会话数量: {len(data.get('sessions', []))}")
    
    if data.get('success'):
        print("✅ 获取成功")
        for s in data['sessions'][:3]:  # 显示前3个
            print(f"  - ID={s['id']}, 标题={s['title']}, 消息数={s['message_count']}")
    else:
        print(f"❌ 失败: {data.get('error')}")


def test_send_message(session, session_id):
    """测试发送消息（会自动保存历史）"""
    print(f"\n=== 测试发送消息 (会话ID={session_id}) ===")
    
    response = session.post(f"{BASE_URL}/api/ai/chat", json={
        'message': '泰迪有什么特点？',
        'session_id': session_id
    })
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"✅ 发送成功")
        print(f"回答预览: {data['answer'][:100]}...")
        print(f"来源: {data.get('source', 'model')}")
        print(f"会话ID: {data.get('session_id')}")
    else:
        print(f"❌ 失败: {data.get('error')}")


def test_get_messages(session, session_id):
    """测试获取消息历史"""
    print(f"\n=== 测试获取消息历史 (会话ID={session_id}) ===")
    
    response = session.get(f"{BASE_URL}/api/ai/sessions/{session_id}/messages")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"✅ 获取成功")
        print(f"消息数量: {data['message_count']}")
        for msg in data['messages']:
            role = '👤 用户' if msg['role'] == 'user' else '🤖 AI'
            preview = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
            print(f"  {role}: {preview}")
    else:
        print(f"❌ 失败: {data.get('error')}")


def test_delete_session(session, session_id):
    """测试删除会话"""
    print(f"\n=== 测试删除会话 (ID={session_id}) ===")
    
    response = session.delete(f"{BASE_URL}/api/ai/sessions/{session_id}")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print("✅ 删除成功")
    else:
        print(f"❌ 失败: {data.get('error')}")


if __name__ == '__main__':
    print("开始测试对话历史API...\n")
    
    # 登录
    session = login()
    
    # 测试流程
    session_id = test_create_session(session)
    
    if session_id:
        test_get_sessions(session)
        test_send_message(session, session_id)
        test_get_messages(session, session_id)
        
        # 询问是否删除
        choice = input("\n是否删除测试会话？(y/n): ").strip().lower()
        if choice == 'y':
            test_delete_session(session, session_id)
    
    print("\n✅ 测试完成")
