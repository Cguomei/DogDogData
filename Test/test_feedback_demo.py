"""
用户反馈系统快速演示脚本
展示反馈 API 的完整使用流程
"""
import requests
from datetime import datetime

# 配置
BASE_URL = 'http://localhost:5000'
SESSION = requests.Session()


def login(username, password):
    """登录用户"""
    print(f"\n🔐 正在登录用户: {username}")
    response = SESSION.post(f'{BASE_URL}/auth/login', data={
        'username': username,
        'password': password
    }, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ 登录成功")
        return True
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return False


def submit_feedback(feedback_type, title, content, priority='medium'):
    """提交反馈"""
    print(f"\n📝 提交反馈 [{feedback_type}]")
    response = SESSION.post(f'{BASE_URL}/api/feedback', json={
        'feedback_type': feedback_type,
        'title': title,
        'content': content,
        'priority': priority,
        'contact_email': 'demo@example.com'
    })
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 反馈提交成功，ID: {data['feedback_id']}")
        print(f"   消息: {data['message']}")
        return data['feedback_id']
    else:
        print(f"❌ 提交失败: {response.status_code}")
        print(f"   错误: {response.json().get('error')}")
        return None


def get_my_feedbacks():
    """获取我的反馈列表"""
    print("\n📋 获取我的反馈列表")
    response = SESSION.get(f'{BASE_URL}/api/feedback?page=1&per_page=5')
    
    if response.status_code == 200:
        data = response.json()
        feedbacks = data['feedbacks']
        pagination = data['pagination']
        
        print(f"✅ 共 {pagination['total']} 条反馈，当前第 {pagination['page']} 页")
        
        for i, fb in enumerate(feedbacks[:3], 1):  # 只显示前3条
            print(f"\n  {i}. [{fb['feedback_type'].upper()}] {fb['title']}")
            print(f"     状态: {fb['status']} | 优先级: {fb['priority']}")
            print(f"     创建时间: {fb['created_at']}")
        
        return feedbacks
    else:
        print(f"❌ 获取失败: {response.status_code}")
        return []


def get_feedback_detail(feedback_id):
    """获取反馈详情"""
    print(f"\n🔍 查看反馈 #{feedback_id} 详情")
    response = SESSION.get(f'{BASE_URL}/api/feedback/{feedback_id}')
    
    if response.status_code == 200:
        data = response.json()
        fb = data['feedback']
        
        print(f"  标题: {fb['title']}")
        print(f"  类型: {fb['feedback_type']}")
        print(f"  内容: {fb['content'][:100]}...")
        print(f"  状态: {fb['status']}")
        print(f"  优先级: {fb['priority']}")
        print(f"  联系邮箱: {fb['contact_email']}")
        
        if fb.get('admin_reply'):
            print(f"  管理员回复: {fb['admin_reply']}")
        
        return fb
    else:
        print(f"❌ 获取失败: {response.status_code}")
        return None


def admin_get_all_feedbacks():
    """管理员获取所有反馈"""
    print("\n👨‍💼 管理员查看所有反馈")
    response = SESSION.get(f'{BASE_URL}/api/feedback/admin/list?page=1&per_page=5')
    
    if response.status_code == 200:
        data = response.json()
        feedbacks = data['feedbacks']
        pagination = data['pagination']
        
        print(f"✅ 共 {pagination['total']} 条反馈")
        
        for i, fb in enumerate(feedbacks[:3], 1):
            username = fb.get('username', '未知')
            print(f"\n  {i}. [用户: {username}] {fb['title']}")
            print(f"     类型: {fb['feedback_type']} | 状态: {fb['status']}")
        
        return feedbacks
    else:
        print(f"❌ 获取失败: {response.status_code}")
        return []


def admin_reply_feedback(feedback_id, reply_text, new_status='processing'):
    """管理员回复反馈"""
    print(f"\n💬 管理员回复反馈 #{feedback_id}")
    response = SESSION.post(
        f'{BASE_URL}/api/feedback/{feedback_id}/reply',
        json={
            'reply': reply_text,
            'status': new_status
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 回复成功")
        print(f"   新状态: {data['feedback']['status']}")
        return True
    else:
        print(f"❌ 回复失败: {response.status_code}")
        return False


def get_feedback_stats():
    """获取反馈统计"""
    print("\n📊 获取反馈统计信息")
    response = SESSION.get(f'{BASE_URL}/api/feedback/stats')
    
    if response.status_code == 200:
        data = response.json()
        stats = data['stats']
        
        print(f"  总反馈数: {stats['total']}")
        print(f"\n  按状态:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
        
        print(f"\n  按类型:")
        for ftype, count in stats['by_type'].items():
            print(f"    {ftype}: {count}")
        
        print(f"\n  按优先级:")
        for priority, count in stats['by_priority'].items():
            print(f"    {priority}: {count}")
        
        return stats
    else:
        print(f"❌ 获取失败: {response.status_code}")
        return None


def main():
    """主函数 - 演示完整流程"""
    print("=" * 70)
    print("用户反馈系统演示")
    print("=" * 70)
    
    # 1. 普通用户登录
    print("\n" + "=" * 70)
    print("步骤 1: 普通用户登录")
    print("=" * 70)
    if not login('user', 'Test@123456'):
        print("⚠️  请先运行应用并创建测试用户")
        return
    
    # 2. 提交多个反馈
    print("\n" + "=" * 70)
    print("步骤 2: 提交多个反馈")
    print("=" * 70)
    
    feedback_id_1 = submit_feedback(
        'bug',
        '图表导出功能异常',
        '点击导出按钮后页面没有反应，控制台显示 500 错误。',
        'high'
    )
    
    feedback_id_2 = submit_feedback(
        'feature',
        '建议添加数据筛选功能',
        '希望能按照日期范围、品种等条件筛选数据，这样分析更方便。',
        'medium'
    )
    
    feedback_id_3 = submit_feedback(
        'improvement',
        '首页加载速度优化',
        '首页数据较多时加载较慢，建议增加懒加载或分页。',
        'low'
    )
    
    # 3. 查看我的反馈
    print("\n" + "=" * 70)
    print("步骤 3: 查看我的反馈列表")
    print("=" * 70)
    my_feedbacks = get_my_feedbacks()
    
    # 4. 查看单个反馈详情
    if feedback_id_1:
        print("\n" + "=" * 70)
        print("步骤 4: 查看反馈详情")
        print("=" * 70)
        get_feedback_detail(feedback_id_1)
    
    # 5. 管理员登录
    print("\n" + "=" * 70)
    print("步骤 5: 管理员登录")
    print("=" * 70)
    if not login('admin', 'Test@123456'):
        print("⚠️  请先创建管理员账户")
        return
    
    # 6. 管理员查看所有反馈
    print("\n" + "=" * 70)
    print("步骤 6: 管理员查看所有反馈")
    print("=" * 70)
    all_feedbacks = admin_get_all_feedbacks()
    
    # 7. 管理员回复反馈
    if feedback_id_1:
        print("\n" + "=" * 70)
        print("步骤 7: 管理员回复反馈")
        print("=" * 70)
        admin_reply_feedback(
            feedback_id_1,
            '感谢您的反馈！我们已经定位到问题，将在下一个版本修复。',
            'processing'
        )
    
    # 8. 查看反馈统计
    print("\n" + "=" * 70)
    print("步骤 8: 查看反馈统计")
    print("=" * 70)
    get_feedback_stats()
    
    # 9. 验证回复效果
    if feedback_id_1:
        print("\n" + "=" * 70)
        print("步骤 9: 验证回复效果")
        print("=" * 70)
        detail = get_feedback_detail(feedback_id_1)
        if detail and detail.get('admin_reply'):
            print(f"\n✅ 管理员已回复: {detail['admin_reply']}")
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("  - 访问 http://localhost:5000 体验完整功能")
    print("  - 查看 docs/Phase3_用户反馈完成报告.md 了解更多")
    print("  - 运行 pytest Test/api_tests/test_feedback.py 执行自动化测试")


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保应用正在运行:")
        print("   python app.py")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
