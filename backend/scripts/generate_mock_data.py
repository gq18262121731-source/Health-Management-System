"""
生成模拟健康数据并写入数据库
运行方式: python -m scripts.generate_mock_data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
import uuid
from sqlalchemy.orm import Session

from database.database import SessionLocal, engine, Base
from database.models import (
    User, UserRole, UserStatus, Gender,
    ElderlyProfile, HealthRecord, SleepData, HealthRecordStatus
)

# 创建表
Base.metadata.create_all(bind=engine)


def create_test_user(db: Session) -> tuple:
    """创建测试用户和老人档案"""
    
    # 检查是否已存在测试用户
    existing_user = db.query(User).filter(User.username == "elderly_001").first()
    if existing_user:
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == existing_user.id
        ).first()
        print(f"✓ 测试用户已存在: {existing_user.username}")
        return existing_user, elderly_profile
    
    # 创建新用户
    user = User(
        id=uuid.uuid4(),
        username="elderly_001",
        phone_number="13800138000",
        password="$2b$12$test_hashed_password",  # 占位符
        role=UserRole.ELDERLY,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.flush()
    
    # 创建老人档案
    elderly_profile = ElderlyProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        name="张三",
        gender=Gender.MALE,
        birth_date=datetime(1955, 5, 15),
        age=70,
        phone_number="13800138000",
        address="北京市朝阳区健康社区1号楼",
        emergency_contact="李四",
        emergency_phone="13900139000",
        height=170.0,
        weight=65.0,
    )
    db.add(elderly_profile)
    db.commit()
    
    print(f"✓ 创建测试用户: {user.username}")
    return user, elderly_profile


def generate_health_records(db: Session, elderly_id: uuid.UUID, days: int = 30):
    """生成健康记录数据"""
    
    # 删除旧数据
    db.query(HealthRecord).filter(HealthRecord.elderly_id == elderly_id).delete()
    
    now = datetime.now()
    records = []
    
    for day in range(days):
        date = now - timedelta(days=day)
        
        # 每天生成多条记录（模拟不同时间点的测量）
        for hour in [8, 12, 18, 22]:
            record_time = date.replace(hour=hour, minute=random.randint(0, 59))
            
            # 生成合理范围内的健康数据
            record = HealthRecord(
                id=uuid.uuid4(),
                elderly_id=elderly_id,
                heart_rate=random.randint(65, 85),
                systolic_pressure=random.randint(110, 130),
                diastolic_pressure=random.randint(70, 85),
                blood_sugar=round(random.uniform(4.5, 6.5), 1),
                temperature=round(random.uniform(36.2, 36.8), 1),
                blood_oxygen=round(random.uniform(96, 99), 1),
                weight=round(random.uniform(64, 66), 1),
                steps=random.randint(500, 3000) if hour >= 12 else random.randint(0, 500),
                status=HealthRecordStatus.NORMAL,
                recorded_at=record_time,
            )
            records.append(record)
    
    db.add_all(records)
    db.commit()
    
    print(f"✓ 生成 {len(records)} 条健康记录 (过去 {days} 天)")


def generate_sleep_data(db: Session, elderly_id: uuid.UUID, days: int = 30):
    """生成睡眠数据"""
    
    # 删除旧数据
    db.query(SleepData).filter(SleepData.elderly_id == elderly_id).delete()
    
    now = datetime.now()
    records = []
    
    for day in range(days):
        date = now - timedelta(days=day)
        
        # 睡眠时间 22:00-23:30 开始
        sleep_start = date.replace(hour=random.randint(22, 23), minute=random.randint(0, 59))
        
        # 睡眠时长 6-8 小时
        total_hours = round(random.uniform(6, 8), 1)
        sleep_end = sleep_start + timedelta(hours=total_hours)
        
        # 深睡眠占比 20-30%
        deep_sleep = round(total_hours * random.uniform(0.2, 0.3), 1)
        light_sleep = round(total_hours - deep_sleep, 1)
        
        # 睡眠质量评分
        quality = random.randint(60, 95)
        
        record = SleepData(
            id=uuid.uuid4(),
            elderly_id=elderly_id,
            date=date.date(),
            sleep_start_time=sleep_start,
            sleep_end_time=sleep_end,
            total_hours=total_hours,
            deep_sleep_hours=deep_sleep,
            light_sleep_hours=light_sleep,
            quality=quality,
        )
        records.append(record)
    
    db.add_all(records)
    db.commit()
    
    print(f"✓ 生成 {len(records)} 条睡眠记录 (过去 {days} 天)")


def main():
    """主函数"""
    print("\n" + "="*50)
    print("生成模拟健康数据")
    print("="*50 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. 创建测试用户
        user, elderly_profile = create_test_user(db)
        
        if not elderly_profile:
            print("❌ 无法创建老人档案")
            return
        
        # 2. 生成健康记录
        generate_health_records(db, elderly_profile.id, days=30)
        
        # 3. 生成睡眠数据
        generate_sleep_data(db, elderly_profile.id, days=30)
        
        print("\n" + "="*50)
        print("✅ 模拟数据生成完成!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
