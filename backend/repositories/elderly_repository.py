"""老人相关的Repository类"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
import uuid

from repositories.base import BaseRepository
from database.models import ElderlyProfile, HealthRecord, Alert, Reminder, ChildrenElderlyRelation


class ElderlyRepository(BaseRepository[ElderlyProfile]):
    """老人档案数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, ElderlyProfile)
    
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[ElderlyProfile]:
        """根据用户ID获取老人档案"""
        return self.get_one(user_id=user_id)
    
    def get_with_health_data(self, elderly_id: uuid.UUID) -> Dict[str, Any]:
        """获取老人档案及其最新健康数据"""
        elderly = self.get_by_id(elderly_id)
        if not elderly:
            return {"elderly": None, "health_data": None}
        
        # 获取最新的各项健康数据
        latest_health_data = {}
        health_types = [
            ("heart_rate", "heart_rate"),
            ("blood_pressure", "systolic_pressure"),
            ("blood_pressure", "diastolic_pressure"),
            ("blood_sugar", "blood_sugar"),
            ("temperature", "temperature"),
            ("step_count", "step_count"),
            ("sleep_time", "sleep_time")
        ]
        
        last_update = None
        
        for data_type, field_name in health_types:
            record = self.db.query(HealthRecord).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.data_type == data_type
            ).order_by(desc(HealthRecord.record_time)).first()
            
            if record:
                latest_health_data[field_name] = record.value
                if not last_update or record.record_time > last_update:
                    last_update = record.record_time
        
        # 计算健康状态
        health_status = "正常"
        if latest_health_data:
            # 简单的健康状态判断逻辑
            if "heart_rate" in latest_health_data:
                heart_rate = latest_health_data["heart_rate"]
                if heart_rate < 60 or heart_rate > 100:
                    health_status = "异常"
            
            if "systolic_pressure" in latest_health_data and "diastolic_pressure" in latest_health_data:
                systolic = latest_health_data["systolic_pressure"]
                diastolic = latest_health_data["diastolic_pressure"]
                if systolic > 140 or diastolic > 90:
                    health_status = "异常"
                elif systolic < 90 or diastolic < 60:
                    health_status = "异常"
            
            if "temperature" in latest_health_data:
                temp = latest_health_data["temperature"]
                if temp < 36.0 or temp > 37.5:
                    health_status = "异常"
        
        latest_health_data["health_status"] = health_status
        latest_health_data["last_update"] = last_update or elderly.updated_at
        
        return {"elderly": elderly, "health_data": latest_health_data}
    
    def get_elderly_list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取老人列表（带简化信息）"""
        try:
            elderly_list = self.db.query(ElderlyProfile).offset(skip).limit(limit).all()
            result = []
            
            for elderly in elderly_list:
                # 计算年龄
                age = 0
                if elderly.birth_date:
                    today = datetime.now()
                    age = today.year - elderly.birth_date.year
                    if (today.month, today.day) < (elderly.birth_date.month, elderly.birth_date.day):
                        age -= 1
                
                # 获取最新的健康状态
                health_status = "未知"
                status_message = None
                last_update = elderly.updated_at
                
                # 查找最新的健康记录
                latest_record = self.db.query(HealthRecord).filter(
                    HealthRecord.elderly_id == elderly.id
                ).order_by(desc(HealthRecord.record_time)).first()
                
                if latest_record:
                    last_update = latest_record.record_time
                    
                    # 查找是否有未处理的告警
                    latest_alert = self.db.query(Alert).filter(
                        Alert.elderly_id == elderly.id,
                        Alert.status == "未处理"
                    ).order_by(desc(Alert.alert_time)).first()
                    
                    if latest_alert:
                        health_status = "告警"
                        status_message = latest_alert.description
                    else:
                        health_status = "正常" if latest_record.is_normal else "异常"
                
                result.append({
                    "id": elderly.id,
                    "name": elderly.name,
                    "age": age,
                    "gender": elderly.gender,
                    "address": elderly.address,
                    "last_update": last_update,
                    "health_status": health_status,
                    "status_message": status_message
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting elderly list: {e}")
            return []
    
    def search_elderly(self, keyword: str, skip: int = 0, limit: int = 100) -> List[ElderlyProfile]:
        """搜索老人（根据姓名或身份证号）"""
        try:
            query = self.db.query(ElderlyProfile)
            
            if keyword:
                query = query.filter(
                    ElderlyProfile.name.like(f"%{keyword}%") | 
                    ElderlyProfile.id_card.like(f"%{keyword}%") |
                    ElderlyProfile.phone_number.like(f"%{keyword}%")
                )
            
            return query.offset(skip).limit(limit).all()
        
        except Exception as e:
            print(f"Error searching elderly: {e}")
            return []
    
    def get_elderly_by_children(self, children_id: uuid.UUID) -> List[ElderlyProfile]:
        """获取关联到指定子女的所有老人"""
        try:
            # 通过关系表查询
            elderly_ids = self.db.query(ChildrenElderlyRelation.elderly_id).filter(
                ChildrenElderlyRelation.children_id == children_id
            ).subquery()
            
            return self.db.query(ElderlyProfile).filter(
                ElderlyProfile.id.in_(elderly_ids)
            ).all()
        
        except Exception as e:
            print(f"Error getting elderly by children: {e}")
            return []
    
    def get_elderly_with_relation(self, elderly_id: uuid.UUID, children_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """获取老人信息及其与指定子女的关系"""
        elderly = self.get_by_id(elderly_id)
        if not elderly:
            return None
        
        relation = self.db.query(ChildrenElderlyRelation).filter(
            ChildrenElderlyRelation.elderly_id == elderly_id,
            ChildrenElderlyRelation.children_id == children_id
        ).first()
        
        return {
            "elderly": elderly,
            "relation": relation,
            "relation_type": relation.relationship_type if relation else None
        }
    
    def get_recent_health_records(self, elderly_id: uuid.UUID, 
                                days: int = 7, data_type: Optional[str] = None) -> List[HealthRecord]:
        """获取最近N天的健康记录"""
        try:
            query = self.db.query(HealthRecord).filter(
                HealthRecord.elderly_id == elderly_id,
                HealthRecord.record_time >= datetime.now() - timedelta(days=days)
            )
            
            if data_type:
                query = query.filter(HealthRecord.data_type == data_type)
            
            return query.order_by(desc(HealthRecord.record_time)).all()
        
        except Exception as e:
            print(f"Error getting recent health records: {e}")
            return []
    
    def get_pending_alerts(self, elderly_id: uuid.UUID) -> List[Alert]:
        """获取老人的未处理告警"""
        try:
            return self.db.query(Alert).filter(
                Alert.elderly_id == elderly_id,
                Alert.status == "未处理"
            ).order_by(desc(Alert.alert_time)).all()
        
        except Exception as e:
            print(f"Error getting pending alerts: {e}")
            return []
    
    def get_today_reminders(self, elderly_id: uuid.UUID) -> List[Reminder]:
        """获取今天的提醒"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            return self.db.query(Reminder).filter(
                Reminder.elderly_id == elderly_id,
                Reminder.reminder_time >= today,
                Reminder.reminder_time < tomorrow,
                Reminder.status != "已取消"
            ).order_by(Reminder.reminder_time).all()
        
        except Exception as e:
            print(f"Error getting today reminders: {e}")
            return []