"""
模块1：评估配置与任务管理子模块
Assessment Configuration and Task Management Module

功能：
- 定期评估与按需评估管理
- 评估时间窗口配置
- 数据完整性检查

算法分配：无复杂算法，主要是任务调度和配置管理
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json


class AssessmentType(Enum):
    """评估类型"""
    SCHEDULED = "scheduled"  # 定期评估
    ON_DEMAND = "on_demand"  # 按需评估


class AssessmentPeriod(Enum):
    """评估周期"""
    WEEKLY = "weekly"  # 每周
    MONTHLY = "monthly"  # 每月
    CUSTOM = "custom"  # 自定义


class TimeWindow(Enum):
    """时间窗口"""
    LAST_7_DAYS = 7
    LAST_30_DAYS = 30
    LAST_90_DAYS = 90
    CUSTOM = 0


class DataCompleteness(Enum):
    """数据完整性等级"""
    COMPLETE = "complete"  # 完整评估
    PARTIAL = "partial"  # 部分评估
    INSUFFICIENT = "insufficient"  # 数据不足


@dataclass
class AssessmentConfig:
    """评估配置"""
    assessment_id: str
    user_id: str
    assessment_type: AssessmentType
    time_window: TimeWindow
    start_date: datetime
    end_date: datetime
    custom_period_days: Optional[int] = None
    triggered_by: str = "system"  # system/family/community
    priority: int = 1  # 1-5, 5最高
    required_metrics: List[str] = field(default_factory=lambda: [
        'blood_pressure', 'blood_glucose', 'blood_lipid', 
        'heart_rate', 'weight', 'sleep', 'steps'
    ])
    optional_metrics: List[str] = field(default_factory=lambda: [
        'medication', 'diet', 'mood'
    ])
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'assessment_id': self.assessment_id,
            'user_id': self.user_id,
            'assessment_type': self.assessment_type.value,
            'time_window': self.time_window.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'custom_period_days': self.custom_period_days,
            'triggered_by': self.triggered_by,
            'priority': self.priority,
            'required_metrics': self.required_metrics,
            'optional_metrics': self.optional_metrics
        }


@dataclass
class DataCompletenessReport:
    """数据完整性报告"""
    completeness_level: DataCompleteness
    overall_completeness_rate: float  # 0-1
    metric_completeness: Dict[str, float]  # 各指标完整性
    missing_days: int
    total_days: int
    warnings: List[str] = field(default_factory=list)
    
    def is_sufficient_for_assessment(self) -> bool:
        """判断数据是否足够进行评估"""
        return self.completeness_level != DataCompleteness.INSUFFICIENT


class AssessmentTaskManager:
    """评估任务管理器"""
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, AssessmentConfig] = {}
        self.task_history: List[Dict] = []
        
    def create_scheduled_assessment(
        self, 
        user_id: str, 
        period: AssessmentPeriod,
        time_window: TimeWindow = TimeWindow.LAST_30_DAYS
    ) -> AssessmentConfig:
        """创建定期评估任务"""
        assessment_id = self._generate_assessment_id(user_id)
        
        end_date = datetime.now()
        if time_window == TimeWindow.CUSTOM:
            start_date = end_date - timedelta(days=30)  # 默认30天
        else:
            start_date = end_date - timedelta(days=time_window.value)
        
        config = AssessmentConfig(
            assessment_id=assessment_id,
            user_id=user_id,
            assessment_type=AssessmentType.SCHEDULED,
            time_window=time_window,
            start_date=start_date,
            end_date=end_date,
            triggered_by="system"
        )
        
        self.scheduled_tasks[assessment_id] = config
        return config
    
    def create_on_demand_assessment(
        self,
        user_id: str,
        triggered_by: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        custom_days: Optional[int] = None
    ) -> AssessmentConfig:
        """创建按需评估任务"""
        assessment_id = self._generate_assessment_id(user_id)
        
        if end_date is None:
            end_date = datetime.now()
        
        if start_date is None:
            if custom_days:
                start_date = end_date - timedelta(days=custom_days)
            else:
                start_date = end_date - timedelta(days=7)  # 默认7天
        
        config = AssessmentConfig(
            assessment_id=assessment_id,
            user_id=user_id,
            assessment_type=AssessmentType.ON_DEMAND,
            time_window=TimeWindow.CUSTOM,
            start_date=start_date,
            end_date=end_date,
            custom_period_days=custom_days,
            triggered_by=triggered_by,
            priority=3  # 按需评估优先级较高
        )
        
        return config
    
    def check_data_completeness(
        self,
        config: AssessmentConfig,
        available_data: Dict[str, List]
    ) -> DataCompletenessReport:
        """
        检查数据完整性
        
        Args:
            config: 评估配置
            available_data: 可用数据 {metric_name: [data_points]}
        
        Returns:
            数据完整性报告
        """
        total_days = (config.end_date - config.start_date).days + 1
        metric_completeness = {}
        warnings = []
        
        # 检查每个必需指标的完整性
        for metric in config.required_metrics:
            if metric not in available_data or not available_data[metric]:
                metric_completeness[metric] = 0.0
                warnings.append(f"缺少必需指标: {metric}")
            else:
                # 计算数据覆盖率
                metric_data = available_data[metric]
                # 如果是列表或字典，计算长度；如果是单个对象，视为1天数据
                if isinstance(metric_data, (list, dict)):
                    data_days = len(metric_data)
                else:
                    data_days = 1
                completeness = min(data_days / total_days, 1.0)
                metric_completeness[metric] = completeness
                
                if completeness < 0.3:
                    warnings.append(f"指标 {metric} 数据严重不足 ({completeness*100:.1f}%)")
                elif completeness < 0.6:
                    warnings.append(f"指标 {metric} 数据不完整 ({completeness*100:.1f}%)")
        
        # 计算总体完整性
        if metric_completeness:
            overall_completeness = sum(metric_completeness.values()) / len(metric_completeness)
        else:
            overall_completeness = 0.0
        
        # 确定完整性等级
        if overall_completeness >= 0.8:
            completeness_level = DataCompleteness.COMPLETE
        elif overall_completeness >= 0.5:
            completeness_level = DataCompleteness.PARTIAL
        else:
            completeness_level = DataCompleteness.INSUFFICIENT
            warnings.append("数据不足，无法进行完整评估")
        
        missing_days = total_days - int(overall_completeness * total_days)
        
        return DataCompletenessReport(
            completeness_level=completeness_level,
            overall_completeness_rate=overall_completeness,
            metric_completeness=metric_completeness,
            missing_days=missing_days,
            total_days=total_days,
            warnings=warnings
        )
    
    def _generate_assessment_id(self, user_id: str) -> str:
        """生成评估ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ASSESS_{user_id}_{timestamp}"
    
    def get_task_status(self, assessment_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if assessment_id in self.scheduled_tasks:
            return self.scheduled_tasks[assessment_id].to_dict()
        
        # 从历史记录中查找
        for task in self.task_history:
            if task['assessment_id'] == assessment_id:
                return task
        
        return None
    
    def archive_task(self, assessment_id: str, result: Dict):
        """归档已完成的任务"""
        if assessment_id in self.scheduled_tasks:
            task = self.scheduled_tasks[assessment_id].to_dict()
            task['completed_at'] = datetime.now().isoformat()
            task['result_summary'] = result
            self.task_history.append(task)
            del self.scheduled_tasks[assessment_id]


# 使用示例
if __name__ == "__main__":
    # 创建任务管理器
    manager = AssessmentTaskManager()
    
    # 创建定期评估
    scheduled_config = manager.create_scheduled_assessment(
        user_id="USER001",
        period=AssessmentPeriod.WEEKLY,
        time_window=TimeWindow.LAST_7_DAYS
    )
    print("定期评估配置:", scheduled_config.to_dict())
    
    # 创建按需评估
    on_demand_config = manager.create_on_demand_assessment(
        user_id="USER001",
        triggered_by="family_member",
        custom_days=14
    )
    print("\n按需评估配置:", on_demand_config.to_dict())
    
    # 模拟数据完整性检查
    mock_data = {
        'blood_pressure': [1] * 25,  # 25天数据
        'blood_glucose': [1] * 20,   # 20天数据
        'sleep': [1] * 28,            # 28天数据
        'steps': [1] * 30,            # 30天数据
    }
    
    completeness_report = manager.check_data_completeness(
        scheduled_config, 
        mock_data
    )
    
    print("\n数据完整性报告:")
    print(f"完整性等级: {completeness_report.completeness_level.value}")
    print(f"总体完整率: {completeness_report.overall_completeness_rate*100:.1f}%")
    print(f"各指标完整性: {completeness_report.metric_completeness}")
    print(f"警告信息: {completeness_report.warnings}")
