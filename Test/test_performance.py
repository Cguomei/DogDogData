"""
性能测试模块
测试 API 响应时间和系统性能
"""
import pytest
import time
from statistics import mean, median, stdev
from bug_tracker import report_bug


class PerformanceTester:
    """性能测试辅助类"""
    
    def __init__(self):
        self.results = {}
    
    def measure_response_time(self, func, iterations=10):
        """测量函数执行的响应时间"""
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                func()
                end = time.time()
                times.append(end - start)
            except Exception as e:
                print(f"第 {i+1} 次执行失败：{e}")
                times.append(float('inf'))
        
        return {
            'min': min(times) if times else 0,
            'max': max(times) if times else 0,
            'avg': mean(times) if times and all(t != float('inf') for t in times) else 0,
            'median': median(times) if times else 0,
            'stdev': stdev(times) if len(times) > 1 else 0,
            'success_count': sum(1 for t in times if t != float('inf')),
            'total_count': iterations
        }


@pytest.fixture
def perf_tester():
    """提供性能测试器"""
    return PerformanceTester()


class TestAPIPerformance:
    """API 性能测试"""
    
    def test_index_page_performance(self, client, perf_tester):
        """测试首页响应时间"""
        def request():
            response = client.get('/')
            assert response.status_code == 200
        
        results = perf_tester.measure_response_time(request, iterations=5)
        
        # 记录性能数据
        print(f"\n首页性能:")
        print(f"  平均响应时间：{results['avg']*1000:.2f}ms")
        print(f"  最大响应时间：{results['max']*1000:.2f}ms")
        print(f"  最小响应时间：{results['min']*1000:.2f}ms")
        
        # 如果平均响应时间超过 2 秒，记录为性能问题
        if results['avg'] > 2.0:
            report_bug(
                title="首页响应时间过长",
                description=f"平均响应时间：{results['avg']*1000:.2f}ms，超过 2000ms 阈值",
                severity="Major",
                priority="Medium",
                module="性能",
                steps_to_reproduce=["访问首页 /"],
                expected_result="响应时间 < 2000ms",
                actual_result=f"平均响应时间：{results['avg']*1000:.2f}ms"
            )
    
    def test_api_breeds_performance(self, client, perf_tester):
        """测试获取品种列表 API 性能"""
        def request():
            response = client.get('/api/breeds')
            assert response.status_code == 200
        
        results = perf_tester.measure_response_time(request, iterations=5)
        
        print(f"\n/api/breeds 性能:")
        print(f"  平均响应时间：{results['avg']*1000:.2f}ms")
        
        # API 响应时间应该更快（< 1 秒）
        if results['avg'] > 1.0:
            report_bug(
                title="品种列表 API 响应慢",
                description=f"平均响应时间：{results['avg']*1000:.2f}ms，超过 1000ms 阈值",
                severity="Major",
                priority="Medium",
                module="性能-API",
                steps_to_reproduce=["GET /api/breeds"],
                expected_result="响应时间 < 1000ms",
                actual_result=f"平均响应时间：{results['avg']*1000:.2f}ms"
            )
    
    @pytest.mark.parametrize('endpoint,name', [
        ('/chart/scatter', '价格散点图'),
        ('/chart/line', '体重折线图'),
        ('/chart/bar', '级别柱状图'),
        ('/chart/hist', 'TOP10 直方图'),
        ('/chart/funnel', '价格漏斗图'),
        ('/chart/map', '世界地图'),
    ])
    def test_chart_pages_performance(self, client, perf_tester, endpoint, name):
        """测试图表页面性能"""
        def request():
            response = client.get(endpoint)
            assert response.status_code == 200
        
        results = perf_tester.measure_response_time(request, iterations=3)
        
        print(f"\n{name} ({endpoint}) 性能:")
        print(f"  平均响应时间：{results['avg']*1000:.2f}ms")
        
        # 图表页面可能较慢，但不应超过 5 秒
        if results['avg'] > 5.0:
            report_bug(
                title=f"{name} 加载过慢",
                description=f"平均响应时间：{results['avg']*1000:.2f}ms，超过 5000ms 阈值",
                severity="Minor",
                priority="Low",
                module="性能 - 图表",
                steps_to_reproduce=[f"访问 {endpoint}"],
                expected_result="响应时间 < 5000ms",
                actual_result=f"平均响应时间：{results['avg']*1000:.2f}ms"
            )
    
    def test_food_dashboard_performance(self, client, perf_tester):
        """测试狗粮看板性能"""
        def request():
            response = client.get('/food')
            assert response.status_code == 200
        
        results = perf_tester.measure_response_time(request, iterations=5)
        
        print(f"\n狗粮看板性能:")
        print(f"  平均响应时间：{results['avg']*1000:.2f}ms")
        
        if results['avg'] > 3.0:
            report_bug(
                title="狗粮看板响应慢",
                description=f"平均响应时间：{results['avg']*1000:.2f}ms",
                severity="Major",
                priority="Medium",
                module="性能",
                steps_to_reproduce=["访问 /food"],
                expected_result="响应时间 < 3000ms",
                actual_result=f"平均响应时间：{results['avg']*1000:.2f}ms"
            )


class TestConcurrentAccess:
    """并发访问测试"""
    
    def test_concurrent_index_access(self, app, perf_tester):
        """测试并发访问首页"""
        import threading
        
        results = []
        errors = []
        
        def make_request():
            with app.test_client() as client:
                try:
                    start = time.time()
                    response = client.get('/')
                    end = time.time()
                    if response.status_code == 200:
                        results.append(end - start)
                    else:
                        errors.append(f"状态码：{response.status_code}")
                except Exception as e:
                    errors.append(str(e))
        
        # 创建 10 个并发请求
        threads = []
        for i in range(10):
            t = threading.Thread(target=make_request)
            threads.append(t)
        
        # 同时启动所有线程
        start_time = time.time()
        for t in threads:
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        total_time = time.time() - start_time
        
        print(f"\n并发测试结果 (10 个并发请求):")
        print(f"  总耗时：{total_time*1000:.2f}ms")
        print(f"  成功数：{len(results)}")
        print(f"  失败数：{len(errors)}")
        if results:
            print(f"  平均响应时间：{mean(results)*1000:.2f}ms")
        
        # 如果有错误，记录下来
        if errors:
            report_bug(
                title="并发访问出现错误",
                description=f"10 个并发请求中有 {len(errors)} 个失败",
                severity="Major",
                priority="High",
                module="性能 - 并发",
                steps_to_reproduce=["并发发送 10 个请求到首页"],
                expected_result="所有请求都成功",
                actual_result=f"{len(errors)} 个请求失败：{errors[:3]}"  # 只显示前 3 个错误
            )


class TestMemoryLeak:
    """内存泄漏检测（简单版本）"""
    
    def test_repeated_requests(self, client):
        """重复请求检测内存问题"""
        initial_memory = None
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pytest.skip("需要安装 psutil 库")
        
        # 执行 100 次请求
        for i in range(100):
            response = client.get('/')
            assert response.status_code == 200
        
        # 检查内存增长
        try:
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            print(f"\n内存使用:")
            print(f"  初始：{initial_memory:.2f} MB")
            print(f"  最终：{final_memory:.2f} MB")
            print(f"  增长：{memory_increase:.2f} MB")
            
            # 如果内存增长超过 50MB，可能存在泄漏
            if memory_increase > 50:
                report_bug(
                    title="潜在的内存泄漏",
                    description=f"100 次请求后内存增长 {memory_increase:.2f} MB",
                    severity="Major",
                    priority="High",
                    module="性能 - 内存",
                    steps_to_reproduce=["连续发送 100 个请求到首页"],
                    expected_result="内存增长 < 50MB",
                    actual_result=f"内存增长：{memory_increase:.2f} MB"
                )
        except Exception as e:
            print(f"无法检测内存：{e}")
