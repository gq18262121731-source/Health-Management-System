# 系统架构设计文档

## 1. 总体架构

### 1.1 系统分层

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                │
│  - Web API接口                                               │
│  - 移动端接口                                                 │
│  - 管理后台                                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   核心引擎层 (Core Engine Layer)             │
│  HealthAssessmentEngine - 评估流程协调                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   业务逻辑层 (Business Logic Layer)          │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ 评估配置管理  │ 数据准备处理  │ 风险评估引擎  │            │
│  └──────────────┴──────────────┴──────────────┘            │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ 生活方式评估  │ 综合风险融合  │ 报告生成管理  │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   算法层 (Algorithm Layer)                   │
│  • 模糊逻辑 • AHP • TOPSIS • Isolation Forest               │
│  • CUSUM • 变点检测 • 时间序列分析                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据层 (Data Layer)                        │
│  • 健康档案数据 • 评估记录 • 配置数据                        │
└─────────────────────────────────────────────────────────────┘
```

## 2. 六大子模块详解

### 2.1 模块1：评估配置与任务管理

**职责**：
- 管理评估任务的创建、调度和执行
- 配置评估参数（时间窗口、评估类型等）
- 检查数据完整性

**核心类**：
- `AssessmentTaskManager`：任务管理器
- `AssessmentConfig`：评估配置
- `DataCompletenessReport`：数据完整性报告

**算法**：无复杂算法，主要是任务调度逻辑

**输入**：用户ID、评估类型、时间窗口
**输出**：评估配置对象、数据完整性报告

---

### 2.2 模块2：数据准备与特征构建

**职责**：
- 从健康档案中提取数据
- 数据预处理（异常值检测、聚合）
- 构建评估所需的特征

**核心类**：
- `DataPreprocessor`：数据预处理器
- `FeatureEngineer`：特征工程器
- `FeatureSet`：特征集合

**算法**：
- **IQR方法**：异常值检测
  ```python
  Q1 = percentile(data, 25)
  Q3 = percentile(data, 75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  ```

- **Z-score方法**：异常值检测
  ```python
  z_score = (x - mean) / std
  outlier if |z_score| > 3
  ```

**输入**：原始健康数据、基线数据
**输出**：特征集合（FeatureSet）

---

### 2.3 模块3：单病种风险评估

**职责**：
- 评估高血压、糖尿病、血脂异常等单病种风险
- 计算控制质量评分
- 生成风险等级和关键发现

**核心类**：
- `HypertensionAssessor`：高血压评估器
- `DiabetesAssessor`：糖尿病评估器
- `DyslipidemiAssessor`：血脂异常评估器

**算法**：

1. **模糊逻辑系统**（处理阈值边界）
   ```
   IF sbp is "high" AND compliance_rate is "low" 
   THEN risk is "high"
   ```

2. **控制质量评分**
   ```python
   score = (
       compliance_rate * 40 +  # 达标率
       stability_score * 30 +   # 稳定性
       bp_level_score * 30      # 血压水平
   )
   ```

3. **风险评分计算**
   ```python
   risk = (
       bp_level_risk * 0.4 +
       compliance_risk * 0.25 +
       volatility_risk * 0.2 +
       trend_risk * 0.15
   )
   ```

**输入**：特征字典、基线数据
**输出**：DiseaseRiskResult（包含风险等级、评分、关键发现）

---

### 2.4 模块4：生活方式与行为风险评估

**职责**：
- 评估睡眠、运动、饮食等生活方式风险
- 检测异常行为模式
- 识别连续不良行为

**核心类**：
- `SleepQualityAssessor`：睡眠评估器
- `ExerciseAssessor`：运动评估器
- `DietAssessor`：饮食评估器
- `AnomalyDetector`：异常检测器

**算法**：

1. **Isolation Forest**（异常行为检测）
   ```python
   # 无监督异常检测
   model = IsolationForest(contamination=0.1)
   predictions = model.fit_predict(lifestyle_features)
   anomalies = predictions == -1
   ```

2. **睡眠规律性评分**
   ```python
   regularity_score = max(0, 100 - std_sleep_duration * 20)
   ```

3. **运动评分**
   ```python
   if steps >= 10000: score = 40
   elif steps >= 6000: score = 25 + 15 * (steps - 6000) / 4000
   else: score = 10 * steps / 6000
   ```

**输入**：特征字典、饮食数据、时间序列数据
**输出**：LifestyleRiskResult（包含各维度评分和风险等级）

---

### 2.5 模块5：综合健康风险评估与分层分级

**职责**：
- 融合多维度风险
- 对风险因素进行优先级排序
- 生成综合健康评分和等级
- 提供可解释性分析

**核心类**：
- `RiskFusionEngine`：风险融合引擎
- `AHPWeightCalculator`：AHP权重计算器
- `TOPSISRanker`：TOPSIS排序器

**算法**：

1. **AHP层次分析法**（权重确定）
   ```
   构建成对比较矩阵 A
   计算最大特征值和特征向量
   特征向量归一化得到权重
   
   一致性检查：CR = CI / RI < 0.1
   ```

2. **TOPSIS多准则决策**（风险排序）
   ```python
   # 1. 构建决策矩阵
   D = [severity, urgency, frequency, trend]
   
   # 2. 归一化
   N = D / sqrt(sum(D^2))
   
   # 3. 加权
   V = N * weights
   
   # 4. 计算理想解距离
   d_best = distance(V, ideal_best)
   d_worst = distance(V, ideal_worst)
   
   # 5. 相对接近度
   closeness = d_worst / (d_best + d_worst)
   ```

3. **综合评分融合**
   ```python
   overall_score = (
       disease_health_score * 0.45 +
       lifestyle_health_score * 0.30 +
       trend_health_score * 0.25
   )
   ```

**输入**：单病种结果、生活方式结果、趋势结果
**输出**：ComprehensiveAssessmentResult（综合评估结果）

---

### 2.6 模块6：评估结果管理与报告生成

**职责**：
- 保存和管理评估记录
- 生成不同角色的报告
- 提供可视化数据接口
- 历史记录查询

**核心类**：
- `AssessmentRecordManager`：记录管理器
- `ReportGenerator`：报告生成器
- `AssessmentRecord`：评估记录

**功能**：

1. **分角色报告**
   - 老人版：简短易懂，3个关键问题，3条建议
   - 家属版：详细完整，包含趋势和分维度评分
   - 社区版：简洁摘要，便于群体管理

2. **可视化数据接口**
   ```json
   {
     "overview": {...},
     "dimension_scores": {...},
     "risk_factors": [...],
     "trend_indicators": [...]
   }
   ```

**输入**：综合评估结果
**输出**：报告文本、可视化数据、评估记录

---

## 3. 数据流图

```
用户健康数据
    ↓
[数据准备与特征构建]
    ↓
特征集合
    ├─→ [单病种风险评估] → 疾病风险结果
    ├─→ [生活方式评估] → 生活方式结果
    └─→ [趋势分析] → 趋势结果
         ↓
    [综合风险融合]
    (AHP + TOPSIS)
         ↓
    综合评估结果
         ↓
    [报告生成]
    ├─→ 老人版报告
    ├─→ 家属版报告
    ├─→ 社区版报告
    └─→ 可视化数据
```

## 4. 算法选择理由

| 算法 | 应用场景 | 选择理由 |
|------|---------|---------|
| **模糊逻辑** | 单病种评估 | 处理阈值边界的模糊性，符合医学实际 |
| **IQR/Z-score** | 异常值检测 | 简单有效，计算快速 |
| **Isolation Forest** | 异常行为检测 | 无监督学习，适合检测罕见异常 |
| **AHP** | 权重确定 | 结构化决策，融入专家知识 |
| **TOPSIS** | 风险排序 | 多准则决策，客观排序 |
| **CUSUM** | 趋势监测 | 敏感检测微小但持续的变化 |

## 5. 扩展性设计

### 5.1 新增疾病评估器
```python
class NewDiseaseAssessor:
    def assess(self, features, baseline):
        # 实现评估逻辑
        return DiseaseRiskResult(...)
```

### 5.2 自定义权重
修改 `config/assessment_config.json`

### 5.3 集成机器学习模型
```python
class MLBasedAssessor:
    def __init__(self):
        self.model = load_trained_model()
    
    def assess(self, features):
        prediction = self.model.predict(features)
        return convert_to_result(prediction)
```

## 6. 性能优化策略

1. **数据缓存**：缓存基线数据和历史记录
2. **并行计算**：多用户评估并行处理
3. **增量更新**：只处理新增数据
4. **索引优化**：评估记录建立索引
5. **批量处理**：批量读写减少IO

## 7. 安全性考虑

1. **数据加密**：敏感健康数据加密存储
2. **访问控制**：基于角色的权限管理
3. **审计日志**：记录所有评估操作
4. **数据脱敏**：报告中隐藏敏感信息
5. **合规性**：符合医疗数据保护法规

## 8. 未来改进方向

1. **深度学习集成**：使用LSTM/Transformer进行时序预测
2. **知识图谱**：构建疾病-症状-风险知识图谱
3. **强化学习**：优化干预策略推荐
4. **联邦学习**：保护隐私的多中心模型训练
5. **实时监测**：接入可穿戴设备实时数据

---

**文档版本**: v1.0.0  
**最后更新**: 2023-11-25  
**维护团队**: Health Assessment Team
