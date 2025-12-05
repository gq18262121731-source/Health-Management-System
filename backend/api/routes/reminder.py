"""提醒管理相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from database.database import get_db
from database.models import User
from schemas.models import (
    ReminderCreate, ReminderUpdate, ReminderResponse,
    ReminderStatusUpdate
)
from dependencies.get_current_user import (
    get_current_user, get_elderly_or_caretaker, get_elderly_user
)
from repositories.reminder_repository import ReminderRepository
from repositories.elderly_repository import ElderlyRepository
from repositories.children_repository import ChildrenRepository
from utils.common_utils import ResponseUtils, DataUtils

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.post("/elderly/{elderly_id}", response_model=dict)
async def create_reminder(
    elderly_id: int,
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """创建提醒
    
    老人本人、子女、管理员和社区管理员可创建提醒
    
    Args:
        elderly_id: 老人ID
        reminder_data: 提醒数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 创建成功的响应
    """
    try:
        # 验证老人是否存在
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 创建提醒
        reminder_repo = ReminderRepository(db)
        reminder = reminder_repo.create_reminder(
            elderly_id=elderly_id,
            created_by=current_user.id,
            **reminder_data.dict()
        )
        
        # 如果是重复提醒，创建多次提醒
        if reminder_data.is_recurring and reminder_data.recurrence_pattern:
            reminder_repo.create_recurring_reminders(
                base_reminder=reminder,
                recurrence_pattern=reminder_data.recurrence_pattern,
                times=reminder_data.recurrence_times or 5  # 默认创建5次
            )
        
        return ResponseUtils.success_response(
            data=ReminderResponse.from_orm(reminder),
            message="提醒创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建提醒失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}", response_model=dict)
async def get_elderly_reminders(
    elderly_id: int,
    date: Optional[datetime] = Query(None, description="查询日期，默认为今天"),
    status: Optional[str] = Query(None, description="提醒状态：pending/completed"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人提醒列表
    
    老人本人、子女、管理员和社区管理员可访问
    
    Args:
        elderly_id: 老人ID
        date: 查询日期，默认为今天
        status: 提醒状态：pending/completed
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 提醒列表
    """
    try:
        # 验证老人是否存在
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 如果没有提供日期，使用今天
        if not date:
            date = datetime.now()
        
        # 获取当天的开始和结束时间
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())
        
        # 查询提醒列表
        reminder_repo = ReminderRepository(db)
        reminders = reminder_repo.get_reminders_by_elderly(
            elderly_id=elderly_id,
            start_time=start_of_day,
            end_time=end_of_day,
            status=status
        )
        
        # 构建响应数据
        items = [ReminderResponse.from_orm(reminder) for reminder in reminders]
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取提醒列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取提醒列表失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/today", response_model=dict)
async def get_today_reminders(
    elderly_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人今日提醒
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 今日提醒列表
    """
    try:
        # 获取今日提醒
        reminder_repo = ReminderRepository(db)
        reminders = reminder_repo.get_today_reminders(elderly_id)
        
        # 构建响应数据
        items = [ReminderResponse.from_orm(reminder) for reminder in reminders]
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except Exception as e:
        logger.error(f"获取今日提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取今日提醒失败，请稍后重试"
        )


@router.get("/{reminder_id}", response_model=dict)
async def get_reminder_detail(
    reminder_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取提醒详情
    
    Args:
        reminder_id: 提醒ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 提醒详情
    """
    try:
        # 获取提醒详情
        reminder_repo = ReminderRepository(db)
        reminder = reminder_repo.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提醒不存在"
            )
        
        return ResponseUtils.success_response(
            data=ReminderResponse.from_orm(reminder)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取提醒详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取提醒详情失败，请稍后重试"
        )


@router.put("/{reminder_id}", response_model=dict)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """更新提醒
    
    Args:
        reminder_id: 提醒ID
        reminder_data: 更新的提醒数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 更新提醒
        reminder_repo = ReminderRepository(db)
        reminder = reminder_repo.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提醒不存在"
            )
        
        # 检查是否是创建者或管理员
        if reminder.created_by != current_user.id and current_user.role not in ["admin", "community_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此提醒"
            )
        
        # 更新提醒
        updated_reminder = reminder_repo.update_reminder(
            reminder_id=reminder_id,
            **reminder_data.dict(exclude_unset=True)
        )
        
        return ResponseUtils.success_response(
            data=ReminderResponse.from_orm(updated_reminder),
            message="提醒更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新提醒失败，请稍后重试"
        )


@router.delete("/{reminder_id}", response_model=dict)
async def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """删除提醒
    
    Args:
        reminder_id: 提醒ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 删除成功的响应
    """
    try:
        # 删除提醒
        reminder_repo = ReminderRepository(db)
        reminder = reminder_repo.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提醒不存在"
            )
        
        # 检查是否是创建者或管理员
        if reminder.created_by != current_user.id and current_user.role not in ["admin", "community_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此提醒"
            )
        
        # 删除提醒
        reminder_repo.delete_reminder(reminder_id)
        
        return ResponseUtils.success_response(
            message="提醒删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除提醒失败，请稍后重试"
        )


@router.put("/{reminder_id}/status", response_model=dict)
async def update_reminder_status(
    reminder_id: int,
    status_update: ReminderStatusUpdate,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """更新提醒状态
    
    Args:
        reminder_id: 提醒ID
        status_update: 状态更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 更新提醒状态
        reminder_repo = ReminderRepository(db)
        reminder = reminder_repo.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提醒不存在"
            )
        
        # 更新状态
        updated_reminder = reminder_repo.update_reminder_status(
            reminder_id=reminder_id,
            status=status_update.status,
            completed_time=datetime.now() if status_update.status == "completed" else None
        )
        
        return ResponseUtils.success_response(
            data=ReminderResponse.from_orm(updated_reminder),
            message="提醒状态更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新提醒状态失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新提醒状态失败，请稍后重试"
        )


@router.get("/statistics/elderly/{elderly_id}", response_model=dict)
async def get_reminder_statistics(
    elderly_id: int,
    days: int = Query(7, ge=1, le=30, description="统计天数，默认为7天"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取提醒统计信息
    
    Args:
        elderly_id: 老人ID
        days: 统计天数，默认为7天
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 提醒统计信息
    """
    try:
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取提醒统计
        reminder_repo = ReminderRepository(db)
        stats = reminder_repo.get_reminder_statistics(
            elderly_id=elderly_id,
            start_time=start_date,
            end_time=end_date
        )
        
        return ResponseUtils.success_response(
            data=stats
        )
        
    except Exception as e:
        logger.error(f"获取提醒统计失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取提醒统计失败，请稍后重试"
        )