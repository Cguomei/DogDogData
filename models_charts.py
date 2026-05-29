"""SQLAlchemy models for the legacy data tables used by charts.py.

These tables (jd_dogs, dog_price, dog_wykl, dashboard_summary) were previously
only accessed via raw PyMySQL queries. This module provides ORM models so that
charts.py can use SQLAlchemy consistently with the rest of the application.
"""

from models import db


class JdDog(db.Model):
    __tablename__ = "jd_dogs"

    number = db.Column(db.BigInteger, primary_key=True)
    link = db.Column(db.Text)
    price = db.Column(db.Float)
    shop_name = db.Column(db.String(55))
    dog_name = db.Column(db.String(25))
    pet_level = db.Column(db.String(50))
    size = db.Column(db.String(25))
    weight = db.Column(db.Float)
    hair_length = db.Column(db.String(50))
    pet_age = db.Column(db.String(50))
    crawl_time = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


class DogPrice(db.Model):
    __tablename__ = "dog_price"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    links = db.Column(db.String(255))
    img_src = db.Column(db.String(255))
    dog_name = db.Column(db.String(50))
    price = db.Column(db.String(50))
    Hairy = db.Column(db.String(50))
    height = db.Column(db.String(50))
    Origin_wool = db.Column(db.String(50))
    dog_function = db.Column(db.String(50))


class DogWykl(db.Model):
    __tablename__ = "dog_wykl"

    food_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text)
    img_src = db.Column(db.Text)
    food_name = db.Column(db.String(255))
    discount_price = db.Column(db.String(50))
    price = db.Column(db.String(50))
    origin = db.Column(db.String(50))


class DashboardSummary(db.Model):
    __tablename__ = "dashboard_summary"

    id = db.Column(db.Integer, primary_key=True, default=1)
    total_dogs = db.Column(db.Integer, nullable=False, default=0)
    avg_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_shops = db.Column(db.Integer, nullable=False, default=0)
    total_breeds = db.Column(db.Integer, nullable=False, default=0)
    top_breeds = db.Column(db.JSON, nullable=True)
    top_shops = db.Column(db.JSON, nullable=True)
    price_dist = db.Column(db.JSON, nullable=True)
    level_pet = db.Column(db.Integer, nullable=True, default=0)
    level_blood = db.Column(db.Integer, nullable=True, default=0)
