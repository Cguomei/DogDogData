"""
数据新鲜度检查与自动更新系统
确保狗狗价格数据保持最新状态
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import text, func
from models_extended import db

logger = logging.getLogger(__name__)


class DataFreshnessChecker:
    """数据新鲜度检查器"""

    def __init__(self):
        self.freshness_threshold_hours = 24  # 默认24小时为新鲜
        self.warning_threshold_hours = 48  # 48小时发出警告
        self.critical_threshold_hours = 72  # 72小时为严重过期

    def check_data_freshness(self) -> dict:
        """
        检查数据新鲜度（使用新表结构）

        Returns:
            新鲜度检查结果
        """
        try:
            from models_dog_breeds import DogBreedPrice

            # 查询最后更新时间
            last_crawl = db.session.query(func.max(DogBreedPrice.crawl_time)).scalar()
            total_count = DogBreedPrice.query.count()

            if total_count == 0:
                return {
                    "status": "no_data",
                    "message": "数据库中没有数据",
                    "recommendation": "立即执行数据爬取",
                }

            hours_since_last_crawl = (
                (datetime.now() - last_crawl).total_seconds() / 3600
                if last_crawl
                else 999
            )

            # 计算各状态的记录数
            fresh_threshold = datetime.now() - timedelta(
                hours=self.freshness_threshold_hours
            )
            warning_threshold = datetime.now() - timedelta(
                hours=self.warning_threshold_hours
            )

            fresh_count = DogBreedPrice.query.filter(
                DogBreedPrice.crawl_time >= fresh_threshold
            ).count()

            warning_count = DogBreedPrice.query.filter(
                (DogBreedPrice.crawl_time < fresh_threshold)
                & (DogBreedPrice.crawl_time >= warning_threshold)
            ).count()

            stale_count = DogBreedPrice.query.filter(
                DogBreedPrice.crawl_time < warning_threshold
            ).count()

            # 判断状态
            if hours_since_last_crawl <= self.freshness_threshold_hours:
                status = "fresh"
                message = f"数据新鲜（{hours_since_last_crawl:.1f}小时前更新）"
            elif hours_since_last_crawl <= self.warning_threshold_hours:
                status = "warning"
                message = f"数据即将过期（{hours_since_last_crawl:.1f}小时前更新）"
            elif hours_since_last_crawl <= self.critical_threshold_hours:
                status = "stale"
                message = f"数据已过期（{hours_since_last_crawl:.1f}小时前更新）"
            else:
                status = "critical"
                message = f"数据严重过期（{hours_since_last_crawl:.1f}小时前更新）"

            # 计算新鲜度百分比
            freshness_ratio = fresh_count / total_count * 100 if total_count > 0 else 0

            return {
                "status": status,
                "message": message,
                "last_crawl_time": last_crawl.isoformat() if last_crawl else None,
                "hours_since_update": round(hours_since_last_crawl, 1),
                "total_records": total_count,
                "fresh_records": fresh_count,
                "warning_records": warning_count,
                "stale_records": stale_count,
                "freshness_percentage": round(freshness_ratio, 1),
                "recommendation": self._get_recommendation(
                    status, hours_since_last_crawl
                ),
            }

        except Exception as e:
            logger.error(f"检查数据新鲜度失败: {str(e)}")
            return {
                "status": "error",
                "message": f"检查失败: {str(e)}",
                "recommendation": "检查数据库连接",
            }

    def _get_recommendation(self, status: str, hours: float) -> str:
        """根据状态获取建议"""
        recommendations = {
            "fresh": "数据状态良好，无需操作",
            "warning": "建议在24小时内更新数据",
            "stale": "建议立即更新数据",
            "critical": "数据严重过期，请立即更新！",
            "no_data": "数据库中无数据，请执行首次爬取",
            "error": "检查数据库连接和配置",
        }
        return recommendations.get(status, "未知状态")

    def get_breed_freshness(self) -> list:
        """
        获取各品种的数据新鲜度（使用新表结构）

        Returns:
            各品种新鲜度列表
        """
        try:
            from models_dog_breeds import DogBreedPrice, DogBreedInfo

            # 按品种分组查询
            results = (
                db.session.query(
                    DogBreedPrice.breed_name,
                    func.count(DogBreedPrice.id).label("count"),
                    func.max(DogBreedPrice.crawl_time).label("last_crawl"),
                    func.avg(DogBreedPrice.price).label("avg_price"),
                )
                .group_by(DogBreedPrice.breed_name)
                .order_by(func.max(DogBreedPrice.crawl_time).asc())
                .limit(20)
                .all()
            )

            breeds = []
            for row in results:
                hours_ago = (
                    (datetime.now() - row.last_crawl).total_seconds() / 3600
                    if row.last_crawl
                    else 999
                )

                if hours_ago <= 24:
                    status = "fresh"
                elif hours_ago <= 48:
                    status = "warning"
                elif hours_ago <= 72:
                    status = "stale"
                else:
                    status = "critical"

                breeds.append(
                    {
                        "breed": row.breed_name,
                        "count": row.count,
                        "avg_price": float(row.avg_price or 0),
                        "last_crawl": (
                            row.last_crawl.isoformat() if row.last_crawl else None
                        ),
                        "hours_ago": round(hours_ago, 1),
                        "status": status,
                    }
                )

            return breeds

        except Exception as e:
            logger.error(f"获取品种新鲜度失败: {str(e)}")
            return []

    def clean_old_data(self, days: int = 90) -> int:
        """
        清理旧数据（使用新表结构）

        Args:
            days: 保留天数

        Returns:
            删除的记录数
        """
        try:
            from models_dog_breeds import DogBreedPrice

            cutoff_date = datetime.now() - timedelta(days=days)

            deleted_count = DogBreedPrice.query.filter(
                DogBreedPrice.crawl_time < cutoff_date
            ).delete()

            db.session.commit()

            logger.info(f"清理了 {deleted_count} 条{days}天前的旧数据")

            return deleted_count

        except Exception as e:
            logger.error(f"清理旧数据失败: {str(e)}")
            db.session.rollback()
            return 0


class AutoUpdateScheduler:
    """自动更新调度器"""

    def __init__(self):
        self.checker = DataFreshnessChecker()

    def should_auto_update(self) -> bool:
        """
        判断是否应该自动更新

        Returns:
            True表示需要更新
        """
        freshness = self.checker.check_data_freshness()

        # 如果数据过期或没有数据，需要更新
        if freshness["status"] in ["stale", "critical", "no_data"]:
            return True

        # 如果新鲜度低于50%，也需要更新
        if freshness.get("freshness_percentage", 100) < 50:
            return True

        return False

    def get_update_priority(self) -> dict:
        """
        获取更新优先级

        Returns:
            优先级信息
        """
        freshness = self.checker.check_data_freshness()

        priority_map = {
            "critical": {"level": "high", "urgency": "immediate"},
            "stale": {"level": "medium", "urgency": "soon"},
            "warning": {"level": "low", "urgency": "scheduled"},
            "fresh": {"level": "none", "urgency": "not_needed"},
            "no_data": {"level": "high", "urgency": "immediate"},
        }

        return {
            "priority": priority_map.get(freshness["status"], {"level": "unknown"}),
            "freshness": freshness,
            "should_update": self.should_auto_update(),
        }


# 全局实例
freshness_checker = DataFreshnessChecker()
auto_scheduler = AutoUpdateScheduler()
