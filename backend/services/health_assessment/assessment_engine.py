"""
健康评估系统核心引擎
Health Assessment System Core Engine

整合所有六个子模块，提供统一的评估接口
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

# 使用相对导入（同一目录下的模块）
from .assessment_config import (
    AssessmentTaskManager, AssessmentConfig, 
    AssessmentType, TimeWindow, AssessmentPeriod
)
from .data_preparation import (
    FeatureEngineer, HealthMetrics, FeatureSet
)
from .disease_assessment import (
    HypertensionAssessor, DiabetesAssessor, DyslipidemiAssessor,
    DiseaseRiskResult
)
from .lifestyle_assessment import (
    LifestyleAssessmentEngine, LifestyleRiskResult
)
from .comprehensive_assessment import (
    RiskFusionEngine, ComprehensiveAssessmentResult
)
from .report_generation import (
    AssessmentRecordManager, ReportGenerator,
    AssessmentRecord, ReportType, ReportFormat
)

logger = logging.getLogger(__name__)


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
        从 MySQL 数据库加载用户健康数据
        
        Args:
            user_id: 用户ID（可以是 elder_id 或 'elderly_001' 格式）
            config: 评估配置
            
        Returns:
            (raw_data, baseline_data) 元组
        """
        from datetime import timedelta
        from .database_manager import DatabaseManager
        
        raw_data = {}
        baseline_data = {}
        
        try:
            db = DatabaseManager()
            
            # 解析 elder_id（支持 'elderly_001' 格式或纯数字）
            if isinstance(user_id, str) and user_id.startswith('elderly_'):
                elder_id = int(user_id.replace('elderly_', '').lstrip('0') or '1')
            else:
                try:
                    elder_id = int(user_id)
                except:
                    elder_id = 1  # 默认使用第一个老人
            
            # 查询时间范围内的健康记录
            sql = """
                SELECT 
                    check_time,
                    systolic_bp,
                    diastolic_bp,
                    heart_rate,
                    blood_sugar,
                    spo2,
                    body_temperature,
                    sleep_hours,
                    steps,
                    weight_kg
                FROM health_record 
                WHERE elder_id = %s 
                  AND check_time >= %s 
                  AND check_time <= %s
                ORDER BY check_time ASC
            """
            
            records = db.execute_query(sql, (
                elder_id, 
                config.start_date.strftime('%Y-%m-%d 00:00:00'),
                config.end_date.strftime('%Y-%m-%d 23:59:59')
            ))
            
            if records:
                # 提取各指标数据
                timestamps = []
                sbp_values = []
                dbp_values = []
                hr_values = []
                glucose_values = []
                sleep_values = []
                steps_values = []
                weight_values = []
                
                for record in records:
                    ts = record.get('check_time')
                    if ts:
                        timestamps.append(ts)
                        
                        if record.get('systolic_bp'):
                            sbp_values.append(float(record['systolic_bp']))
                        if record.get('diastolic_bp'):
                            dbp_values.append(float(record['diastolic_bp']))
                        if record.get('heart_rate'):
                            hr_values.append(float(record['heart_rate']))
                        if record.get('blood_sugar'):
                            glucose_values.append(float(record['blood_sugar']))
                        if record.get('sleep_hours'):
                            sleep_values.append(float(record['sleep_hours']))
                        if record.get('steps'):
                            steps_values.append(float(record['steps']))
                        if record.get('weight_kg'):
                            weight_values.append(float(record['weight_kg']))
                
                # 构建 HealthMetrics 对象
                if sbp_values:
                    raw_data['blood_pressure'] = HealthMetrics(
                        metric_name='blood_pressure',
                        timestamps=timestamps[:len(sbp_values)],
                        values=sbp_values,
                        unit='mmHg'
                    )
                
                if glucose_values:
                    raw_data['blood_glucose'] = HealthMetrics(
                        metric_name='blood_glucose',
                        timestamps=timestamps[:len(glucose_values)],
                        values=glucose_values,
                        unit='mmol/L'
                    )
                
                if hr_values:
                    raw_data['heart_rate'] = HealthMetrics(
                        metric_name='heart_rate',
                        timestamps=timestamps[:len(hr_values)],
                        values=hr_values,
                        unit='bpm'
                    )
                
                if sleep_values:
                    raw_data['sleep'] = HealthMetrics(
                        metric_name='sleep',
                        timestamps=timestamps[:len(sleep_values)],
                        values=sleep_values,
                        unit='hours'
                    )
                
                if steps_values:
                    raw_data['steps'] = HealthMetrics(
                        metric_name='steps',
                        timestamps=timestamps[:len(steps_values)],
                        values=steps_values,
                        unit='steps'
                    )
                
                if weight_values:
                    raw_data['weight'] = HealthMetrics(
                        metric_name='weight',
                        timestamps=timestamps[:len(weight_values)],
                        values=weight_values,
                        unit='kg'
                    )
                
                # 计算基线数据（使用历史平均值）
                if sbp_values:
                    baseline_data['sbp_mean'] = sum(sbp_values) / len(sbp_values)
                if glucose_values:
                    baseline_data['glucose_mean'] = sum(glucose_values) / len(glucose_values)
                if weight_values:
                    baseline_data['weight'] = sum(weight_values) / len(weight_values)
                
                print(f"✓ 从数据库加载了 {len(records)} 条健康记录")
            else:
                print(f"⚠️ 未找到用户 {elder_id} 在指定时间范围内的健康记录，使用默认数据")
                raw_data, baseline_data = self._generate_default_data(config)
                
        except Exception as e:
            print(f"⚠️ 数据库查询失败: {e}，使用默认数据")
            raw_data, baseline_data = self._generate_default_data(config)
        
        return raw_data, baseline_data
    
    def _generate_default_data(self, config: AssessmentConfig) -> tuple:
        """生成默认数据（当数据库不可用时）"""
        import numpy as np
        from datetime import timedelta
        
        days = (config.end_date - config.start_date).days + 1
        timestamps = [config.start_date + timedelta(days=i) for i in range(days)]
        
        raw_data = {}
        
        # 血压数据
        sbp_values = np.random.normal(130, 10, days).tolist()
        raw_data['blood_pressure'] = HealthMetrics(
            metric_name='blood_pressure',
            timestamps=timestamps,
            values=sbp_values,
            unit='mmHg'
        )
        
        # 血糖数据
        glucose_values = np.random.normal(6.0, 0.8, days).tolist()
        raw_data['blood_glucose'] = HealthMetrics(
            metric_name='blood_glucose',
            timestamps=timestamps,
            values=glucose_values,
            unit='mmol/L'
        )
        
        # 睡眠数据
        sleep_values = np.random.normal(7.0, 1.0, days).tolist()
        raw_data['sleep'] = HealthMetrics(
            metric_name='sleep',
            timestamps=timestamps,
            values=sleep_values,
            unit='hours'
        )
        
        # 步数数据
        steps_values = np.random.normal(5000, 1500, days).tolist()
        raw_data['steps'] = HealthMetrics(
            metric_name='steps',
            timestamps=timestamps,
            values=steps_values,
            unit='steps'
        )
        
        baseline_data = {
            'sbp_mean': 130,
            'glucose_mean': 6.0,
            'weight': 70
        }
        
        return raw_data, baseline_data
    
    def _load_diet_data(self, user_id: str) -> Dict:
        """从数据库加载饮食数据"""
        # 目前数据库中没有饮食数据表，返回默认值
        # 后续可扩展
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
