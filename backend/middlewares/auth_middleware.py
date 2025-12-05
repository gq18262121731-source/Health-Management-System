"""认证和权限管理中间件"""
from typing import Optional, List, Set
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uuid

from config.settings import settings
from database.database import get_db
from repositories.user_repository import UserRepository
from repositories.community_repository import CommunityRepository

# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthMiddleware:
    """认证中间件类"""
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """验证 JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = AuthMiddleware.verify_token(token)
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            
            # 获取用户信息
            user_repo = UserRepository(db)
            user = user_repo.get_by_id(uuid.UUID(user_id))
            
            if user is None:
                raise credentials_exception
            
            # 检查用户状态
            if user.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户账号已被禁用"
                )
            
            return user
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    async def get_current_active_user(current_user = Depends(get_current_user)):
        """获取当前活跃用户"""
        if current_user.status != "active":
            raise HTTPException(status_code=400, detail="用户账号未激活")
        return current_user


class RoleChecker:
    """角色检查器"""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user = Depends(AuthMiddleware.get_current_active_user)):
        if current_user.role in self.allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法访问此资源"
        )


class PermissionChecker:
    """权限检查器"""
    
    @staticmethod
    async def check_elderly_access(current_user, elderly_id: uuid.UUID, db: Session) -> bool:
        """检查用户是否有权限访问指定老人的信息"""
        # 超级管理员和社区管理员可以访问所有老人
        if current_user.role in ["super_admin", "community_admin"]:
            return True
        
        # 检查是否是该老人的子女
        from repositories.children_repository import ChildrenRepository
        children_repo = ChildrenRepository(db)
        
        # 获取子女关联的老人列表
        elderly_list = children_repo.get_children_elderly_list(current_user.id)
        
        # 检查是否在列表中
        for item in elderly_list:
            if item["elderly"].id == elderly_id:
                return True
        
        return False
    
    @staticmethod
    async def check_community_access(current_user, community_id: uuid.UUID, db: Session) -> bool:
        """检查用户是否有权限访问指定社区"""
        # 超级管理员可以访问所有社区
        if current_user.role == "super_admin":
            return True
        
        # 检查是否是该社区的管理员
        community_repo = CommunityRepository(db)
        return community_repo.check_admin_permission(community_id, current_user.id)


# 角色依赖
super_admin_role = RoleChecker(["super_admin"])
community_admin_role = RoleChecker(["super_admin", "community_admin"])
user_role = RoleChecker(["super_admin", "community_admin", "user"])


async def get_elderly_access(elderly_id: uuid.UUID, 
                           current_user = Depends(user_role),
                           db: Session = Depends(get_db)):
    """获取老人访问权限"""
    has_access = await PermissionChecker.check_elderly_access(current_user, elderly_id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法访问此老人信息"
        )
    return current_user


async def get_community_access(community_id: uuid.UUID,
                             current_user = Depends(community_admin_role),
                             db: Session = Depends(get_db)):
    """获取社区访问权限"""
    has_access = await PermissionChecker.check_community_access(current_user, community_id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法访问此社区信息"
        )
    return current_user


def role_required(roles: List[str]):
    """角色要求装饰器"""
    async def role_checker(current_user = Depends(AuthMiddleware.get_current_active_user)):
        if current_user.role in roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要特定角色访问此资源"
        )
    return role_checker