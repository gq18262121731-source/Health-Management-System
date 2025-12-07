# 数据结构文档 (Data Structures)

## 📋 目录

- [核心数据类](#核心数据类)
- [枚举类型](#枚举类型)
- [数据库表结构](#数据库表结构)
- [JSON数据格式](#json数据格式)
- [配置文件结构](#配置文件结构)

---

## 核心数据类

### 1. 评估配置 (AssessmentConfig)

**模块**: `modules.assessment_config`

```python
@dataclass
class AssessmentConfig:
    assessment_id: str              # 评估唯一ID
    user_id: str                    # 用户ID
    assessment_type: AssessmentType # 评估类型
    period: AssessmentPeriod        # 评估周期
    time_window: TimeWindow         # 时间窗口
    start_date: datetime            # 开始日期
    end_date: datetime              # 结束日期
    required_metrics: List[str]     # 必需指标列表
    triggered_by: Optional[str]     # 触发者
    created_at: datetime            # 创建时间
```

**示例**:
```python
config = AssessmentConfig(
    assessment_id="ASM_20240115_001",
    user_id="USER001",
    assessment_type=AssessmentType.SCHEDULED,
    period=AssessmentPeriod.MONTHLY,
    time_window=TimeWindow.LAST_30_DAYS,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 15),
    required_metrics=["blood_pressure", "blood_glucose", "sleep", "steps"],
    triggered_by=None,
    created_at=datetime.now()
)
```

---

### 2. 健康指标数据 (HealthMetrics)

**模块**: `modules.data_preparation`

```python
@dataclass
class HealthMetrics:
    metric_name: str                # 指标名称
    timestamps: List[datetime]      # 时间戳列表
    values: List[float]             # 数值列表
    unit: str                       # 单位
    metadata: Optional[Dict] = None # 元数据
```

**示例**:
```python
bp_data = HealthMetrics(
    metric_name="blood_pressure",
    timestamps=[datetime(2024, 1, 1), datetime(2024, 1, 2)],
    values=[135, 132],
    unit="mmHg",
    metadata={"type": "systolic"}
)
```

---

### 3. 特征集合 (FeatureSet)

**模块**: `modules.data_preparation`

```python
@dataclass
class FeatureSet:
    # 血压特征
    sbp_mean: Optional[float] = None        # 收缩压均值
    sbp_std: Optional[float] = None         # 收缩压标准差
    sbp_max: Optional[float] = None         # 收缩压最大值
    sbp_min: Optional[float] = None         # 收缩压最小值
    sbp_trend: Optional[float] = None       # 收缩压趋势
    dbp_mean: Optional[float] = None        # 舒张压均值
    dbp_std: Optional[float] = None         # 舒张压标准差
    
    # 血糖特征
    glucose_mean: Optional[float] = None    # 血糖均值
    glucose_std: Optional[float] = None     # 血糖标准差
    glucose_cv: Optional[float] = None      # 血糖变异系数
    glucose_compliance_rate: Optional[float] = None  # 达标率
    
    # 血脂特征
    tc_mean: Optional[float] = None         # 总胆固醇
    ldl_mean: Optional[float] = None        # 低密度脂蛋白
    hdl_mean: Optional[float] = None        # 高密度脂蛋白
    tg_mean: Optional[float] = None         # 甘油三酯
    
    # 睡眠特征
    sleep_mean: Optional[float] = None      # 平均睡眠时长
    sleep_std: Optional[float] = None       # 睡眠时长标准差
    sleep_insufficient_days: Optional[int] = None  # 睡眠不足天数
    
    # 运动特征
    steps_mean: Optional[float] = None      # 平均步数
    steps_std: Optional[float] = None       # 步数标准差
    active_days: Optional[int] = None       # 活跃天数
    sedentary_days: Optional[int] = None    # 久坐天数
    
    # 基线偏离
    sbp_baseline_deviation: Optional[float] = None
    glucose_baseline_deviation: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {k: v for k, v in self.__dict__.items() if v is not None}
```

---

### 4. 单病种评估结果 (DiseaseRiskResult)

**模块**: `modules.disease_assessment`

```python
@dataclass
class DiseaseRiskResult:
    disease_name: str               # 疾病名称
    control_status: ControlStatus   # 控制状态
    risk_level: RiskLevel           # 风险等级
    risk_score: float               # 风险评分 (0-100)
    control_quality_score: float    # 控制质量评分 (0-100)
    key_findings: List[str]         # 关键发现
    recommendations: List[str]      # 建议
    details: Optional[Dict] = None  # 详细数据
    
    def to_dict(self) -> Dict:
        return {
            "disease_name": self.disease_name,
            "control_status": self.control_status.value,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "control_quality_score": self.control_quality_score,
            "key_findings": self.key_findings,
            "recommendations": self.recommendations,
            "details": self.details
        }
```

**示例**:
```python
result = DiseaseRiskResult(
    disease_name="高血压",
    control_status=ControlStatus.FAIR,
    risk_level=RiskLevel.MEDIUM,
    risk_score=45.0,
    control_quality_score=65.0,
    key_findings=["血压控制一般", "波动较大"],
    recommendations=["加强监测", "规律服药"],
    details={"bp_grade": 2, "compliance_rate": 0.7}
)
```

---

### 5. 生活方式评估结果 (LifestyleRiskResult)

**模块**: `modules.lifestyle_assessment`

```python
@dataclass
class LifestyleRiskResult:
    overall_score: float            # 综合评分 (0-100)
    overall_risk_level: RiskLevel   # 综合风险等级
    
    # 各维度评分
    sleep_score: float              # 睡眠评分
    sleep_risk_level: RiskLevel     # 睡眠风险等级
    sleep_findings: List[str]       # 睡眠发现
    
    exercise_score: float           # 运动评分
    exercise_risk_level: RiskLevel  # 运动风险等级
    exercise_findings: List[str]    # 运动发现
    
    diet_score: float               # 饮食评分
    diet_risk_level: RiskLevel      # 饮食风险等级
    diet_findings: List[str]        # 饮食发现
    
    # 异常检测
    anomaly_detected: bool          # 是否检测到异常
    anomaly_details: List[str]      # 异常详情
    
    recommendations: List[str]      # 综合建议
    
    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "overall_risk_level": self.overall_risk_level.value,
            "sleep": {
                "score": self.sleep_score,
                "risk_level": self.sleep_risk_level.value,
                "findings": self.sleep_findings
            },
            "exercise": {
                "score": self.exercise_score,
                "risk_level": self.exercise_risk_level.value,
                "findings": self.exercise_findings
            },
            "diet": {
                "score": self.diet_score,
                "risk_level": self.diet_risk_level.value,
                "findings": self.diet_findings
            },
            "anomaly": {
                "detected": self.anomaly_detected,
                "details": self.anomaly_details
            },
            "recommendations": self.recommendations
        }
```

---

### 6. 综合评估结果 (ComprehensiveAssessmentResult)

**模块**: `modules.comprehensive_assessment`

```python
@dataclass
class ComprehensiveAssessmentResult:
    assessment_id: str              # 评估ID
    user_id: str                    # 用户ID
    assessment_date: datetime       # 评估日期
    
    # 综合评分
    overall_score: float            # 综合评分 (0-100)
    health_level: HealthLevel       # 健康等级
    
    # 各维度评分
    disease_risk_score: float       # 疾病维度评分
    lifestyle_risk_score: float     # 生活方式维度评分
    trend_risk_score: float         # 趋势维度评分
    
    # 维度详细评分
    dimension_scores: Dict[str, float]  # 各维度详细评分
    
    # 风险因素
    top_risk_factors: List[RiskFactor]  # TOP风险因素
    all_risk_factors: List[RiskFactor]  # 所有风险因素
    
    # 建议
    priority_recommendations: List[str]  # 优先建议
    
    # 可解释性
    feature_importance: Dict[str, float]  # 特征重要性
    risk_distribution: Dict[str, int]     # 风险分布
    
    # 元数据
    data_quality: str               # 数据质量
    algorithm_version: str          # 算法版本
    
    def to_dict(self) -> Dict:
        return {
            "assessment_id": self.assessment_id,
            "user_id": self.user_id,
            "assessment_date": self.assessment_date.isoformat(),
            "overall_score": self.overall_score,
            "health_level": self.health_level.value,
            "disease_risk_score": self.disease_risk_score,
            "lifestyle_risk_score": self.lifestyle_risk_score,
            "trend_risk_score": self.trend_risk_score,
            "dimension_scores": self.dimension_scores,
            "top_risk_factors": [rf.to_dict() for rf in self.top_risk_factors],
            "priority_recommendations": self.priority_recommendations,
            "feature_importance": self.feature_importance,
            "risk_distribution": self.risk_distribution,
            "data_quality": self.data_quality,
            "algorithm_version": self.algorithm_version
        }
```

---

### 7. 风险因素 (RiskFactor)

**模块**: `modules.comprehensive_assessment`

```python
@dataclass
class RiskFactor:
    name: str                       # 风险因素名称
    category: str                   # 类别 (disease/lifestyle/trend)
    score: float                    # 风险评分
    priority: RiskPriority          # 优先级
    topsis_closeness: float         # TOPSIS接近度
    description: str                # 描述
    recommendation: str             # 建议
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "score": self.score,
            "priority": self.priority.value,
            "topsis_closeness": self.topsis_closeness,
            "description": self.description,
            "recommendation": self.recommendation
        }
```

---

### 8. 评估记录 (AssessmentRecord)

**模块**: `modules.report_generation`

```python
@dataclass
class AssessmentRecord:
    assessment_id: str              # 评估ID
    user_id: str                    # 用户ID
    assessment_date: datetime       # 评估日期
    assessment_type: str            # 评估类型
    time_window: Dict               # 时间窗口
    data_completeness: Dict         # 数据完整性
    overall_score: float            # 综合评分
    health_level: str               # 健康等级
    disease_risk_score: float       # 疾病评分
    lifestyle_risk_score: float     # 生活方式评分
    trend_risk_score: float         # 趋势评分
    top_risk_factors: List[Dict]    # TOP风险因素
    recommendations: List[str]      # 建议
    
    def to_dict(self) -> Dict:
        return {
            "assessment_id": self.assessment_id,
            "user_id": self.user_id,
            "assessment_date": self.assessment_date.isoformat(),
            "assessment_type": self.assessment_type,
            "time_window": self.time_window,
            "data_completeness": self.data_completeness,
            "overall_score": self.overall_score,
            "health_level": self.health_level,
            "disease_risk_score": self.disease_risk_score,
            "lifestyle_risk_score": self.lifestyle_risk_score,
            "trend_risk_score": self.trend_risk_score,
            "top_risk_factors": self.top_risk_factors,
            "recommendations": self.recommendations
        }
```

---

### 9. 智能体消息 (AgentMessage)

**模块**: `agents.base_agent`

```python
@dataclass
class AgentMessage:
    content: str                    # 消息内容
    sender: str                     # 发送者
    timestamp: datetime             # 时间戳
    message_type: MessageType       # 消息类型
    emotion: EmotionState           # 情绪状态
    metadata: Dict                  # 元数据
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type.value,
            "emotion": self.emotion.value,
            "metadata": self.metadata
        }
```

---

### 10. 智能体记忆 (AgentMemory)

**模块**: `agents.base_agent`

```python
@dataclass
class AgentMemory:
    user_id: str                    # 用户ID
    short_term: List[AgentMessage]  # 短期记忆（对话历史）
    long_term: Dict                 # 长期记忆（用户画像）
    context: Dict                   # 上下文数据
    
    def add_message(self, message: AgentMessage):
        """添加消息到短期记忆"""
        self.short_term.append(message)
        if len(self.short_term) > 20:  # 保留最近20条
            self.short_term = self.short_term[-20:]
    
    def update_user_profile(self, key: str, value: Any):
        """更新用户画像"""
        self.long_term[key] = value
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """获取上下文"""
        return self.context.get(key, default)
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term = []
```

---

## 枚举类型

### AssessmentType - 评估类型

```python
class AssessmentType(Enum):
    SCHEDULED = "scheduled"     # 定期评估
    ON_DEMAND = "on_demand"     # 按需评估
```

### AssessmentPeriod - 评估周期

```python
class AssessmentPeriod(Enum):
    WEEKLY = "weekly"           # 每周
    MONTHLY = "monthly"         # 每月
    QUARTERLY = "quarterly"     # 每季度
    ON_DEMAND = "on_demand"     # 按需
```

### TimeWindow - 时间窗口

```python
class TimeWindow(Enum):
    LAST_7_DAYS = "last_7_days"
    LAST_14_DAYS = "last_14_days"
    LAST_30_DAYS = "last_30_days"
    CUSTOM = "custom"
```

### RiskLevel - 风险等级

```python
class RiskLevel(Enum):
    LOW = "low"                 # 低风险
    MEDIUM = "medium"           # 中风险
    HIGH = "high"               # 高风险
    VERY_HIGH = "very_high"     # 极高风险
```

### ControlStatus - 控制状态

```python
class ControlStatus(Enum):
    EXCELLENT = "excellent"     # 优秀
    GOOD = "good"               # 良好
    FAIR = "fair"               # 一般
    POOR = "poor"               # 较差
    UNCONTROLLED = "uncontrolled"  # 未控制
```

### HealthLevel - 健康等级

```python
class HealthLevel(Enum):
    EXCELLENT = "excellent"     # 优秀 (≥85分)
    GOOD = "good"               # 良好 (70-85分)
    SUBOPTIMAL = "suboptimal"   # 亚健康 (55-70分)
    ATTENTION = "attention"     # 需关注 (40-55分)
    HIGH_RISK = "high_risk"     # 高风险 (<40分)
```

### RiskPriority - 风险优先级

```python
class RiskPriority(Enum):
    CRITICAL = "critical"       # 紧急
    HIGH = "high"               # 高
    MEDIUM = "medium"           # 中
    LOW = "low"                 # 低
```

### ReportType - 报告类型

```python
class ReportType(Enum):
    ELDERLY = "elderly"         # 老人版
    FAMILY = "family"           # 家属版
    COMMUNITY = "community"     # 社区版
```

### ReportFormat - 报告格式

```python
class ReportFormat(Enum):
    TEXT = "text"               # 纯文本
    JSON = "json"               # JSON
    HTML = "html"               # HTML
    PDF = "pdf"                 # PDF
```

### AgentRole - 智能体角色

```python
class AgentRole(Enum):
    HEALTH_BUTLER = "health_butler"       # 健康管家
    CHRONIC_EXPERT = "chronic_expert"     # 慢病专家
    LIFESTYLE_COACH = "lifestyle_coach"   # 生活教练
    EMOTIONAL_CARE = "emotional_care"     # 心理关怀
```

### MessageType - 消息类型

```python
class MessageType(Enum):
    USER_INPUT = "user_input"   # 用户输入
    AGENT_RESPONSE = "agent_response"  # 智能体响应
    SYSTEM = "system"           # 系统消息
```

### EmotionState - 情绪状态

```python
class EmotionState(Enum):
    HAPPY = "happy"             # 开心
    NEUTRAL = "neutral"         # 中性
    CONCERNED = "concerned"     # 关切
    ENCOURAGING = "encouraging" # 鼓励
    EMPATHETIC = "empathetic"   # 同理
```

---

## 数据库表结构

### elder_info - 老人信息表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INT | 主键 |
| `name` | VARCHAR(50) | 姓名 |
| `gender` | TINYINT | 性别 (0女/1男/2其他) |
| `birthday` | DATE | 出生日期 |
| `age` | INT | 年龄 |
| `phone` | VARCHAR(20) | 联系电话 |
| `address` | VARCHAR(255) | 居住地址 |
| `height_cm` | DECIMAL(5,2) | 身高(cm) |
| `chronic_tags` | VARCHAR(255) | 慢病标签 |
| `status` | TINYINT | 状态 (1在管/0离开) |
| `remark` | VARCHAR(255) | 备注 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### health_record - 健康检测记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INT | 主键 |
| `elder_id` | INT | 老人ID (FK) |
| `tester_code` | VARCHAR(50) | 检测人/设备编号 |
| `check_time` | DATETIME | 检查时间 |
| `spo2` | TINYINT | 血氧 |
| `spo2_status` | VARCHAR(20) | 血氧状态 |
| `heart_rate` | TINYINT | 心率 |
| `heart_rate_status` | VARCHAR(20) | 心率状态 |
| `diastolic_bp` | TINYINT | 舒张压 |
| `systolic_bp` | TINYINT | 收缩压 |
| `pulse_rate` | TINYINT | 脉率 |
| `blood_sugar` | DECIMAL(4,1) | 血糖 |
| `uric_acid` | INT | 血尿酸 |
| `body_temperature` | DECIMAL(3,1) | 体温 |
| `health_risk_level` | VARCHAR(20) | 健康风险等级 |
| `sleep_hours` | DECIMAL(4,1) | 睡眠时长 |
| `steps` | INT | 步数 |
| `weight_kg` | DECIMAL(5,2) | 体重 |
| `data_source` | VARCHAR(20) | 数据来源 |
| `created_at` | DATETIME | 创建时间 |

### assessment_result - 评估结果表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INT | 主键 |
| `elder_id` | INT | 老人ID (FK) |
| `assessment_time` | DATETIME | 评估时间 |
| `window_start_date` | DATE | 窗口开始日期 |
| `window_end_date` | DATE | 窗口结束日期 |
| `data_quality_flag` | VARCHAR(20) | 数据质量标记 |
| `overall_risk_level` | VARCHAR(20) | 综合风险等级 |
| `overall_risk_score` | DECIMAL(5,2) | 综合风险分 |
| `disease_overall_score` | DECIMAL(5,2) | 疾病维度分 |
| `lifestyle_risk_score` | DECIMAL(5,2) | 生活方式维度分 |
| `trend_risk_score` | DECIMAL(5,2) | 趋势维度分 |
| `comorbidity_count` | INT | 合并症数量 |
| `main_diseases` | VARCHAR(255) | 主要疾病 |
| `topsis_score` | DECIMAL(5,3) | TOPSIS分数 |
| `disease_summary_json` | JSON | 疾病详情JSON |
| `advice_text_elder` | TEXT | 老人建议 |
| `advice_text_family` | TEXT | 家属建议 |
| `key_risk_factors` | VARCHAR(255) | 关键风险因素 |
| `created_at` | DATETIME | 创建时间 |

### ai_consult_log - AI问诊记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INT | 主键 |
| `elder_id` | INT | 老人ID (FK) |
| `user_id` | INT | 用户ID (FK) |
| `consult_time` | DATETIME | 问诊时间 |
| `channel` | VARCHAR(20) | 渠道 |
| `question` | TEXT | 问题 |
| `answer` | TEXT | 回答 |
| `ref_assessment_id` | INT | 关联评估ID |
| `risk_level_at_time` | VARCHAR(20) | 当时风险等级 |
| `model_version` | VARCHAR(50) | 模型版本 |
| `created_at` | DATETIME | 创建时间 |

---

## JSON数据格式

### 可视化数据格式

```json
{
    "overview": {
        "overall_score": 65.5,
        "health_level": "suboptimal",
        "health_level_text": "亚健康",
        "assessment_date": "2024-01-15T10:30:00",
        "data_quality": "complete"
    },
    "dimension_scores": {
        "disease": {
            "score": 45,
            "level": "medium",
            "label": "疾病风险"
        },
        "lifestyle": {
            "score": 55,
            "level": "low",
            "label": "生活方式"
        },
        "trend": {
            "score": 70,
            "level": "low",
            "label": "趋势变化"
        }
    },
    "risk_factors": [
        {
            "name": "高血压",
            "score": 65,
            "priority": "high",
            "category": "disease",
            "description": "血压控制一般，波动较大",
            "recommendation": "加强血压监测，规律服药"
        }
    ],
    "trend_indicators": [
        {
            "metric": "sbp",
            "metric_name": "收缩压",
            "direction": "worsening",
            "direction_text": "恶化",
            "deviation": 8.5,
            "baseline": 130,
            "current": 138.5
        }
    ],
    "risk_distribution": {
        "high": 1,
        "medium": 2,
        "low": 3
    },
    "recommendations": [
        {
            "priority": 1,
            "category": "disease",
            "content": "加强血压监测，规律服药，减少盐分摄入"
        },
        {
            "priority": 2,
            "category": "lifestyle",
            "content": "增加日常活动量，每天至少6000步"
        }
    ]
}
```

### 疾病详情JSON格式

```json
{
    "hypertension": {
        "disease_name": "高血压",
        "control_status": "fair",
        "risk_level": "medium",
        "risk_score": 45,
        "control_quality_score": 65,
        "bp_grade": 2,
        "compliance_rate": 0.7,
        "key_findings": [
            "血压控制一般",
            "波动较大"
        ],
        "recommendations": [
            "加强监测",
            "规律服药"
        ]
    },
    "diabetes": {
        "disease_name": "糖尿病",
        "control_status": "good",
        "risk_level": "low",
        "risk_score": 30,
        "control_quality_score": 75,
        "fasting_compliance_rate": 0.8,
        "postprandial_compliance_rate": 0.7,
        "glucose_cv": 0.15,
        "key_findings": [
            "血糖控制良好"
        ],
        "recommendations": [
            "继续保持"
        ]
    }
}
```

---

## 配置文件结构

### health_standards.json - 健康标准配置

```json
{
    "blood_pressure": {
        "normal": {
            "systolic": [90, 120],
            "diastolic": [60, 80]
        },
        "elevated": {
            "systolic": [120, 130],
            "diastolic": [80, 80]
        },
        "stage1_hypertension": {
            "systolic": [130, 140],
            "diastolic": [80, 90]
        },
        "stage2_hypertension": {
            "systolic": [140, 180],
            "diastolic": [90, 120]
        },
        "hypertensive_crisis": {
            "systolic": [180, 999],
            "diastolic": [120, 999]
        }
    },
    "blood_glucose": {
        "fasting": {
            "normal": [3.9, 6.1],
            "prediabetes": [6.1, 7.0],
            "diabetes": [7.0, 999]
        },
        "postprandial_2h": {
            "normal": [3.9, 7.8],
            "prediabetes": [7.8, 11.1],
            "diabetes": [11.1, 999]
        }
    },
    "lipids": {
        "total_cholesterol": {
            "desirable": [0, 5.2],
            "borderline_high": [5.2, 6.2],
            "high": [6.2, 999]
        },
        "ldl": {
            "optimal": [0, 2.6],
            "near_optimal": [2.6, 3.4],
            "borderline_high": [3.4, 4.1],
            "high": [4.1, 4.9],
            "very_high": [4.9, 999]
        },
        "hdl": {
            "low": [0, 1.0],
            "normal": [1.0, 1.5],
            "high": [1.5, 999]
        },
        "triglycerides": {
            "normal": [0, 1.7],
            "borderline_high": [1.7, 2.3],
            "high": [2.3, 5.6],
            "very_high": [5.6, 999]
        }
    },
    "heart_rate": {
        "bradycardia": [0, 60],
        "normal": [60, 100],
        "tachycardia": [100, 999]
    },
    "spo2": {
        "normal": [95, 100],
        "mild_hypoxia": [90, 95],
        "moderate_hypoxia": [85, 90],
        "severe_hypoxia": [0, 85]
    }
}
```

### assessment_config.json - 评估系统配置

```json
{
    "assessment_weights": {
        "disease_risk": 0.45,
        "lifestyle_risk": 0.30,
        "trend_risk": 0.25
    },
    "ahp_comparison_matrix": {
        "disease_vs_lifestyle": 1.5,
        "disease_vs_trend": 2.0,
        "lifestyle_vs_trend": 1.3
    },
    "topsis_criteria_weights": {
        "severity": 0.35,
        "urgency": 0.30,
        "frequency": 0.20,
        "trend": 0.15
    },
    "health_levels": {
        "excellent": {
            "min_score": 85,
            "label": "优秀",
            "color": "#4CAF50"
        },
        "good": {
            "min_score": 70,
            "label": "良好",
            "color": "#8BC34A"
        },
        "suboptimal": {
            "min_score": 55,
            "label": "亚健康",
            "color": "#FFC107"
        },
        "attention": {
            "min_score": 40,
            "label": "需关注",
            "color": "#FF9800"
        },
        "high_risk": {
            "min_score": 0,
            "label": "高风险",
            "color": "#F44336"
        }
    },
    "data_requirements": {
        "minimum_days": 7,
        "required_metrics": [
            "blood_pressure",
            "blood_glucose"
        ],
        "optional_metrics": [
            "sleep",
            "steps",
            "weight",
            "heart_rate"
        ]
    },
    "report_settings": {
        "elderly": {
            "max_risk_factors": 3,
            "max_recommendations": 3,
            "font_size": "large"
        },
        "family": {
            "max_risk_factors": 5,
            "max_recommendations": 5,
            "include_trends": true
        },
        "community": {
            "max_risk_factors": 3,
            "max_recommendations": 3,
            "summary_only": true
        }
    }
}
```

---

**版本**: v1.0.0  
**更新日期**: 2024-01-15
