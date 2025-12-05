"""子女相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database.database import get_db
from database.models import User
from schemas.models import (
    ChildrenProfileCreate, ChildrenProfileUpdate, ChildrenProfileResponse,
    ChildrenElderlyRelationCreate, ElderlyWithStatsResponse,
    # 新增子女端模型
    ElderListResponse, ElderInfo, ElderVitalSigns,
    ElderDetailResponse, ElderDetailData,
    RealtimeMonitorResponse, RealtimeMonitorData,
    ReminderCreate, ReminderCreateResponse, ReminderData
)
from dependencies.get_current_user import (
    get_current_user, get_children_user, get_elderly_or_caretaker
)
from repositories.children_repository import ChildrenRepository
from repositories.user_repository import UserRepository
from repositories.elderly_repository import ElderlyRepository
from utils.common_utils import ResponseUtils, DataUtils
from middlewares.error_middleware import BusinessError

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器（前缀在 main.py 统一设置为 /api/v1/children）
router = APIRouter(tags=["children"])


@router.post("/profile", response_model=dict)
async def create_children_profile(
    profile_data: ChildrenProfileCreate,
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """创建子女档案
    
    仅子女用户可创建
    
    Args:
        profile_data: 子女档案数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 创建成功的响应
    """
    try:
        # 检查是否已存在档案
        children_repo = ChildrenRepository(db)
        existing_profile = children_repo.get_profile_by_user_id(current_user.id)
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已创建过子女档案"
            )
        
        # 创建子女档案
        profile = children_repo.create_children_profile(
            user_id=current_user.id,
            **profile_data.dict()
        )
        
        return ResponseUtils.success_response(
            data=ChildrenProfileResponse.from_orm(profile),
            message="子女档案创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建子女档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建子女档案失败，请稍后重试"
        )


@router.get("/profile", response_model=dict)
async def get_children_profile(
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取子女档案
    
    仅子女用户可访问
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 子女档案
    """
    try:
        # 获取子女档案
        children_repo = ChildrenRepository(db)
        profile = children_repo.get_profile_by_user_id(current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="子女档案不存在，请先创建档案"
            )
        
        return ResponseUtils.success_response(
            data=ChildrenProfileResponse.from_orm(profile)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取子女档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取子女档案失败，请稍后重试"
        )


@router.put("/profile", response_model=dict)
async def update_children_profile(
    profile_data: ChildrenProfileUpdate,
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新子女档案
    
    仅子女用户可更新
    
    Args:
        profile_data: 更新的子女档案数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 获取子女档案
        children_repo = ChildrenRepository(db)
        profile = children_repo.get_profile_by_user_id(current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="子女档案不存在，请先创建档案"
            )
        
        # 更新子女档案
        updated_profile = children_repo.update_children_profile(
            profile_id=profile.id,
            **profile_data.dict(exclude_unset=True)
        )
        
        return ResponseUtils.success_response(
            data=ChildrenProfileResponse.from_orm(updated_profile),
            message="子女档案更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新子女档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新子女档案失败，请稍后重试"
        )


@router.get("/elderly", response_model=dict)
async def get_my_elderly_list(
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取我关联的老人列表
    
    仅子女用户可访问
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 关联的老人列表
    """
    try:
        # 获取关联的老人列表
        children_repo = ChildrenRepository(db)
        elderly_list = children_repo.get_elderly_by_children(current_user.id)
        
        # 构建响应数据
        items = []
        for elderly in elderly_list:
            # 获取健康数据统计
            health_stats = children_repo.get_elderly_health_statistics(elderly.id)
            
            # 构建响应
            elderly_data = ElderlyWithStatsResponse.from_orm(elderly)
            elderly_data.latest_health_record = health_stats.get("latest_record")
            elderly_data.today_reminders_count = health_stats.get("today_reminders_count", 0)
            elderly_data.pending_alerts_count = health_stats.get("pending_alerts_count", 0)
            
            items.append(elderly_data)
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except Exception as e:
        logger.error(f"获取关联老人列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取关联老人列表失败，请稍后重试"
        )


@router.post("/elderly/relation", response_model=dict)
async def add_elderly_relation(
    relation_data: ChildrenElderlyRelationCreate,
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """添加与老人的关系
    
    仅子女用户可添加
    
    Args:
        relation_data: 关系数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 添加成功的响应
    """
    try:
        # 验证老人是否存在
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(relation_data.elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 检查关系是否已存在
        children_repo = ChildrenRepository(db)
        if children_repo.check_relation_exists(
            children_user_id=current_user.id,
            elderly_id=relation_data.elderly_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已与该老人建立了关系"
            )
        
        # 添加关系
        children_repo.add_elderly_relation(
            children_user_id=current_user.id,
            **relation_data.dict()
        )
        
        return ResponseUtils.success_response(
            message="与老人的关系添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加老人关系失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加老人关系失败，请稍后重试"
        )


@router.delete("/elderly/relation/{elderly_id}", response_model=dict)
async def remove_elderly_relation(
    elderly_id: int,
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """移除与老人的关系
    
    仅子女用户可移除
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 移除成功的响应
    """
    try:
        # 检查关系是否存在
        children_repo = ChildrenRepository(db)
        if not children_repo.check_relation_exists(
            children_user_id=current_user.id,
            elderly_id=elderly_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您与该老人的关系不存在"
            )
        
        # 移除关系
        children_repo.remove_elderly_relation(
            children_user_id=current_user.id,
            elderly_id=elderly_id
        )
        
        return ResponseUtils.success_response(
            message="与老人的关系移除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除老人关系失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除老人关系失败，请稍后重试"
        )


@router.get("/dashboard", response_model=dict)
async def get_children_dashboard(
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取子女仪表盘数据
    
    仅子女用户可访问
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 仪表盘数据
    """
    try:
        # 获取仪表盘数据
        children_repo = ChildrenRepository(db)
        dashboard_data = children_repo.get_children_dashboard(current_user.id)
        
        return ResponseUtils.success_response(
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仪表盘数据失败，请稍后重试"
        )


@router.get("/search/elderly", response_model=dict)
async def search_elderly(
    keyword: str = Query(..., min_length=1, description="搜索关键字：姓名或手机号"),
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """搜索老人（用于添加关系）
    
    仅子女用户可搜索
    
    Args:
        keyword: 搜索关键字：姓名或手机号
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 搜索结果列表
    """
    try:
        # 搜索老人
        children_repo = ChildrenRepository(db)
        results = children_repo.search_elderly_for_relation(
            children_user_id=current_user.id,
            keyword=keyword
        )
        
        # 构建响应数据
        items = []
        for elderly in results:
            elderly_data = ElderlyWithStatsResponse.from_orm(elderly)
            elderly_data.latest_health_record = None  # 搜索结果不需要统计数据
            elderly_data.today_reminders_count = 0
            elderly_data.pending_alerts_count = 0
            items.append(elderly_data)
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except Exception as e:
        logger.error(f"搜索老人失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索老人失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/health-summary", response_model=dict)
async def get_elderly_health_summary(
    elderly_id: int,
    current_user: User = Depends(get_children_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取关联老人的健康摘要
    
    仅子女用户可访问
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 健康摘要
    """
    try:
        # 检查关系是否存在
        children_repo = ChildrenRepository(db)
        if not children_repo.check_relation_exists(
            children_user_id=current_user.id,
            elderly_id=elderly_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权查看该老人的健康摘要"
            )
        
        # 获取健康摘要
        health_summary = children_repo.get_elderly_health_statistics(elderly_id)
        
        return ResponseUtils.success_response(
            data=health_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取老人健康摘要失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取老人健康摘要失败，请稍后重试"
        )


# ============================================================================
# 新版子女端接口（符合前端预期路径）
# ============================================================================

@router.get("/elders/list", response_model=ElderListResponse)
async def get_elders_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取绑定的老人列表
    
    返回子女绑定的所有老人信息，包括健康状态和生命体征
    """
    import random
    import uuid
    
    try:
        logger.info(f"用户 {current_user.id} 获取绑定老人列表")
        
        # TODO: 从数据库获取真实数据
        # 目前返回模拟数据
        elders = [
            {
                "elderId": str(uuid.uuid4()),
                "name": "张爷爷",
                "avatar": None,
                "age": 72,
                "gender": "男",
                "relationship": "父亲",
                "healthStatus": "good",
                "lastUpdate": datetime.now().isoformat(),
                "location": "家中",
                "recentAlerts": 0,
                "vitalSigns": {
                    "heartRate": random.randint(65, 80),
                    "bloodPressure": f"{random.randint(115, 130)}/{random.randint(70, 85)}",
                    "temperature": round(random.uniform(36.2, 36.8), 1)
                }
            },
            {
                "elderId": str(uuid.uuid4()),
                "name": "李奶奶",
                "avatar": None,
                "age": 68,
                "gender": "女",
                "relationship": "母亲",
                "healthStatus": "warning",
                "lastUpdate": datetime.now().isoformat(),
                "location": "社区活动中心",
                "recentAlerts": 2,
                "vitalSigns": {
                    "heartRate": random.randint(70, 90),
                    "bloodPressure": f"{random.randint(130, 145)}/{random.randint(85, 95)}",
                    "temperature": round(random.uniform(36.3, 36.9), 1)
                }
            }
        ]
        
        return {
            "success": True,
            "data": {
                "elders": elders,
                "total": len(elders)
            }
        }
        
    except Exception as e:
        logger.error(f"获取老人列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取老人列表失败")


@router.get("/elders/{elder_id}/detail", response_model=ElderDetailResponse)
async def get_elder_detail(
    elder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人详细信息
    
    包括个人信息、健康数据、告警和用药信息
    """
    import random
    
    try:
        logger.info(f"用户 {current_user.id} 获取老人详情: {elder_id}")
        
        # TODO: 验证权限并从数据库获取真实数据
        # 目前返回模拟数据
        detail = {
            "elderId": elder_id,
            "personalInfo": {
                "name": "张爷爷",
                "age": 72,
                "gender": "男",
                "phone": "138****1234",
                "address": "北京市朝阳区XX小区",
                "emergencyContact": "张三",
                "emergencyPhone": "139****5678",
                "bloodType": "A型",
                "allergies": ["青霉素"],
                "chronicDiseases": ["高血压", "糖尿病"]
            },
            "healthData": {
                "bloodPressure": {
                    "systolic": random.randint(115, 135),
                    "diastolic": random.randint(70, 88),
                    "status": "normal",
                    "measuredAt": datetime.now().isoformat()
                },
                "heartRate": {
                    "value": random.randint(65, 82),
                    "status": "normal",
                    "measuredAt": datetime.now().isoformat()
                },
                "bloodSugar": {
                    "value": round(random.uniform(5.0, 7.5), 1),
                    "status": "warning",
                    "measuredAt": datetime.now().isoformat()
                },
                "sleep": {
                    "duration": round(random.uniform(5.5, 8.0), 1),
                    "quality": "good",
                    "deepSleep": round(random.uniform(1.5, 2.5), 1)
                },
                "steps": random.randint(3000, 8000)
            },
            "alerts": [
                {
                    "alertId": "alert-001",
                    "type": "血糖偏高",
                    "level": "warning",
                    "message": "今日餐后血糖7.2mmol/L，略高于正常值",
                    "time": datetime.now().isoformat(),
                    "handled": False
                }
            ],
            "medications": [
                {
                    "medicationId": "med-001",
                    "name": "降压药",
                    "dosage": "1片",
                    "frequency": "每日一次",
                    "time": "08:00",
                    "taken": True
                },
                {
                    "medicationId": "med-002",
                    "name": "降糖药",
                    "dosage": "1片",
                    "frequency": "每日两次",
                    "time": "08:00, 18:00",
                    "taken": True
                }
            ]
        }
        
        return {
            "success": True,
            "data": detail
        }
        
    except Exception as e:
        logger.error(f"获取老人详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取老人详情失败")


@router.get("/monitor/{elder_id}/realtime", response_model=RealtimeMonitorResponse)
async def get_realtime_monitor(
    elder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人实时监控数据
    
    返回当前时刻的生命体征和位置信息
    """
    import random
    
    try:
        logger.info(f"用户 {current_user.id} 获取实时监控: {elder_id}")
        
        # TODO: 从设备/数据库获取真实实时数据
        # 目前返回模拟数据
        monitor_data = {
            "elderId": elder_id,
            "timestamp": datetime.now().isoformat(),
            "heartRate": random.randint(65, 85),
            "bloodPressure": {
                "systolic": random.randint(115, 135),
                "diastolic": random.randint(70, 88)
            },
            "bloodOxygen": random.randint(95, 99),
            "temperature": round(random.uniform(36.2, 36.8), 1),
            "location": {
                "name": "家中",
                "latitude": 39.9042 + random.uniform(-0.001, 0.001),
                "longitude": 116.4074 + random.uniform(-0.001, 0.001),
                "updatedAt": datetime.now().isoformat()
            },
            "activityStatus": random.choice(["静坐", "行走", "休息"]),
            "deviceStatus": "在线"
        }
        
        return {
            "success": True,
            "data": monitor_data
        }
        
    except Exception as e:
        logger.error(f"获取实时监控失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取实时监控数据失败")


@router.post("/reminders/create", response_model=ReminderCreateResponse)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """创建提醒
    
    为绑定的老人创建用药、预约、运动等提醒
    """
    import uuid
    
    try:
        logger.info(f"用户 {current_user.id} 创建提醒: {reminder_data.title}")
        
        # TODO: 保存到数据库
        # 目前返回模拟响应
        reminder = {
            "reminderId": str(uuid.uuid4()),
            "elderId": reminder_data.elder_id,
            "elderName": "张爷爷",  # TODO: 从数据库获取
            "type": reminder_data.type,
            "title": reminder_data.title,
            "description": reminder_data.description,
            "scheduledTime": reminder_data.scheduled_time,
            "status": "pending",
            "priority": reminder_data.priority,
            "createdAt": datetime.now().isoformat()
        }
        
        # 类型对应的消息
        type_messages = {
            "medication": "用药提醒已创建，将按时通知老人服药",
            "appointment": "预约提醒已创建，将提前通知老人",
            "exercise": "运动提醒已创建，帮助老人保持健康",
            "other": "提醒已创建成功"
        }
        
        return {
            "success": True,
            "data": reminder,
            "message": type_messages.get(reminder_data.type, "提醒创建成功")
        }
        
    except Exception as e:
        logger.error(f"创建提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建提醒失败")