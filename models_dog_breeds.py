"""
狗狗品种数据模型
用于存储从公开数据源获取的狗狗品种信息
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class DogBreedInfo(db.Model):
    """狗狗品种信息表 - 存储品种的基本信息"""

    __tablename__ = "dog_breed_info"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 基本信息
    breed_name = db.Column(
        db.String(100), nullable=False, index=True, comment="品种名称"
    )
    aliases = db.Column(db.String(500), comment="别名，逗号分隔")
    english_name = db.Column(db.String(100), comment="英文名称")

    # 物理特征
    size_category = db.Column(
        db.Enum("小型", "中型", "大型", "超大型"), comment="体型分类"
    )
    avg_weight_min = db.Column(db.Numeric(5, 2), comment="平均体重最小值(kg)")
    avg_weight_max = db.Column(db.Numeric(5, 2), comment="平均体重最大值(kg)")
    avg_height_min = db.Column(db.Numeric(5, 2), comment="平均肩高最小值(cm)")
    avg_height_max = db.Column(db.Numeric(5, 2), comment="平均肩高最大值(cm)")

    # 寿命和原产地
    lifespan_min = db.Column(db.Integer, comment="寿命最小值(年)")
    lifespan_max = db.Column(db.Integer, comment="寿命最大值(年)")
    origin_country = db.Column(db.String(100), comment="原产地")

    # 性格特征
    characteristics = db.Column(db.Text, comment="性格特征，逗号分隔")
    temperament = db.Column(db.Text, comment="气质描述")

    # 价格信息（市场参考价）
    price_min = db.Column(db.Numeric(10, 2), comment="价格最小值(元)")
    price_max = db.Column(db.Numeric(10, 2), comment="价格最大值(元)")
    price_avg = db.Column(db.Numeric(10, 2), comment="平均价格(元)")

    # 热度指标
    popularity_score = db.Column(db.Integer, default=0, comment="热度评分(0-100)")

    # 养护难度
    care_difficulty = db.Column(
        db.Enum("简单", "中等", "困难"), default="中等", comment="养护难度"
    )
    exercise_need = db.Column(
        db.Enum("低", "中", "高"), default="中", comment="运动需求"
    )
    grooming_need = db.Column(
        db.Enum("低", "中", "高"), default="中", comment="美容需求"
    )

    # 适用场景
    suitable_for = db.Column(db.String(500), comment="适用场景，逗号分隔")

    # 数据来源
    data_source = db.Column(
        db.String(100), default="public_database", comment="数据来源"
    )
    source_url = db.Column(db.String(500), comment="来源URL")

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
    crawl_time = db.Column(db.DateTime, default=datetime.now, comment="爬取时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "breed_name": self.breed_name,
            "aliases": self.aliases,
            "english_name": self.english_name,
            "size_category": self.size_category,
            "avg_weight": (
                f"{self.avg_weight_min}-{self.avg_weight_max}kg"
                if self.avg_weight_min
                else None
            ),
            "avg_height": (
                f"{self.avg_height_min}-{self.avg_height_max}cm"
                if self.avg_height_min
                else None
            ),
            "lifespan": (
                f"{self.lifespan_min}-{self.lifespan_max}年"
                if self.lifespan_min
                else None
            ),
            "origin_country": self.origin_country,
            "characteristics": self.characteristics,
            "price_range": (
                f"¥{self.price_min}-¥{self.price_max}" if self.price_min else None
            ),
            "price_avg": float(self.price_avg) if self.price_avg else None,
            "popularity_score": self.popularity_score,
            "care_difficulty": self.care_difficulty,
            "exercise_need": self.exercise_need,
            "grooming_need": self.grooming_need,
            "suitable_for": self.suitable_for,
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DogBreedPrice(db.Model):
    """狗狗品种价格记录表 - 存储不同渠道的价格数据"""

    __tablename__ = "dog_breed_price"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 关联品种
    breed_id = db.Column(
        db.Integer, db.ForeignKey("dog_breed_info.id"), nullable=False, index=True
    )
    breed_name = db.Column(
        db.String(100),
        nullable=False,
        index=True,
        comment="品种名称（冗余字段，便于查询）",
    )

    # 价格信息
    price = db.Column(db.Numeric(10, 2), nullable=False, comment="价格(元)")
    channel = db.Column(db.String(100), comment="销售渠道（如：专业犬舍、宠物店等）")
    location = db.Column(db.String(100), comment="地区")

    # 附加信息
    quality_level = db.Column(
        db.Enum("宠物级", "繁育级", "赛级"), default="宠物级", comment="品质等级"
    )
    age_months = db.Column(db.Integer, comment="年龄(月)")
    gender = db.Column(db.Enum("公", "母", "未知"), default="未知", comment="性别")

    # 热度/销量指标
    sales_count = db.Column(db.Integer, default=0, comment="销量/关注度")
    rating = db.Column(db.Numeric(3, 2), comment="评分(0-5)")

    # 数据来源
    data_source = db.Column(db.String(100), comment="数据来源")
    source_url = db.Column(db.String(500), comment="来源URL")

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    crawl_time = db.Column(db.DateTime, default=datetime.now, comment="爬取时间")

    # 关系
    breed = db.relationship(
        "DogBreedInfo", backref=db.backref("prices", lazy="dynamic")
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "breed_id": self.breed_id,
            "breed_name": self.breed_name,
            "price": float(self.price),
            "channel": self.channel,
            "location": self.location,
            "quality_level": self.quality_level,
            "age_months": self.age_months,
            "gender": self.gender,
            "sales_count": self.sales_count,
            "rating": float(self.rating) if self.rating else None,
            "data_source": self.data_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DogBreedStatistics(db.Model):
    """狗狗品种统计表 - 存储品种的统计数据"""

    __tablename__ = "dog_breed_statistics"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 关联品种
    breed_id = db.Column(
        db.Integer,
        db.ForeignKey("dog_breed_info.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    breed_name = db.Column(
        db.String(100), nullable=False, unique=True, index=True, comment="品种名称"
    )

    # 统计数据
    total_records = db.Column(db.Integer, default=0, comment="总记录数")
    avg_price = db.Column(db.Numeric(10, 2), comment="平均价格")
    min_price = db.Column(db.Numeric(10, 2), comment="最低价格")
    max_price = db.Column(db.Numeric(10, 2), comment="最高价格")
    price_std = db.Column(db.Numeric(10, 2), comment="价格标准差")

    # 渠道统计
    channel_count = db.Column(db.Integer, default=0, comment="渠道数量")
    location_count = db.Column(db.Integer, default=0, comment="地区数量")

    # 时间统计
    last_update = db.Column(db.DateTime, comment="最后更新时间")
    data_freshness_hours = db.Column(db.Integer, comment="数据新鲜度(小时)")

    # 趋势数据
    price_trend = db.Column(
        db.Enum("上涨", "下跌", "稳定"), default="稳定", comment="价格趋势"
    )
    popularity_trend = db.Column(
        db.Enum("上升", "下降", "稳定"), default="稳定", comment="热度趋势"
    )

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    breed = db.relationship(
        "DogBreedInfo", backref=db.backref("statistics", uselist=False)
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "breed_id": self.breed_id,
            "breed_name": self.breed_name,
            "total_records": self.total_records,
            "avg_price": float(self.avg_price) if self.avg_price else None,
            "min_price": float(self.min_price) if self.min_price else None,
            "max_price": float(self.max_price) if self.max_price else None,
            "channel_count": self.channel_count,
            "location_count": self.location_count,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "data_freshness_hours": self.data_freshness_hours,
            "price_trend": self.price_trend,
            "popularity_trend": self.popularity_trend,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
