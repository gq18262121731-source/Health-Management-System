"""
指标评估器
Indicator Evaluator

负责根据指标值判断状态并生成状态描述文本
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from .health_report_models import IndicatorStatus, VitalSignIndicator


@dataclass
class ReferenceRange:
    """参考范围定义"""
    name: str
    unit: str
    normal_low: float
    normal_high: float
    warning_low: Optional[float] = None
    warning_high: Optional[float] = None
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    
    def get_range_text(self) -> str:
        """获取参考范围文本"""
        return f"{self.normal_low} - {self.normal_high} {self.unit}"


class IndicatorEvaluator:
    """
    指标评估器
    
    根据预设的参考范围评估各项健康指标的状态
    """
    
    def __init__(self):
        # 初始化各指标的参考范围（可从配置文件加载）
        self.reference_ranges = self._init_reference_ranges()
    
    def _init_reference_ranges(self) -> Dict[str, ReferenceRange]:
        """初始化参考范围配置"""
        return {
            # 生命体征
            'spo2': ReferenceRange(
                name='血氧',
                unit='%',
                normal_low=95,
                normal_high=100,
                warning_low=90,
                critical_low=85
            ),
            'heart_rate': ReferenceRange(
                name='心率',
                unit='次/分',
                normal_low=60,
                normal_high=100,
                warning_low=50,
                warning_high=110,
                critical_low=40,
                critical_high=130
            ),
            'systolic_bp': ReferenceRange(
                name='收缩压',
                unit='mmHg',
                normal_low=90,
                normal_high=140,
                warning_high=160,
                critical_high=180,
                warning_low=80,
                critical_low=70
            ),
            'diastolic_bp': ReferenceRange(
                name='舒张压',
                unit='mmHg',
                normal_low=60,
                normal_high=90,
                warning_high=100,
                critical_high=110,
                warning_low=50,
                critical_low=40
            ),
            'pulse_rate': ReferenceRange(
                name='脉率',
                unit='次/分',
                normal_low=60,
                normal_high=100,
                warning_low=50,
                warning_high=110
            ),
            'body_temperature': ReferenceRange(
                name='体温',
                unit='℃',
                normal_low=36.0,
                normal_high=37.3,
                warning_high=38.0,
                critical_high=39.0,
                warning_low=35.5,
                critical_low=35.0
            ),
            
            # 代谢指标
            'blood_sugar_fasting': ReferenceRange(
                name='空腹血糖',
                unit='mmol/L',
                normal_low=3.9,
                normal_high=6.1,
                warning_high=7.0,
                critical_high=11.1,
                warning_low=3.5,
                critical_low=2.8
            ),
            'blood_sugar_random': ReferenceRange(
                name='随机血糖',
                unit='mmol/L',
                normal_low=3.9,
                normal_high=7.8,
                warning_high=11.1,
                critical_high=16.7
            ),
            'uric_acid_male': ReferenceRange(
                name='血尿酸(男)',
                unit='μmol/L',
                normal_low=208,
                normal_high=428,
                warning_high=480,
                critical_high=540
            ),
            'uric_acid_female': ReferenceRange(
                name='血尿酸(女)',
                unit='μmol/L',
                normal_low=155,
                normal_high=357,
                warning_high=420,
                critical_high=480
            ),
            'bmi': ReferenceRange(
                name='BMI',
                unit='',
                normal_low=18.5,
                normal_high=24.0,
                warning_high=28.0,
                critical_high=32.0,
                warning_low=17.0,
                critical_low=16.0
            )
        }
    
    def evaluate(
        self, 
        indicator_key: str, 
        value: Optional[float],
        gender: str = "男"
    ) -> Tuple[IndicatorStatus, str]:
        """
        评估指标状态
        
        Args:
            indicator_key: 指标键名
            value: 指标值
            gender: 性别（用于某些性别差异指标）
        
        Returns:
            (状态枚举, 状态描述文本)
        """
        if value is None:
            return IndicatorStatus.NO_DATA, "暂无数据"
        
        # 处理性别差异指标
        if indicator_key == 'uric_acid':
            indicator_key = 'uric_acid_male' if gender == "男" else 'uric_acid_female'
        
        ref = self.reference_ranges.get(indicator_key)
        if not ref:
            return IndicatorStatus.NORMAL, "位于系统设定参考范围内"
        
        # 判断状态
        status, text = self._determine_status(value, ref)
        return status, text
    
    def _determine_status(
        self, 
        value: float, 
        ref: ReferenceRange
    ) -> Tuple[IndicatorStatus, str]:
        """根据参考范围判断状态"""
        
        # 严重偏高
        if ref.critical_high and value >= ref.critical_high:
            return IndicatorStatus.CRITICAL_HIGH, f"明显高于系统参考上限（参考范围：{ref.get_range_text()}）"
        
        # 严重偏低
        if ref.critical_low and value <= ref.critical_low:
            return IndicatorStatus.CRITICAL_LOW, f"明显低于系统参考下限（参考范围：{ref.get_range_text()}）"
        
        # 偏高
        if ref.warning_high and value >= ref.warning_high:
            return IndicatorStatus.HIGH, f"高于系统参考范围（参考范围：{ref.get_range_text()}）"
        
        # 偏低
        if ref.warning_low and value <= ref.warning_low:
            return IndicatorStatus.LOW, f"低于系统参考范围（参考范围：{ref.get_range_text()}）"
        
        # 略高
        if value > ref.normal_high:
            return IndicatorStatus.SLIGHTLY_HIGH, f"略高于系统参考上限（参考范围：{ref.get_range_text()}）"
        
        # 略低
        if value < ref.normal_low:
            return IndicatorStatus.SLIGHTLY_LOW, f"略低于系统参考下限（参考范围：{ref.get_range_text()}）"
        
        # 正常
        return IndicatorStatus.NORMAL, "位于系统设定参考范围内"
    
    def create_vital_sign_indicator(
        self,
        indicator_key: str,
        value: Optional[float],
        gender: str = "男"
    ) -> VitalSignIndicator:
        """
        创建生命体征指标对象
        
        Args:
            indicator_key: 指标键名
            value: 指标值
            gender: 性别
        
        Returns:
            VitalSignIndicator对象
        """
        ref = self.reference_ranges.get(indicator_key)
        if not ref:
            # 未知指标
            return VitalSignIndicator(
                name=indicator_key,
                value=value,
                unit="",
                status=IndicatorStatus.NO_DATA,
                status_text="暂无数据"
            )
        
        status, status_text = self.evaluate(indicator_key, value, gender)
        
        return VitalSignIndicator(
            name=ref.name,
            value=value,
            unit=ref.unit,
            status=status,
            status_text=status_text,
            reference_range=ref.get_range_text()
        )
    
    def get_reference_range(self, indicator_key: str) -> Optional[ReferenceRange]:
        """获取指标的参考范围"""
        return self.reference_ranges.get(indicator_key)
    
    def update_reference_range(
        self, 
        indicator_key: str, 
        normal_low: float = None,
        normal_high: float = None,
        **kwargs
    ):
        """
        更新指标参考范围（用于个性化设置）
        
        Args:
            indicator_key: 指标键名
            normal_low: 正常下限
            normal_high: 正常上限
            **kwargs: 其他参数
        """
        if indicator_key in self.reference_ranges:
            ref = self.reference_ranges[indicator_key]
            if normal_low is not None:
                ref.normal_low = normal_low
            if normal_high is not None:
                ref.normal_high = normal_high
            for key, value in kwargs.items():
                if hasattr(ref, key):
                    setattr(ref, key, value)


class PersonalizedEvaluator(IndicatorEvaluator):
    """
    个性化指标评估器
    
    支持根据用户历史数据调整参考范围
    """
    
    def __init__(self, user_baseline: Optional[Dict] = None):
        super().__init__()
        self.user_baseline = user_baseline or {}
    
    def set_user_baseline(self, baseline: Dict):
        """设置用户个人基线"""
        self.user_baseline = baseline
    
    def evaluate_with_baseline(
        self,
        indicator_key: str,
        value: Optional[float],
        gender: str = "男"
    ) -> Tuple[IndicatorStatus, str, str]:
        """
        结合个人基线评估指标
        
        Returns:
            (状态枚举, 状态描述, 与基线对比描述)
        """
        status, status_text = self.evaluate(indicator_key, value, gender)
        
        baseline_comparison = ""
        if indicator_key in self.user_baseline and value is not None:
            baseline_value = self.user_baseline[indicator_key].get('mean')
            if baseline_value:
                diff = value - baseline_value
                diff_percent = (diff / baseline_value) * 100 if baseline_value != 0 else 0
                
                if abs(diff_percent) < 5:
                    baseline_comparison = "与个人历史平均水平相近"
                elif diff > 0:
                    baseline_comparison = f"高于个人历史平均水平 {abs(diff_percent):.1f}%"
                else:
                    baseline_comparison = f"低于个人历史平均水平 {abs(diff_percent):.1f}%"
        
        return status, status_text, baseline_comparison


# 使用示例
if __name__ == "__main__":
    evaluator = IndicatorEvaluator()
    
    # 测试各种指标
    test_cases = [
        ('spo2', 98),
        ('spo2', 92),
        ('heart_rate', 75),
        ('heart_rate', 115),
        ('systolic_bp', 135),
        ('systolic_bp', 165),
        ('blood_sugar_fasting', 5.5),
        ('blood_sugar_fasting', 7.5),
        ('bmi', 22.5),
        ('bmi', 29.0),
    ]
    
    print("指标评估测试:")
    print("-" * 60)
    for key, value in test_cases:
        status, text = evaluator.evaluate(key, value)
        print(f"{key} = {value}: {status.value}")
        print(f"  描述: {text}")
        print()
