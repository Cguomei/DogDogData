"""
时区管理工具
提供时区检测、转换和格式化功能
"""

from datetime import datetime
import pytz
from flask import request, session


def get_user_timezone():
    """
    获取用户时区

    优先级:
    1. Session 中保存的时区
    2. Cookie 中的时区
    3. 请求头中的时区
    4. 默认时区 (Asia/Shanghai)

    Returns:
        str: 时区名称，如 'Asia/Shanghai'
    """
    # 1. 从 Session 获取
    tz = session.get("timezone")
    if tz and tz in pytz.all_timezones:
        return tz

    # 2. 从 Cookie 获取
    tz = request.cookies.get("timezone")
    if tz and tz in pytz.all_timezones:
        return tz

    # 3. 从请求头获取（浏览器通常会发送）
    # 注意：HTTP 标准中没有直接的时区头，需要前端 JS 检测后发送

    # 4. 返回默认时区
    return "Asia/Shanghai"


def convert_to_user_timezone(dt, user_tz=None):
    """
    将 UTC 时间转换为用户时区时间

    Args:
        dt: datetime 对象（应该是 UTC 时间）
        user_tz: 用户时区字符串，如果为 None 则自动检测

    Returns:
        datetime: 转换后的本地时间
    """
    if user_tz is None:
        user_tz = get_user_timezone()

    # 确保输入是 UTC 时间
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    # 转换到用户时区
    user_timezone = pytz.timezone(user_tz)
    return dt.astimezone(user_timezone)


def format_datetime_for_user(dt, format="medium", user_tz=None):
    """
    格式化时间为用户时区

    Args:
        dt: datetime 对象
        format: 格式类型 ('short', 'medium', 'long', 'full', 或自定义格式字符串)
        user_tz: 用户时区

    Returns:
        str: 格式化后的时间字符串
    """
    # 转换时区
    local_dt = convert_to_user_timezone(dt, user_tz)

    # 格式化
    if format == "short":
        return local_dt.strftime("%m-%d %H:%M")
    elif format == "medium":
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format == "long":
        return local_dt.strftime("%Y年%m月%d日 %H:%M:%S")
    elif format == "date_only":
        return local_dt.strftime("%Y-%m-%d")
    elif format == "time_only":
        return local_dt.strftime("%H:%M:%S")
    else:
        # 自定义格式
        return local_dt.strftime(format)


def get_timezone_offset(tz_name):
    """
    获取时区相对于 UTC 的偏移量

    Args:
        tz_name: 时区名称

    Returns:
        str: 偏移量字符串，如 '+08:00'
    """
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    offset = now.utcoffset()

    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60

    sign = "+" if total_seconds >= 0 else "-"
    return f"{sign}{hours:02d}:{minutes:02d}"


def get_common_timezones():
    """
    获取常用时区列表

    Returns:
        list: 时区字典列表 [{'name': 'Asia/Shanghai', 'label': '中国标准时间 (UTC+8)'}]
    """
    common_tzs = [
        ("UTC", "协调世界时 (UTC+0)"),
        ("Asia/Shanghai", "中国标准时间 (UTC+8)"),
        ("Asia/Tokyo", "日本标准时间 (UTC+9)"),
        ("Asia/Seoul", "韩国标准时间 (UTC+9)"),
        ("Asia/Hong_Kong", "香港时间 (UTC+8)"),
        ("Asia/Taipei", "台北时间 (UTC+8)"),
        ("Asia/Singapore", "新加坡时间 (UTC+8)"),
        ("America/New_York", "美国东部时间 (UTC-5)"),
        ("America/Los_Angeles", "美国太平洋时间 (UTC-8)"),
        ("Europe/London", "英国时间 (UTC+0)"),
        ("Europe/Paris", "中欧时间 (UTC+1)"),
        ("Australia/Sydney", "澳大利亚东部时间 (UTC+10)"),
    ]

    return [{"name": name, "label": label} for name, label in common_tzs]


# Flask-Babel 时区选择器
def get_timezone():
    """
    Flask-Babel 时区选择器

    Returns:
        pytz.timezone: 用户时区对象
    """
    tz_name = get_user_timezone()
    return pytz.timezone(tz_name)
