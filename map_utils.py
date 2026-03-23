# # map_utils.py
# import pymysql
# from pyecharts.charts import Map
# from pyecharts import options as opts
# from translate import Translator
#
# def get_world_map():
#     """从数据库获取数据并生成世界地图，返回 HTML 字符串"""
#     data_list1 = []
#     try:
#         # 连接数据库（建议将数据库配置放在外面，这里简化）
#         con = pymysql.connect("localhost", "root", "123456", "dog")
#         cur = con.cursor()
#         sql = """
#         select Origin_wool as 家乡, count(Origin_wool)
#         from dog_price GROUP BY Origin_wool
#         order by count(Origin_wool) desc LIMIT 20;
#         """
#         cur.execute(sql)
#         data = cur.fetchall()
#         for n in data:
#             translator = Translator(from_lang="chinese", to_lang="english")
#             translation = translator.translate(n[0])
#             data_list1.append((translation, n[1]))
#         con.close()
#     except Exception as e:
#         print("数据库查询出错：", e)
#         return "<p>数据加载失败</p>"
#
#     # 生成地图
#     world_map = (
#         Map()
#         .add('', data_list1, 'world')
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title='世界地图 - 狗狗家乡分布'),
#             visualmap_opts=opts.VisualMapOpts(
#                 max_=100,
#                 min_=0,
#                 is_piecewise=True
#             )
#         )
#         .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     )
#     # 返回完整的 HTML 页面
#     return world_map.render_embed()
#
#
# """
# 有多个类似的图表代码,在 map_utils.py 中定义多个函数，例如：
#
# get_world_map()
# get_china_map()
# get_bar_chart()
#
# 然后在 app.py 中为每个图表创建单独的路由：
#
# python
# @app.route('/map/world')
# def world_map():
#     return get_world_map()
#
# @app.route('/map/china')
# def china_map():
#     return get_china_map()
# """