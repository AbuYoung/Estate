from datetime import datetime
import pytz
from app import db
from app.models import Property

class StatisticsService:
    @staticmethod
    def get_default_date_range():
        """获取默认的统计时间范围"""
        return (
            datetime(2024, 1, 1, tzinfo=pytz.timezone('Asia/Shanghai')),
            datetime(2024, 10, 31, 23, 59, 59, tzinfo=pytz.timezone('Asia/Shanghai'))
        )

    @staticmethod
    def parse_date(date_str):
        """解析日期字符串为datetime对象"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            return date.replace(tzinfo=pytz.timezone('Asia/Shanghai'))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_statistics(start_date=None, end_date=None):
        """获取指定时间范围的统计数据"""
        if not start_date or not end_date:
            start_date, end_date = StatisticsService.get_default_date_range()
        
        # 确保end_date包含当天的最后一秒
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # 查询总数量
        total_count = Property.query.filter(
            Property.first_cert_date.between(start_date, end_date)
        ).count()
        
        # 查询总面积
        total_area_result = db.session.query(
            db.func.sum(Property.house_area)
        ).filter(
            Property.first_cert_date.between(start_date, end_date)
        ).first()
        
        # 查询月度统计
        monthly_stats = db.session.query(
            db.func.strftime('%Y-%m', Property.first_cert_date).label('month'),
            db.func.count(Property.id).label('count'),
            db.func.sum(Property.house_area).label('area')
        ).filter(
            Property.first_cert_date.between(start_date, end_date)
        ).group_by(
            db.func.strftime('%Y-%m', Property.first_cert_date)
        ).order_by(
            db.func.strftime('%Y-%m', Property.first_cert_date)
        ).all()
        
        months = []
        counts = []
        areas = []
        for stat in monthly_stats:
            months.append(stat.month)
            counts.append(stat.count)
            areas.append(round(stat.area or 0, 2))
            
        return {
            'total_count': total_count,
            'total_area': round(total_area_result[0] or 0, 2),
            'months': months,
            'counts': counts,
            'areas': areas,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }