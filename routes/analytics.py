"""
用户行为埋点 API
追踪用户操作、页面浏览、功能使用等
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from models_extended import UserEvent
from models import db
import json
from datetime import datetime, timedelta
from sqlalchemy import func

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/analytics/track", methods=["POST"])
def track_event():
    """
    追踪用户事件

    请求体:
    {
        "event_name": "button_click",
        "event_category": "click",
        "event_label": "export_chart",
        "page_url": "/chart/1",
        "properties": {"chart_type": "bar", "data_points": 100}
    }
    """
    data = request.get_json()

    if not data or "event_name" not in data:
        return jsonify({"error": "缺少 event_name"}), 400

    try:
        # 解析 User-Agent
        user_agent = request.headers.get("User-Agent", "")
        device_info = parse_user_agent(user_agent)

        # 获取 IP 地址
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

        # 创建事件记录
        event = UserEvent(
            user_id=current_user.id if current_user.is_authenticated else None,
            event_name=data["event_name"],
            event_category=data.get("event_category", "custom"),
            event_label=data.get("event_label"),
            page_url=data.get("page_url", request.referrer),
            page_title=data.get("page_title"),
            referrer=data.get("referrer"),
            device_type=device_info.get("device_type"),
            browser=device_info.get("browser"),
            os=device_info.get("os"),
            screen_resolution=data.get("screen_resolution"),
            ip_address=ip_address.split(",")[0].strip(),  # 处理多个 IP
            session_id=data.get("session_id"),
            properties=json.dumps(data.get("properties", {})),
        )

        db.session.add(event)
        db.session.commit()

        return (
            jsonify({"success": True, "message": "事件已记录", "event_id": event.id}),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"记录失败: {str(e)}"}), 500


@analytics_bp.route("/api/analytics/batch", methods=["POST"])
def batch_track_events():
    """批量追踪事件（提高性能）"""
    data = request.get_json()

    if not data or "events" not in data:
        return jsonify({"error": "缺少 events 数组"}), 400

    events_data = data["events"]
    if not isinstance(events_data, list):
        return jsonify({"error": "events 必须是数组"}), 400

    if len(events_data) > 100:
        return jsonify({"error": "单次最多提交 100 个事件"}), 400

    try:
        events = []
        for event_data in events_data:
            if "event_name" not in event_data:
                continue

            user_agent = request.headers.get("User-Agent", "")
            device_info = parse_user_agent(user_agent)
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

            event = UserEvent(
                user_id=current_user.id if current_user.is_authenticated else None,
                event_name=event_data["event_name"],
                event_category=event_data.get("event_category", "custom"),
                event_label=event_data.get("event_label"),
                page_url=event_data.get("page_url"),
                page_title=event_data.get("page_title"),
                referrer=event_data.get("referrer"),
                device_type=device_info.get("device_type"),
                browser=device_info.get("browser"),
                os=device_info.get("os"),
                screen_resolution=event_data.get("screen_resolution"),
                ip_address=ip_address.split(",")[0].strip(),
                session_id=event_data.get("session_id"),
                properties=json.dumps(event_data.get("properties", {})),
            )
            events.append(event)

        if events:
            db.session.bulk_save_objects(events)
            db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"成功记录 {len(events)} 个事件",
                    "count": len(events),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"批量记录失败: {str(e)}"}), 500


@analytics_bp.route("/api/analytics/events", methods=["GET"])
def get_events():
    """获取事件列表（支持筛选和分页）"""
    # 权限检查：仅管理员
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    # 查询参数
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    event_name = request.args.get("event_name")
    event_category = request.args.get("event_category")
    user_id = request.args.get("user_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # 构建查询
    query = UserEvent.query

    if event_name:
        query = query.filter_by(event_name=event_name)
    if event_category:
        query = query.filter_by(event_category=event_category)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(UserEvent.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(UserEvent.created_at <= datetime.fromisoformat(end_date))

    # 按时间倒序
    query = query.order_by(UserEvent.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    events = [e.to_dict() for e in pagination.items]

    return (
        jsonify(
            {
                "success": True,
                "events": events,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@analytics_bp.route("/api/analytics/stats", methods=["GET"])
def get_analytics_stats():
    """获取分析统计数据"""
    # 权限检查
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    # 时间范围（默认最近 7 天）
    days = request.args.get("days", 7, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # 总事件数
    total_events = UserEvent.query.filter(UserEvent.created_at >= start_date).count()

    # 按分类统计
    category_stats = (
        db.session.query(UserEvent.event_category, func.count(UserEvent.id))
        .filter(UserEvent.created_at >= start_date)
        .group_by(UserEvent.event_category)
        .all()
    )

    # 按事件名统计（TOP 20）
    top_events = (
        db.session.query(UserEvent.event_name, func.count(UserEvent.id).label("count"))
        .filter(UserEvent.created_at >= start_date)
        .group_by(UserEvent.event_name)
        .order_by(func.count(UserEvent.id).desc())
        .limit(20)
        .all()
    )

    # 独立用户数
    unique_users = (
        db.session.query(func.count(func.distinct(UserEvent.user_id)))
        .filter(UserEvent.created_at >= start_date, UserEvent.user_id.isnot(None))
        .scalar()
        or 0
    )

    # 独立会话数
    unique_sessions = (
        db.session.query(func.count(func.distinct(UserEvent.session_id)))
        .filter(UserEvent.created_at >= start_date, UserEvent.session_id.isnot(None))
        .scalar()
        or 0
    )

    # 按设备类型统计
    device_stats = (
        db.session.query(UserEvent.device_type, func.count(UserEvent.id))
        .filter(UserEvent.created_at >= start_date, UserEvent.device_type.isnot(None))
        .group_by(UserEvent.device_type)
        .all()
    )

    # 按浏览器统计
    browser_stats = (
        db.session.query(UserEvent.browser, func.count(UserEvent.id))
        .filter(UserEvent.created_at >= start_date, UserEvent.browser.isnot(None))
        .group_by(UserEvent.browser)
        .order_by(func.count(UserEvent.id).desc())
        .limit(10)
        .all()
    )

    return (
        jsonify(
            {
                "success": True,
                "stats": {
                    "period": f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
                    "total_events": total_events,
                    "unique_users": unique_users,
                    "unique_sessions": unique_sessions,
                    "by_category": {cat: count for cat, count in category_stats},
                    "top_events": [
                        {"event": event, "count": count} for event, count in top_events
                    ],
                    "by_device": {device: count for device, count in device_stats},
                    "by_browser": {browser: count for browser, count in browser_stats},
                },
            }
        ),
        200,
    )


@analytics_bp.route("/api/analytics/funnel", methods=["GET"])
def get_conversion_funnel():
    """获取转化漏斗数据"""
    # 权限检查
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    # 定义漏斗步骤（示例：用户注册流程）
    funnel_steps = [
        "page_view_home",  # 访问首页
        "click_register",  # 点击注册
        "page_view_register",  # 访问注册页
        "submit_register",  # 提交注册
        "register_success",  # 注册成功
    ]

    days = request.args.get("days", 7, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    funnel_data = []
    for step in funnel_steps:
        count = UserEvent.query.filter(
            UserEvent.event_name == step, UserEvent.created_at >= start_date
        ).count()

        funnel_data.append({"step": step, "count": count})

    # 计算转化率
    if funnel_data and funnel_data[0]["count"] > 0:
        base_count = funnel_data[0]["count"]
        for item in funnel_data:
            item["conversion_rate"] = round((item["count"] / base_count) * 100, 2)
    else:
        for item in funnel_data:
            item["conversion_rate"] = 0

    return (
        jsonify(
            {
                "success": True,
                "funnel": funnel_data,
                "period": f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            }
        ),
        200,
    )


# 工具函数
def parse_user_agent(user_agent):
    """
    简单解析 User-Agent
    实际项目中建议使用 ua-parser 库
    """
    device_info = {"device_type": "desktop", "browser": "Unknown", "os": "Unknown"}

    # 检测设备类型
    if "Mobile" in user_agent or "Android" in user_agent:
        device_info["device_type"] = "mobile"
    elif "Tablet" in user_agent or "iPad" in user_agent:
        device_info["device_type"] = "tablet"

    # 检测浏览器
    if "Chrome" in user_agent and "Edg" not in user_agent:
        device_info["browser"] = "Chrome"
    elif "Firefox" in user_agent:
        device_info["browser"] = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        device_info["browser"] = "Safari"
    elif "Edg" in user_agent:
        device_info["browser"] = "Edge"
    elif "MSIE" in user_agent or "Trident" in user_agent:
        device_info["browser"] = "IE"

    # 检测操作系统
    if "Windows" in user_agent:
        device_info["os"] = "Windows"
    elif "Mac OS" in user_agent:
        device_info["os"] = "macOS"
    elif "Linux" in user_agent:
        device_info["os"] = "Linux"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        device_info["os"] = "iOS"
    elif "Android" in user_agent:
        device_info["os"] = "Android"

    return device_info
