"""
模块5：综合健康风险评估与分层分级子模块
Comprehensive Health Risk Assessment and Stratification Module

功能：
- 多维度风险融合
- 综合健康评分计算
- 风险分层分级
- TOP风险点提取

算法分配：
- AHP（层次分析法）：权重确定
- TOPSIS：多准则决策排序
- Stacking集成学习（可选）：模型融合
- SHAP：可解释性分析
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 尝试导入可选依赖
try:
    from sklearn.ensemble import StackingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class HealthLevel(Enum):
    """健康等级"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"  # 良好
    SUBOPTIMAL = "suboptimal"  # 亚健康
    ATTENTION_NEEDED = "attention_needed"  # 需重点关注
    HIGH_RISK = "high_risk"  # 高风险


class RiskPriority(Enum):
    """风险优先级"""
    CRITICAL = "critical"  # 紧急
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低


@dataclass
class RiskFactor:
    """风险因素"""
    category: str  # 类别：disease/lifestyle/trend
    name: str  # 名称
    risk_score: float  # 风险评分 0-100
    severity: float  # 严重程度 0-1
    urgency: float  # 紧迫性 0-1
    controllability: float  # 可控性 0-1
    priority: RiskPriority  # 优先级
    description: str  # 描述
    evidence: List[str] = field(default_factory=list)  # 依据
    
    def to_dict(self) -> Dict:
        return {
            'category': self.category,
            'name': self.name,
            'risk_score': self.risk_score,
            'severity': self.severity,
            'urgency': self.urgency,
            'controllability': self.controllability,
            'priority': self.priority.value,
            'description': self.description,
            'evidence': self.evidence
        }


@dataclass
class ComprehensiveAssessmentResult:
    """综合评估结果"""
    user_id: str
    assessment_id: str
    assessment_date: datetime
    
    # 综合评分与等级
    overall_score: float = 0.0  # 0-100
    health_level: HealthLevel = HealthLevel.SUBOPTIMAL
    
    # 各维度评分
    disease_risk_score: float = 0.0
    lifestyle_risk_score: float = 0.0
    trend_risk_score: float = 0.0
    
    # TOP风险因素
    top_risk_factors: List[RiskFactor] = field(default_factory=list)
    
    # 分维度详细结果
    disease_results: Dict = field(default_factory=dict)
    lifestyle_result: Dict = field(default_factory=dict)
    trend_results: Dict = field(default_factory=dict)
    
    # 优先关注建议
    priority_recommendations: List[str] = field(default_factory=list)
    
    # 可解释性信息
    feature_importance: Dict = field(default_factory=dict)
    risk_distribution: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'assessment_id': self.assessment_id,
            'assessment_date': self.assessment_date.isoformat(),
            'overall_score': self.overall_score,
            'health_level': self.health_level.value,
            'disease_risk_score': self.disease_risk_score,
            'lifestyle_risk_score': self.lifestyle_risk_score,
            'trend_risk_score': self.trend_risk_score,
            'top_risk_factors': [rf.to_dict() for rf in self.top_risk_factors],
            'disease_results': self.disease_results,
            'lifestyle_result': self.lifestyle_result,
            'trend_results': self.trend_results,
            'priority_recommendations': self.priority_recommendations,
            'feature_importance': self.feature_importance,
            'risk_distribution': self.risk_distribution
        }


class AHPWeightCalculator:
    """AHP层次分析法权重计算器"""
    
    def __init__(self):
        # 默认权重配置（可根据专家意见调整）
        self.default_weights = {
            'disease_risk': 0.45,
            'lifestyle_risk': 0.30,
            'trend_risk': 0.25
        }
        
        # 疾病内部权重
        self.disease_weights = {
            'hypertension': 0.40,
            'diabetes': 0.35,
            'dyslipidemia': 0.25
        }
        
        # 生活方式内部权重
        self.lifestyle_weights = {
            'sleep': 0.35,
            'exercise': 0.35,
            'diet': 0.20,
            'regularity': 0.10
        }
    
    def calculate_weights(
        self, 
        comparison_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        计算权重
        
        Args:
            comparison_matrix: 成对比较矩阵（可选）
        
        Returns:
            权重字典
        """
        if comparison_matrix is not None:
            # 使用特征值法计算权重
            eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
            max_eigenvalue_index = np.argmax(eigenvalues)
            weights_vector = eigenvectors[:, max_eigenvalue_index].real
            weights_vector = weights_vector / np.sum(weights_vector)
            
            return {
                'disease_risk': weights_vector[0],
                'lifestyle_risk': weights_vector[1],
                'trend_risk': weights_vector[2]
            }
        else:
            return self.default_weights
    
    def check_consistency(self, comparison_matrix: np.ndarray) -> float:
        """
        检查一致性比率（CR）
        
        CR < 0.1 表示一致性可接受
        """
        n = comparison_matrix.shape[0]
        eigenvalues = np.linalg.eigvals(comparison_matrix)
        lambda_max = np.max(eigenvalues.real)
        
        # 一致性指标
        ci = (lambda_max - n) / (n - 1)
        
        # 随机一致性指标（查表）
        ri_table = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
        ri = ri_table.get(n, 1.49)
        
        # 一致性比率
        cr = ci / ri if ri > 0 else 0
        
        return cr


class TOPSISRanker:
    """TOPSIS多准则决策排序器"""
    
    def __init__(self):
        # 准则权重
        self.criteria_weights = {
            'severity': 0.35,      # 严重程度
            'urgency': 0.30,       # 紧迫性
            'frequency': 0.20,     # 频率
            'trend': 0.15          # 趋势
        }
    
    def rank_risk_factors(
        self, 
        risk_factors: List[Dict]
    ) -> List[RiskFactor]:
        """
        对风险因素进行排序
        
        Args:
            risk_factors: 风险因素列表
        
        Returns:
            排序后的风险因素列表
        """
        if not risk_factors:
            return []
        
        # 构建决策矩阵
        n = len(risk_factors)
        m = 4  # 4个准则
        decision_matrix = np.zeros((n, m))
        
        for i, rf in enumerate(risk_factors):
            decision_matrix[i, 0] = rf.get('severity', 0.5)
            decision_matrix[i, 1] = rf.get('urgency', 0.5)
            decision_matrix[i, 2] = rf.get('frequency', 0.5)
            decision_matrix[i, 3] = rf.get('trend_score', 0.5)
        
        # 归一化决策矩阵
        normalized_matrix = self._normalize_matrix(decision_matrix)
        
        # 加权归一化矩阵
        weights = np.array([
            self.criteria_weights['severity'],
            self.criteria_weights['urgency'],
            self.criteria_weights['frequency'],
            self.criteria_weights['trend']
        ])
        weighted_matrix = normalized_matrix * weights
        
        # 确定理想解和负理想解
        ideal_best = np.max(weighted_matrix, axis=0)
        ideal_worst = np.min(weighted_matrix, axis=0)
        
        # 计算距离
        distances_to_best = np.sqrt(np.sum((weighted_matrix - ideal_best) ** 2, axis=1))
        distances_to_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst) ** 2, axis=1))
        
        # 计算相对接近度
        closeness = distances_to_worst / (distances_to_best + distances_to_worst + 1e-10)
        
        # 排序
        ranked_indices = np.argsort(closeness)[::-1]
        
        # 构建排序后的风险因素列表
        ranked_factors = []
        for idx in ranked_indices:
            rf_dict = risk_factors[idx]
            
            # 确定优先级
            if closeness[idx] >= 0.7:
                priority = RiskPriority.CRITICAL
            elif closeness[idx] >= 0.5:
                priority = RiskPriority.HIGH
            elif closeness[idx] >= 0.3:
                priority = RiskPriority.MEDIUM
            else:
                priority = RiskPriority.LOW
            
            risk_factor = RiskFactor(
                category=rf_dict.get('category', 'unknown'),
                name=rf_dict.get('name', ''),
                risk_score=rf_dict.get('risk_score', 0),
                severity=rf_dict.get('severity', 0.5),
                urgency=rf_dict.get('urgency', 0.5),
                controllability=rf_dict.get('controllability', 0.5),
                priority=priority,
                description=rf_dict.get('description', ''),
                evidence=rf_dict.get('evidence', [])
            )
            ranked_factors.append(risk_factor)
        
        return ranked_factors
    
    def _normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """归一化决策矩阵（向量归一化）"""
        norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        norms[norms == 0] = 1  # 避免除零
        return matrix / norms


class RiskFusionEngine:
    """风险融合引擎"""
    
    def __init__(self):
        self.ahp_calculator = AHPWeightCalculator()
        self.topsis_ranker = TOPSISRanker()
        self.weights = self.ahp_calculator.default_weights
    
    def fuse_risks(
        self,
        disease_results: Dict,
        lifestyle_result: Dict,
        trend_results: Dict,
        user_id: str,
        assessment_id: str
    ) -> ComprehensiveAssessmentResult:
        """
        融合多维度风险
        
        Args:
            disease_results: 单病种评估结果
            lifestyle_result: 生活方式评估结果
            trend_results: 趋势分析结果
            user_id: 用户ID
            assessment_id: 评估ID
        
        Returns:
            综合评估结果
        """
        result = ComprehensiveAssessmentResult(
            user_id=user_id,
            assessment_id=assessment_id,
            assessment_date=datetime.now()
        )
        
        # 1. 计算各维度风险评分
        disease_score = self._calculate_disease_risk_score(disease_results)
        lifestyle_score = self._calculate_lifestyle_risk_score(lifestyle_result)
        trend_score = self._calculate_trend_risk_score(trend_results)
        
        result.disease_risk_score = disease_score
        result.lifestyle_risk_score = lifestyle_score
        result.trend_risk_score = trend_score
        
        # 2. 加权融合计算综合评分
        # 注意：这里的评分是"健康评分"，越高越好
        # 需要将风险评分转换为健康评分
        disease_health_score = 100 - disease_score
        lifestyle_health_score = lifestyle_result.get('overall_score', 60)
        trend_health_score = 100 - trend_score
        
        overall_score = (
            disease_health_score * self.weights['disease_risk'] +
            lifestyle_health_score * self.weights['lifestyle_risk'] +
            trend_health_score * self.weights['trend_risk']
        )
        result.overall_score = overall_score
        
        # 3. 确定健康等级
        result.health_level = self._determine_health_level(overall_score)
        
        # 4. 提取所有风险因素
        all_risk_factors = self._extract_all_risk_factors(
            disease_results, 
            lifestyle_result, 
            trend_results
        )
        
        # 5. 使用TOPSIS排序风险因素
        ranked_factors = self.topsis_ranker.rank_risk_factors(all_risk_factors)
        
        # 6. 提取TOP 3风险因素
        result.top_risk_factors = ranked_factors[:3]
        
        # 7. 生成优先关注建议
        result.priority_recommendations = self._generate_recommendations(
            result.top_risk_factors,
            result.health_level
        )
        
        # 8. 计算特征重要性
        result.feature_importance = self._calculate_feature_importance(
            disease_results,
            lifestyle_result,
            trend_results
        )
        
        # 9. 风险分布
        result.risk_distribution = self._calculate_risk_distribution(ranked_factors)
        
        # 10. 保存详细结果
        result.disease_results = disease_results
        result.lifestyle_result = lifestyle_result
        result.trend_results = trend_results
        
        return result
    
    def _calculate_disease_risk_score(self, disease_results: Dict) -> float:
        """计算疾病维度风险评分"""
        if not disease_results:
            return 0.0
        
        disease_weights = self.ahp_calculator.disease_weights
        total_score = 0.0
        total_weight = 0.0
        
        for disease_name, result in disease_results.items():
            weight = disease_weights.get(disease_name, 0.33)
            risk_score = result.get('risk_score', 0)
            total_score += risk_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_lifestyle_risk_score(self, lifestyle_result: Dict) -> float:
        """计算生活方式风险评分（转换为风险分）"""
        overall_score = lifestyle_result.get('overall_score', 60)
        # 将健康评分转换为风险评分
        return 100 - overall_score
    
    def _calculate_trend_risk_score(self, trend_results: Dict) -> float:
        """计算趋势风险评分"""
        if not trend_results:
            return 0.0
        
        risk_scores = []
        for metric_name, trend_data in trend_results.items():
            # 基于趋势方向和偏离程度计算风险
            trend_direction = trend_data.get('trend_direction', 'stable')
            deviation = abs(trend_data.get('deviation_from_baseline', 0))
            
            if trend_direction == 'worsening':
                risk_score = min(50 + deviation * 10, 100)
            elif trend_direction == 'improving':
                risk_score = max(20 - deviation * 5, 0)
            else:  # stable
                risk_score = 30
            
            risk_scores.append(risk_score)
        
        return np.mean(risk_scores) if risk_scores else 0.0
    
    def _determine_health_level(self, overall_score: float) -> HealthLevel:
        """确定健康等级"""
        if overall_score >= 85:
            return HealthLevel.EXCELLENT
        elif overall_score >= 70:
            return HealthLevel.GOOD
        elif overall_score >= 55:
            return HealthLevel.SUBOPTIMAL
        elif overall_score >= 40:
            return HealthLevel.ATTENTION_NEEDED
        else:
            return HealthLevel.HIGH_RISK
    
    def _extract_all_risk_factors(
        self,
        disease_results: Dict,
        lifestyle_result: Dict,
        trend_results: Dict
    ) -> List[Dict]:
        """提取所有风险因素"""
        risk_factors = []
        
        # 提取疾病风险因素
        for disease_name, result in disease_results.items():
            if result.get('risk_score', 0) > 30:  # 只关注中等以上风险
                risk_factors.append({
                    'category': 'disease',
                    'name': disease_name,
                    'risk_score': result.get('risk_score', 0),
                    'severity': result.get('risk_score', 0) / 100,
                    'urgency': 1 - result.get('compliance_rate', 0.5),
                    'frequency': 1 - result.get('compliance_rate', 0.5),
                    'trend_score': 0.5,
                    'controllability': 0.7,
                    'description': f"{disease_name}风险",
                    'evidence': result.get('key_findings', [])
                })
        
        # 提取生活方式风险因素
        if lifestyle_result.get('sleep_risk') in ['medium', 'high']:
            risk_factors.append({
                'category': 'lifestyle',
                'name': '睡眠质量',
                'risk_score': 100 - lifestyle_result.get('sleep_score', 60),
                'severity': (100 - lifestyle_result.get('sleep_score', 60)) / 100,
                'urgency': 0.6,
                'frequency': 0.7,
                'trend_score': 0.5,
                'controllability': 0.8,
                'description': '睡眠质量不佳',
                'evidence': lifestyle_result.get('sleep_details', {}).get('issues', [])
            })
        
        if lifestyle_result.get('exercise_risk') in ['medium', 'high']:
            risk_factors.append({
                'category': 'lifestyle',
                'name': '运动不足',
                'risk_score': 100 - lifestyle_result.get('exercise_score', 60),
                'severity': (100 - lifestyle_result.get('exercise_score', 60)) / 100,
                'urgency': 0.5,
                'frequency': 0.8,
                'trend_score': 0.5,
                'controllability': 0.9,
                'description': '运动量不足',
                'evidence': lifestyle_result.get('exercise_details', {}).get('issues', [])
            })
        
        if lifestyle_result.get('diet_risk') in ['medium', 'high']:
            risk_factors.append({
                'category': 'lifestyle',
                'name': '饮食不合理',
                'risk_score': 100 - lifestyle_result.get('diet_score', 60),
                'severity': (100 - lifestyle_result.get('diet_score', 60)) / 100,
                'urgency': 0.4,
                'frequency': 0.9,
                'trend_score': 0.5,
                'controllability': 0.85,
                'description': '饮食习惯不健康',
                'evidence': lifestyle_result.get('diet_details', {}).get('issues', [])
            })
        
        # 提取趋势风险因素
        for metric_name, trend_data in trend_results.items():
            if trend_data.get('trend_direction') == 'worsening':
                risk_factors.append({
                    'category': 'trend',
                    'name': f"{metric_name}恶化趋势",
                    'risk_score': 60,
                    'severity': 0.6,
                    'urgency': 0.7,
                    'frequency': 0.5,
                    'trend_score': 0.8,
                    'controllability': 0.6,
                    'description': f"{metric_name}呈恶化趋势",
                    'evidence': [f"相比基线偏离{trend_data.get('deviation_from_baseline', 0):.1f}"]
                })
        
        return risk_factors
    
    def _generate_recommendations(
        self,
        top_risk_factors: List[RiskFactor],
        health_level: HealthLevel
    ) -> List[str]:
        """生成优先关注建议"""
        recommendations = []
        
        for rf in top_risk_factors:
            if rf.category == 'disease':
                if '高血压' in rf.name:
                    recommendations.append("建议加强血压监测，规律服药，减少盐分摄入")
                elif '糖' in rf.name:
                    recommendations.append("建议控制饮食，增加运动，定期监测血糖")
                elif '血脂' in rf.name:
                    recommendations.append("建议低脂饮食，适量运动，必要时药物治疗")
            
            elif rf.category == 'lifestyle':
                if '睡眠' in rf.name:
                    recommendations.append("建议改善睡眠习惯，保持规律作息，每晚7-8小时睡眠")
                elif '运动' in rf.name:
                    recommendations.append("建议增加日常活动量，每天至少6000步，每周150分钟中等强度运动")
                elif '饮食' in rf.name:
                    recommendations.append("建议调整饮食结构，减少高盐高油高糖食物，增加蔬菜水果")
            
            elif rf.category == 'trend':
                recommendations.append(f"建议密切关注{rf.name}，及时就医咨询")
        
        # 根据健康等级添加总体建议
        if health_level == HealthLevel.HIGH_RISK:
            recommendations.insert(0, "健康状况需要紧急关注，建议尽快就医")
        elif health_level == HealthLevel.ATTENTION_NEEDED:
            recommendations.insert(0, "健康状况需要重点关注，建议定期复查")
        
        return recommendations[:5]  # 最多返回5条建议
    
    def _calculate_feature_importance(
        self,
        disease_results: Dict,
        lifestyle_result: Dict,
        trend_results: Dict
    ) -> Dict[str, float]:
        """计算特征重要性（简化版SHAP思想）"""
        importance = {}
        
        # 疾病维度
        for disease_name, result in disease_results.items():
            risk_score = result.get('risk_score', 0)
            importance[disease_name] = risk_score * self.weights['disease_risk']
        
        # 生活方式维度
        lifestyle_risk = 100 - lifestyle_result.get('overall_score', 60)
        importance['lifestyle'] = lifestyle_risk * self.weights['lifestyle_risk']
        
        # 趋势维度
        for metric_name, trend_data in trend_results.items():
            if trend_data.get('trend_direction') == 'worsening':
                importance[f"{metric_name}_trend"] = 50 * self.weights['trend_risk']
        
        # 归一化
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        
        return importance
    
    def _calculate_risk_distribution(
        self,
        risk_factors: List[RiskFactor]
    ) -> Dict:
        """计算风险分布"""
        distribution = {
            'by_category': {'disease': 0, 'lifestyle': 0, 'trend': 0},
            'by_priority': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'total_count': len(risk_factors)
        }
        
        for rf in risk_factors:
            distribution['by_category'][rf.category] += 1
            distribution['by_priority'][rf.priority.value] += 1
        
        return distribution


# 使用示例
if __name__ == "__main__":
    # 模拟输入数据
    disease_results = {
        'hypertension': {
            'risk_score': 65,
            'compliance_rate': 0.6,
            'key_findings': ['血压控制不佳', '波动明显']
        },
        'diabetes': {
            'risk_score': 45,
            'compliance_rate': 0.75,
            'key_findings': ['血糖偏高']
        }
    }
    
    lifestyle_result = {
        'overall_score': 55,
        'sleep_score': 50,
        'exercise_score': 45,
        'diet_score': 60,
        'sleep_risk': 'high',
        'exercise_risk': 'high',
        'diet_risk': 'medium',
        'sleep_details': {'issues': ['睡眠不足']},
        'exercise_details': {'issues': ['运动量偏低']}
    }
    
    trend_results = {
        'sbp': {
            'trend_direction': 'worsening',
            'deviation_from_baseline': 8.5
        }
    }
    
    # 创建融合引擎
    fusion_engine = RiskFusionEngine()
    
    # 执行综合评估
    result = fusion_engine.fuse_risks(
        disease_results=disease_results,
        lifestyle_result=lifestyle_result,
        trend_results=trend_results,
        user_id='USER001',
        assessment_id='ASSESS_001'
    )
    
    print("综合健康评估结果:")
    print(f"综合评分: {result.overall_score:.1f}")
    print(f"健康等级: {result.health_level.value}")
    print(f"\nTOP风险因素:")
    for i, rf in enumerate(result.top_risk_factors, 1):
        print(f"{i}. {rf.name} (优先级: {rf.priority.value}, 评分: {rf.risk_score:.1f})")
    print(f"\n优先建议:")
    for rec in result.priority_recommendations:
        print(f"  - {rec}")
