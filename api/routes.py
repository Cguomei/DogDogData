"""
API 蓝图模块
集中管理所有 API 路由，便于维护和扩展
为 APP 调用预留标准接口
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models import db, User, DogBreed
from sqlalchemy.exc import IntegrityError
from utils.api_response import APIResponse
from utils.auth import token_required, login_required_api

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


# ===== 公共接口（无需认证） =====


@api_bp.route("/breeds", methods=["GET"])
def get_breeds():
    """获取所有狗狗品种列表"""
    try:
        breeds = DogBreed.query.all()
        data = [
            {
                "id": b.id,
                "breed_name": b.breed_name,
                "avg_life_years": float(b.avg_life_years) if b.avg_life_years else None,
                "size_category": b.size_category,
                "popularity": b.popularity,
            }
            for b in breeds
        ]

        return APIResponse.success(data, message="获取成功")
    except Exception as e:
        return APIResponse.error(str(e), code=500)


@api_bp.route("/breeds/<int:id>", methods=["GET"])
def get_breed(id):
    """获取单个品种详情"""
    breed = DogBreed.query.get_or_404(id)
    data = {
        "id": breed.id,
        "breed_name": breed.breed_name,
        "avg_life_years": float(breed.avg_life_years) if breed.avg_life_years else None,
        "size_category": breed.size_category,
        "popularity": breed.popularity,
    }
    return APIResponse.success(data)


# ===== 需要认证的接口 =====


@api_bp.route("/breeds", methods=["POST"])
@login_required_api
def add_breed():
    """添加新狗狗品种"""
    data = request.get_json()

    if not data:
        return APIResponse.validation_error(["请求数据不能为空"])

    breed_name = data.get("breed_name")
    avg_life_years = data.get("avg_life_years")
    size_category = data.get("size_category")
    popularity = data.get("popularity", 0)

    # 验证
    errors = []
    if not breed_name or len(breed_name.strip()) < 2:
        errors.append("品种名称至少 2 个字符")

    if errors:
        return APIResponse.validation_error(errors)

    breed = DogBreed(
        breed_name=breed_name.strip(),
        avg_life_years=avg_life_years,
        size_category=size_category,
        popularity=popularity,
    )

    try:
        db.session.add(breed)
        db.session.commit()

        return APIResponse.created({"id": breed.id, "breed_name": breed.breed_name})
    except IntegrityError:
        db.session.rollback()
        return APIResponse.error("该品种已存在", code=400, error_code="DUPLICATE_ENTRY")
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"添加失败：{str(e)}", code=500)


@api_bp.route("/breeds/<int:id>", methods=["PUT"])
@login_required_api
def update_breed(id):
    """更新狗狗品种信息"""
    breed = DogBreed.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return APIResponse.validation_error(["请求数据不能为空"])

    breed_name = data.get("breed_name")
    avg_life_years = data.get("avg_life_years")
    size_category = data.get("size_category")
    popularity = data.get("popularity", 0)

    # 验证
    errors = []
    if not breed_name or len(breed_name.strip()) < 2:
        errors.append("品种名称至少 2 个字符")

    if errors:
        return APIResponse.validation_error(errors)

    # 检查是否与其他记录重复
    existing = DogBreed.query.filter(
        DogBreed.breed_name == breed_name.strip(), DogBreed.id != id
    ).first()
    if existing:
        return APIResponse.error(
            "该品种名称已存在", code=400, error_code="DUPLICATE_ENTRY"
        )

    breed.breed_name = breed_name.strip()
    breed.avg_life_years = avg_life_years
    breed.size_category = size_category
    breed.popularity = popularity

    try:
        db.session.commit()
        return APIResponse.success({"message": "更新成功"})
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"更新失败：{str(e)}", code=500)


@api_bp.route("/breeds/<int:id>", methods=["DELETE"])
@login_required_api
def delete_breed(id):
    """删除狗狗品种"""
    breed = DogBreed.query.get_or_404(id)

    try:
        db.session.delete(breed)
        db.session.commit()
        return APIResponse.success({"message": "删除成功"})
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"删除失败：{str(e)}", code=500)


# ===== 用户相关 API（为 APP 预留） =====


@api_bp.route("/profile", methods=["GET"])
@login_required_api
def get_profile():
    """获取当前用户资料"""
    from models_extended import UserProfile

    profile = UserProfile.query.filter_by(
        user_id=current_app.config.get("current_user_id", None)
    ).first()

    if not profile:
        return APIResponse.not_found("用户资料不存在")

    return APIResponse.success(profile.to_dict())


@api_bp.route("/favorites", methods=["GET"])
@login_required_api
def get_favorites():
    """获取用户收藏列表"""
    from models_extended import UserFavorite

    favorites = UserFavorite.query.filter_by(
        user_id=current_app.config.get("current_user_id", None)
    ).all()

    data = [fav.to_dict() for fav in favorites]
    return APIResponse.success(data)


@api_bp.route("/favorites/<int:breed_id>", methods=["POST"])
@login_required_api
def add_favorite(breed_id):
    """添加收藏"""
    from models_extended import UserFavorite

    breed = DogBreed.query.get_or_404(breed_id)

    # 检查是否已收藏
    existing = UserFavorite.query.filter_by(
        user_id=current_app.config.get("current_user_id", None), breed_id=breed_id
    ).first()

    if existing:
        return APIResponse.error(
            "已收藏该品种", code=400, error_code="ALREADY_FAVORITED"
        )

    note = request.get_json().get("note", "") if request.get_json() else ""

    favorite = UserFavorite(
        user_id=current_app.config.get("current_user_id", None),
        breed_id=breed_id,
        note=note,
    )

    try:
        db.session.add(favorite)
        db.session.commit()
        return APIResponse.created(favorite.to_dict())
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"收藏失败：{str(e)}", code=500)


@api_bp.route("/favorites/<int:breed_id>", methods=["DELETE"])
@login_required_api
def remove_favorite(breed_id):
    """取消收藏"""
    from models_extended import UserFavorite

    favorite = UserFavorite.query.filter_by(
        user_id=current_app.config.get("current_user_id", None), breed_id=breed_id
    ).first_or_404()

    try:
        db.session.delete(favorite)
        db.session.commit()
        return APIResponse.success({"message": "取消收藏成功"})
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(f"取消收藏失败：{str(e)}", code=500)
