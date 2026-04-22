"""
用户行为埋点 API 测试
测试事件追踪、批量提交、统计分析等功能
"""
import pytest
from Test.test_framework import test_case


class TestAnalyticsAPI:
    """埋点 API 测试套件"""
    
    @test_case('TC-ANALYTICS-001', priority='High', expected='记录单个事件成功')
    def test_track_single_event(self, client):
        """测试记录单个事件"""
        response = client.post('/api/analytics/track', json={
            'event_name': 'button_click',
            'event_category': 'click',
            'event_label': 'export_chart',
            'page_url': '/chart/1',
            'properties': {
                'chart_type': 'bar',
                'data_points': 100
            }
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert 'event_id' in data
        
        print(f"✅ 事件记录成功，ID: {data['event_id']}")
    
    @test_case('TC-ANALYTICS-002', priority='High', expected='批量记录事件')
    def test_batch_track_events(self, client):
        """测试批量记录事件"""
        events = [
            {
                'event_name': 'page_view',
                'event_category': 'page_view',
                'page_url': '/home'
            },
            {
                'event_name': 'button_click',
                'event_category': 'click',
                'event_label': 'login_button'
            },
            {
                'event_name': 'api_call',
                'event_category': 'api_call',
                'event_label': 'get_data'
            }
        ]
        
        response = client.post('/api/analytics/batch', json={
            'events': events
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert data['count'] == 3
        
        print(f"✅ 批量记录成功，共 {data['count']} 个事件")
    
    @test_case('TC-ANALYTICS-003', priority='Critical', expected='验证必填字段')
    def test_track_event_validation(self, client):
        """测试事件记录验证"""
        # 缺少 event_name
        response = client.post('/api/analytics/track', json={
            'event_category': 'click'
        })
        assert response.status_code == 400
        
        # 正常记录
        response = client.post('/api/analytics/track', json={
            'event_name': 'test_event'
        })
        assert response.status_code == 201
        
        print("✅ 事件验证正常")
    
    @test_case('TC-ANALYTICS-004', priority='Medium', expected='支持多种事件分类')
    def test_event_categories(self, client):
        """测试多种事件分类"""
        categories = ['page_view', 'click', 'api_call', 'error', 'custom']
        
        for category in categories:
            response = client.post('/api/analytics/track', json={
                'event_name': f'test_{category}',
                'event_category': category
            })
            assert response.status_code == 201, f"分类 {category} 应该有效"
        
        print("✅ 多种事件分类支持正常")
    
    @test_case('TC-ANALYTICS-005', priority='Medium', expected='自动解析 User-Agent')
    def test_user_agent_parsing(self, client):
        """测试 User-Agent 自动解析"""
        # 模拟 Chrome Windows
        response = client.post('/api/analytics/track', 
            json={'event_name': 'test'},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        assert response.status_code == 201
        
        # 模拟 Safari macOS
        response = client.post('/api/analytics/track',
            json={'event_name': 'test2'},
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
        )
        assert response.status_code == 201
        
        print("✅ User-Agent 解析正常")
    
    @test_case('TC-ANALYTICS-006', priority='High', expected='获取事件列表（管理员）')
    def test_get_events_admin(self, admin_client):
        """测试管理员获取事件列表"""
        # 先记录一些事件
        for i in range(5):
            admin_client.post('/api/analytics/track', json={
                'event_name': f'test_event_{i}',
                'event_category': 'test'
            })
        
        # 获取事件列表（已登录为管理员）
        response = admin_client.get('/api/analytics/events?page=1&per_page=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'events' in data
        assert 'pagination' in data
        
        print(f"✅ 事件列表获取成功，共 {len(data['events'])} 条")
    
    @test_case('TC-ANALYTICS-007', priority='High', expected='需要管理员权限')
    def test_analytics_requires_admin(self, client, create_test_users):
        """测试分析接口需要管理员权限"""
        # 普通用户登录
        client.post('/auth/login', data={
            'username': 'user',
            'password': 'Test@123456'
        }, follow_redirects=True)
        
        # 尝试获取事件列表（应该失败）
        response = client.get('/api/analytics/events')
        assert response.status_code == 403
        
        print("✅ 管理员权限验证正常")
    
    @test_case('TC-ANALYTICS-008', priority='Medium', expected='事件筛选功能')
    def test_event_filtering(self, admin_client):
        """测试事件筛选功能"""
        # 记录不同类型事件
        admin_client.post('/api/analytics/track', json={
            'event_name': 'page_home',
            'event_category': 'page_view'
        })
        admin_client.post('/api/analytics/track', json={
            'event_name': 'click_button',
            'event_category': 'click'
        })
        
        # 按分类筛选（已登录为管理员）
        response = admin_client.get('/api/analytics/events?event_category=page_view')
        assert response.status_code == 200, f"请求失败: {response.status_code}"
        
        data = response.get_json()
        assert 'events' in data, f"响应中没有 events 字段: {data}"
        
        for event in data['events']:
            assert event['event_category'] == 'page_view'
        
        print("✅ 事件筛选功能正常")
    
    @test_case('TC-ANALYTICS-009', priority='Low', expected='批量提交限制')
    def test_batch_limit(self, client):
        """测试批量提交数量限制"""
        # 创建 101 个事件（超过限制）
        events = [{'event_name': f'event_{i}'} for i in range(101)]
        
        response = client.post('/api/analytics/batch', json={
            'events': events
        })
        
        assert response.status_code == 400
        
        print("✅ 批量提交限制正常")
    
    @test_case('TC-ANALYTICS-010', priority='Medium', expected='自定义属性存储')
    def test_custom_properties(self, client):
        """测试自定义属性存储"""
        properties = {
            'user_action': 'download',
            'file_size': 1024,
            'duration_ms': 500,
            'nested': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        response = client.post('/api/analytics/track', json={
            'event_name': 'file_download',
            'properties': properties
        })
        
        assert response.status_code == 201
        
        print("✅ 自定义属性存储正常")
    
    @test_case('TC-ANALYTICS-011', priority='High', expected='获取统计数据')
    def test_get_analytics_stats(self, admin_client):
        """测试获取统计数据"""
        # 记录多个事件
        for i in range(10):
            admin_client.post('/api/analytics/track', json={
                'event_name': f'test_event_{i % 3}',
                'event_category': ['page_view', 'click', 'api_call'][i % 3]
            })
        
        # 获取统计（已登录为管理员）
        response = admin_client.get('/api/analytics/stats?days=7')
        assert response.status_code == 200, f"请求失败: {response.status_code}"
        
        data = response.get_json()
        stats = data['stats']
        
        assert 'total_events' in stats
        assert 'unique_users' in stats
        assert 'by_category' in stats
        assert 'top_events' in stats
        
        print(f"✅ 统计数据获取成功:")
        print(f"   总事件数: {stats['total_events']}")
        print(f"   独立用户: {stats['unique_users']}")
        print(f"   分类统计: {stats['by_category']}")
    
    @test_case('TC-ANALYTICS-012', priority='Medium', expected='转化漏斗数据')
    def test_conversion_funnel(self, admin_client):
        """测试转化漏斗数据"""
        # 模拟漏斗步骤
        funnel_events = [
            'page_view_home',
            'click_register',
            'page_view_register',
            'submit_register',
            'register_success'
        ]
        
        for event in funnel_events:
            admin_client.post('/api/analytics/track', json={
                'event_name': event,
                'event_category': 'funnel'
            })
        
        # 获取漏斗数据（已登录为管理员）
        response = admin_client.get('/api/analytics/funnel?days=7')
        assert response.status_code == 200, f"请求失败: {response.status_code}"
        
        data = response.get_json()
        assert 'funnel' in data
        
        funnel = data['funnel']
        assert len(funnel) > 0
        
        # 验证转化率计算
        if funnel[0]['count'] > 0:
            assert 'conversion_rate' in funnel[0]
        
        print(f"✅ 转化漏斗数据获取成功，共 {len(funnel)} 个步骤")
    
    @test_case('TC-ANALYTICS-013', priority='Low', expected='会话 ID 追踪')
    def test_session_tracking(self, client):
        """测试会话 ID 追踪"""
        session_id = 'test-session-12345'
        
        # 记录同一会话的多个事件
        for i in range(3):
            response = client.post('/api/analytics/track', json={
                'event_name': f'session_event_{i}',
                'session_id': session_id
            })
            assert response.status_code == 201
        
        print(f"✅ 会话追踪正常，Session ID: {session_id}")
    
    @test_case('TC-ANALYTICS-014', priority='Medium', expected='分页查询')
    def test_events_pagination(self, admin_client):
        """测试事件分页查询"""
        # 创建多个事件
        for i in range(25):
            admin_client.post('/api/analytics/track', json={
                'event_name': f'paginated_event_{i}'
            })
        
        # 查询第一页（已登录为管理员）
        response = admin_client.get('/api/analytics/events?page=1&per_page=10')
        assert response.status_code == 200, f"请求失败: {response.status_code}"
        
        data = response.get_json()
        assert 'events' in data, f"响应中没有 events 字段: {data}"
        assert len(data['events']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['total'] >= 25
        
        print(f"✅ 分页查询正常，第1页 {len(data['events'])} 条，总共 {data['pagination']['total']} 条")
    
    @test_case('TC-ANALYTICS-015', priority='Low', expected='时间范围筛选')
    def test_date_range_filter(self, admin_client):
        """测试时间范围筛选"""
        from datetime import datetime, timedelta
        
        # 查询最近 7 天（已登录为管理员）
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        response = admin_client.get(f'/api/analytics/events?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}')
        assert response.status_code == 200, f"请求失败: {response.status_code}"
        
        print("✅ 时间范围筛选正常")


# 性能测试
@pytest.mark.performance
class TestAnalyticsPerformance:
    """埋点性能测试"""
    
    def test_batch_track_performance(self, client):
        """测试批量追踪性能"""
        import time
        
        # 创建 50 个事件
        events = [
            {
                'event_name': f'perf_event_{i}',
                'event_category': 'performance_test',
                'properties': {'index': i}
            }
            for i in range(50)
        ]
        
        start_time = time.time()
        
        response = client.post('/api/analytics/batch', json={
            'events': events
        })
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 201
        
        print(f"\n📊 批量追踪性能:")
        print(f"  50 个事件提交时间: {elapsed*1000:.1f}ms")
        print(f"  平均每个事件: {(elapsed/50)*1000:.1f}ms")
        
        # 应该在 1 秒内完成
        assert elapsed < 1.0, f"批量提交太慢: {elapsed:.2f}秒"
    
    def test_analytics_query_performance(self, admin_client):
        """测试分析查询性能"""
        import time
        
        # 先创建一些数据
        for i in range(100):
            admin_client.post('/api/analytics/track', json={
                'event_name': f'query_perf_{i % 10}',
                'event_category': 'perf_test'
            })
        
        start_time = time.time()
        
        # 查询统计数据（已登录为管理员）
        response = admin_client.get('/api/analytics/stats?days=7')
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        print(f"\n📊 统计查询性能:")
        print(f"  查询时间: {elapsed*1000:.1f}ms")
        
        # 应该在 500ms 内完成
        assert elapsed < 0.5, f"统计查询太慢: {elapsed:.2f}秒"
