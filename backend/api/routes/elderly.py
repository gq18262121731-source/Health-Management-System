"""老人档案相关API接口"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
import logging

from database.database import get_db
from database.models import User, ElderlyProfile
from schemas.models import (
    ElderlyCreate, ElderlyUpdate, ElderlyResponse, ElderlyListResponse,
    ElderlyWithHealthResponse, HealthRecordResponse,
    TodayHealthData, TodayHealthResponse,
    AIMessageRequest, AIMessageResponse, AIMessageData,
    AIAnalyzeRequest, AIAnalyzeResponse, AIAnalyzeData,
    # 图表相关
    HeartRateChartResponse, HeartRateChartData, ChartDataPoint,
    SleepChartResponse, SleepChartData, SleepDataPoint,
    BloodPressureChartResponse, BloodPressureChartData, BloodPressureDataPoint,
    RadarChartResponse, RadarChartData, RadarCategory,
    # 报告相关
    CurrentReportResponse, HealthReport, ReportMetric,
    # 心情相关
    MoodRecord, MoodRecordResponse, MoodRecordData
)
from dependencies.get_current_user import (
    get_current_user, get_admin_or_community_admin, get_elderly_or_caretaker
)
from repositories.elderly_repository import ElderlyRepository
from repositories.health_repository import HealthRepository
from repositories.user_repository import UserRepository
from utils.common_utils import ResponseUtils, DataUtils, ValidationUtils, FileUtils
from middlewares.error_middleware import BusinessError

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建路由器（prefix 在 main.py 统一设置为 /api/v1/elderly）
router = APIRouter(tags=["elderly"])


@router.post("/", response_model=ElderlyResponse)
async def create_elderly_profile(
    elderly_data: ElderlyCreate,
    current_user: User = Depends(get_admin_or_community_admin),
    db: Session = Depends(get_db)
) -> dict:
    """创建老人档案
    
    仅管理员和社区管理员可创建老人档案
    
    Args:
        elderly_data: 老人档案创建数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 创建成功的响应
    """
    try:
        # 验证手机号格式
        if not ValidationUtils.validate_phone_number(elderly_data.phone_number):
            raise BusinessError(
                code=400,
                message="手机号格式不正确"
            )
        
        # 验证身份证号格式
        if elderly_data.id_card and not ValidationUtils.validate_id_card(elderly_data.id_card):
            raise BusinessError(
                code=400,
                message="身份证号格式不正确"
            )
        
        # 检查手机号是否已存在
        user_repo = UserRepository(db)
        existing_user = user_repo.get_by_phone_number(elderly_data.phone_number)
        
        if existing_user:
            # 如果用户存在但没有老人档案，则创建老人档案
            if existing_user.role == "elderly" and not existing_user.elderly_profile:
                elderly_repo = ElderlyRepository(db)
                elderly = elderly_repo.create_elderly_profile(
                    user_id=existing_user.id,
                    **elderly_data.dict(exclude={"phone_number", "password"})
                )
                return ResponseUtils.success_response(
                    data=ElderlyResponse.from_orm(elderly)
                )
            else:
                raise BusinessError(
                    code=400,
                    message="该手机号已被注册"
                )
        
        # 创建新用户和老人档案
        user_repo = UserRepository(db)
        user = user_repo.create_user_with_profile(
            phone_number=elderly_data.phone_number,
            password=elderly_data.password,
            role="elderly",
            profile_data=elderly_data.dict(exclude={"phone_number", "password"})
        )
        
        if user and user.elderly_profile:
            return ResponseUtils.success_response(
                data=ElderlyResponse.from_orm(user.elderly_profile)
            )
        else:
            raise BusinessError(
                code=500,
                message="创建老人档案失败"
            )
            
    except BusinessError as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except Exception as e:
        logger.error(f"创建老人档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建老人档案失败，请稍后重试"
        )


@router.get("/", response_model=dict)
async def get_elderly_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    name: Optional[str] = Query(None, description="老人姓名"),
    community_id: Optional[int] = Query(None, description="社区ID"),
    status: Optional[str] = Query(None, description="健康状态"),
    current_user: User = Depends(get_admin_or_community_admin),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人列表
    
    仅管理员和社区管理员可获取老人列表
    
    Args:
        page: 页码
        size: 每页大小
        name: 老人姓名（模糊搜索）
        community_id: 社区ID
        status: 健康状态
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 分页老人列表
    """
    try:
        # 格式化分页参数
        page, size = DataUtils.format_pagination_params(page, size)
        
        # 查询老人列表
        elderly_repo = ElderlyRepository(db)
        elderly_list, total = elderly_repo.get_elderly_list(
            page=page,
            size=size,
            name=name,
            community_id=community_id,
            status=status
        )
        
        # 构建响应数据
        items = [ElderlyListResponse.from_orm(elderly) for elderly in elderly_list]
        
        return ResponseUtils.pagination_response(
            data=items,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"获取老人列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取老人列表失败，请稍后重试"
        )


@router.get("/{elderly_id}", response_model=dict)
async def get_elderly_detail(
    elderly_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人详情
    
    老人本人、子女、管理员和社区管理员可访问
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 老人详细信息
    """
    try:
        # 查询老人信息
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        return ResponseUtils.success_response(
            data=ElderlyResponse.from_orm(elderly)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取老人详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取老人详情失败，请稍后重试"
        )


@router.put("/{elderly_id}", response_model=dict)
async def update_elderly_profile(
    elderly_id: int,
    elderly_data: ElderlyUpdate,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """更新老人档案
    
    老人本人、子女、管理员和社区管理员可更新
    
    Args:
        elderly_id: 老人ID
        elderly_data: 更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新成功的响应
    """
    try:
        # 查询老人信息
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 验证身份证号格式（如果更新）
        if elderly_data.id_card and not ValidationUtils.validate_id_card(elderly_data.id_card):
            raise BusinessError(
                code=400,
                message="身份证号格式不正确"
            )
        
        # 更新老人档案
        update_data = elderly_data.dict(exclude_unset=True)
        updated_elderly = elderly_repo.update(elderly_id, update_data)
        
        return ResponseUtils.success_response(
            data=ElderlyResponse.from_orm(updated_elderly),
            message="更新成功"
        )
        
    except HTTPException:
        raise
    except BusinessError as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except Exception as e:
        logger.error(f"更新老人档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新老人档案失败，请稍后重试"
        )


@router.delete("/{elderly_id}", response_model=dict)
async def delete_elderly_profile(
    elderly_id: int,
    current_user: User = Depends(get_admin_or_community_admin),
    db: Session = Depends(get_db)
) -> dict:
    """删除老人档案
    
    仅管理员和社区管理员可删除
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 删除成功的响应
    """
    try:
        # 查询老人信息
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 删除老人档案（软删除）
        elderly_repo.delete(elderly_id)
        
        return ResponseUtils.success_response(
            message="删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除老人档案失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除老人档案失败，请稍后重试"
        )


@router.get("/{elderly_id}/health-summary", response_model=dict)
async def get_elderly_health_summary(
    elderly_id: int,
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """获取老人健康摘要信息
    
    老人本人、子女、管理员和社区管理员可访问
    
    Args:
        elderly_id: 老人ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 健康摘要信息
    """
    try:
        # 查询老人健康信息
        elderly_repo = ElderlyRepository(db)
        elderly_with_health = elderly_repo.get_with_health_data(elderly_id)
        
        if not elderly_with_health:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 构建响应数据
        response_data = ElderlyWithHealthResponse(
            elderly=ElderlyResponse.from_orm(elderly_with_health),
            latest_health_records=[HealthRecordResponse.from_orm(record) 
                                  for record in elderly_with_health.health_records[:5]],
            pending_alerts_count=elderly_with_health.pending_alerts_count
        )
        
        return ResponseUtils.success_response(
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取老人健康摘要失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取老人健康摘要失败，请稍后重试"
        )


@router.post("/{elderly_id}/upload-avatar", response_model=dict)
async def upload_elderly_avatar(
    elderly_id: int,
    file: UploadFile = File(..., description="头像图片文件"),
    current_user: User = Depends(get_elderly_or_caretaker),
    db: Session = Depends(get_db)
) -> dict:
    """上传老人头像
    
    Args:
        elderly_id: 老人ID
        file: 头像文件
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 上传成功的响应
    """
    try:
        # 验证文件类型
        allowed_extensions = ["jpg", "jpeg", "png", "gif"]
        if not FileUtils.validate_file_extension(file.filename, allowed_extensions):
            raise BusinessError(
                code=400,
                message="仅支持jpg、jpeg、png、gif格式的图片"
            )
        
        # 验证文件大小
        contents = await file.read()
        if not FileUtils.validate_file_size(len(contents), max_size_mb=5.0):
            raise BusinessError(
                code=400,
                message="文件大小不能超过5MB"
            )
        
        # 这里应该实现文件保存逻辑
        # 为了演示，我们只更新数据库记录
        elderly_repo = ElderlyRepository(db)
        elderly = elderly_repo.get_by_id(elderly_id)
        
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 生成文件名并保存文件（这里简化处理）
        filename = FileUtils.generate_filename(file.filename, prefix="elderly_")
        # 实际应用中应该保存文件到文件系统或云存储
        # 这里只是模拟更新
        elderly_repo.update(elderly_id, {"profile_image": f"/uploads/elderly/{filename}"})
        
        return ResponseUtils.success_response(
            data={"avatar_url": f"/uploads/elderly/{filename}"},
            message="头像上传成功"
        )
        
    except HTTPException:
        raise
    except BusinessError as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传头像失败，请稍后重试"
        )


# ============================================================================
# 健康数据相关接口
# ============================================================================

@router.get("/health/today", response_model=TodayHealthResponse)
async def get_today_health_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取今日健康数据
    
    需要 JWT Token 认证，从 Token 中提取用户信息
    
    Args:
        current_user: 当前登录用户（从 Token 中提取）
        db: 数据库会话
        
    Returns:
        TodayHealthResponse: 今日健康数据响应
    """
    import random
    from datetime import datetime
    
    try:
        logger.info(f"获取用户 {current_user.id} 的今日健康数据")
        
        # 获取用户的老人档案
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == current_user.id
        ).first()
        
        if not elderly_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到老人档案，请先完善个人信息"
            )
        
        # TODO: 从数据库获取真实健康数据
        # 目前使用模拟数据
        
        # 生成模拟的健康数据（实际应从 health_records 表获取）
        systolic = random.randint(110, 140)
        diastolic = random.randint(70, 90)
        heart_rate = random.randint(60, 100)
        
        # 判断健康状态
        health_status = "normal"
        health_tips = "您的各项指标正常，请继续保持健康的生活方式。"
        
        if systolic >= 140 or diastolic >= 90:
            health_status = "warning"
            health_tips = "血压偏高，建议减少盐分摄入，保持适度运动。"
        elif systolic < 90 or diastolic < 60:
            health_status = "warning"
            health_tips = "血压偏低，建议多补充水分和营养。"
        
        if heart_rate > 100:
            health_status = "warning"
            health_tips = "心率偏快，建议放松休息，避免剧烈运动。"
        
        health_data = TodayHealthData(
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate,
            blood_oxygen=random.randint(95, 99),
            blood_sugar=round(random.uniform(4.5, 7.0), 1),
            temperature=round(random.uniform(36.3, 36.8), 1),
            steps=random.randint(1000, 8000),
            sleep_hours=round(random.uniform(5.5, 8.5), 1),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            health_status=health_status,
            health_tips=health_tips
        )
        
        return {
            "status": "success",
            "data": health_data,
            "message": "获取今日健康数据成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取今日健康数据失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康数据失败，请稍后重试"
        )


# ============================================================================
# AI 健康助手接口
# ============================================================================

@router.post("/ai/chat", response_model=AIMessageResponse)
async def ai_chat(
    request: AIMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """AI 健康助手对话
    
    根据用户消息和上下文，提供健康建议和回复
    
    Args:
        request: AI 对话请求（包含消息和上下文）
        current_user: 当前登录用户（从 Token 中提取）
        db: 数据库会话
        
    Returns:
        AIMessageResponse: AI 回复
    """
    try:
        logger.info(f"用户 {current_user.id} 发起 AI 对话: {request.message[:50]}...")
        
        # 获取用户的老人档案信息
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == current_user.id
        ).first()
        
        user_name = elderly_profile.name if elderly_profile else "用户"
        
        # TODO: 集成真实的 AI 服务（如 DeepSeek、智谱 GLM 等）
        # 目前使用模拟响应
        
        response_data = _generate_ai_response(request.message, request.context, user_name)
        
        return {
            "success": True,
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 对话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 服务暂时不可用，请稍后重试"
        )


@router.post("/ai/analyze", response_model=AIAnalyzeResponse)
async def ai_analyze(
    request: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """AI 健康数据分析
    
    分析用户的健康数据趋势，提供专业建议
    
    Args:
        request: 分析请求（数据类型和时间范围）
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        AIAnalyzeResponse: 分析结果
    """
    try:
        logger.info(f"用户 {current_user.id} 请求 AI 分析: {request.dataType}")
        
        # TODO: 从数据库获取历史健康数据进行分析
        # 目前使用模拟响应
        
        analysis_data = _generate_ai_analysis(request.dataType, request.timeRange)
        
        return {
            "success": True,
            "data": analysis_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 分析失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 分析服务暂时不可用，请稍后重试"
        )


def _generate_ai_response(message: str, context, user_name: str) -> dict:
    """生成 AI 对话响应（模拟）
    
    TODO: 替换为真实的 AI 服务调用
    """
    import random
    
    # 根据消息关键词生成不同回复
    message_lower = message.lower()
    
    if any(kw in message_lower for kw in ['血压', '高血压', '低血压']):
        return {
            "responseText": f"{user_name}您好！关于血压问题，建议您保持规律作息，减少盐分摄入，适度运动。"
                           f"如果血压持续偏高（>140/90mmHg）或偏低（<90/60mmHg），建议及时就医。",
            "suggestions": [
                "每天定时测量血压并记录",
                "减少高盐食物摄入",
                "保持适度有氧运动",
                "避免情绪激动"
            ],
            "needsAttention": context.healthStatus == "warning" if context else False,
            "confidence": 0.92
        }
    
    elif any(kw in message_lower for kw in ['心率', '心跳', '心脏']):
        return {
            "responseText": f"{user_name}您好！正常成人静息心率在60-100次/分钟之间。"
                           f"如果您感到心跳过快或过慢，建议放松休息，避免剧烈运动和情绪波动。",
            "suggestions": [
                "保持规律作息",
                "避免过量咖啡因",
                "适度进行有氧运动",
                "保持心情愉悦"
            ],
            "needsAttention": False,
            "confidence": 0.88
        }
    
    elif any(kw in message_lower for kw in ['血糖', '糖尿病', '血糖高']):
        return {
            "responseText": f"{user_name}您好！空腹血糖正常值为3.9-6.1mmol/L，餐后2小时血糖应<7.8mmol/L。"
                           f"建议您控制饮食，少吃高糖食物，保持适量运动。",
            "suggestions": [
                "控制主食摄入量",
                "多吃蔬菜和粗粮",
                "餐后适当散步",
                "定期监测血糖"
            ],
            "needsAttention": True,
            "confidence": 0.90
        }
    
    elif any(kw in message_lower for kw in ['睡眠', '失眠', '睡不着']):
        return {
            "responseText": f"{user_name}您好！良好的睡眠对健康至关重要。建议您保持规律作息，"
                           f"睡前避免使用电子设备，可以尝试喝杯温牛奶或泡脚。",
            "suggestions": [
                "固定作息时间",
                "睡前1小时放下手机",
                "保持卧室安静舒适",
                "睡前可以听轻音乐放松"
            ],
            "needsAttention": False,
            "confidence": 0.85
        }
    
    else:
        # 默认回复
        responses = [
            f"{user_name}您好！我是您的健康助手，很高兴为您服务。请问有什么健康问题需要咨询吗？",
            f"{user_name}您好！我可以为您提供血压、心率、血糖、睡眠等方面的健康建议，请问您想了解哪方面的信息？",
        ]
        return {
            "responseText": random.choice(responses),
            "suggestions": [
                "查看今日健康数据",
                "了解血压注意事项",
                "查看睡眠质量分析",
                "获取饮食建议"
            ],
            "needsAttention": False,
            "confidence": 0.80
        }


def _generate_ai_analysis(data_type: str, time_range: str) -> dict:
    """生成 AI 数据分析结果（模拟）
    
    TODO: 替换为真实的数据分析逻辑
    """
    import random
    
    trends = ["上升", "稳定", "下降"]
    risk_levels = ["low", "medium", "high"]
    
    analyses = {
        "血压": {
            "analysis": f"根据您近{time_range}的血压数据分析，您的血压整体处于正常范围。"
                       f"收缩压平均值约128mmHg，舒张压平均值约82mmHg。",
            "trend": random.choice(trends),
            "riskLevel": "low",
            "recommendations": [
                "继续保持健康的生活方式",
                "每天坚持测量血压",
                "保持适度运动"
            ]
        },
        "心率": {
            "analysis": f"根据您近{time_range}的心率数据分析，您的静息心率平均为72次/分钟，"
                       f"属于正常范围。运动时心率响应良好。",
            "trend": "稳定",
            "riskLevel": "low",
            "recommendations": [
                "保持规律的有氧运动",
                "注意运动强度适中",
                "保持良好心态"
            ]
        },
        "血糖": {
            "analysis": f"根据您近{time_range}的血糖数据分析，您的空腹血糖平均为5.8mmol/L，"
                       f"处于正常偏高水平，建议注意饮食控制。",
            "trend": "稳定",
            "riskLevel": "medium",
            "recommendations": [
                "减少精制糖摄入",
                "增加膳食纤维",
                "餐后适当运动"
            ]
        },
        "睡眠": {
            "analysis": f"根据您近{time_range}的睡眠数据分析，您的平均睡眠时长为6.5小时，"
                       f"深度睡眠比例约20%，睡眠质量一般。",
            "trend": "稳定",
            "riskLevel": "low",
            "recommendations": [
                "尽量保证7-8小时睡眠",
                "固定作息时间",
                "改善睡眠环境"
            ]
        }
    }
    
    return analyses.get(data_type, {
        "analysis": f"暂无{data_type}类型的分析数据",
        "trend": "稳定",
        "riskLevel": "low",
        "recommendations": ["请先记录相关健康数据"]
    })


# ============================================================================
# 健康图表接口
# ============================================================================

@router.get("/health/charts/heartrate", response_model=HeartRateChartResponse)
async def get_heartrate_chart(
    period: str = Query("today", description="时间段: today, week, month"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取心率趋势图数据"""
    import random
    from datetime import datetime, timedelta
    
    try:
        logger.info(f"用户 {current_user.id} 获取心率图表, period={period}")
        
        # 生成模拟数据
        data_points = []
        if period == "today":
            # 24小时数据
            for i in range(24):
                data_points.append({
                    "time": f"{i:02d}:00",
                    "value": random.randint(60, 95),
                    "timestamp": (datetime.now().replace(hour=i, minute=0)).isoformat()
                })
        elif period == "week":
            # 7天数据
            days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            for i, day in enumerate(days):
                data_points.append({
                    "time": day,
                    "value": random.randint(65, 85),
                    "timestamp": (datetime.now() - timedelta(days=6-i)).isoformat()
                })
        else:  # month
            for i in range(30):
                data_points.append({
                    "time": f"{i+1}日",
                    "value": random.randint(65, 90),
                    "timestamp": (datetime.now() - timedelta(days=29-i)).isoformat()
                })
        
        values = [p["value"] for p in data_points]
        
        return {
            "success": True,
            "data": {
                "period": period,
                "dataPoints": data_points,
                "statistics": {
                    "average": round(sum(values) / len(values), 1),
                    "min": min(values),
                    "max": max(values)
                }
            }
        }
    except Exception as e:
        logger.error(f"获取心率图表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取心率数据失败")


@router.get("/health/charts/sleep", response_model=SleepChartResponse)
async def get_sleep_chart(
    period: str = Query("week", description="时间段: week, month"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取睡眠分析图表数据"""
    import random
    from datetime import datetime, timedelta
    
    try:
        logger.info(f"用户 {current_user.id} 获取睡眠图表, period={period}")
        
        data_points = []
        days_count = 7 if period == "week" else 30
        
        for i in range(days_count):
            date = datetime.now() - timedelta(days=days_count-1-i)
            deep = round(random.uniform(1.5, 3.0), 1)
            light = round(random.uniform(3.0, 5.0), 1)
            data_points.append({
                "day": date.strftime("%m-%d"),
                "deepSleep": deep,
                "lightSleep": light,
                "total": round(deep + light, 1)
            })
        
        avg_deep = sum(p["deepSleep"] for p in data_points) / len(data_points)
        avg_total = sum(p["total"] for p in data_points) / len(data_points)
        
        quality = "good" if avg_total >= 7 else ("fair" if avg_total >= 6 else "poor")
        
        return {
            "success": True,
            "data": {
                "period": period,
                "dataPoints": data_points,
                "statistics": {
                    "averageDeepSleep": round(avg_deep, 1),
                    "averageTotalSleep": round(avg_total, 1),
                    "sleepQuality": quality
                }
            }
        }
    except Exception as e:
        logger.error(f"获取睡眠图表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取睡眠数据失败")


@router.get("/health/charts/bloodpressure", response_model=BloodPressureChartResponse)
async def get_bloodpressure_chart(
    period: str = Query("week", description="时间段: week, month"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取血压趋势图表数据"""
    import random
    from datetime import datetime, timedelta
    
    try:
        logger.info(f"用户 {current_user.id} 获取血压图表, period={period}")
        
        data_points = []
        days_count = 7 if period == "week" else 30
        
        for i in range(days_count):
            date = datetime.now() - timedelta(days=days_count-1-i)
            systolic = random.randint(110, 140)
            diastolic = random.randint(70, 90)
            data_points.append({
                "time": date.strftime("%m-%d"),
                "systolic": systolic,
                "diastolic": diastolic,
                "timestamp": date.isoformat()
            })
        
        avg_sys = sum(p["systolic"] for p in data_points) / len(data_points)
        avg_dia = sum(p["diastolic"] for p in data_points) / len(data_points)
        
        return {
            "success": True,
            "data": {
                "period": period,
                "dataPoints": data_points,
                "statistics": {
                    "averageSystolic": round(avg_sys, 1),
                    "averageDiastolic": round(avg_dia, 1)
                }
            }
        }
    except Exception as e:
        logger.error(f"获取血压图表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取血压数据失败")


@router.get("/health/charts/radar", response_model=RadarChartResponse)
async def get_health_radar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取健康雷达图数据"""
    import random
    
    try:
        logger.info(f"用户 {current_user.id} 获取健康雷达图")
        
        categories = [
            {"category": "心血管", "score": random.randint(70, 95), "maxScore": 100},
            {"category": "睡眠质量", "score": random.randint(65, 90), "maxScore": 100},
            {"category": "运动健康", "score": random.randint(60, 85), "maxScore": 100},
            {"category": "营养状况", "score": random.randint(70, 90), "maxScore": 100},
            {"category": "心理健康", "score": random.randint(75, 95), "maxScore": 100},
            {"category": "免疫力", "score": random.randint(65, 88), "maxScore": 100},
        ]
        
        overall = sum(c["score"] for c in categories) / len(categories)
        
        return {
            "success": True,
            "data": {
                "categories": categories,
                "overallScore": round(overall, 1)
            }
        }
    except Exception as e:
        logger.error(f"获取雷达图失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取健康雷达数据失败")


# ============================================================================
# 健康报告接口
# ============================================================================

@router.get("/reports/current", response_model=CurrentReportResponse)
async def get_current_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取当前健康报告"""
    import uuid
    from datetime import datetime
    
    try:
        logger.info(f"用户 {current_user.id} 获取当前健康报告")
        
        # 获取用户名
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == current_user.id
        ).first()
        user_name = elderly_profile.name if elderly_profile else "用户"
        
        report = {
            "reportId": str(uuid.uuid4()),
            "generatedAt": datetime.now().isoformat(),
            "reportType": "daily",
            "metrics": [
                {"name": "血压", "value": "125/82 mmHg", "status": "normal", "trend": "stable"},
                {"name": "心率", "value": "72 bpm", "status": "normal", "trend": "stable"},
                {"name": "血糖", "value": "5.8 mmol/L", "status": "warning", "trend": "up"},
                {"name": "睡眠", "value": "6.5 小时", "status": "normal", "trend": "down"},
                {"name": "运动", "value": "5200 步", "status": "normal", "trend": "up"},
                {"name": "体重", "value": "68 kg", "status": "normal", "trend": "stable"},
            ],
            "summary": f"{user_name}您好！今日健康状况整体良好。血压、心率等主要指标正常，血糖略有偏高，建议注意饮食控制。睡眠时长有所下降，建议保持规律作息。",
            "recommendations": [
                "控制饮食中的糖分摄入，避免高糖食物",
                "保持每天7-8小时的睡眠时间",
                "继续保持适度运动，目标每日8000步",
                "建议每周测量2-3次血压并记录"
            ],
            "overallStatus": "good"
        }
        
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取健康报告失败")


# ============================================================================
# 心理健康/心情接口
# ============================================================================

@router.post("/psychology/mood", response_model=MoodRecordResponse)
async def record_mood(
    mood_data: MoodRecord,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """记录心情"""
    import uuid
    from datetime import datetime
    
    try:
        logger.info(f"用户 {current_user.id} 记录心情: {mood_data.mood}")
        
        # 心情分数映射
        mood_scores = {
            "happy": 5,
            "calm": 4,
            "tired": 3,
            "anxious": 2,
            "sad": 1
        }
        
        score = mood_scores.get(mood_data.mood, 3)
        
        # TODO: 保存到数据库
        # 目前返回模拟响应
        
        record = {
            "recordId": str(uuid.uuid4()),
            "mood": mood_data.mood,
            "score": score,
            "note": mood_data.note,
            "recordedAt": mood_data.timestamp or datetime.now().isoformat()
        }
        
        # 根据心情给出反馈
        messages = {
            "happy": "很高兴您今天心情愉快！保持好心情对健康很重要。",
            "calm": "平和的心态是健康的基石，继续保持！",
            "tired": "感到疲惫时要注意休息，适当放松一下。",
            "anxious": "如果感到焦虑，可以尝试深呼吸或散步放松。",
            "sad": "心情不好时可以和家人朋友聊聊，或者做些喜欢的事情。"
        }
        
        return {
            "success": True,
            "data": record,
            "message": messages.get(mood_data.mood, "心情已记录")
        }
    except Exception as e:
        logger.error(f"记录心情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="记录心情失败")