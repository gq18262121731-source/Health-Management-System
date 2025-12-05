"""儿童（子女）相关的Repository类"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, or_, func
import uuid

from repositories.base import BaseRepository
from database.models import User, ElderlyProfile, ChildrenElderlyRelation, HealthRecord, Alert


class ChildrenRepository(BaseRepository[User]):
    """儿童（子女）数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_children_by_id(self, children_id: uuid.UUID) -> Optional[User]:
        """根据ID获取子女用户信息"""
        try:
            user = self.get_by_id(children_id)
            if user and user.role == "user":
                return user
            return None
        except Exception as e:
            print(f"Error getting children by id: {e}")
            return None
    
    def add_elderly_relation(self, children_id: uuid.UUID, elderly_id: uuid.UUID,
                            relationship_type: str) -> Optional[ChildrenElderlyRelation]:
        """添加子女-老人关系"""
        try:
            # 检查子女和老人是否存在
            children = self.get_by_id(children_id)
            if not children or children.role != "user":
                return None
            
            elderly = self.db.query(ElderlyProfile).filter(ElderlyProfile.id == elderly_id).first()
            if not elderly:
                return None
            
            # 检查关系是否已存在
            existing_relation = self.db.query(ChildrenElderlyRelation).filter(
                and_(
                    ChildrenElderlyRelation.children_id == children_id,
                    ChildrenElderlyRelation.elderly_id == elderly_id
                )
            ).first()
            
            if existing_relation:
                # 如果关系已存在，更新关系类型
                existing_relation.relationship_type = relationship_type
                existing_relation.updated_at = datetime.now()
                self.db.commit()
                self.db.refresh(existing_relation)
                return existing_relation
            
            # 创建新的关系
            relation = ChildrenElderlyRelation(
                children_id=children_id,
                elderly_id=elderly_id,
                relationship_type=relationship_type
            )
            
            self.db.add(relation)
            self.db.commit()
            self.db.refresh(relation)
            
            return relation
        
        except Exception as e:
            self.db.rollback()
            print(f"Error adding elderly relation: {e}")
            return None
    
    def remove_elderly_relation(self, children_id: uuid.UUID, elderly_id: uuid.UUID) -> bool:
        """移除子女-老人关系"""
        try:
            # 查找关系
            relation = self.db.query(ChildrenElderlyRelation).filter(
                and_(
                    ChildrenElderlyRelation.children_id == children_id,
                    ChildrenElderlyRelation.elderly_id == elderly_id
                )
            ).first()
            
            if not relation:
                return False
            
            # 删除关系
            self.db.delete(relation)
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            print(f"Error removing elderly relation: {e}")
            return False
    
    def get_children_elderly_list(self, children_id: uuid.UUID, 
                                skip: int = 0, limit: int = 100,
                                search_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取子女关联的老人列表"""
        try:
            # 查询子女关联的老人
            query = self.db.query(ElderlyProfile).join(
                ChildrenElderlyRelation,
                ElderlyProfile.id == ChildrenElderlyRelation.elderly_id
            ).filter(
                ChildrenElderlyRelation.children_id == children_id
            )
            
            # 搜索过滤
            if search_keyword:
                query = query.filter(
                    or_(
                        ElderlyProfile.name.like(f"%{search_keyword}%"),
                        ElderlyProfile.id_card.like(f"%{search_keyword}%"),
                        ElderlyProfile.phone_number.like(f"%{search_keyword}%")
                    )
                )
            
            elderly_list = query.order_by(desc(ChildrenElderlyRelation.created_at)).offset(skip).limit(limit).all()
            
            result = []
            for elderly in elderly_list:
                # 获取关系类型
                relation = self.db.query(ChildrenElderlyRelation).filter(
                    and_(
                        ChildrenElderlyRelation.children_id == children_id,
                        ChildrenElderlyRelation.elderly_id == elderly.id
                    )
                ).first()
                
                # 获取最新健康记录
                latest_health = self.db.query(HealthRecord).filter(
                    HealthRecord.elderly_id == elderly.id
                ).order_by(desc(HealthRecord.record_time)).first()
                
                # 获取待处理告警数量
                pending_alerts_count = self.db.query(func.count(Alert.id)).filter(
                    and_(
                        Alert.elderly_id == elderly.id,
                        Alert.status == "pending"
                    )
                ).scalar()
                
                result.append({
                    "elderly": elderly,
                    "relationship_type": relation.relationship_type if relation else None,
                    "latest_health": latest_health,
                    "pending_alerts_count": pending_alerts_count
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting children elderly list: {e}")
            return []
    
    def get_elderly_children_list(self, elderly_id: uuid.UUID) -> List[Dict[str, Any]]:
        """获取老人的子女列表"""
        try:
            # 查询老人关联的子女
            relations = self.db.query(
                User,
                ChildrenElderlyRelation.relationship_type,
                ChildrenElderlyRelation.created_at
            ).join(
                ChildrenElderlyRelation,
                User.id == ChildrenElderlyRelation.children_id
            ).filter(
                ChildrenElderlyRelation.elderly_id == elderly_id
            ).all()
            
            result = []
            for user, relationship_type, created_at in relations:
                result.append({
                    "user": user,
                    "relationship_type": relationship_type,
                    "created_at": created_at
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting elderly children list: {e}")
            return []
    
    def get_children_elderly_dashboard(self, children_id: uuid.UUID) -> Dict[str, Any]:
        """获取子女的老人管理仪表盘数据"""
        dashboard_data = {
            "total_elderly": 0,
            "pending_alerts": 0,
            "recent_health_records": [],
            "elderly_status_summary": []
        }
        
        try:
            # 统计子女关联的老人总数
            total_elderly = self.db.query(func.count(ChildrenElderlyRelation.id)).filter(
                ChildrenElderlyRelation.children_id == children_id
            ).scalar()
            dashboard_data["total_elderly"] = total_elderly
            
            # 获取关联老人的ID列表
            elderly_ids = [r.elderly_id for r in self.db.query(
                ChildrenElderlyRelation.elderly_id
            ).filter(
                ChildrenElderlyRelation.children_id == children_id
            ).all()]
            
            if elderly_ids:
                # 统计待处理告警数量
                pending_alerts = self.db.query(func.count(Alert.id)).filter(
                    and_(
                        Alert.elderly_id.in_(elderly_ids),
                        Alert.status == "pending"
                    )
                ).scalar()
                dashboard_data["pending_alerts"] = pending_alerts
                
                # 获取最近的健康记录（按时间倒序，最多10条）
                recent_records = self.db.query(
                    HealthRecord,
                    ElderlyProfile.name
                ).join(
                    ElderlyProfile,
                    HealthRecord.elderly_id == ElderlyProfile.id
                ).filter(
                    HealthRecord.elderly_id.in_(elderly_ids)
                ).order_by(
                    desc(HealthRecord.record_time)
                ).limit(10).all()
                
                dashboard_data["recent_health_records"] = [
                    {
                        "record": record,
                        "elderly_name": elderly_name
                    }
                    for record, elderly_name in recent_records
                ]
                
                # 获取每位老人的健康状态摘要
                for elderly_id in elderly_ids:
                    # 获取老人信息
                    elderly = self.db.query(ElderlyProfile).filter(
                        ElderlyProfile.id == elderly_id
                    ).first()
                    
                    if elderly:
                        # 获取最新健康记录
                        latest_health = self.db.query(HealthRecord).filter(
                            HealthRecord.elderly_id == elderly_id
                        ).order_by(desc(HealthRecord.record_time)).first()
                        
                        # 获取待处理告警数量
                        elderly_pending_alerts = self.db.query(func.count(Alert.id)).filter(
                            and_(
                                Alert.elderly_id == elderly_id,
                                Alert.status == "pending"
                            )
                        ).scalar()
                        
                        # 获取24小时内的健康记录数量
                        last_24h_records = self.db.query(func.count(HealthRecord.id)).filter(
                            and_(
                                HealthRecord.elderly_id == elderly_id,
                                HealthRecord.record_time >= datetime.now() - timedelta(hours=24)
                            )
                        ).scalar()
                        
                        # 判断健康状态
                        health_status = "normal"
                        if elderly_pending_alerts > 0:
                            health_status = "alert"
                        elif not latest_health or last_24h_records == 0:
                            health_status = "inactive"
                        elif latest_health and (latest_health.blood_pressure_abnormal or 
                                              latest_health.heart_rate_abnormal or 
                                              latest_health.blood_sugar_abnormal):
                            health_status = "abnormal"
                        
                        dashboard_data["elderly_status_summary"].append({
                            "elderly_id": elderly.id,
                            "elderly_name": elderly.name,
                            "health_status": health_status,
                            "pending_alerts": elderly_pending_alerts,
                            "latest_record_time": latest_health.record_time if latest_health else None,
                            "age": elderly.age
                        })
            
            return dashboard_data
        
        except Exception as e:
            print(f"Error getting children elderly dashboard: {e}")
            return dashboard_data
    
    def update_children_profile(self, children_id: uuid.UUID, **kwargs) -> Optional[User]:
        """更新子女用户资料"""
        try:
            children = self.get_by_id(children_id)
            if not children or children.role != "user":
                return None
            
            # 更新用户资料
            for key, value in kwargs.items():
                if hasattr(children, key):
                    # 不允许更新的字段
                    if key in ["id", "created_at", "role", "status"]:
                        continue
                    setattr(children, key, value)
            
            children.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(children)
            
            return children
        
        except Exception as e:
            self.db.rollback()
            print(f"Error updating children profile: {e}")
            return None
    
    def search_children_by_phone_or_name(self, phone_number: Optional[str] = None,
                                       name: Optional[str] = None) -> List[User]:
        """根据手机号或姓名搜索子女用户"""
        try:
            query = self.db.query(User).filter(User.role == "user")
            
            # 手机号搜索
            if phone_number:
                query = query.filter(User.phone_number.like(f"%{phone_number}%"))
            
            # 姓名搜索
            if name:
                query = query.filter(User.username.like(f"%{name}%"))
            
            # 如果两个条件都没有，返回空列表
            if not phone_number and not name:
                return []
            
            return query.limit(10).all()
        
        except Exception as e:
            print(f"Error searching children: {e}")
            return []
    
    def get_children_activity_stats(self, children_id: uuid.UUID) -> Dict[str, Any]:
        """获取子女的活动统计信息"""
        stats = {
            "last_login": None,
            "login_count_7d": 0,
            "view_elderly_count_7d": 0,
            "created_reminders_7d": 0,
            "responded_alerts_7d": 0
        }
        
        try:
            # 获取子女信息
            children = self.get_by_id(children_id)
            if children:
                stats["last_login"] = children.last_login
            
            # 这里可以根据实际情况添加更多的活动统计
            # 例如登录次数、查看老人次数、创建提醒次数等
            # 由于没有这些活动记录的表，这里只是示例
            
            return stats
        
        except Exception as e:
            print(f"Error getting children activity stats: {e}")
            return stats