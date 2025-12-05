"""健康记录相关的Repository类"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, extract
import uuid

from repositories.base import BaseRepository
from database.models import HealthRecord, Alert


class HealthRepository(BaseRepository[HealthRecord]):
    """健康记录数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, HealthRecord)
    
    def add_health_record(self, elderly_id: uuid.UUID, data_type: str, 
                         value: float, record_time: Optional[datetime] = None) -> HealthRecord:
        """添加健康记录"""
        try:
            # 检查是否有相同类型的最新记录
            latest_record = self.get_latest_record(elderly_id, data_type)
            
            # 确定健康记录是否正常
            is_normal = self._check_health_normal(data_type, value)
            
            # 创建健康记录
            health_record = HealthRecord(
                elderly_id=elderly_id,
                data_type=data_type,
                value=value,
                record_time=record_time or datetime.now(),
                is_normal=is_normal
            )
            
            self.db.add(health_record)
            self.db.commit()
            self.db.refresh(health_record)
            
            # 如果异常，创建告警
            if not is_normal:
                self._create_health_alert(elderly_id, data_type, value, health_record.record_time)
            
            return health_record
        
        except Exception as e:
            self.db.rollback()
            print(f"Error adding health record: {e}")
            raise
    
    def get_latest_record(self, elderly_id: uuid.UUID, data_type: str) -> Optional[HealthRecord]:
        """获取指定类型的最新健康记录"""
        try:
            return self.db.query(HealthRecord).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.data_type == data_type
            ).order_by(desc(HealthRecord.record_time)).first()
        
        except Exception as e:
            print(f"Error getting latest record: {e}")
            return None
    
    def get_latest_records_by_types(self, elderly_id: uuid.UUID, 
                                  data_types: List[str]) -> Dict[str, Optional[HealthRecord]]:
        """获取多种类型的最新健康记录"""
        result = {}
        
        try:
            for data_type in data_types:
                record = self.get_latest_record(elderly_id, data_type)
                result[data_type] = record
            
            return result
        
        except Exception as e:
            print(f"Error getting latest records by types: {e}")
            # 返回空的结果字典，避免调用方出错
            return {data_type: None for data_type in data_types}
    
    def get_records_by_date_range(self, elderly_id: uuid.UUID, data_type: str,
                                start_date: datetime, end_date: datetime, 
                                skip: int = 0, limit: int = 1000) -> List[HealthRecord]:
        """获取指定日期范围内的健康记录"""
        try:
            return self.db.query(HealthRecord).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.data_type == data_type,
                HealthRecord.record_time >= start_date,
                HealthRecord.record_time <= end_date
            ).order_by(desc(HealthRecord.record_time)).offset(skip).limit(limit).all()
        
        except Exception as e:
            print(f"Error getting records by date range: {e}")
            return []
    
    def get_daily_summary(self, elderly_id: uuid.UUID, date: datetime) -> Dict[str, Any]:
        """获取指定日期的健康数据汇总"""
        # 定义一天的时间范围
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 定义需要统计的数据类型
        data_types = ["heart_rate", "blood_pressure", "blood_sugar", "temperature", "step_count", "sleep_time"]
        
        summary = {
            "date": date.date(),
            "data_count": 0,
            "has_abnormal": False,
            "health_metrics": {}
        }
        
        try:
            for data_type in data_types:
                # 查询该类型当天的所有记录
                records = self.db.query(HealthRecord).filter(
                    HealthRecord.elderly_id == elderly_id,
                    HealthRecord.data_type == data_type,
                    HealthRecord.record_time >= start_of_day,
                    HealthRecord.record_time <= end_of_day
                ).all()
                
                if records:
                    summary["data_count"] += len(records)
                    
                    # 检查是否有异常记录
                    has_abnormal = any(not record.is_normal for record in records)
                    summary["has_abnormal"] = summary["has_abnormal"] or has_abnormal
                    
                    # 血压特殊处理，分别统计收缩压和舒张压
                    if data_type == "blood_pressure":
                        # 这里需要从记录中提取收缩压和舒张压（假设值存储为字符串 "收缩压/舒张压"）
                        systolic_values = []
                        diastolic_values = []
                        
                        for record in records:
                            try:
                                # 假设值存储格式为 "收缩压,舒张压"
                                systolic, diastolic = map(float, str(record.value).split(','))
                                systolic_values.append(systolic)
                                diastolic_values.append(diastolic)
                            except (ValueError, AttributeError, TypeError):
                                # 处理可能的格式错误
                                pass
                        
                        if systolic_values and diastolic_values:
                            summary["health_metrics"]["systolic_pressure"] = {
                                "min": min(systolic_values),
                                "max": max(systolic_values),
                                "avg": sum(systolic_values) / len(systolic_values),
                                "count": len(systolic_values),
                                "has_abnormal": any(v > 140 or v < 90 for v in systolic_values)
                            }
                            
                            summary["health_metrics"]["diastolic_pressure"] = {
                                "min": min(diastolic_values),
                                "max": max(diastolic_values),
                                "avg": sum(diastolic_values) / len(diastolic_values),
                                "count": len(diastolic_values),
                                "has_abnormal": any(v > 90 or v < 60 for v in diastolic_values)
                            }
                    else:
                        # 其他数据类型的处理
                        values = [record.value for record in records]
                        summary["health_metrics"][data_type] = {
                            "min": min(values),
                            "max": max(values),
                            "avg": sum(values) / len(values),
                            "count": len(values),
                            "has_abnormal": has_abnormal
                        }
            
            return summary
        
        except Exception as e:
            print(f"Error getting daily summary: {e}")
            return summary
    
    def get_weekly_trend(self, elderly_id: uuid.UUID, data_type: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取指定健康指标的周趋势数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trend_data = []
        
        try:
            # 按天分组获取统计数据
            current_date = start_date
            while current_date <= end_date:
                daily_summary = self.get_daily_summary(elderly_id, current_date)
                
                if data_type in daily_summary["health_metrics"]:
                    metric_data = daily_summary["health_metrics"][data_type]
                    trend_data.append({
                        "date": current_date.date(),
                        "value": metric_data["avg"],
                        "max": metric_data["max"],
                        "min": metric_data["min"],
                        "has_abnormal": metric_data["has_abnormal"]
                    })
                else:
                    # 如果当天没有数据，添加一个空记录
                    trend_data.append({
                        "date": current_date.date(),
                        "value": None,
                        "max": None,
                        "min": None,
                        "has_abnormal": False
                    })
                
                current_date += timedelta(days=1)
            
            return trend_data
        
        except Exception as e:
            print(f"Error getting weekly trend: {e}")
            return []
    
    def get_health_statistics(self, elderly_id: uuid.UUID, days: int = 30) -> Dict[str, Any]:
        """获取指定天数内的健康统计数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            "total_records": 0,
            "abnormal_records": 0,
            "abnormal_rate": 0.0,
            "daily_average": 0.0,
            "data_types": {}
        }
        
        try:
            # 获取记录总数
            total_records = self.db.query(func.count(HealthRecord.id)).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.record_time >= start_date,
                HealthRecord.record_time <= end_date
            ).scalar()
            
            # 获取异常记录数
            abnormal_records = self.db.query(func.count(HealthRecord.id)).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.record_time >= start_date,
                HealthRecord.record_time <= end_date,
                HealthRecord.is_normal == False
            ).scalar()
            
            # 计算异常率
            if total_records > 0:
                stats["total_records"] = total_records
                stats["abnormal_records"] = abnormal_records
                stats["abnormal_rate"] = (abnormal_records / total_records) * 100
                stats["daily_average"] = total_records / days
            
            # 按数据类型统计
            data_types = self.db.query(
                HealthRecord.data_type,
                func.count(HealthRecord.id).label('count'),
                func.sum(HealthRecord.is_normal == False).label('abnormal_count')
            ).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.record_time >= start_date,
                HealthRecord.record_time <= end_date
            ).group_by(HealthRecord.data_type).all()
            
            for data_type, count, abnormal_count in data_types:
                stats["data_types"][data_type] = {
                    "count": count,
                    "abnormal_count": abnormal_count,
                    "abnormal_rate": (abnormal_count / count * 100) if count > 0 else 0
                }
            
            return stats
        
        except Exception as e:
            print(f"Error getting health statistics: {e}")
            return stats
    
    def _check_health_normal(self, data_type: str, value: float) -> bool:
        """检查健康数据是否在正常范围内"""
        # 根据不同的健康数据类型设置不同的正常范围
        normal_ranges = {
            "heart_rate": (60, 100),  # 心率：60-100次/分
            "blood_pressure": (80, 140),  # 收缩压：90-140mmHg，舒张压：60-90mmHg
            "blood_sugar": (3.9, 6.1),  # 血糖：3.9-6.1mmol/L（空腹）
            "temperature": (36.0, 37.5),  # 体温：36.0-37.5℃
            "step_count": (5000, 15000),  # 步数：5000-15000步/天
            "sleep_time": (6, 9)  # 睡眠时间：6-9小时/天
        }
        
        # 检查是否为有效范围
        if data_type not in normal_ranges:
            return True  # 未知类型默认为正常
        
        # 获取正常范围
        min_value, max_value = normal_ranges[data_type]
        
        # 血压需要特殊处理
        if data_type == "blood_pressure":
            try:
                # 假设值存储格式为 "收缩压,舒张压"
                systolic, diastolic = map(float, str(value).split(','))
                # 收缩压和舒张压都需要在正常范围内
                systolic_normal = 90 <= systolic <= 140
                diastolic_normal = 60 <= diastolic <= 90
                return systolic_normal and diastolic_normal
            except (ValueError, AttributeError, TypeError):
                # 处理格式错误
                return False
        
        # 其他类型的正常范围检查
        return min_value <= value <= max_value
    
    def _create_health_alert(self, elderly_id: uuid.UUID, data_type: str, 
                           value: float, alert_time: datetime) -> Optional[Alert]:
        """创建健康告警"""
        try:
            # 构建告警描述
            alert_descriptions = {
                "heart_rate": f"心率异常: {value}次/分",
                "blood_pressure": f"血压异常: {value}mmHg",
                "blood_sugar": f"血糖异常: {value}mmol/L",
                "temperature": f"体温异常: {value}℃",
                "step_count": f"步数异常: {value}步",
                "sleep_time": f"睡眠时间异常: {value}小时"
            }
            
            description = alert_descriptions.get(data_type, f"健康指标异常: {data_type} = {value}")
            
            # 检查是否已有相同类型的未处理告警，如果有则不重复创建
            existing_alert = self.db.query(Alert).filter(
                Alert.elderly_id == elderly_id,
                Alert.alert_type == data_type,
                Alert.status == "未处理"
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    elderly_id=elderly_id,
                    alert_type=data_type,
                    description=description,
                    alert_time=alert_time,
                    status="未处理"
                )
                
                self.db.add(alert)
                self.db.commit()
                self.db.refresh(alert)
                
                return alert
            
            return None
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating health alert: {e}")
            return None
    
    def batch_add_health_records(self, records: List[Dict[str, Any]]) -> List[HealthRecord]:
        """批量添加健康记录"""
        created_records = []
        
        try:
            for record_data in records:
                # 验证必要字段
                if 'elderly_id' not in record_data or 'data_type' not in record_data or 'value' not in record_data:
                    continue
                
                # 检查是否有相同类型的最新记录
                latest_record = self.get_latest_record(record_data['elderly_id'], record_data['data_type'])
                
                # 确定健康记录是否正常
                is_normal = self._check_health_normal(record_data['data_type'], record_data['value'])
                
                # 创建健康记录
                health_record = HealthRecord(
                    elderly_id=record_data['elderly_id'],
                    data_type=record_data['data_type'],
                    value=record_data['value'],
                    record_time=record_data.get('record_time', datetime.now()),
                    is_normal=is_normal
                )
                
                self.db.add(health_record)
                created_records.append(health_record)
                
                # 如果异常，创建告警
                if not is_normal:
                    self._create_health_alert(
                        record_data['elderly_id'],
                        record_data['data_type'],
                        record_data['value'],
                        health_record.record_time
                    )
            
            self.db.commit()
            
            # 刷新所有创建的记录
            for record in created_records:
                self.db.refresh(record)
            
            return created_records
        
        except Exception as e:
            self.db.rollback()
            print(f"Error batch adding health records: {e}")
            raise