"""
健康评估算法模块
================

整合自 health_assessment_system，提供专业的健康风险评估算法：
- 单病种风险评估（高血压、糖尿病、血脂异常）
- 生活方式评估（睡眠、运动、饮食）
- 综合风险融合（AHP + TOPSIS）
- 趋势预警分析
"""

from .assessment_engine import HealthAssessmentEngine
from .disease_assessment import (
    HypertensionAssessor, 
    DiabetesAssessor, 
    DyslipidemiAssessor,
    DiseaseRiskResult,
    RiskLevel,
    ControlStatus
)
from .lifestyle_assessment import (
    LifestyleAssessmentEngine,
    LifestyleRiskResult
)
from .comprehensive_assessment import (
    RiskFusionEngine,
    ComprehensiveAssessmentResult,
    HealthLevel,
    RiskFactor
)
from .trend_alert import (
    HealthTrendAnalyzer,
    TrendAlert,
    AlertLevel,
    TrendDirection
)

__all__ = [
    # 核心引擎
    'HealthAssessmentEngine',
    
    # 疾病评估
    'HypertensionAssessor',
    'DiabetesAssessor', 
    'DyslipidemiAssessor',
    'DiseaseRiskResult',
    'RiskLevel',
    'ControlStatus',
    
    # 生活方式评估
    'LifestyleAssessmentEngine',
    'LifestyleRiskResult',
    
    # 综合评估
    'RiskFusionEngine',
    'ComprehensiveAssessmentResult',
    'HealthLevel',
    'RiskFactor',
    
    # 趋势预警
    'HealthTrendAnalyzer',
    'TrendAlert',
    'AlertLevel',
    'TrendDirection',
]
