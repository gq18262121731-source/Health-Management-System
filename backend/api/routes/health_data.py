"""
健康数据 API 路由
提供健康数据的 CRUD 操作
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import uuid

from database.database import get_db
from database.models import (
    User, ElderlyProfile, HealthRecord, SleepData, HealthRecordStatus
)

router = APIRouter()


# ============================================================================
# 响应模型
# ============================================================================

class VitalSigns(BaseModel):
    temperature: dict
    bloodSugar: dict
    bloodPressure: dict
    heartRate: dict
    spo2: dict


class Activity(BaseModel):
    steps: int
    goal: int
    percentage: int
    distance: float
    calories: int


class Weight(BaseModel):
    value: float
    unit: str
    bmi: float
    bmiStatus: str


class TodayHealthResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class ChartDataResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# ============================================================================
# API 路由
# ============================================================================

@router.get("/today")
async def get_today_health(
    user_id: str = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取今日健康数据"""
    try:
        # 查找老人档案
        elderly = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == user_id
        ).first()
        
        # 如果按 user_id 找不到，尝试按 username 匹配
        if not elderly:
            user = db.query(User).filter(
                User.username.like(f"%{user_id}%")
            ).first()
            if user:
                elderly = db.query(ElderlyProfile).filter(
                    ElderlyProfile.user_id == user.id
                ).first()
        
        if not elderly:
            # 返回默认数据
            return get_default_health_data()
        
        # 获取今日最新的健康记录
        today = datetime.now().date()
        latest_record = db.query(HealthRecord).filter(
            HealthRecord.elderly_id == elderly.id,
            func.date(HealthRecord.recorded_at) == today
        ).order_by(desc(HealthRecord.recorded_at)).first()
        
        # 获取今日步数总和
        today_steps = db.query(func.max(HealthRecord.steps)).filter(
            HealthRecord.elderly_id == elderly.id,
            func.date(HealthRecord.recorded_at) == today
        ).scalar() or 0
        
        # 计算 BMI
        height_m = (elderly.height or 170) / 100
        weight = elderly.weight or 65
        bmi = round(weight / (height_m ** 2), 1)
        bmi_status = get_bmi_status(bmi)
        
        if latest_record:
            data = {
                "userId": user_id,
                "userName": elderly.name,
                "vitalSigns": {
                    "temperature": {
                        "value": latest_record.temperature or 36.5,
                        "unit": "°C",
                        "change": 0,
                        "status": get_temp_status(latest_record.temperature or 36.5)
                    },
                    "bloodSugar": {
                        "value": latest_record.blood_sugar or 5.2,
                        "unit": "mmol/L",
                        "status": get_blood_sugar_status(latest_record.blood_sugar or 5.2),
                        "testType": "空腹"
                    },
                    "bloodPressure": {
                        "systolic": latest_record.systolic_pressure or 120,
                        "diastolic": latest_record.diastolic_pressure or 80,
                        "unit": "mmHg",
                        "status": get_bp_status(
                            latest_record.systolic_pressure or 120,
                            latest_record.diastolic_pressure or 80
                        )
                    },
                    "heartRate": {
                        "value": latest_record.heart_rate or 72,
                        "unit": "bpm",
                        "change": 0,
                        "status": get_hr_status(latest_record.heart_rate or 72)
                    },
                    "spo2": {
                        "value": latest_record.blood_oxygen or 98,
                        "unit": "%",
                        "status": get_spo2_status(latest_record.blood_oxygen or 98)
                    }
                },
                "activity": {
                    "steps": today_steps,
                    "goal": 10000,
                    "percentage": min(100, int(today_steps / 100)),
                    "distance": round(today_steps * 0.0007, 1),
                    "calories": int(today_steps * 0.04)
                },
                "weight": {
                    "value": weight,
                    "unit": "kg",
                    "bmi": bmi,
                    "bmiStatus": bmi_status
                }
            }
        else:
            # 没有今日数据，返回默认值
            return get_default_health_data()
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/charts")
async def get_chart_data(
    user_id: str = Query(..., description="用户ID"),
    days: int = Query(7, description="天数"),
    db: Session = Depends(get_db)
):
    """获取图表数据"""
    try:
        # 查找老人档案
        elderly = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == user_id
        ).first()
        
        if not elderly:
            user = db.query(User).filter(
                User.username.like(f"%{user_id}%")
            ).first()
            if user:
                elderly = db.query(ElderlyProfile).filter(
                    ElderlyProfile.user_id == user.id
                ).first()
        
        if not elderly:
            return get_default_chart_data()
        
        # 获取历史健康记录
        start_date = datetime.now() - timedelta(days=days)
        records = db.query(HealthRecord).filter(
            HealthRecord.elderly_id == elderly.id,
            HealthRecord.recorded_at >= start_date
        ).order_by(HealthRecord.recorded_at).all()
        
        # 获取睡眠数据
        sleep_records = db.query(SleepData).filter(
            SleepData.elderly_id == elderly.id,
            SleepData.date >= start_date.date()
        ).order_by(SleepData.date).all()
        
        # 处理心率数据
        heart_rate_data = []
        for r in records[-24:]:  # 最近24条
            heart_rate_data.append({
                "time": r.recorded_at.strftime("%H:%M"),
                "value": r.heart_rate or 72
            })
        
        # 处理血压数据（按天聚合）
        bp_data = {}
        for r in records:
            day = r.recorded_at.strftime("%m-%d")
            if day not in bp_data:
                bp_data[day] = {
                    "systolic": [],
                    "diastolic": []
                }
            if r.systolic_pressure:
                bp_data[day]["systolic"].append(r.systolic_pressure)
            if r.diastolic_pressure:
                bp_data[day]["diastolic"].append(r.diastolic_pressure)
        
        blood_pressure_data = []
        for day, values in bp_data.items():
            if values["systolic"] and values["diastolic"]:
                blood_pressure_data.append({
                    "day": day,
                    "systolic": int(sum(values["systolic"]) / len(values["systolic"])),
                    "diastolic": int(sum(values["diastolic"]) / len(values["diastolic"])),
                    "normalHigh": 120,
                    "normalLow": 80
                })
        
        # 处理睡眠数据
        sleep_data = []
        for s in sleep_records:
            sleep_data.append({
                "date": s.date.strftime("%Y-%m-%d") if hasattr(s.date, 'strftime') else str(s.date),
                "duration": s.total_hours,
                "quality": "good" if s.quality >= 70 else "fair"
            })
        
        # 健康雷达图数据
        radar_data = [
            {"subject": "心血管", "value": 85},
            {"subject": "睡眠", "value": 75},
            {"subject": "运动", "value": 70},
            {"subject": "营养", "value": 80},
            {"subject": "心理", "value": 88},
            {"subject": "免疫", "value": 82}
        ]
        
        return {
            "success": True,
            "data": {
                "heartRate": heart_rate_data,
                "bloodPressure": blood_pressure_data,
                "sleep": sleep_data,
                "healthRadar": radar_data
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/visualization")
async def get_visualization_data(
    user_id: str = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取可视化数据"""
    return {
        "success": True,
        "data": {
            "radar_data": [
                {"dimension": "心血管", "score": 85, "max": 100},
                {"dimension": "睡眠质量", "score": 75, "max": 100},
                {"dimension": "运动健康", "score": 70, "max": 100},
                {"dimension": "营养状态", "score": 80, "max": 100},
                {"dimension": "心理健康", "score": 88, "max": 100},
                {"dimension": "免疫功能", "score": 82, "max": 100},
            ],
            "trend_data": [
                {"metric": "血压", "direction": "stable", "deviation": 2},
                {"metric": "心率", "direction": "improving", "deviation": -3},
                {"metric": "睡眠", "direction": "improving", "deviation": 5},
            ],
            "risk_distribution": {
                "high": 1,
                "medium": 2,
                "low": 5,
            }
        }
    }


# ============================================================================
# 辅助函数
# ============================================================================

def get_default_health_data():
    """返回默认健康数据"""
    return {
        "success": True,
        "data": {
            "userId": "elderly_001",
            "userName": "张三",
            "vitalSigns": {
                "temperature": {"value": 36.5, "unit": "°C", "change": 0, "status": "正常"},
                "bloodSugar": {"value": 5.2, "unit": "mmol/L", "status": "正常", "testType": "空腹"},
                "bloodPressure": {"systolic": 118, "diastolic": 75, "unit": "mmHg", "status": "正常"},
                "heartRate": {"value": 72, "unit": "bpm", "change": 0, "status": "正常"},
                "spo2": {"value": 98, "unit": "%", "status": "正常"},
            },
            "activity": {
                "steps": 6500,
                "goal": 10000,
                "percentage": 65,
                "distance": 4.5,
                "calories": 260
            },
            "weight": {
                "value": 65,
                "unit": "kg",
                "bmi": 22.5,
                "bmiStatus": "正常"
            }
        }
    }


def get_default_chart_data():
    """返回默认图表数据"""
    return {
        "success": True,
        "data": {
            "heartRate": [{"time": f"{h:02d}:00", "value": 70 + (h % 10)} for h in range(24)],
            "bloodPressure": [],
            "sleep": [],
            "healthRadar": [
                {"subject": "心血管", "value": 85},
                {"subject": "睡眠", "value": 75},
                {"subject": "运动", "value": 70},
                {"subject": "营养", "value": 80},
                {"subject": "心理", "value": 88},
                {"subject": "免疫", "value": 82}
            ]
        }
    }


def get_temp_status(temp: float) -> str:
    if temp < 36.0:
        return "偏低"
    elif temp > 37.3:
        return "发热"
    return "正常"


def get_blood_sugar_status(value: float) -> str:
    if value < 3.9:
        return "偏低"
    elif value > 6.1:
        return "偏高"
    return "正常"


def get_bp_status(systolic: int, diastolic: int) -> str:
    if systolic >= 140 or diastolic >= 90:
        return "偏高"
    elif systolic < 90 or diastolic < 60:
        return "偏低"
    return "正常"


def get_hr_status(hr: int) -> str:
    if hr < 60:
        return "偏低"
    elif hr > 100:
        return "偏高"
    return "正常"


def get_spo2_status(spo2: float) -> str:
    if spo2 < 95:
        return "偏低"
    return "正常"


def get_bmi_status(bmi: float) -> str:
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常"
    elif bmi < 28:
        return "偏胖"
    return "肥胖"
