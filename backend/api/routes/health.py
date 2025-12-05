"""健康记录相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from database.database import get_db
from database.models import User
from schemas.models import (
    HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse,
    HealthAlertResponse, DailyHealthSummary, WeeklyHealthTrend
)
from dependencies.get_current_user import (
    get_current_user, get_elderly_or_caretaker, get_elderly_user
)
from repositories.health_repository import HealthRepository
from repositories.elderly_repository import ElderlyRepository
from repositories.alert_repository import AlertRepository
from utils.common_utils import ResponseUtils, DataUtils
from middlewares.error_middleware import BusinessError

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.post("/elderly/{elderly_id}/records", response_model=dict)
async def add_health_record(
    elderly_id: int,
    health_data: HealthRecordCreate,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """添加健康记录
    
    老人本人、子女、管理员和社区管理员可添加健康记录
    
    Args:
        elderly_id: 老人ID
        health_data: 健康记录数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 添加成功的响应
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
        
        # 添加健康记录
        health_repo = HealthRepository(db)
        health_record = health_repo.add_health_record(
            elderly_id=elderly_id,
            **health_data.dict()
        )
        
        # 检查是否需要生成健康警报
        alert_repo = AlertRepository(db)
        alerts = []
        
        # 检查各项健康指标是否异常
        if health_data.blood_pressure_high >= 140 or health_data.blood_pressure_low >= 90:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "high_blood_pressure",
                "alert_message": f"血压偏高：{health_data.blood_pressure_high}/{health_data.blood_pressure_low}",
                "severity": "high"
            })
        
        if health_data.blood_pressure_high < 90 or health_data.blood_pressure_low < 60:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "low_blood_pressure",
                "alert_message": f"血压偏低：{health_data.blood_pressure_high}/{health_data.blood_pressure_low}",
                "severity": "high"
            })
        
        if health_data.heart_rate > 100:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "high_heart_rate",
                "alert_message": f"心率偏快：{health_data.heart_rate} 次/分",
                "severity": "medium"
            })
        
        if health_data.heart_rate < 60:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "low_heart_rate",
                "alert_message": f"心率偏慢：{health_data.heart_rate} 次/分",
                "severity": "medium"
            })
        
        if health_data.blood_sugar > 7.0:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "high_blood_sugar",
                "alert_message": f"血糖偏高：{health_data.blood_sugar} mmol/L",
                "severity": "medium"
            })
        
        if health_data.weight_change and abs(health_data.weight_change) > 2.0:
            alerts.append({
                "elderly_id": elderly_id,
                "alert_type": "abnormal_weight_change",
                "alert_message": f"体重变化异常：{health_data.weight_change} kg",
                "severity": "low"
            })
        
        # 创建警报
        for alert_data in alerts:
            alert_repo.create_alert(**alert_data)
        
        return ResponseUtils.success_response(
            data=HealthRecordResponse.from_orm(health_record),
            message="健康记录添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加健康记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加健康记录失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/records", response_model=dict)
async def get_elderly_health_records(
    elderly_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人健康记录列表
    
    老人本人、子女、管理员和社区管理员可访问
    
    Args:
        elderly_id: 老人ID
        page: 页码
        size: 每页大小
        start_date: 开始日期
        end_date: 结束日期
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 分页健康记录列表
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
        
        # 格式化分页参数
        page, size = DataUtils.format_pagination_params(page, size)
        
        # 查询健康记录
        health_repo = HealthRepository(db)
        records, total = health_repo.get_elderly_health_records(
            elderly_id=elderly_id,
            page=page,
            size=size,
            start_date=start_date,
            end_date=end_date
        )
        
        # 构建响应数据
        items = [HealthRecordResponse.from_orm(record) for record in records]
        
        return ResponseUtils.pagination_response(
            data=items,
            total=total,
            page=page,
            size=size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康记录失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/records/latest", response_model=dict)
async def get_latest_health_record(
    elderly_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取最新健康记录
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 最新健康记录
    """
    try:
        # 获取最新健康记录
        health_repo = HealthRepository(db)
        record = health_repo.get_latest_health_record(elderly_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="暂无健康记录"
            )
        
        return ResponseUtils.success_response(
            data=HealthRecordResponse.from_orm(record)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新健康记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取最新健康记录失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/daily-summary", response_model=dict)
async def get_daily_health_summary(
    elderly_id: int,
    date: Optional[datetime] = Query(None, description="日期，默认为今天"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人每日健康摘要
    
    Args:
        elderly_id: 老人ID
        date: 日期，默认为今天
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 每日健康摘要
    """
    try:
        # 如果没有提供日期，使用今天
        if not date:
            date = datetime.now()
        
        # 计算当天的开始和结束时间
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())
        
        # 获取每日健康摘要
        health_repo = HealthRepository(db)
        summary = health_repo.generate_daily_summary(
            elderly_id=elderly_id,
            start_time=start_of_day,
            end_time=end_of_day
        )
        
        # 获取当天的警报数量
        alert_repo = AlertRepository(db)
        alerts_count = alert_repo.count_alerts_by_date(
            elderly_id=elderly_id,
            date=date.date()
        )
        
        # 构建响应数据
        response_data = DailyHealthSummary(
            date=date.date(),
            total_records=summary.get("total_records", 0),
            average_blood_pressure=summary.get("average_blood_pressure"),
            average_heart_rate=summary.get("average_heart_rate"),
            average_blood_sugar=summary.get("average_blood_sugar"),
            weight=summary.get("latest_weight"),
            alerts_count=alerts_count
        )
        
        return ResponseUtils.success_response(
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"获取每日健康摘要失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取每日健康摘要失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/weekly-trends", response_model=dict)
async def get_weekly_health_trends(
    elderly_id: int,
    weeks: int = Query(1, ge=1, le=4, description="查看几周的数据，默认为1周"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人健康数据趋势（周）
    
    Args:
        elderly_id: 老人ID
        weeks: 查看几周的数据，默认为1周
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 健康数据趋势
    """
    try:
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        # 获取健康数据趋势
        health_repo = HealthRepository(db)
        trends = health_repo.calculate_weekly_trends(
            elderly_id=elderly_id,
            start_time=start_date,
            end_time=end_date
        )
        
        # 构建响应数据
        response_data = WeeklyHealthTrend(
            period=f"最近{weeks}周",
            start_date=start_date.date(),
            end_date=end_date.date(),
            trends=trends
        )
        
        return ResponseUtils.success_response(
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"获取健康数据趋势失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康数据趋势失败，请稍后重试"
        )


@router.get("/elderly/{elderly_id}/alerts", response_model=dict)
async def get_elderly_health_alerts(
    elderly_id: int,
    status: Optional[str] = Query("pending", description="警报状态：pending/completed"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人健康警报
    
    Args:
        elderly_id: 老人ID
        status: 警报状态：pending/completed
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 健康警报列表
    """
    try:
        # 获取健康警报
        alert_repo = AlertRepository(db)
        alerts = alert_repo.get_alerts_by_elderly(
            elderly_id=elderly_id,
            status=status
        )
        
        # 构建响应数据
        items = [HealthAlertResponse.from_orm(alert) for alert in alerts]
        
        return ResponseUtils.success_response(
            data=items
        )
        
    except Exception as e:
        logger.error(f"获取健康警报失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康警报失败，请稍后重试"
        )


@router.put("/alerts/{alert_id}/complete", response_model=dict)
async def complete_health_alert(
    alert_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """完成健康警报处理
    
    Args:
        alert_id: 警报ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作成功的响应
    """
    try:
        # 更新警报状态
        alert_repo = AlertRepository(db)
        alert = alert_repo.get_by_id(alert_id)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="警报不存在"
            )
        
        # 更新警报状态为已完成
        alert_repo.update_alert_status(alert_id, "completed")
        
        return ResponseUtils.success_response(
            message="警报已标记为已处理"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理健康警报失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理健康警报失败，请稍后重试"
        )