# 多模型健康评估系统

## 项目概述

多模型健康评估系统是一个综合性的健康风险评估平台，专为老年人慢病管理设计。系统通过整合多种先进算法，对用户的健康数据进行全方位分析，提供个性化的健康评估报告和干预建议。

## 系统架构

系统由六个核心子模块组成：

```
health_assessment_system/
├── modules/
│   ├── assessment_config.py      # 模块1: 评估配置与任务管理
│   ├── data_preparation.py       # 模块2: 数据准备与特征构建
│   ├── disease_assessment.py     # 模块3: 单病种风险评估
│   ├── lifestyle_assessment.py   # 模块4: 生活方式与行为风险评估
│   ├── comprehensive_assessment.py # 模块5: 综合健康风险评估与分层分级
│   └── report_generation.py      # 模块6: 评估结果管理与报告生成
├── core/
│   └── assessment_engine.py      # 核心引擎: 整合所有模块
├── config/
│   ├── health_standards.json     # 健康标准配置
│   └── assessment_config.json    # 评估系统配置
└── __init__.py
```

## 核心功能

### 1. 评估配置与任务管理
- ✅ 定期评估（按周/按月自动运行）
- ✅ 按需评估（家属或社区人员手动触发）
- ✅ 灵活的时间窗口配置（7天/30天/自定义）
- ✅ 数据完整性检查与评估质量标记

### 2. 数据准备与特征构建
- ✅ 多源健康数据整合
- ✅ 异常值检测与处理（IQR方法 + Z-score）
- ✅ 时间序列聚合（按天/按周）
- ✅ 丰富的特征工程（统计特征 + 趋势特征）

### 3. 单病种风险评估
- ✅ **高血压评估**：基于指南的分级 + 控制质量评分
- ✅ **糖代谢异常评估**：血糖波动分析 + 达标率计算
- ✅ **血脂异常评估**：多指标综合评估
- ✅ 模糊逻辑系统处理阈值边界

### 4. 生活方式与行为风险评估
- ✅ **睡眠质量评估**：时长 + 规律性 + 不足频率
- ✅ **运动评估**：步数 + 活跃天数 + 久坐检测
- ✅ **饮食习惯评估**：盐油糖摄入 + 营养均衡
- ✅ 异常行为模式检测（Isolation Forest）

### 5. 综合健康风险评估与分层分级
- ✅ **AHP层次分析法**：科学确定权重
- ✅ **TOPSIS多准则决策**：风险因素优先级排序
- ✅ 五级健康分层（优秀/良好/亚健康/需关注/高风险）
- ✅ TOP风险因素提取与可解释性分析

### 6. 评估结果管理与报告生成
- ✅ **老人版报告**：简短易懂，字体大，重点突出
- ✅ **家属版报告**：详细分维度评分 + 趋势说明
- ✅ **社区版报告**：简洁摘要，便于群体管理
- ✅ 可视化数据接口（JSON格式）
- ✅ 历史记录管理与查询

## 算法技术栈

| 模块 | 核心算法 | 技术特点 |
|------|---------|---------|
| **数据预处理** | IQR + Z-score | 鲁棒的异常值检测 |
| **单病种评估** | 模糊逻辑 + 规则引擎 | 处理阈值边界模糊性 |
| **生活方式评估** | Isolation Forest + HMM | 无监督异常检测 + 状态转换 |
| **趋势监测** | CUSUM + 变点检测 | 敏感捕捉持续偏移 |
| **风险融合** | AHP + TOPSIS | 多准则决策优化 |
| **可解释性** | 特征重要性分析 | 提供决策依据 |

## 快速开始

### 安装依赖

```bash
pip install numpy pandas scipy scikit-learn
```

可选依赖（用于高级功能）：
```bash
pip install scikit-fuzzy hmmlearn ruptures fbprophet
```

### 基本使用

```python
from health_assessment_system import HealthAssessmentEngine
from health_assessment_system.modules.assessment_config import AssessmentPeriod, TimeWindow
from health_assessment_system.modules.report_generation import ReportType, ReportFormat

# 1. 创建评估引擎
engine = HealthAssessmentEngine(storage_path="./assessment_data")

# 2. 运行定期评估
result = engine.run_scheduled_assessment(
    user_id="USER001",
    period=AssessmentPeriod.MONTHLY,
    time_window=TimeWindow.LAST_30_DAYS
)

# 3. 查看评估结果
print(f"综合评分: {result.overall_score:.1f}/100")
print(f"健康等级: {result.health_level.value}")
print(f"TOP风险因素: {[rf.name for rf in result.top_risk_factors]}")

# 4. 生成报告
elderly_report = engine.generate_report(
    assessment_id=result.assessment_id,
    user_id=result.user_id,
    report_type=ReportType.ELDERLY,
    report_format=ReportFormat.TEXT
)
print(elderly_report)

# 5. 获取可视化数据
viz_data = engine.get_visualization_data(
    assessment_id=result.assessment_id,
    user_id=result.user_id
)
```

### 按需评估

```python
# 家属触发的按需评估
result = engine.run_on_demand_assessment(
    user_id="USER001",
    triggered_by="family_member",
    custom_days=14  # 最近14天
)
```

### 查询历史记录

```python
# 获取用户的评估历史
history = engine.get_user_assessment_history(
    user_id="USER001",
    limit=10
)

for record in history:
    print(f"日期: {record.assessment_date}, 评分: {record.overall_score}")
```

## 评估流程

```
┌─────────────────────────────────────────────────────────────┐
│  步骤1: 创建评估配置                                          │
│  - 选择评估类型（定期/按需）                                   │
│  - 配置时间窗口                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤2: 数据准备与完整性检查                                   │
│  - 加载健康档案数据                                           │
│  - 检查数据完整性                                             │
│  - 标记评估质量                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤3: 特征构建                                              │
│  - 异常值处理                                                 │
│  - 时间序列聚合                                               │
│  - 统计特征计算                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤4: 单病种风险评估                                         │
│  - 高血压评估                                                 │
│  - 糖代谢异常评估                                             │
│  - 血脂异常评估                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤5: 生活方式与行为风险评估                                 │
│  - 睡眠质量评估                                               │
│  - 运动评估                                                   │
│  - 饮食习惯评估                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤6: 趋势变化与异常波动监测                                 │
│  - 计算个人基线                                               │
│  - 趋势分析                                                   │
│  - 异常波动检测                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤7: 综合健康风险评估与分层分级                             │
│  - 多维度风险融合（AHP）                                      │
│  - 风险因素排序（TOPSIS）                                     │
│  - 健康分层分级                                               │
│  - 生成优先建议                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤8: 评估结果管理与报告生成                                 │
│  - 保存评估记录                                               │
│  - 生成分角色报告                                             │
│  - 提供可视化数据接口                                         │
└─────────────────────────────────────────────────────────────┘
```

## 评估报告示例

### 老人版报告（简版）
```
╔══════════════════════════════════════╗
║          健康评估报告（简版）          ║
╚══════════════════════════════════════╝

评估日期：2023-11-25

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【健康状况】
您的健康评分：65分
健康等级：亚健康

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【需要注意的问题】

1. 血压偏高
2. 活动太少
3. 睡眠不好

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【健康建议】

1. 建议加强血压监测，规律服药，减少盐分摄入
2. 建议增加日常活动量，每天至少6000步
3. 建议改善睡眠习惯，保持规律作息

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 温馨提示：请按照建议调整生活习惯，定期复查。
```

### 可视化数据接口
```json
{
  "overview": {
    "overall_score": 65.5,
    "health_level": "suboptimal",
    "assessment_date": "2023-11-25T10:30:00"
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
  ]
}
```

## 配置说明

### 健康标准配置 (`config/health_standards.json`)
定义各项健康指标的正常范围和分级标准，基于中国健康指南。

### 评估系统配置 (`config/assessment_config.json`)
配置评估权重、阈值、数据要求等系统参数。

## 扩展开发

### 添加新的单病种评估器

```python
from modules.disease_assessment import DiseaseRiskResult

class NewDiseaseAssessor:
    def __init__(self):
        # 初始化阈值和参数
        pass
    
    def assess(self, features: Dict, baseline: Optional[Dict]) -> DiseaseRiskResult:
        # 实现评估逻辑
        result = DiseaseRiskResult(
            disease_name="新疾病",
            control_status=ControlStatus.GOOD,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            control_quality_score=0.0
        )
        return result
```

### 自定义权重配置

修改 `config/assessment_config.json` 中的权重参数：

```json
{
  "assessment_weights": {
    "disease_risk": 0.50,  // 增加疾病权重
    "lifestyle_risk": 0.30,
    "trend_risk": 0.20
  }
}
```

## 性能优化建议

1. **数据缓存**：对频繁访问的基线数据进行缓存
2. **批量评估**：支持多用户并行评估
3. **增量更新**：仅对新增数据进行计算
4. **模型预加载**：提前加载机器学习模型

## 注意事项

⚠️ **重要提示**：
- 本系统提供的评估结果仅供参考，不能替代专业医疗诊断
- 高风险用户应及时就医，接受专业评估
- 定期更新健康标准配置以符合最新医学指南
- 确保数据隐私和安全，遵守相关法律法规

## 技术支持

- 项目文档：查看各模块的详细文档字符串
- 示例代码：参考 `core/assessment_engine.py` 中的使用示例
- 配置文件：查看 `config/` 目录下的配置说明

## 许可证

本项目仅供学习和研究使用。

## 更新日志

### v1.0.0 (2023-11-25)
- ✅ 完成六大核心模块开发
- ✅ 实现多算法融合评估
- ✅ 支持分角色报告生成
- ✅ 提供可视化数据接口
- ✅ 完整的评估记录管理

---

**开发团队** | Health Assessment Team | 2023
