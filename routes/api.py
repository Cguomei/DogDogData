from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user
from utils.auth import login_required_api
from models import DogBreed, db
from sqlalchemy.exc import IntegrityError
import os
import sys
import subprocess
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import text

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

APP_VERSION = "v5.0.0"

api_bp = Blueprint("api", __name__)


# ===== 宠物日志保存 API =====
@api_bp.route("/api/save_pet_logs", methods=["POST"])
def save_pet_logs():
    """保存宠物日志到 log 文件夹"""
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "..", "log")
        os.makedirs(log_dir, exist_ok=True)

        content = request.data.decode("utf-8")
        lines = content.split("\n")
        raw_session = lines[0].replace("session=", "") if lines else "unknown"
        session = re.sub(r"[^a-zA-Z0-9_-]", "", raw_session)[:64] or "unknown"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pet_log_{session}_{timestamp}.txt"
        filepath = os.path.join(log_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===== 自定义数据分析 =====
@api_bp.route("/custom-analysis")
def custom_analysis():
    """用户自定义数据分析页面"""
    return render_template("custom_analysis.html")


@api_bp.route("/api/upload-data", methods=["POST"])
def upload_data():
    """API: 接收用户上传的 CSV/Excel 数据（含质量校验）"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "文件名为空"}), 400

        # 读取上传的文件
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8")
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "不支持的文件格式，请上传 CSV 或 Excel 文件"}), 400

        # ===== 数据质量校验 =====
        quality_report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "issues": [],
        }

        # 1. 空值检测
        null_counts = df.isnull().sum()
        for col, null_count in null_counts.items():
            null_ratio = null_count / len(df) * 100
            if null_ratio > 30:
                quality_report["issues"].append(
                    {
                        "type": "high_null_ratio",
                        "column": col,
                        "message": f'列 "{col}" 空值比例过高: {null_ratio:.1f}%',
                        "severity": "warning",
                    }
                )

        # 2. 数据类型检测
        for col in df.columns:
            if df[col].dtype in ["int64", "float64"]:
                # 检查是否有非数字值
                non_numeric = df[col][
                    pd.to_numeric(df[col], errors="coerce").isna()
                ].count()
                if non_numeric > 0:
                    quality_report["issues"].append(
                        {
                            "type": "non_numeric_in_numeric_column",
                            "column": col,
                            "message": f'数值列 "{col}" 中有 {non_numeric} 个非数字值',
                            "severity": "error",
                        }
                    )

        # 3. 异常值检测（示例：检测负数）
        for col in df.select_dtypes(include=["number"]).columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                quality_report["issues"].append(
                    {
                        "type": "negative_values",
                        "column": col,
                        "message": f'列 "{col}" 中有 {negative_count} 个负数值',
                        "severity": "warning",
                    }
                )

        # 4. 重复值检测
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            quality_report["issues"].append(
                {
                    "type": "duplicate_rows",
                    "message": f"发现 {duplicate_count} 行完全重复的数据",
                    "severity": "info",
                }
            )

        # 返回前 100 行数据和校验报告
        columns = df.columns.tolist()
        data_sample = df.head(100).to_dict("records")

        return jsonify(
            {
                "success": True,
                "columns": columns,
                "row_count": len(df),
                "data": data_sample,
                "quality_report": quality_report,
            }
        )
    except Exception as e:
        return jsonify({"error": f"解析文件失败：{str(e)}"}), 500


@api_bp.route("/api/generate-chart", methods=["POST"])
def generate_chart():
    """API: 根据用户配置生成图表"""
    try:
        data = request.get_json()
        chart_type = data.get("chart_type")  # scatter, line, bar, pie
        x_column = data.get("x_column")
        y_column = data.get("y_column")
        title = data.get("title", "自定义图表")
        upload_data = data.get("data", [])  # 前端传递的表格数据

        if not all([chart_type, x_column, y_column]):
            return jsonify({"error": "缺少必要参数"}), 400

        if not upload_data or len(upload_data) == 0:
            return jsonify({"error": "没有数据可生成图表"}), 400

        # 将数据转换为DataFrame
        df = pd.DataFrame(upload_data)

        # 验证列是否存在
        if x_column not in df.columns or y_column not in df.columns:
            return jsonify({"error": f"列名不存在: {x_column} 或 {y_column}"}), 400

        # 提取数据
        x_data = df[x_column].tolist()
        y_data = df[y_column].tolist()

        # 过滤无效数据
        valid_pairs = [
            (x, y) for x, y in zip(x_data, y_data) if pd.notna(x) and pd.notna(y)
        ]

        if len(valid_pairs) == 0:
            return jsonify({"error": "没有有效数据对"}), 400

        x_valid, y_valid = zip(*valid_pairs)

        # 根据图表类型生成 PyECharts 配置
        from pyecharts.charts import Scatter, Line, Bar, Pie
        from pyecharts import options as opts

        if chart_type == "scatter":
            chart = (
                Scatter()
                .add_xaxis(list(x_valid))
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column),
                )
            )

        elif chart_type == "line":
            chart = (
                Line()
                .add_xaxis(list(x_valid))
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column),
                )
            )

        elif chart_type == "bar":
            chart = (
                Bar()
                .add_xaxis([str(x) for x in x_valid])
                .add_yaxis(title, list(y_valid))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(name=x_column),
                    yaxis_opts=opts.AxisOpts(name=y_column),
                )
            )

        elif chart_type == "pie":
            # 饼图需要特殊处理
            pie_data = [[str(x), float(y)] for x, y in valid_pairs]
            chart = (
                Pie()
                .add(title, pie_data)
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
            )

        else:
            return jsonify({"error": f"不支持的图表类型: {chart_type}"}), 400

        # 渲染为 HTML
        chart_html = chart.render_embed()

        return jsonify(
            {
                "success": True,
                "chart_html": chart_html,
                "message": f"图表已生成：{title}",
                "data_points": len(valid_pairs),
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"生成图表失败：{str(e)}"}), 500


# ===== 狗狗品种 API =====
@api_bp.route("/api/breeds")
def get_breeds():
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
    return jsonify(data)


@api_bp.route("/api/breeds/<int:id>")
def get_breed(id):
    breed = DogBreed.query.get_or_404(id)
    return jsonify(
        {
            "id": breed.id,
            "breed_name": breed.breed_name,
            "avg_life_years": (
                float(breed.avg_life_years) if breed.avg_life_years else None
            ),
            "size_category": breed.size_category,
            "popularity": breed.popularity,
        }
    )


@api_bp.route("/api/breeds", methods=["POST"])
@login_required_api
def add_breed():
    """添加新的狗狗品种（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({"error": "权限不足，需要管理员权限"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    breed_name = data.get("breed_name")
    avg_life_years = data.get("avg_life_years")
    size_category = data.get("size_category")
    popularity = data.get("popularity", 0)

    if not breed_name or len(breed_name.strip()) < 2:
        return jsonify({"error": "品种名称至少 2 个字符"}), 400

    breed = DogBreed(
        breed_name=breed_name.strip(),
        avg_life_years=avg_life_years,
        size_category=size_category,
        popularity=popularity,
    )

    try:
        db.session.add(breed)
        db.session.commit()
        return jsonify({"message": "添加成功", "id": breed.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "添加失败，可能是品种名称重复"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"添加失败：{str(e)}"}), 500


@api_bp.route("/api/breeds/<int:id>", methods=["PUT"])
@login_required_api
def update_breed(id):
    """更新狗狗品种信息（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({"error": "权限不足，需要管理员权限"}), 403

    breed = DogBreed.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    breed_name = data.get("breed_name")
    avg_life_years = data.get("avg_life_years")
    size_category = data.get("size_category")
    popularity = data.get("popularity", 0)

    if not breed_name or len(breed_name.strip()) < 2:
        return jsonify({"error": "品种名称至少 2 个字符"}), 400

    # 检查是否与其他记录重复
    existing = DogBreed.query.filter(
        DogBreed.breed_name == breed_name.strip(), DogBreed.id != id
    ).first()
    if existing:
        return jsonify({"error": "该品种名称已存在"}), 400

    breed.breed_name = breed_name.strip()
    breed.avg_life_years = avg_life_years
    breed.size_category = size_category
    breed.popularity = popularity

    try:
        db.session.commit()
        return jsonify({"message": "更新成功"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "更新失败"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失败：{str(e)}"}), 500


@api_bp.route("/api/breeds/<int:id>", methods=["DELETE"])
@login_required_api
def delete_breed(id):
    """删除狗狗品种（需要管理员权限）"""
    # 检查管理员权限
    if not current_user.is_admin():
        return jsonify({"error": "权限不足，需要管理员权限"}), 403

    breed = DogBreed.query.get_or_404(id)

    try:
        db.session.delete(breed)
        db.session.commit()
        return jsonify({"message": "删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除失败：{str(e)}"}), 500


# ===== 狗粮数据 API =====
@api_bp.route("/api/food")
def get_food():
    """获取狗粮列表数据"""
    from charts import get_dog_food_list

    food_list = get_dog_food_list()
    return jsonify(food_list)


@api_bp.route("/api/food/statistics")
def get_food_statistics():
    """获取狗粮统计数据"""
    from charts import get_dog_food_stats

    stats = get_dog_food_stats()
    return jsonify(stats)


@api_bp.route("/api/food/list")
def get_food_list():
    """获取狗粮列表（支持分页）"""
    from charts import get_dog_food_list

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # 限制每页数量
    per_page = min(per_page, 100)

    all_foods = get_dog_food_list(limit=1000)  # 获取足够多的数据
    total = len(all_foods)

    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_foods = all_foods[start:end]

    return jsonify(
        {
            "foods": paginated_foods,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
    )


@api_bp.route("/api/food/search")
def search_food():
    """搜索狗粮（按品牌或产地）"""
    from charts import get_dog_food_list

    brand = request.args.get("brand", "")
    origin = request.args.get("origin", "")

    all_foods = get_dog_food_list(limit=1000)

    # 过滤
    filtered = all_foods
    if brand:
        filtered = [f for f in filtered if brand.lower() in f.get("name", "").lower()]
    if origin:
        filtered = [
            f for f in filtered if origin.lower() in f.get("origin", "").lower()
        ]

    return jsonify({"foods": filtered})


@api_bp.route("/api/food/filter")
def filter_food():
    """筛选狗粮（按价格区间）"""
    from charts import get_dog_food_list

    try:
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
    except:
        return jsonify({"error": "价格参数格式错误"}), 400

    all_foods = get_dog_food_list(limit=1000)

    # 过滤价格
    filtered = all_foods
    if min_price is not None and max_price is not None:
        filtered = [
            f
            for f in filtered
            if isinstance(f.get("price"), (int, float))
            and min_price <= f["price"] <= max_price
        ]
    elif min_price is not None:
        filtered = [
            f
            for f in filtered
            if isinstance(f.get("price"), (int, float)) and f["price"] >= min_price
        ]
    elif max_price is not None:
        filtered = [
            f
            for f in filtered
            if isinstance(f.get("price"), (int, float)) and f["price"] <= max_price
        ]

    return jsonify({"foods": filtered})


@api_bp.route("/api/food/<int:food_id>")
def get_food_detail(food_id):
    """获取单个狗粮详情"""
    from charts import get_dog_food_list

    all_foods = get_dog_food_list(limit=1000)

    if food_id < len(all_foods):
        return jsonify(all_foods[food_id])
    else:
        return jsonify({"error": "未找到该狗粮"}), 404


@api_bp.route("/api/food/export")
def export_food_data():
    """导出狗粮数据"""
    from charts import get_dog_food_list
    import pandas as pd
    import io
    from flask import send_file

    format_type = request.args.get("format", "csv")

    foods = get_dog_food_list(limit=1000)
    df = pd.DataFrame(foods)

    if format_type == "csv":
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_buffer.seek(0)

        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="dog_food_data.csv",
        )
    else:  # excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="DogFood")
        excel_buffer.seek(0)

        return send_file(
            excel_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="dog_food_data.xlsx",
        )


# ===== 数据导出 API =====
@api_bp.route("/api/export-data", methods=["POST"])
def export_data():
    """导出数据为 Excel 或 CSV"""
    try:
        data = request.get_json()
        export_format = data.get("format", "excel")  # excel 或 csv
        table_data = data.get("data", [])
        filename = data.get("filename", "data")

        if not table_data:
            return jsonify({"error": "没有数据可导出"}), 400

        df = pd.DataFrame(table_data)

        import io
        from flask import send_file

        if export_format == "csv":
            # 导出 CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
            csv_buffer.seek(0)

            return send_file(
                io.BytesIO(csv_buffer.getvalue().encode("utf-8-sig")),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"{filename}.csv",
            )

        else:  # excel
            # 导出 Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Data")
            excel_buffer.seek(0)

            return send_file(
                excel_buffer,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"{filename}.xlsx",
            )

    except Exception as e:
        return jsonify({"error": f"导出失败：{str(e)}"}), 500


# ===== 测试页面 =====
@api_bp.route("/test-pet")
def test_pet_page():
    """2.5D 宠物功能测试页面"""
    return render_template("test_pet.html")


@api_bp.route("/clear-cache")
def clear_cache_page():
    """清除缓存指南页面"""
    return render_template("clear_cache.html")


@api_bp.route("/test-pet-alpine")
def test_pet_alpine_page():
    """Alpine.js 宠物组件测试页面"""
    return render_template("test_pet_alpine.html")


@api_bp.route("/api/restart", methods=["POST"])
def api_restart():
    """API: 重启应用（需要管理员权限）"""
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({"success": False, "message": "权限不足"}), 403

    try:
        script_path = sys.argv[0]
        subprocess.Popen([sys.executable, script_path])
        return jsonify({"success": True, "message": "应用正在重启..."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ===== 国际化 API =====
@api_bp.route("/api/set-language", methods=["POST"])
def set_language():
    """设置用户语言偏好"""
    from flask import session

    data = request.get_json()
    lang = data.get("language", "zh_CN")

    # 验证语言代码
    supported_languages = ["zh_CN", "en_US", "ja_JP"]
    if lang not in supported_languages:
        return jsonify({"error": f"不支持的语言: {lang}"}), 400

    # 保存到 Session
    session["language"] = lang

    return (
        jsonify({"success": True, "message": f"语言已切换为 {lang}", "language": lang}),
        200,
    )


@api_bp.route("/api/get-language")
def get_language():
    """获取当前语言设置"""
    from flask import session

    current_lang = session.get("language", "zh_CN")

    return (
        jsonify(
            {
                "language": current_lang,
                "supported_languages": ["zh_CN", "en_US", "ja_JP"],
            }
        ),
        200,
    )


@api_bp.route("/api/dashboard/stats")
def get_dashboard_stats():
    """获取首页统计数据（用于 Alpine.js 动态刷新）"""
    try:
        from charts import get_dashboard_stats_from_summary

        stats = get_dashboard_stats_from_summary()

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": f"获取统计数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/<chart_type>/data")
def get_chart_data(chart_type):
    """获取图表数据（用于 Alpine.js 动态渲染）"""
    try:
        # 这里应该根据 chart_type 返回对应的数据
        # 示例实现
        chart_data_map = {
            "scatter": {"x_data": [1, 2, 3], "y_data": [4, 5, 6]},
            "line": {"x_data": [1, 2, 3], "y_data": [4, 5, 6]},
            "bar": {"x_data": ["A", "B", "C"], "y_data": [10, 20, 30]},
        }

        data = chart_data_map.get(chart_type, {"x_data": [], "y_data": []})
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"获取图表数据失败: {str(e)}"}), 500


@api_bp.route("/api/charts/list")
def get_charts_list():
    """获取图表列表（用于图表列表页面）"""
    try:
        charts = [
            {
                "id": "scatter",
                "title": "价格散点图",
                "description": "展示狗狗价格分布情况",
                "category": "basic",
                "icon": "📈",
            },
            {
                "id": "line",
                "title": "体重折线图",
                "description": "展示狗狗体重趋势",
                "category": "basic",
                "icon": "📉",
            },
            {
                "id": "bar",
                "title": "级别柱状图",
                "description": "展示不同级别的狗狗数量",
                "category": "basic",
                "icon": "📊",
            },
            {
                "id": "hist",
                "title": "TOP10 直方图",
                "description": "热门狗狗品种和店铺排行",
                "category": "advanced",
                "icon": "🏆",
            },
            {
                "id": "funnel",
                "title": "价格漏斗图",
                "description": "价格区间转化分析",
                "category": "advanced",
                "icon": "🔍",
            },
            {
                "id": "map",
                "title": "世界地图",
                "description": "狗狗家乡分布地图",
                "category": "map",
                "icon": "🗺️",
            },
        ]

        return jsonify(charts), 200
    except Exception as e:
        return jsonify({"error": f"获取图表列表失败: {str(e)}"}), 500


@api_bp.route("/api/health")
def health_check():
    """健康检查接口（供监控系统调用）"""
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    if HAS_PSUTIL:
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            system_info = {
                "status": "ok",
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent,
                "available_memory_mb": memory.available / (1024 * 1024),
            }
        except Exception:
            system_info = {"status": "unavailable"}
    else:
        system_info = {"status": "psutil not installed"}

    is_healthy = db_status == "ok"
    status_code = 200 if is_healthy else 503

    return (
        jsonify(
            {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": APP_VERSION,
                "python_version": sys.version,
                "checks": {"database": db_status, "system": system_info},
            }
        ),
        status_code,
    )


# ===== 图表数据 API =====
@api_bp.route("/api/chart/scatter/data")
def get_scatter_data():
    """获取价格散点图数据"""
    try:
        from charts import get_price_scatter_data

        data = get_price_scatter_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取散点图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/line/data")
def get_line_data():
    """获取体重折线图数据"""
    try:
        from charts import get_weight_line_data

        data = get_weight_line_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取折线图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/bar/data")
def get_bar_data():
    """获取级别柱状图数据"""
    try:
        from charts import get_level_bar_data

        data = get_level_bar_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取柱状图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/hist/data")
def get_hist_data():
    """获取TOP10直方图数据"""
    try:
        from charts import get_hist_data

        data = get_hist_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取直方图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/funnel/data")
def get_funnel_data():
    """获取价格漏斗图数据"""
    try:
        from charts import get_funnel_data

        data = get_funnel_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取漏斗图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/map/data")
def get_map_data():
    """获取世界地图数据"""
    try:
        from charts import get_map_data

        data = get_map_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"获取地图数据失败: {str(e)}"}), 500


@api_bp.route("/api/chart/<name>")
def get_chart_embed(name):
    """返回指定图表的 embed HTML（用于数据大盘）"""
    try:
        from charts import (
            get_price_scatter,
            get_weight_line,
            get_level_bar,
            get_shop_top10_hist,
            get_price_funnel,
            get_world_map,
        )

        funcs = {
            "scatter": get_price_scatter,
            "line": get_weight_line,
            "bar": get_level_bar,
            "hist": get_shop_top10_hist,
            "funnel": get_price_funnel,
            "map": get_world_map,
        }
        func = funcs.get(name)
        if not func:
            return jsonify({"error": "未知图表"}), 404
        html = func()
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"<p>图表加载失败: {str(e)}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}
