# charts.py
import json

from flask import current_app
from sqlalchemy import func, case, cast, Numeric, Float
from pyecharts import options as opts
from pyecharts.globals import ThemeType

from models import db
from models_charts import JdDog, DogPrice, DogWykl, DashboardSummary

# 中文→英文地名映射（避免每次调用翻译API）
COUNTRY_MAP = {
    "中国": "China", "美国": "United States", "英国": "United Kingdom",
    "德国": "Germany", "法国": "France", "日本": "Japan", "韩国": "South Korea",
    "加拿大": "Canada", "澳大利亚": "Australia", "俄罗斯": "Russia",
    "意大利": "Italy", "西班牙": "Spain", "荷兰": "Netherlands",
    "瑞士": "Switzerland", "瑞典": "Sweden", "挪威": "Norway",
    "芬兰": "Finland", "丹麦": "Denmark", "比利时": "Belgium",
    "奥地利": "Austria", "爱尔兰": "Ireland", "葡萄牙": "Portugal",
    "波兰": "Poland", "捷克": "Czech Republic", "匈牙利": "Hungary",
    "希腊": "Greece", "土耳其": "Turkey", "印度": "India",
    "泰国": "Thailand", "新加坡": "Singapore", "马来西亚": "Malaysia",
    "越南": "Vietnam", "菲律宾": "Philippines", "新西兰": "New Zealand",
    "巴西": "Brazil", "阿根廷": "Argentina", "墨西哥": "Mexico",
    "南非": "South Africa", "乌克兰": "Ukraine", "罗马尼亚": "Romania",
}

# ==================== 首页看板数据函数 ====================


def get_dashboard_stats_from_summary():
    """从 dashboard_summary 表获取统计数据（速度快）"""
    try:
        row = DashboardSummary.query.filter_by(id=1).first()
        if row:
            return {
                "total_dogs": row.total_dogs,
                "avg_price": float(row.avg_price) if row.avg_price else 0,
                "total_shops": row.total_shops,
                "total_breeds": row.total_breeds,
                "top_breeds": row.top_breeds if row.top_breeds else [],
                "top_shops": row.top_shops if row.top_shops else [],
                "price_dist": row.price_dist if row.price_dist else [],
                "level_pet": row.level_pet or 0,
                "level_blood": row.level_blood or 0,
            }
        else:
            stats = get_dashboard_stats()
            update_dashboard_summary()
            return stats
    except Exception as e:
        print("从汇总表读取失败，回退到原始查询", e)
        return get_dashboard_stats()


def get_dashboard_stats():
    """获取首页看板的各项统计数据，返回字典"""
    try:
        total_dogs = db.session.query(func.count(JdDog.number)).scalar() or 0
        avg_price = db.session.query(func.avg(JdDog.price)).scalar()
        avg_price = round(float(avg_price), 2) if avg_price else 0
        total_shops = db.session.query(func.count(func.distinct(JdDog.shop_name))).scalar() or 0
        total_breeds = db.session.query(func.count(func.distinct(JdDog.dog_name))).scalar() or 0

        top_breeds = [
            (row[0], row[1])
            for row in db.session.query(JdDog.dog_name, func.count(JdDog.number))
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(5)
            .all()
        ]

        top_shops = [
            (row[0], row[1])
            for row in db.session.query(JdDog.shop_name, func.count(JdDog.number))
            .group_by(JdDog.shop_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(5)
            .all()
        ]

        price_dist = _get_price_distribution()

        pet_count = db.session.query(func.count(JdDog.number)).filter(JdDog.pet_level == "宠物级").scalar() or 0
        blood_count = db.session.query(func.count(JdDog.number)).filter(JdDog.pet_level == "血统级").scalar() or 0

        return {
            "total_dogs": total_dogs,
            "avg_price": avg_price,
            "total_shops": total_shops,
            "total_breeds": total_breeds,
            "top_breeds": top_breeds,
            "top_shops": top_shops,
            "price_dist": price_dist,
            "level_pet": pet_count,
            "level_blood": blood_count,
        }
    except Exception as e:
        print("获取看板数据出错：", e)
        return {
            "total_dogs": 0,
            "avg_price": 0,
            "total_shops": 0,
            "total_breeds": 0,
            "top_breeds": [],
            "top_shops": [],
            "price_dist": [],
            "level_pet": 0,
            "level_blood": 0,
        }


def _get_price_distribution():
    """获取价格区间分布"""
    price_ranges = [
        (0, 2500, "0-2.5k"),
        (2500, 5000, "2.5k-5k"),
        (5000, 7500, "5k-7.5k"),
        (7500, 10000, "7.5k-1w"),
        (10000, 20000, "1w-2w"),
        (20000, 1000000, "2w以上"),
    ]
    result = []
    for low, high, label in price_ranges:
        count = (
            db.session.query(func.count(JdDog.number))
            .filter(JdDog.price > low, JdDog.price <= high)
            .scalar()
            or 0
        )
        result.append((label, count))
    return result


# ==================== 1. 价格散点图 ====================


def get_price_scatter():
    """狗狗价格散点图"""
    try:
        rows = (
            db.session.query(JdDog.price, func.count(JdDog.price))
            .group_by(JdDog.price)
            .order_by(JdDog.price)
            .all()
        )
        n_list = [r[0] for r in rows]
        n_list1 = [r[1] for r in rows]
    except Exception as e:
        print("价格散点图数据库查询出错：", e)
        return "<p>价格散点图数据加载失败</p>"

    from pyecharts.charts import Scatter

    c = (
        Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(xaxis_data=n_list)
        .add_yaxis(
            series_name="数量",
            y_axis=n_list1,
            symbol_size=5,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)),
            tooltip_opts=opts.TooltipOpts(is_show=False),
        )
    )
    return c.render_embed()


# ==================== 2. 体重折线图 ====================


def get_weight_line():
    """狗狗体重折线图"""
    from pyecharts.charts import Line

    try:
        weight_case = case(
            (JdDog.weight > 20, "20kg以上"),
            (JdDog.weight > 10, "10-20kg"),
            (JdDog.weight > 5, "5-10kg"),
            (JdDog.weight > 2, "2-5kg"),
            (JdDog.weight > 1, "1-2kg"),
            (JdDog.weight > 0, "0-1kg"),
            else_="000",
        )

        rows = (
            db.session.query(weight_case.label("weight_bucket"), func.count(JdDog.number))
            .filter(JdDog.weight.isnot(None))
            .group_by("weight_bucket")
            .all()
        )

        # Sort by the weight bucket order
        bucket_order = {"0-1kg": 0, "1-2kg": 1, "2-5kg": 2, "5-10kg": 3, "10-20kg": 4, "20kg以上": 5}
        sorted_rows = sorted(rows, key=lambda r: bucket_order.get(r[0], 99))

        n1 = [r[0] for r in sorted_rows if r[0] != "000"]
        n2 = [r[1] for r in sorted_rows if r[0] != "000"]
    except Exception as e:
        print("体重折线图数据库查询出错：", e)
        return "<p>体重折线图数据加载失败</p>"

    c = (
        Line(init_opts=opts.InitOpts(width="800px", height="500px"))
        .add_xaxis(xaxis_data=n1)
        .add_yaxis(
            series_name="体重",
            y_axis=n2,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="狗狗体重分布图"),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )
    return c.render_embed()


# ==================== 3. 级别柱状图（体型分布分析）====================


def get_level_bar():
    """体型分布分析图（小型/中型/大型）"""
    from pyecharts.charts import Bar

    try:
        rows = (
            db.session.query(
                JdDog.dog_name,
                func.sum(case((JdDog.size == "小型犬", 1), else_=0)).label("small"),
                func.sum(case((JdDog.size == "中型犬", 1), else_=0)).label("medium"),
                func.sum(case((JdDog.size == "大型犬", 1), else_=0)).label("large"),
            )
            .filter(JdDog.size.isnot(None), JdDog.size != "")
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(20)
            .all()
        )

        n_list = [r[0] for r in rows]
        n_list1 = [r[1] or 0 for r in rows]
        n_list2 = [r[2] or 0 for r in rows]
        n_list3 = [r[3] or 0 for r in rows]
    except Exception as e:
        print("体型分布图数据库查询出错：", e)
        return "<p>体型分布图数据加载失败</p>"

    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="500px", theme=ThemeType.LIGHT))
        .add_xaxis(n_list)
        .add_yaxis("小型犬", n_list1, stack="stack")
        .add_yaxis("中型犬", n_list2, stack="stack")
        .add_yaxis("大型犬", n_list3, stack="stack")
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
                axislabel_opts=opts.LabelOpts(rotate=-45),
            ),
            title_opts=opts.TitleOpts(title="🐕 体型分布分析 - TOP20 犬种"),
            legend_opts=opts.LegendOpts(pos_top="10%"),
        )
    )
    return bar.render_embed()


# ==================== 4. 狗狗+店铺TOP10直方图 ====================


def get_shop_top10_hist():
    """售卖前10种宠物狗 + 店铺售卖种类最多top-10直方图"""
    from pyecharts.charts import Bar

    try:
        dog_rows = (
            db.session.query(JdDog.dog_name, func.count(JdDog.number))
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(10)
            .all()
        )
        shop_rows = (
            db.session.query(JdDog.shop_name, func.count(JdDog.number))
            .group_by(JdDog.shop_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(10)
            .all()
        )

        dog_list = [r[0] for r in dog_rows]
        dog_list1 = [r[1] for r in dog_rows]
        data_list = [r[0] for r in shop_rows]
        data_list1 = [r[1] for r in shop_rows]

        x = dog_list + data_list
        dog_list1.reverse()  # 保持与原代码一致
        y = dog_list1 + data_list1
    except Exception as e:
        print("直方图数据库查询出错：", e)
        return "<p>直方图数据加载失败</p>"

    c = (
        Bar(init_opts=opts.InitOpts(width="1300px", height="500px", theme=ThemeType.LIGHT))
        .add_xaxis(x)
        .add_yaxis("top-10", y, category_gap=10, color="#d48265")
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
                axislabel_opts=opts.LabelOpts(rotate=-45),
            ),
            yaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            datazoom_opts=opts.DataZoomOpts(type_="inside"),
            title_opts=opts.TitleOpts(title="售卖前10种宠物狗+店铺售卖种类最多top-10直方图"),
        )
    )
    return c.render_embed()


# ==================== 5. 价格段漏斗图 ====================


def get_price_funnel():
    """价格段漏斗图"""
    from pyecharts.charts import Funnel

    # Order of price ranges used for sorting
    _FUNNEL_ORDER = {"0-2.5k": 0, "2.5k-5k": 1, "5k-7.5k": 2, "7.5k-1w": 3, "1w-2w": 4, "2w 以上": 5}

    try:
        price_case = case(
            (JdDog.price > 20000, "2w 以上"),
            (JdDog.price > 10000, "1w-2w"),
            (JdDog.price > 7500, "7.5k-1w"),
            (JdDog.price > 5000, "5k-7.5k"),
            (JdDog.price > 2500, "2.5k-5k"),
            (JdDog.price > 0, "0-2.5k"),
            else_="其他",
        )

        rows = (
            db.session.query(price_case.label("price_range"), func.count(JdDog.number))
            .filter(JdDog.price.isnot(None), JdDog.price > 0)
            .group_by("price_range")
            .all()
        )

        # Sort in price range order (Python-side, MySQL/SQLite compatible)
        sorted_rows = sorted(rows, key=lambda r: _FUNNEL_ORDER.get(r[0], 99))
        n_list = list(sorted_rows)
    except Exception as e:
        print("漏斗图数据库查询出错：", e)
        return "<p>价格段漏斗图数据加载失败</p>"

    c = (
        Funnel(init_opts=opts.InitOpts(width="100%", height="600px", bg_color="#f5f5f5"))
        .add(
            "狗狗数量",
            n_list,
            sort_="descending",
            gap=2,
            label_opts=opts.LabelOpts(
                is_show=True, position="inside", formatter="{b}: {c}", font_size=12, color="#fff", font_weight="bold"
            ),
            itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color="#fff"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="🐶 狗狗价格段漏斗图",
                subtitle="从低价到高价的价格分布展示",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_size=18, font_weight="bold", color="#333"),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="item",
                formatter="{b}: {c}只 ({d}%)",
                background_color="rgba(255, 255, 255, 0.9)",
                border_color="#667eea",
                border_width=1,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c.render_embed()


# ==================== 6. 世界地图（狗狗家乡）====================


def get_world_map():
    """世界地图 - 狗狗家乡分布"""
    from pyecharts.charts import Map

    data_list1 = []
    try:
        rows = (
            db.session.query(DogPrice.Origin_wool, func.count(DogPrice.Origin_wool))
            .filter(DogPrice.Origin_wool.isnot(None), DogPrice.Origin_wool != "")
            .group_by(DogPrice.Origin_wool)
            .order_by(func.count(DogPrice.Origin_wool).desc())
            .limit(20)
            .all()
        )

        for r in rows:
            cname = r[0].strip() if r[0] else ""
            ename = COUNTRY_MAP.get(cname, cname)
            data_list1.append((ename, r[1]))
    except Exception as e:
        print("世界地图数据库查询出错：", e)
        return "<p>世界地图数据加载失败</p>"

    if not data_list1:
        return "<p style='text-align:center;padding:40px;color:#999;'>暂无地图数据</p>"

    world_map = (
        Map()
        .add("", data_list1, "world")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="世界地图 - 狗狗家乡分布"),
            visualmap_opts=opts.VisualMapOpts(max_=100, min_=0, is_piecewise=True),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return world_map.render_embed()


# =====  狗粮统计函数  ========


def get_dog_food_stats():
    """从 dog_wykl 表获取狗粮统计数据"""
    try:
        total_brands = db.session.query(func.count(func.distinct(DogWykl.food_name))).scalar() or 0

        # Parse numeric prices in Python (handles mixed string format better than REGEXP)
        all_prices = db.session.query(DogWykl.price).filter(DogWykl.price.isnot(None)).all()
        numeric_prices = []
        for (p,) in all_prices:
            try:
                numeric_prices.append(float(p))
            except (ValueError, TypeError):
                pass
        avg_price = round(sum(numeric_prices) / len(numeric_prices), 2) if numeric_prices else 0

        top_origins = (
            db.session.query(DogWykl.origin, func.count(DogWykl.food_id))
            .filter(DogWykl.origin.isnot(None), DogWykl.origin != "")
            .group_by(DogWykl.origin)
            .order_by(func.count(DogWykl.food_id).desc())
            .limit(5)
            .all()
        )
        top_origins = [(r[0], r[1]) for r in top_origins]

        price_ranges = [
            (0, 50, "0-50 元"),
            (50, 100, "50-100 元"),
            (100, 200, "100-200 元"),
            (200, 500, "200-500 元"),
            (500, 10000, "500 元以上"),
        ]
        price_dist = []
        for low, high, label in price_ranges:
            count = 0
            for p in numeric_prices:
                if low < p <= high or (low == 0 and p == 0):
                    count += 1
            price_dist.append((label, count))

        return {
            "total_brands": total_brands,
            "avg_price": avg_price,
            "top_origins": top_origins,
            "price_dist": price_dist,
        }
    except Exception as e:
        print("获取狗粮数据出错：", e)
        return {"total_brands": 0, "avg_price": 0, "top_origins": [], "price_dist": []}


def get_dog_food_list(limit=100):
    """获取狗粮列表数据（用于前端表格展示）"""
    try:
        rows = (
            db.session.query(DogWykl.food_name, DogWykl.price, DogWykl.origin)
            .filter(DogWykl.food_name.isnot(None), DogWykl.food_name != "")
            .order_by(DogWykl.food_id)
            .limit(limit)
            .all()
        )

        food_list = []
        for row in rows:
            name = row[0] if row[0] else "-"
            price_val = "-"
            if row[1]:
                try:
                    price_val = float(row[1])
                except (ValueError, TypeError):
                    price_val = "-"
            origin = row[2] if row[2] else "-"
            food_list.append({"name": name, "price": price_val, "origin": origin})

        return food_list
    except Exception as e:
        print("获取狗粮列表出错：", e)
        return []


def get_breed_distribution():
    """获取狗狗品种分布数据"""
    try:
        rows = (
            db.session.query(JdDog.dog_name, func.count(JdDog.number))
            .filter(JdDog.dog_name.isnot(None), JdDog.dog_name != "")
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .all()
        )
        return [{"breed": r[0], "count": r[1]} for r in rows]
    except Exception as e:
        print("获取品种分布数据出错：", e)
        return []


# =====  执行所有原始统计查询，并将结果插入/更新到汇总表。========


def update_dashboard_summary():
    """计算并更新 dashboard_summary 表（可被定时任务调用）"""
    stats = get_dashboard_stats()

    summary = DashboardSummary.query.filter_by(id=1).first()
    if not summary:
        summary = DashboardSummary(id=1)
        db.session.add(summary)

    summary.total_dogs = stats["total_dogs"]
    summary.avg_price = stats["avg_price"]
    summary.total_shops = stats["total_shops"]
    summary.total_breeds = stats["total_breeds"]
    summary.top_breeds = stats["top_breeds"]
    summary.top_shops = stats["top_shops"]
    summary.price_dist = stats["price_dist"]
    summary.level_pet = stats["level_pet"]
    summary.level_blood = stats["level_blood"]

    db.session.commit()
    print("汇总表更新完成")


# ===== 图表数据提取 API（用于导出功能） =====


def get_price_scatter_data():
    """获取价格散点图数据（用于导出）"""
    try:
        rows = (
            db.session.query(JdDog.price, func.count(JdDog.price).label("count"))
            .group_by(JdDog.price)
            .order_by(JdDog.price)
            .all()
        )
        return [{"价格": row[0], "数量": row[1]} for row in rows]
    except Exception as e:
        print("获取价格散点图数据出错：", e)
        return []


def get_weight_line_data():
    """获取体重折线图数据（用于导出）"""
    try:
        weight_case = case(
            (JdDog.weight > 20, "20kg以上"),
            (JdDog.weight > 10, "10-20kg"),
            (JdDog.weight > 5, "5-10kg"),
            (JdDog.weight > 2, "2-5kg"),
            (JdDog.weight > 1, "1-2kg"),
            (JdDog.weight > 0, "0-1kg"),
            else_="其他",
        )
        rows = (
            db.session.query(weight_case.label("weight_bucket"), func.count(JdDog.number))
            .filter(JdDog.weight.isnot(None))
            .group_by("weight_bucket")
            .all()
        )
        bucket_order = {"0-1kg": 0, "1-2kg": 1, "2-5kg": 2, "5-10kg": 3, "10-20kg": 4, "20kg以上": 5}
        sorted_rows = sorted(rows, key=lambda r: bucket_order.get(r[0], 99))
        return [{"体重区间": r[0], "数量": r[1]} for r in sorted_rows]
    except Exception as e:
        print("获取体重折线图数据出错：", e)
        return []


def get_level_bar_data():
    """获取级别柱状图数据（用于导出）"""
    try:
        rows = (
            db.session.query(
                JdDog.dog_name,
                func.sum(case((JdDog.pet_level == "宠物级", 1), else_=0)).label("pet_level_count"),
                func.sum(case((JdDog.pet_level == "血统级", 1), else_=0)).label("blood_level_count"),
            )
            .filter(JdDog.dog_name.isnot(None), JdDog.pet_level.isnot(None))
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(20)
            .all()
        )
        return [{"品种": r[0], "宠物级": r[1] or 0, "血统级": r[2] or 0} for r in rows]
    except Exception as e:
        print("获取级别柱状图数据出错：", e)
        return []


def get_hist_data():
    """获取TOP10直方图数据（用于导出）"""
    try:
        breed_rows = (
            db.session.query(JdDog.dog_name, func.count(JdDog.number))
            .group_by(JdDog.dog_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(10)
            .all()
        )
        shop_rows = (
            db.session.query(JdDog.shop_name, func.count(JdDog.number))
            .group_by(JdDog.shop_name)
            .order_by(func.count(JdDog.number).desc())
            .limit(10)
            .all()
        )

        result = []
        for r in breed_rows:
            result.append({"类型": "品种", "名称": r[0] if r[0] else "-", "数量": r[1]})
        for r in shop_rows:
            result.append({"类型": "店铺", "名称": r[0] if r[0] else "-", "数量": r[1]})
        return result
    except Exception as e:
        print("获取TOP10直方图数据出错：", e)
        return []


def get_funnel_data():
    """获取价格漏斗图数据（用于导出）"""
    try:
        price_ranges = [
            (0, 2500, "0-2.5k"),
            (2500, 5000, "2.5k-5k"),
            (5000, 7500, "5k-7.5k"),
            (7500, 10000, "7.5k-1w"),
            (10000, 20000, "1w-2w"),
            (20000, 1000000, "2w以上"),
        ]
        result = []
        for low, high, label in price_ranges:
            count = (
                db.session.query(func.count(JdDog.number))
                .filter(JdDog.price > low, JdDog.price <= high)
                .scalar()
                or 0
            )
            result.append({"价格区间": label, "数量": count})
        return result
    except Exception as e:
        print("获取价格漏斗图数据出错：", e)
        return []


def get_map_data():
    """获取世界地图数据（用于导出）"""
    try:
        rows = (
            db.session.query(DogPrice.Origin_wool, func.count(DogPrice.Origin_wool))
            .filter(DogPrice.Origin_wool.isnot(None), DogPrice.Origin_wool != "")
            .group_by(DogPrice.Origin_wool)
            .order_by(func.count(DogPrice.Origin_wool).desc())
            .limit(20)
            .all()
        )

        result = []
        for r in rows:
            origin_cn = r[0].strip() if r[0] else ""
            origin_en = COUNTRY_MAP.get(origin_cn, origin_cn)
            result.append({"产地（中文）": origin_cn, "产地（英文）": origin_en, "数量": r[1]})
        return result
    except Exception as e:
        print("获取世界地图数据出错：", e)
        return []
