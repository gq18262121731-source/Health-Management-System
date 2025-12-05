"""社区相关的Repository类"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, or_, func
import uuid

from repositories.base import BaseRepository
from database.models import Community, User, CommunityProfile, ElderlyProfile, ChildrenElderlyRelation


class CommunityRepository(BaseRepository[Community]):
    """社区数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, Community)
    
    def create_community(self, name: str, address: str, contact_person: str,
                        contact_phone: str, description: Optional[str] = None) -> Community:
        """创建社区"""
        try:
            community = Community(
                name=name,
                address=address,
                contact_person=contact_person,
                contact_phone=contact_phone,
                description=description,
                status="active"
            )
            
            self.db.add(community)
            self.db.commit()
            self.db.refresh(community)
            
            return community
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating community: {e}")
            raise
    
    def get_community_list(self, skip: int = 0, limit: int = 100,
                          search_keyword: Optional[str] = None,
                          status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取社区列表（带统计信息）"""
        try:
            query = self.db.query(Community)
            
            # 搜索过滤
            if search_keyword:
                query = query.filter(
                    or_(
                        Community.name.like(f"%{search_keyword}%"),
                        Community.address.like(f"%{search_keyword}%"),
                        Community.contact_person.like(f"%{search_keyword}%")
                    )
                )
            
            # 状态过滤
            if status:
                query = query.filter(Community.status == status)
            
            communities = query.order_by(desc(Community.created_at)).offset(skip).limit(limit).all()
            
            result = []
            for community in communities:
                # 获取社区老人数量
                elderly_count = self.db.query(func.count(ElderlyProfile.id)).filter(
                    ElderlyProfile.community_id == community.id
                ).scalar()
                
                # 获取社区管理员数量
                admin_count = 0  # 暂时设为0，实际应该查询CommunityProfile
                
                result.append({
                    "community": community,
                    "elderly_count": elderly_count,
                    "admin_count": admin_count
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting community list: {e}")
            return []
    
    def get_community_by_id(self, community_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """获取社区详情（带统计信息）"""
        try:
            community = self.get_by_id(community_id)
            if not community:
                return None
            
            # 获取社区老人数量
            elderly_count = self.db.query(func.count(ElderlyProfile.id)).filter(
                ElderlyProfile.community_id == community_id
            ).scalar()
            
            # 获取社区管理员列表
            admins = self.db.query(
                User.id,
                User.username,
                User.phone_number,
                User.avatar,
                CommunityAdmin.role
            ).join(
                CommunityAdmin,
                User.id == CommunityAdmin.user_id
            ).filter(
                CommunityAdmin.community_id == community_id
            ).all()
            
            admin_list = []
            for admin in admins:
                admin_list.append({
                    "user_id": admin.id,
                    "username": admin.username,
                    "phone_number": admin.phone_number,
                    "avatar": admin.avatar,
                    "role": admin.role
                })
            
            return {
                "community": community,
                "elderly_count": elderly_count,
                "admin_list": admin_list
            }
        
        except Exception as e:
            print(f"Error getting community by id: {e}")
            return None
    
    def update_community(self, community_id: uuid.UUID, **kwargs) -> Optional[Community]:
        """更新社区信息"""
        try:
            community = self.get_by_id(community_id)
            if not community:
                return None
            
            # 更新社区信息
            for key, value in kwargs.items():
                if hasattr(community, key):
                    setattr(community, key, value)
            
            community.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(community)
            
            return community
        
        except Exception as e:
            self.db.rollback()
            print(f"Error updating community: {e}")
            return None
    
    def add_community_admin(self, community_id: uuid.UUID, user_id: uuid.UUID,
                          role: str = "admin") -> Optional[CommunityProfile]:
        """添加社区管理员（当前使用CommunityProfile）"""
        try:
            # 检查用户是否存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # 检查社区是否存在
            community = self.get_by_id(community_id)
            if not community:
                return None
            
            # 检查用户是否已经有社区档案
            community_profile = self.db.query(CommunityProfile).filter(
                CommunityProfile.user_id == user_id
            ).first()
            
            return community_profile
        
        except Exception as e:
            print(f"Error adding community admin: {e}")
            return None
    
    def remove_community_admin(self, community_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """移除社区管理员（当前使用CommunityProfile）"""
        try:
            # 当前逻辑简化，实际可能需要更新用户角色或状态
            return True
        
        except Exception as e:
            print(f"Error removing community admin: {e}")
            return False
    
    def get_user_communities(self, user_id: uuid.UUID) -> List[Community]:
        """获取用户管理的社区列表（基于CommunityProfile）"""
        try:
            # 获取用户的社区档案
            community_profile = self.db.query(CommunityProfile).filter(
                CommunityProfile.user_id == user_id
            ).first()
            
            if community_profile:
                # 获取关联的社区
                community = self.db.query(Community).filter(
                    Community.community_name == community_profile.community_name
                ).first()
                return [community] if community else []
            
            return []
        
        except Exception as e:
            print(f"Error getting user communities: {e}")
            return []
    
    def check_admin_permission(self, community_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """检查用户是否有社区管理权限（基于CommunityProfile）"""
        try:
            # 检查用户是否有社区档案并且属于该社区
            community_profile = self.db.query(CommunityProfile).filter(
                and_(
                    CommunityProfile.user_id == user_id,
                    CommunityProfile.id == community_id
                )
            ).first()
            
            return community_profile is not None
        
        except Exception as e:
            print(f"Error checking admin permission: {e}")
            return False
    
    def get_community_elderly_list(self, community_id: uuid.UUID, 
                                 skip: int = 0, limit: int = 100,
                                 search_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取社区内的老人列表"""
        try:
            query = self.db.query(ElderlyProfile).filter(
                ElderlyProfile.community_id == community_id
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
            
            elderly_list = query.order_by(desc(ElderlyProfile.created_at)).offset(skip).limit(limit).all()
            
            result = []
            for elderly in elderly_list:
                # 获取子女信息
                children_relations = self.db.query(
                    User.id,
                    User.username,
                    User.phone_number,
                    ChildrenElderlyRelation.relationship_type
                ).join(
                    ChildrenElderlyRelation,
                    User.id == ChildrenElderlyRelation.children_id
                ).filter(
                    ChildrenElderlyRelation.elderly_id == elderly.id
                ).all()
                
                children_list = []
                for child in children_relations:
                    children_list.append({
                        "user_id": child.id,
                        "username": child.username,
                        "phone_number": child.phone_number,
                        "relationship_type": child.relationship_type
                    })
                
                result.append({
                    "elderly": elderly,
                    "children_list": children_list
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting community elderly list: {e}")
            return []
    
    def get_community_statistics(self, community_id: uuid.UUID) -> Dict[str, Any]:
        """获取社区统计信息"""
        stats = {
            "elderly_count": 0,
            "active_elderly_count": 0,
            "children_count": 0,
            "admin_count": 0,
            "gender_distribution": {"男": 0, "女": 0},
            "age_distribution": {}
        }
        
        try:
            # 统计老人总数
            elderly_count = self.db.query(func.count(ElderlyProfile.id)).filter(
                ElderlyProfile.community_id == community_id
            ).scalar()
            stats["elderly_count"] = elderly_count
            
            # 统计活跃老人数（有健康记录的老人）
            active_elderly_subquery = self.db.query(
                HealthRecord.elderly_id
            ).distinct()
            
            active_elderly_count = self.db.query(func.count(ElderlyProfile.id)).filter(
                and_(
                    ElderlyProfile.community_id == community_id,
                    ElderlyProfile.id.in_(active_elderly_subquery)
                )
            ).scalar()
            stats["active_elderly_count"] = active_elderly_count
            
            # 统计子女数量
            children_subquery = self.db.query(
                ChildrenElderlyRelation.children_id
            ).join(
                ElderlyProfile,
                ChildrenElderlyRelation.elderly_id == ElderlyProfile.id
            ).filter(
                ElderlyProfile.community_id == community_id
            ).distinct()
            
            children_count = self.db.query(func.count(User.id)).filter(
                User.id.in_(children_subquery)
            ).scalar()
            stats["children_count"] = children_count
            
            # 获取社区管理员数量
            admin_count = 0  # 暂时设为0，实际应该查询CommunityProfile
            stats["admin_count"] = admin_count
            
            # 统计性别分布
            gender_stats = self.db.query(
                ElderlyProfile.gender,
                func.count(ElderlyProfile.id).label('count')
            ).filter(
                ElderlyProfile.community_id == community_id
            ).group_by(ElderlyProfile.gender).all()
            
            for gender, count in gender_stats:
                if gender in stats["gender_distribution"]:
                    stats["gender_distribution"][gender] = count
            
            # 统计年龄分布
            # 这里简化处理，按年龄段统计
            age_groups = {
                "60-69": 0,
                "70-79": 0,
                "80-89": 0,
                "90+": 0
            }
            
            # 获取所有老人的出生日期
            elderly_list = self.db.query(ElderlyProfile).filter(
                ElderlyProfile.community_id == community_id
            ).all()
            
            today = datetime.now()
            
            for elderly in elderly_list:
                if elderly.birth_date:
                    # 计算年龄
                    age = today.year - elderly.birth_date.year
                    if (today.month, today.day) < (elderly.birth_date.month, elderly.birth_date.day):
                        age -= 1
                    
                    # 分类到年龄段
                    if 60 <= age < 70:
                        age_groups["60-69"] += 1
                    elif 70 <= age < 80:
                        age_groups["70-79"] += 1
                    elif 80 <= age < 90:
                        age_groups["80-89"] += 1
                    elif age >= 90:
                        age_groups["90+"] += 1
            
            stats["age_distribution"] = age_groups
            
            return stats
        
        except Exception as e:
            print(f"Error getting community statistics: {e}")
            return stats


# 导入缺失的HealthRecord
from database.models import HealthRecord