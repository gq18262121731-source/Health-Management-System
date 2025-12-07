"""
Step 3: 健康数据生成器
======================

根据用户画像生成30天的健康监测数据
包含时间规律、随机波动、异常值
"""

import random
import math
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from user_profiles import get_profile, UserProfile, VitalSignsProfile, LifestyleProfile
from user_generator import User, generate_users


# =============================================================================
# 数据记录模型
# =============================================================================

@dataclass
class HealthRecord:
    """健康记录"""
    record_id: str
    user_id: str
    data_type: str
    timestamp: str
    values: Dict
    is_outlier: bool = False
    is_missing: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# 健康数据生成器
# =============================================================================

class HealthDataGenerator:
    """健康数据生成器"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.record_counter = 0
    
    def _next_record_id(self) -> str:
        """生成记录ID"""
        self.record_counter += 1
        return f"REC_{self.record_counter:06d}"
    
    def _add_noise(self, base: float, std: float) -> float:
        """添加高斯噪声"""
        return base + random.gauss(0, std)
    
    def _time_factor(self, hour: int, data_type: str) -> float:
        """
        时间因素调整
        返回一个乘数或加数，用于模拟日内变化
        """
        if data_type == "blood_pressure":
            # 晨峰效应：6-10点血压较高
            if 6 <= hour <= 10:
                return random.uniform(5, 15)  # 加5-15
            elif 14 <= hour <= 16:
                return random.uniform(-5, 0)  # 减0-5
            elif 22 <= hour or hour <= 4:
                return random.uniform(-8, -3)  # 减3-8
            return 0
        
        elif data_type == "heart_rate":
            # 睡眠时心率低，活动时高
            if 0 <= hour <= 5:
                return random.uniform(-12, -8)
            elif 10 <= hour <= 18:
                return random.uniform(3, 10)
            return 0
        
        elif data_type == "temperature":
            # 下午体温略高
            if 14 <= hour <= 18:
                return random.uniform(0.2, 0.4)
            elif 2 <= hour <= 6:
                return random.uniform(-0.3, -0.1)
            return 0
        
        return 0
    
    def _weekend_factor(self, weekday: int, data_type: str) -> float:
        """周末因素调整"""
        is_weekend = weekday >= 5  # 周六=5, 周日=6
        
        if data_type == "steps" and is_weekend:
            return random.uniform(0.7, 0.9)  # 周末步数减少
        elif data_type == "sleep" and is_weekend:
            return random.uniform(1.0, 1.2)  # 周末睡眠可能更长
        
        return 1.0
    
    def _should_create_outlier(self, rate: float) -> bool:
        """是否生成异常值"""
        return random.random() < rate
    
    def _should_skip(self, compliance: float) -> bool:
        """是否跳过（模拟漏测）"""
        return random.random() > compliance
    
    # =========================================================================
    # 各类型数据生成
    # =========================================================================
    
    def generate_blood_pressure(
        self,
        user_id: str,
        profile: VitalSignsProfile,
        dt: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成血压数据"""
        
        hour = dt.hour
        time_adj = self._time_factor(hour, "blood_pressure")
        
        # 基础值 + 时间调整 + 随机波动
        systolic = profile.systolic[0] + time_adj + random.gauss(0, profile.systolic[1])
        diastolic = profile.diastolic[0] + time_adj * 0.5 + random.gauss(0, profile.diastolic[1])
        pulse = profile.heart_rate[0] + random.gauss(0, 5)
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            if random.random() > 0.5:
                systolic += random.uniform(30, 50)
                diastolic += random.uniform(15, 25)
            else:
                systolic -= random.uniform(20, 40)
                diastolic -= random.uniform(10, 20)
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="blood_pressure",
            timestamp=dt.isoformat(),
            values={
                "systolic": round(max(70, min(220, systolic))),
                "diastolic": round(max(40, min(140, diastolic))),
                "pulse": round(max(40, min(150, pulse))),
                "position": "sitting",
                "arm": random.choice(["left", "right"])
            },
            is_outlier=is_outlier
        )
    
    def generate_glucose(
        self,
        user_id: str,
        profile: VitalSignsProfile,
        dt: datetime,
        test_type: str,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成血糖数据"""
        
        if test_type == "fasting":
            base, std = profile.fasting_glucose
            meal_time = "breakfast"
        else:
            base, std = profile.postprandial_glucose
            meal_time = random.choice(["breakfast", "lunch", "dinner"])
        
        value = self._add_noise(base, std)
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            value += random.uniform(3, 8)
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="glucose",
            timestamp=dt.isoformat(),
            values={
                "value": round(max(2.0, min(30.0, value)), 1),
                "test_type": test_type,
                "meal_time": meal_time
            },
            is_outlier=is_outlier
        )
    
    def generate_heart_rate(
        self,
        user_id: str,
        profile: VitalSignsProfile,
        dt: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成心率数据"""
        
        hour = dt.hour
        time_adj = self._time_factor(hour, "heart_rate")
        
        base, std = profile.heart_rate
        value = base + time_adj + random.gauss(0, std)
        
        # 活动级别
        if 0 <= hour <= 5:
            activity = "sleep"
        elif 6 <= hour <= 8 or 17 <= hour <= 19:
            activity = random.choice(["light", "moderate"])
        else:
            activity = "rest"
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            value += random.choice([-30, 40])
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="heart_rate",
            timestamp=dt.isoformat(),
            values={
                "value": round(max(35, min(180, value))),
                "activity_level": activity,
                "is_resting": activity in ["rest", "sleep"]
            },
            is_outlier=is_outlier
        )
    
    def generate_sleep(
        self,
        user_id: str,
        profile: LifestyleProfile,
        date: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成睡眠数据"""
        
        weekday = date.weekday()
        weekend_factor = self._weekend_factor(weekday, "sleep")
        
        # 睡眠时长
        base_duration, std = profile.sleep_duration
        duration = (base_duration + random.gauss(0, std)) * weekend_factor
        duration = max(3, min(12, duration))
        
        # 深睡比例
        deep_ratio = profile.deep_sleep_ratio[0] + random.gauss(0, profile.deep_sleep_ratio[1])
        deep_ratio = max(0.05, min(0.35, deep_ratio))
        
        deep_sleep = duration * deep_ratio
        rem_sleep = duration * random.uniform(0.15, 0.25)
        light_sleep = duration - deep_sleep - rem_sleep
        
        # 夜醒次数
        awake_times = random.randint(0, 4)
        
        # 睡眠质量评分
        quality = int(70 + (deep_ratio - 0.15) * 200 + (duration - 6) * 5 - awake_times * 5)
        quality = max(30, min(100, quality))
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            duration = random.choice([2.5, 3.0, 12.0, 13.0])
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="sleep",
            timestamp=date.strftime("%Y-%m-%d") + "T08:00:00",
            values={
                "duration": round(duration, 1),
                "deep_sleep": round(deep_sleep, 1),
                "light_sleep": round(max(0, light_sleep), 1),
                "rem_sleep": round(rem_sleep, 1),
                "awake_times": awake_times,
                "quality_score": quality,
                "sleep_time": profile.sleep_time,
                "wake_time": profile.wake_time
            },
            is_outlier=is_outlier
        )
    
    def generate_steps(
        self,
        user_id: str,
        profile: LifestyleProfile,
        date: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成步数数据"""
        
        weekday = date.weekday()
        weekend_factor = self._weekend_factor(weekday, "steps")
        
        # 是否活跃日
        is_active_day = random.random() < (profile.active_days_per_week / 7)
        
        base, std = profile.daily_steps
        if is_active_day:
            steps = (base + random.gauss(0, std)) * weekend_factor
        else:
            steps = (base * 0.5 + random.gauss(0, std * 0.5)) * weekend_factor
        
        steps = max(500, int(steps))
        
        # 计算距离和卡路里
        distance = round(steps * 0.0007, 2)  # km
        calories = round(steps * 0.04)       # kcal
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            steps = random.choice([50, 100, 35000, 40000])
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="steps",
            timestamp=date.strftime("%Y-%m-%d") + "T23:59:00",
            values={
                "value": steps,
                "distance": distance,
                "calories": calories,
                "active_minutes": int(steps / 100)
            },
            is_outlier=is_outlier
        )
    
    def generate_weight(
        self,
        user_id: str,
        base_weight: float,
        base_height: float,
        profile: LifestyleProfile,
        date: datetime,
        day_index: int
    ) -> Optional[HealthRecord]:
        """生成体重数据"""
        
        # 体重趋势 + 日波动
        trend = profile.weight_trend * (day_index / 7)  # 每周变化
        daily_var = random.gauss(0, 0.3)                # 日波动
        
        weight = base_weight + trend + daily_var
        weight = max(30, round(weight, 1))
        
        # BMI
        height_m = base_height / 100
        bmi = round(weight / (height_m ** 2), 1)
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="weight",
            timestamp=date.strftime("%Y-%m-%d") + "T07:00:00",
            values={
                "value": weight,
                "bmi": bmi,
                "body_fat": round(random.uniform(20, 35), 1) if random.random() > 0.5 else None
            }
        )
    
    def generate_temperature(
        self,
        user_id: str,
        profile: VitalSignsProfile,
        dt: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成体温数据"""
        
        hour = dt.hour
        time_adj = self._time_factor(hour, "temperature")
        
        base, std = profile.temperature
        value = base + time_adj + random.gauss(0, std)
        
        # 异常值（发烧）
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            value = random.uniform(37.8, 39.0)
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="temperature",
            timestamp=dt.isoformat(),
            values={
                "value": round(max(35.0, min(42.0, value)), 1),
                "measurement_site": random.choice(["forehead", "armpit"])
            },
            is_outlier=is_outlier
        )
    
    def generate_spo2(
        self,
        user_id: str,
        profile: VitalSignsProfile,
        dt: datetime,
        outlier_rate: float
    ) -> Optional[HealthRecord]:
        """生成血氧数据"""
        
        base, std = profile.spo2
        value = base + random.gauss(0, std)
        
        # 异常值
        is_outlier = False
        if self._should_create_outlier(outlier_rate):
            is_outlier = True
            value = random.randint(85, 90)
        
        return HealthRecord(
            record_id=self._next_record_id(),
            user_id=user_id,
            data_type="spo2",
            timestamp=dt.isoformat(),
            values={
                "value": round(max(80, min(100, value))),
                "perfusion_index": round(random.uniform(1, 5), 1)
            },
            is_outlier=is_outlier
        )
    
    # =========================================================================
    # 主生成函数
    # =========================================================================
    
    def generate_user_data(
        self,
        user: User,
        days: int = 30
    ) -> List[HealthRecord]:
        """生成单个用户的全部健康数据"""
        
        profile = get_profile(user.profile_id)
        if not profile:
            return []
        
        vs = profile.vital_signs
        ls = profile.lifestyle
        records = []
        
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)
        
        for day_idx in range(days):
            current_date = start_date + timedelta(days=day_idx)
            weekday = current_date.weekday()
            
            # 跳过检查（依从性）
            skip_today = self._should_skip(profile.measurement_compliance)
            
            # ----- 血压 (早晚各1次) -----
            if not skip_today or random.random() > 0.5:
                # 早晨测量 7-9点
                morning_bp_time = current_date.replace(
                    hour=random.randint(7, 9),
                    minute=random.randint(0, 59)
                )
                rec = self.generate_blood_pressure(
                    user.user_id, vs, morning_bp_time, profile.outlier_rate
                )
                if rec:
                    records.append(rec)
                
                # 晚间测量 19-21点
                evening_bp_time = current_date.replace(
                    hour=random.randint(19, 21),
                    minute=random.randint(0, 59)
                )
                rec = self.generate_blood_pressure(
                    user.user_id, vs, evening_bp_time, profile.outlier_rate
                )
                if rec:
                    records.append(rec)
            
            # ----- 血糖 (空腹 + 偶尔餐后) -----
            if not skip_today:
                # 空腹血糖
                fasting_time = current_date.replace(hour=7, minute=random.randint(0, 30))
                rec = self.generate_glucose(
                    user.user_id, vs, fasting_time, "fasting", profile.outlier_rate
                )
                if rec:
                    records.append(rec)
                
                # 餐后血糖（50%概率）
                if random.random() > 0.5:
                    postprandial_time = current_date.replace(
                        hour=random.choice([10, 14, 20]),
                        minute=random.randint(0, 30)
                    )
                    rec = self.generate_glucose(
                        user.user_id, vs, postprandial_time, "postprandial", profile.outlier_rate
                    )
                    if rec:
                        records.append(rec)
            
            # ----- 心率 (每6小时) -----
            for hour in [6, 12, 18, 23]:
                hr_time = current_date.replace(hour=hour, minute=random.randint(0, 30))
                rec = self.generate_heart_rate(
                    user.user_id, vs, hr_time, profile.outlier_rate
                )
                if rec:
                    records.append(rec)
            
            # ----- 睡眠 (每日1条) -----
            rec = self.generate_sleep(user.user_id, ls, current_date, profile.outlier_rate)
            if rec:
                records.append(rec)
            
            # ----- 步数 (每日1条) -----
            rec = self.generate_steps(user.user_id, ls, current_date, profile.outlier_rate)
            if rec:
                records.append(rec)
            
            # ----- 体重 (每日1条) -----
            rec = self.generate_weight(
                user.user_id, user.weight, user.height, ls, current_date, day_idx
            )
            if rec:
                records.append(rec)
            
            # ----- 体温 (每日1次) -----
            temp_time = current_date.replace(hour=8, minute=random.randint(0, 30))
            rec = self.generate_temperature(user.user_id, vs, temp_time, profile.outlier_rate)
            if rec:
                records.append(rec)
            
            # ----- 血氧 (早晚各1次) -----
            for hour in [8, 20]:
                spo2_time = current_date.replace(hour=hour, minute=random.randint(0, 30))
                rec = self.generate_spo2(user.user_id, vs, spo2_time, profile.outlier_rate)
                if rec:
                    records.append(rec)
        
        return records
    
    def generate_all_data(
        self,
        users: List[User],
        days: int = 30
    ) -> List[HealthRecord]:
        """生成所有用户的健康数据"""
        all_records = []
        
        for user in users:
            user_records = self.generate_user_data(user, days)
            all_records.extend(user_records)
            print(f"  生成 {user.user_id} ({user.name}) 的数据: {len(user_records)} 条")
        
        return all_records


# =============================================================================
# 导出函数
# =============================================================================

def generate_health_data(users: List[User], days: int = 30, seed: int = 42) -> List[HealthRecord]:
    """生成健康数据"""
    generator = HealthDataGenerator(seed=seed)
    return generator.generate_all_data(users, days)


def records_to_json(records: List[HealthRecord]) -> str:
    """转换为JSON"""
    return json.dumps(
        [r.to_dict() for r in records],
        ensure_ascii=False,
        indent=2
    )


def save_records(records: List[HealthRecord], filepath: str):
    """保存到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            [r.to_dict() for r in records],
            f,
            ensure_ascii=False,
            indent=2
        )


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("健康数据生成器")
    print("=" * 60)
    
    # 生成用户
    users = generate_users(seed=42)
    print(f"\n已加载 {len(users)} 个用户")
    
    # 生成健康数据
    print(f"\n开始生成30天健康数据...\n")
    records = generate_health_data(users, days=30, seed=42)
    
    # 统计
    print("\n" + "-" * 60)
    print("数据统计:")
    print("-" * 60)
    
    type_counts = {}
    outlier_count = 0
    for r in records:
        type_counts[r.data_type] = type_counts.get(r.data_type, 0) + 1
        if r.is_outlier:
            outlier_count += 1
    
    for dtype, count in sorted(type_counts.items()):
        print(f"  {dtype}: {count} 条")
    
    print(f"\n  总计: {len(records)} 条")
    print(f"  异常值: {outlier_count} 条 ({outlier_count/len(records)*100:.1f}%)")
    
    # 保存
    save_records(records, "health_records.json")
    print(f"\n✓ 数据已保存到 health_records.json")
