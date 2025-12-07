"""
养生之道·智能健康报告 数据模型
Health Report Data Models

用于生成标准化健康报告的数据结构定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, date
from enum import Enum


class IndicatorStatus(Enum):
    """指标状态枚举"""
    NORMAL = "normal"           # 正常范围内
    SLIGHTLY_HIGH = "slightly_high"  # 略高
    SLIGHTLY_LOW = "slightly_low"    # 略低
    HIGH = "high"               # 偏高
    LOW = "low"                 # 偏低
    CRITICAL_HIGH = "critical_high"  # 严重偏高
    CRITICAL_LOW = "critical_low"    # 严重偏低
    NO_DATA = "no_data"         # 暂无数据


@dataclass
class ElderBasicInfo:
    """老人基本信息"""
    elder_id: str
    elder_name: str
    elder_gender: str  # 男/女
    elder_age: int
    elder_phone: str = ""
    elder_address: str = ""
    elder_chronic_tags: List[str] = field(default_factory=list)  # 既往记录标签
    
    def get_chronic_tags_text(self) -> str:
        """获取既往记录标签文本"""
        if not self.elder_chronic_tags:
            return "暂无"
        return " / ".join(self.elder_chronic_tags)


@dataclass
class VitalSignIndicator:
    """生命体征指标"""
    name: str           # 指标名称
    value: Optional[float]  # 本次结果
    unit: str           # 单位
    status: IndicatorStatus = IndicatorStatus.NO_DATA
    status_text: str = ""   # 系统状态描述
    reference_range: str = ""  # 参考范围
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'status': self.status.value,
            'status_text': self.status_text,
            'reference_range': self.reference_range
        }


@dataclass
class VitalSigns:
    """生命体征数据集"""
    spo2: VitalSignIndicator = None           # 血氧
    heart_rate: VitalSignIndicator = None     # 心率
    systolic_bp: VitalSignIndicator = None    # 收缩压
    diastolic_bp: VitalSignIndicator = None   # 舒张压
    pulse_rate: VitalSignIndicator = None     # 脉率
    body_temperature: VitalSignIndicator = None  # 体温
    
    def __post_init__(self):
        if self.spo2 is None:
            self.spo2 = VitalSignIndicator("血氧", None, "%")
        if self.heart_rate is None:
            self.heart_rate = VitalSignIndicator("心率", None, "次/分")
        if self.systolic_bp is None:
            self.systolic_bp = VitalSignIndicator("收缩压", None, "mmHg")
        if self.diastolic_bp is None:
            self.diastolic_bp = VitalSignIndicator("舒张压", None, "mmHg")
        if self.pulse_rate is None:
            self.pulse_rate = VitalSignIndicator("脉率", None, "次/分")
        if self.body_temperature is None:
            self.body_temperature = VitalSignIndicator("体温", None, "℃")
    
    def to_dict(self) -> Dict:
        return {
            'spo2': self.spo2.to_dict() if self.spo2 else None,
            'heart_rate': self.heart_rate.to_dict() if self.heart_rate else None,
            'systolic_bp': self.systolic_bp.to_dict() if self.systolic_bp else None,
            'diastolic_bp': self.diastolic_bp.to_dict() if self.diastolic_bp else None,
            'pulse_rate': self.pulse_rate.to_dict() if self.pulse_rate else None,
            'body_temperature': self.body_temperature.to_dict() if self.body_temperature else None
        }


@dataclass
class MetabolicIndicators:
    """代谢相关指标"""
    blood_sugar: VitalSignIndicator = None    # 血糖
    uric_acid: VitalSignIndicator = None      # 血尿酸
    weight: VitalSignIndicator = None         # 体重
    bmi: VitalSignIndicator = None            # BMI
    
    def __post_init__(self):
        if self.blood_sugar is None:
            self.blood_sugar = VitalSignIndicator("血糖", None, "mmol/L")
        if self.uric_acid is None:
            self.uric_acid = VitalSignIndicator("血尿酸", None, "μmol/L")
        if self.weight is None:
            self.weight = VitalSignIndicator("体重", None, "kg")
        if self.bmi is None:
            self.bmi = VitalSignIndicator("BMI", None, "")
    
    def to_dict(self) -> Dict:
        return {
            'blood_sugar': self.blood_sugar.to_dict() if self.blood_sugar else None,
            'uric_acid': self.uric_acid.to_dict() if self.uric_acid else None,
            'weight': self.weight.to_dict() if self.weight else None,
            'bmi': self.bmi.to_dict() if self.bmi else None
        }


@dataclass
class TrendStatistics:
    """趋势统计数据"""
    metric_name: str
    avg_value: Optional[float] = None
    max_value: Optional[float] = None
    min_value: Optional[float] = None
    std_value: Optional[float] = None
    trend_desc: str = ""  # 趋势描述
    stat_text: str = ""   # 统计结果文本
    
    def to_dict(self) -> Dict:
        return {
            'metric_name': self.metric_name,
            'avg_value': self.avg_value,
            'max_value': self.max_value,
            'min_value': self.min_value,
            'std_value': self.std_value,
            'trend_desc': self.trend_desc,
            'stat_text': self.stat_text
        }


@dataclass
class TrendAnalysis:
    """近期变化趋势分析"""
    trend_window_start: Optional[date] = None
    trend_window_end: Optional[date] = None
    valid_check_count: int = 0
    
    bp_trend: Optional[TrendStatistics] = None      # 收缩压趋势
    dbp_trend: Optional[TrendStatistics] = None     # 舒张压趋势
    sugar_trend: Optional[TrendStatistics] = None   # 血糖趋势
    hr_trend: Optional[TrendStatistics] = None      # 心率趋势
    temp_trend: Optional[TrendStatistics] = None    # 体温趋势
    weight_trend: Optional[TrendStatistics] = None  # 体重趋势
    uric_acid_trend: Optional[TrendStatistics] = None  # 血尿酸趋势
    
    trend_overall_text: str = ""  # 趋势综合描述
    
    def to_dict(self) -> Dict:
        return {
            'trend_window_start': self.trend_window_start.isoformat() if self.trend_window_start else None,
            'trend_window_end': self.trend_window_end.isoformat() if self.trend_window_end else None,
            'valid_check_count': self.valid_check_count,
            'bp_trend': self.bp_trend.to_dict() if self.bp_trend else None,
            'dbp_trend': self.dbp_trend.to_dict() if self.dbp_trend else None,
            'sugar_trend': self.sugar_trend.to_dict() if self.sugar_trend else None,
            'hr_trend': self.hr_trend.to_dict() if self.hr_trend else None,
            'temp_trend': self.temp_trend.to_dict() if self.temp_trend else None,
            'weight_trend': self.weight_trend.to_dict() if self.weight_trend else None,
            'uric_acid_trend': self.uric_acid_trend.to_dict() if self.uric_acid_trend else None,
            'trend_overall_text': self.trend_overall_text
        }


@dataclass
class FeatureRecognition:
    """系统特征识别小结"""
    feature_overview_text: str = ""       # 指标特征概览
    combined_feature_text: str = ""       # 组合特征说明
    system_focus_points: List[str] = field(default_factory=list)  # 系统标记的关注点
    
    def to_dict(self) -> Dict:
        return {
            'feature_overview_text': self.feature_overview_text,
            'combined_feature_text': self.combined_feature_text,
            'system_focus_points': self.system_focus_points
        }


@dataclass
class BaselineComparison:
    """历史对比与个体基线"""
    baseline_days: int = 90  # 基线计算天数
    personal_baseline_desc: str = ""  # 个人基线区间说明
    
    bp_vs_baseline_text: str = ""      # 血压对比
    sugar_vs_baseline_text: str = ""   # 血糖对比
    others_vs_baseline_text: str = ""  # 其他对比
    
    def to_dict(self) -> Dict:
        return {
            'baseline_days': self.baseline_days,
            'personal_baseline_desc': self.personal_baseline_desc,
            'bp_vs_baseline_text': self.bp_vs_baseline_text,
            'sugar_vs_baseline_text': self.sugar_vs_baseline_text,
            'others_vs_baseline_text': self.others_vs_baseline_text
        }


@dataclass
class HealthReportData:
    """
    养生之道·智能健康报告 完整数据结构
    
    包含报告所需的所有数据字段
    """
    # 报告元信息
    report_id: str
    report_date: datetime
    
    # 一、基本信息
    elder_info: ElderBasicInfo
    
    # 二、关键指标一览
    vital_signs: VitalSigns
    metabolic_indicators: MetabolicIndicators
    
    # 三、近期变化趋势
    trend_analysis: TrendAnalysis
    
    # 四、系统特征识别小结
    feature_recognition: FeatureRecognition
    
    # 五、历史对比与个体基线
    baseline_comparison: BaselineComparison
    
    # 六、报告说明（固定文案）
    disclaimer: str = field(default_factory=lambda: (
        "本报告由「养生之道」系统根据用户日常检测数据自动生成，"
        "仅用于帮助用户及家属了解当前数据与变化情况。\n"
        "本报告不包含医疗诊断内容，也不替代任何专业医疗意见。\n"
        "如需获取诊断、治疗或用药等专业信息，请以正规医疗机构和专业人士的意见为准。"
    ))
    
    def to_dict(self) -> Dict:
        """转换为字典，用于模板渲染"""
        return {
            'report_id': self.report_id,
            'report_date': self.report_date.strftime('%Y年%m月%d日'),
            'elder_name': self.elder_info.elder_name,
            'elder_gender': self.elder_info.elder_gender,
            'elder_age': self.elder_info.elder_age,
            'elder_phone': self.elder_info.elder_phone,
            'elder_address': self.elder_info.elder_address,
            'elder_chronic_tags': self.elder_info.get_chronic_tags_text(),
            'vital_signs': self.vital_signs.to_dict(),
            'metabolic_indicators': self.metabolic_indicators.to_dict(),
            'trend_analysis': self.trend_analysis.to_dict(),
            'feature_recognition': self.feature_recognition.to_dict(),
            'baseline_comparison': self.baseline_comparison.to_dict(),
            'disclaimer': self.disclaimer
        }
    
    def to_template_vars(self) -> Dict:
        """
        转换为模板变量字典
        
        返回与模板中 {{变量名}} 对应的扁平化字典
        """
        vs = self.vital_signs
        mi = self.metabolic_indicators
        ta = self.trend_analysis
        fr = self.feature_recognition
        bc = self.baseline_comparison
        
        return {
            # 基本信息
            'elder_name': self.elder_info.elder_name,
            'elder_gender': self.elder_info.elder_gender,
            'elder_age': self.elder_info.elder_age,
            'elder_phone': self.elder_info.elder_phone,
            'elder_address': self.elder_info.elder_address,
            'elder_chronic_tags': self.elder_info.get_chronic_tags_text(),
            'report_date': self.report_date.strftime('%Y年%m月%d日'),
            
            # 生命体征
            'spo2': vs.spo2.value if vs.spo2.value else "暂无数据",
            'spo2_status_text': vs.spo2.status_text or "暂无数据",
            'heart_rate': vs.heart_rate.value if vs.heart_rate.value else "暂无数据",
            'heart_rate_status_text': vs.heart_rate.status_text or "暂无数据",
            'systolic_bp': vs.systolic_bp.value if vs.systolic_bp.value else "暂无数据",
            'systolic_bp_status_text': vs.systolic_bp.status_text or "暂无数据",
            'diastolic_bp': vs.diastolic_bp.value if vs.diastolic_bp.value else "暂无数据",
            'diastolic_bp_status_text': vs.diastolic_bp.status_text or "暂无数据",
            'pulse_rate': vs.pulse_rate.value if vs.pulse_rate.value else "暂无数据",
            'pulse_rate_status_text': vs.pulse_rate.status_text or "暂无数据",
            'body_temperature': vs.body_temperature.value if vs.body_temperature.value else "暂无数据",
            'body_temperature_status_text': vs.body_temperature.status_text or "暂无数据",
            
            # 代谢指标
            'blood_sugar': mi.blood_sugar.value if mi.blood_sugar.value else "暂无数据",
            'blood_sugar_status_text': mi.blood_sugar.status_text or "暂无数据",
            'uric_acid': mi.uric_acid.value if mi.uric_acid.value else "暂无数据",
            'uric_acid_status_text': mi.uric_acid.status_text or "暂无数据",
            'weight_kg': mi.weight.value if mi.weight.value else "暂无数据",
            'weight_status_text': mi.weight.status_text or "暂无数据",
            'bmi': mi.bmi.value if mi.bmi.value else "暂无数据",
            'bmi_status_text': mi.bmi.status_text or "暂无数据",
            
            # 趋势分析
            'trend_window_start': ta.trend_window_start.strftime('%Y-%m-%d') if ta.trend_window_start else "暂无",
            'trend_window_end': ta.trend_window_end.strftime('%Y-%m-%d') if ta.trend_window_end else "暂无",
            'valid_check_count': ta.valid_check_count,
            # 收缩压趋势
            'bp_trend_stat_text': ta.bp_trend.stat_text if ta.bp_trend else "暂无数据",
            'bp_sys_avg': ta.bp_trend.avg_value if ta.bp_trend else "暂无",
            'bp_sys_max': ta.bp_trend.max_value if ta.bp_trend else "暂无",
            'bp_sys_min': ta.bp_trend.min_value if ta.bp_trend else "暂无",
            'bp_trend_desc': ta.bp_trend.trend_desc if ta.bp_trend else "暂无数据",
            # 舒张压趋势
            'dbp_trend_stat_text': ta.dbp_trend.stat_text if ta.dbp_trend else "暂无数据",
            'dbp_avg': ta.dbp_trend.avg_value if ta.dbp_trend else "暂无",
            'dbp_max': ta.dbp_trend.max_value if ta.dbp_trend else "暂无",
            'dbp_min': ta.dbp_trend.min_value if ta.dbp_trend else "暂无",
            'dbp_trend_desc': ta.dbp_trend.trend_desc if ta.dbp_trend else "暂无数据",
            # 血糖趋势
            'sugar_trend_stat_text': ta.sugar_trend.stat_text if ta.sugar_trend else "暂无数据",
            'sugar_trend_desc': ta.sugar_trend.trend_desc if ta.sugar_trend else "暂无数据",
            # 心率趋势
            'hr_trend_desc': ta.hr_trend.trend_desc if ta.hr_trend else "暂无数据",
            # 体温趋势
            'temp_trend_desc': ta.temp_trend.trend_desc if ta.temp_trend else "暂无数据",
            # 体重趋势
            'weight_trend_stat_text': ta.weight_trend.stat_text if ta.weight_trend else "暂无数据",
            'weight_trend_desc': ta.weight_trend.trend_desc if ta.weight_trend else "暂无数据",
            # 血尿酸趋势
            'uric_acid_trend_stat_text': ta.uric_acid_trend.stat_text if ta.uric_acid_trend else "暂无数据",
            'uric_acid_trend_desc': ta.uric_acid_trend.trend_desc if ta.uric_acid_trend else "暂无数据",
            # 综合趋势
            'trend_overall_text': ta.trend_overall_text or "暂无趋势数据",
            
            # 特征识别
            'feature_overview_text': fr.feature_overview_text or "暂无特征数据",
            'combined_feature_text': fr.combined_feature_text or "暂无组合特征",
            'system_focus_points': fr.system_focus_points,
            
            # 基线对比
            'baseline_days': bc.baseline_days,
            'personal_baseline_desc': bc.personal_baseline_desc or "暂无基线数据",
            'bp_vs_baseline_text': bc.bp_vs_baseline_text or "暂无对比数据",
            'sugar_vs_baseline_text': bc.sugar_vs_baseline_text or "暂无对比数据",
            'others_vs_baseline_text': bc.others_vs_baseline_text or "暂无对比数据",
            
            # 免责声明
            'disclaimer': self.disclaimer
        }
