"""用户相关的Repository类"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import uuid

from repositories.base import BaseRepository
from database.models import User, UserStatus, ElderlyProfile, ChildrenProfile, CommunityProfile


class UserRepository(BaseRepository[User]):
    """用户数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """根据手机号获取用户"""
        return self.get_one(phone_number=phone_number)
    
    def get_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """根据角色获取用户列表"""
        try:
            return self.db.query(User).filter(
                User.role == role
            ).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error getting users by role: {e}")
            return []
    
    def get_by_status(self, status: UserStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """根据状态获取用户列表"""
        try:
            return self.db.query(User).filter(
                User.status == status
            ).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error getting users by status: {e}")
            return []
    
    def update_status(self, user_id: uuid.UUID, status: UserStatus) -> Optional[User]:
        """更新用户状态"""
        user = self.get_by_id(user_id)
        if user:
            return self.update(user, {"status": status})
        return None
    
    def update_password(self, user_id: uuid.UUID, password_hash: str) -> Optional[User]:
        """更新用户密码"""
        user = self.get_by_id(user_id)
        if user:
            return self.update(user, {"password_hash": password_hash})
        return None
    
    def get_with_profile(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """获取用户及其关联的档案信息"""
        user = self.get_by_id(user_id)
        if not user:
            return {"user": None, "profile": None}
        
        profile = None
        
        # 根据用户角色获取对应档案
        if user.role == "elderly":
            profile = self.db.query(ElderlyProfile).filter(
                ElderlyProfile.user_id == user_id
            ).first()
        elif user.role == "children":
            profile = self.db.query(ChildrenProfile).filter(
                ChildrenProfile.user_id == user_id
            ).first()
        elif user.role == "community":
            profile = self.db.query(CommunityProfile).filter(
                CommunityProfile.user_id == user_id
            ).first()
        
        return {"user": user, "profile": profile}
    
    def search_users(self, keyword: str, role: Optional[str] = None, 
                    skip: int = 0, limit: int = 100) -> List[User]:
        """搜索用户（根据手机号或角色）"""
        try:
            query = self.db.query(User)
            
            if keyword:
                query = query.filter(User.phone_number.like(f"%{keyword}%"))
            
            if role:
                query = query.filter(User.role == role)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    def create_user_with_profile(self, user_data: Dict[str, Any], 
                               profile_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建用户及其关联档案"""
        try:
            # 创建用户
            user = self.create(user_data)
            if not user:
                return {"success": False, "message": "用户创建失败"}
            
            # 创建关联档案
            profile = None
            if profile_data and user.role in ["elderly", "children", "community"]:
                profile_data["user_id"] = user.id
                
                if user.role == "elderly":
                    profile = ElderlyProfile(**profile_data)
                elif user.role == "children":
                    profile = ChildrenProfile(**profile_data)
                elif user.role == "community":
                    profile = CommunityUserProfile(**profile_data)
                
                self.db.add(profile)
                self.db.commit()
                self.db.refresh(profile)
            
            return {"success": True, "user": user, "profile": profile}
        
        except Exception as e:
            self.db.rollback()
            print(f"Error creating user with profile: {e}")
            return {"success": False, "message": str(e)}
    
    def check_phone_number_exists(self, phone_number: str, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """检查手机号是否已存在"""
        try:
            query = self.db.query(User).filter(User.phone_number == phone_number)
            
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
            
            return query.first() is not None
        except Exception as e:
            print(f"Error checking phone number existence: {e}")
            return False