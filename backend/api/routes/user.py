"""用户相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from database.database import get_db
from database.models import User
from schemas.models import (
    UserCreate, UserUpdate, UserResponse, LoginResponse,
    UserRole, UserStatus, TokenData
)
from dependencies.get_current_user import get_current_user
from repositories.user_repository import UserRepository
from utils.password_utils import PasswordUtils, JWTUtils, TokenManager
from utils.common_utils import ResponseUtils, ValidationUtils
from middlewares.error_middleware import BusinessError

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/register", response_model=dict)
async def user_register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> dict:
    """用户注册
    
    支持不同角色的用户注册：普通用户（老人）、子女、社区管理员
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        dict: 注册成功的响应
    """
    try:
        # 验证手机号
        if not ValidationUtils.validate_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号格式不正确"
            )
        
        # 验证身份证号
        if user_data.id_card and not ValidationUtils.validate_id_card(user_data.id_card):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="身份证号格式不正确"
            )
        
        # 检查手机号是否已注册
        user_repo = UserRepository(db)
        if user_repo.get_user_by_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已注册"
            )
        
        # 检查用户名是否已存在
        if user_repo.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 验证密码强度
        if not PasswordUtils.validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码强度不足，需包含数字和字母，长度至少8位"
            )
        
        # 哈希密码
        hashed_password = PasswordUtils.hash_password(user_data.password)
        
        # 创建用户
        user = user_repo.create_user(
            username=user_data.username,
            password=hashed_password,
            phone=user_data.phone,
            role=user_data.role,
            id_card=user_data.id_card,
            name=user_data.name,
            avatar=user_data.avatar
        )
        
        return ResponseUtils.success_response(
            message="注册成功",
            data=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=dict)
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict:
    """用户登录
    
    支持使用用户名或手机号登录
    
    Args:
        form_data: OAuth2登录表单数据
        db: 数据库会话
        
    Returns:
        dict: 包含访问令牌和用户信息的响应
    """
    try:
        # 尝试通过手机号或用户名查找用户
        user_repo = UserRepository(db)
        
        # 检查是手机号还是用户名
        if ValidationUtils.validate_phone(form_data.username):
            user = user_repo.get_user_by_phone(form_data.username)
        else:
            user = user_repo.get_user_by_username(form_data.username)
        
        # 验证用户和密码
        if not user or not PasswordUtils.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账号已被禁用，请联系管理员"
            )
        
        # 生成访问令牌和刷新令牌
        access_token = TokenManager.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        refresh_token = TokenManager.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # 构建响应
        return ResponseUtils.success_response(
            data=LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserResponse.from_orm(user)
            ),
            message="登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> dict:
    """刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        db: 数据库会话
        
    Returns:
        dict: 包含新访问令牌的响应
    """
    try:
        # 验证刷新令牌
        payload = JWTUtils.decode_token(refresh_token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload["sub"]
        
        # 查找用户
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账号已被禁用，请联系管理员"
            )
        
        # 生成新的访问令牌
        new_access_token = TokenManager.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        
        return ResponseUtils.success_response(
            data={
                "access_token": new_access_token,
                "token_type": "bearer"
            },
            message="令牌刷新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌失败，请稍后重试"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> dict:
    """获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 当前用户信息
    """
    try:
        return ResponseUtils.success_response(
            data=UserResponse.from_orm(current_user)
        )
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败，请稍后重试"
        )


@router.put("/me", response_model=dict)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新当前用户信息
    
    Args:
        user_data: 用户更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 验证输入数据
        update_data = user_data.dict(exclude_unset=True)
        
        # 检查手机号是否被其他用户使用
        if "phone" in update_data:
            if not ValidationUtils.validate_phone(update_data["phone"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号格式不正确"
                )
            
            user_repo = UserRepository(db)
            existing_user = user_repo.get_user_by_phone(update_data["phone"])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被其他用户使用"
                )
        
        # 更新密码时的处理
        if "password" in update_data:
            if not PasswordUtils.validate_password_strength(update_data["password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码强度不足，需包含数字和字母，长度至少8位"
                )
            update_data["password"] = PasswordUtils.hash_password(update_data["password"])
        
        # 更新用户信息
        user_repo = UserRepository(db)
        updated_user = user_repo.update_user(current_user.id, **update_data)
        
        return ResponseUtils.success_response(
            data=UserResponse.from_orm(updated_user),
            message="用户信息更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败，请稍后重试"
        )


@router.put("/me/avatar", response_model=dict)
async def update_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新用户头像
    
    Args:
        avatar_url: 头像URL
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        user_repo = UserRepository(db)
        updated_user = user_repo.update_user(current_user.id, avatar=avatar_url)
        
        return ResponseUtils.success_response(
            data=UserResponse.from_orm(updated_user),
            message="头像更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新头像失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新头像失败，请稍后重试"
        )


@router.post("/change-password", response_model=dict)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """修改密码
    
    Args:
        old_password: 原密码
        new_password: 新密码
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 修改成功的响应
    """
    try:
        # 验证原密码
        if not PasswordUtils.verify_password(old_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        # 验证新密码强度
        if not PasswordUtils.validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码强度不足，需包含数字和字母，长度至少8位"
            )
        
        # 哈希新密码并更新
        user_repo = UserRepository(db)
        hashed_new_password = PasswordUtils.hash_password(new_password)
        user_repo.update_user(current_user.id, password=hashed_new_password)
        
        return ResponseUtils.success_response(
            message="密码修改成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后重试"
        )


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user)
) -> dict:
    """用户登出
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 登出成功的响应
    """
    try:
        # 在实际应用中，可以将令牌添加到黑名单中
        # 这里简单返回成功消息
        return ResponseUtils.success_response(
            message="登出成功"
        )
        
    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败，请稍后重试"
        )