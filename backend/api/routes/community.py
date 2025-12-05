"""社区管理相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database.database import get_db
from database.models import User
from schemas.models import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    CommunityMemberResponse, CommunityAdminResponse
)
from dependencies.get_current_user import (
    get_current_user, get_admin_user, get_community_admin_or_higher
)
from repositories.community_repository import CommunityRepository
from repositories.elderly_repository import ElderlyRepository
from repositories.user_repository import UserRepository
from utils.common_utils import ResponseUtils, DataUtils
from middlewares.error_middleware import BusinessError

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器（仅资源前缀，版本和 /api 在 main.py 统一处理）
router = APIRouter(prefix="/communities", tags=["communities"])


@router.post("", response_model=dict)
async def create_community(
    community_data: CommunityCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """创建社区
    
    仅管理员可创建社区
    
    Args:
        community_data: 社区数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 创建成功的响应
    """
    try:
        # 创建社区
        community_repo = CommunityRepository(db)
        
        # 检查社区名称是否已存在
        if community_repo.check_community_name_exists(community_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="社区名称已存在"
            )
        
        # 创建社区
        community = community_repo.create_community(
            created_by=current_user.id,
            **community_data.dict()
        )
        
        return ResponseUtils.success_response(
            data=CommunityResponse.from_orm(community),
            message="社区创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建社区失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建社区失败，请稍后重试"
        )


@router.get("", response_model=dict)
async def get_communities(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    name: Optional[str] = Query(None, description="社区名称关键字"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取社区列表
    
    所有登录用户均可访问
    
    Args:
        page: 页码
        size: 每页大小
        name: 社区名称关键字
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 分页社区列表
    """
    try:
        # 格式化分页参数
        page, size = DataUtils.format_pagination_params(page, size)
        
        # 查询社区列表
        community_repo = CommunityRepository(db)
        communities, total = community_repo.get_communities(
            page=page,
            size=size,
            name=name
        )
        
        # 构建响应数据
        items = [CommunityResponse.from_orm(community) for community in communities]
        
        return ResponseUtils.pagination_response(
            data=items,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"获取社区列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取社区列表失败，请稍后重试"
        )


@router.get("/{community_id}", response_model=dict)
async def get_community_detail(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取社区详情
    
    所有登录用户均可访问
    
    Args:
        community_id: 社区ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 社区详情
    """
    try:
        # 获取社区详情
        community_repo = CommunityRepository(db)
        community = community_repo.get_community_detail(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        # 补充统计信息
        stats = community_repo.get_community_statistics(community_id)
        
        # 构建响应数据
        response_data = CommunityResponse.from_orm(community)
        response_data.total_elderly = stats.get("total_elderly", 0)
        response_data.total_children = stats.get("total_children", 0)
        response_data.total_admins = stats.get("total_admins", 0)
        
        return ResponseUtils.success_response(
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取社区详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取社区详情失败，请稍后重试"
        )


@router.put("/{community_id}", response_model=dict)
async def update_community(
    community_id: int,
    community_data: CommunityUpdate,
    current_user: User = Depends(get_community_admin_or_higher),
    db: Session = Depends(get_db)
) -> dict:
    """更新社区信息
    
    管理员和社区管理员可更新
    
    Args:
        community_id: 社区ID
        community_data: 更新的社区数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 检查社区是否存在
        community_repo = CommunityRepository(db)
        community = community_repo.get_by_id(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        # 检查权限（社区管理员只能更新自己管理的社区）
        if current_user.role == "community_admin":
            if not community_repo.is_community_admin(current_user.id, community_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权更新此社区"
                )
        
        # 如果更新名称，检查是否已存在
        if community_data.name and community_data.name != community.name:
            if community_repo.check_community_name_exists(community_data.name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="社区名称已存在"
                )
        
        # 更新社区
        updated_community = community_repo.update_community(
            community_id=community_id,
            **community_data.dict(exclude_unset=True)
        )
        
        return ResponseUtils.success_response(
            data=CommunityResponse.from_orm(updated_community),
            message="社区信息更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新社区失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新社区失败，请稍后重试"
        )


@router.get("/{community_id}/elderly", response_model=dict)
async def get_community_elderly(
    community_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取社区老人列表
    
    所有登录用户均可访问
    
    Args:
        community_id: 社区ID
        page: 页码
        size: 每页大小
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 分页老人列表
    """
    try:
        # 验证社区是否存在
        community_repo = CommunityRepository(db)
        community = community_repo.get_by_id(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        # 格式化分页参数
        page, size = DataUtils.format_pagination_params(page, size)
        
        # 获取社区老人列表
        elderly_list, total = community_repo.get_community_elderly(
            community_id=community_id,
            page=page,
            size=size
        )
        
        # 构建响应数据
        items = [CommunityMemberResponse.from_orm(elderly) for elderly in elderly_list]
        
        return ResponseUtils.pagination_response(
            data=items,
            total=total,
            page=page,
            size=size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取社区老人列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取社区老人列表失败，请稍后重试"
        )


@router.post("/{community_id}/admins", response_model=dict)
async def add_community_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """添加社区管理员
    
    仅管理员可添加
    
    Args:
        community_id: 社区ID
        user_id: 用户ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作成功的响应
    """
    try:
        # 验证社区和用户是否存在
        community_repo = CommunityRepository(db)
        community = community_repo.get_by_id(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查是否已经是社区管理员
        if community_repo.is_community_admin(user_id, community_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户已经是社区管理员"
            )
        
        # 添加社区管理员
        community_repo.add_community_admin(
            community_id=community_id,
            user_id=user_id
        )
        
        # 更新用户角色为社区管理员
        user_repo.update_user_role(user_id, "community_admin")
        
        return ResponseUtils.success_response(
            message="社区管理员添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加社区管理员失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加社区管理员失败，请稍后重试"
        )


@router.delete("/{community_id}/admins/{user_id}", response_model=dict)
async def remove_community_admin(
    community_id: int,
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """移除社区管理员
    
    仅管理员可移除
    
    Args:
        community_id: 社区ID
        user_id: 用户ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作成功的响应
    """
    try:
        # 验证社区是否存在
        community_repo = CommunityRepository(db)
        community = community_repo.get_by_id(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        # 检查是否是社区管理员
        if not community_repo.is_community_admin(user_id, community_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户不是社区管理员"
            )
        
        # 移除社区管理员
        community_repo.remove_community_admin(
            community_id=community_id,
            user_id=user_id
        )
        
        # 检查用户是否还是其他社区的管理员，如果不是则更新角色
        if not community_repo.is_admin_of_any_community(user_id):
            user_repo = UserRepository(db)
            user_repo.update_user_role(user_id, "children")  # 默认为子女角色
        
        return ResponseUtils.success_response(
            message="社区管理员移除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除社区管理员失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除社区管理员失败，请稍后重试"
        )


@router.get("/{community_id}/admins", response_model=dict)
async def get_community_admins(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取社区管理员列表
    
    所有登录用户均可访问
    
    Args:
        community_id: 社区ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 社区管理员列表
    """
    try:
        # 获取社区管理员列表
        community_repo = CommunityRepository(db)
        admins = community_repo.get_community_admins(community_id)
        
        # 构建响应数据
        items = [CommunityAdminResponse.from_orm(admin) for admin in admins]
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except Exception as e:
        logger.error(f"获取社区管理员列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取社区管理员列表失败，请稍后重试"
        )


@router.get("/{community_id}/statistics", response_model=dict)
async def get_community_statistics(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取社区统计信息
    
    所有登录用户均可访问
    
    Args:
        community_id: 社区ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 社区统计信息
    """
    try:
        # 验证社区是否存在
        community_repo = CommunityRepository(db)
        community = community_repo.get_by_id(community_id)
        
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社区不存在"
            )
        
        # 获取社区统计信息
        stats = community_repo.get_community_statistics(community_id)
        
        return ResponseUtils.success_response(
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取社区统计信息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取社区统计信息失败，请稍后重试"
        )