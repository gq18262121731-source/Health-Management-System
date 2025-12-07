"""
健康评估服务适配层
==================

将健康评估算法模块与 Health-Management-System 现有系统对接。
提供简化的接口供 API 路由和多智能体系统调用。
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID

# 评估算法模块
from .disease_assessment import (
    HypertensionAssessor,
    DiabetesAssessor,
    DyslipidemiAssessor,
    DiseaseRiskResult,
    RiskLevel
)
from .lifestyle_assessment import LifestyleAssessmentEngine, LifestyleRiskResult
from .comprehensive_assessment import (
    RiskFusionEngine,
    ComprehensiveAssessmentResult,
    HealthLevel,
    AHPWeightCalculator,
    TOPSISRanker
)
from .trend_alert import HealthTrendAnalyzer, TrendAlert, AlertLevel

logger = logging.getLogger(__name__)


class HealthAssessmentService:
    """
    健康评估服务
    
    整合所有评估算法，提供统一的评估接口。
    与现有的 Health-Management-System 数据模型对接。
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 初始化评估器
        self.ht_assessor = HypertensionAssessor()
        self.dm_assessor = DiabetesAssessor()
        self.dl_assessor = DyslipidemiAssessor()
        self.lifestyle_engine = LifestyleAssessmentEngine()
        self.fusion_engine = RiskFusionEngine()
        self.trend_analyzer = HealthTrendAnalyzer()
        self.ahp_calculator = AHPWeightCalculator()
        
        self._initialized = True
        logger.info("健康评估服务初始化完成")
    
    def assess_blood_pressure(
        self,
        systolic_values: List[float],
        diastolic_values: List[float],
        baseline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        评估血压风险
        
        Args:
            systolic_values: 收缩压数据列表
            diastolic_values: 舒张压数据列表
            baseline: 基线数据（可选）
        
        Returns:
            评估结果字典
        """
        try:
            # 构建特征
            features = {
                'sbp_mean': sum(systolic_values) / len(systolic_values) if systolic_values else 0,
                'sbp_max': max(systolic_values) if systolic_values else 0,
                'sbp_min': min(systolic_values) if systolic_values else 0,
                'sbp_std': self._calculate_std(systolic_values),
                'dbp_mean': sum(diastolic_values) / len(diastolic_values) if diastolic_values else 0,
                'dbp_max': max(diastolic_values) if diastolic_values else 0,
                'dbp_min': min(diastolic_values) if diastolic_values else 0,
                'dbp_std': self._calculate_std(diastolic_values),
                'measurement_count': len(systolic_values),
            }
            
            # 计算达标率
            compliance_count = sum(
                1 for s, d in zip(systolic_values, diastolic_values)
                if s < 140 and d < 90
            )
            features['compliance_rate'] = compliance_count / len(systolic_values) if systolic_values else 0
            
            # 调用评估器
            result = self.ht_assessor.assess(features, baseline)
            
            return {
                'disease_name': result.disease_name,
                'risk_level': result.risk_level.value,
                'risk_score': result.risk_score,
                'control_status': result.control_status.value,
                'control_quality_score': result.control_quality_score,
                'compliance_rate': result.compliance_rate,
                'key_findings': result.key_findings,
                'metric_grades': result.metric_grades,
                'details': result.details
            }
        except Exception as e:
            logger.error(f"血压评估失败: {e}")
            return self._get_default_result('高血压')
    
    def assess_blood_sugar(
        self,
        fasting_values: List[float],
        postprandial_values: Optional[List[float]] = None,
        baseline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        评估血糖风险
        
        Args:
            fasting_values: 空腹血糖数据列表
            postprandial_values: 餐后血糖数据列表（可选）
            baseline: 基线数据（可选）
        
        Returns:
            评估结果字典
        """
        try:
            # 构建特征
            features = {
                'fasting_mean': sum(fasting_values) / len(fasting_values) if fasting_values else 0,
                'fasting_max': max(fasting_values) if fasting_values else 0,
                'fasting_min': min(fasting_values) if fasting_values else 0,
                'fasting_std': self._calculate_std(fasting_values),
                'measurement_count': len(fasting_values),
            }
            
            if postprandial_values:
                features['postprandial_mean'] = sum(postprandial_values) / len(postprandial_values)
                features['postprandial_max'] = max(postprandial_values)
            
            # 计算达标率
            compliance_count = sum(1 for v in fasting_values if 3.9 <= v <= 7.0)
            features['compliance_rate'] = compliance_count / len(fasting_values) if fasting_values else 0
            
            # 调用评估器
            result = self.dm_assessor.assess(features, baseline)
            
            return {
                'disease_name': result.disease_name,
                'risk_level': result.risk_level.value,
                'risk_score': result.risk_score,
                'control_status': result.control_status.value,
                'control_quality_score': result.control_quality_score,
                'compliance_rate': result.compliance_rate,
                'key_findings': result.key_findings,
                'metric_grades': result.metric_grades,
                'details': result.details
            }
        except Exception as e:
            logger.error(f"血糖评估失败: {e}")
            return self._get_default_result('糖尿病')
    
    def assess_lifestyle(
        self,
        sleep_data: Optional[Dict] = None,
        exercise_data: Optional[Dict] = None,
        diet_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        评估生活方式风险
        
        Args:
            sleep_data: 睡眠数据 {duration_hours: float, quality_score: int, ...}
            exercise_data: 运动数据 {steps: int, duration_minutes: int, ...}
            diet_data: 饮食数据 {meals_per_day: int, salt_intake: str, ...}
        
        Returns:
            评估结果字典
        """
        try:
            # 构建特征
            features = {}
            
            if sleep_data:
                features['sleep_duration_mean'] = sleep_data.get('duration_hours', 7)
                features['sleep_quality_score'] = sleep_data.get('quality_score', 70)
                features['sleep_regularity'] = sleep_data.get('regularity', 0.8)
            
            if exercise_data:
                features['daily_steps_mean'] = exercise_data.get('steps', 5000)
                features['exercise_duration_mean'] = exercise_data.get('duration_minutes', 30)
                features['exercise_frequency'] = exercise_data.get('frequency_per_week', 3)
            
            if diet_data:
                features['meals_regularity'] = diet_data.get('regularity', 0.8)
                features['salt_intake_level'] = diet_data.get('salt_level', 'medium')
                features['vegetable_intake'] = diet_data.get('vegetable_servings', 3)
            
            # 调用评估器
            result = self.lifestyle_engine.assess(features)
            
            return {
                'overall_score': result.overall_score,
                'risk_level': result.risk_level.value,
                'sleep_score': result.sleep_score,
                'exercise_score': result.exercise_score,
                'diet_score': result.diet_score,
                'key_findings': result.key_findings,
                'recommendations': result.recommendations,
                'details': result.details
            }
        except Exception as e:
            logger.error(f"生活方式评估失败: {e}")
            return {
                'overall_score': 70,
                'risk_level': 'medium',
                'sleep_score': 70,
                'exercise_score': 70,
                'diet_score': 70,
                'key_findings': [],
                'recommendations': [],
                'details': {}
            }
    
    def analyze_trend(
        self,
        metric_name: str,
        values: List[float],
        timestamps: Optional[List[datetime]] = None
    ) -> Dict[str, Any]:
        """
        分析健康指标趋势
        
        Args:
            metric_name: 指标名称 (systolic_bp, diastolic_bp, blood_sugar, heart_rate)
            values: 数值列表
            timestamps: 时间戳列表（可选）
        
        Returns:
            趋势分析结果
        """
        try:
            if not values or len(values) < 3:
                return {
                    'metric_name': metric_name,
                    'alert_level': 'normal',
                    'trend_direction': 'stable',
                    'message': '数据不足，无法分析趋势',
                    'suggestion': '请继续记录健康数据'
                }
            
            # 调用趋势分析器
            alert = self.trend_analyzer.analyze_metric(metric_name, values, timestamps)
            
            return {
                'metric_name': alert.metric_name,
                'alert_level': alert.alert_level.value,
                'trend_direction': alert.trend_direction.value,
                'message': alert.message,
                'suggestion': alert.suggestion,
                'current_value': alert.current_value,
                'avg_value': alert.avg_value,
                'trend_slope': alert.trend_slope,
                'volatility': alert.volatility,
                'consecutive_abnormal': alert.consecutive_abnormal
            }
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {
                'metric_name': metric_name,
                'alert_level': 'normal',
                'trend_direction': 'stable',
                'message': '分析过程出现错误',
                'suggestion': '请稍后重试'
            }
    
    def comprehensive_assessment(
        self,
        health_data: Dict[str, Any],
        baseline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        综合健康评估
        
        Args:
            health_data: 健康数据字典，包含：
                - blood_pressure: {systolic: [], diastolic: []}
                - blood_sugar: {fasting: [], postprandial: []}
                - lifestyle: {sleep: {}, exercise: {}, diet: {}}
            baseline: 基线数据
        
        Returns:
            综合评估结果
        """
        try:
            results = {}
            
            # 1. 疾病风险评估
            bp_data = health_data.get('blood_pressure', {})
            if bp_data.get('systolic') and bp_data.get('diastolic'):
                results['hypertension'] = self.assess_blood_pressure(
                    bp_data['systolic'],
                    bp_data['diastolic'],
                    baseline
                )
            
            bs_data = health_data.get('blood_sugar', {})
            if bs_data.get('fasting'):
                results['diabetes'] = self.assess_blood_sugar(
                    bs_data['fasting'],
                    bs_data.get('postprandial'),
                    baseline
                )
            
            # 2. 生活方式评估
            lifestyle_data = health_data.get('lifestyle', {})
            if lifestyle_data:
                results['lifestyle'] = self.assess_lifestyle(
                    lifestyle_data.get('sleep'),
                    lifestyle_data.get('exercise'),
                    lifestyle_data.get('diet')
                )
            
            # 3. 趋势分析
            trend_results = {}
            if bp_data.get('systolic'):
                trend_results['systolic_bp'] = self.analyze_trend('systolic_bp', bp_data['systolic'])
            if bs_data.get('fasting'):
                trend_results['blood_sugar'] = self.analyze_trend('blood_sugar', bs_data['fasting'])
            results['trends'] = trend_results
            
            # 4. 综合评分（使用AHP权重）
            overall_score = self._calculate_overall_score(results)
            health_level = self._determine_health_level(overall_score)
            
            # 5. 提取TOP风险因素
            top_risks = self._extract_top_risks(results)
            
            return {
                'overall_score': overall_score,
                'health_level': health_level,
                'disease_results': {
                    'hypertension': results.get('hypertension'),
                    'diabetes': results.get('diabetes')
                },
                'lifestyle_result': results.get('lifestyle'),
                'trend_results': results.get('trends'),
                'top_risk_factors': top_risks,
                'recommendations': self._generate_recommendations(results),
                'assessment_time': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"综合评估失败: {e}")
            return {
                'overall_score': 70,
                'health_level': 'suboptimal',
                'error': str(e)
            }
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if not values or len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """计算综合评分（使用AHP权重）"""
        weights = self.ahp_calculator.default_weights
        
        scores = []
        total_weight = 0
        
        # 疾病风险评分
        if results.get('hypertension'):
            # 风险分数越高，健康分数越低
            ht_health_score = 100 - results['hypertension'].get('risk_score', 50)
            scores.append(ht_health_score * weights.get('disease_risk', 0.45) * 0.5)
            total_weight += weights.get('disease_risk', 0.45) * 0.5
        
        if results.get('diabetes'):
            dm_health_score = 100 - results['diabetes'].get('risk_score', 50)
            scores.append(dm_health_score * weights.get('disease_risk', 0.45) * 0.5)
            total_weight += weights.get('disease_risk', 0.45) * 0.5
        
        # 生活方式评分
        if results.get('lifestyle'):
            lifestyle_score = results['lifestyle'].get('overall_score', 70)
            scores.append(lifestyle_score * weights.get('lifestyle_risk', 0.30))
            total_weight += weights.get('lifestyle_risk', 0.30)
        
        # 趋势评分
        trend_score = self._calculate_trend_score(results.get('trends', {}))
        scores.append(trend_score * weights.get('trend_risk', 0.25))
        total_weight += weights.get('trend_risk', 0.25)
        
        if total_weight > 0:
            return sum(scores) / total_weight
        return 70.0
    
    def _calculate_trend_score(self, trends: Dict) -> float:
        """计算趋势评分"""
        if not trends:
            return 80.0
        
        scores = []
        for metric, trend in trends.items():
            alert_level = trend.get('alert_level', 'normal')
            if alert_level == 'normal':
                scores.append(90)
            elif alert_level == 'attention':
                scores.append(70)
            elif alert_level == 'warning':
                scores.append(50)
            else:  # critical
                scores.append(30)
        
        return sum(scores) / len(scores) if scores else 80.0
    
    def _determine_health_level(self, score: float) -> str:
        """确定健康等级"""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 55:
            return 'suboptimal'
        elif score >= 40:
            return 'attention_needed'
        else:
            return 'high_risk'
    
    def _extract_top_risks(self, results: Dict, top_n: int = 3) -> List[Dict]:
        """提取TOP风险因素"""
        risks = []
        
        # 从疾病评估中提取
        for disease in ['hypertension', 'diabetes']:
            if results.get(disease):
                risk_level = results[disease].get('risk_level', 'low')
                if risk_level in ['high', 'very_high']:
                    risks.append({
                        'category': 'disease',
                        'name': results[disease].get('disease_name', disease),
                        'risk_level': risk_level,
                        'findings': results[disease].get('key_findings', [])[:2]
                    })
        
        # 从趋势中提取
        for metric, trend in results.get('trends', {}).items():
            if trend.get('alert_level') in ['warning', 'critical']:
                risks.append({
                    'category': 'trend',
                    'name': trend.get('metric_name', metric),
                    'risk_level': trend.get('alert_level'),
                    'message': trend.get('message')
                })
        
        # 按风险等级排序
        risk_order = {'critical': 0, 'very_high': 1, 'high': 2, 'warning': 3}
        risks.sort(key=lambda x: risk_order.get(x.get('risk_level', 'low'), 4))
        
        return risks[:top_n]
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 基于疾病风险的建议
        if results.get('hypertension'):
            ht = results['hypertension']
            if ht.get('risk_level') in ['high', 'very_high']:
                recommendations.append("血压控制需要加强，建议每日监测并记录血压")
                recommendations.append("减少盐分摄入，每日不超过5克")
        
        if results.get('diabetes'):
            dm = results['diabetes']
            if dm.get('risk_level') in ['high', 'very_high']:
                recommendations.append("血糖波动较大，建议规律监测空腹和餐后血糖")
                recommendations.append("控制碳水化合物摄入，增加膳食纤维")
        
        # 基于生活方式的建议
        if results.get('lifestyle'):
            ls = results['lifestyle']
            if ls.get('sleep_score', 100) < 60:
                recommendations.append("睡眠质量需要改善，建议保持规律作息")
            if ls.get('exercise_score', 100) < 60:
                recommendations.append("运动量不足，建议每天步行6000步以上")
        
        # 基于趋势的建议
        for metric, trend in results.get('trends', {}).items():
            if trend.get('alert_level') == 'warning':
                recommendations.append(trend.get('suggestion', ''))
        
        return [r for r in recommendations if r][:5]
    
    def _get_default_result(self, disease_name: str) -> Dict[str, Any]:
        """获取默认评估结果"""
        return {
            'disease_name': disease_name,
            'risk_level': 'medium',
            'risk_score': 50,
            'control_status': 'fair',
            'control_quality_score': 60,
            'compliance_rate': 0.5,
            'key_findings': ['数据不足，无法进行完整评估'],
            'metric_grades': {},
            'details': {}
        }


# 创建全局服务实例
health_assessment_service = HealthAssessmentService()
