"""
Prometheus 监控指标
提供应用性能监控和业务指标收集
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps

# ===== HTTP 请求指标 =====
HTTP_REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# ===== 业务指标 =====

# 用户相关
USER_REGISTRATION_COUNT = Counter(
    'user_registrations_total',
    'Total User Registrations'
)

USER_LOGIN_COUNT = Counter(
    'user_logins_total',
    'Total User Logins'
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of Active Users'
)

# 数据相关
DATA_UPLOAD_COUNT = Counter(
    'data_uploads_total',
    'Total Data Uploads',
    ['file_type']
)

CHART_GENERATION_COUNT = Counter(
    'chart_generations_total',
    'Total Chart Generations',
    ['chart_type']
)

# 反馈相关
FEEDBACK_SUBMISSION_COUNT = Counter(
    'feedback_submissions_total',
    'Total Feedback Submissions',
    ['feedback_type']
)

# 埋点相关
EVENT_TRACKING_COUNT = Counter(
    'event_tracking_total',
    'Total Event Tracking',
    ['event_category']
)

# 系统指标
DB_QUERY_LATENCY = Histogram(
    'database_query_duration_seconds',
    'Database Query Latency',
    ['query_type']
)

CACHE_HIT_COUNT = Counter(
    'cache_hits_total',
    'Total Cache Hits'
)

CACHE_MISS_COUNT = Counter(
    'cache_misses_total',
    'Total Cache Misses'
)

# ===== 监控装饰器 =====

def monitor_http_request(func):
    """监控 HTTP 请求的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        start_time = time.time()
        
        try:
            response = func(*args, **kwargs)
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            
            # 记录请求计数
            HTTP_REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=status_code
            ).inc()
            
            return response
            
        except Exception as e:
            # 记录错误
            HTTP_REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=500
            ).inc()
            raise
            
        finally:
            # 记录延迟
            duration = time.time() - start_time
            HTTP_REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)
    
    return wrapper


def track_user_registration(func):
    """追踪用户注册"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        USER_REGISTRATION_COUNT.inc()
        return result
    return wrapper


def track_user_login(func):
    """追踪用户登录"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        USER_LOGIN_COUNT.inc()
        return result
    return wrapper


def track_data_upload(file_type='unknown'):
    """追踪数据上传"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            DATA_UPLOAD_COUNT.labels(file_type=file_type).inc()
            return result
        return wrapper
    return decorator


def track_chart_generation(chart_type='unknown'):
    """追踪图表生成"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            CHART_GENERATION_COUNT.labels(chart_type=chart_type).inc()
            return result
        return wrapper
    return decorator


def track_feedback_submission(feedback_type='other'):
    """追踪反馈提交"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            FEEDBACK_SUBMISSION_COUNT.labels(feedback_type=feedback_type).inc()
            return result
        return wrapper
    return decorator


def track_event_tracking(event_category='custom'):
    """追踪事件埋点"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            EVENT_TRACKING_COUNT.labels(event_category=event_category).inc()
            return result
        return wrapper
    return decorator


# ===== 辅助函数 =====

def update_active_users(count):
    """更新活跃用户数"""
    ACTIVE_USERS.set(count)


def record_db_query_latency(query_type, duration):
    """记录数据库查询延迟"""
    DB_QUERY_LATENCY.labels(query_type=query_type).observe(duration)


def record_cache_hit():
    """记录缓存命中"""
    CACHE_HIT_COUNT.inc()


def record_cache_miss():
    """记录缓存未命中"""
    CACHE_MISS_COUNT.inc()


def get_metrics_summary():
    """获取指标摘要（用于调试）"""
    return {
        'http_requests': HTTP_REQUEST_COUNT._metrics,
        'active_users': ACTIVE_USERS._value.get(),
        'cache_hits': CACHE_HIT_COUNT._value.get(),
        'cache_misses': CACHE_MISS_COUNT._value.get(),
    }
