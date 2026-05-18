"""
用户反馈 API 路由
提供反馈提交、查询、管理等功能
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models_extended import Feedback
from models import db
from datetime import datetime

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    """提交用户反馈"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    # 验证必填字段
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "反馈内容不能为空"}), 400

    if len(content) > 5000:
        return jsonify({"error": "反馈内容过长，请控制在 5000 字以内"}), 400

    # 验证反馈类型（支持 feedback_type 和 type 两种字段名）
    feedback_type = data.get("feedback_type") or data.get("type", "other")
    valid_types = ["bug", "feature", "improvement", "other"]
    if feedback_type not in valid_types:
        return jsonify({"error": f"无效的反馈类型，支持的类型: {valid_types}"}), 400

    # 验证优先级
    priority = data.get("priority", "medium")
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority not in valid_priorities:
        return (
            jsonify({"error": f"无效的优先级，支持的优先级: {valid_priorities}"}),
            400,
        )

    # 创建反馈记录
    feedback = Feedback(
        user_id=current_user.id,
        feedback_type=feedback_type,
        title=data.get("title", ""),
        content=content,
        screenshot_url=data.get("screenshot_url"),
        attachment_url=data.get("attachment_url"),
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        priority=priority,
    )

    try:
        db.session.add(feedback)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "反馈已提交，感谢您的建议！",
                    "feedback_id": feedback.id,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"提交失败：{str(e)}"}), 500


@feedback_bp.route("/api/feedback", methods=["GET"])
@login_required
def get_user_feedbacks():
    """获取当前用户的反馈列表"""
    # 分页参数
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # 过滤参数
    status = request.args.get("status")
    feedback_type = request.args.get("type")  # 支持 type 参数

    # 构建查询
    query = Feedback.query.filter_by(user_id=current_user.id)

    if status:
        query = query.filter_by(status=status)
    if feedback_type:
        query = query.filter_by(feedback_type=feedback_type)

    # 按创建时间倒序
    query = query.order_by(Feedback.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    feedbacks = [f.to_dict() for f in pagination.items]

    return (
        jsonify(
            {
                "success": True,
                "feedbacks": feedbacks,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ),
        200,
    )


@feedback_bp.route("/api/feedback/<int:feedback_id>", methods=["GET"])
@login_required
def get_feedback_detail(feedback_id):
    """获取反馈详情"""
    feedback = Feedback.query.get_or_404(feedback_id)

    # 权限检查：只能查看自己的反馈（管理员除外）
    if feedback.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"error": "权限不足"}), 403

    return (
        jsonify({"success": True, "feedback": feedback.to_dict(include_user=True)}),
        200,
    )


@feedback_bp.route("/api/feedback/admin/list", methods=["GET"])
@login_required
def admin_get_all_feedbacks():
    """管理员获取所有反馈列表"""
    # 权限检查
    if not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    # 分页参数
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # 过滤参数
    status = request.args.get("status")
    feedback_type = request.args.get("type")
    priority = request.args.get("priority")

    # 构建查询
    query = Feedback.query

    if status:
        query = query.filter_by(status=status)
    if feedback_type:
        query = query.filter_by(feedback_type=feedback_type)
    if priority:
        query = query.filter_by(priority=priority)

    # 按优先级和创建时间排序
    priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}

    query = query.order_by(
        db.case(priority_order, value=Feedback.priority), Feedback.created_at.desc()
    )

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    feedbacks = [f.to_dict(include_user=True) for f in pagination.items]

    return (
        jsonify(
            {
                "success": True,
                "feedbacks": feedbacks,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ),
        200,
    )


@feedback_bp.route("/api/feedback/<int:feedback_id>/reply", methods=["POST"])
@login_required
def reply_to_feedback(feedback_id):
    """管理员回复反馈"""
    # 权限检查
    if not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    feedback = Feedback.query.get_or_404(feedback_id)
    data = request.get_json()

    reply_content = data.get("reply", "").strip()
    if not reply_content:
        return jsonify({"error": "回复内容不能为空"}), 400

    # 更新反馈
    feedback.admin_reply = reply_content
    feedback.replied_by = current_user.id
    feedback.replied_at = datetime.utcnow()
    feedback.status = data.get("status", "processing")

    try:
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "回复成功",
                    "feedback": feedback.to_dict(include_user=True),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"回复失败：{str(e)}"}), 500


@feedback_bp.route("/api/feedback/<int:feedback_id>/status", methods=["PUT"])
@login_required
def update_feedback_status(feedback_id):
    """更新反馈状态"""
    # 权限检查
    if not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    feedback = Feedback.query.get_or_404(feedback_id)
    data = request.get_json()

    new_status = data.get("status")
    valid_statuses = ["pending", "processing", "resolved", "closed"]

    if new_status not in valid_statuses:
        return jsonify({"error": f"无效的状态，支持的状态: {valid_statuses}"}), 400

    feedback.status = new_status

    try:
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "状态更新成功",
                    "feedback": feedback.to_dict(include_user=True),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失败：{str(e)}"}), 500


@feedback_bp.route("/api/feedback/stats", methods=["GET"])
@login_required
def get_feedback_stats():
    """获取反馈统计信息"""
    # 权限检查：仅管理员
    if not current_user.is_admin():
        return jsonify({"error": "需要管理员权限"}), 403

    # 按状态统计
    status_stats = (
        db.session.query(Feedback.status, db.func.count(Feedback.id))
        .group_by(Feedback.status)
        .all()
    )

    # 按类型统计
    type_stats = (
        db.session.query(Feedback.feedback_type, db.func.count(Feedback.id))
        .group_by(Feedback.feedback_type)
        .all()
    )

    # 按优先级统计
    priority_stats = (
        db.session.query(Feedback.priority, db.func.count(Feedback.id))
        .group_by(Feedback.priority)
        .all()
    )

    # 总数
    total_count = Feedback.query.count()

    return (
        jsonify(
            {
                "success": True,
                "stats": {
                    "total": total_count,
                    "by_status": {status: count for status, count in status_stats},
                    "by_type": {ftype: count for ftype, count in type_stats},
                    "by_priority": {
                        priority: count for priority, count in priority_stats
                    },
                },
            }
        ),
        200,
    )
