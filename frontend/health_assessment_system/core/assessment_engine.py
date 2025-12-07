"""
健康评估系统核心引擎
Health Assessment System Core Engine

整合所有六个子模块，提供统一的评估接口
"""

from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from modules.assessment_config import (
    AssessmentTaskManager, AssessmentConfig, 
    AssessmentType, TimeWindow, AssessmentPeriod
)
from modules.data_preparation import (
    FeatureEngineer, HealthMetrics, FeatureSet
)
from modules.disease_assessment import (
    HypertensionAssessor, DiabetesAssessor, DyslipidemiAssessor,
    DiseaseRiskResult
)
from modules.lifestyle_assessment import (
    LifestyleAssessmentEngine, LifestyleRiskResult
)
from modules.comprehensive_assessment import (
    RiskFusionEngine, ComprehensiveAssessmentResult
)
from modules.report_generation import (
    AssessmentRecordManager, ReportGenerator,
    AssessmentRecord, ReportType, ReportFormat
)


class HealthAssessmentEngine:
    """
    健康评估系统主引擎
    
    功能：
    1. 协调六个子模块
    2. 提供统一的评估接口
    3. 管理评估流程
    """
    
    def __init__(self):
        """
        初始化评估引擎
        """
        # 初始化各个子模块
        self.task_manager = AssessmentTaskManager()
        self.feature_engineer = FeatureEngineer()
        self.ht_assessor = HypertensionAssessor()
        self.dm_assessor = DiabetesAssessor()
        self.dl_assessor = DyslipidemiAssessor()
        self.lifestyle_engine = LifestyleAssessmentEngine()
        self.fusion_engine = RiskFusionEngine()
        self.record_manager = AssessmentRecordManager()
        self.report_generator = ReportGenerator()
        
        print("✓ 健康评估引擎初始化完成")
    
    def run_scheduled_assessment(
        self,
        user_id: str,
        period: AssessmentPeriod = AssessmentPeriod.MONTHLY,
        time_window: TimeWindow = TimeWindow.LAST_30_DAYS
    ) -> ComprehensiveAssessmentResult:
        """
        运行定期评估
        
        Args:
            user_id: 用户ID
            period: 评估周期
            time_window: 时间窗口
        
        Returns:
            综合评估结果
        """
        print(f"\n{'='*60}")
        print(f"开始定期健康评估 - 用户: {user_id}")
        print(f"{'='*60}\n")
        
        # 1. 创建评估配置
        print("步骤1: 创建评估配置...")
        config = self.task_manager.create_scheduled_assessment(
            user_id=user_id,
            period=period,
            time_window=time_window
        )
        print(f"✓ 评估ID: {config.assessment_id}")
        print(f"✓ 时间窗口: {config.start_date.date()} 至 {config.end_date.date()}")
        
        # 2. 执行完整评估
        result = self._execute_assessment(config, user_id)
        
        # 3. 归档任务
        self.task_manager.archive_task(
            config.assessment_id,
            {'status': 'completed', 'score': result.overall_score}
        )
        
        print(f"\n{'='*60}")
        print(f"定期评估完成")
        print(f"{'='*60}\n")
        
        return result
    
    def run_on_demand_assessment(
        self,
        user_id: str,
        triggered_by: str,
        custom_days: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ComprehensiveAssessmentResult:
        """
        运行按需评估
        
        Args:
            user_id: 用户ID
            triggered_by: 触发者（family/community/doctor）
            custom_days: 自定义天数
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            综合评估结果
        """
        print(f"\n{'='*60}")
        print(f"开始按需健康评估 - 用户: {user_id}")
        print(f"触发者: {triggered_by}")
        print(f"{'='*60}\n")
        
        # 1. 创建评估配置
        print("步骤1: 创建评估配置...")
        config = self.task_manager.create_on_demand_assessment(
            user_id=user_id,
            triggered_by=triggered_by,
            custom_days=custom_days,
            start_date=start_date,
            end_date=end_date
        )
        print(f"✓ 评估ID: {config.assessment_id}")
        
        # 2. 执行完整评估
        result = self._execute_assessment(config, user_id)
        
        print(f"\n{'='*60}")
        print(f"按需评估完成")
        print(f"{'='*60}\n")
        
        return result
    
    def _execute_assessment(
        self,
        config: AssessmentConfig,
        user_id: str
    ) -> ComprehensiveAssessmentResult:
        """
        执行完整评估流程
        
        Args:
            config: 评估配置
            user_id: 用户ID
        
        Returns:
            综合评估结果
        """
        # 2. 数据准备与完整性检查
        print("\n步骤2: 数据准备与完整性检查...")
        raw_data, baseline_data = self._load_user_data(user_id, config)
        
        completeness_report = self.task_manager.check_data_completeness(
            config, raw_data
        )
        print(f"✓ 数据完整性: {completeness_report.completeness_level.value}")
        print(f"✓ 完整率: {completeness_report.overall_completeness_rate*100:.1f}%")
        
        if not completeness_report.is_sufficient_for_assessment():
            print("⚠️  警告: 数据不足，评估结果可能不准确")
        
        # 3. 特征构建
        print("\n步骤3: 特征构建...")
        features = self.feature_engineer.build_features(
            user_id=user_id,
            raw_data=raw_data,
            assessment_period=(config.start_date, config.end_date),
            baseline_data=baseline_data
        )
        print(f"✓ 已构建 {len([k for k, v in features.to_dict().items() if v is not None])} 个特征")
        
        # 4. 单病种风险评估
        print("\n步骤4: 单病种风险评估...")
        disease_results = self._assess_diseases(features.to_dict(), baseline_data)
        
        for disease_name, result in disease_results.items():
            print(f"  • {disease_name}: {result['control_status']} / 风险{result['risk_level']}")
        
        # 5. 生活方式评估
        print("\n步骤5: 生活方式与行为风险评估...")
        diet_data = self._load_diet_data(user_id)
        lifestyle_result = self.lifestyle_engine.assess(
            features=features.to_dict(),
            diet_data=diet_data
        )
        print(f"✓ 生活方式评分: {lifestyle_result.overall_score:.1f}")
        print(f"✓ 风险等级: {lifestyle_result.overall_risk_level.value}")
        
        # 6. 趋势分析
        print("\n步骤6: 趋势变化与异常波动监测...")
        trend_results = self._analyze_trends(user_id, features.to_dict(), baseline_data)
        print(f"✓ 已分析 {len(trend_results)} 个指标的趋势")
        
        # 7. 综合风险融合
        print("\n步骤7: 综合健康风险评估与分层分级...")
        comprehensive_result = self.fusion_engine.fuse_risks(
            disease_results=disease_results,
            lifestyle_result=lifestyle_result.to_dict(),
            trend_results=trend_results,
            user_id=user_id,
            assessment_id=config.assessment_id
        )
        print(f"✓ 综合评分: {comprehensive_result.overall_score:.1f}")
        print(f"✓ 健康等级: {comprehensive_result.health_level.value}")
        print(f"✓ TOP风险因素: {len(comprehensive_result.top_risk_factors)} 个")
        
        # 8. 保存评估记录
        print("\n步骤8: 保存评估记录...")
        self._save_assessment_record(
            config, 
            comprehensive_result, 
            completeness_report
        )
        print("✓ 评估记录已保存")
        
        return comprehensive_result
    
    def _load_user_data(
        self,
        user_id: str,
        config: AssessmentConfig
    ) -> tuple:
        """
        加载用户数据（模拟）
        
        实际应用中应从数据库或健康档案系统加载
        """
        import numpy as np
        from datetime import timedelta
        
        # 模拟生成数据
        days = (config.end_date - config.start_date).days + 1
        timestamps = [config.start_date + timedelta(days=i) for i in range(days)]
        
        raw_data = {}
        
        # 血压数据
        if 'blood_pressure' in config.required_metrics:
            sbp_values = np.random.normal(135, 12, days).tolist()
            raw_data['blood_pressure'] = HealthMetrics(
                metric_name='blood_pressure',
                timestamps=timestamps,
                values=sbp_values,
                unit='mmHg'
            )
        
        # 血糖数据
        if 'blood_glucose' in config.required_metrics:
            glucose_values = np.random.normal(6.5, 1.2, days).tolist()
            raw_data['blood_glucose'] = HealthMetrics(
                metric_name='blood_glucose',
                timestamps=timestamps,
                values=glucose_values,
                unit='mmol/L'
            )
        
        # 睡眠数据
        if 'sleep' in config.required_metrics:
            sleep_values = np.random.normal(6.5, 1.5, days).tolist()
            raw_data['sleep'] = HealthMetrics(
                metric_name='sleep',
                timestamps=timestamps,
                values=sleep_values,
                unit='hours'
            )
        
        # 步数数据
        if 'steps' in config.required_metrics:
            steps_values = np.random.normal(5000, 2000, days).tolist()
            raw_data['steps'] = HealthMetrics(
                metric_name='steps',
                timestamps=timestamps,
                values=steps_values,
                unit='steps'
            )
        
        # 基线数据
        baseline_data = {
            'sbp_mean': 130,
            'glucose_mean': 6.0,
            'weight': 70
        }
        
        return raw_data, baseline_data
    
    def _load_diet_data(self, user_id: str) -> Dict:
        """加载饮食数据（模拟）"""
        return {
            'salt_intake': 'medium',
            'oil_intake': 'medium',
            'sugar_intake': 'medium',
            'vegetable_intake': 'medium'
        }
    
    def _assess_diseases(
        self,
        features: Dict,
        baseline: Optional[Dict]
    ) -> Dict:
        """评估所有单病种"""
        disease_results = {}
        
        # 高血压评估
        if features.get('sbp_mean') is not None:
            ht_result = self.ht_assessor.assess(features, baseline)
            disease_results['hypertension'] = ht_result.to_dict()
        
        # 糖尿病评估
        if features.get('glucose_mean') is not None:
            dm_result = self.dm_assessor.assess(features, baseline)
            disease_results['diabetes'] = dm_result.to_dict()
        
        # 血脂评估
        if features.get('tc_mean') is not None:
            dl_result = self.dl_assessor.assess(features, baseline)
            disease_results['dyslipidemia'] = dl_result.to_dict()
        
        return disease_results
    
    def _analyze_trends(
        self,
        user_id: str,
        features: Dict,
        baseline: Optional[Dict]
    ) -> Dict:
        """分析趋势（简化版）"""
        trend_results = {}
        
        # 血压趋势
        if features.get('sbp_mean') and baseline and 'sbp_mean' in baseline:
            deviation = features['sbp_mean'] - baseline['sbp_mean']
            trend_results['sbp'] = {
                'trend_direction': 'worsening' if deviation > 5 else 'stable',
                'deviation_from_baseline': deviation
            }
        
        # 血糖趋势
        if features.get('glucose_mean') and baseline and 'glucose_mean' in baseline:
            deviation = features['glucose_mean'] - baseline['glucose_mean']
            trend_results['glucose'] = {
                'trend_direction': 'worsening' if deviation > 1 else 'stable',
                'deviation_from_baseline': deviation
            }
        
        return trend_results
    
    def _save_assessment_record(
        self,
        config: AssessmentConfig,
        result: ComprehensiveAssessmentResult,
        completeness_report
    ):
        """保存评估记录"""
        record = AssessmentRecord(
            assessment_id=config.assessment_id,
            user_id=config.user_id,
            assessment_date=result.assessment_date,
            assessment_type=config.assessment_type.value,
            time_window={
                'start': config.start_date.isoformat(),
                'end': config.end_date.isoformat(),
                'days': (config.end_date - config.start_date).days + 1
            },
            data_completeness={
                'level': completeness_report.completeness_level.value,
                'rate': completeness_report.overall_completeness_rate
            },
            overall_score=result.overall_score,
            health_level=result.health_level.value,
            disease_risk_score=result.disease_risk_score,
            lifestyle_risk_score=result.lifestyle_risk_score,
            trend_risk_score=result.trend_risk_score,
            top_risk_factors=[rf.to_dict() for rf in result.top_risk_factors],
            recommendations=result.priority_recommendations
        )
        
        self.record_manager.save_record(record)
    
    def generate_report(
        self,
        assessment_id: str,
        user_id: str,
        report_type: ReportType = ReportType.FAMILY,
        report_format: ReportFormat = ReportFormat.TEXT
    ) -> str:
        """
        生成评估报告
        
        Args:
            assessment_id: 评估ID
            user_id: 用户ID
            report_type: 报告类型
            report_format: 报告格式
        
        Returns:
            报告内容
        """
        # 加载评估记录
        record = self.record_manager.load_record(assessment_id, user_id)
        
        if not record:
            return "评估记录不存在"
        
        # 生成报告
        result_dict = record.to_dict()
        report = self.report_generator.generate_report(
            result_dict,
            report_type,
            report_format
        )
        
        return report
    
    def get_visualization_data(
        self,
        assessment_id: str,
        user_id: str
    ) -> Dict:
        """
        获取可视化数据
        
        Args:
            assessment_id: 评估ID
            user_id: 用户ID
        
        Returns:
            可视化数据
        """
        record = self.record_manager.load_record(assessment_id, user_id)
        
        if not record:
            return {}
        
        return self.report_generator.generate_visualization_data(record.to_dict())
    
    def get_user_assessment_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[AssessmentRecord]:
        """
        获取用户评估历史
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量
        
        Returns:
            评估记录列表
        """
        return self.record_manager.get_user_records(user_id, limit)


# 使用示例和测试
if __name__ == "__main__":
    print("="*60)
    print("健康评估系统 - 完整流程演示")
    print("="*60)
    
    # 创建评估引擎
    engine = HealthAssessmentEngine()
    
    # 运行定期评估
    result = engine.run_scheduled_assessment(
        user_id="USER001",
        period=AssessmentPeriod.MONTHLY,
        time_window=TimeWindow.LAST_30_DAYS
    )
    
    # 显示评估结果摘要
    print("\n" + "="*60)
    print("评估结果摘要")
    print("="*60)
    print(f"综合评分: {result.overall_score:.1f}/100")
    print(f"健康等级: {result.health_level.value}")
    print(f"\nTOP风险因素:")
    for i, rf in enumerate(result.top_risk_factors, 1):
        print(f"{i}. {rf.name} (优先级: {rf.priority.value})")
    
    print(f"\n优先建议:")
    for i, rec in enumerate(result.priority_recommendations, 1):
        print(f"{i}. {rec}")
    
    # 生成不同版本的报告
    print("\n" + "="*60)
    print("生成报告")
    print("="*60)
    
    # 老人版报告
    elderly_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.ELDERLY,
        report_format=ReportFormat.TEXT
    )
    print(elderly_report)
    
    # 获取可视化数据
    viz_data = engine.get_visualization_data(
        assessment_id=result.assessment_id,
        user_id=result.user_id
    )
    print("\n" + "="*60)
    print("可视化数据已生成")
    print(f"维度评分: {viz_data['dimension_scores']}")
    print("="*60)
