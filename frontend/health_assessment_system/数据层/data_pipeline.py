"""
数据处理流水线 (Data Pipeline)
==============================

完整的数据动线：数据采集 → 数据清洗 → 数据处理 → 数据可视化

本模块定义了整个数据处理流程的核心逻辑。

数据动线图：
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据采集层                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 传感器   │  │ 手动输入  │  │ 批量导入  │  │ API调用   │  │ 数据库   │       │
│  │ (IoT)    │  │ (表单)   │  │ (CSV/JSON)│  │ (第三方)  │  │ (MySQL)  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       └─────────────┴─────────────┴─────────────┴─────────────┘             │
│                                   ↓                                          │
│                          RawHealthRecord                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据清洗层                                      │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  1. 去重 (Deduplication)                                          │       │
│  │     - 时间戳去重                                                   │       │
│  │     - 相似记录合并                                                 │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  2. 异常值处理 (Outlier Detection)                                │       │
│  │     - IQR方法 (四分位距)                                           │       │
│  │     - Z-score方法 (标准差)                                         │       │
│  │     - 业务规则过滤                                                 │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  3. 缺失值处理 (Missing Value)                                    │       │
│  │     - 前向填充 / 后向填充                                          │       │
│  │     - 线性插值                                                    │       │
│  │     - 均值/中位数填充                                              │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  4. 格式化 (Formatting)                                           │       │
│  │     - 时间戳标准化                                                 │       │
│  │     - 数值单位统一                                                 │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  5. 标准化 (Normalization)                                        │       │
│  │     - Min-Max归一化                                               │       │
│  │     - Z-score标准化                                               │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                   ↓                                          │
│                          CleanedHealthData                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据处理层                                      │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  1. 特征工程 (Feature Engineering)                                │       │
│  │     - 统计特征: 均值、标准差、最大最小值                             │       │
│  │     - 趋势特征: 线性回归斜率、变化率                                 │       │
│  │     - 变异特征: 变异系数、波动频率                                   │       │
│  │     - 达标率: 根据医学标准计算                                       │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  2. 时序聚合 (Time Aggregation)                                   │       │
│  │     - 按小时/天/周/月聚合                                          │       │
│  │     - 滑动窗口统计                                                 │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  3. 健康评估 (Health Assessment)                                  │       │
│  │     - 单病种评估: 高血压、糖尿病、血脂异常                           │       │
│  │     - 生活方式评估: 睡眠、运动、饮食                                 │       │
│  │     - 综合评估: AHP权重 + TOPSIS排序                                │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                   ↓                                          │
│                       ProcessedHealthFeatures                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据可视化层                                    │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  前端展示 (React)                                                  │       │
│  │  ├── 心率折线图      ← /api/health/heart-rate                     │       │
│  │  ├── 血压趋势图      ← /api/health/blood-pressure                 │       │
│  │  ├── 睡眠柱状图      ← /api/health/sleep                          │       │
│  │  ├── 健康雷达图      ← /api/health/radar                          │       │
│  │  ├── 今日健康卡片    ← /api/health/today                          │       │
│  │  └── 健康评估报告    ← /api/health/assessment                     │       │
│  └──────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘

作者: 智能诊断系统
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import json


# =============================================================================
# 枚举定义
# =============================================================================

class DataSource(Enum):
    """数据来源"""
    SENSOR = "sensor"           # 传感器（IoT设备）
    MANUAL = "manual"           # 手动输入
    BATCH_IMPORT = "batch"      # 批量导入（CSV/JSON）
    API = "api"                 # API调用（第三方）
    DATABASE = "database"       # 数据库同步


class CleaningMethod(Enum):
    """清洗方法"""
    IQR = "iqr"                 # 四分位距法
    ZSCORE = "zscore"           # Z-score法
    BUSINESS_RULE = "rule"      # 业务规则


class NormalizationMethod(Enum):
    """标准化方法"""
    MIN_MAX = "minmax"          # 最小-最大归一化
    ZSCORE = "zscore"           # Z-score标准化
    NONE = "none"               # 不标准化


class AggregationPeriod(Enum):
    """聚合周期"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# =============================================================================
# 数据模型
# =============================================================================

@dataclass
class RawDataRecord:
    """原始数据记录"""
    record_id: str                  # 记录唯一ID
    user_id: str                    # 用户ID
    data_type: str                  # 数据类型
    timestamp: datetime             # 采集时间
    values: Dict[str, Any]          # 数据值
    source: DataSource              # 数据来源
    device_id: Optional[str] = None # 设备ID（传感器数据）
    metadata: Dict = field(default_factory=dict)  # 元数据
    
    def __post_init__(self):
        if not self.record_id:
            # 自动生成唯一ID
            content = f"{self.user_id}_{self.data_type}_{self.timestamp}_{json.dumps(self.values, sort_keys=True)}"
            self.record_id = hashlib.md5(content.encode()).hexdigest()[:16]


@dataclass
class CleanedDataRecord:
    """清洗后的数据记录"""
    record_id: str
    user_id: str
    data_type: str
    timestamp: datetime
    value: float                    # 标准化后的单一数值
    original_values: Dict[str, Any] # 原始值
    quality_flags: List[str] = field(default_factory=list)  # 质量标记
    is_interpolated: bool = False   # 是否为插值
    cleaning_applied: List[str] = field(default_factory=list)  # 应用的清洗方法


@dataclass
class DataQualityReport:
    """数据质量报告"""
    user_id: str
    data_type: str
    period: Tuple[datetime, datetime]
    
    total_records: int = 0
    valid_records: int = 0
    duplicates_removed: int = 0
    outliers_detected: int = 0
    missing_filled: int = 0
    
    quality_score: float = 0.0      # 0-100
    completeness: float = 0.0       # 完整性
    accuracy: float = 0.0           # 准确性
    consistency: float = 0.0        # 一致性
    
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# 数据采集器
# =============================================================================

class DataCollector:
    """
    数据采集器 - 统一的数据采集入口
    
    支持多种数据源：
    - 传感器数据（IoT设备）
    - 手动输入（表单提交）
    - 批量导入（CSV/JSON文件）
    - API调用（第三方健康平台）
    - 数据库同步
    """
    
    # 数据类型与字段映射
    DATA_SCHEMAS = {
        'blood_pressure': {
            'required': ['systolic', 'diastolic'],
            'optional': ['pulse', 'position', 'arm'],
            'unit': 'mmHg',
            'valid_range': {'systolic': (60, 250), 'diastolic': (40, 150)}
        },
        'glucose': {
            'required': ['value'],
            'optional': ['test_type', 'meal_time'],  # fasting, postprandial
            'unit': 'mmol/L',
            'valid_range': {'value': (1.0, 35.0)}
        },
        'heart_rate': {
            'required': ['value'],
            'optional': ['activity_level', 'resting'],
            'unit': 'bpm',
            'valid_range': {'value': (30, 220)}
        },
        'weight': {
            'required': ['value'],
            'optional': ['body_fat', 'muscle_mass', 'water_ratio'],
            'unit': 'kg',
            'valid_range': {'value': (20, 300)}
        },
        'sleep': {
            'required': ['duration'],
            'optional': ['deep_sleep', 'light_sleep', 'rem_sleep', 'awake_times'],
            'unit': 'hours',
            'valid_range': {'duration': (0, 24)}
        },
        'steps': {
            'required': ['value'],
            'optional': ['distance', 'calories', 'floors'],
            'unit': 'steps',
            'valid_range': {'value': (0, 100000)}
        },
        'temperature': {
            'required': ['value'],
            'optional': ['measurement_site'],  # oral, armpit, forehead
            'unit': '°C',
            'valid_range': {'value': (34.0, 42.0)}
        },
        'spo2': {
            'required': ['value'],
            'optional': ['perfusion_index'],
            'unit': '%',
            'valid_range': {'value': (70, 100)}
        }
    }
    
    def __init__(self):
        self._buffer: List[RawDataRecord] = []  # 数据缓冲区
        self._validators = {}
        self._initialize_validators()
    
    def _initialize_validators(self):
        """初始化数据验证器"""
        for data_type, schema in self.DATA_SCHEMAS.items():
            self._validators[data_type] = schema
    
    def collect_single(
        self,
        user_id: str,
        data_type: str,
        values: Dict[str, Any],
        source: DataSource = DataSource.MANUAL,
        timestamp: Optional[datetime] = None,
        device_id: Optional[str] = None
    ) -> Tuple[bool, Optional[RawDataRecord], Optional[str]]:
        """
        采集单条数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            values: 数据值字典
            source: 数据来源
            timestamp: 采集时间（默认当前）
            device_id: 设备ID
        
        Returns:
            (success, record, error_message)
        """
        # 验证数据类型
        if data_type not in self.DATA_SCHEMAS:
            return False, None, f"不支持的数据类型: {data_type}"
        
        # 验证必填字段
        schema = self.DATA_SCHEMAS[data_type]
        for field in schema['required']:
            if field not in values or values[field] is None:
                return False, None, f"缺少必填字段: {field}"
        
        # 验证数值范围
        valid_range = schema.get('valid_range', {})
        for field, (min_val, max_val) in valid_range.items():
            if field in values:
                val = values[field]
                if not (min_val <= val <= max_val):
                    return False, None, f"{field} 超出有效范围 [{min_val}, {max_val}]"
        
        # 创建记录
        record = RawDataRecord(
            record_id="",  # 自动生成
            user_id=user_id,
            data_type=data_type,
            timestamp=timestamp or datetime.now(),
            values=values,
            source=source,
            device_id=device_id,
            metadata={'collected_at': datetime.now().isoformat()}
        )
        
        self._buffer.append(record)
        return True, record, None
    
    def collect_batch(
        self,
        user_id: str,
        records: List[Dict[str, Any]],
        source: DataSource = DataSource.BATCH_IMPORT
    ) -> Tuple[int, int, List[str]]:
        """
        批量采集数据
        
        Args:
            user_id: 用户ID
            records: 记录列表，每条包含 data_type, values, timestamp
        
        Returns:
            (success_count, fail_count, errors)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        for idx, record_data in enumerate(records):
            data_type = record_data.get('data_type')
            values = record_data.get('values', {})
            timestamp = record_data.get('timestamp')
            
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = None
            
            success, _, error = self.collect_single(
                user_id=user_id,
                data_type=data_type,
                values=values,
                source=source,
                timestamp=timestamp
            )
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"记录{idx}: {error}")
        
        return success_count, fail_count, errors
    
    def import_from_csv(
        self,
        user_id: str,
        file_path: str,
        data_type: str,
        column_mapping: Dict[str, str]
    ) -> Tuple[int, int, List[str]]:
        """
        从CSV文件导入数据
        
        Args:
            user_id: 用户ID
            file_path: CSV文件路径
            data_type: 数据类型
            column_mapping: 列名映射 {csv列名: 标准字段名}
        """
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return 0, 0, [f"读取CSV失败: {str(e)}"]
        
        records = []
        for _, row in df.iterrows():
            values = {}
            timestamp = None
            
            for csv_col, std_field in column_mapping.items():
                if csv_col in row:
                    if std_field == 'timestamp':
                        timestamp = row[csv_col]
                    else:
                        values[std_field] = row[csv_col]
            
            records.append({
                'data_type': data_type,
                'values': values,
                'timestamp': timestamp
            })
        
        return self.collect_batch(user_id, records, DataSource.BATCH_IMPORT)
    
    def flush_buffer(self) -> List[RawDataRecord]:
        """获取并清空缓冲区"""
        records = self._buffer.copy()
        self._buffer.clear()
        return records
    
    def get_buffer_size(self) -> int:
        """获取缓冲区大小"""
        return len(self._buffer)


# =============================================================================
# 数据清洗器
# =============================================================================

class DataCleaner:
    """
    数据清洗器 - 完整的数据清洗流程
    
    清洗步骤：
    1. 去重
    2. 异常值检测与处理
    3. 缺失值填充
    4. 格式标准化
    5. 数值归一化（可选）
    """
    
    def __init__(
        self,
        outlier_method: CleaningMethod = CleaningMethod.IQR,
        normalization: NormalizationMethod = NormalizationMethod.NONE,
        iqr_multiplier: float = 1.5,
        zscore_threshold: float = 3.0
    ):
        self.outlier_method = outlier_method
        self.normalization = normalization
        self.iqr_multiplier = iqr_multiplier
        self.zscore_threshold = zscore_threshold
        
        # 业务规则（医学合理范围）
        self.business_rules = {
            'blood_pressure': {'systolic': (70, 200), 'diastolic': (40, 130)},
            'glucose': {'value': (2.0, 30.0)},
            'heart_rate': {'value': (35, 200)},
            'weight': {'value': (25, 250)},
            'sleep': {'duration': (0.5, 16)},
            'steps': {'value': (0, 80000)},
            'temperature': {'value': (35.0, 41.0)},
            'spo2': {'value': (75, 100)}
        }
    
    def clean(
        self,
        records: List[RawDataRecord],
        fill_missing: bool = True,
        remove_duplicates: bool = True
    ) -> Tuple[List[CleanedDataRecord], DataQualityReport]:
        """
        执行完整的数据清洗流程
        
        Args:
            records: 原始数据记录列表
            fill_missing: 是否填充缺失值
            remove_duplicates: 是否去重
        
        Returns:
            (cleaned_records, quality_report)
        """
        if not records:
            return [], self._create_empty_report()
        
        user_id = records[0].user_id
        data_type = records[0].data_type
        
        # 初始化报告
        report = DataQualityReport(
            user_id=user_id,
            data_type=data_type,
            period=(
                min(r.timestamp for r in records),
                max(r.timestamp for r in records)
            ),
            total_records=len(records)
        )
        
        # 步骤1: 去重
        if remove_duplicates:
            records, dups = self._remove_duplicates(records)
            report.duplicates_removed = dups
        
        # 步骤2: 提取主要数值
        values_with_records = self._extract_values(records, data_type)
        
        # 步骤3: 异常值检测
        clean_mask, outliers = self._detect_outliers(
            [v for v, _ in values_with_records],
            data_type
        )
        report.outliers_detected = outliers
        
        # 步骤4: 过滤异常值
        filtered = [(v, r) for (v, r), m in zip(values_with_records, clean_mask) if m]
        
        # 步骤5: 缺失值填充（如果需要）
        if fill_missing:
            filled_count = 0  # TODO: 实现时间序列插值
            report.missing_filled = filled_count
        
        # 步骤6: 标准化
        values = [v for v, _ in filtered]
        if self.normalization != NormalizationMethod.NONE and values:
            values = self._normalize(values, self.normalization)
        
        # 创建清洗后的记录
        cleaned_records = []
        for i, (original_val, raw_record) in enumerate(filtered):
            cleaned = CleanedDataRecord(
                record_id=raw_record.record_id,
                user_id=raw_record.user_id,
                data_type=raw_record.data_type,
                timestamp=raw_record.timestamp,
                value=values[i] if i < len(values) else original_val,
                original_values=raw_record.values,
                cleaning_applied=[self.outlier_method.value]
            )
            cleaned_records.append(cleaned)
        
        # 计算质量评分
        report.valid_records = len(cleaned_records)
        report = self._calculate_quality_metrics(report)
        
        return cleaned_records, report
    
    def _remove_duplicates(
        self, 
        records: List[RawDataRecord]
    ) -> Tuple[List[RawDataRecord], int]:
        """去除重复记录"""
        seen = set()
        unique = []
        
        for record in records:
            # 基于用户+时间+数据类型判断重复
            key = f"{record.user_id}_{record.data_type}_{record.timestamp.isoformat()}"
            if key not in seen:
                seen.add(key)
                unique.append(record)
        
        return unique, len(records) - len(unique)
    
    def _extract_values(
        self, 
        records: List[RawDataRecord],
        data_type: str
    ) -> List[Tuple[float, RawDataRecord]]:
        """提取主要数值"""
        primary_field_map = {
            'blood_pressure': 'systolic',
            'glucose': 'value',
            'heart_rate': 'value',
            'weight': 'value',
            'sleep': 'duration',
            'steps': 'value',
            'temperature': 'value',
            'spo2': 'value'
        }
        
        primary_field = primary_field_map.get(data_type, 'value')
        result = []
        
        for record in records:
            val = record.values.get(primary_field)
            if val is not None:
                try:
                    result.append((float(val), record))
                except (ValueError, TypeError):
                    pass
        
        return result
    
    def _detect_outliers(
        self,
        values: List[float],
        data_type: str
    ) -> Tuple[List[bool], int]:
        """检测异常值"""
        if not values:
            return [], 0
        
        arr = np.array(values)
        
        # 方法1: 业务规则过滤
        rule_mask = np.ones(len(values), dtype=bool)
        if data_type in self.business_rules:
            rules = self.business_rules[data_type]
            for field, (min_val, max_val) in rules.items():
                rule_mask &= (arr >= min_val) & (arr <= max_val)
        
        # 方法2: 统计方法
        if self.outlier_method == CleaningMethod.IQR:
            stat_mask = self._iqr_filter(arr)
        elif self.outlier_method == CleaningMethod.ZSCORE:
            stat_mask = self._zscore_filter(arr)
        else:
            stat_mask = np.ones(len(values), dtype=bool)
        
        # 综合判断
        final_mask = rule_mask & stat_mask
        outliers = len(values) - np.sum(final_mask)
        
        return final_mask.tolist(), outliers
    
    def _iqr_filter(self, arr: np.ndarray) -> np.ndarray:
        """IQR异常值过滤"""
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        lower = q1 - self.iqr_multiplier * iqr
        upper = q3 + self.iqr_multiplier * iqr
        return (arr >= lower) & (arr <= upper)
    
    def _zscore_filter(self, arr: np.ndarray) -> np.ndarray:
        """Z-score异常值过滤"""
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return np.ones(len(arr), dtype=bool)
        z_scores = np.abs((arr - mean) / std)
        return z_scores <= self.zscore_threshold
    
    def _normalize(
        self, 
        values: List[float],
        method: NormalizationMethod
    ) -> List[float]:
        """数值标准化"""
        arr = np.array(values)
        
        if method == NormalizationMethod.MIN_MAX:
            min_val, max_val = arr.min(), arr.max()
            if max_val == min_val:
                return [0.5] * len(values)
            return ((arr - min_val) / (max_val - min_val)).tolist()
        
        elif method == NormalizationMethod.ZSCORE:
            mean, std = arr.mean(), arr.std()
            if std == 0:
                return [0.0] * len(values)
            return ((arr - mean) / std).tolist()
        
        return values
    
    def _calculate_quality_metrics(self, report: DataQualityReport) -> DataQualityReport:
        """计算数据质量指标"""
        total = report.total_records
        if total == 0:
            return report
        
        # 完整性: 有效记录比例
        report.completeness = report.valid_records / total * 100
        
        # 准确性: 非异常值比例
        report.accuracy = (total - report.outliers_detected) / total * 100
        
        # 一致性: 非重复比例
        report.consistency = (total - report.duplicates_removed) / total * 100
        
        # 综合评分
        report.quality_score = (
            report.completeness * 0.4 +
            report.accuracy * 0.4 +
            report.consistency * 0.2
        )
        
        # 问题和建议
        if report.outliers_detected > total * 0.1:
            report.issues.append(f"异常值比例过高 ({report.outliers_detected}/{total})")
            report.recommendations.append("检查数据采集设备是否正常")
        
        if report.duplicates_removed > 0:
            report.issues.append(f"存在 {report.duplicates_removed} 条重复记录")
            report.recommendations.append("检查数据同步逻辑，避免重复上传")
        
        return report
    
    def _create_empty_report(self) -> DataQualityReport:
        """创建空报告"""
        return DataQualityReport(
            user_id="",
            data_type="",
            period=(datetime.now(), datetime.now())
        )


# =============================================================================
# 数据处理管道
# =============================================================================

class DataPipeline:
    """
    数据处理管道 - 串联整个数据处理流程
    
    使用示例:
    ```python
    pipeline = DataPipeline()
    
    # 1. 采集数据
    pipeline.collect(user_id, data_type, values)
    
    # 2. 执行清洗
    cleaned_data, quality_report = pipeline.clean(user_id, data_type)
    
    # 3. 获取处理结果
    result = pipeline.process(user_id, days=7)
    ```
    """
    
    def __init__(self):
        self.collector = DataCollector()
        self.cleaner = DataCleaner()
        
        # 数据存储
        self._raw_store: Dict[str, List[RawDataRecord]] = {}
        self._cleaned_store: Dict[str, List[CleanedDataRecord]] = {}
        self._quality_reports: Dict[str, DataQualityReport] = {}
    
    def collect(
        self,
        user_id: str,
        data_type: str,
        values: Dict[str, Any],
        source: DataSource = DataSource.MANUAL,
        timestamp: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """采集数据"""
        success, record, error = self.collector.collect_single(
            user_id, data_type, values, source, timestamp
        )
        
        if success and record:
            key = f"{user_id}_{data_type}"
            if key not in self._raw_store:
                self._raw_store[key] = []
            self._raw_store[key].append(record)
        
        return success, error
    
    def collect_batch(
        self,
        user_id: str,
        records: List[Dict]
    ) -> Tuple[int, int, List[str]]:
        """批量采集"""
        success, fail, errors = self.collector.collect_batch(user_id, records)
        
        # 存储采集的数据
        for record in self.collector.flush_buffer():
            key = f"{record.user_id}_{record.data_type}"
            if key not in self._raw_store:
                self._raw_store[key] = []
            self._raw_store[key].append(record)
        
        return success, fail, errors
    
    def clean(
        self,
        user_id: str,
        data_type: str,
        days: int = 30
    ) -> Tuple[List[CleanedDataRecord], DataQualityReport]:
        """清洗数据"""
        key = f"{user_id}_{data_type}"
        
        # 获取原始数据
        raw_records = self._raw_store.get(key, [])
        
        # 按时间过滤
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [r for r in raw_records if r.timestamp >= cutoff]
        
        # 执行清洗
        cleaned, report = self.cleaner.clean(filtered)
        
        # 存储结果
        self._cleaned_store[key] = cleaned
        self._quality_reports[key] = report
        
        return cleaned, report
    
    def get_cleaned_data(
        self,
        user_id: str,
        data_type: str
    ) -> List[CleanedDataRecord]:
        """获取清洗后的数据"""
        key = f"{user_id}_{data_type}"
        return self._cleaned_store.get(key, [])
    
    def get_quality_report(
        self,
        user_id: str,
        data_type: str
    ) -> Optional[DataQualityReport]:
        """获取数据质量报告"""
        key = f"{user_id}_{data_type}"
        return self._quality_reports.get(key)
    
    def get_pipeline_summary(self, user_id: str) -> Dict:
        """获取管道处理摘要"""
        summary = {
            'user_id': user_id,
            'data_types': {},
            'total_raw_records': 0,
            'total_cleaned_records': 0,
            'overall_quality_score': 0
        }
        
        quality_scores = []
        
        for key in self._raw_store:
            if key.startswith(f"{user_id}_"):
                data_type = key.split('_', 1)[1]
                raw_count = len(self._raw_store.get(key, []))
                cleaned_count = len(self._cleaned_store.get(key, []))
                report = self._quality_reports.get(key)
                
                summary['data_types'][data_type] = {
                    'raw_records': raw_count,
                    'cleaned_records': cleaned_count,
                    'quality_score': report.quality_score if report else 0
                }
                
                summary['total_raw_records'] += raw_count
                summary['total_cleaned_records'] += cleaned_count
                
                if report:
                    quality_scores.append(report.quality_score)
        
        if quality_scores:
            summary['overall_quality_score'] = round(sum(quality_scores) / len(quality_scores), 1)
        
        return summary


# =============================================================================
# 全局实例
# =============================================================================

_pipeline_instance: Optional[DataPipeline] = None

def get_pipeline() -> DataPipeline:
    """获取数据管道单例"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DataPipeline()
    return _pipeline_instance


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    import random
    
    print("=" * 70)
    print("数据处理管道测试")
    print("=" * 70)
    
    pipeline = get_pipeline()
    user_id = "pipeline_test_user"
    
    # 1. 测试数据采集
    print("\n1. 数据采集测试")
    print("-" * 40)
    
    # 采集正常数据
    for i in range(30):
        day = datetime.now() - timedelta(days=29-i)
        
        # 血压
        pipeline.collect(
            user_id, "blood_pressure",
            {"systolic": 130 + random.randint(-15, 20), "diastolic": 80 + random.randint(-8, 12)},
            timestamp=day
        )
        
        # 心率
        pipeline.collect(
            user_id, "heart_rate",
            {"value": 72 + random.randint(-10, 15)},
            timestamp=day
        )
    
    # 采集一些异常数据
    pipeline.collect(user_id, "blood_pressure", {"systolic": 300, "diastolic": 180})  # 异常
    pipeline.collect(user_id, "blood_pressure", {"systolic": 120, "diastolic": 80})   # 重复测试
    pipeline.collect(user_id, "blood_pressure", {"systolic": 120, "diastolic": 80})   # 重复
    
    print(f"   采集血压数据: 33 条（含异常值和重复）")
    print(f"   采集心率数据: 30 条")
    
    # 2. 测试数据清洗
    print("\n2. 数据清洗测试")
    print("-" * 40)
    
    bp_cleaned, bp_report = pipeline.clean(user_id, "blood_pressure", days=30)
    print(f"   血压数据清洗结果:")
    print(f"     原始记录: {bp_report.total_records}")
    print(f"     有效记录: {bp_report.valid_records}")
    print(f"     去除重复: {bp_report.duplicates_removed}")
    print(f"     检测异常: {bp_report.outliers_detected}")
    print(f"     质量评分: {bp_report.quality_score:.1f}")
    
    hr_cleaned, hr_report = pipeline.clean(user_id, "heart_rate", days=30)
    print(f"\n   心率数据清洗结果:")
    print(f"     原始记录: {hr_report.total_records}")
    print(f"     有效记录: {hr_report.valid_records}")
    print(f"     质量评分: {hr_report.quality_score:.1f}")
    
    # 3. 获取管道摘要
    print("\n3. 管道摘要")
    print("-" * 40)
    summary = pipeline.get_pipeline_summary(user_id)
    print(f"   用户: {summary['user_id']}")
    print(f"   原始记录总数: {summary['total_raw_records']}")
    print(f"   清洗后记录总数: {summary['total_cleaned_records']}")
    print(f"   综合质量评分: {summary['overall_quality_score']}")
    
    print("\n✓ 数据管道测试完成")
