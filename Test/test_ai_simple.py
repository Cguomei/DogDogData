"""
简单测试AI助手API
使用Flask测试客户端
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User

def test_ai_assistant():
    """测试AI助手功能"""
    
    # 创建测试应用
    os.environ['TESTING'] = '1'
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        print("=" * 60)
        print("AI助手简单测试")
        print("=" * 60)
        
        # Step 1: 登录
        print("\n[1] 尝试登录...")
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
        
        # Step 2: 检查模型状态
        print("\n[2] 检查模型状态...")
        response = client.get('/api/ai/model/status')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ 状态: {data.get('status')}")
            print(f"   类型: {data.get('type')}")
            print(f"   URL: {data.get('url')}")
            
            if data.get('status') != 'online':
                print("\n⚠️ 模型未在线，但继续测试...")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.data[:200]}")
            return
        
        # Step 3: 测试聊天
        print("\n[3] 测试聊天功能...")
        test_messages = [
            "金毛的价格是多少？",
            "泰迪有什么特点？",
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   [{i}] 发送: {message}")
            response = client.post('/api/ai/chat', json={
                'message': message
            })
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"   ✅ 类型: {data.get('type')}")
                    answer = data.get('answer', '')
                    print(f"   回复: {answer[:150]}...")
                else:
                    print(f"   ❌ 错误: {data.get('error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                print(f"   响应: {response.data[:200]}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

if __name__ == '__main__':
    try:
        test_ai_assistant()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
