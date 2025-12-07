"""
Step 1: 用户画像定义
====================

定义10个虚拟用户的健康特征和行为模式
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum


class HealthStatus(Enum):
    """健康状态分类"""
    HEALTHY = "healthy"              # 健康
    HYPERTENSION = "hypertension"    # 高血压
    DIABETES = "diabetes"            # 糖尿病/前期
    SUBOPTIMAL = "suboptimal"        # 亚健康
    MULTIPLE = "multiple"            # 多病共存


@dataclass
class VitalSignsProfile:
    """生命体征画像"""
    # 血压 (收缩压, 舒张压) - (基础值, 波动范围)
    systolic: Tuple[int, int] = (120, 10)      # 收缩压: 基础120, ±10
    diastolic: Tuple[int, int] = (80, 6)       # 舒张压: 基础80, ±6
    
    # 心率
    heart_rate: Tuple[int, int] = (72, 8)      # 静息心率: 72, ±8
    
    # 血糖
    fasting_glucose: Tuple[float, float] = (5.2, 0.4)     # 空腹血糖
    postprandial_glucose: Tuple[float, float] = (7.0, 0.8) # 餐后血糖
    
    # 体温
    temperature: Tuple[float, float] = (36.5, 0.3)
    
    # 血氧
    spo2: Tuple[int, int] = (97, 1)


@dataclass
class LifestyleProfile:
    """生活方式画像"""
    # 睡眠
    sleep_duration: Tuple[float, float] = (7.0, 0.8)      # 睡眠时长
    deep_sleep_ratio: Tuple[float, float] = (0.20, 0.05)  # 深睡比例
    sleep_time: str = "22:00"                              # 入睡时间
    wake_time: str = "06:00"                               # 起床时间
    
    # 运动
    daily_steps: Tuple[int, int] = (6000, 2000)           # 日均步数
    active_days_per_week: int = 5                          # 每周活跃天数
    
    # 体重变化趋势
    weight_trend: float = 0.0                              # kg/周 (正=增重)


@dataclass
class UserProfile:
    """完整用户画像"""
    profile_id: str
    profile_name: str
    health_status: HealthStatus
    
    # 基础信息范围
    age_range: Tuple[int, int] = (65, 75)
    gender_ratio: float = 0.5                  # 女性比例
    bmi_range: Tuple[float, float] = (22, 26)
    
    # 健康特征
    vital_signs: VitalSignsProfile = field(default_factory=VitalSignsProfile)
    lifestyle: LifestyleProfile = field(default_factory=LifestyleProfile)
    
    # 病史和用药
    medical_history: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    
    # 数据特征
    missing_rate: float = 0.02                 # 缺失率
    outlier_rate: float = 0.02                 # 异常值率
    measurement_compliance: float = 0.9        # 测量依从性


# =============================================================================
# 10个用户画像定义
# =============================================================================

PROFILES: Dict[str, UserProfile] = {
    
    # =========================================================================
    # 1-2: 健康老人 (2人)
    # =========================================================================
    
    "healthy_1": UserProfile(
        profile_id="healthy_1",
        profile_name="健康老人A",
        health_status=HealthStatus.HEALTHY,
        age_range=(65, 70),
        gender_ratio=0.0,  # 男性
        bmi_range=(22, 24),
        vital_signs=VitalSignsProfile(
            systolic=(118, 8),
            diastolic=(75, 5),
            heart_rate=(68, 6),
            fasting_glucose=(5.0, 0.3),
            postprandial_glucose=(6.5, 0.5),
            temperature=(36.4, 0.2),
            spo2=(98, 1)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(7.5, 0.5),
            deep_sleep_ratio=(0.22, 0.04),
            sleep_time="21:30",
            wake_time="05:30",
            daily_steps=(8000, 1500),
            active_days_per_week=6,
            weight_trend=0.0
        ),
        medical_history=[],
        medications=[],
        measurement_compliance=0.95
    ),
    
    "healthy_2": UserProfile(
        profile_id="healthy_2",
        profile_name="健康老人B",
        health_status=HealthStatus.HEALTHY,
        age_range=(66, 72),
        gender_ratio=1.0,  # 女性
        bmi_range=(21, 23),
        vital_signs=VitalSignsProfile(
            systolic=(115, 8),
            diastolic=(72, 5),
            heart_rate=(70, 6),
            fasting_glucose=(4.8, 0.3),
            postprandial_glucose=(6.2, 0.5),
            temperature=(36.5, 0.2),
            spo2=(98, 1)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(7.0, 0.6),
            deep_sleep_ratio=(0.20, 0.04),
            sleep_time="22:00",
            wake_time="06:00",
            daily_steps=(7000, 1500),
            active_days_per_week=5,
            weight_trend=0.0
        ),
        medical_history=[],
        medications=[],
        measurement_compliance=0.92
    ),
    
    # =========================================================================
    # 3-4: 高血压患者 (2人)
    # =========================================================================
    
    "hypertension_1": UserProfile(
        profile_id="hypertension_1",
        profile_name="高血压患者A",
        health_status=HealthStatus.HYPERTENSION,
        age_range=(68, 75),
        gender_ratio=0.0,  # 男性
        bmi_range=(25, 28),
        vital_signs=VitalSignsProfile(
            systolic=(145, 12),      # 偏高
            diastolic=(92, 8),       # 偏高
            heart_rate=(76, 8),
            fasting_glucose=(5.5, 0.4),
            postprandial_glucose=(7.2, 0.6),
            temperature=(36.5, 0.3),
            spo2=(96, 2)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(6.5, 0.8),
            deep_sleep_ratio=(0.15, 0.05),  # 深睡减少
            sleep_time="23:00",
            wake_time="06:30",
            daily_steps=(5000, 1500),
            active_days_per_week=4,
            weight_trend=0.1
        ),
        medical_history=["高血压"],
        medications=["氨氯地平", "缬沙坦"],
        measurement_compliance=0.88
    ),
    
    "hypertension_2": UserProfile(
        profile_id="hypertension_2",
        profile_name="高血压患者B",
        health_status=HealthStatus.HYPERTENSION,
        age_range=(70, 78),
        gender_ratio=1.0,  # 女性
        bmi_range=(24, 27),
        vital_signs=VitalSignsProfile(
            systolic=(150, 15),      # 控制不佳
            diastolic=(95, 10),
            heart_rate=(78, 10),
            fasting_glucose=(5.8, 0.5),
            postprandial_glucose=(7.5, 0.7),
            temperature=(36.4, 0.3),
            spo2=(96, 2)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(6.0, 1.0),
            deep_sleep_ratio=(0.12, 0.04),
            sleep_time="23:30",
            wake_time="06:00",
            daily_steps=(4000, 1500),
            active_days_per_week=3,
            weight_trend=0.15
        ),
        medical_history=["高血压", "高血脂"],
        medications=["硝苯地平", "阿托伐他汀"],
        measurement_compliance=0.85
    ),
    
    # =========================================================================
    # 5-6: 糖尿病/前期 (2人)
    # =========================================================================
    
    "diabetes_1": UserProfile(
        profile_id="diabetes_1",
        profile_name="糖尿病前期A",
        health_status=HealthStatus.DIABETES,
        age_range=(65, 72),
        gender_ratio=0.0,  # 男性
        bmi_range=(26, 29),
        vital_signs=VitalSignsProfile(
            systolic=(128, 10),
            diastolic=(82, 6),
            heart_rate=(74, 8),
            fasting_glucose=(6.5, 0.5),      # 空腹血糖受损
            postprandial_glucose=(9.0, 1.0), # 餐后偏高
            temperature=(36.5, 0.3),
            spo2=(97, 1)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(6.5, 0.7),
            deep_sleep_ratio=(0.16, 0.04),
            sleep_time="22:30",
            wake_time="06:00",
            daily_steps=(5500, 1500),
            active_days_per_week=4,
            weight_trend=0.1
        ),
        medical_history=["糖尿病前期"],
        medications=["二甲双胍"],
        measurement_compliance=0.90
    ),
    
    "diabetes_2": UserProfile(
        profile_id="diabetes_2",
        profile_name="2型糖尿病B",
        health_status=HealthStatus.DIABETES,
        age_range=(68, 75),
        gender_ratio=1.0,  # 女性
        bmi_range=(27, 30),
        vital_signs=VitalSignsProfile(
            systolic=(132, 10),
            diastolic=(85, 7),
            heart_rate=(76, 8),
            fasting_glucose=(7.5, 0.8),       # 糖尿病
            postprandial_glucose=(11.0, 1.5), # 餐后高
            temperature=(36.4, 0.3),
            spo2=(96, 2)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(6.0, 0.8),
            deep_sleep_ratio=(0.14, 0.04),
            sleep_time="23:00",
            wake_time="06:30",
            daily_steps=(4500, 1500),
            active_days_per_week=3,
            weight_trend=0.2
        ),
        medical_history=["2型糖尿病", "高血脂"],
        medications=["二甲双胍", "格列美脲"],
        measurement_compliance=0.85
    ),
    
    # =========================================================================
    # 7-8: 亚健康老人 (2人)
    # =========================================================================
    
    "suboptimal_1": UserProfile(
        profile_id="suboptimal_1",
        profile_name="亚健康老人A",
        health_status=HealthStatus.SUBOPTIMAL,
        age_range=(70, 76),
        gender_ratio=0.0,  # 男性
        bmi_range=(24, 27),
        vital_signs=VitalSignsProfile(
            systolic=(130, 12),      # 正常高值
            diastolic=(85, 8),
            heart_rate=(75, 10),
            fasting_glucose=(5.8, 0.5),
            postprandial_glucose=(7.8, 0.8),
            temperature=(36.4, 0.3),
            spo2=(96, 2)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(5.5, 1.0),        # 睡眠不足
            deep_sleep_ratio=(0.12, 0.04),    # 深睡很少
            sleep_time="00:00",               # 晚睡
            wake_time="06:00",
            daily_steps=(3500, 1500),         # 运动很少
            active_days_per_week=2,
            weight_trend=0.2
        ),
        medical_history=["失眠"],
        medications=["褪黑素"],
        missing_rate=0.05,                    # 测量不规律
        measurement_compliance=0.75
    ),
    
    "suboptimal_2": UserProfile(
        profile_id="suboptimal_2",
        profile_name="亚健康老人B",
        health_status=HealthStatus.SUBOPTIMAL,
        age_range=(68, 74),
        gender_ratio=1.0,  # 女性
        bmi_range=(20, 22),  # 偏瘦
        vital_signs=VitalSignsProfile(
            systolic=(105, 10),      # 偏低
            diastolic=(65, 6),
            heart_rate=(80, 12),     # 波动大
            fasting_glucose=(5.2, 0.4),
            postprandial_glucose=(7.0, 0.6),
            temperature=(36.2, 0.3),
            spo2=(95, 2)             # 偏低
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(5.0, 1.2),
            deep_sleep_ratio=(0.10, 0.04),
            sleep_time="23:30",
            wake_time="05:00",
            daily_steps=(3000, 1000),
            active_days_per_week=2,
            weight_trend=-0.1                 # 体重下降
        ),
        medical_history=["贫血", "焦虑"],
        medications=["铁剂"],
        missing_rate=0.08,
        measurement_compliance=0.70
    ),
    
    # =========================================================================
    # 9-10: 多病共存 (2人)
    # =========================================================================
    
    "multiple_1": UserProfile(
        profile_id="multiple_1",
        profile_name="多病共存A",
        health_status=HealthStatus.MULTIPLE,
        age_range=(72, 80),
        gender_ratio=0.0,  # 男性
        bmi_range=(28, 32),
        vital_signs=VitalSignsProfile(
            systolic=(155, 15),      # 高血压
            diastolic=(98, 10),
            heart_rate=(82, 12),
            fasting_glucose=(7.8, 0.8),       # 糖尿病
            postprandial_glucose=(12.0, 1.5),
            temperature=(36.5, 0.3),
            spo2=(94, 3)             # 偏低
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(5.5, 1.0),
            deep_sleep_ratio=(0.10, 0.04),
            sleep_time="23:00",
            wake_time="05:30",
            daily_steps=(3000, 1000),
            active_days_per_week=2,
            weight_trend=0.1
        ),
        medical_history=["高血压", "2型糖尿病", "高血脂", "冠心病"],
        medications=["氨氯地平", "二甲双胍", "阿司匹林", "阿托伐他汀"],
        outlier_rate=0.05,            # 更多异常
        measurement_compliance=0.80
    ),
    
    "multiple_2": UserProfile(
        profile_id="multiple_2",
        profile_name="多病共存B",
        health_status=HealthStatus.MULTIPLE,
        age_range=(75, 82),
        gender_ratio=1.0,  # 女性
        bmi_range=(26, 30),
        vital_signs=VitalSignsProfile(
            systolic=(160, 18),      # 高血压控制差
            diastolic=(100, 12),
            heart_rate=(85, 15),     # 波动大
            fasting_glucose=(8.5, 1.0),
            postprandial_glucose=(13.0, 2.0),
            temperature=(36.4, 0.4),
            spo2=(93, 3)
        ),
        lifestyle=LifestyleProfile(
            sleep_duration=(5.0, 1.2),
            deep_sleep_ratio=(0.08, 0.04),
            sleep_time="22:00",
            wake_time="04:30",
            daily_steps=(2500, 1000),
            active_days_per_week=1,
            weight_trend=0.0
        ),
        medical_history=["高血压", "2型糖尿病", "慢性肾病", "骨质疏松"],
        medications=["硝苯地平", "胰岛素", "钙片", "降压药"],
        outlier_rate=0.06,
        missing_rate=0.05,
        measurement_compliance=0.75
    ),
}


def get_all_profiles() -> List[UserProfile]:
    """获取所有用户画像"""
    return list(PROFILES.values())


def get_profile(profile_id: str) -> Optional[UserProfile]:
    """获取指定画像"""
    return PROFILES.get(profile_id)


def get_profiles_by_status(status: HealthStatus) -> List[UserProfile]:
    """按健康状态获取画像"""
    return [p for p in PROFILES.values() if p.health_status == status]


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("用户画像定义")
    print("=" * 60)
    
    profiles = get_all_profiles()
    print(f"\n共定义 {len(profiles)} 个用户画像:\n")
    
    for p in profiles:
        bp = p.vital_signs
        ls = p.lifestyle
        print(f"  {p.profile_id}: {p.profile_name}")
        print(f"    健康状态: {p.health_status.value}")
        print(f"    年龄范围: {p.age_range[0]}-{p.age_range[1]}岁")
        print(f"    血压基础: {bp.systolic[0]}/{bp.diastolic[0]} mmHg")
        print(f"    空腹血糖: {bp.fasting_glucose[0]} mmol/L")
        print(f"    日均步数: {ls.daily_steps[0]} 步")
        print(f"    病史: {p.medical_history or '无'}")
        print()
    
    print("✓ 用户画像定义完成")
