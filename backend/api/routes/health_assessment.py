"""
健康评估API路由
===============

提供专业的健康风险评估接口，集成模糊逻辑、AHP、TOPSIS等算法。
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
import uuid

from database.database import get_db
from api.auth import get_current_active_user
from database.models import User, HealthRecord, ElderlyProfile

# 导入健康评估服务
try:
    from services.health_assessment.assessment_service import health_assessment_service
    HAS_ASSESSMENT = True
except ImportError as e:
    HAS_ASSESSMENT = False
    health_assessment_service = None
    logging.warning(f"健康评估模块加载失败: {e}")

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== 请求/响应模型 ==========

class BloodPressureAssessmentRequest(BaseModel):
    """血压评估请求"""
    systolic_values: List[float] = Field(..., description="收缩压数据列表")
    diastolic_values: List[float] = Field(..., description="舒张压数据列表")
    baseline: Optional[Dict[str, Any]] = Field(None, description="基线数据")


class BloodSugarAssessmentRequest(BaseModel):
    """血糖评估请求"""
    fasting_values: List[float] = Field(..., description="空腹血糖数据列表")
    postprandial_values: Optional[List[float]] = Field(None, description="餐后血糖数据列表")
    baseline: Optional[Dict[str, Any]] = Field(None, description="基线数据")


class LifestyleAssessmentRequest(BaseModel):
    """生活方式评估请求"""
    sleep_data: Optional[Dict[str, Any]] = Field(None, description="睡眠数据")
    exercise_data: Optional[Dict[str, Any]] = Field(None, description="运动数据")
    diet_data: Optional[Dict[str, Any]] = Field(None, description="饮食数据")


class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""
    metric_name: str = Field(..., description="指标名称 (systolic_bp, blood_sugar, heart_rate)")
    values: List[float] = Field(..., description="数值列表")


class ComprehensiveAssessmentRequest(BaseModel):
    """综合评估请求"""
    elderly_id: Optional[str] = Field(None, description="老人ID（可选，用于从数据库获取数据）")
    days: int = Field(30, description="评估数据天数")
    blood_pressure: Optional[Dict[str, List[float]]] = Field(None, description="血压数据")
    blood_sugar: Optional[Dict[str, List[float]]] = Field(None, description="血糖数据")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活方式数据")


class AssessmentResponse(BaseModel):
    """评估响应"""
    status: str = "success"
    data: Dict[str, Any]
    message: str = "评估完成"


# ========== API 路由 ==========

@router.post("/blood-pressure", response_model=AssessmentResponse)
async def assess_blood_pressure(
    request: BloodPressureAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    血压风险评估
    
    使用模糊逻辑算法评估血压控制情况和风险等级。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        result = health_assessment_service.assess_blood_pressure(
            request.systolic_values,
            request.diastolic_values,
            request.baseline
        )
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="血压评估完成"
        )
    except Exception as e:
        logger.error(f"血压评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估失败: {str(e)}"
        )


@router.post("/blood-sugar", response_model=AssessmentResponse)
async def assess_blood_sugar(
    request: BloodSugarAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    血糖风险评估
    
    评估血糖控制情况和糖尿病风险。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        result = health_assessment_service.assess_blood_sugar(
            request.fasting_values,
            request.postprandial_values,
            request.baseline
        )
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="血糖评估完成"
        )
    except Exception as e:
        logger.error(f"血糖评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估失败: {str(e)}"
        )


@router.post("/lifestyle", response_model=AssessmentResponse)
async def assess_lifestyle(
    request: LifestyleAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    生活方式评估
    
    评估睡眠、运动、饮食等生活方式风险。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        result = health_assessment_service.assess_lifestyle(
            request.sleep_data,
            request.exercise_data,
            request.diet_data
        )
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="生活方式评估完成"
        )
    except Exception as e:
        logger.error(f"生活方式评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估失败: {str(e)}"
        )


@router.post("/trend", response_model=AssessmentResponse)
async def analyze_trend(
    request: TrendAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    健康趋势分析
    
    分析健康指标的变化趋势，检测异常波动。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        result = health_assessment_service.analyze_trend(
            request.metric_name,
            request.values
        )
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="趋势分析完成"
        )
    except Exception as e:
        logger.error(f"趋势分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.post("/comprehensive", response_model=AssessmentResponse)
async def comprehensive_assessment(
    request: ComprehensiveAssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    综合健康评估
    
    整合多维度数据，使用AHP+TOPSIS算法进行综合风险评估。
    返回综合评分、健康等级、TOP风险因素和建议。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        health_data = {}
        
        # 如果提供了elderly_id，从数据库获取数据
        if request.elderly_id:
            elderly_uuid = uuid.UUID(request.elderly_id)
            health_data = await _get_health_data_from_db(db, elderly_uuid, request.days)
        
        # 合并请求中的数据
        if request.blood_pressure:
            health_data['blood_pressure'] = request.blood_pressure
        if request.blood_sugar:
            health_data['blood_sugar'] = request.blood_sugar
        if request.lifestyle:
            health_data['lifestyle'] = request.lifestyle
        
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请提供健康数据或有效的老人ID"
            )
        
        result = health_assessment_service.comprehensive_assessment(health_data)
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="综合评估完成"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估失败: {str(e)}"
        )


@router.get("/elderly/{elderly_id}", response_model=AssessmentResponse)
async def get_elderly_assessment(
    elderly_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取老人的综合健康评估
    
    根据老人ID自动获取健康数据并进行综合评估。
    """
    if not HAS_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="健康评估服务暂不可用"
        )
    
    try:
        elderly_uuid = uuid.UUID(elderly_id)
        
        # 验证老人存在
        elderly = db.query(ElderlyProfile).filter(ElderlyProfile.id == elderly_uuid).first()
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人档案不存在"
            )
        
        # 从数据库获取健康数据
        health_data = await _get_health_data_from_db(db, elderly_uuid, days)
        
        if not health_data:
            return AssessmentResponse(
                status="warning",
                data={
                    "overall_score": 0,
                    "health_level": "unknown",
                    "message": "健康数据不足，无法进行评估"
                },
                message="数据不足"
            )
        
        result = health_assessment_service.comprehensive_assessment(health_data)
        
        # 添加老人基本信息
        result['elderly_info'] = {
            'id': str(elderly.id),
            'name': elderly.name,
            'age': elderly.age if hasattr(elderly, 'age') else None
        }
        
        return AssessmentResponse(
            status="success",
            data=result,
            message="评估完成"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取老人评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估失败: {str(e)}"
        )


@router.get("/status")
async def get_assessment_status():
    """
    获取健康评估服务状态
    """
    return {
        "status": "available" if HAS_ASSESSMENT else "unavailable",
        "algorithms": [
            "模糊逻辑 (Fuzzy Logic)",
            "AHP层次分析法",
            "TOPSIS多准则决策",
            "Isolation Forest异常检测",
            "线性回归趋势分析"
        ] if HAS_ASSESSMENT else [],
        "capabilities": [
            "血压风险评估",
            "血糖风险评估",
            "生活方式评估",
            "趋势预警分析",
            "综合健康评估"
        ] if HAS_ASSESSMENT else []
    }


# ========== 辅助函数 ==========

async def _get_health_data_from_db(
    db: Session,
    elderly_id: uuid.UUID,
    days: int = 30
) -> Dict[str, Any]:
    """
    从数据库获取健康数据
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    health_data = {}
    
    try:
        # 获取健康记录
        records = db.query(HealthRecord).filter(
            HealthRecord.elderly_id == elderly_id,
            HealthRecord.created_at >= start_date,
            HealthRecord.created_at <= end_date
        ).order_by(HealthRecord.created_at).all()
        
        if not records:
            return {}
        
        # 提取血压数据
        systolic_values = []
        diastolic_values = []
        fasting_values = []
        heart_rate_values = []
        
        for record in records:
            if record.systolic_pressure and record.diastolic_pressure:
                systolic_values.append(float(record.systolic_pressure))
                diastolic_values.append(float(record.diastolic_pressure))
            
            if record.blood_sugar:
                fasting_values.append(float(record.blood_sugar))
            
            if record.heart_rate:
                heart_rate_values.append(float(record.heart_rate))
        
        if systolic_values and diastolic_values:
            health_data['blood_pressure'] = {
                'systolic': systolic_values,
                'diastolic': diastolic_values
            }
        
        if fasting_values:
            health_data['blood_sugar'] = {
                'fasting': fasting_values
            }
        
        if heart_rate_values:
            health_data['heart_rate'] = heart_rate_values
        
        return health_data
        
    except Exception as e:
        logger.error(f"获取健康数据失败: {e}")
        return {}
