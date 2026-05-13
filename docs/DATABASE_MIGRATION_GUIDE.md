# 狗狗品种数据库迁移指南

## 📋 概述

本次更新将数据库从简单的 `jd_dogs` 表升级为更专业的三表结构，更好地适配公开数据源的特点。

## 🔄 数据库结构对比

### 旧结构（jd_dogs）
```sql
- dog_name (品种名称)
- price (价格)
- shop_name (店铺名称)
- comment_count (评论数)
- size (体型)
- crawl_time (爬取时间)
```

**问题：**
- ❌ 字段语义不清晰（shop_name用于公开数据不合适）
- ❌ 缺少品种详细信息
- ❌ 价格单一，无法记录价格区间
- ❌ 没有数据来源标识

### 新结构（三表设计）

#### 1. dog_breed_info（品种信息表）
存储品种的基本信息和特征：
- 基本信息：品种名、别名、英文名
- 物理特征：体型、体重、身高
- 寿命和原产地
- 性格特征
- 价格区间（市场参考价）
- 热度评分
- 养护难度、运动需求、美容需求
- 适用场景

#### 2. dog_breed_price（价格记录表）
存储不同渠道的价格数据：
- 关联品种（breed_id）
- 价格、渠道、地区
- 品质等级（宠物级/繁育级/赛级）
- 年龄、性别
- 销量/关注度、评分
- 数据来源

#### 3. dog_breed_statistics（统计表）
存储品种的统计数据：
- 总记录数、平均/最低/最高价格
- 渠道数量、地区数量
- 数据新鲜度
- 价格趋势、热度趋势

## 🚀 迁移步骤

### 步骤1：执行数据库迁移脚本

```bash
cd D:\PycharmProjects\fastApiProject
python scripts/migrate_dog_breed_db.py
```

脚本会自动：
1. ✅ 创建三个新表
2. ✅ 迁移旧表数据（如果存在）
3. ✅ 验证表结构

### 步骤2：验证迁移结果

```python
from app import create_app
from models_dog_breeds import DogBreedInfo, DogBreedPrice, DogBreedStatistics

app = create_app()
with app.app_context():
    # 检查表是否存在
    print(f"品种数量: {DogBreedInfo.query.count()}")
    print(f"价格记录: {DogBreedPrice.query.count()}")
    print(f"统计记录: {DogBreedStatistics.query.count()}")
```

### 步骤3：测试爬虫功能

```bash
python scripts/tools/public_dog_crawler.py
```

## 💡 使用示例

### 查询品种信息

```python
from models_dog_breeds import DogBreedInfo, DogBreedPrice

# 获取金毛的详细信息
breed = DogBreedInfo.query.filter_by(breed_name='金毛寻回犬').first()
print(breed.to_dict())

# 获取金毛的所有价格记录
prices = DogBreedPrice.query.filter_by(breed_name='金毛寻回犬').all()
for price in prices:
    print(f"{price.channel}: ¥{price.price}")
```

### 获取统计数据

```python
from models_dog_breeds import DogBreedStatistics

# 获取所有品种的统计
stats = DogBreedStatistics.query.all()
for stat in stats:
    print(f"{stat.breed_name}: 均价¥{stat.avg_price}, "
          f"渠道数{stat.channel_count}")
```

### API调用

```bash
# 获取爬虫统计
curl http://localhost:5000/api/crawler/stats

# 检查数据新鲜度
curl http://localhost:5000/api/data/freshness

# 获取品种新鲜度
curl http://localhost:5000/api/data/breed-freshness
```

## 📊 优势对比

| 特性 | 旧结构 | 新结构 |
|------|--------|--------|
| 品种信息完整性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 价格数据丰富度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 数据统计能力 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 扩展性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 查询性能 | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🔧 常见问题

### Q1: 旧表jd_dogs还需要吗？

A: 迁移完成后，如果确认数据已正确迁移，可以删除旧表：
```sql
DROP TABLE jd_dogs;
```

### Q2: 如何回滚迁移？

A: 如果需要回滚，可以删除新表并恢复旧表：
```sql
DROP TABLE dog_breed_statistics;
DROP TABLE dog_breed_price;
DROP TABLE dog_breed_info;
```

### Q3: 统计数据多久更新一次？

A: 每次爬取后会自动更新统计数据。也可以手动触发更新。

### Q4: 如何添加新品种？

A: 通过爬虫自动添加，或手动插入：
```python
breed = DogBreedInfo(
    breed_name='新品种',
    size_category='中型',
    origin_country='中国',
    popularity_score=50
)
db.session.add(breed)
db.session.commit()
```

## 📝 注意事项

1. **备份数据**：迁移前请备份数据库
2. **测试环境**：建议先在测试环境验证
3. **依赖导入**：确保导入了 `models_dog_breeds` 模块
4. **API兼容**：大部分API已自动适配新结构

## 🎯 后续优化建议

1. 添加品种图片URL字段
2. 实现价格趋势分析
3. 添加用户收藏功能
4. 实现智能推荐算法

---

**迁移完成时间**: 2026-05-12  
**版本**: v2.0  
**维护者**: AI Assistant
