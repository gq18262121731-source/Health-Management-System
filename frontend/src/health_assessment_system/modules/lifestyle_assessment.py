"""
模块4：生活方式与行为风险评估子模块
Lifestyle and Behavioral Risk Assessment Module

功能：
- 睡眠质量风险评估
- 运动不足风险评估
- 饮食习惯风险评估
- 作息规律性评估

算法分配：
- HMM（隐马尔可夫模型）：识别行为状态转换
- 时间序列聚类（DTW）：识别异常模式
- Isolation Forest：异常行为检测
- 规则引擎：基于阈值的评分
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# 尝试导入可选依赖
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class LifestyleRiskLevel(Enum):
    """生活方式风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class LifestyleRiskResult:
    """生活方式风险评估结果"""
    overall_score: float  # 0-100，越高越好
    overall_risk_level: LifestyleRiskLevel
    
    # 分项评分
    sleep_score: float = 0.0
    exercise_score: float = 0.0
    diet_score: float = 0.0
    regularity_score: float = 0.0
    
    # 分项风险
    sleep_risk: LifestyleRiskLevel = LifestyleRiskLevel.LOW
    exercise_risk: LifestyleRiskLevel = LifestyleRiskLevel.LOW
    diet_risk: LifestyleRiskLevel = LifestyleRiskLevel.LOW
    
    # 关键问题
    key_issues: List[str] = field(default_factory=list)
    
    # 详细信息
    sleep_details: Dict = field(default_factory=dict)
    exercise_details: Dict = field(default_factory=dict)
    diet_details: Dict = field(default_factory=dict)
    
    # 异常天数
    abnormal_days: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'overall_score': self.overall_score,
            'overall_risk_level': self.overall_risk_level.value,
            'sleep_score': self.sleep_score,
            'exercise_score': self.exercise_score,
            'diet_score': self.diet_score,
            'regularity_score': self.regularity_score,
            'sleep_risk': self.sleep_risk.value,
            'exercise_risk': self.exercise_risk.value,
            'diet_risk': self.diet_risk.value,
            'key_issues': self.key_issues,
            'sleep_details': self.sleep_details,
            'exercise_details': self.exercise_details,
            'diet_details': self.diet_details,
            'abnormal_days_count': len(self.abnormal_days)
        }


class SleepQualityAssessor:
    """睡眠质量评估器"""
    
    def __init__(self):
        # 睡眠标准
        self.optimal_duration = (7, 9)  # 最佳睡眠时长（小时）
        self.minimum_duration = 6
        self.maximum_duration = 10
        
        # 作息规律性标准
        self.regularity_threshold = 1.5  # 标准差阈值（小时）
    
    def assess(self, features: Dict) -> Tuple[float, LifestyleRiskLevel, Dict]:
        """
        评估睡眠质量
        
        Args:
            features: 特征字典
        
        Returns:
            (睡眠评分, 风险等级, 详细信息)
        """
        sleep_duration_mean = features.get('sleep_duration_mean', 7.0)
        sleep_duration_std = features.get('sleep_duration_std', 0.5)
        sleep_insufficient_days = features.get('sleep_insufficient_days', 0)
        data_days = features.get('data_collection_days', 30)
        sleep_regularity_score = features.get('sleep_regularity_score', 80)
        
        score = 0.0
        details = {}
        issues = []
        
        # 1. 睡眠时长评分 (0-40分)
        duration_score = self._score_sleep_duration(sleep_duration_mean)
        score += duration_score
        details['duration_score'] = duration_score
        details['average_duration'] = sleep_duration_mean
        
        if sleep_duration_mean < self.minimum_duration:
            issues.append(f"平均睡眠时长不足（{sleep_duration_mean:.1f}小时/天）")
        elif sleep_duration_mean > self.maximum_duration:
            issues.append(f"平均睡眠时长过长（{sleep_duration_mean:.1f}小时/天）")
        
        # 2. 睡眠规律性评分 (0-30分)
        regularity_score = self._score_sleep_regularity(sleep_duration_std)
        score += regularity_score
        details['regularity_score'] = regularity_score
        details['duration_std'] = sleep_duration_std
        
        if sleep_duration_std > self.regularity_threshold:
            issues.append(f"睡眠时间不规律（标准差{sleep_duration_std:.1f}小时）")
        
        # 3. 睡眠不足频率评分 (0-30分)
        if data_days > 0:
            insufficient_ratio = sleep_insufficient_days / data_days
            frequency_score = max(0, 30 * (1 - insufficient_ratio * 2))
            score += frequency_score
            details['frequency_score'] = frequency_score
            details['insufficient_days'] = sleep_insufficient_days
            details['insufficient_ratio'] = insufficient_ratio
            
            if insufficient_ratio > 0.3:
                issues.append(f"睡眠不足天数过多（{insufficient_ratio*100:.1f}%）")
        
        # 确定风险等级
        if score >= 70:
            risk_level = LifestyleRiskLevel.LOW
        elif score >= 50:
            risk_level = LifestyleRiskLevel.MEDIUM
        else:
            risk_level = LifestyleRiskLevel.HIGH
        
        details['issues'] = issues
        
        return score, risk_level, details
    
    def _score_sleep_duration(self, duration: float) -> float:
        """睡眠时长评分"""
        if self.optimal_duration[0] <= duration <= self.optimal_duration[1]:
            return 40.0
        elif self.minimum_duration <= duration < self.optimal_duration[0]:
            # 线性插值
            return 20 + 20 * (duration - self.minimum_duration) / (self.optimal_duration[0] - self.minimum_duration)
        elif self.optimal_duration[1] < duration <= self.maximum_duration:
            return 20 + 20 * (self.maximum_duration - duration) / (self.maximum_duration - self.optimal_duration[1])
        elif duration < self.minimum_duration:
            return max(0, 20 * duration / self.minimum_duration)
        else:  # duration > maximum_duration
            return max(0, 20 - 5 * (duration - self.maximum_duration))
    
    def _score_sleep_regularity(self, std: float) -> float:
        """睡眠规律性评分"""
        if std < 0.5:
            return 30.0
        elif std < 1.0:
            return 25.0
        elif std < 1.5:
            return 20.0
        elif std < 2.0:
            return 10.0
        else:
            return 0.0
    
    def detect_sleep_patterns(
        self, 
        sleep_data: List[Tuple[datetime, float]]
    ) -> Dict:
        """
        检测睡眠模式（如连续熬夜）
        
        Args:
            sleep_data: [(日期, 睡眠时长), ...]
        
        Returns:
            模式检测结果
        """
        patterns = {
            'consecutive_insufficient': [],  # 连续睡眠不足
            'weekend_catchup': False,  # 周末补觉
            'irregular_pattern': False  # 不规律模式
        }
        
        if len(sleep_data) < 3:
            return patterns
        
        # 检测连续睡眠不足
        consecutive_count = 0
        consecutive_start = None
        
        for i, (date, duration) in enumerate(sleep_data):
            if duration < self.minimum_duration:
                if consecutive_count == 0:
                    consecutive_start = date
                consecutive_count += 1
            else:
                if consecutive_count >= 3:
                    patterns['consecutive_insufficient'].append({
                        'start_date': consecutive_start,
                        'days': consecutive_count
                    })
                consecutive_count = 0
        
        # 检测周末补觉模式
        weekday_sleep = []
        weekend_sleep = []
        
        for date, duration in sleep_data:
            if date.weekday() < 5:  # 周一到周五
                weekday_sleep.append(duration)
            else:
                weekend_sleep.append(duration)
        
        if weekday_sleep and weekend_sleep:
            weekday_avg = np.mean(weekday_sleep)
            weekend_avg = np.mean(weekend_sleep)
            
            if weekend_avg - weekday_avg > 1.5:
                patterns['weekend_catchup'] = True
        
        return patterns


class ExerciseAssessor:
    """运动评估器"""
    
    def __init__(self):
        # 运动标准
        self.optimal_steps = 10000
        self.minimum_steps = 6000
        self.sedentary_threshold = 3000
        
        # 活跃天数标准
        self.active_days_target = 0.8  # 80%的天数应该活跃
    
    def assess(self, features: Dict) -> Tuple[float, LifestyleRiskLevel, Dict]:
        """
        评估运动情况
        
        Returns:
            (运动评分, 风险等级, 详细信息)
        """
        steps_mean = features.get('steps_mean', 5000)
        steps_std = features.get('steps_std', 2000)
        active_days_ratio = features.get('active_days_ratio', 0.5)
        sedentary_time = features.get('sedentary_time_mean', 8.0)
        
        score = 0.0
        details = {}
        issues = []
        
        # 1. 日均步数评分 (0-40分)
        steps_score = self._score_steps(steps_mean)
        score += steps_score
        details['steps_score'] = steps_score
        details['average_steps'] = steps_mean
        
        if steps_mean < self.sedentary_threshold:
            issues.append(f"日均步数严重不足（{steps_mean:.0f}步），久坐风险高")
        elif steps_mean < self.minimum_steps:
            issues.append(f"日均步数不足（{steps_mean:.0f}步），运动量偏低")
        
        # 2. 活跃天数比例评分 (0-35分)
        active_score = active_days_ratio * 35
        score += active_score
        details['active_score'] = active_score
        details['active_days_ratio'] = active_days_ratio
        
        if active_days_ratio < 0.5:
            issues.append(f"活跃天数过少（{active_days_ratio*100:.1f}%）")
        
        # 3. 运动规律性评分 (0-25分)
        regularity_score = self._score_exercise_regularity(steps_std, steps_mean)
        score += regularity_score
        details['regularity_score'] = regularity_score
        
        # 确定风险等级
        if score >= 70:
            risk_level = LifestyleRiskLevel.LOW
        elif score >= 50:
            risk_level = LifestyleRiskLevel.MEDIUM
        else:
            risk_level = LifestyleRiskLevel.HIGH
        
        details['issues'] = issues
        
        return score, risk_level, details
    
    def _score_steps(self, steps: float) -> float:
        """步数评分"""
        if steps >= self.optimal_steps:
            return 40.0
        elif steps >= self.minimum_steps:
            return 25 + 15 * (steps - self.minimum_steps) / (self.optimal_steps - self.minimum_steps)
        elif steps >= self.sedentary_threshold:
            return 10 + 15 * (steps - self.sedentary_threshold) / (self.minimum_steps - self.sedentary_threshold)
        else:
            return max(0, 10 * steps / self.sedentary_threshold)
    
    def _score_exercise_regularity(self, std: float, mean: float) -> float:
        """运动规律性评分（基于变异系数）"""
        if mean == 0:
            return 0.0
        
        cv = std / mean
        
        if cv < 0.3:
            return 25.0
        elif cv < 0.5:
            return 20.0
        elif cv < 0.7:
            return 15.0
        elif cv < 1.0:
            return 10.0
        else:
            return 5.0
    
    def detect_sedentary_patterns(
        self, 
        steps_data: List[Tuple[datetime, int]]
    ) -> Dict:
        """
        检测久坐模式
        
        Returns:
            久坐模式检测结果
        """
        patterns = {
            'consecutive_sedentary_days': 0,
            'sedentary_weeks': [],
            'trend': 'stable'
        }
        
        if len(steps_data) < 7:
            return patterns
        
        # 检测连续久坐天数
        consecutive = 0
        max_consecutive = 0
        
        for date, steps in steps_data:
            if steps < self.sedentary_threshold:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        patterns['consecutive_sedentary_days'] = max_consecutive
        
        # 检测趋势
        recent_steps = [s for _, s in steps_data[-7:]]
        earlier_steps = [s for _, s in steps_data[:7]] if len(steps_data) >= 14 else recent_steps
        
        if np.mean(recent_steps) < np.mean(earlier_steps) * 0.8:
            patterns['trend'] = 'decreasing'
        elif np.mean(recent_steps) > np.mean(earlier_steps) * 1.2:
            patterns['trend'] = 'increasing'
        
        return patterns


class DietAssessor:
    """饮食习惯评估器"""
    
    def __init__(self):
        # 饮食评分标准（基于简单自评）
        self.diet_categories = {
            'salt_intake': {'low': 30, 'medium': 20, 'high': 0},
            'oil_intake': {'low': 25, 'medium': 15, 'high': 0},
            'sugar_intake': {'low': 25, 'medium': 15, 'high': 0},
            'vegetable_intake': {'high': 20, 'medium': 10, 'low': 0}
        }
    
    def assess(self, diet_data: Dict) -> Tuple[float, LifestyleRiskLevel, Dict]:
        """
        评估饮食习惯
        
        Args:
            diet_data: 饮食数据 {
                'salt_intake': 'low'/'medium'/'high',
                'oil_intake': 'low'/'medium'/'high',
                'sugar_intake': 'low'/'medium'/'high',
                'vegetable_intake': 'low'/'medium'/'high'
            }
        
        Returns:
            (饮食评分, 风险等级, 详细信息)
        """
        score = 0.0
        details = {}
        issues = []
        
        # 盐分摄入评分
        salt_level = diet_data.get('salt_intake', 'medium')
        salt_score = self.diet_categories['salt_intake'].get(salt_level, 10)
        score += salt_score
        details['salt_score'] = salt_score
        
        if salt_level == 'high':
            issues.append("盐分摄入过多，增加高血压风险")
        
        # 油脂摄入评分
        oil_level = diet_data.get('oil_intake', 'medium')
        oil_score = self.diet_categories['oil_intake'].get(oil_level, 10)
        score += oil_score
        details['oil_score'] = oil_score
        
        if oil_level == 'high':
            issues.append("油脂摄入过多，增加血脂异常风险")
        
        # 糖分摄入评分
        sugar_level = diet_data.get('sugar_intake', 'medium')
        sugar_score = self.diet_categories['sugar_intake'].get(sugar_level, 10)
        score += sugar_score
        details['sugar_score'] = sugar_score
        
        if sugar_level == 'high':
            issues.append("糖分摄入过多，增加糖尿病风险")
        
        # 蔬菜摄入评分
        veg_level = diet_data.get('vegetable_intake', 'medium')
        veg_score = self.diet_categories['vegetable_intake'].get(veg_level, 10)
        score += veg_score
        details['vegetable_score'] = veg_score
        
        if veg_level == 'low':
            issues.append("蔬菜摄入不足，营养不均衡")
        
        # 确定风险等级
        if score >= 70:
            risk_level = LifestyleRiskLevel.LOW
        elif score >= 50:
            risk_level = LifestyleRiskLevel.MEDIUM
        else:
            risk_level = LifestyleRiskLevel.HIGH
        
        details['issues'] = issues
        
        return score, risk_level, details


class AnomalyDetector:
    """异常行为检测器（使用Isolation Forest）"""
    
    def __init__(self):
        self.model = None
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(contamination=0.1, random_state=42)
    
    def detect_anomalies(
        self, 
        lifestyle_features: np.ndarray
    ) -> Tuple[np.ndarray, List[int]]:
        """
        检测异常行为天数
        
        Args:
            lifestyle_features: 生活方式特征矩阵 (n_days, n_features)
        
        Returns:
            (预测结果, 异常天索引列表)
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            # 简化版本：基于统计方法
            return self._simple_anomaly_detection(lifestyle_features)
        
        predictions = self.model.fit_predict(lifestyle_features)
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        
        return predictions, anomaly_indices
    
    def _simple_anomaly_detection(
        self, 
        features: np.ndarray
    ) -> Tuple[np.ndarray, List[int]]:
        """简化的异常检测（基于Z-score）"""
        z_scores = np.abs((features - np.mean(features, axis=0)) / (np.std(features, axis=0) + 1e-6))
        
        # 任何特征的Z-score > 3 视为异常
        is_anomaly = np.any(z_scores > 3, axis=1)
        predictions = np.where(is_anomaly, -1, 1)
        anomaly_indices = np.where(is_anomaly)[0].tolist()
        
        return predictions, anomaly_indices


class LifestyleAssessmentEngine:
    """生活方式评估引擎"""
    
    def __init__(self):
        self.sleep_assessor = SleepQualityAssessor()
        self.exercise_assessor = ExerciseAssessor()
        self.diet_assessor = DietAssessor()
        self.anomaly_detector = AnomalyDetector()
        
        # 各维度权重
        self.weights = {
            'sleep': 0.35,
            'exercise': 0.35,
            'diet': 0.20,
            'regularity': 0.10
        }
    
    def assess(
        self,
        features: Dict,
        diet_data: Optional[Dict] = None,
        lifestyle_time_series: Optional[np.ndarray] = None
    ) -> LifestyleRiskResult:
        """
        综合评估生活方式风险
        
        Args:
            features: 特征字典
            diet_data: 饮食数据
            lifestyle_time_series: 生活方式时间序列数据（用于异常检测）
        
        Returns:
            生活方式风险评估结果
        """
        result = LifestyleRiskResult(
            overall_score=0.0,
            overall_risk_level=LifestyleRiskLevel.LOW
        )
        
        # 1. 睡眠评估
        sleep_score, sleep_risk, sleep_details = self.sleep_assessor.assess(features)
        result.sleep_score = sleep_score
        result.sleep_risk = sleep_risk
        result.sleep_details = sleep_details
        
        if sleep_details.get('issues'):
            result.key_issues.extend(sleep_details['issues'])
        
        # 2. 运动评估
        exercise_score, exercise_risk, exercise_details = self.exercise_assessor.assess(features)
        result.exercise_score = exercise_score
        result.exercise_risk = exercise_risk
        result.exercise_details = exercise_details
        
        if exercise_details.get('issues'):
            result.key_issues.extend(exercise_details['issues'])
        
        # 3. 饮食评估
        if diet_data:
            diet_score, diet_risk, diet_details = self.diet_assessor.assess(diet_data)
            result.diet_score = diet_score
            result.diet_risk = diet_risk
            result.diet_details = diet_details
            
            if diet_details.get('issues'):
                result.key_issues.extend(diet_details['issues'])
        else:
            result.diet_score = 60.0  # 默认中等
            result.diet_risk = LifestyleRiskLevel.MEDIUM
        
        # 4. 规律性评分
        regularity_score = features.get('sleep_regularity_score', 70)
        result.regularity_score = regularity_score
        
        # 5. 异常检测
        if lifestyle_time_series is not None:
            _, anomaly_indices = self.anomaly_detector.detect_anomalies(lifestyle_time_series)
            result.abnormal_days = [f"Day_{i}" for i in anomaly_indices]
            
            if len(anomaly_indices) > 5:
                result.key_issues.append(f"检测到{len(anomaly_indices)}天异常行为模式")
        
        # 6. 计算总体评分
        overall_score = (
            sleep_score * self.weights['sleep'] +
            exercise_score * self.weights['exercise'] +
            result.diet_score * self.weights['diet'] +
            regularity_score * self.weights['regularity']
        )
        result.overall_score = overall_score
        
        # 7. 确定总体风险等级
        if overall_score >= 70:
            result.overall_risk_level = LifestyleRiskLevel.LOW
        elif overall_score >= 50:
            result.overall_risk_level = LifestyleRiskLevel.MEDIUM
        else:
            result.overall_risk_level = LifestyleRiskLevel.HIGH
        
        return result


# 使用示例
if __name__ == "__main__":
    # 模拟特征数据
    features = {
        'sleep_duration_mean': 6.2,
        'sleep_duration_std': 1.8,
        'sleep_insufficient_days': 12,
        'sleep_regularity_score': 55,
        'steps_mean': 4500,
        'steps_std': 2000,
        'active_days_ratio': 0.45,
        'data_collection_days': 30
    }
    
    diet_data = {
        'salt_intake': 'high',
        'oil_intake': 'medium',
        'sugar_intake': 'medium',
        'vegetable_intake': 'low'
    }
    
    # 创建评估引擎
    engine = LifestyleAssessmentEngine()
    
    # 执行评估
    result = engine.assess(features, diet_data)
    
    print("生活方式风险评估结果:")
    print(f"总体评分: {result.overall_score:.1f}")
    print(f"总体风险: {result.overall_risk_level.value}")
    print(f"睡眠评分: {result.sleep_score:.1f} (风险: {result.sleep_risk.value})")
    print(f"运动评分: {result.exercise_score:.1f} (风险: {result.exercise_risk.value})")
    print(f"饮食评分: {result.diet_score:.1f} (风险: {result.diet_risk.value})")
    print(f"\n关键问题:")
    for issue in result.key_issues:
        print(f"  - {issue}")
