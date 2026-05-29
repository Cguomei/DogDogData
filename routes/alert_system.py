"""
智能预警系统路由
提供价格预警、新品种提醒和通知管理功能
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models_extended import PriceAlert, BreedAlert, AlertNotification
from sqlalchemy import text
import json
import logging
from datetime import datetime

logger = logging.getLogger("alert_system")

alert_bp = Blueprint("alert_system", __name__)


# ===== 价格预警管理 =====


@alert_bp.route("/api/alerts/price", methods=["POST"])
@login_required
def create_price_alert():
    """创建价格预警"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400

        # 验证必填字段
        breed_name = data.get("breed_name")
        target_price = data.get("target_price")
        condition = data.get("condition")

        if not all([breed_name, target_price, condition]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "缺少必填字段：breed_name, target_price, condition",
                    }
                ),
                400,
            )

        # 验证条件
        if condition not in ["above", "below"]:
            return (
                jsonify({"success": False, "error": "condition必须是above或below"}),
                400,
            )

        # 验证价格
        try:
            target_price = float(target_price)
            if target_price <= 0:
                return jsonify({"success": False, "error": "目标价格必须大于0"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "无效的价格值"}), 400

        # 创建预警
        alert = PriceAlert(
            user_id=current_user.id,
            breed_name=breed_name,
            target_price=target_price,
            condition=condition,
            notify_email=data.get("notify_email", True),
            notify_in_app=data.get("notify_in_app", True),
        )

        db.session.add(alert)
        db.session.commit()

        logger.info(
            f"用户 {current_user.username} 创建价格预警: {breed_name} {condition} {target_price}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "价格预警创建成功",
                    "data": alert.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建价格预警失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/price", methods=["GET"])
@login_required
def get_price_alerts():
    """获取用户的价格预警列表"""
    try:
        active_only = request.args.get("active_only", "true").lower() == "true"

        query = PriceAlert.query.filter_by(user_id=current_user.id)
        if active_only:
            query = query.filter_by(is_active=True)

        alerts = query.order_by(PriceAlert.created_at.desc()).all()

        return jsonify(
            {
                "success": True,
                "data": [alert.to_dict() for alert in alerts],
                "total": len(alerts),
            }
        )

    except Exception as e:
        logger.error(f"获取价格预警失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/price/<int:alert_id>", methods=["PUT"])
@login_required
def update_price_alert(alert_id):
    """更新价格预警"""
    try:
        alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        if not alert:
            return jsonify({"success": False, "error": "预警不存在或无权访问"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400

        # 更新字段
        if "target_price" in data:
            try:
                alert.target_price = float(data["target_price"])
            except (ValueError, TypeError):
                return jsonify({"success": False, "error": "无效的价格值"}), 400

        if "condition" in data:
            if data["condition"] not in ["above", "below"]:
                return (
                    jsonify({"success": False, "error": "condition必须是above或below"}),
                    400,
                )
            alert.condition = data["condition"]

        if "is_active" in data:
            alert.is_active = bool(data["is_active"])

        if "notify_email" in data:
            alert.notify_email = bool(data["notify_email"])

        if "notify_in_app" in data:
            alert.notify_in_app = bool(data["notify_in_app"])

        db.session.commit()

        logger.info(f"用户 {current_user.username} 更新价格预警 {alert_id}")

        return jsonify(
            {"success": True, "message": "预警更新成功", "data": alert.to_dict()}
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新价格预警失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/price/<int:alert_id>", methods=["DELETE"])
@login_required
def delete_price_alert(alert_id):
    """删除价格预警"""
    try:
        alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        if not alert:
            return jsonify({"success": False, "error": "预警不存在或无权访问"}), 404

        db.session.delete(alert)
        db.session.commit()

        logger.info(f"用户 {current_user.username} 删除价格预警 {alert_id}")

        return jsonify({"success": True, "message": "预警删除成功"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除价格预警失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 品种提醒管理 =====


@alert_bp.route("/api/alerts/breed", methods=["POST"])
@login_required
def create_breed_alert():
    """创建新品种提醒"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400

        alert_type = data.get("alert_type", "all")
        valid_types = ["all", "new_breed", "size_category"]

        if alert_type not in valid_types:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"无效的alert_type，支持: {valid_types}",
                    }
                ),
                400,
            )

        # 创建提醒
        alert = BreedAlert(
            user_id=current_user.id,
            alert_type=alert_type,
            filters=(
                json.dumps(data.get("filters", {}), ensure_ascii=False)
                if data.get("filters")
                else None
            ),
            notify_email=data.get("notify_email", True),
            notify_in_app=data.get("notify_in_app", True),
        )

        db.session.add(alert)
        db.session.commit()

        logger.info(f"用户 {current_user.username} 创建品种提醒: {alert_type}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "品种提醒创建成功",
                    "data": alert.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建品种提醒失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/breed", methods=["GET"])
@login_required
def get_breed_alerts():
    """获取用户的品种提醒列表"""
    try:
        active_only = request.args.get("active_only", "true").lower() == "true"

        query = BreedAlert.query.filter_by(user_id=current_user.id)
        if active_only:
            query = query.filter_by(is_active=True)

        alerts = query.order_by(BreedAlert.created_at.desc()).all()

        return jsonify(
            {
                "success": True,
                "data": [alert.to_dict() for alert in alerts],
                "total": len(alerts),
            }
        )

    except Exception as e:
        logger.error(f"获取品种提醒失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/breed/<int:alert_id>", methods=["DELETE"])
@login_required
def delete_breed_alert(alert_id):
    """删除品种提醒"""
    try:
        alert = BreedAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        if not alert:
            return jsonify({"success": False, "error": "提醒不存在或无权访问"}), 404

        db.session.delete(alert)
        db.session.commit()

        logger.info(f"用户 {current_user.username} 删除品种提醒 {alert_id}")

        return jsonify({"success": True, "message": "提醒删除成功"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除品种提醒失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 通知管理 =====


@alert_bp.route("/api/alerts/notifications", methods=["GET"])
@login_required
def get_notifications():
    """获取用户的通知列表"""
    try:
        unread_only = request.args.get("unread_only", "false").lower() == "true"
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        query = AlertNotification.query.filter_by(user_id=current_user.id)
        if unread_only:
            query = query.filter_by(is_read=False)

        pagination = query.order_by(AlertNotification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "success": True,
                "data": [notif.to_dict() for notif in pagination.items],
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages,
            }
        )

    except Exception as e:
        logger.error(f"获取通知失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route(
    "/api/alerts/notifications/<int:notification_id>/read", methods=["POST"]
)
@login_required
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        notification = AlertNotification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first()

        if not notification:
            return jsonify({"success": False, "error": "通知不存在或无权访问"}), 404

        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()

        return jsonify({"success": True, "message": "已标记为已读"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"标记通知已读失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():
    """标记所有通知为已读"""
    try:
        notifications = AlertNotification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).all()

        for notif in notifications:
            notif.is_read = True
            notif.read_at = datetime.now()

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"已标记{len(notifications)}条通知为已读",
                "count": len(notifications),
            }
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"标记所有通知已读失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@alert_bp.route("/api/alerts/notifications/unread-count", methods=["GET"])
@login_required
def get_unread_count():
    """获取未读通知数量"""
    try:
        count = AlertNotification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()

        return jsonify({"success": True, "data": {"unread_count": count}})

    except Exception as e:
        logger.error(f"获取未读数失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 预警检查（定时任务调用）=====


@alert_bp.route("/api/alerts/check-price", methods=["POST"])
def check_price_alerts():
    """检查价格预警（内部接口，可由定时任务调用）"""
    try:
        from models_charts import JdDog
        from sqlalchemy import func

        # 获取所有活跃的价格预警
        active_alerts = PriceAlert.query.filter_by(
            is_active=True, triggered=False
        ).all()

        triggered_count = 0

        for alert in active_alerts:
            # 查询当前价格（用 SQLAlchemy 替代 raw pymysql cursor）
            result = (
                db.session.query(func.avg(JdDog.price))
                .filter(JdDog.dog_name.like(f"%{alert.breed_name}%"))
                .scalar()
            )

            if result:
                current_price = float(result)
                alert.last_check_price = current_price

                # 检查是否触发
                should_trigger = False
                if alert.condition == "above" and current_price > alert.target_price:
                    should_trigger = True
                elif alert.condition == "below" and current_price < alert.target_price:
                    should_trigger = True

                if should_trigger:
                    # 触发预警
                    alert.triggered = True
                    alert.triggered_at = datetime.now()

                    # 创建通知
                    notification = AlertNotification(
                        user_id=alert.user_id,
                        notification_type="price_alert",
                        related_id=alert.id,
                        title=f"🔔 价格预警触发",
                        content=f'{alert.breed_name}当前均价¥{current_price:.0f}，已{ "高于" if alert.condition == "above" else "低于"}您设置的目标价¥{alert.target_price:.0f}',
                    )
                    db.session.add(notification)
                    triggered_count += 1

                    logger.info(
                        f"价格预警触发: 用户{alert.user_id}, {alert.breed_name} ¥{current_price}"
                    )

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"检查完成，触发{triggered_count}个预警",
                "triggered_count": triggered_count,
            }
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"检查价格预警失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
