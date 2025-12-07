"""
模块3：单病种风险评估子模块
Disease-Specific Risk Assessment Module

功能：
- 高血压风险评估
- 糖代谢异常风险评估
- 血脂异常风险评估

算法分配：
- 模糊逻辑系统（处理阈值边界）
- XGBoost/LightGBM（可选，用于微调）
- 规则引擎（基于指南的评估规则）
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import warnings

# 尝试导入scikit-fuzzy，如果没有安装则使用简化版本
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    warnings.warn("skfuzzy not installed, using simplified fuzzy logic")


class ControlStatus(Enum):
    """控制状态"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"  # 良好
    FAIR = "fair"  # 一般
    POOR = "poor"  # 较差


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中风险
    HIGH = "high"  # 高风险
    VERY_HIGH = "very_high"  # 极高风险


@dataclass
class DiseaseRiskResult:
    """单病种风险评估结果"""
    disease_name: str
    control_status: ControlStatus
    risk_level: RiskLevel
    risk_score: float  # 0-100
    control_quality_score: float  # 0-100
    
    # 关键依据
    key_findings: List[str] = field(default_factory=list)
    metric_grades: Dict[str, str] = field(default_factory=dict)
    compliance_rate: float = 0.0
    volatility_level: str = "normal"
    baseline_deviation: Optional[float] = None
    
    # 详细信息
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'disease_name': self.disease_name,
            'control_status': self.control_status.value,
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'control_quality_score': self.control_quality_score,
            'key_findings': self.key_findings,
            'metric_grades': self.metric_grades,
            'compliance_rate': self.compliance_rate,
            'volatility_level': self.volatility_level,
            'baseline_deviation': self.baseline_deviation,
            'details': self.details
        }


class SimplifiedFuzzyLogic:
    """简化的模糊逻辑实现（当skfuzzy不可用时）"""
    
    @staticmethod
    def trimf(x: float, params: List[float]) -> float:
        """三角隶属度函数"""
        a, b, c = params
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        else:  # b < x < c
            return (c - x) / (c - b) if c != b else 1.0
    
    @staticmethod
    def trapmf(x: float, params: List[float]) -> float:
        """梯形隶属度函数"""
        a, b, c, d = params
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b < x <= c:
            return 1.0
        else:  # c < x < d
            return (d - x) / (d - c) if d != c else 1.0
    
    @staticmethod
    def fuzzy_and(memberships: List[float]) -> float:
        """模糊AND操作（取最小值）"""
        return min(memberships)
    
    @staticmethod
    def fuzzy_or(memberships: List[float]) -> float:
        """模糊OR操作（取最大值）"""
        return max(memberships)


class HypertensionAssessor:
    """高血压风险评估器"""
    
    def __init__(self):
        self.fuzzy = SimplifiedFuzzyLogic()
        
        # 血压分级标准（中国高血压指南）
        self.sbp_thresholds = {
            'normal': (0, 120),
            'elevated': (120, 140),
            'stage1': (140, 160),
            'stage2': (160, 180),
            'stage3': (180, 300)
        }
        
        self.dbp_thresholds = {
            'normal': (0, 80),
            'elevated': (80, 90),
            'stage1': (90, 100),
            'stage2': (100, 110),
            'stage3': (110, 200)
        }
    
    def assess(
        self,
        features: Dict,
        baseline: Optional[Dict] = None
    ) -> DiseaseRiskResult:
        """
        评估高血压风险
        
        Args:
            features: 特征字典（来自FeatureSet）
            baseline: 基线数据
        
        Returns:
            高血压风险评估结果
        """
        result = DiseaseRiskResult(
            disease_name="高血压",
            control_status=ControlStatus.GOOD,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            control_quality_score=0.0
        )
        
        # 1. 阈值分级
        sbp_mean = features.get('sbp_mean', 120)
        dbp_mean = features.get('dbp_mean', 80)
        
        sbp_grade = self._classify_sbp(sbp_mean)
        dbp_grade = self._classify_dbp(dbp_mean)
        
        result.metric_grades = {
            'sbp': sbp_grade,
            'dbp': dbp_grade
        }
        
        # 2. 计算达标率
        compliance_rate = features.get('sbp_compliance_rate', 1.0)
        result.compliance_rate = compliance_rate
        
        # 3. 计算波动性
        sbp_cv = features.get('sbp_cv', 0.0)
        volatility = self._assess_volatility(sbp_cv)
        result.volatility_level = volatility
        
        # 4. 计算与基线的偏离
        if baseline and 'sbp_mean' in baseline:
            baseline_sbp = baseline['sbp_mean']
            deviation = sbp_mean - baseline_sbp
            result.baseline_deviation = deviation
        
        # 5. 模糊逻辑综合评估
        control_score = self._calculate_control_score(
            sbp_mean, dbp_mean, compliance_rate, sbp_cv
        )
        result.control_quality_score = control_score
        
        # 6. 风险评分
        risk_score = self._calculate_risk_score(
            sbp_mean, dbp_mean, compliance_rate, sbp_cv, result.baseline_deviation
        )
        result.risk_score = risk_score
        
        # 7. 确定控制状态和风险等级
        result.control_status = self._determine_control_status(control_score)
        result.risk_level = self._determine_risk_level(risk_score)
        
        # 8. 生成关键发现
        result.key_findings = self._generate_key_findings(
            sbp_mean, dbp_mean, sbp_grade, compliance_rate, 
            volatility, result.baseline_deviation
        )
        
        # 9. 详细信息
        result.details = {
            'sbp_mean': sbp_mean,
            'dbp_mean': dbp_mean,
            'sbp_std': features.get('sbp_std', 0),
            'sbp_max': features.get('sbp_max', 0),
            'sbp_min': features.get('sbp_min', 0),
            'sbp_trend': features.get('sbp_trend', 0)
        }
        
        return result
    
    def _classify_sbp(self, sbp: float) -> str:
        """收缩压分级"""
        if sbp < 120:
            return "正常"
        elif sbp < 140:
            return "正常高值"
        elif sbp < 160:
            return "1级高血压"
        elif sbp < 180:
            return "2级高血压"
        else:
            return "3级高血压"
    
    def _classify_dbp(self, dbp: float) -> str:
        """舒张压分级"""
        if dbp < 80:
            return "正常"
        elif dbp < 90:
            return "正常高值"
        elif dbp < 100:
            return "1级高血压"
        elif dbp < 110:
            return "2级高血压"
        else:
            return "3级高血压"
    
    def _assess_volatility(self, cv: float) -> str:
        """评估波动性"""
        if cv < 0.1:
            return "稳定"
        elif cv < 0.15:
            return "轻度波动"
        elif cv < 0.2:
            return "中度波动"
        else:
            return "严重波动"
    
    def _calculate_control_score(
        self,
        sbp: float,
        dbp: float,
        compliance_rate: float,
        cv: float
    ) -> float:
        """
        计算控制质量评分（使用平滑模糊逻辑）
        
        评分规则：
        - 达标率越高越好
        - 波动越小越好
        - 血压值越接近正常越好
        
        优化：在边界处使用线性插值，避免硬切割跳变
        """
        # 达标率得分 (0-40分) - 本身就是连续的
        compliance_score = compliance_rate * 40
        
        # 稳定性得分 (0-30分) - 使用平滑过渡
        stability_score = self._smooth_stability_score(cv)
        
        # 血压水平得分 (0-30分) - 使用平滑过渡
        bp_score = self._smooth_bp_score(sbp, dbp)
        
        total_score = compliance_score + stability_score + bp_score
        return min(100, total_score)
    
    def _smooth_stability_score(self, cv: float) -> float:
        """
        平滑的稳定性评分（减少边界跳变）
        
        使用线性插值在边界处平滑过渡：
        - CV < 0.08: 30分（完全稳定）
        - CV 0.08-0.12: 30→20分（线性过渡）
        - CV 0.12-0.17: 20→10分（线性过渡）
        - CV 0.17-0.22: 10→0分（线性过渡）
        - CV > 0.22: 0分（严重波动）
        """
        if cv < 0.08:
            return 30.0
        elif cv < 0.12:
            # 从30分线性降到20分
            return 30.0 - (cv - 0.08) / 0.04 * 10.0
        elif cv < 0.17:
            # 从20分线性降到10分
            return 20.0 - (cv - 0.12) / 0.05 * 10.0
        elif cv < 0.22:
            # 从10分线性降到0分
            return 10.0 - (cv - 0.17) / 0.05 * 10.0
        else:
            return 0.0
    
    def _smooth_bp_score(self, sbp: float, dbp: float) -> float:
        """
        平滑的血压水平评分（减少边界跳变）
        
        使用线性插值在边界处平滑过渡：
        - 正常血压: 30分
        - 正常高值: 20-30分（渐变）
        - 1级高血压: 10-20分（渐变）
        - 2级及以上: 0-10分（渐变）
        """
        # 分别计算收缩压和舒张压的得分，取较低者
        sbp_score = self._smooth_sbp_score(sbp)
        dbp_score = self._smooth_dbp_score(dbp)
        
        # 取两者中较低的分数（更保守的评估）
        return min(sbp_score, dbp_score)
    
    def _smooth_sbp_score(self, sbp: float) -> float:
        """收缩压平滑评分"""
        if sbp < 115:
            return 30.0
        elif sbp < 125:
            # 115-125: 从30分渐变到25分
            return 30.0 - (sbp - 115) / 10.0 * 5.0
        elif sbp < 135:
            # 125-135: 从25分渐变到20分
            return 25.0 - (sbp - 125) / 10.0 * 5.0
        elif sbp < 145:
            # 135-145: 从20分渐变到15分
            return 20.0 - (sbp - 135) / 10.0 * 5.0
        elif sbp < 155:
            # 145-155: 从15分渐变到10分
            return 15.0 - (sbp - 145) / 10.0 * 5.0
        elif sbp < 170:
            # 155-170: 从10分渐变到5分
            return 10.0 - (sbp - 155) / 15.0 * 5.0
        elif sbp < 185:
            # 170-185: 从5分渐变到0分
            return 5.0 - (sbp - 170) / 15.0 * 5.0
        else:
            return 0.0
    
    def _smooth_dbp_score(self, dbp: float) -> float:
        """舒张压平滑评分"""
        if dbp < 75:
            return 30.0
        elif dbp < 82:
            # 75-82: 从30分渐变到25分
            return 30.0 - (dbp - 75) / 7.0 * 5.0
        elif dbp < 87:
            # 82-87: 从25分渐变到20分
            return 25.0 - (dbp - 82) / 5.0 * 5.0
        elif dbp < 93:
            # 87-93: 从20分渐变到15分
            return 20.0 - (dbp - 87) / 6.0 * 5.0
        elif dbp < 98:
            # 93-98: 从15分渐变到10分
            return 15.0 - (dbp - 93) / 5.0 * 5.0
        elif dbp < 105:
            # 98-105: 从10分渐变到5分
            return 10.0 - (dbp - 98) / 7.0 * 5.0
        elif dbp < 115:
            # 105-115: 从5分渐变到0分
            return 5.0 - (dbp - 105) / 10.0 * 5.0
        else:
            return 0.0
    
    def _calculate_risk_score(
        self,
        sbp: float,
        dbp: float,
        compliance_rate: float,
        cv: float,
        baseline_deviation: Optional[float]
    ) -> float:
        """
        计算风险评分（0-100，越高风险越大）
        
        优化：在边界处使用线性插值，避免硬切割跳变
        """
        risk_score = 0.0
        
        # 血压水平风险 (0-40分) - 使用平滑过渡
        risk_score += self._smooth_bp_risk(sbp, dbp)
        
        # 达标率风险 (0-25分) - 本身就是连续的
        risk_score += (1 - compliance_rate) * 25
        
        # 波动性风险 (0-20分) - 使用平滑过渡
        risk_score += self._smooth_cv_risk(cv)
        
        # 趋势风险 (0-15分) - 使用平滑过渡
        if baseline_deviation is not None:
            risk_score += self._smooth_trend_risk(baseline_deviation)
        
        return min(100, risk_score)
    
    def _smooth_bp_risk(self, sbp: float, dbp: float) -> float:
        """
        平滑的血压水平风险评分
        
        使用线性插值在边界处平滑过渡：
        - SBP < 125 或 DBP < 82: 0分
        - SBP 125-135 或 DBP 82-87: 0→10分
        - SBP 135-145 或 DBP 87-93: 10→20分
        - SBP 145-165 或 DBP 93-103: 20→30分
        - SBP 165-185 或 DBP 103-115: 30→40分
        - SBP >= 185 或 DBP >= 115: 40分
        """
        sbp_risk = self._smooth_sbp_risk(sbp)
        dbp_risk = self._smooth_dbp_risk(dbp)
        
        # 取两者中较高的风险（更保守的评估）
        return max(sbp_risk, dbp_risk)
    
    def _smooth_sbp_risk(self, sbp: float) -> float:
        """收缩压平滑风险评分"""
        if sbp < 125:
            return 0.0
        elif sbp < 135:
            # 125-135: 从0分渐变到10分
            return (sbp - 125) / 10.0 * 10.0
        elif sbp < 145:
            # 135-145: 从10分渐变到20分
            return 10.0 + (sbp - 135) / 10.0 * 10.0
        elif sbp < 165:
            # 145-165: 从20分渐变到30分
            return 20.0 + (sbp - 145) / 20.0 * 10.0
        elif sbp < 185:
            # 165-185: 从30分渐变到40分
            return 30.0 + (sbp - 165) / 20.0 * 10.0
        else:
            return 40.0
    
    def _smooth_dbp_risk(self, dbp: float) -> float:
        """舒张压平滑风险评分"""
        if dbp < 82:
            return 0.0
        elif dbp < 87:
            # 82-87: 从0分渐变到10分
            return (dbp - 82) / 5.0 * 10.0
        elif dbp < 93:
            # 87-93: 从10分渐变到20分
            return 10.0 + (dbp - 87) / 6.0 * 10.0
        elif dbp < 103:
            # 93-103: 从20分渐变到30分
            return 20.0 + (dbp - 93) / 10.0 * 10.0
        elif dbp < 115:
            # 103-115: 从30分渐变到40分
            return 30.0 + (dbp - 103) / 12.0 * 10.0
        else:
            return 40.0
    
    def _smooth_cv_risk(self, cv: float) -> float:
        """
        平滑的波动性风险评分
        
        使用线性插值在边界处平滑过渡：
        - CV < 0.08: 0分
        - CV 0.08-0.12: 0→10分
        - CV 0.12-0.17: 10→15分
        - CV 0.17-0.22: 15→20分
        - CV >= 0.22: 20分
        """
        if cv < 0.08:
            return 0.0
        elif cv < 0.12:
            # 从0分渐变到10分
            return (cv - 0.08) / 0.04 * 10.0
        elif cv < 0.17:
            # 从10分渐变到15分
            return 10.0 + (cv - 0.12) / 0.05 * 5.0
        elif cv < 0.22:
            # 从15分渐变到20分
            return 15.0 + (cv - 0.17) / 0.05 * 5.0
        else:
            return 20.0
    
    def _smooth_trend_risk(self, baseline_deviation: float) -> float:
        """
        平滑的趋势风险评分
        
        使用线性插值在边界处平滑过渡：
        - 偏离 <= 0: 0分
        - 偏离 0-5: 0→5分
        - 偏离 5-10: 5→10分
        - 偏离 10-15: 10→15分
        - 偏离 >= 15: 15分
        """
        if baseline_deviation <= 0:
            return 0.0
        elif baseline_deviation < 5:
            # 从0分渐变到5分
            return baseline_deviation / 5.0 * 5.0
        elif baseline_deviation < 10:
            # 从5分渐变到10分
            return 5.0 + (baseline_deviation - 5) / 5.0 * 5.0
        elif baseline_deviation < 15:
            # 从10分渐变到15分
            return 10.0 + (baseline_deviation - 10) / 5.0 * 5.0
        else:
            return 15.0
    
    def _determine_control_status(self, control_score: float) -> ControlStatus:
        """根据控制评分确定控制状态"""
        if control_score >= 80:
            return ControlStatus.EXCELLENT
        elif control_score >= 60:
            return ControlStatus.GOOD
        elif control_score >= 40:
            return ControlStatus.FAIR
        else:
            return ControlStatus.POOR
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """根据风险评分确定风险等级"""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MEDIUM
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _generate_key_findings(
        self,
        sbp: float,
        dbp: float,
        sbp_grade: str,
        compliance_rate: float,
        volatility: str,
        baseline_deviation: Optional[float]
    ) -> List[str]:
        """生成关键发现"""
        findings = []
        
        # 血压水平
        if sbp >= 140 or dbp >= 90:
            findings.append(f"平均血压处于{sbp_grade}水平（收缩压{sbp:.1f}mmHg，舒张压{dbp:.1f}mmHg）")
        
        # 达标率
        if compliance_rate < 0.5:
            findings.append(f"血压达标率较低（{compliance_rate*100:.1f}%），控制不佳")
        elif compliance_rate < 0.8:
            findings.append(f"血压达标率一般（{compliance_rate*100:.1f}%），需要改善")
        
        # 波动性
        if volatility in ["中度波动", "严重波动"]:
            findings.append(f"血压波动{volatility}，稳定性较差")
        
        # 趋势
        if baseline_deviation is not None and baseline_deviation > 5:
            findings.append(f"相比基线血压升高{baseline_deviation:.1f}mmHg，呈恶化趋势")
        
        if not findings:
            findings.append("血压控制良好，继续保持")
        
        return findings


class DiabetesAssessor:
    """糖代谢异常风险评估器"""
    
    def __init__(self):
        self.fuzzy = SimplifiedFuzzyLogic()
        
        # 血糖分级标准
        self.glucose_thresholds = {
            'normal_fasting': 6.1,
            'ifg': 7.0,  # 空腹血糖受损
            'diabetes': 7.0,
            'high_risk': 10.0
        }
    
    def assess(
        self,
        features: Dict,
        baseline: Optional[Dict] = None
    ) -> DiseaseRiskResult:
        """评估糖代谢异常风险"""
        result = DiseaseRiskResult(
            disease_name="糖代谢异常",
            control_status=ControlStatus.GOOD,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            control_quality_score=0.0
        )
        
        glucose_mean = features.get('glucose_mean', 5.5)
        glucose_cv = features.get('glucose_cv', 0.0)
        compliance_rate = features.get('glucose_compliance_rate', 1.0)
        
        # 分级
        glucose_grade = self._classify_glucose(glucose_mean)
        result.metric_grades = {'glucose': glucose_grade}
        result.compliance_rate = compliance_rate
        
        # 波动性
        volatility = self._assess_glucose_volatility(glucose_cv)
        result.volatility_level = volatility
        
        # 基线偏离
        if baseline and 'glucose_mean' in baseline:
            deviation = glucose_mean - baseline['glucose_mean']
            result.baseline_deviation = deviation
        
        # 控制评分
        control_score = self._calculate_control_score(
            glucose_mean, compliance_rate, glucose_cv
        )
        result.control_quality_score = control_score
        
        # 风险评分
        risk_score = self._calculate_risk_score(
            glucose_mean, compliance_rate, glucose_cv, result.baseline_deviation
        )
        result.risk_score = risk_score
        
        # 状态和等级
        result.control_status = self._determine_control_status(control_score)
        result.risk_level = self._determine_risk_level(risk_score)
        
        # 关键发现
        result.key_findings = self._generate_key_findings(
            glucose_mean, glucose_grade, compliance_rate, 
            volatility, result.baseline_deviation
        )
        
        result.details = {
            'glucose_mean': glucose_mean,
            'glucose_std': features.get('glucose_std', 0),
            'glucose_max': features.get('glucose_max', 0),
            'glucose_cv': glucose_cv
        }
        
        return result
    
    def _classify_glucose(self, glucose: float) -> str:
        """血糖分级"""
        if glucose < 6.1:
            return "正常"
        elif glucose < 7.0:
            return "空腹血糖受损"
        elif glucose < 10.0:
            return "糖尿病（控制中）"
        else:
            return "糖尿病（控制差）"
    
    def _assess_glucose_volatility(self, cv: float) -> str:
        """评估血糖波动"""
        if cv < 0.15:
            return "稳定"
        elif cv < 0.25:
            return "轻度波动"
        elif cv < 0.35:
            return "中度波动"
        else:
            return "严重波动"
    
    def _calculate_control_score(
        self,
        glucose: float,
        compliance_rate: float,
        cv: float
    ) -> float:
        """计算控制评分"""
        compliance_score = compliance_rate * 40
        
        if cv < 0.15:
            stability_score = 30
        elif cv < 0.25:
            stability_score = 20
        elif cv < 0.35:
            stability_score = 10
        else:
            stability_score = 0
        
        if glucose < 6.1:
            glucose_score = 30
        elif glucose < 7.0:
            glucose_score = 20
        elif glucose < 10.0:
            glucose_score = 10
        else:
            glucose_score = 0
        
        return min(100, compliance_score + stability_score + glucose_score)
    
    def _calculate_risk_score(
        self,
        glucose: float,
        compliance_rate: float,
        cv: float,
        baseline_deviation: Optional[float]
    ) -> float:
        """计算风险评分"""
        risk_score = 0.0
        
        if glucose >= 10.0:
            risk_score += 40
        elif glucose >= 7.0:
            risk_score += 25
        elif glucose >= 6.1:
            risk_score += 15
        
        risk_score += (1 - compliance_rate) * 25
        
        if cv >= 0.35:
            risk_score += 20
        elif cv >= 0.25:
            risk_score += 15
        elif cv >= 0.15:
            risk_score += 10
        
        if baseline_deviation is not None and baseline_deviation > 1.0:
            risk_score += 15
        
        return min(100, risk_score)
    
    def _determine_control_status(self, control_score: float) -> ControlStatus:
        """确定控制状态"""
        if control_score >= 80:
            return ControlStatus.EXCELLENT
        elif control_score >= 60:
            return ControlStatus.GOOD
        elif control_score >= 40:
            return ControlStatus.FAIR
        else:
            return ControlStatus.POOR
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """确定风险等级"""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MEDIUM
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _generate_key_findings(
        self,
        glucose: float,
        glucose_grade: str,
        compliance_rate: float,
        volatility: str,
        baseline_deviation: Optional[float]
    ) -> List[str]:
        """生成关键发现"""
        findings = []
        
        if glucose >= 7.0:
            findings.append(f"平均血糖处于{glucose_grade}水平（{glucose:.1f}mmol/L）")
        
        if compliance_rate < 0.6:
            findings.append(f"血糖达标率低（{compliance_rate*100:.1f}%）")
        
        if volatility in ["中度波动", "严重波动"]:
            findings.append(f"血糖{volatility}，需要关注")
        
        if baseline_deviation is not None and baseline_deviation > 1.0:
            findings.append(f"血糖相比基线升高{baseline_deviation:.1f}mmol/L")
        
        if not findings:
            findings.append("血糖控制良好")
        
        return findings


class DyslipidemiAssessor:
    """血脂异常风险评估器"""
    
    def __init__(self):
        # 血脂标准（mmol/L）
        self.thresholds = {
            'tc_normal': 5.2,
            'tc_borderline': 6.2,
            'ldl_optimal': 3.4,
            'ldl_borderline': 4.1,
            'hdl_low': 1.0,
            'tg_normal': 1.7,
            'tg_borderline': 2.3
        }
    
    def assess(
        self,
        features: Dict,
        baseline: Optional[Dict] = None
    ) -> DiseaseRiskResult:
        """评估血脂异常风险"""
        result = DiseaseRiskResult(
            disease_name="血脂异常",
            control_status=ControlStatus.GOOD,
            risk_level=RiskLevel.LOW,
            risk_score=0.0,
            control_quality_score=70.0  # 默认良好
        )
        
        tc = features.get('tc_mean', 5.0)
        ldl = features.get('ldl_mean', 3.0)
        hdl = features.get('hdl_mean', 1.2)
        tg = features.get('tg_mean', 1.5)
        
        # 分级
        result.metric_grades = {
            'tc': self._classify_tc(tc),
            'ldl': self._classify_ldl(ldl),
            'hdl': self._classify_hdl(hdl),
            'tg': self._classify_tg(tg)
        }
        
        # 风险评分
        risk_score = self._calculate_risk_score(tc, ldl, hdl, tg)
        result.risk_score = risk_score
        result.risk_level = self._determine_risk_level(risk_score)
        
        # 关键发现
        result.key_findings = self._generate_key_findings(tc, ldl, hdl, tg)
        
        result.details = {'tc': tc, 'ldl': ldl, 'hdl': hdl, 'tg': tg}
        
        return result
    
    def _classify_tc(self, tc: float) -> str:
        """总胆固醇分级"""
        if tc < 5.2:
            return "合适"
        elif tc < 6.2:
            return "边缘升高"
        else:
            return "升高"
    
    def _classify_ldl(self, ldl: float) -> str:
        """低密度脂蛋白分级"""
        if ldl < 3.4:
            return "合适"
        elif ldl < 4.1:
            return "边缘升高"
        else:
            return "升高"
    
    def _classify_hdl(self, hdl: float) -> str:
        """高密度脂蛋白分级"""
        if hdl < 1.0:
            return "降低"
        else:
            return "正常"
    
    def _classify_tg(self, tg: float) -> str:
        """甘油三酯分级"""
        if tg < 1.7:
            return "合适"
        elif tg < 2.3:
            return "边缘升高"
        else:
            return "升高"
    
    def _calculate_risk_score(
        self,
        tc: float,
        ldl: float,
        hdl: float,
        tg: float
    ) -> float:
        """计算风险评分"""
        risk_score = 0.0
        
        # TC风险
        if tc >= 6.2:
            risk_score += 20
        elif tc >= 5.2:
            risk_score += 10
        
        # LDL风险
        if ldl >= 4.1:
            risk_score += 25
        elif ldl >= 3.4:
            risk_score += 15
        
        # HDL风险（低HDL是风险因素）
        if hdl < 1.0:
            risk_score += 20
        
        # TG风险
        if tg >= 2.3:
            risk_score += 20
        elif tg >= 1.7:
            risk_score += 10
        
        return min(100, risk_score)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """确定风险等级"""
        if risk_score < 20:
            return RiskLevel.LOW
        elif risk_score < 40:
            return RiskLevel.MEDIUM
        elif risk_score < 60:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _generate_key_findings(
        self,
        tc: float,
        ldl: float,
        hdl: float,
        tg: float
    ) -> List[str]:
        """生成关键发现"""
        findings = []
        
        if tc >= 6.2:
            findings.append(f"总胆固醇升高（{tc:.2f}mmol/L）")
        if ldl >= 4.1:
            findings.append(f"低密度脂蛋白升高（{ldl:.2f}mmol/L）")
        if hdl < 1.0:
            findings.append(f"高密度脂蛋白偏低（{hdl:.2f}mmol/L）")
        if tg >= 2.3:
            findings.append(f"甘油三酯升高（{tg:.2f}mmol/L）")
        
        if not findings:
            findings.append("血脂水平正常")
        
        return findings


# 使用示例
if __name__ == "__main__":
    # 模拟特征数据
    features = {
        'sbp_mean': 145,
        'dbp_mean': 92,
        'sbp_std': 12,
        'sbp_cv': 0.08,
        'sbp_compliance_rate': 0.6,
        'sbp_trend': 0.5
    }
    
    baseline = {
        'sbp_mean': 135
    }
    
    # 高血压评估
    ht_assessor = HypertensionAssessor()
    ht_result = ht_assessor.assess(features, baseline)
    
    print("高血压风险评估结果:")
    print(f"控制状态: {ht_result.control_status.value}")
    print(f"风险等级: {ht_result.risk_level.value}")
    print(f"风险评分: {ht_result.risk_score:.1f}")
    print(f"控制质量评分: {ht_result.control_quality_score:.1f}")
    print(f"关键发现: {ht_result.key_findings}")
