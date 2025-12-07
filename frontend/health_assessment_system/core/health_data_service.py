"""
健康数据服务层
===============

整合数据采集、清洗、分析、评估的完整流水线。
作为 API 和底层模块之间的桥梁。

数据处理流程：
    原始数据 → 数据清洗 → 特征工程 → 健康评估 → API 响应

作者: 智能诊断系统
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json

# 导入数据处理模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_preparation import (
    DataPreprocessor, 
    FeatureEngineer, 
    HealthMetrics, 
    FeatureSet
)
from modules.indicator_evaluator import IndicatorEvaluator, ReferenceRange


# =============================================================================
# 数据模型定义
# =============================================================================

@dataclass
class RawHealthRecord:
    """原始健康记录（未清洗）"""
    user_id: str
    timestamp: datetime
    data_type: str  # blood_pressure, glucose, heart_rate, sleep, steps, weight
    values: Dict[str, Any]
    source: str = "manual"  # manual, sensor, device
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass 
class CleanedHealthData:
    """清洗后的健康数据"""
    user_id: str
    data_type: str
    timestamps: List[datetime]
    values: List[float]
    outliers_removed: int = 0
    cleaning_method: str = "iqr"
    quality_score: float = 1.0  # 数据质量评分 0-1


@dataclass
class ProcessedHealthFeatures:
    """处理后的健康特征"""
    user_id: str
    period: Tuple[datetime, datetime]
    features: FeatureSet
    
    # 各指标评估结果
    blood_pressure_assessment: Optional[Dict] = None
    glucose_assessment: Optional[Dict] = None
    heart_rate_assessment: Optional[Dict] = None
    sleep_assessment: Optional[Dict] = None
    activity_assessment: Optional[Dict] = None
    
    # 综合评分
    overall_score: float = 0.0
    health_level: str = "unknown"
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'period': {
                'start': self.period[0].isoformat(),
                'end': self.period[1].isoformat()
            },
            'features': self.features.to_dict() if self.features else {},
            'assessments': {
                'blood_pressure': self.blood_pressure_assessment,
                'glucose': self.glucose_assessment,
                'heart_rate': self.heart_rate_assessment,
                'sleep': self.sleep_assessment,
                'activity': self.activity_assessment
            },
            'overall_score': self.overall_score,
            'health_level': self.health_level
        }


# =============================================================================
# 健康数据服务类
# =============================================================================

class HealthDataService:
    """
    健康数据服务 - 数据处理核心
    
    职责：
    1. 数据清洗 - 去除异常值、填充缺失值
    2. 数据聚合 - 按时间周期聚合
    3. 特征工程 - 计算统计特征
    4. 健康评估 - 调用评估模块
    5. 数据缓存 - 避免重复计算
    
    使用示例：
    ```python
    service = HealthDataService()
    
    # 添加原始数据
    service.add_raw_data(RawHealthRecord(
        user_id="elderly_001",
        timestamp=datetime.now(),
        data_type="blood_pressure",
        values={"systolic": 135, "diastolic": 85}
    ))
    
    # 处理并获取结果
    result = service.process_user_data("elderly_001", days=7)
    ```
    """
    
    def __init__(self):
        # 数据处理器
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.indicator_evaluator = IndicatorEvaluator()
        
        # 数据存储（内存缓存，后续可替换为数据库）
        self._raw_data_store: Dict[str, List[RawHealthRecord]] = {}
        self._cleaned_data_cache: Dict[str, Dict[str, CleanedHealthData]] = {}
        self._feature_cache: Dict[str, ProcessedHealthFeatures] = {}
        
        # 配置
        self.outlier_method = "iqr"  # iqr 或 zscore
        self.cache_ttl_seconds = 300  # 缓存有效期
        
        print("✓ HealthDataService 初始化完成")
    
    # =========================================================================
    # 1. 数据输入接口
    # =========================================================================
    
    def add_raw_data(self, record: RawHealthRecord) -> bool:
        """
        添加原始健康数据
        
        Args:
            record: 原始健康记录
            
        Returns:
            是否添加成功
        """
        user_id = record.user_id
        
        if user_id not in self._raw_data_store:
            self._raw_data_store[user_id] = []
        
        self._raw_data_store[user_id].append(record)
        
        # 清除该用户的缓存（数据已更新）
        self._invalidate_cache(user_id)
        
        return True
    
    def add_batch_data(self, records: List[RawHealthRecord]) -> int:
        """批量添加原始数据"""
        success_count = 0
        for record in records:
            if self.add_raw_data(record):
                success_count += 1
        return success_count
    
    def import_from_dict(self, user_id: str, data_type: str, data: Dict) -> bool:
        """
        从字典导入数据（便捷方法）
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data: 数据字典，如 {"systolic": 135, "diastolic": 85}
        """
        record = RawHealthRecord(
            user_id=user_id,
            timestamp=datetime.now(),
            data_type=data_type,
            values=data,
            source="api"
        )
        return self.add_raw_data(record)
    
    # =========================================================================
    # 2. 数据清洗
    # =========================================================================
    
    def clean_data(
        self, 
        user_id: str, 
        data_type: str,
        days: int = 30
    ) -> Optional[CleanedHealthData]:
        """
        清洗指定类型的健康数据
        
        流程：
        1. 提取原始数据
        2. 去除异常值（IQR/Z-score）
        3. 处理缺失值
        4. 计算数据质量评分
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            days: 回溯天数
            
        Returns:
            清洗后的数据
        """
        # 检查缓存
        cache_key = f"{user_id}_{data_type}_{days}"
        if cache_key in self._cleaned_data_cache.get(user_id, {}):
            return self._cleaned_data_cache[user_id][cache_key]
        
        # 获取原始数据
        raw_records = self._get_raw_data(user_id, data_type, days)
        if not raw_records:
            return None
        
        # 提取时间戳和数值
        timestamps = []
        values = []
        
        for record in raw_records:
            timestamps.append(record.timestamp)
            # 根据数据类型提取主要数值
            value = self._extract_primary_value(record.data_type, record.values)
            if value is not None:
                values.append(value)
        
        if not values:
            return None
        
        # 转换为 numpy 数组进行处理
        values_array = np.array(values)
        
        # 去除异常值
        cleaned_values, outlier_mask = self.preprocessor.remove_outliers(
            values_array, 
            method=self.outlier_method
        )
        
        outliers_removed = len(values) - len(cleaned_values)
        
        # 过滤对应的时间戳
        cleaned_timestamps = [ts for ts, mask in zip(timestamps, outlier_mask) if mask]
        
        # 计算数据质量评分
        quality_score = self._calculate_quality_score(
            total_count=len(values),
            outliers_removed=outliers_removed,
            expected_count=days  # 期望每天至少1条数据
        )
        
        # 创建清洗后的数据对象
        cleaned_data = CleanedHealthData(
            user_id=user_id,
            data_type=data_type,
            timestamps=cleaned_timestamps,
            values=cleaned_values.tolist(),
            outliers_removed=outliers_removed,
            cleaning_method=self.outlier_method,
            quality_score=quality_score
        )
        
        # 缓存结果
        if user_id not in self._cleaned_data_cache:
            self._cleaned_data_cache[user_id] = {}
        self._cleaned_data_cache[user_id][cache_key] = cleaned_data
        
        return cleaned_data
    
    def _extract_primary_value(self, data_type: str, values: Dict) -> Optional[float]:
        """从数据字典中提取主要数值"""
        extractors = {
            'blood_pressure': lambda v: v.get('systolic'),  # 收缩压作为主要指标
            'glucose': lambda v: v.get('value') or v.get('glucose'),
            'heart_rate': lambda v: v.get('value') or v.get('hr') or v.get('heart_rate'),
            'sleep': lambda v: v.get('duration') or v.get('total_hours'),
            'steps': lambda v: v.get('value') or v.get('steps') or v.get('count'),
            'weight': lambda v: v.get('value') or v.get('weight'),
            'temperature': lambda v: v.get('value') or v.get('temp'),
            'spo2': lambda v: v.get('value') or v.get('spo2')
        }
        
        extractor = extractors.get(data_type, lambda v: v.get('value'))
        return extractor(values)
    
    def _calculate_quality_score(
        self, 
        total_count: int, 
        outliers_removed: int,
        expected_count: int
    ) -> float:
        """计算数据质量评分"""
        if total_count == 0:
            return 0.0
        
        # 完整性评分（数据量是否充足）
        completeness = min(1.0, total_count / max(expected_count, 1))
        
        # 清洁度评分（异常值比例）
        cleanliness = 1.0 - (outliers_removed / total_count) if total_count > 0 else 0.0
        
        # 综合评分
        return round(completeness * 0.6 + cleanliness * 0.4, 2)
    
    # =========================================================================
    # 3. 特征工程
    # =========================================================================
    
    def build_features(
        self, 
        user_id: str, 
        days: int = 7
    ) -> Optional[ProcessedHealthFeatures]:
        """
        构建健康特征
        
        流程：
        1. 清洗各类型数据
        2. 构建统计特征（均值、标准差、趋势等）
        3. 进行各维度健康评估
        4. 计算综合评分
        
        Args:
            user_id: 用户ID
            days: 评估周期
            
        Returns:
            处理后的健康特征
        """
        now = datetime.now()
        start_date = now - timedelta(days=days)
        period = (start_date, now)
        
        # 收集各类型的清洗后数据
        data_types = ['blood_pressure', 'glucose', 'heart_rate', 'sleep', 'steps', 'weight']
        raw_data = {}
        
        for dtype in data_types:
            cleaned = self.clean_data(user_id, dtype, days)
            if cleaned and cleaned.values:
                # 转换为 HealthMetrics 格式
                raw_data[dtype] = HealthMetrics(
                    metric_name=dtype,
                    timestamps=cleaned.timestamps,
                    values=cleaned.values,
                    unit=self._get_unit(dtype)
                )
        
        if not raw_data:
            return None
        
        # 使用 FeatureEngineer 构建特征
        features = self.feature_engineer.build_features(
            user_id=user_id,
            raw_data=raw_data,
            assessment_period=period
        )
        
        # 创建处理结果
        result = ProcessedHealthFeatures(
            user_id=user_id,
            period=period,
            features=features
        )
        
        # 进行各维度评估
        result.blood_pressure_assessment = self._assess_blood_pressure(features)
        result.glucose_assessment = self._assess_glucose(features)
        result.heart_rate_assessment = self._assess_heart_rate(features)
        result.sleep_assessment = self._assess_sleep(features)
        result.activity_assessment = self._assess_activity(features)
        
        # 计算综合评分
        result.overall_score, result.health_level = self._calculate_overall_score(result)
        
        return result
    
    def _get_unit(self, data_type: str) -> str:
        """获取数据单位"""
        units = {
            'blood_pressure': 'mmHg',
            'glucose': 'mmol/L',
            'heart_rate': 'bpm',
            'sleep': 'hours',
            'steps': 'steps',
            'weight': 'kg',
            'temperature': '°C',
            'spo2': '%'
        }
        return units.get(data_type, '')
    
    # =========================================================================
    # 4. 健康评估
    # =========================================================================
    
    def _assess_blood_pressure(self, features: FeatureSet) -> Optional[Dict]:
        """评估血压状况"""
        if features.sbp_mean is None:
            return None
        
        sbp = features.sbp_mean
        dbp = features.dbp_mean or 80
        
        # 判断等级
        if sbp < 120 and dbp < 80:
            level = "正常"
            score = 100
        elif sbp < 130 and dbp < 85:
            level = "正常偏高"
            score = 85
        elif sbp < 140 and dbp < 90:
            level = "1级高血压前期"
            score = 70
        elif sbp < 160 and dbp < 100:
            level = "1级高血压"
            score = 55
        elif sbp < 180 and dbp < 110:
            level = "2级高血压"
            score = 40
        else:
            level = "3级高血压"
            score = 25
        
        return {
            'mean_systolic': round(sbp, 1),
            'mean_diastolic': round(dbp, 1) if dbp else None,
            'variability': round(features.sbp_cv * 100, 1) if features.sbp_cv else None,
            'trend': round(features.sbp_trend, 2) if features.sbp_trend else None,
            'compliance_rate': round(features.sbp_compliance_rate * 100, 1) if features.sbp_compliance_rate else None,
            'level': level,
            'score': score,
            'advice': self._get_bp_advice(level)
        }
    
    def _assess_glucose(self, features: FeatureSet) -> Optional[Dict]:
        """评估血糖状况"""
        if features.glucose_mean is None:
            return None
        
        glucose = features.glucose_mean
        
        if glucose < 6.1:
            level = "正常"
            score = 100
        elif glucose < 7.0:
            level = "空腹血糖受损"
            score = 75
        elif glucose < 11.1:
            level = "糖尿病前期"
            score = 55
        else:
            level = "糖尿病"
            score = 35
        
        return {
            'mean_value': round(glucose, 2),
            'variability': round(features.glucose_cv * 100, 1) if features.glucose_cv else None,
            'compliance_rate': round(features.glucose_compliance_rate * 100, 1) if features.glucose_compliance_rate else None,
            'level': level,
            'score': score,
            'advice': self._get_glucose_advice(level)
        }
    
    def _assess_heart_rate(self, features: FeatureSet) -> Optional[Dict]:
        """评估心率状况"""
        if features.hr_mean is None:
            return None
        
        hr = features.hr_mean
        
        if 60 <= hr <= 100:
            level = "正常"
            score = 100
        elif 50 <= hr < 60 or 100 < hr <= 110:
            level = "边缘"
            score = 80
        else:
            level = "异常"
            score = 50
        
        return {
            'mean_value': round(hr, 1),
            'min_value': round(features.hr_min, 1) if features.hr_min else None,
            'max_value': round(features.hr_max, 1) if features.hr_max else None,
            'variability': round(features.hr_std, 1) if features.hr_std else None,
            'level': level,
            'score': score
        }
    
    def _assess_sleep(self, features: FeatureSet) -> Optional[Dict]:
        """评估睡眠状况"""
        if features.sleep_duration_mean is None:
            return None
        
        duration = features.sleep_duration_mean
        
        if 7 <= duration <= 9:
            level = "优秀"
            score = 100
        elif 6 <= duration < 7 or 9 < duration <= 10:
            level = "良好"
            score = 80
        elif 5 <= duration < 6:
            level = "不足"
            score = 60
        else:
            level = "严重不足"
            score = 40
        
        return {
            'mean_duration': round(duration, 1),
            'regularity_score': round(features.sleep_regularity_score, 1) if features.sleep_regularity_score else None,
            'insufficient_days': features.sleep_insufficient_days,
            'level': level,
            'score': score
        }
    
    def _assess_activity(self, features: FeatureSet) -> Optional[Dict]:
        """评估运动状况"""
        if features.steps_mean is None:
            return None
        
        steps = features.steps_mean
        
        if steps >= 10000:
            level = "优秀"
            score = 100
        elif steps >= 8000:
            level = "良好"
            score = 85
        elif steps >= 6000:
            level = "达标"
            score = 70
        elif steps >= 4000:
            level = "不足"
            score = 55
        else:
            level = "严重不足"
            score = 40
        
        return {
            'mean_steps': round(steps),
            'active_days_ratio': round(features.active_days_ratio * 100, 1) if features.active_days_ratio else None,
            'level': level,
            'score': score
        }
    
    def _calculate_overall_score(
        self, 
        result: ProcessedHealthFeatures
    ) -> Tuple[float, str]:
        """计算综合健康评分"""
        scores = []
        weights = []
        
        # 权重配置（AHP层次分析法确定）
        weight_config = {
            'blood_pressure': 0.25,
            'glucose': 0.20,
            'heart_rate': 0.15,
            'sleep': 0.20,
            'activity': 0.20
        }
        
        assessments = {
            'blood_pressure': result.blood_pressure_assessment,
            'glucose': result.glucose_assessment,
            'heart_rate': result.heart_rate_assessment,
            'sleep': result.sleep_assessment,
            'activity': result.activity_assessment
        }
        
        for key, assessment in assessments.items():
            if assessment and 'score' in assessment:
                scores.append(assessment['score'])
                weights.append(weight_config[key])
        
        if not scores:
            return 0.0, "unknown"
        
        # 归一化权重
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # 加权平均
        overall = sum(s * w for s, w in zip(scores, normalized_weights))
        
        # 确定健康等级
        if overall >= 85:
            level = "excellent"
        elif overall >= 70:
            level = "good"
        elif overall >= 55:
            level = "suboptimal"
        elif overall >= 40:
            level = "attention_needed"
        else:
            level = "high_risk"
        
        return round(overall, 1), level
    
    def _get_bp_advice(self, level: str) -> List[str]:
        """获取血压建议"""
        advice_map = {
            "正常": ["继续保持健康的生活方式"],
            "正常偏高": ["减少盐的摄入", "适当增加运动"],
            "1级高血压前期": ["调整饮食结构", "规律运动", "定期监测血压"],
            "1级高血压": ["建议就医", "遵医嘱服药", "低盐低脂饮食"],
            "2级高血压": ["及时就医", "严格按医嘱服药", "避免情绪激动"],
            "3级高血压": ["立即就医", "严密监控", "避免剧烈活动"]
        }
        return advice_map.get(level, [])
    
    def _get_glucose_advice(self, level: str) -> List[str]:
        """获取血糖建议"""
        advice_map = {
            "正常": ["继续保持健康饮食"],
            "空腹血糖受损": ["控制饮食", "减少糖分摄入", "增加运动"],
            "糖尿病前期": ["严格控制饮食", "定期复查", "考虑就医"],
            "糖尿病": ["遵医嘱治疗", "严格控制饮食", "定期监测血糖"]
        }
        return advice_map.get(level, [])
    
    # =========================================================================
    # 5. 辅助方法
    # =========================================================================
    
    def _get_raw_data(
        self, 
        user_id: str, 
        data_type: str, 
        days: int
    ) -> List[RawHealthRecord]:
        """获取指定用户、类型、时间范围的原始数据"""
        if user_id not in self._raw_data_store:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            record for record in self._raw_data_store[user_id]
            if record.data_type == data_type and record.timestamp >= cutoff
        ]
    
    def _invalidate_cache(self, user_id: str):
        """清除用户缓存"""
        if user_id in self._cleaned_data_cache:
            del self._cleaned_data_cache[user_id]
        if user_id in self._feature_cache:
            del self._feature_cache[user_id]
    
    def get_user_data_summary(self, user_id: str) -> Dict:
        """获取用户数据摘要"""
        if user_id not in self._raw_data_store:
            return {'user_id': user_id, 'record_count': 0, 'data_types': []}
        
        records = self._raw_data_store[user_id]
        data_types = list(set(r.data_type for r in records))
        
        return {
            'user_id': user_id,
            'record_count': len(records),
            'data_types': data_types,
            'date_range': {
                'earliest': min(r.timestamp for r in records).isoformat() if records else None,
                'latest': max(r.timestamp for r in records).isoformat() if records else None
            }
        }


# =============================================================================
# 便捷函数
# =============================================================================

# 全局服务实例
_health_data_service: Optional[HealthDataService] = None

def get_health_data_service() -> HealthDataService:
    """获取健康数据服务单例"""
    global _health_data_service
    if _health_data_service is None:
        _health_data_service = HealthDataService()
    return _health_data_service


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("健康数据服务测试")
    print("=" * 60)
    
    # 创建服务
    service = HealthDataService()
    
    # 模拟添加30天的数据
    user_id = "test_user_001"
    print(f"\n1. 为用户 {user_id} 添加模拟数据...")
    
    for i in range(30):
        day = datetime.now() - timedelta(days=29-i)
        
        # 血压数据
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=day,
            data_type="blood_pressure",
            values={
                "systolic": 130 + random.randint(-15, 20),
                "diastolic": 80 + random.randint(-8, 12)
            }
        ))
        
        # 血糖数据
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=day,
            data_type="glucose",
            values={"value": round(5.8 + random.uniform(-0.5, 1.2), 1)}
        ))
        
        # 心率数据
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=day,
            data_type="heart_rate",
            values={"value": 72 + random.randint(-10, 15)}
        ))
        
        # 睡眠数据
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=day,
            data_type="sleep",
            values={"duration": round(6.5 + random.uniform(-1, 1.5), 1)}
        ))
        
        # 步数数据
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=day,
            data_type="steps",
            values={"value": random.randint(4000, 10000)}
        ))
    
    # 添加一些异常值测试清洗功能
    service.add_raw_data(RawHealthRecord(
        user_id=user_id,
        timestamp=datetime.now() - timedelta(days=5),
        data_type="blood_pressure",
        values={"systolic": 250, "diastolic": 150}  # 异常值
    ))
    
    print(f"   添加了 {30*5 + 1} 条记录")
    
    # 查看数据摘要
    print("\n2. 数据摘要:")
    summary = service.get_user_data_summary(user_id)
    print(f"   记录数: {summary['record_count']}")
    print(f"   数据类型: {summary['data_types']}")
    
    # 数据清洗测试
    print("\n3. 数据清洗测试 (血压):")
    cleaned_bp = service.clean_data(user_id, "blood_pressure", days=30)
    if cleaned_bp:
        print(f"   原始数据点: {cleaned_bp.outliers_removed + len(cleaned_bp.values)}")
        print(f"   清洗后数据点: {len(cleaned_bp.values)}")
        print(f"   去除异常值: {cleaned_bp.outliers_removed}")
        print(f"   数据质量评分: {cleaned_bp.quality_score}")
    
    # 特征构建测试
    print("\n4. 特征构建与健康评估:")
    features = service.build_features(user_id, days=7)
    if features:
        print(f"   综合评分: {features.overall_score}")
        print(f"   健康等级: {features.health_level}")
        
        if features.blood_pressure_assessment:
            bp = features.blood_pressure_assessment
            print(f"\n   血压评估:")
            print(f"     平均收缩压: {bp['mean_systolic']} mmHg")
            print(f"     等级: {bp['level']}")
            print(f"     评分: {bp['score']}")
        
        if features.glucose_assessment:
            gl = features.glucose_assessment
            print(f"\n   血糖评估:")
            print(f"     平均血糖: {gl['mean_value']} mmol/L")
            print(f"     等级: {gl['level']}")
            print(f"     评分: {gl['score']}")
    
    print("\n✓ 测试完成")
