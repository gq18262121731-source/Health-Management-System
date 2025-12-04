# API 接口参考文档 (API Reference)

## 📋 目录

- [核心引擎 API](#核心引擎-api)
- [多智能体系统 API](#多智能体系统-api)
- [Web API 接口](#web-api-接口)
- [模块级 API](#模块级-api)
- [数据库操作 API](#数据库操作-api)

---

## 核心引擎 API

### HealthAssessmentEngine

**模块**: `core.assessment_engine`

#### 初始化

```python
from health_assessment_system import HealthAssessmentEngine

engine = HealthAssessmentEngine()
```

#### 方法列表

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `run_scheduled_assessment()` | 运行定期评估 | `ComprehensiveAssessmentResult` |
| `run_on_demand_assessment()` | 运行按需评估 | `ComprehensiveAssessmentResult` |
| `generate_report()` | 生成评估报告 | `str` |
| `get_visualization_data()` | 获取可视化数据 | `Dict` |
| `get_user_assessment_history()` | 获取用户评估历史 | `List[AssessmentRecord]` |

---

### run_scheduled_assessment

运行定期健康评估。

```python
def run_scheduled_assessment(
    self,
    user_id: str,
    period: AssessmentPeriod = AssessmentPeriod.MONTHLY,
    time_window: TimeWindow = TimeWindow.LAST_30_DAYS
) -> ComprehensiveAssessmentResult
```

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `user_id` | `str` | ✅ | - | 用户唯一标识 |
| `period` | `AssessmentPeriod` | ❌ | `MONTHLY` | 评估周期 |
| `time_window` | `TimeWindow` | ❌ | `LAST_30_DAYS` | 时间窗口 |

**AssessmentPeriod 枚举**:
- `WEEKLY` - 每周评估
- `MONTHLY` - 每月评估
- `QUARTERLY` - 每季度评估
- `ON_DEMAND` - 按需评估

**TimeWindow 枚举**:
- `LAST_7_DAYS` - 最近7天
- `LAST_14_DAYS` - 最近14天
- `LAST_30_DAYS` - 最近30天
- `CUSTOM` - 自定义

**返回值**: `ComprehensiveAssessmentResult`

**示例**:
```python
from health_assessment_system.modules.assessment_config import AssessmentPeriod, TimeWindow

result = engine.run_scheduled_assessment(
    user_id="USER001",
    period=AssessmentPeriod.MONTHLY,
    time_window=TimeWindow.LAST_30_DAYS
)

print(f"综合评分: {result.overall_score}")
print(f"健康等级: {result.health_level.value}")
```

---

### run_on_demand_assessment

运行按需健康评估（由家属、社区或医生触发）。

```python
def run_on_demand_assessment(
    self,
    user_id: str,
    triggered_by: str,
    custom_days: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> ComprehensiveAssessmentResult
```

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `user_id` | `str` | ✅ | - | 用户唯一标识 |
| `triggered_by` | `str` | ✅ | - | 触发者类型: `family`/`community`/`doctor` |
| `custom_days` | `int` | ❌ | `None` | 自定义天数 |
| `start_date` | `datetime` | ❌ | `None` | 开始日期 |
| `end_date` | `datetime` | ❌ | `None` | 结束日期 |

**示例**:
```python
# 家属触发的14天评估
result = engine.run_on_demand_assessment(
    user_id="USER001",
    triggered_by="family",
    custom_days=14
)

# 自定义日期范围
from datetime import datetime
result = engine.run_on_demand_assessment(
    user_id="USER001",
    triggered_by="doctor",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 15)
)
```

---

### generate_report

生成评估报告。

```python
def generate_report(
    self,
    assessment_id: str,
    user_id: str,
    report_type: ReportType = ReportType.FAMILY,
    report_format: ReportFormat = ReportFormat.TEXT
) -> str
```

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `assessment_id` | `str` | ✅ | - | 评估ID |
| `user_id` | `str` | ✅ | - | 用户ID |
| `report_type` | `ReportType` | ❌ | `FAMILY` | 报告类型 |
| `report_format` | `ReportFormat` | ❌ | `TEXT` | 报告格式 |

**ReportType 枚举**:
- `ELDERLY` - 老人版（简短易懂）
- `FAMILY` - 家属版（详细完整）
- `COMMUNITY` - 社区版（简洁摘要）

**ReportFormat 枚举**:
- `TEXT` - 纯文本
- `JSON` - JSON格式
- `HTML` - HTML格式
- `PDF` - PDF格式

**示例**:
```python
from health_assessment_system.modules.report_generation import ReportType, ReportFormat

# 生成老人版文本报告
report = engine.generate_report(
    assessment_id=result.assessment_id,
    user_id="USER001",
    report_type=ReportType.ELDERLY,
    report_format=ReportFormat.TEXT
)
print(report)

# 生成家属版HTML报告
html_report = engine.generate_report(
    assessment_id=result.assessment_id,
    user_id="USER001",
    report_type=ReportType.FAMILY,
    report_format=ReportFormat.HTML
)
```

---

### get_visualization_data

获取可视化数据接口。

```python
def get_visualization_data(
    self,
    assessment_id: str,
    user_id: str
) -> Dict
```

**返回值结构**:
```python
{
    "overview": {
        "overall_score": 65.5,
        "health_level": "suboptimal",
        "assessment_date": "2024-01-15T10:30:00"
    },
    "dimension_scores": {
        "disease": 45,
        "lifestyle": 55,
        "trend": 70
    },
    "risk_factors": [...],
    "trend_indicators": [...],
    "risk_distribution": {...}
}
```

---

### get_user_assessment_history

获取用户评估历史记录。

```python
def get_user_assessment_history(
    self,
    user_id: str,
    limit: int = 10
) -> List[AssessmentRecord]
```

**示例**:
```python
history = engine.get_user_assessment_history(user_id="USER001", limit=5)

for record in history:
    print(f"日期: {record.assessment_date}")
    print(f"评分: {record.overall_score}")
    print(f"等级: {record.health_level}")
```

---

## 多智能体系统 API

### MultiAgentSystem

**模块**: `agents.multi_agent_system`

#### 初始化

```python
from agents import MultiAgentSystem

system = MultiAgentSystem(
    user_id: str,
    user_name: str = "",
    enable_assessment: bool = True
)
```

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `user_id` | `str` | ✅ | - | 用户唯一标识 |
| `user_name` | `str` | ❌ | `""` | 用户姓名 |
| `enable_assessment` | `bool` | ❌ | `True` | 是否启用健康评估集成 |

#### 方法列表

| 方法 | 描述 | 返回类型 |
|------|------|----------|
| `chat()` | 与数字人对话 | `str` |
| `get_greeting()` | 获取问候语 | `str` |
| `get_agents_info()` | 获取所有智能体信息 | `List[Dict]` |
| `get_session_info()` | 获取会话信息 | `Dict` |
| `clear_conversation()` | 清空对话历史 | `None` |
| `update_health_data()` | 更新健康数据 | `None` |
| `set_user_profile()` | 设置用户画像 | `None` |
| `get_user_profile()` | 获取用户画像 | `Dict` |

---

### chat

与数字人进行对话。

```python
def chat(self, user_input: str) -> str
```

**特殊触发词**:
- 包含 `评估`、`报告`、`分析` → 生成健康报告
- 包含 `全面`、`综合`、`专家` → 多智能体协作会诊

**示例**:
```python
# 普通对话
response = system.chat("我最近血压有点高")

# 触发健康报告
report = system.chat("帮我做个健康评估")

# 触发专家会诊
consultation = system.chat("请专家全面分析一下")
```

---

### update_health_data

更新用户健康数据到记忆系统。

```python
def update_health_data(self, data_type: str, data: Dict)
```

**支持的数据类型**:
- `blood_pressure` - 血压数据
- `glucose` - 血糖数据
- `sleep` - 睡眠数据
- `steps` - 步数数据
- `weight` - 体重数据

**示例**:
```python
system.update_health_data("blood_pressure", {
    "systolic": 135,
    "diastolic": 85,
    "pulse": 72,
    "time": "2024-01-15 08:00"
})

system.update_health_data("glucose", {
    "fasting": 6.2,
    "postprandial": 8.5,
    "time": "2024-01-15 07:00"
})
```

---

### set_user_profile / get_user_profile

设置和获取用户画像。

```python
def set_user_profile(self, key: str, value: Any)
def get_user_profile(self) -> Dict
```

**常用画像字段**:
- `name` - 姓名
- `age` - 年龄
- `gender` - 性别
- `chronic_diseases` - 慢病列表
- `medications` - 用药列表
- `allergies` - 过敏史

**示例**:
```python
system.set_user_profile("chronic_diseases", ["高血压", "2型糖尿病"])
system.set_user_profile("age", 68)

profile = system.get_user_profile()
print(profile)
```

---

## Web API 接口

### 基础信息

- **基础URL**: `http://localhost:5000`
- **内容类型**: `application/json`

### 端点列表

| 方法 | 端点 | 描述 |
|------|------|------|
| `GET` | `/` | 主页（3D数字人界面） |
| `POST` | `/api/chat` | 聊天接口 |
| `GET` | `/api/greeting` | 获取问候语 |
| `GET` | `/models/<filename>` | 获取VRM模型文件 |

---

### POST /api/chat

与AI数字人对话。

**请求**:
```json
{
    "message": "我最近血压有点高"
}
```

**响应**:
```json
{
    "response": "血压偏高需要注意...",
    "emotion": "happy"
}
```

**emotion 可选值**:
- `happy` - 开心
- `neutral` - 中性
- `concerned` - 关切
- `encouraging` - 鼓励

**cURL 示例**:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

**JavaScript 示例**:
```javascript
async function chat(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
    });
    return await response.json();
}

const result = await chat('我血压有点高');
console.log(result.response);
```

---

### GET /api/greeting

获取问候语。

**响应**:
```json
{
    "message": "你好！我是小康，很高兴见到你！"
}
```

---

## 模块级 API

### 评估配置模块

**模块**: `modules.assessment_config`

```python
from modules.assessment_config import (
    AssessmentTaskManager,
    AssessmentConfig,
    AssessmentType,
    AssessmentPeriod,
    TimeWindow,
    DataCompletenessReport
)

# 创建任务管理器
task_manager = AssessmentTaskManager()

# 创建定期评估配置
config = task_manager.create_scheduled_assessment(
    user_id="USER001",
    period=AssessmentPeriod.MONTHLY,
    time_window=TimeWindow.LAST_30_DAYS
)

# 检查数据完整性
completeness = task_manager.check_data_completeness(config, raw_data)
print(f"完整性等级: {completeness.completeness_level.value}")
print(f"完整率: {completeness.overall_completeness_rate}")
```

---

### 数据准备模块

**模块**: `modules.data_preparation`

```python
from modules.data_preparation import (
    FeatureEngineer,
    DataPreprocessor,
    HealthMetrics,
    FeatureSet
)

# 创建特征工程器
feature_engineer = FeatureEngineer()

# 构建特征
features = feature_engineer.build_features(
    user_id="USER001",
    raw_data=raw_data,
    assessment_period=(start_date, end_date),
    baseline_data=baseline
)

# 转换为字典
feature_dict = features.to_dict()
```

---

### 单病种评估模块

**模块**: `modules.disease_assessment`

```python
from modules.disease_assessment import (
    HypertensionAssessor,
    DiabetesAssessor,
    DyslipidemiAssessor,
    DiseaseRiskResult,
    RiskLevel,
    ControlStatus
)

# 高血压评估
ht_assessor = HypertensionAssessor()
ht_result = ht_assessor.assess(features, baseline)

print(f"控制状态: {ht_result.control_status.value}")
print(f"风险等级: {ht_result.risk_level.value}")
print(f"风险评分: {ht_result.risk_score}")
print(f"关键发现: {ht_result.key_findings}")

# 糖尿病评估
dm_assessor = DiabetesAssessor()
dm_result = dm_assessor.assess(features, baseline)

# 血脂评估
dl_assessor = DyslipidemiAssessor()
dl_result = dl_assessor.assess(features, baseline)
```

**RiskLevel 枚举**:
- `LOW` - 低风险
- `MEDIUM` - 中风险
- `HIGH` - 高风险
- `VERY_HIGH` - 极高风险

**ControlStatus 枚举**:
- `EXCELLENT` - 优秀
- `GOOD` - 良好
- `FAIR` - 一般
- `POOR` - 较差
- `UNCONTROLLED` - 未控制

---

### 生活方式评估模块

**模块**: `modules.lifestyle_assessment`

```python
from modules.lifestyle_assessment import (
    LifestyleAssessmentEngine,
    SleepQualityAssessor,
    ExerciseAssessor,
    DietAssessor,
    LifestyleRiskResult
)

# 创建评估引擎
lifestyle_engine = LifestyleAssessmentEngine()

# 综合评估
result = lifestyle_engine.assess(
    features=feature_dict,
    diet_data=diet_data
)

print(f"综合评分: {result.overall_score}")
print(f"睡眠评分: {result.sleep_score}")
print(f"运动评分: {result.exercise_score}")
print(f"饮食评分: {result.diet_score}")
print(f"风险等级: {result.overall_risk_level.value}")
```

---

### 综合评估模块

**模块**: `modules.comprehensive_assessment`

```python
from modules.comprehensive_assessment import (
    RiskFusionEngine,
    AHPWeightCalculator,
    TOPSISRanker,
    ComprehensiveAssessmentResult,
    HealthLevel,
    RiskFactor
)

# 创建风险融合引擎
fusion_engine = RiskFusionEngine()

# 融合多维度风险
result = fusion_engine.fuse_risks(
    disease_results=disease_results,
    lifestyle_result=lifestyle_result,
    trend_results=trend_results,
    user_id="USER001",
    assessment_id="ASM_001"
)

print(f"综合评分: {result.overall_score}")
print(f"健康等级: {result.health_level.value}")
print(f"TOP风险因素: {[rf.name for rf in result.top_risk_factors]}")
print(f"优先建议: {result.priority_recommendations}")
```

**HealthLevel 枚举**:
- `EXCELLENT` - 优秀 (≥85分)
- `GOOD` - 良好 (70-85分)
- `SUBOPTIMAL` - 亚健康 (55-70分)
- `ATTENTION` - 需关注 (40-55分)
- `HIGH_RISK` - 高风险 (<40分)

---

### 报告生成模块

**模块**: `modules.report_generation`

```python
from modules.report_generation import (
    ReportGenerator,
    AssessmentRecordManager,
    AssessmentRecord,
    ReportType,
    ReportFormat
)

# 报告生成器
report_generator = ReportGenerator()

# 生成报告
report = report_generator.generate_report(
    result_dict=result.to_dict(),
    report_type=ReportType.ELDERLY,
    report_format=ReportFormat.TEXT
)

# 生成可视化数据
viz_data = report_generator.generate_visualization_data(result.to_dict())

# 记录管理器
record_manager = AssessmentRecordManager()

# 保存记录
record_manager.save_record(record)

# 加载记录
record = record_manager.load_record(assessment_id, user_id)

# 获取用户记录列表
records = record_manager.get_user_records(user_id, limit=10)
```

---

## 数据库操作 API

### DatabaseManager

**模块**: `core.database_manager`

```python
from core.database_manager import DatabaseManager

# 创建数据库管理器
db = DatabaseManager(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="health_assessment_db"
)

# 获取老人信息
elder = db.get_elder_info(elder_id=1)

# 获取最新健康记录
record = db.get_latest_health_record(elder_id=1)

# 获取评估结果
assessment = db.get_latest_assessment(elder_id=1)

# 保存健康记录
db.save_health_record({
    "elder_id": 1,
    "check_time": "2024-01-15 08:00:00",
    "systolic_bp": 135,
    "diastolic_bp": 85,
    "heart_rate": 72
})

# 保存评估结果
db.save_assessment_result({
    "elder_id": 1,
    "overall_risk_score": 65.5,
    "overall_risk_level": "MEDIUM",
    ...
})
```

---

## 错误处理

### 常见异常

```python
# 评估数据不足
class InsufficientDataError(Exception):
    pass

# 配置错误
class ConfigurationError(Exception):
    pass

# 评估失败
class AssessmentError(Exception):
    pass
```

### 错误处理示例

```python
try:
    result = engine.run_scheduled_assessment(user_id="USER001")
except InsufficientDataError as e:
    print(f"数据不足: {e}")
except AssessmentError as e:
    print(f"评估失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 类型定义

### TypedDict 定义

```python
from typing import TypedDict, List, Optional

class HealthRecordDict(TypedDict):
    elder_id: int
    check_time: str
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    heart_rate: Optional[int]
    blood_sugar: Optional[float]
    spo2: Optional[int]

class AssessmentResultDict(TypedDict):
    assessment_id: str
    user_id: str
    overall_score: float
    health_level: str
    disease_risk_score: float
    lifestyle_risk_score: float
    trend_risk_score: float
    top_risk_factors: List[dict]
    recommendations: List[str]

class VisualizationDataDict(TypedDict):
    overview: dict
    dimension_scores: dict
    risk_factors: List[dict]
    trend_indicators: List[dict]
    risk_distribution: dict
```

---

**版本**: v1.0.0  
**更新日期**: 2024-01-15
