# charts.py
import os

import pymysql
from pyecharts.charts import Scatter, Line, Bar, Funnel, Map
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from translate import Translator  # 用于世界地图的中文翻译

# ==================== 数据库配置（请按实际情况修改）====================
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': os.getenv('DB_PASSWORD', '123456'),  # 从环境变量读取，如果没有则用默认值（仅开发）
#     'database': 'dog',
#     'charset': 'utf8mb4'
# }

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'dog'),
    'charset': 'utf8mb4'
}


# ==================== 首页看板数据函数 ====================
def get_dashboard_stats_from_summary():
    """从 dashboard_summary 表获取统计数据（速度快）"""
    import json
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        cur.execute("SELECT * FROM dashboard_summary WHERE id = 1")
        row = cur.fetchone()
        con.close()
        if row:
            # 将 JSON 字段解析回 Python 对象
            return {
                'total_dogs': row[1],
                'avg_price': row[2],
                'total_shops': row[3],
                'total_breeds': row[4],
                'top_breeds': json.loads(row[5]),
                'top_shops': json.loads(row[6]),
                'price_dist': json.loads(row[7]),
                'level_pet': row[8],
                'level_blood': row[9]
            }
        else:
            # 如果汇总表为空，回退到原始查询并初始化
            stats = get_dashboard_stats()
            update_dashboard_summary()  # 生成汇总数据
            return stats
    except Exception as e:
        print("从汇总表读取失败，回退到原始查询", e)
        return get_dashboard_stats()

def get_dashboard_stats():
    """获取首页看板的各项统计数据，返回字典"""
    stats = {}
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()

        # 1. 狗狗总数
        cur.execute("SELECT COUNT(*) FROM jd_dogs")
        stats['total_dogs'] = cur.fetchone()[0]

        # 2. 平均价格（保留两位小数）
        cur.execute("SELECT AVG(price) FROM jd_dogs")
        avg_price = cur.fetchone()[0]
        stats['avg_price'] = round(avg_price, 2) if avg_price else 0

        # 3. 店铺总数（去重）
        cur.execute("SELECT COUNT(DISTINCT shop_name) FROM jd_dogs")
        stats['total_shops'] = cur.fetchone()[0]

        # 4. 狗狗品种总数（去重）
        cur.execute("SELECT COUNT(DISTINCT dog_name) FROM jd_dogs")
        stats['total_breeds'] = cur.fetchone()[0]

        # 5. 热门狗狗品种 TOP 5
        cur.execute("""
            SELECT dog_name, COUNT(*) as cnt
            FROM jd_dogs
            GROUP BY dog_name
            ORDER BY cnt DESC
            LIMIT 5
        """)
        stats['top_breeds'] = cur.fetchall()  # 返回列表 [(name, count), ...]

        # 6. 热门店铺 TOP 5
        cur.execute("""
            SELECT shop_name, COUNT(*) as cnt
            FROM jd_dogs
            GROUP BY shop_name
            ORDER BY cnt DESC
            LIMIT 5
        """)
        stats['top_shops'] = cur.fetchall()

        # 7. 价格区间分布（用于迷你柱状图）
        price_ranges = [
            (0, 2500, '0-2.5k'),
            (2500, 5000, '2.5k-5k'),
            (5000, 7500, '5k-7.5k'),
            (7500, 10000, '7.5k-1w'),
            (10000, 20000, '1w-2w'),
            (20000, 1000000, '2w以上')
        ]
        price_dist = []
        for low, high, label in price_ranges:
            cur.execute("SELECT COUNT(*) FROM jd_dogs WHERE price > %s AND price <= %s", (low, high))
            count = cur.fetchone()[0]
            price_dist.append((label, count))
        stats['price_dist'] = price_dist

        # 8. 等级比例（宠物级/血统级）
        cur.execute("SELECT pet_level, COUNT(*) FROM jd_dogs GROUP BY pet_level")
        level_data = cur.fetchall()
        # 可能还有空值或其他等级，这里只取宠物级和血统级
        pet_count = 0
        blood_count = 0
        for level, cnt in level_data:
            if level == '宠物级':
                pet_count = cnt
            elif level == '血统级':
                blood_count = cnt
        stats['level_pet'] = pet_count
        stats['level_blood'] = blood_count

        con.close()
    except Exception as e:
        print("获取看板数据出错：", e)
        # 返回空数据避免前端报错
        stats = {
            'total_dogs': 0, 'avg_price': 0, 'total_shops': 0, 'total_breeds': 0,
            'top_breeds': [], 'top_shops': [], 'price_dist': [],
            'level_pet': 0, 'level_blood': 0
        }
    return stats


# ==================== 1. 价格散点图 ====================
def get_price_scatter():
    """狗狗价格散点图"""
    n_list = []
    n_list1 = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        sql = "select price, count(price) from jd_dogs GROUP BY price;"
        cur.execute(sql)
        price = cur.fetchall()
        for n in price:
            n_list.append(n[0])
            n_list1.append(n[1])
        con.close()
    except Exception as e:
        print("价格散点图数据库查询出错：", e)
        return "<p>价格散点图数据加载失败</p>"

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
            xaxis_opts=opts.AxisOpts(
                type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=False),
        )
    )
    return c.render_embed()


# ==================== 2. 体重折线图 ====================
def get_weight_line():
    """狗狗体重折线图"""
    n1 = []
    n2 = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        sql = """
            SELECT weight, count(*) AS 总计
            FROM
            (select case when 0 < weight and weight <= 1 then '0-1kg'
                         when 1 < weight and weight <= 2 then '1-2kg'
                         when 2 < weight and weight <= 5 then '2-5kg'
                         when 5 < weight and weight <= 10 then '5-10kg'
                         when 10 < weight and weight <= 20 then '10-20kg'
                         when weight > 20 then '20kg以上'
                     else '000'
                     end as weight
            FROM jd_dogs
            WHERE 1
            ) AS  weight_num
            GROUP BY weight
            ORDER BY weight;
        """
        cur.execute(sql)
        name = cur.fetchall()
        for n in name:
            n1.append(n[0])
            n2.append(n[1])
        con.close()
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


# ==================== 3. 级别柱状图 ====================
def get_level_bar():
    """级别柱状图（宠物级 vs 血统级）"""
    n_list = []
    n_list1 = []
    n_list2 = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        sql = """
            select dog_name, 
                   count(case when pet_level='宠物级' then 1 end) as 宠物级,
                   count(case when pet_level='血统级' then 1 end) as 血统级
            from jd_dogs 
            GROUP BY dog_name 
            ORDER BY count(*) DESC;
        """
        cur.execute(sql)
        name = cur.fetchall()
        for n in name:
            n_list.append(n[0])
            n_list1.append(n[1])
            n_list2.append(n[2])
        con.close()
    except Exception as e:
        print("级别柱状图数据库查询出错：", e)
        return "<p>级别柱状图数据加载失败</p>"

    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="500px", theme=ThemeType.LIGHT))
        .add_xaxis(n_list)
        .add_yaxis("宠物级", n_list1)
        .add_yaxis("血统级", n_list2)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
                axislabel_opts=opts.LabelOpts(rotate=-45)
            ),
            title_opts=opts.TitleOpts(title="血统占比")
        )
    )
    return bar.render_embed()


# ==================== 4. 狗狗+店铺TOP10直方图 ====================
def get_shop_top10_hist():
    """售卖前10种宠物狗 + 店铺售卖种类最多top-10直方图"""
    dog_list = []
    dog_list1 = []
    data_list = []
    data_list1 = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        # 狗狗品种 top10
        sql = """
            select dog_name, count(dog_name) from jd_dogs 
            GROUP BY dog_name
            order by count(dog_name) DESC LIMIT 10;
        """
        cur.execute(sql)
        dog = cur.fetchall()
        for n in dog:
            dog_list.append(n[0])
            dog_list1.append(n[1])

        # 店铺 top10
        sql2 = """
            select shop_name, count(shop_name) from jd_dogs 
            GROUP BY shop_name 
            order by count(shop_name) DESC LIMIT 10;
        """
        cur.execute(sql2)
        data = cur.fetchall()
        for n in data:
            data_list.append(n[0])
            data_list1.append(n[1])
        con.close()
    except Exception as e:
        print("直方图数据库查询出错：", e)
        return "<p>直方图数据加载失败</p>"

    # 合并 x 轴数据（狗狗品种 + 店铺名）
    x = dog_list + data_list
    dog_list1.reverse()  # 原代码中这样做了，保留
    y = dog_list1 + data_list1

    c = (
        Bar(init_opts=opts.InitOpts(width="1300px", height="500px", theme=ThemeType.LIGHT))
        .add_xaxis(x)
        .add_yaxis("top-10", y, category_gap=10, color='#d48265')
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
                axislabel_opts=opts.LabelOpts(rotate=-45)
            ),
            yaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            datazoom_opts=opts.DataZoomOpts(type_="inside"),
            title_opts=opts.TitleOpts(title="售卖前10种宠物狗+店铺售卖种类最多top-10直方图")
        )
    )
    return c.render_embed()


# ==================== 5. 价格段漏斗图 ====================
def get_price_funnel():
    """价格段漏斗图"""
    n_list = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        sql = """
            SELECT price, count(*) AS number 
            FROM
                (select case when 0 < price and price <= 2500 then '0-2.5k'
                             when 2500 < price and price <= 5000 then '2.5k-5k'
                             when 5000 < price and price <= 7500 then '5k-7.5k'
                             when 7500 < price and price <= 10000 then '7.5k-1w'
                             when 10000 < price and price <= 20000 then '1w-2w'
                             when price > 20000 then '2w以上'
                        else '000'
                        end as price
                FROM jd_dogs
                WHERE 1
                ) AS price_summaries
            GROUP BY price
            ORDER BY price;
        """
        cur.execute(sql)
        name = cur.fetchall()
        for n in name:
            n_list.append(n)
        con.close()
    except Exception as e:
        print("漏斗图数据库查询出错：", e)
        return "<p>价格段漏斗图数据加载失败</p>"

    c = (
        Funnel(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add(
            "价格段",
            n_list,
            sort_="ascending",
            label_opts=opts.LabelOpts(position="inside"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="宠物狗价格分布", pos_left='center'),
            legend_opts=opts.LegendOpts(pos_top='6%')
        )
    )
    return c.render_embed()


# ==================== 6. 世界地图（狗狗家乡）====================
def get_world_map():
    """世界地图 - 狗狗家乡分布"""
    data_list1 = []
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()
        # 注意：表名可能是 dog_price，原脚本中用的是 dog_price
        sql = """
        select Origin_wool as 家乡, count(Origin_wool) 
        from dog_price GROUP BY Origin_wool
        order by count(Origin_wool) desc LIMIT 20;
        """
        cur.execute(sql)
        data = cur.fetchall()
        for n in data:
            # 中文地名翻译为英文（原脚本逻辑）
            translator = Translator(from_lang="chinese", to_lang="english")
            translation = translator.translate(n[0])
            data_list1.append((translation, n[1]))
        con.close()
    except Exception as e:
        print("世界地图数据库查询或翻译出错：", e)
        return "<p>世界地图数据加载失败</p>"

    world_map = (
        Map()
        .add('', data_list1, 'world')
        .set_global_opts(
            title_opts=opts.TitleOpts(title='世界地图 - 狗狗家乡分布'),
            visualmap_opts=opts.VisualMapOpts(
                max_=100,
                min_=0,
                is_piecewise=True
            )
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return world_map.render_embed()

# =====  狗粮统计函数  ========
def get_dog_food_stats():
    """从 dog_wykl 表获取狗粮统计数据"""
    stats = {}
    try:
        con = pymysql.connect(**DB_CONFIG)
        cur = con.cursor()

        # 狗粮品牌总数（去重）
        cur.execute("SELECT COUNT(DISTINCT food_name) FROM dog_wykl")
        stats['total_brands'] = cur.fetchone()[0]

        # 平均价格（取 price 字段的平均值，注意字段类型）
        cur.execute("SELECT AVG(CAST(price AS DECIMAL(10,2))) FROM dog_wykl WHERE price REGEXP '^[0-9.]+$'")
        avg_price = cur.fetchone()[0]
        stats['avg_price'] = round(avg_price, 2) if avg_price else 0

        # 产地分布 TOP5
        cur.execute("""
            SELECT origin, COUNT(*) as cnt 
            FROM dog_wykl 
            WHERE origin IS NOT NULL AND origin != ''
            GROUP BY origin 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        stats['top_origins'] = cur.fetchall()

        # 价格区间分布（自定义区间）
        price_ranges = [
            (0, 50, '0-50元'),
            (50, 100, '50-100元'),
            (100, 200, '100-200元'),
            (200, 500, '200-500元'),
            (500, 10000, '500元以上')
        ]
        price_dist = []
        for low, high, label in price_ranges:
            cur.execute("""
                SELECT COUNT(*) FROM dog_wykl 
                WHERE CAST(price AS DECIMAL(10,2)) BETWEEN %s AND %s
            """, (low, high))
            count = cur.fetchone()[0]
            price_dist.append((label, count))
        stats['price_dist'] = price_dist

        con.close()
    except Exception as e:
        print("获取狗粮数据出错：", e)
        stats = {
            'total_brands': 0,
            'avg_price': 0,
            'top_origins': [],
            'price_dist': []
        }
    return stats

# =====  执行所有原始统计查询，并将结果插入/更新到汇总表。========
def update_dashboard_summary():
    """计算并更新 dashboard_summary 表（可被定时任务调用）"""
    import json
    stats = get_dashboard_stats()  # 复用你现有的统计函数（它返回字典）

    # 将需要存储的字段转换为 JSON
    top_breeds_json = json.dumps(stats['top_breeds'], ensure_ascii=False)
    top_shops_json = json.dumps(stats['top_shops'], ensure_ascii=False)
    price_dist_json = json.dumps(stats['price_dist'], ensure_ascii=False)

    # 连接数据库，执行 REPLACE INTO 或 INSERT ... ON DUPLICATE KEY UPDATE
    con = pymysql.connect(**DB_CONFIG)
    cur = con.cursor()
    sql = """
        REPLACE INTO dashboard_summary 
        (id, total_dogs, avg_price, total_shops, total_breeds, 
         top_breeds, top_shops, price_dist, level_pet, level_blood)
        VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (
        stats['total_dogs'],
        stats['avg_price'],
        stats['total_shops'],
        stats['total_breeds'],
        top_breeds_json,
        top_shops_json,
        price_dist_json,
        stats['level_pet'],
        stats['level_blood']
    ))
    con.commit()
    cur.close()
    con.close()
    print("汇总表更新完成")

if __name__ == '__main__':
    # 测试地图生成
    html = get_world_map()
    with open('test_map.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("测试地图已保存为 test_map.html")