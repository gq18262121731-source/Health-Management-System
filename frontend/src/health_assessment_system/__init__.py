"""
多模型健康评估系统
Multi-Model Health Assessment System

主要模块：
1. assessment_config - 评估配置与任务管理
2. data_preparation - 数据准备与特征构建
3. disease_assessment - 单病种风险评估
4. lifestyle_assessment - 生活方式与行为风险评估
5. comprehensive_assessment - 综合健康风险评估与分层分级
6. report_generation - 评估结果管理与报告生成
"""

__version__ = "1.0.0"
__author__ = "Health Assessment Team"

from .core.assessment_engine import HealthAssessmentEngine

__all__ = ['HealthAssessmentEngine']
