# 系统融合指南 (Integration Guide)

## 📋 概述

本文档提供了**多模型健康评估系统**的完整融合指南，帮助开发者快速理解和集成系统的各个组件。

---

## 🏗️ 系统架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           应用层 (Application Layer)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │   Web API       │  │   3D数字人       │  │   桌面应用       │          │
│  │   (Flask)       │  │   (VRM/Three.js) │  │   (PyQt5)       │          │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │
└───────────┼─────────────────────┼─────────────────────┼──────────────────┘
            │                     │                     │
┌───────────┼─────────────────────┼─────────────────────┼──────────────────┐
│           ▼                     ▼                     ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    多智能体系统 (Multi-Agent System)              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │健康管家   │ │慢病专家   │ │生活教练   │ │心理关怀   │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                      │
│                                   ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                 健康评估引擎 (Health Assessment Engine)           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                      │
│           ┌───────────────────────┼───────────────────────┐              │
│           ▼                       ▼                       ▼              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  评估配置管理    │  │  数据准备处理    │  │  风险评估模块    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  生活方式评估    │  │  综合风险融合    │  │  报告生成管理    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│                              核心业务层                                   │
└──────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           数据层 (Data Layer)                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  MySQL数据库     │  │  JSON配置文件    │  │  评估记录存储    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
health_assessment_system/
│
├── __init__.py                      # 包入口，导出 HealthAssessmentEngine
├── requirements.txt                 # Python依赖
├── run_web.py                       # Web服务启动脚本
├── run_shark.py                     # 桌面应用启动脚本
│
├── core/                            # 核心引擎
│   ├── __init__.py
│   ├── assessment_engine.py         # 健康评估主引擎 ⭐
│   └── database_manager.py          # 数据库管理器
│
├── modules/                         # 六大核心模块
│   ├── __init__.py
│   ├── assessment_config.py         # 模块1: 评估配置与任务管理
│   ├── data_preparation.py          # 模块2: 数据准备与特征构建
│   ├── disease_assessment.py        # 模块3: 单病种风险评估
│   ├── lifestyle_assessment.py      # 模块4: 生活方式评估
│   ├── comprehensive_assessment.py  # 模块5: 综合风险评估
│   ├── report_generation.py         # 模块6: 报告生成
│   ├── indicator_evaluator.py       # 指标评估器
│   ├── health_report_models.py      # 健康报告数据模型
│   └── yangsheng_report_generator.py # 养生报告生成器
│
├── agents/                          # 多智能体系统
│   ├── __init__.py
│   ├── base_agent.py                # 智能体基类
│   ├── health_butler.py             # 健康管家智能体
│   ├── chronic_disease_expert.py    # 慢病专家智能体
│   ├── lifestyle_coach.py           # 生活教练智能体
│   ├── emotional_care.py            # 心理关怀智能体
│   ├── agent_coordinator.py         # 智能体协调器
│   └── multi_agent_system.py        # 多智能体系统入口 ⭐
│
├── config/                          # 配置文件
│   ├── health_standards.json        # 健康标准配置
│   ├── assessment_config.json       # 评估系统配置
│   └── indicator_reference.json     # 指标参考配置
│
├── database/                        # 数据库
│   ├── README.md                    # 数据库说明
│   ├── schema.sql                   # 数据库表结构
│   └── seed_data.sql                # 测试数据
│
├── web_digital_human/               # Web版数字人
│   ├── app.py                       # Flask后端
│   └── static/                      # 前端静态文件
│
├── digital_human_3d/                # 桌面版3D数字人
│   ├── __init__.py
│   ├── vrm_viewer.py                # VRM模型查看器
│   └── models/                      # 3D模型文件
│
├── examples/                        # 示例代码
│   ├── complete_demo.py             # 完整演示
│   ├── digital_human_demo.py        # 数字人演示
│   ├── generate_report_from_db.py   # 从数据库生成报告
│   └── yangsheng_report_demo.py     # 养生报告演示
│
└── docs/                            # 文档
    ├── README.md
    ├── 养生之道报告实施方案.md
    └── 算法学习指南.md
```

---

## 🔌 核心组件接口

### 1. 健康评估引擎 (HealthAssessmentEngine)

**位置**: `core/assessment_engine.py`

```python
from health_assessment_system import HealthAssessmentEngine
from health_assessment_system.modules.assessment_config import AssessmentPeriod, TimeWindow
from health_assessment_system.modules.report_generation import ReportType, ReportFormat

# 创建引擎
engine = HealthAssessmentEngine()

# 运行定期评估
result = engine.run_scheduled_assessment(
    user_id="USER001",
    period=AssessmentPeriod.MONTHLY,
    time_window=TimeWindow.LAST_30_DAYS
)

# 运行按需评估
result = engine.run_on_demand_assessment(
    user_id="USER001",
    triggered_by="family",  # family/community/doctor
    custom_days=14
)

# 生成报告
report = engine.generate_report(
    assessment_id=result.assessment_id,
    user_id=result.user_id,
    report_type=ReportType.ELDERLY,  # ELDERLY/FAMILY/COMMUNITY
    report_format=ReportFormat.TEXT   # TEXT/JSON/HTML
)

# 获取可视化数据
viz_data = engine.get_visualization_data(
    assessment_id=result.assessment_id,
    user_id=result.user_id
)

# 获取历史记录
history = engine.get_user_assessment_history(user_id="USER001", limit=10)
```

### 2. 多智能体系统 (MultiAgentSystem)

**位置**: `agents/multi_agent_system.py`

```python
from agents import MultiAgentSystem

# 创建系统
system = MultiAgentSystem(
    user_id="USER001",
    user_name="张三",
    enable_assessment=True  # 是否启用健康评估集成
)

# 对话
response = system.chat("我最近血压有点高，该怎么办？")
print(response)

# 获取问候语
greeting = system.get_greeting()

# 获取健康报告
report = system.chat("帮我做个健康评估")

# 专家会诊（多智能体协作）
consultation = system.chat("请专家全面分析一下我的健康状况")

# 更新健康数据
system.update_health_data("blood_pressure", {
    "systolic": 135,
    "diastolic": 85,
    "time": "2024-01-15 08:00"
})

# 设置用户画像
system.set_user_profile("chronic_diseases", ["高血压", "糖尿病"])

# 获取会话信息
session_info = system.get_session_info()

# 清空对话历史
system.clear_conversation()
```

### 3. Web API 接口

**位置**: `web_digital_human/app.py`

```python
# 启动服务
python run_web.py
# 访问: http://localhost:5000

# API端点:
# GET  /                    - 主页
# POST /api/chat            - 聊天接口
# GET  /api/greeting        - 获取问候语
# GET  /models/<filename>   - 获取VRM模型文件
```

**聊天API示例**:
```javascript
// POST /api/chat
fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: '我血压有点高'})
})
.then(res => res.json())
.then(data => {
    console.log(data.response);  // AI回复
    console.log(data.emotion);   // 情绪状态
});
```

---

## 📊 数据结构

### 评估结果 (ComprehensiveAssessmentResult)

```python
{
    "assessment_id": "ASM_20240115_001",
    "user_id": "USER001",
    "assessment_date": "2024-01-15T10:30:00",
    "overall_score": 65.5,           # 综合评分 0-100
    "health_level": "suboptimal",    # excellent/good/suboptimal/attention/high_risk
    "disease_risk_score": 45.0,      # 疾病维度评分
    "lifestyle_risk_score": 55.0,    # 生活方式维度评分
    "trend_risk_score": 70.0,        # 趋势维度评分
    "top_risk_factors": [            # TOP风险因素
        {
            "name": "高血压",
            "score": 65,
            "priority": "high",
            "category": "disease"
        }
    ],
    "priority_recommendations": [     # 优先建议
        "加强血压监测，规律服药",
        "增加日常活动量"
    ]
}
```

### 可视化数据结构

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
    "risk_factors": [
        {
            "name": "高血压",
            "score": 65,
            "priority": "high",
            "category": "disease"
        }
    ],
    "trend_indicators": [
        {
            "metric": "sbp",
            "direction": "worsening",
            "deviation": 8.5
        }
    ],
    "risk_distribution": {
        "high": 1,
        "medium": 2,
        "low": 3
    }
}
```

### 数据库表结构

| 表名 | 用途 | 主要字段 |
|------|------|----------|
| `elder_info` | 老人信息 | id, name, gender, birthday, chronic_tags |
| `user_account` | 用户账号 | id, username, password_hash, role |
| `elder_user_relation` | 老人-用户关系 | elder_id, user_id, relation_type |
| `health_record` | 健康检测记录 | elder_id, check_time, spo2, heart_rate, systolic_bp, blood_sugar |
| `assessment_result` | 评估结果 | elder_id, overall_risk_score, disease_summary_json |
| `ai_consult_log` | AI问诊记录 | elder_id, question, answer |

---

## 🔧 配置说明

### 健康标准配置 (config/health_standards.json)

```json
{
    "blood_pressure": {
        "normal": {"systolic": [90, 120], "diastolic": [60, 80]},
        "elevated": {"systolic": [120, 130], "diastolic": [80, 80]},
        "stage1": {"systolic": [130, 140], "diastolic": [80, 90]},
        "stage2": {"systolic": [140, 180], "diastolic": [90, 120]},
        "crisis": {"systolic": [180, 999], "diastolic": [120, 999]}
    },
    "blood_glucose": {
        "fasting": {"normal": [3.9, 6.1], "prediabetes": [6.1, 7.0], "diabetes": [7.0, 999]},
        "postprandial": {"normal": [3.9, 7.8], "prediabetes": [7.8, 11.1], "diabetes": [11.1, 999]}
    }
}
```

### 评估权重配置 (config/assessment_config.json)

```json
{
    "assessment_weights": {
        "disease_risk": 0.45,
        "lifestyle_risk": 0.30,
        "trend_risk": 0.25
    },
    "topsis_criteria_weights": {
        "severity": 0.35,
        "urgency": 0.30,
        "frequency": 0.20,
        "trend": 0.15
    },
    "health_levels": {
        "excellent": {"min_score": 85},
        "good": {"min_score": 70},
        "suboptimal": {"min_score": 55},
        "attention": {"min_score": 40},
        "high_risk": {"min_score": 0}
    }
}
```

---

## 🚀 快速集成

### 方式1: 作为Python包导入

```python
# 安装依赖
pip install -r requirements.txt

# 导入使用
from health_assessment_system import HealthAssessmentEngine
from health_assessment_system.agents import MultiAgentSystem

# 健康评估
engine = HealthAssessmentEngine()
result = engine.run_scheduled_assessment(user_id="USER001")

# 智能对话
system = MultiAgentSystem(user_id="USER001")
response = system.chat("你好")
```

### 方式2: 作为Web服务

```python
# 启动服务
python run_web.py

# 调用API
import requests

# 聊天
response = requests.post('http://localhost:5000/api/chat', 
    json={'message': '我血压有点高'})
print(response.json())
```

### 方式3: 嵌入现有系统

```python
# 在您的Flask/Django应用中集成
from health_assessment_system.agents import MultiAgentSystem
from health_assessment_system import HealthAssessmentEngine

class HealthService:
    def __init__(self):
        self.engine = HealthAssessmentEngine()
        self.agents = {}
    
    def get_agent(self, user_id):
        if user_id not in self.agents:
            self.agents[user_id] = MultiAgentSystem(user_id=user_id)
        return self.agents[user_id]
    
    def chat(self, user_id, message):
        agent = self.get_agent(user_id)
        return agent.chat(message)
    
    def assess(self, user_id):
        return self.engine.run_on_demand_assessment(
            user_id=user_id,
            triggered_by="system"
        )
```

---

## 🔗 模块依赖关系

```
HealthAssessmentEngine
    ├── AssessmentTaskManager (评估配置)
    ├── FeatureEngineer (特征工程)
    ├── HypertensionAssessor (高血压评估)
    ├── DiabetesAssessor (糖尿病评估)
    ├── DyslipidemiAssessor (血脂评估)
    ├── LifestyleAssessmentEngine (生活方式评估)
    ├── RiskFusionEngine (风险融合)
    ├── AssessmentRecordManager (记录管理)
    └── ReportGenerator (报告生成)

MultiAgentSystem
    ├── AgentCoordinator (协调器)
    │   ├── HealthButlerAgent (健康管家)
    │   ├── ChronicDiseaseExpertAgent (慢病专家)
    │   ├── LifestyleCoachAgent (生活教练)
    │   └── EmotionalCareAgent (心理关怀)
    ├── AgentMemory (记忆系统)
    └── HealthAssessmentEngine (可选集成)
```

---

## 📝 扩展开发

### 添加新的智能体

```python
from agents.base_agent import BaseAgent, AgentRole, AgentMessage

class NewExpertAgent(BaseAgent):
    def __init__(self, name="新专家"):
        super().__init__(
            name=name,
            role=AgentRole.CHRONIC_EXPERT,  # 或自定义角色
            description="新专家的描述"
        )
    
    def process(self, message, memory, context=None):
        # 实现处理逻辑
        response_text = self._generate_response(message)
        return AgentMessage(
            content=response_text,
            sender=self.name,
            metadata={"processed_by": self.role.value}
        )
    
    def can_handle(self, message, context=None):
        # 判断是否能处理该消息
        keywords = ["关键词1", "关键词2"]
        return any(k in message for k in keywords)
```

### 添加新的评估器

```python
from modules.disease_assessment import DiseaseRiskResult, RiskLevel, ControlStatus

class NewDiseaseAssessor:
    def __init__(self):
        self.thresholds = {...}
    
    def assess(self, features, baseline=None):
        # 实现评估逻辑
        risk_score = self._calculate_risk(features)
        
        return DiseaseRiskResult(
            disease_name="新疾病",
            control_status=ControlStatus.GOOD,
            risk_level=RiskLevel.LOW,
            risk_score=risk_score,
            control_quality_score=85.0,
            key_findings=["发现1", "发现2"],
            recommendations=["建议1", "建议2"]
        )
```

---

## ⚠️ 注意事项

1. **数据隐私**: 健康数据属于敏感信息，请确保数据传输和存储的安全性
2. **医疗免责**: 系统提供的评估结果仅供参考，不能替代专业医疗诊断
3. **配置更新**: 健康标准应根据最新医学指南定期更新
4. **性能优化**: 大规模部署时建议使用缓存和异步处理

---

## 📞 技术支持

- 查看 `README.md` 了解基本使用
- 查看 `ARCHITECTURE.md` 了解系统设计
- 查看 `docs/` 目录获取更多文档
- 运行 `examples/` 目录下的示例代码

---

**版本**: v1.0.0  
**更新日期**: 2024-01-15
