"""获取当前用户的依赖注入"""
from typing import Optional, Union, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import logging

from config.settings import settings
from database.database import get_db
from database.models import User
from schemas.models import UserResponse, ElderlyResponse, ChildrenResponse
from utils.password_utils import JWTUtils
from repositories.user_repository import UserRepository

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建OAuth2密码Bearer实例
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        User: 用户模型实例
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证JWT令牌
        payload = JWTUtils.decode_token(token)
        if payload is None:
            raise credentials_exception
        
        # 获取用户ID（UUID 字符串）
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except (JWTError, ValueError) as e:
        logger.warning(f"JWT令牌验证失败: {token}, 错误: {e}")
        raise credentials_exception
    
    # 查询用户（user_id 是 UUID 字符串）
    import uuid
    user_repo = UserRepository(db)
    try:
        user_uuid = uuid.UUID(user_id_str)
        user = user_repo.get_by_id(user_uuid)
    except ValueError:
        logger.warning(f"无效的用户ID格式: {user_id_str}")
        raise credentials_exception
    
    if user is None:
        logger.warning(f"用户不存在: {user_id_str}")
        raise credentials_exception
    
    # 检查用户状态（使用 status 枚举字段）
    from database.models import UserStatus
    if user.status != UserStatus.ACTIVE:
        logger.warning(f"用户已被禁用: {user_id_str}, 状态: {user.status}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用"
        )
    
    return user


# 直接定义角色检查函数
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

async def get_community_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "community_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或社区管理员权限"
        )
    return current_user

async def get_elderly_or_children_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["elderly", "children"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要老人或子女权限"
        )
    return current_user

async def get_any_user(current_user: User = Depends(get_current_user)):
    # 所有已登录用户都可以访问
    return current_user

# 社区管理员或更高权限的用户
async def get_community_admin_or_higher(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "community_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或社区管理员权限"
        )
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 活跃用户
        
    Raises:
        HTTPException: 用户未激活时抛出
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号未激活"
        )
    return current_user


async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Union[UserResponse, ElderlyResponse, ChildrenResponse]:
    """获取当前用户的详细信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        Union[UserResponse, ElderlyResponse, ChildrenResponse]: 用户详细信息
    """
    from schemas.models import UserResponse, ElderlyResponse, ChildrenResponse
    
    # 根据用户角色返回不同的用户信息
    if current_user.role == "elderly" and current_user.elderly_profile:
        return ElderlyResponse(
            id=current_user.id,
            phone_number=current_user.phone_number,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            elderly_id=current_user.elderly_profile.id,
            name=current_user.elderly_profile.name,
            gender=current_user.elderly_profile.gender,
            birth_date=current_user.elderly_profile.birth_date,
            id_card=current_user.elderly_profile.id_card,
            address=current_user.elderly_profile.address,
            emergency_contact=current_user.elderly_profile.emergency_contact,
            emergency_phone=current_user.elderly_profile.emergency_phone,
            health_status=current_user.elderly_profile.health_status,
            profile_image=current_user.elderly_profile.profile_image
        )
    elif current_user.role == "children" and current_user.children_profile:
        return ChildrenResponse(
            id=current_user.id,
            phone_number=current_user.phone_number,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            children_id=current_user.children_profile.id,
            name=current_user.children_profile.name,
            gender=current_user.children_profile.gender,
            id_card=current_user.children_profile.id_card,
            profile_image=current_user.children_profile.profile_image
        )
    else:
        # 管理员或普通用户
        return UserResponse(
            id=current_user.id,
            phone_number=current_user.phone_number,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            username=current_user.username
        )


# 移除不再需要的角色检查器实例和依赖定义


async def get_elderly_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取老年人用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 老年人用户
        
    Raises:
        HTTPException: 不是老年人用户时抛出
    """
    if current_user.role != "elderly" or not current_user.elderly_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅老年人用户可访问"
        )
    return current_user


async def get_children_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取子女用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 子女用户
        
    Raises:
        HTTPException: 不是子女用户时抛出
    """
    if current_user.role != "children" or not current_user.children_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅子女用户可访问"
        )
    return current_user


async def get_admin_or_community_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取管理员或社区管理员
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 管理员或社区管理员
        
    Raises:
        HTTPException: 权限不足时抛出
    """
    if current_user.role not in ["admin", "community_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

# 获取社区管理员或更高权限的用户
async def get_community_admin_or_higher(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取社区管理员或更高权限的用户
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        User: 社区管理员或更高权限的用户
        
    Raises:
        HTTPException: 权限不足
    """
    if current_user.role not in ["admin", "community_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或社区管理员权限"
        )
    return current_user


async def get_elderly_or_caretaker(
    elderly_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """获取老年人本人或其子女/监护人
    
    Args:
        elderly_id: 老年人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        User: 符合条件的用户
        
    Raises:
        HTTPException: 无权限访问时抛出
    """
    # 检查是否是老年人本人
    if current_user.role == "elderly" and current_user.elderly_profile and current_user.elderly_profile.id == elderly_id:
        return current_user
    
    # 检查是否是管理员或社区管理员
    if current_user.role in ["admin", "community_admin"]:
        return current_user
    
    # 检查是否是子女/监护人
    if current_user.role == "children" and current_user.children_profile:
        # 查询子女与老年人的关系
        from database.models import ChildrenElderlyRelation
        relation = db.query(ChildrenElderlyRelation).filter(
            ChildrenElderlyRelation.children_id == current_user.children_profile.id,
            ChildrenElderlyRelation.elderly_id == elderly_id
        ).first()
        
        if relation:
            return current_user
    
    # 无权限访问
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权访问该老年人信息"
    )