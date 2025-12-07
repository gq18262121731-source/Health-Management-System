# 数据层 - 核心文件汇总

本文件夹包含数据处理的所有核心代码和文档。

## 文件说明

| 文件 | 功能 | 核心类/函数 |
|------|------|-------------|
| **data_pipeline.py** | 数据采集 + 数据清洗 | `DataCollector`, `DataCleaner`, `DataPipeline` |
| **health_data_service.py** | 数据服务层（特征工程+评估） | `HealthDataService` |
| **data_preparation.py** | 特征工程模块 | `FeatureEngineer`, `DataPreprocessor` |
| **database_manager.py** | 数据库连接管理 | `DatabaseManager` |
| **DATA_STRUCTURES.md** | 数据结构定义文档 | - |
| **数据动线架构.md** | 完整数据流架构图 | - |

## 数据处理流程

```
数据采集 → 数据清洗 → 特征工程 → 健康评估 → API输出
   ↓          ↓          ↓          ↓          ↓
DataCollector → DataCleaner → FeatureEngineer → Assessment → API
```

## 快速使用

```python
# 方式1: 使用数据管道
from data_pipeline import get_pipeline

pipeline = get_pipeline()
pipeline.collect(user_id, data_type, values)
cleaned, report = pipeline.clean(user_id, data_type)

# 方式2: 使用数据服务
from health_data_service import get_health_data_service

service = get_health_data_service()
service.add_raw_data(record)
features = service.build_features(user_id, days=7)
```

## 核心算法

- **异常值检测**: IQR法、Z-score法
- **特征工程**: 均值、标准差、趋势斜率、变异系数、达标率
- **健康评估**: AHP层次分析法 + TOPSIS多准则决策
