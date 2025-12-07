"""
模块2：数据准备与特征构建子模块
Data Preparation and Feature Engineering Module

功能：
- 从健康档案抽取数据
- 数据预处理（异常值处理、聚合）
- 特征工程（统计量计算）

算法分配：
- 异常值检测：IQR方法 + Z-score
- 时间序列聚合：滑动窗口统计
- 特征工程：统计特征 + 趋势特征
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from scipy import stats


@dataclass
class HealthMetrics:
    """健康指标数据"""
    metric_name: str
    timestamps: List[datetime]
    values: List[float]
    unit: str
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        return pd.DataFrame({
            'timestamp': self.timestamps,
            'value': self.values
        })


@dataclass
class FeatureSet:
    """特征集合"""
    user_id: str
    assessment_period: Tuple[datetime, datetime]
    
    # 血压特征
    sbp_mean: Optional[float] = None
    sbp_std: Optional[float] = None
    sbp_max: Optional[float] = None
    sbp_min: Optional[float] = None
    sbp_trend: Optional[float] = None  # 趋势斜率
    sbp_cv: Optional[float] = None  # 变异系数
    sbp_compliance_rate: Optional[float] = None  # 达标率
    
    dbp_mean: Optional[float] = None
    dbp_std: Optional[float] = None
    dbp_max: Optional[float] = None
    dbp_min: Optional[float] = None
    
    # 血糖特征
    glucose_mean: Optional[float] = None
    glucose_std: Optional[float] = None
    glucose_max: Optional[float] = None
    glucose_fasting_mean: Optional[float] = None
    glucose_postprandial_mean: Optional[float] = None
    glucose_cv: Optional[float] = None
    glucose_compliance_rate: Optional[float] = None
    
    # 血脂特征
    tc_mean: Optional[float] = None  # 总胆固醇
    ldl_mean: Optional[float] = None  # 低密度脂蛋白
    hdl_mean: Optional[float] = None  # 高密度脂蛋白
    tg_mean: Optional[float] = None  # 甘油三酯
    
    # 心率特征
    hr_mean: Optional[float] = None
    hr_std: Optional[float] = None
    hr_max: Optional[float] = None
    hr_min: Optional[float] = None
    
    # 体重/BMI特征
    weight_mean: Optional[float] = None
    weight_change: Optional[float] = None  # 相对基线的变化
    bmi_mean: Optional[float] = None
    bmi_category: Optional[str] = None
    
    # 睡眠特征
    sleep_duration_mean: Optional[float] = None
    sleep_duration_std: Optional[float] = None
    sleep_quality_score: Optional[float] = None
    sleep_insufficient_days: Optional[int] = None
    sleep_regularity_score: Optional[float] = None
    
    # 运动特征
    steps_mean: Optional[float] = None
    steps_std: Optional[float] = None
    active_days_ratio: Optional[float] = None  # 活跃天数比例
    sedentary_time_mean: Optional[float] = None
    
    # 用药特征
    medication_adherence: Optional[float] = None  # 用药依从性
    medication_count: Optional[int] = None
    
    # 时间特征
    data_collection_days: int = 0
    weekday_weekend_diff: Optional[Dict] = None  # 工作日/周末差异
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        self.outlier_method = "iqr"  # iqr 或 zscore
        self.iqr_multiplier = 1.5
        self.zscore_threshold = 3.0
    
    def remove_outliers(
        self, 
        data: np.ndarray, 
        method: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        去除异常值
        
        Returns:
            (cleaned_data, outlier_mask)
        """
        method = method or self.outlier_method
        
        if method == "iqr":
            return self._remove_outliers_iqr(data)
        elif method == "zscore":
            return self._remove_outliers_zscore(data)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _remove_outliers_iqr(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """IQR方法去除异常值"""
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        mask = (data >= lower_bound) & (data <= upper_bound)
        return data[mask], mask
    
    def _remove_outliers_zscore(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Z-score方法去除异常值"""
        z_scores = np.abs(stats.zscore(data))
        mask = z_scores < self.zscore_threshold
        return data[mask], mask
    
    def aggregate_by_day(
        self, 
        timestamps: List[datetime], 
        values: List[float]
    ) -> pd.DataFrame:
        """按天聚合数据"""
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        daily_agg = df.groupby('date').agg({
            'value': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()
        
        daily_agg.columns = ['date', 'mean', 'std', 'min', 'max', 'count']
        return daily_agg
    
    def aggregate_by_week(
        self, 
        timestamps: List[datetime], 
        values: List[float]
    ) -> pd.DataFrame:
        """按周聚合数据"""
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        weekly_agg = df.resample('W').agg({
            'value': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()
        
        weekly_agg.columns = ['week', 'mean', 'std', 'min', 'max', 'count']
        return weekly_agg


class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        
        # 健康标准阈值（可从配置文件加载）
        self.thresholds = {
            'sbp_normal': 120,
            'sbp_high': 140,
            'dbp_normal': 80,
            'dbp_high': 90,
            'glucose_fasting_normal': 6.1,
            'glucose_fasting_high': 7.0,
            'sleep_min': 6.0,
            'sleep_optimal': 7.0,
            'steps_min': 6000,
            'steps_optimal': 10000,
        }
    
    def build_features(
        self,
        user_id: str,
        raw_data: Dict[str, HealthMetrics],
        assessment_period: Tuple[datetime, datetime],
        baseline_data: Optional[Dict] = None
    ) -> FeatureSet:
        """
        构建特征集合
        
        Args:
            user_id: 用户ID
            raw_data: 原始健康数据
            assessment_period: 评估周期
            baseline_data: 基线数据（用于计算变化）
        
        Returns:
            特征集合
        """
        features = FeatureSet(
            user_id=user_id,
            assessment_period=assessment_period
        )
        
        # 构建血压特征
        if 'blood_pressure' in raw_data:
            bp_data = raw_data['blood_pressure']
            features = self._build_blood_pressure_features(features, bp_data, baseline_data)
        
        # 构建血糖特征
        if 'blood_glucose' in raw_data:
            glucose_data = raw_data['blood_glucose']
            features = self._build_glucose_features(features, glucose_data, baseline_data)
        
        # 构建血脂特征
        if 'blood_lipid' in raw_data:
            lipid_data = raw_data['blood_lipid']
            features = self._build_lipid_features(features, lipid_data)
        
        # 构建心率特征
        if 'heart_rate' in raw_data:
            hr_data = raw_data['heart_rate']
            features = self._build_heart_rate_features(features, hr_data)
        
        # 构建体重/BMI特征
        if 'weight' in raw_data:
            weight_data = raw_data['weight']
            features = self._build_weight_features(features, weight_data, baseline_data)
        
        # 构建睡眠特征
        if 'sleep' in raw_data:
            sleep_data = raw_data['sleep']
            features = self._build_sleep_features(features, sleep_data)
        
        # 构建运动特征
        if 'steps' in raw_data:
            steps_data = raw_data['steps']
            features = self._build_activity_features(features, steps_data)
        
        # 构建用药特征
        if 'medication' in raw_data:
            med_data = raw_data['medication']
            features = self._build_medication_features(features, med_data)
        
        return features
    
    def _build_blood_pressure_features(
        self, 
        features: FeatureSet, 
        bp_data: HealthMetrics,
        baseline_data: Optional[Dict]
    ) -> FeatureSet:
        """构建血压特征"""
        # 假设bp_data包含收缩压和舒张压
        df = bp_data.to_dataframe()
        
        # 这里简化处理，实际应该分别处理SBP和DBP
        values = np.array(df['value'].tolist())
        
        # 去除异常值
        clean_values, _ = self.preprocessor.remove_outliers(values)
        
        if len(clean_values) > 0:
            features.sbp_mean = float(np.mean(clean_values))
            features.sbp_std = float(np.std(clean_values))
            features.sbp_max = float(np.max(clean_values))
            features.sbp_min = float(np.min(clean_values))
            
            # 变异系数
            if features.sbp_mean > 0:
                features.sbp_cv = features.sbp_std / features.sbp_mean
            
            # 趋势计算（线性回归斜率）
            if len(clean_values) > 2:
                x = np.arange(len(clean_values))
                slope, _ = np.polyfit(x, clean_values, 1)
                features.sbp_trend = float(slope)
            
            # 达标率
            compliant_count = np.sum(clean_values < self.thresholds['sbp_high'])
            features.sbp_compliance_rate = compliant_count / len(clean_values)
        
        return features
    
    def _build_glucose_features(
        self, 
        features: FeatureSet, 
        glucose_data: HealthMetrics,
        baseline_data: Optional[Dict]
    ) -> FeatureSet:
        """构建血糖特征"""
        df = glucose_data.to_dataframe()
        values = np.array(df['value'].tolist())
        
        clean_values, _ = self.preprocessor.remove_outliers(values)
        
        if len(clean_values) > 0:
            features.glucose_mean = float(np.mean(clean_values))
            features.glucose_std = float(np.std(clean_values))
            features.glucose_max = float(np.max(clean_values))
            
            # 变异系数（血糖波动的重要指标）
            if features.glucose_mean > 0:
                features.glucose_cv = features.glucose_std / features.glucose_mean
            
            # 达标率
            compliant_count = np.sum(clean_values < self.thresholds['glucose_fasting_high'])
            features.glucose_compliance_rate = compliant_count / len(clean_values)
        
        return features
    
    def _build_lipid_features(
        self, 
        features: FeatureSet, 
        lipid_data: HealthMetrics
    ) -> FeatureSet:
        """构建血脂特征"""
        # 简化处理，实际应分别处理TC、LDL、HDL、TG
        df = lipid_data.to_dataframe()
        values = np.array(df['value'].tolist())
        
        if len(values) > 0:
            features.tc_mean = float(np.mean(values))
        
        return features
    
    def _build_heart_rate_features(
        self, 
        features: FeatureSet, 
        hr_data: HealthMetrics
    ) -> FeatureSet:
        """构建心率特征"""
        df = hr_data.to_dataframe()
        values = np.array(df['value'].tolist())
        
        clean_values, _ = self.preprocessor.remove_outliers(values)
        
        if len(clean_values) > 0:
            features.hr_mean = float(np.mean(clean_values))
            features.hr_std = float(np.std(clean_values))
            features.hr_max = float(np.max(clean_values))
            features.hr_min = float(np.min(clean_values))
        
        return features
    
    def _build_weight_features(
        self, 
        features: FeatureSet, 
        weight_data: HealthMetrics,
        baseline_data: Optional[Dict]
    ) -> FeatureSet:
        """构建体重/BMI特征"""
        df = weight_data.to_dataframe()
        values = np.array(df['value'].tolist())
        
        if len(values) > 0:
            features.weight_mean = float(np.mean(values))
            
            # 计算相对基线的变化
            if baseline_data and 'weight' in baseline_data:
                baseline_weight = baseline_data['weight']
                features.weight_change = features.weight_mean - baseline_weight
        
        return features
    
    def _build_sleep_features(
        self, 
        features: FeatureSet, 
        sleep_data: HealthMetrics
    ) -> FeatureSet:
        """构建睡眠特征"""
        df = sleep_data.to_dataframe()
        values = np.array(df['value'].tolist())  # 睡眠时长（小时）
        
        if len(values) > 0:
            features.sleep_duration_mean = float(np.mean(values))
            features.sleep_duration_std = float(np.std(values))
            
            # 睡眠不足天数
            insufficient_days = np.sum(values < self.thresholds['sleep_min'])
            features.sleep_insufficient_days = int(insufficient_days)
            
            # 睡眠规律性评分（基于标准差，越小越规律）
            if features.sleep_duration_std is not None:
                # 标准差越小，规律性越高
                features.sleep_regularity_score = max(0, 100 - features.sleep_duration_std * 20)
        
        return features
    
    def _build_activity_features(
        self, 
        features: FeatureSet, 
        steps_data: HealthMetrics
    ) -> FeatureSet:
        """构建运动特征"""
        df = steps_data.to_dataframe()
        values = np.array(df['value'].tolist())
        
        if len(values) > 0:
            features.steps_mean = float(np.mean(values))
            features.steps_std = float(np.std(values))
            
            # 活跃天数比例（步数达标的天数）
            active_days = np.sum(values >= self.thresholds['steps_min'])
            features.active_days_ratio = active_days / len(values)
            
            features.data_collection_days = len(values)
        
        return features
    
    def _build_medication_features(
        self, 
        features: FeatureSet, 
        med_data: HealthMetrics
    ) -> FeatureSet:
        """构建用药特征"""
        df = med_data.to_dataframe()
        
        # 假设value为1表示按时服药，0表示未服药
        if len(df) > 0:
            adherence = df['value'].mean()
            features.medication_adherence = float(adherence)
            features.medication_count = len(df)
        
        return features
    
    def calculate_baseline(
        self,
        historical_data: Dict[str, HealthMetrics],
        baseline_period_days: int = 90
    ) -> Dict:
        """
        计算个人基线
        
        Args:
            historical_data: 历史数据
            baseline_period_days: 基线周期天数
        
        Returns:
            基线数据字典
        """
        baseline = {}
        
        for metric_name, metric_data in historical_data.items():
            df = metric_data.to_dataframe()
            values = np.array(df['value'].tolist())
            
            if len(values) > 0:
                clean_values, _ = self.preprocessor.remove_outliers(values)
                if len(clean_values) > 0:
                    baseline[metric_name] = {
                        'mean': float(np.mean(clean_values)),
                        'std': float(np.std(clean_values)),
                        'median': float(np.median(clean_values)),
                        'p25': float(np.percentile(clean_values, 25)),
                        'p75': float(np.percentile(clean_values, 75))
                    }
        
        return baseline


# 使用示例
if __name__ == "__main__":
    # 模拟数据
    from datetime import datetime, timedelta
    
    # 创建模拟血压数据
    start_date = datetime.now() - timedelta(days=30)
    timestamps = [start_date + timedelta(days=i) for i in range(30)]
    sbp_values = np.random.normal(135, 10, 30).tolist()  # 收缩压
    
    bp_data = HealthMetrics(
        metric_name='systolic_bp',
        timestamps=timestamps,
        values=sbp_values,
        unit='mmHg'
    )
    
    # 创建特征工程器
    engineer = FeatureEngineer()
    
    # 构建特征
    raw_data = {'blood_pressure': bp_data}
    features = engineer.build_features(
        user_id='USER001',
        raw_data=raw_data,
        assessment_period=(start_date, datetime.now())
    )
    
    print("构建的特征:")
    print(features.to_dict())
