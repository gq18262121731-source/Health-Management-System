"""数据库模型定义"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    UUID,
    func,
    Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
import enum
import uuid
from datetime import datetime

from database.database import Base


# 枚举类型定义
class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ELDERLY = "elderly"
    CHILDREN = "children"
    COMMUNITY = "community"


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class Gender(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RelationshipType(str, enum.Enum):
    """关系类型枚举"""
    FATHER = "父亲"
    MOTHER = "母亲"
    SON = "儿子"
    DAUGHTER = "女儿"
    HUSBAND = "丈夫"
    WIFE = "妻子"
    OTHER = "其他"


class AlertSeverity(str, enum.Enum):
    """预警严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AlertStatus(str, enum.Enum):
    """预警状态枚举"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertType(str, enum.Enum):
    """预警类型枚举"""
    HEART_RATE_HIGH = "heart_rate_high"
    HEART_RATE_LOW = "heart_rate_low"
    BLOOD_PRESSURE_HIGH = "blood_pressure_high"
    BLOOD_PRESSURE_LOW = "blood_pressure_low"
    BLOOD_SUGAR_HIGH = "blood_sugar_high"
    BLOOD_SUGAR_LOW = "blood_sugar_low"
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    BLOOD_OXYGEN_LOW = "blood_oxygen_low"
    FALL_DETECTED = "fall_detected"
    NO_ACTIVITY = "no_activity"
    MEDICATION_MISSED = "medication_missed"
    OTHER = "other"


class ReminderType(str, enum.Enum):
    """提醒类型枚举"""
    MEDICATION = "medication"
    EXERCISE = "exercise"
    MEAL = "meal"
    MEASUREMENT = "measurement"
    OTHER = "other"


class ReminderFrequency(str, enum.Enum):
    """提醒频率枚举"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReminderStatus(str, enum.Enum):
    """提醒状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    EXPIRED = "expired"


class HealthRecordStatus(str, enum.Enum):
    """健康记录状态枚举"""
    NORMAL = "normal"
    WARNING = "warning"
    DANGER = "danger"


class QueryType(str, enum.Enum):
    """AI查询类型枚举"""
    HEALTH_ADVICE = "health_advice"
    DISEASE_INFORMATION = "disease_information"
    MEDICATION_INFORMATION = "medication_information"
    LIFE_SUGGESTION = "life_suggestion"
    OTHER = "other"


class ReportType(str, enum.Enum):
    """报告类型枚举"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# 数据库模型定义
class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    elderly_profile = relationship("ElderlyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    children_profile = relationship("ChildrenProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    community_profile = relationship("CommunityProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ai_queries = relationship("AIQuery", back_populates="user", cascade="all, delete-orphan")


class ElderlyProfile(Base):
    """老人基本信息表"""
    __tablename__ = "elderly_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birth_date = Column(DateTime(timezone=True), nullable=False)
    age = Column(Integer, nullable=False)  # 根据birth_date计算并存储
    address = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    emergency_contact = Column(String(50), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    medical_history = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    blood_type = Column(String(5), nullable=True)
    height = Column(Float, nullable=True)  # 身高，单位：cm
    weight = Column(Float, nullable=True)  # 体重，单位：kg
    bmi = Column(Float, nullable=True)  # 体重指数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="elderly_profile")
    health_records = relationship("HealthRecord", back_populates="elderly", cascade="all, delete-orphan")
    sleep_data = relationship("SleepData", back_populates="elderly", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="elderly", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="elderly", cascade="all, delete-orphan")
    health_assessments = relationship("HealthAssessment", back_populates="elderly", cascade="all, delete-orphan")
    children_relations = relationship("ChildrenElderlyRelation", back_populates="elderly", cascade="all, delete-orphan")


class ChildrenProfile(Base):
    """子女信息表"""
    __tablename__ = "children_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="children_profile")
    elderly_relations = relationship("ChildrenElderlyRelation", back_populates="children", cascade="all, delete-orphan")


class CommunityProfile(Base):
    """社区信息表"""
    __tablename__ = "community_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    community_name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    contact_person = Column(String(50), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="community_profile")
    reports = relationship("CommunityReport", back_populates="community", cascade="all, delete-orphan")


class HealthRecord(Base):
    """健康记录表"""
    __tablename__ = "health_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    heart_rate = Column(Integer, nullable=True)  # 心率，单位：bpm
    systolic_pressure = Column(Integer, nullable=True)  # 收缩压
    diastolic_pressure = Column(Integer, nullable=True)  # 舒张压
    blood_sugar = Column(Float, nullable=True)  # 血糖，单位：mmol/L
    temperature = Column(Float, nullable=True)  # 体温，单位：℃
    blood_oxygen = Column(Float, nullable=True)  # 血氧饱和度，单位：%
    weight = Column(Float, nullable=True)  # 体重，单位：kg
    steps = Column(Integer, nullable=True)  # 步数
    notes = Column(Text, nullable=True)
    status = Column(Enum(HealthRecordStatus), default=HealthRecordStatus.NORMAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    elderly = relationship("ElderlyProfile", back_populates="health_records")


class SleepData(Base):
    """睡眠数据表"""
    __tablename__ = "sleep_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)  # 睡眠日期
    sleep_start_time = Column(DateTime(timezone=True), nullable=True)
    sleep_end_time = Column(DateTime(timezone=True), nullable=True)
    total_hours = Column(Float, nullable=False)  # 总睡眠时间，单位：小时
    deep_sleep_hours = Column(Float, nullable=False)  # 深度睡眠，单位：小时
    light_sleep_hours = Column(Float, nullable=False)  # 浅睡眠，单位：小时
    quality = Column(Integer, nullable=False)  # 睡眠质量评分，0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    elderly = relationship("ElderlyProfile", back_populates="sleep_data")


class Alert(Base):
    """预警信息表"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    alert_message = Column(String(255), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    health_record_id = Column(UUID(as_uuid=True), ForeignKey("health_records.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    elderly = relationship("ElderlyProfile", back_populates="alerts")
    health_record = relationship("HealthRecord")
    resolution = relationship("AlertResolution", back_populates="alert", uselist=False, cascade="all, delete-orphan")


class AlertResolution(Base):
    """预警解决方案表"""
    __tablename__ = "alert_resolutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), unique=True, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_time = Column(DateTime(timezone=True), server_default=func.now())
    resolution_method = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    
    # 关系
    alert = relationship("Alert", back_populates="resolution")
    resolver = relationship("User")


class Reminder(Base):
    """提醒表"""
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    reminder_type = Column(Enum(ReminderType), nullable=False)
    frequency = Column(Enum(ReminderFrequency), default=ReminderFrequency.ONCE)
    next_reminder_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(ReminderStatus), default=ReminderStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    elderly = relationship("ElderlyProfile", back_populates="reminders")
    creator = relationship("User")


class HealthAssessment(Base):
    """健康评估表"""
    __tablename__ = "health_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    cardiovascular = Column(Integer, nullable=False)  # 心血管健康，0-100
    sleep_quality = Column(Integer, nullable=False)  # 睡眠质量，0-100
    exercise = Column(Integer, nullable=False)  # 运动情况，0-100
    nutrition = Column(Integer, nullable=False)  # 营养状况，0-100
    mental_health = Column(Integer, nullable=False)  # 心理健康，0-100
    weight_management = Column(Integer, nullable=False)  # 体重管理，0-100
    overall = Column(Integer, nullable=False)  # 整体健康评分，0-100
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    elderly = relationship("ElderlyProfile", back_populates="health_assessments")


class ChildrenElderlyRelation(Base):
    """子女老人关系表"""
    __tablename__ = "children_elderly_relations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    children_id = Column(UUID(as_uuid=True), ForeignKey("children_profiles.id"), nullable=False)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    children = relationship("ChildrenProfile", back_populates="elderly_relations")
    elderly = relationship("ElderlyProfile", back_populates="children_relations")


class AIQuery(Base):
    """AI咨询记录表"""
    __tablename__ = "ai_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(Enum(QueryType), nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="ai_queries")
    elderly = relationship("ElderlyProfile")


class Community(Base):
    """社区表"""
    __tablename__ = "communities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_name = Column(String(100), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    contact_person = Column(String(50), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CommunityReport(Base):
    """社区报告表"""
    __tablename__ = "community_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), ForeignKey("community_profiles.id"), nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=False)
    report_data = Column(Text, nullable=False)  # JSON格式存储详细数据
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    community = relationship("CommunityProfile", back_populates="reports")