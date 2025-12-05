"""告警和提醒相关的Repository类"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
import uuid

from repositories.base import BaseRepository
from database.models import Alert, Reminder, ElderlyProfile


class AlertRepository(BaseRepository[Alert]):
    """告警数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, Alert)
    
    def create_alert(self, elderly_id: uuid.UUID, alert_type: str, 
                    description: str, alert_time: Optional[datetime] = None) -> Alert:
        """创建告警"""
        try:
            alert = Alert(
                elderly_id=elderly_id,
                alert_type=alert_type,
                description=description,
                alert_time=alert_time or datetime.now(),
                status="未处理"
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating alert: {e}")
            raise
    
    def get_elderly_alerts(self, elderly_id: uuid.UUID, 
                          status: Optional[str] = None, 
                          alert_type: Optional[str] = None, 
                          skip: int = 0, limit: int = 100) -> List[Alert]:
        """获取老人的告警列表"""
        try:
            query = self.db.query(Alert).filter(Alert.elderly_id == elderly_id)
            
            # 根据状态筛选
            if status:
                query = query.filter(Alert.status == status)
            
            # 根据告警类型筛选
            if alert_type:
                query = query.filter(Alert.alert_type == alert_type)
            
            # 按告警时间降序排列
            return query.order_by(desc(Alert.alert_time)).offset(skip).limit(limit).all()
        
        except Exception as e:
            print(f"Error getting elderly alerts: {e}")
            return []
    
    def get_pending_alerts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有未处理的告警（带老人信息）"""
        try:
            # 联合查询告警和老人信息
            alerts_with_elderly = self.db.query(
                Alert,
                ElderlyProfile.name.label('elderly_name'),
                ElderlyProfile.phone_number.label('elderly_phone')
            ).join(
                ElderlyProfile,
                Alert.elderly_id == ElderlyProfile.id
            ).filter(
                Alert.status == "未处理"
            ).order_by(
                desc(Alert.alert_time)
            ).offset(skip).limit(limit).all()
            
            result = []
            for alert, elderly_name, elderly_phone in alerts_with_elderly:
                result.append({
                    "alert": alert,
                    "elderly_name": elderly_name,
                    "elderly_phone": elderly_phone
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting pending alerts: {e}")
            return []
    
    def get_alerts_by_date_range(self, elderly_id: uuid.UUID, 
                               start_date: datetime, end_date: datetime, 
                               skip: int = 0, limit: int = 100) -> List[Alert]:
        """获取指定日期范围内的告警"""
        try:
            return self.db.query(Alert).filter(
                Alert.elderly_id == elderly_id,
                Alert.alert_time >= start_date,
                Alert.alert_time <= end_date
            ).order_by(desc(Alert.alert_time)).offset(skip).limit(limit).all()
        
        except Exception as e:
            print(f"Error getting alerts by date range: {e}")
            return []
    
    def update_alert_status(self, alert_id: uuid.UUID, status: str, 
                          processed_by: Optional[uuid.UUID] = None, 
                          processed_time: Optional[datetime] = None, 
                          remark: Optional[str] = None) -> Optional[Alert]:
        """更新告警状态"""
        try:
            alert = self.get_by_id(alert_id)
            if not alert:
                return None
            
            # 更新告警状态
            alert.status = status
            alert.processed_by = processed_by
            alert.processed_time = processed_time or datetime.now()
            alert.remark = remark
            alert.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
        
        except Exception as e:
            self.db.rollback()
            print(f"Error updating alert status: {e}")
            return None
    
    def batch_update_alert_status(self, alert_ids: List[uuid.UUID], status: str, 
                                 processed_by: Optional[uuid.UUID] = None) -> int:
        """批量更新告警状态"""
        try:
            result = self.db.query(Alert).filter(
                Alert.id.in_(alert_ids)
            ).update({
                "status": status,
                "processed_by": processed_by,
                "processed_time": datetime.now(),
                "updated_at": datetime.now()
            }, synchronize_session=False)
            
            self.db.commit()
            return result
        
        except Exception as e:
            self.db.rollback()
            print(f"Error batch updating alert status: {e}")
            return 0
    
    def get_alert_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取告警统计信息"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            "total_alerts": 0,
            "pending_alerts": 0,
            "processed_alerts": 0,
            "alert_types": {},
            "daily_alerts": []
        }
        
        try:
            # 总告警数
            total_alerts = self.db.query(func.count(Alert.id)).filter(
                Alert.alert_time >= start_date,
                Alert.alert_time <= end_date
            ).scalar()
            
            # 未处理告警数
            pending_alerts = self.db.query(func.count(Alert.id)).filter(
                Alert.alert_time >= start_date,
                Alert.alert_time <= end_date,
                Alert.status == "未处理"
            ).scalar()
            
            # 已处理告警数
            processed_alerts = total_alerts - pending_alerts
            
            stats["total_alerts"] = total_alerts
            stats["pending_alerts"] = pending_alerts
            stats["processed_alerts"] = processed_alerts
            
            # 按告警类型统计
            alert_type_stats = self.db.query(
                Alert.alert_type,
                func.count(Alert.id).label('count')
            ).filter(
                Alert.alert_time >= start_date,
                Alert.alert_time <= end_date
            ).group_by(Alert.alert_type).all()
            
            for alert_type, count in alert_type_stats:
                stats["alert_types"][alert_type] = count
            
            # 按天统计告警数
            current_date = start_date
            while current_date <= end_date:
                next_day = current_date + timedelta(days=1)
                
                daily_count = self.db.query(func.count(Alert.id)).filter(
                    Alert.alert_time >= current_date,
                    Alert.alert_time < next_day
                ).scalar()
                
                stats["daily_alerts"].append({
                    "date": current_date.date(),
                    "count": daily_count
                })
                
                current_date = next_day
            
            return stats
        
        except Exception as e:
            print(f"Error getting alert statistics: {e}")
            return stats


class ReminderRepository(BaseRepository[Reminder]):
    """提醒数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, Reminder)
    
    def create_reminder(self, elderly_id: uuid.UUID, reminder_type: str,
                       description: str, reminder_time: datetime,
                       is_recurring: bool = False, recurring_rule: Optional[str] = None) -> Reminder:
        """创建提醒"""
        try:
            reminder = Reminder(
                elderly_id=elderly_id,
                reminder_type=reminder_type,
                description=description,
                reminder_time=reminder_time,
                is_recurring=is_recurring,
                recurring_rule=recurring_rule,
                status="待提醒"
            )
            
            self.db.add(reminder)
            self.db.commit()
            self.db.refresh(reminder)
            
            return reminder
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating reminder: {e}")
            raise
    
    def get_elderly_reminders(self, elderly_id: uuid.UUID,
                            status: Optional[str] = None,
                            reminder_type: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None,
                            skip: int = 0, limit: int = 100) -> List[Reminder]:
        """获取老人的提醒列表"""
        try:
            query = self.db.query(Reminder).filter(Reminder.elderly_id == elderly_id)
            
            # 根据状态筛选
            if status:
                query = query.filter(Reminder.status == status)
            
            # 根据提醒类型筛选
            if reminder_type:
                query = query.filter(Reminder.reminder_type == reminder_type)
            
            # 根据时间范围筛选
            if start_time:
                query = query.filter(Reminder.reminder_time >= start_time)
            
            if end_time:
                query = query.filter(Reminder.reminder_time <= end_time)
            
            # 按提醒时间升序排列（先到先得）
            return query.order_by(Reminder.reminder_time).offset(skip).limit(limit).all()
        
        except Exception as e:
            print(f"Error getting elderly reminders: {e}")
            return []
    
    def get_pending_reminders(self, current_time: Optional[datetime] = None) -> List[Reminder]:
        """获取所有待提醒的记录（当前时间或之后）"""
        try:
            now = current_time or datetime.now()
            
            # 查找所有待提醒且时间未到或刚到的提醒
            return self.db.query(Reminder).filter(
                Reminder.status == "待提醒",
                Reminder.reminder_time <= now + timedelta(minutes=5)  # 包括未来5分钟内的提醒
            ).order_by(Reminder.reminder_time).all()
        
        except Exception as e:
            print(f"Error getting pending reminders: {e}")
            return []
    
    def get_today_reminders(self, elderly_id: uuid.UUID) -> List[Reminder]:
        """获取今天的提醒"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.combine(tomorrow, datetime.min.time()) - timedelta(seconds=1)
            
            return self.get_elderly_reminders(
                elderly_id=elderly_id,
                start_time=start_time,
                end_time=end_time
            )
        
        except Exception as e:
            print(f"Error getting today reminders: {e}")
            return []
    
    def update_reminder_status(self, reminder_id: uuid.UUID, status: str,
                             completed_time: Optional[datetime] = None,
                             remark: Optional[str] = None) -> Optional[Reminder]:
        """更新提醒状态"""
        try:
            reminder = self.get_by_id(reminder_id)
            if not reminder:
                return None
            
            # 更新提醒状态
            reminder.status = status
            if status == "已完成":
                reminder.completed_time = completed_time or datetime.now()
            reminder.remark = remark
            reminder.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(reminder)
            
            # 如果是重复提醒，创建下一次提醒
            if reminder.is_recurring and status in ["已完成", "已提醒"]:
                self._create_next_recurring_reminder(reminder)
            
            return reminder
        
        except Exception as e:
            self.db.rollback()
            print(f"Error updating reminder status: {e}")
            return None
    
    def delete_reminder(self, reminder_id: uuid.UUID) -> bool:
        """删除提醒"""
        try:
            reminder = self.get_by_id(reminder_id)
            if not reminder:
                return False
            
            # 如果是重复提醒，需要考虑是否停止所有后续提醒
            self.db.delete(reminder)
            self.db.commit()
            
            return True
        
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting reminder: {e}")
            return False
    
    def get_reminder_statistics(self, elderly_id: uuid.UUID, days: int = 30) -> Dict[str, Any]:
        """获取提醒统计信息"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            "total_reminders": 0,
            "completed_reminders": 0,
            "missed_reminders": 0,
            "reminder_types": {}
        }
        
        try:
            # 总提醒数
            total_reminders = self.db.query(func.count(Reminder.id)).filter(
                Reminder.elderly_id == elderly_id,
                Reminder.reminder_time >= start_date,
                Reminder.reminder_time <= end_date
            ).scalar()
            
            # 已完成的提醒数
            completed_reminders = self.db.query(func.count(Reminder.id)).filter(
                Reminder.elderly_id == elderly_id,
                Reminder.reminder_time >= start_date,
                Reminder.reminder_time <= end_date,
                Reminder.status == "已完成"
            ).scalar()
            
            # 未完成且已过期的提醒（错过的提醒）
            missed_reminders = self.db.query(func.count(Reminder.id)).filter(
                Reminder.elderly_id == elderly_id,
                Reminder.reminder_time < datetime.now(),
                Reminder.reminder_time >= start_date,
                Reminder.status == "待提醒"
            ).scalar()
            
            stats["total_reminders"] = total_reminders
            stats["completed_reminders"] = completed_reminders
            stats["missed_reminders"] = missed_reminders
            
            # 按提醒类型统计
            reminder_type_stats = self.db.query(
                Reminder.reminder_type,
                func.count(Reminder.id).label('count')
            ).filter(
                Reminder.elderly_id == elderly_id,
                Reminder.reminder_time >= start_date,
                Reminder.reminder_time <= end_date
            ).group_by(Reminder.reminder_type).all()
            
            for reminder_type, count in reminder_type_stats:
                stats["reminder_types"][reminder_type] = count
            
            return stats
        
        except Exception as e:
            print(f"Error getting reminder statistics: {e}")
            return stats
    
    def _create_next_recurring_reminder(self, reminder: Reminder) -> Optional[Reminder]:
        """根据重复规则创建下一次提醒"""
        try:
            if not reminder.is_recurring or not reminder.recurring_rule:
                return None
            
            # 解析重复规则（简单实现）
            # 支持的规则格式：
            # - "daily": 每天
            # - "weekly": 每周
            # - "monthly": 每月
            # - "custom:2": 每2天
            # - "custom:3d": 每3天
            # - "custom:1w": 每1周
            
            next_reminder_time = None
            
            if reminder.recurring_rule == "daily":
                next_reminder_time = reminder.reminder_time + timedelta(days=1)
            elif reminder.recurring_rule == "weekly":
                next_reminder_time = reminder.reminder_time + timedelta(weeks=1)
            elif reminder.recurring_rule == "monthly":
                # 简单处理，加30天
                next_reminder_time = reminder.reminder_time + timedelta(days=30)
            elif reminder.recurring_rule.startswith("custom:"):
                rule_value = reminder.recurring_rule.split(":")[1]
                
                # 检查是否有单位
                if rule_value.endswith("d"):
                    days = int(rule_value[:-1])
                    next_reminder_time = reminder.reminder_time + timedelta(days=days)
                elif rule_value.endswith("w"):
                    weeks = int(rule_value[:-1])
                    next_reminder_time = reminder.reminder_time + timedelta(weeks=weeks)
                else:
                    # 默认按天计算
                    days = int(rule_value)
                    next_reminder_time = reminder.reminder_time + timedelta(days=days)
            
            # 如果成功计算出下一次提醒时间，创建新提醒
            if next_reminder_time:
                new_reminder = Reminder(
                    elderly_id=reminder.elderly_id,
                    reminder_type=reminder.reminder_type,
                    description=reminder.description,
                    reminder_time=next_reminder_time,
                    is_recurring=reminder.is_recurring,
                    recurring_rule=reminder.recurring_rule,
                    status="待提醒"
                )
                
                self.db.add(new_reminder)
                self.db.commit()
                self.db.refresh(new_reminder)
                
                return new_reminder
            
            return None
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating next recurring reminder: {e}")
            return None


# 导入缺失的func
from sqlalchemy import func