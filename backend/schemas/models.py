"""Pydantic模型定义"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, time
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict, UUID4
import uuid
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    ELDERLY = "elderly"
    CHILDREN = "children"
    COMMUNITY = "community"


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None


class ElderlyResponse(BaseModel):
    """老人响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="老人ID")
    name: str = Field(..., description="姓名")
    gender: str = Field(..., description="性别")
    age: int = Field(..., description="年龄")
    address: str = Field(..., description="居住地址")
    health_status: str = Field(..., description="健康状态")
    last_update: datetime = Field(..., description="最后更新时间")


class ChildrenResponse(BaseModel):
    """子女响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="子女ID")
    name: str = Field(..., description="姓名")
    phone_number: str = Field(..., description="手机号码")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="居住地址")
    created_at: datetime = Field(..., description="创建时间")

# 基础模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error_code: int = Field(..., description="错误代码")
    error_msg: str = Field(..., description="错误信息")
    detail: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")


# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="手机号码")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v.isdigit():
            raise ValueError('手机号码必须全部为数字')
        if not v.startswith('1'):
            raise ValueError('手机号码必须以1开头')
        return v


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: str = Field(..., description="用户角色")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        allowed_roles = ['elderly', 'children', 'community']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {allowed_roles}')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="手机号码")
    password: str = Field(..., description="密码")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v.isdigit():
            raise ValueError('手机号码必须全部为数字')
        if not v.startswith('1'):
            raise ValueError('手机号码必须以1开头')
        return v


class UserLoginData(BaseModel):
    """登录响应数据"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")


class UserLoginResponse(BaseModel):
    """用户登录响应模型 - 符合前端期望格式"""
    status: str = Field(..., description="状态")
    data: UserLoginData = Field(..., description="登录数据")
    message: str = Field(..., description="消息")


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user_info: Dict[str, Any] = Field(..., description="用户信息")


class UserUpdate(BaseModel):
    """用户更新模型"""
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11, description="手机号码")
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None:
            if not v.isdigit():
                raise ValueError('手机号码必须全部为数字')
            if not v.startswith('1'):
                raise ValueError('手机号码必须以1开头')
        return v


class UserResponse(BaseModel):
    """用户响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="用户ID")
    phone_number: str = Field(..., description="手机号码")
    role: str = Field(..., description="用户角色")
    status: str = Field(..., description="用户状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 老人档案相关模型
class ElderlyProfileBase(BaseModel):
    """老人档案基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: str = Field(..., description="性别")
    birth_date: datetime = Field(..., description="出生日期")
    id_card: str = Field(..., min_length=18, max_length=18, description="身份证号")
    address: str = Field(..., max_length=200, description="居住地址")
    emergency_contact: str = Field(..., min_length=11, max_length=11, description="紧急联系人电话")
    blood_type: Optional[str] = Field(None, description="血型")
    medical_history: Optional[str] = Field(None, max_length=500, description="病史")
    allergy_history: Optional[str] = Field(None, max_length=500, description="过敏史")
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ['男', '女']:
            raise ValueError('性别必须是男或女')
        return v
    
    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v):
        if not v.isalnum():
            raise ValueError('身份证号必须是字母和数字的组合')
        return v
    
    @field_validator('emergency_contact')
    @classmethod
    def validate_emergency_contact(cls, v):
        if not v.isdigit():
            raise ValueError('紧急联系人电话必须全部为数字')
        return v


class ElderlyProfileCreate(ElderlyProfileBase):
    """老人档案创建模型"""
    user_id: Optional[UUID4] = Field(None, description="关联用户ID")


class ElderlyProfileUpdate(BaseModel):
    """老人档案更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = Field(None)
    birth_date: Optional[datetime] = Field(None)
    id_card: Optional[str] = Field(None, min_length=18, max_length=18)
    address: Optional[str] = Field(None, max_length=200)
    emergency_contact: Optional[str] = Field(None, min_length=11, max_length=11)
    blood_type: Optional[str] = Field(None)
    medical_history: Optional[str] = Field(None, max_length=500)
    allergy_history: Optional[str] = Field(None, max_length=500)
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ['男', '女']:
            raise ValueError('性别必须是男或女')
        return v


class ElderlyProfileResponse(ElderlyProfileBase):
    """老人档案响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="档案ID")
    user_id: UUID4 = Field(..., description="关联用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ElderlyListResponse(BaseModel):
    """老人列表响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="档案ID")
    name: str = Field(..., description="姓名")
    age: int = Field(..., description="年龄")
    gender: str = Field(..., description="性别")
    address: str = Field(..., description="居住地址")
    last_update: datetime = Field(..., description="最后更新时间")
    health_status: str = Field(..., description="健康状态")
    status_message: Optional[str] = Field(None, description="状态说明")


# ============================================================================
# 健康数据相关模型
# ============================================================================

class TodayHealthData(BaseModel):
    """今日健康数据模型"""
    systolic: int = Field(..., description="收缩压 (mmHg)", ge=60, le=250)
    diastolic: int = Field(..., description="舒张压 (mmHg)", ge=40, le=150)
    heart_rate: int = Field(..., description="心率 (bpm)", ge=30, le=200)
    blood_oxygen: Optional[int] = Field(None, description="血氧饱和度 (%)", ge=70, le=100)
    blood_sugar: Optional[float] = Field(None, description="血糖 (mmol/L)", ge=2.0, le=30.0)
    temperature: Optional[float] = Field(None, description="体温 (℃)", ge=35.0, le=42.0)
    steps: Optional[int] = Field(None, description="今日步数", ge=0)
    sleep_hours: Optional[float] = Field(None, description="睡眠时长 (小时)", ge=0, le=24)
    last_updated: str = Field(..., description="最后更新时间")
    health_status: str = Field(default="normal", description="健康状态: normal/warning/danger")
    health_tips: Optional[str] = Field(None, description="健康建议")


class TodayHealthResponse(BaseModel):
    """今日健康数据响应"""
    status: str = Field(default="success", description="响应状态")
    data: TodayHealthData = Field(..., description="健康数据")
    message: str = Field(default="获取成功", description="响应消息")


# ============================================================================
# AI 健康助手相关模型
# ============================================================================

class AIContextData(BaseModel):
    """AI 对话上下文数据"""
    dataType: Optional[str] = Field(None, description="数据类型：血压、心率、血糖等")
    currentValue: Optional[str] = Field(None, description="当前值")
    healthStatus: Optional[str] = Field(None, description="健康状态")
    additionalInfo: Optional[Dict[str, Any]] = Field(None, description="额外信息")


class AIMessageRequest(BaseModel):
    """AI 对话请求模型"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    context: Optional[AIContextData] = Field(None, description="对话上下文")


class AIMessageData(BaseModel):
    """AI 对话响应数据"""
    responseText: str = Field(..., description="AI 回复文本")
    suggestions: List[str] = Field(default=[], description="建议列表")
    needsAttention: bool = Field(default=False, description="是否需要注意/预警")
    confidence: Optional[float] = Field(None, description="置信度 0-1")


class AIMessageResponse(BaseModel):
    """AI 对话响应模型"""
    success: bool = Field(default=True, description="是否成功")
    data: AIMessageData = Field(..., description="响应数据")


class AIAnalyzeRequest(BaseModel):
    """AI 数据分析请求模型"""
    dataType: str = Field(..., description="数据类型：血压、心率、血糖、睡眠")
    timeRange: Optional[str] = Field("week", description="时间范围：day、week、month")


class AIAnalyzeData(BaseModel):
    """AI 分析响应数据"""
    analysis: str = Field(..., description="分析结果文本")
    trend: str = Field(..., description="趋势：上升、稳定、下降")
    riskLevel: str = Field(default="low", description="风险等级：low、medium、high")
    recommendations: List[str] = Field(default=[], description="建议列表")


class AIAnalyzeResponse(BaseModel):
    """AI 分析响应模型"""
    success: bool = Field(default=True, description="是否成功")
    data: AIAnalyzeData = Field(..., description="响应数据")


# ============================================================================
# 健康图表相关模型
# ============================================================================

class ChartDataPoint(BaseModel):
    """图表数据点"""
    time: str = Field(..., description="时间点")
    value: Optional[float] = Field(None, description="数值")
    timestamp: Optional[str] = Field(None, description="时间戳")


class HeartRateChartData(BaseModel):
    """心率图表数据"""
    period: str = Field(..., description="时间段: today, week, month")
    dataPoints: List[ChartDataPoint] = Field(default=[], description="数据点列表")
    statistics: Dict[str, Any] = Field(default={}, description="统计信息")


class HeartRateChartResponse(BaseModel):
    """心率图表响应"""
    success: bool = Field(default=True)
    data: HeartRateChartData


class SleepDataPoint(BaseModel):
    """睡眠数据点"""
    day: str = Field(..., description="日期")
    deepSleep: float = Field(..., description="深睡时长(小时)")
    lightSleep: float = Field(..., description="浅睡时长(小时)")
    total: float = Field(..., description="总睡眠时长(小时)")


class SleepChartData(BaseModel):
    """睡眠图表数据"""
    period: str = Field(..., description="时间段")
    dataPoints: List[SleepDataPoint] = Field(default=[], description="数据点")
    statistics: Dict[str, Any] = Field(default={}, description="统计信息")


class SleepChartResponse(BaseModel):
    """睡眠图表响应"""
    success: bool = Field(default=True)
    data: SleepChartData


class BloodPressureDataPoint(BaseModel):
    """血压数据点"""
    time: str = Field(..., description="时间")
    systolic: int = Field(..., description="收缩压")
    diastolic: int = Field(..., description="舒张压")
    timestamp: Optional[str] = Field(None, description="时间戳")


class BloodPressureChartData(BaseModel):
    """血压图表数据"""
    period: str = Field(..., description="时间段")
    dataPoints: List[BloodPressureDataPoint] = Field(default=[], description="数据点")
    statistics: Dict[str, Any] = Field(default={}, description="统计信息")


class BloodPressureChartResponse(BaseModel):
    """血压图表响应"""
    success: bool = Field(default=True)
    data: BloodPressureChartData


class RadarCategory(BaseModel):
    """雷达图分类"""
    category: str = Field(..., description="分类名称")
    score: float = Field(..., description="得分")
    maxScore: float = Field(default=100, description="最大分")


class RadarChartData(BaseModel):
    """雷达图数据"""
    categories: List[RadarCategory] = Field(default=[], description="各分类数据")
    overallScore: float = Field(..., description="综合得分")


class RadarChartResponse(BaseModel):
    """雷达图响应"""
    success: bool = Field(default=True)
    data: RadarChartData


# ============================================================================
# 健康报告相关模型
# ============================================================================

class ReportMetric(BaseModel):
    """报告指标"""
    name: str = Field(..., description="指标名称")
    value: str = Field(..., description="当前值")
    status: str = Field(..., description="状态: normal, warning, danger")
    trend: Optional[str] = Field(None, description="趋势: up, down, stable")


class HealthReport(BaseModel):
    """健康报告"""
    reportId: str = Field(..., description="报告ID")
    generatedAt: str = Field(..., description="生成时间")
    reportType: str = Field(default="daily", description="报告类型")
    metrics: List[ReportMetric] = Field(default=[], description="健康指标")
    summary: str = Field(..., description="总结")
    recommendations: List[str] = Field(default=[], description="建议")
    overallStatus: str = Field(default="good", description="总体状态")


class CurrentReportResponse(BaseModel):
    """当前报告响应"""
    success: bool = Field(default=True)
    data: HealthReport


# ============================================================================
# 心理健康/心情相关模型
# ============================================================================

class MoodRecord(BaseModel):
    """心情记录请求"""
    mood: str = Field(..., description="心情: happy, calm, tired, anxious, sad")
    note: Optional[str] = Field(None, max_length=500, description="备注")
    timestamp: Optional[str] = Field(None, description="时间戳")


class MoodRecordData(BaseModel):
    """心情记录响应数据"""
    recordId: str = Field(..., description="记录ID")
    mood: str = Field(..., description="心情")
    score: int = Field(..., description="心情分数 1-5")
    note: Optional[str] = Field(None, description="备注")
    recordedAt: str = Field(..., description="记录时间")


class MoodRecordResponse(BaseModel):
    """心情记录响应"""
    success: bool = Field(default=True)
    data: MoodRecordData
    message: str = Field(default="记录成功")


# ============================================================================
# 子女端相关模型
# ============================================================================

class ElderVitalSigns(BaseModel):
    """老人生命体征"""
    heartRate: int = Field(..., description="心率")
    bloodPressure: str = Field(..., description="血压")
    temperature: float = Field(..., description="体温")


class ElderInfo(BaseModel):
    """老人信息"""
    elderId: str = Field(..., description="老人ID")
    name: str = Field(..., description="姓名")
    avatar: Optional[str] = Field(None, description="头像")
    age: int = Field(..., description="年龄")
    gender: str = Field(..., description="性别")
    relationship: str = Field(..., description="与子女的关系")
    healthStatus: str = Field(default="good", description="健康状态: good, warning, danger")
    lastUpdate: str = Field(..., description="最后更新时间")
    location: Optional[str] = Field(None, description="当前位置")
    recentAlerts: int = Field(default=0, description="近期告警数")
    vitalSigns: ElderVitalSigns = Field(..., description="生命体征")


class ElderListResponse(BaseModel):
    """老人列表响应"""
    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(..., description="老人列表数据")


class ElderDetailData(BaseModel):
    """老人详情数据"""
    elderId: str = Field(..., description="老人ID")
    personalInfo: Dict[str, Any] = Field(..., description="个人信息")
    healthData: Dict[str, Any] = Field(..., description="健康数据")
    alerts: List[Dict[str, Any]] = Field(default=[], description="告警列表")
    medications: List[Dict[str, Any]] = Field(default=[], description="用药信息")


class ElderDetailResponse(BaseModel):
    """老人详情响应"""
    success: bool = Field(default=True)
    data: ElderDetailData


class RealtimeMonitorData(BaseModel):
    """实时监控数据"""
    elderId: str = Field(..., description="老人ID")
    timestamp: str = Field(..., description="时间戳")
    heartRate: int = Field(..., description="心率")
    bloodPressure: Dict[str, int] = Field(..., description="血压")
    bloodOxygen: int = Field(..., description="血氧")
    temperature: float = Field(..., description="体温")
    location: Optional[Dict[str, Any]] = Field(None, description="位置信息")
    activityStatus: str = Field(default="正常", description="活动状态")
    deviceStatus: str = Field(default="在线", description="设备状态")


class RealtimeMonitorResponse(BaseModel):
    """实时监控响应"""
    success: bool = Field(default=True)
    data: RealtimeMonitorData


class ReminderCreate(BaseModel):
    """创建提醒请求"""
    elder_id: str = Field(..., alias="elderId", description="老人ID")
    type: str = Field(..., description="类型: medication, appointment, exercise, other")
    title: str = Field(..., max_length=100, description="标题")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    scheduled_time: str = Field(..., alias="scheduledTime", description="计划时间")
    repeat: Optional[str] = Field(None, description="重复: daily, weekly, monthly, none")
    priority: str = Field(default="normal", description="优先级: low, normal, high")
    
    class Config:
        populate_by_name = True


class ReminderData(BaseModel):
    """提醒数据"""
    reminderId: str = Field(..., description="提醒ID")
    elderId: str = Field(..., description="老人ID")
    elderName: str = Field(..., description="老人姓名")
    type: str = Field(..., description="类型")
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    scheduledTime: str = Field(..., description="计划时间")
    status: str = Field(default="pending", description="状态: pending, completed, cancelled")
    priority: str = Field(default="normal", description="优先级")
    createdAt: str = Field(..., description="创建时间")


class ReminderCreateResponse(BaseModel):
    """创建提醒响应"""
    success: bool = Field(default=True)
    data: ReminderData
    message: str = Field(default="提醒创建成功")


# ElderlyCreate模型，用于创建老人档案
class ElderlyCreate(BaseModel):
    """创建老人档案请求模型"""
    phone_number: str
    password: str
    name: str
    gender: str
    birth_date: date
    id_card: Optional[str] = None
    address: Optional[str] = None
    community_id: Optional[int] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    health_status: Optional[str] = None

# ElderlyUpdate模型，用于更新老人档案
class ElderlyUpdate(BaseModel):
    """更新老人档案请求模型"""
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    community_id: Optional[int] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    health_status: Optional[str] = None
    profile_image: Optional[str] = None

# 用于返回老人列表的新模型
class ElderlyListResponse(BaseModel):
    """老人列表响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="档案ID")
    phone_number: str = Field(..., description="手机号码")
    name: str = Field(..., description="姓名")
    gender: str = Field(..., description="性别")
    age: int = Field(..., description="年龄")
    address: Optional[str] = Field(None, description="居住地址")
    community_id: Optional[UUID4] = Field(None, description="社区ID")
    community_name: Optional[str] = Field(None, description="社区名称")
    health_status: Optional[str] = Field(None, description="健康状态")
    created_at: datetime = Field(..., description="创建时间")


# 子女档案相关模型
class ChildrenProfileBase(BaseModel):
    """子女档案基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: str = Field(..., description="性别")
    id_card: str = Field(..., min_length=18, max_length=18, description="身份证号")
    phone_number: str = Field(..., min_length=11, max_length=11, description="手机号码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, max_length=200, description="居住地址")
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ['男', '女']:
            raise ValueError('性别必须是男或女')
        return v
    
    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v):
        if not v.isalnum():
            raise ValueError('身份证号必须是字母和数字的组合')
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if not v.isdigit():
            raise ValueError('手机号码必须全部为数字')
        if not v.startswith('1'):
            raise ValueError('手机号码必须以1开头')
        return v


class ChildrenProfileCreate(ChildrenProfileBase):
    """子女档案创建模型"""
    user_id: Optional[UUID4] = Field(None, description="关联用户ID")


class ChildrenProfileUpdate(BaseModel):
    """子女档案更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = Field(None)
    id_card: Optional[str] = Field(None, min_length=18, max_length=18)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = Field(None)
    address: Optional[str] = Field(None, max_length=200)


class ChildrenProfileResponse(ChildrenProfileBase):
    """子女档案响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="档案ID")
    user_id: UUID4 = Field(..., description="关联用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 健康记录相关模型
class HealthRecordBase(BaseModel):
    """健康记录基础模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    data_type: str = Field(..., description="数据类型")
    value: float = Field(..., description="数据值")
    unit: str = Field(..., description="单位")
    record_time: datetime = Field(..., description="记录时间")
    is_normal: Optional[bool] = Field(None, description="是否正常")
    
    @field_validator('data_type')
    @classmethod
    def validate_data_type(cls, v):
        allowed_types = ['heart_rate', 'blood_pressure', 'blood_sugar', 'temperature', 'step_count', 'sleep_time']
        if v not in allowed_types:
            raise ValueError(f'数据类型必须是以下之一: {allowed_types}')
        return v


class HealthRecordCreate(HealthRecordBase):
    """健康记录创建模型"""
    pass


class HealthRecordResponse(HealthRecordBase):
    """健康记录响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="记录ID")
    created_at: datetime = Field(..., description="创建时间")

# 用于返回健康记录的新模型
class HealthRecordResponse(BaseModel):
    """健康记录响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="记录ID")
    elderly_id: UUID4 = Field(..., description="老人ID")
    record_type: str = Field(..., description="记录类型")
    record_value: str = Field(..., description="记录值")
    measurement_time: datetime = Field(..., description="测量时间")
    created_at: datetime = Field(..., description="创建时间")
    notes: Optional[str] = Field(None, description="备注")


class HealthDataResponse(BaseModel):
    """健康数据响应模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    heart_rate: Optional[float] = Field(None, description="心率")
    systolic_pressure: Optional[float] = Field(None, description="收缩压")
    diastolic_pressure: Optional[float] = Field(None, description="舒张压")
    blood_sugar: Optional[float] = Field(None, description="血糖")
    temperature: Optional[float] = Field(None, description="体温")
    step_count: Optional[int] = Field(None, description="步数")
    sleep_time: Optional[float] = Field(None, description="睡眠时间")
    last_update: datetime = Field(..., description="最后更新时间")
    health_status: str = Field(..., description="健康状态")

# ElderlyWithHealthResponse模型，用于返回带有健康信息的老人详情
class ElderlyWithHealthResponse(BaseModel):
    """带健康信息的老人响应模型"""
    elderly: ElderlyResponse
    latest_health_records: List[HealthRecordResponse] = []
    health_statistics: Optional[Dict[str, Any]] = None

# HealthRecordCreate模型，用于创建健康记录
class HealthRecordCreate(BaseModel):
    """创建健康记录请求模型"""
    record_type: str
    record_value: str
    measurement_time: datetime
    notes: Optional[str] = None

# HealthRecordUpdate模型，用于更新健康记录
class HealthRecordUpdate(BaseModel):
    """更新健康记录请求模型"""
    record_value: Optional[str] = None
    measurement_time: Optional[datetime] = None
    notes: Optional[str] = None

# HealthAlertResponse模型，用于返回健康告警信息
class HealthAlertResponse(BaseModel):
    """健康告警响应模型"""
    id: int
    elderly_id: int
    alert_type: str
    alert_level: str
    alert_message: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# DailyHealthSummary模型，用于返回每日健康摘要
class DailyHealthSummary(BaseModel):
    """每日健康摘要模型"""
    date: date
    total_records: int
    avg_heart_rate: Optional[float] = None
    avg_blood_pressure: Optional[Dict[str, float]] = None
    avg_blood_sugar: Optional[float] = None
    health_status: str

# WeeklyHealthTrend模型，用于返回周健康趋势
class WeeklyHealthTrend(BaseModel):
    """周健康趋势模型"""
    week_start: date
    week_end: date
    health_metrics: Dict[str, List[Dict[str, Any]]]
    improvement_rate: Optional[float] = None

# ReminderCreate模型，用于创建提醒
class ReminderCreate(BaseModel):
    """创建提醒请求模型"""
    title: str
    description: Optional[str] = None
    reminder_time: time
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True

# ReminderUpdate模型，用于更新提醒
class ReminderUpdate(BaseModel):
    """更新提醒请求模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[time] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

# ReminderStatusUpdate模型，用于更新提醒状态
class ReminderStatusUpdate(BaseModel):
    """更新提醒状态请求模型"""
    is_active: bool

# ReminderResponse模型，用于返回提醒信息
class ReminderResponse(BaseModel):
    """提醒响应模型"""
    id: int
    elderly_id: int
    title: str
    description: Optional[str] = None
    reminder_time: time
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# CommunityCreate模型，用于创建社区
class CommunityCreate(BaseModel):
    """创建社区请求模型"""
    name: str
    address: str
    contact_person: str
    contact_phone: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# CommunityUpdate模型，用于更新社区信息
class CommunityUpdate(BaseModel):
    """更新社区请求模型"""
    name: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None

# CommunityResponse模型，用于返回社区信息
class CommunityResponse(BaseModel):
    """社区响应模型"""
    id: int
    name: str
    address: str
    contact_person: str
    contact_phone: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elderly_count: int = 0
    admin_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# CommunityMemberResponse模型，用于返回社区成员信息
class CommunityMemberResponse(BaseModel):
    """社区成员响应模型"""
    id: int
    community_id: int
    user_id: int
    role: str
    join_date: date
    is_active: bool
    user_name: str
    user_phone: str
    
    class Config:
        from_attributes = True

# CommunityAdminResponse模型，用于返回社区管理员信息
class CommunityAdminResponse(BaseModel):
    """社区管理员响应模型"""
    id: int
    community_id: int
    user_id: int
    role: str
    appointment_date: date
    is_active: bool
    user_name: str
    user_phone: str
    
    class Config:
        from_attributes = True


# 老人统计信息响应模型
class ElderlyWithStatsResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    phone: str
    health_status: Optional[str] = None
    community_id: Optional[int] = None
    community_name: Optional[str] = None
    activity_count: int = 0  # 活动数量
    reminder_count: int = 0  # 提醒数量
    health_check_count: int = 0  # 健康检查次数
    last_activity_time: Optional[datetime] = None  # 最后活动时间
    
    class Config:
        from_attributes = True


# 告警相关模型
class AlertBase(BaseModel):
    """告警基础模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    description: str = Field(..., description="告警描述")
    alert_time: datetime = Field(..., description="告警时间")
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        allowed_severities = ['低', '中', '高']
        if v not in allowed_severities:
            raise ValueError(f'严重程度必须是以下之一: {allowed_severities}')
        return v


class AlertCreate(AlertBase):
    """告警创建模型"""
    pass


class AlertUpdate(BaseModel):
    """告警更新模型"""
    status: str = Field(..., description="告警状态")
    processing_notes: Optional[str] = Field(None, max_length=500, description="处理记录")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['未处理', '处理中', '已解决', '已忽略']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {allowed_statuses}')
        return v


class AlertResponse(AlertBase):
    """告警响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="告警ID")
    status: str = Field(..., description="告警状态")
    processing_notes: Optional[str] = Field(None, description="处理记录")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 提醒相关模型
class ReminderBase(BaseModel):
    """提醒基础模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    reminder_type: str = Field(..., description="提醒类型")
    title: str = Field(..., max_length=100, description="提醒标题")
    content: str = Field(..., max_length=500, description="提醒内容")
    reminder_time: datetime = Field(..., description="提醒时间")
    is_recurring: bool = Field(default=False, description="是否重复")
    recurrence_rule: Optional[str] = Field(None, description="重复规则")
    
    @field_validator('reminder_type')
    @classmethod
    def validate_reminder_type(cls, v):
        allowed_types = ['服药', '运动', '饮食', '其他']
        if v not in allowed_types:
            raise ValueError(f'提醒类型必须是以下之一: {allowed_types}')
        return v


class ReminderCreate(ReminderBase):
    """提醒创建模型"""
    pass


class ReminderUpdate(BaseModel):
    """提醒更新模型"""
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, max_length=500)
    reminder_time: Optional[datetime] = Field(None)
    is_recurring: Optional[bool] = Field(None)
    recurrence_rule: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['未执行', '已执行', '已取消']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {allowed_statuses}')
        return v


class ReminderResponse(ReminderBase):
    """提醒响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="提醒ID")
    status: str = Field(..., description="提醒状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 关系相关模型
class ChildrenElderlyRelationCreate(BaseModel):
    """子女老人关系创建模型"""
    children_id: UUID4 = Field(..., description="子女ID")
    elderly_id: UUID4 = Field(..., description="老人ID")
    relationship_type: str = Field(..., description="关系类型")
    
    @field_validator('relationship_type')
    @classmethod
    def validate_relationship_type(cls, v):
        allowed_types = ['子女', '孙子孙女', '其他']
        if v not in allowed_types:
            raise ValueError(f'关系类型必须是以下之一: {allowed_types}')
        return v


class ChildrenElderlyRelationResponse(BaseModel):
    """子女老人关系响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="关系ID")
    children_id: UUID4 = Field(..., description="子女ID")
    elderly_id: UUID4 = Field(..., description="老人ID")
    relationship_type: str = Field(..., description="关系类型")
    created_at: datetime = Field(..., description="创建时间")


# 社区用户相关模型
class CommunityUserProfileBase(BaseModel):
    """社区用户档案基础模型"""
    community_name: str = Field(..., max_length=100, description="社区名称")
    community_code: str = Field(..., max_length=20, description="社区代码")
    contact_person: str = Field(..., max_length=50, description="联系人")
    contact_phone: str = Field(..., min_length=11, max_length=11, description="联系电话")
    address: str = Field(..., max_length=200, description="社区地址")
    service_scope: Optional[str] = Field(None, max_length=500, description="服务范围")
    
    @field_validator('contact_phone')
    @classmethod
    def validate_contact_phone(cls, v):
        if not v.isdigit():
            raise ValueError('联系电话必须全部为数字')
        if not v.startswith('1'):
            raise ValueError('联系电话必须以1开头')
        return v


class CommunityUserProfileCreate(CommunityUserProfileBase):
    """社区用户档案创建模型"""
    user_id: Optional[UUID4] = Field(None, description="关联用户ID")


class CommunityUserProfileUpdate(BaseModel):
    """社区用户档案更新模型"""
    community_name: Optional[str] = Field(None, max_length=100)
    community_code: Optional[str] = Field(None, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=50)
    contact_phone: Optional[str] = Field(None, min_length=11, max_length=11)
    address: Optional[str] = Field(None, max_length=200)
    service_scope: Optional[str] = Field(None, max_length=500)


class CommunityUserProfileResponse(CommunityUserProfileBase):
    """社区用户档案响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID4 = Field(..., description="档案ID")
    user_id: UUID4 = Field(..., description="关联用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 健康分析相关模型
class HealthAnalysisRequest(BaseModel):
    """健康分析请求模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    analysis_type: str = Field(..., description="分析类型")


class HealthAnalysisResponse(BaseModel):
    """健康分析响应模型"""
    elderly_id: UUID4 = Field(..., description="老人ID")
    elderly_name: str = Field(..., description="老人姓名")
    analysis_type: str = Field(..., description="分析类型")
    analysis_period: str = Field(..., description="分析周期")
    analysis_result: Dict[str, Any] = Field(..., description="分析结果")
    recommendations: List[str] = Field(..., description="健康建议")
    analysis_time: datetime = Field(..., description="分析时间")