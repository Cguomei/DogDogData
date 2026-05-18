"""
数据分析表设计文档
基于数据新鲜度监控系统的增强分析功能

版本: v1.0
日期: 2026-05-12
作者: AI Assistant
"""

# ============================================================================
# 一、设计目标
# ============================================================================
"""
基于新增的 crawl_time 和 updated_at 字段，设计以下数据分析表：

1. 数据质量分析表 - 监控数据完整性、准确性
2. 爬取效率分析表 - 统计爬虫性能和成功率
3. 价格趋势分析表 - 跟踪品种价格变化
4. 品种热度分析表 - 分析品种受欢迎程度
5. 用户行为分析表 - 记录用户查询和收藏行为
6. 系统性能分析表 - 监控系统响应时间和负载

所有表都支持时间维度分析，便于生成日报、周报、月报。
"""

# ============================================================================
# 二、数据库表结构设计
# ============================================================================

from models import db
from datetime import datetime


class DataQualityMetrics(db.Model):
    """
    数据质量指标表

    用途: 每日统计数据质量指标，用于监控数据健康状况

    更新频率: 每日凌晨自动计算
    """

    __tablename__ = "data_quality_metrics"

    id = db.Column(db.Integer, primary_key=True)

    # 统计日期
    stat_date = db.Column(db.Date, nullable=False, index=True, comment="统计日期")

    # 数据量指标
    total_records = db.Column(db.Integer, default=0, comment="总记录数")
    fresh_records = db.Column(db.Integer, default=0, comment="新鲜记录数(<24h)")
    warning_records = db.Column(db.Integer, default=0, comment="警告记录数(24-48h)")
    stale_records = db.Column(db.Integer, default=0, comment="过期记录数(>48h)")

    # 质量指标
    completeness_rate = db.Column(db.Float, default=0.0, comment="数据完整率(%)")
    accuracy_rate = db.Column(db.Float, default=0.0, comment="数据准确率(%)")
    duplicate_count = db.Column(db.Integer, default=0, comment="重复记录数")
    null_price_count = db.Column(db.Integer, default=0, comment="价格为空数量")
    null_image_count = db.Column(db.Integer, default=0, comment="图片为空数量")

    # 新鲜度指标
    freshness_percentage = db.Column(db.Float, default=0.0, comment="新鲜度百分比")
    avg_hours_since_crawl = db.Column(
        db.Float, default=0.0, comment="平均爬取时长(小时)"
    )
    max_hours_since_crawl = db.Column(
        db.Float, default=0.0, comment="最大爬取时长(小时)"
    )

    # 品种分布
    breed_count = db.Column(db.Integer, default=0, comment="品种数量")
    top_breed = db.Column(db.String(100), comment="最多记录的品种")
    top_breed_count = db.Column(db.Integer, default=0, comment="最多记录的品种数量")

    # 价格指标
    avg_price = db.Column(db.Float, default=0.0, comment="平均价格")
    min_price = db.Column(db.Float, default=0.0, comment="最低价格")
    max_price = db.Column(db.Float, default=0.0, comment="最高价格")
    price_std = db.Column(db.Float, default=0.0, comment="价格标准差")

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    def to_dict(self):
        return {
            "stat_date": self.stat_date.strftime("%Y-%m-%d"),
            "total_records": self.total_records,
            "freshness_percentage": self.freshness_percentage,
            "avg_price": self.avg_price,
            "breed_count": self.breed_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class CrawlPerformanceLog(db.Model):
    """
    爬取性能日志表

    用途: 记录每次爬取任务的详细性能数据

    更新频率: 每次爬取任务完成后自动记录
    """

    __tablename__ = "crawl_performance_log"

    id = db.Column(db.Integer, primary_key=True)

    # 任务信息
    task_id = db.Column(
        db.String(100), unique=True, nullable=False, index=True, comment="任务ID"
    )
    keywords = db.Column(db.Text, comment="搜索关键词(JSON数组)")

    # 时间信息
    start_time = db.Column(db.DateTime, nullable=False, comment="开始时间")
    end_time = db.Column(db.DateTime, comment="结束时间")
    duration_seconds = db.Column(db.Float, comment="耗时(秒)")

    # 结果统计
    total_found = db.Column(db.Integer, default=0, comment="发现总数")
    success_count = db.Column(db.Integer, default=0, comment="成功爬取数")
    failed_count = db.Column(db.Integer, default=0, comment="失败数")
    skipped_count = db.Column(db.Integer, default=0, comment="跳过数(已存在)")

    # 性能指标
    requests_per_second = db.Column(db.Float, default=0.0, comment="请求速度( req/s)")
    success_rate = db.Column(db.Float, default=0.0, comment="成功率(%)")
    avg_response_time = db.Column(db.Float, default=0.0, comment="平均响应时间(ms)")

    # 错误信息
    error_count = db.Column(db.Integer, default=0, comment="错误次数")
    error_details = db.Column(db.Text, comment="错误详情(JSON)")

    # 状态
    status = db.Column(
        db.Enum("success", "partial", "failed"), default="success", comment="任务状态"
    )

    # 执行者
    triggered_by = db.Column(
        db.String(50), default="manual", comment="触发方式: manual/auto/scheduled"
    )

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "keywords": self.keywords,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": self.duration_seconds,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "status": self.status,
        }


class PriceTrendDaily(db.Model):
    """
    价格趋势日统计表

    用途: 按品种统计每日价格变化，用于价格趋势分析

    更新频率: 每日凌晨自动计算
    """

    __tablename__ = "price_trend_daily"

    id = db.Column(db.Integer, primary_key=True)

    # 统计日期和品种
    stat_date = db.Column(db.Date, nullable=False, index=True, comment="统计日期")
    breed_name = db.Column(
        db.String(100), nullable=False, index=True, comment="品种名称"
    )

    # 价格统计
    avg_price = db.Column(db.Float, comment="平均价格")
    min_price = db.Column(db.Float, comment="最低价格")
    max_price = db.Column(db.Float, comment="最高价格")
    median_price = db.Column(db.Float, comment="中位数价格")
    price_std = db.Column(db.Float, comment="价格标准差")

    # 数据量
    record_count = db.Column(db.Integer, default=0, comment="记录数量")
    shop_count = db.Column(db.Integer, default=0, comment="店铺数量")

    # 价格变化（与前一天对比）
    prev_day_avg_price = db.Column(db.Float, comment="前一日平均价格")
    price_change = db.Column(db.Float, comment="价格变化额")
    price_change_percent = db.Column(db.Float, comment="价格变化百分比")

    # 新鲜度
    fresh_data_ratio = db.Column(db.Float, default=0.0, comment="新鲜数据占比")

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint("stat_date", "breed_name", name="unique_date_breed"),
    )

    def to_dict(self):
        return {
            "stat_date": self.stat_date.strftime("%Y-%m-%d"),
            "breed_name": self.breed_name,
            "avg_price": self.avg_price,
            "price_change_percent": self.price_change_percent,
            "record_count": self.record_count,
        }


class BreedPopularityStats(db.Model):
    """
    品种热度统计表

    用途: 统计各品种的受欢迎程度（基于查询次数、收藏数等）

    更新频率: 每日凌晨自动计算
    """

    __tablename__ = "breed_popularity_stats"

    id = db.Column(db.Integer, primary_key=True)

    # 统计日期和品种
    stat_date = db.Column(db.Date, nullable=False, index=True, comment="统计日期")
    breed_name = db.Column(
        db.String(100), nullable=False, index=True, comment="品种名称"
    )

    # 基础数据
    total_records = db.Column(db.Integer, default=0, comment="数据记录数")
    avg_price = db.Column(db.Float, comment="平均价格")

    # 用户行为指标
    search_count = db.Column(db.Integer, default=0, comment="搜索次数")
    view_count = db.Column(db.Integer, default=0, comment="查看次数")
    favorite_count = db.Column(db.Integer, default=0, comment="收藏次数")
    share_count = db.Column(db.Integer, default=0, comment="分享次数")

    # AI助手交互
    ai_query_count = db.Column(db.Integer, default=0, comment="AI查询次数")

    # 热度评分（综合计算）
    popularity_score = db.Column(db.Float, default=0.0, comment="热度评分(0-100)")
    rank = db.Column(db.Integer, comment="排名")

    # 环比变化
    prev_week_score = db.Column(db.Float, comment="上周热度评分")
    score_change = db.Column(db.Float, comment="评分变化")
    trend = db.Column(db.Enum("up", "down", "stable"), comment="趋势")

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint(
            "stat_date", "breed_name", name="unique_popularity_date_breed"
        ),
    )

    def to_dict(self):
        return {
            "stat_date": self.stat_date.strftime("%Y-%m-%d"),
            "breed_name": self.breed_name,
            "popularity_score": self.popularity_score,
            "rank": self.rank,
            "trend": self.trend,
        }


class UserBehaviorAnalytics(db.Model):
    """
    用户行为分析表

    用途: 记录和分析用户在系统中的行为模式

    更新频率: 实时记录，每日汇总
    """

    __tablename__ = "user_behavior_analytics"

    id = db.Column(db.Integer, primary_key=True)

    # 用户信息
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        comment="用户ID（匿名为NULL）",
    )
    session_id = db.Column(db.String(100), index=True, comment="会话ID")

    # 行为信息
    action_type = db.Column(
        db.String(50), nullable=False, index=True, comment="行为类型"
    )
    # action_type 可选值:
    # - page_view: 页面浏览
    # - chart_view: 图表查看
    # - data_query: 数据查询
    # - breed_search: 品种搜索
    # - favorite_add: 添加收藏
    # - favorite_remove: 取消收藏
    # - ai_chat: AI对话
    # - data_export: 数据导出
    # - crawler_start: 启动爬虫

    target_id = db.Column(db.String(100), comment="目标ID（如品种ID、图表ID等）")
    target_name = db.Column(db.String(200), comment="目标名称")

    # 行为详情
    metadata = db.Column(db.Text, comment="附加信息(JSON)")
    duration_seconds = db.Column(db.Float, comment="停留时长(秒)")

    # 设备信息
    device_type = db.Column(db.String(20), comment="设备类型: desktop/mobile/tablet")
    browser = db.Column(db.String(50), comment="浏览器")
    ip_address = db.Column(db.String(50), comment="IP地址")

    # 时间信息
    action_time = db.Column(
        db.DateTime, server_default=db.func.now(), index=True, comment="行为时间"
    )

    # 关联
    user = db.relationship("User", backref=db.backref("behaviors", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "target_name": self.target_name,
            "action_time": self.action_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": self.duration_seconds,
        }


class SystemPerformanceMetrics(db.Model):
    """
    系统性能指标表

    用途: 监控系统API响应时间、错误率等性能指标

    更新频率: 每分钟聚合一次
    """

    __tablename__ = "system_performance_metrics"

    id = db.Column(db.Integer, primary_key=True)

    # 时间窗口
    metric_time = db.Column(
        db.DateTime, nullable=False, index=True, comment="统计时间点"
    )
    time_window = db.Column(
        db.String(20), default="1min", comment="时间窗口: 1min/5min/1hour/1day"
    )

    # API性能
    total_requests = db.Column(db.Integer, default=0, comment="总请求数")
    avg_response_time = db.Column(db.Float, default=0.0, comment="平均响应时间(ms)")
    p95_response_time = db.Column(db.Float, default=0.0, comment="P95响应时间(ms)")
    p99_response_time = db.Column(db.Float, default=0.0, comment="P99响应时间(ms)")

    # 错误统计
    error_count = db.Column(db.Integer, default=0, comment="错误数")
    error_rate = db.Column(db.Float, default=0.0, comment="错误率(%)")

    # 按端点分类（JSON格式）
    endpoint_stats = db.Column(db.Text, comment="端点统计(JSON)")
    # 示例: {"api/data/freshness": {"count": 100, "avg_time": 45}, ...}

    # 资源使用
    active_users = db.Column(db.Integer, default=0, comment="活跃用户数")
    concurrent_connections = db.Column(db.Integer, default=0, comment="并发连接数")

    # 数据库性能
    db_query_count = db.Column(db.Integer, default=0, comment="数据库查询数")
    db_avg_query_time = db.Column(
        db.Float, default=0.0, comment="数据库平均查询时间(ms)"
    )

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "metric_time": self.metric_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_requests": self.total_requests,
            "avg_response_time": self.avg_response_time,
            "error_rate": self.error_rate,
            "active_users": self.active_users,
        }


class DailySummaryReport(db.Model):
    """
    每日汇总报告表

    用途: 存储每日的综合分析报告，便于快速展示

    更新频率: 每日凌晨自动生成
    """

    __tablename__ = "daily_summary_report"

    id = db.Column(db.Integer, primary_key=True)

    # 报告日期
    report_date = db.Column(
        db.Date, nullable=False, unique=True, index=True, comment="报告日期"
    )

    # 核心指标（JSON格式存储）
    summary_data = db.Column(db.Text, nullable=False, comment="汇总数据(JSON)")
    # 示例结构:
    # {
    #   "data_quality": {
    #     "total_records": 2278,
    #     "freshness": 95.5,
    #     "quality_score": 92
    #   },
    #   "top_breeds": [
    #     {"name": "金毛", "count": 250, "avg_price": 4468},
    #     ...
    #   ],
    #   "price_trends": {
    #     "avg_change": -2.5,
    #     "trending_up": ["柯基"],
    #     "trending_down": ["泰迪"]
    #   },
    #   "user_activity": {
    #     "active_users": 150,
    #     "total_queries": 500,
    #     "ai_chats": 80
    #   },
    #   "system_health": {
    #     "uptime": 99.9,
    #     "avg_response_time": 45,
    #     "error_rate": 0.5
    #   }
    # }

    # 报告状态
    generation_status = db.Column(
        db.Enum("pending", "generating", "completed", "failed"),
        default="pending",
        comment="生成状态",
    )
    generated_at = db.Column(db.DateTime, comment="生成时间")

    # 时间戳
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    def to_dict(self):
        import json

        return {
            "report_date": self.report_date.strftime("%Y-%m-%d"),
            "summary_data": json.loads(self.summary_data) if self.summary_data else {},
            "generation_status": self.generation_status,
            "generated_at": (
                self.generated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.generated_at
                else None
            ),
        }


# ============================================================================
# 三、索引优化建议
# ============================================================================
"""
CREATE INDEX idx_quality_date ON data_quality_metrics(stat_date);
CREATE INDEX idx_crawl_task ON crawl_performance_log(task_id);
CREATE INDEX idx_crawl_time ON crawl_performance_log(start_time);
CREATE INDEX idx_price_date_breed ON price_trend_daily(stat_date, breed_name);
CREATE INDEX idx_popularity_date ON breed_popularity_stats(stat_date);
CREATE INDEX idx_popularity_score ON breed_popularity_stats(popularity_score DESC);
CREATE INDEX idx_behavior_user ON user_behavior_analytics(user_id);
CREATE INDEX idx_behavior_time ON user_behavior_analytics(action_time);
CREATE INDEX idx_behavior_type ON user_behavior_analytics(action_type);
CREATE INDEX idx_perf_time ON system_performance_metrics(metric_time);
CREATE INDEX idx_daily_report_date ON daily_summary_report(report_date);
"""

# ============================================================================
# 四、自动化任务配置
# ============================================================================
"""
在 app.py 中添加定时任务：

from apscheduler.schedulers.background import BackgroundScheduler

def calculate_daily_metrics():
    '''每日凌晨计算各项指标'''
    from utils.analytics_calculator import AnalyticsCalculator
    calculator = AnalyticsCalculator()
    calculator.calculate_all_metrics()

scheduler = BackgroundScheduler()
scheduler.add_job(calculate_daily_metrics, 'cron', hour=2, minute=0)  # 每天凌晨2点
scheduler.start()
"""

# ============================================================================
# 五、API接口设计
# ============================================================================
"""
新增API端点：

1. GET /api/analytics/quality
   - 获取数据质量指标
   - 参数: date_range (7d/30d/90d)
   
2. GET /api/analytics/crawl-performance
   - 获取爬取性能统计
   - 参数: task_id, date_range
   
3. GET /api/analytics/price-trend
   - 获取价格趋势数据
   - 参数: breed_name, date_range
   
4. GET /api/analytics/breed-popularity
   - 获取品种热度排行
   - 参数: limit, date_range
   
5. GET /api/analytics/user-behavior
   - 获取用户行为分析
   - 参数: user_id, action_type, date_range
   
6. GET /api/analytics/system-performance
   - 获取系统性能指标
   - 参数: time_window
   
7. GET /api/analytics/daily-report/:date
   - 获取每日汇总报告
   - 参数: date (YYYY-MM-DD)
"""
