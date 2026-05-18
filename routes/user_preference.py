"""
用户偏好管理路由
提供用户偏好的CRUD操作和个性化推荐功能
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models_extended import UserPreference
import json
import logging

logger = logging.getLogger("user_preference")

preference_bp = Blueprint("user_preference", __name__)


@preference_bp.route("/api/user/preferences", methods=["GET"])
@login_required
def get_preferences():
    """获取当前用户的偏好设置"""
    try:
        preference = UserPreference.query.filter_by(user_id=current_user.id).first()

        if not preference:
            # 返回默认偏好
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "preferred_breeds": [],
                        "preferred_size": "all",
                        "budget_range": "",
                        "experience_level": "beginner",
                        "purpose": "",
                        "max_age": None,
                        "gender_preference": "any",
                        "response_style": "concise",
                        "auto_save_chat": True,
                        "price_alert_enabled": False,
                        "new_breed_alert_enabled": False,
                    },
                }
            )

        return jsonify({"success": True, "data": preference.to_dict()})

    except Exception as e:
        logger.error(f"获取偏好失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@preference_bp.route("/api/user/preferences", methods=["POST", "PUT"])
@login_required
def update_preferences():
    """更新用户偏好设置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400

        # 查找或创建偏好记录
        preference = UserPreference.query.filter_by(user_id=current_user.id).first()

        if not preference:
            preference = UserPreference(user_id=current_user.id)
            db.session.add(preference)

        # 更新字段
        if "preferred_breeds" in data:
            preference.preferred_breeds = json.dumps(
                data["preferred_breeds"], ensure_ascii=False
            )

        if "preferred_size" in data:
            valid_sizes = ["small", "medium", "large", "all"]
            if data["preferred_size"] not in valid_sizes:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"无效的体型值，支持: {valid_sizes}",
                        }
                    ),
                    400,
                )
            preference.preferred_size = data["preferred_size"]

        if "budget_range" in data:
            preference.budget_range = data["budget_range"]

        if "experience_level" in data:
            valid_levels = ["beginner", "intermediate", "advanced"]
            if data["experience_level"] not in valid_levels:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"无效的经验等级，支持: {valid_levels}",
                        }
                    ),
                    400,
                )
            preference.experience_level = data["experience_level"]

        if "purpose" in data:
            preference.purpose = data["purpose"]

        if "max_age" in data:
            preference.max_age = data["max_age"]

        if "gender_preference" in data:
            valid_genders = ["male", "female", "any"]
            if data["gender_preference"] not in valid_genders:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"无效的性别偏好，支持: {valid_genders}",
                        }
                    ),
                    400,
                )
            preference.gender_preference = data["gender_preference"]

        if "response_style" in data:
            valid_styles = ["concise", "detailed", "friendly"]
            if data["response_style"] not in valid_styles:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"无效的回复风格，支持: {valid_styles}",
                        }
                    ),
                    400,
                )
            preference.response_style = data["response_style"]

        if "auto_save_chat" in data:
            preference.auto_save_chat = bool(data["auto_save_chat"])

        if "price_alert_enabled" in data:
            preference.price_alert_enabled = bool(data["price_alert_enabled"])

        if "new_breed_alert_enabled" in data:
            preference.new_breed_alert_enabled = bool(data["new_breed_alert_enabled"])

        db.session.commit()

        logger.info(f"用户 {current_user.username} 更新偏好设置")

        return jsonify(
            {"success": True, "message": "偏好设置已保存", "data": preference.to_dict()}
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新偏好失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@preference_bp.route("/api/user/preferences/recommendations", methods=["GET"])
@login_required
def get_personalized_recommendations():
    """基于用户偏好获取个性化推荐"""
    try:
        from sqlalchemy import text

        preference = UserPreference.query.filter_by(user_id=current_user.id).first()

        if not preference:
            return jsonify({"success": True, "message": "请先设置您的偏好", "data": []})

        # 构建查询条件
        conditions = []
        params = {}

        # 体型筛选
        if preference.preferred_size and preference.preferred_size != "all":
            size_map = {
                "small": ["小型犬", "小型"],
                "medium": ["中型犬", "中型"],
                "large": ["大型犬", "大型"],
            }
            size_keywords = size_map.get(preference.preferred_size, [])
            if size_keywords:
                size_condition = " OR ".join(
                    [f"size LIKE :size{i}" for i in range(len(size_keywords))]
                )
                conditions.append(f"({size_condition})")
                for i, kw in enumerate(size_keywords):
                    params[f"size{i}"] = f"%{kw}%"

        # 预算筛选
        if preference.budget_range:
            if preference.budget_range == "0-3000":
                conditions.append("price <= 3000")
            elif preference.budget_range == "3000-8000":
                conditions.append("price > 3000 AND price <= 8000")
            elif preference.budget_range == "8000+":
                conditions.append("price > 8000")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询推荐品种
        sql = text(f"""
            SELECT 
                dog_name,
                AVG(price) as avg_price,
                size,
                COUNT(*) as count
            FROM jd_dogs
            WHERE {where_clause}
            GROUP BY dog_name, size
            ORDER BY count DESC
            LIMIT 10
        """)

        results = db.session.execute(sql, params).fetchall()

        recommendations = []
        for row in results:
            recommendations.append(
                {
                    "breed_name": row.dog_name,
                    "avg_price": float(row.avg_price) if row.avg_price else 0,
                    "size": row.size or "未知",
                    "popularity": row.count,
                }
            )

        logger.info(
            f"为用户 {current_user.username} 生成个性化推荐: {len(recommendations)}个"
        )

        return jsonify(
            {
                "success": True,
                "data": recommendations,
                "preference_summary": {
                    "size": preference.preferred_size,
                    "budget": preference.budget_range,
                    "experience": preference.experience_level,
                },
            }
        )

    except Exception as e:
        logger.error(f"生成推荐失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@preference_bp.route("/api/user/preferences/stats", methods=["GET"])
@login_required
def get_preference_stats():
    """获取用户偏好统计信息"""
    try:
        from models_extended import UserFavorite

        # 收藏数量
        favorite_count = UserFavorite.query.filter_by(user_id=current_user.id).count()

        # 偏好设置状态
        preference = UserPreference.query.filter_by(user_id=current_user.id).first()
        has_preference = preference is not None

        # 对话历史统计（如果有的话）
        from models_extended import ChatSession

        session_count = ChatSession.query.filter_by(user_id=current_user.id).count()

        stats = {
            "favorite_count": favorite_count,
            "has_preference": has_preference,
            "session_count": session_count,
            "preference_last_updated": (
                preference.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if preference and preference.updated_at
                else None
            ),
        }

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
