"""
健康趋势预警模块
Health Trend Alert Module

功能：
- 血压/血糖/心率趋势检测
- 连续异常告警
- 波动加剧预警
- 长期趋势分析

算法：
- 线性回归（趋势斜率）
- 移动平均（平滑处理）
- 变异系数（波动检测）
- 规则引擎（告警触发）
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class AlertLevel(Enum):
    """告警级别"""
    NORMAL = "normal"          # 正常
    ATTENTION = "attention"    # 关注
    WARNING = "warning"        # 警告
    CRITICAL = "critical"      # 紧急


class TrendDirection(Enum):
    """趋势方向"""
    RISING = "rising"          # 上升
    FALLING = "falling"        # 下降
    STABLE = "stable"          # 稳定
    VOLATILE = "volatile"      # 波动


@dataclass
class TrendAlert:
    """趋势告警"""
    metric_name: str           # 指标名称
    alert_level: AlertLevel    # 告警级别
    trend_direction: TrendDirection  # 趋势方向
    message: str               # 告警消息
    suggestion: str            # 建议措施
    
    # 详细数据
    current_value: float = 0.0
    avg_value: float = 0.0
    trend_slope: float = 0.0   # 趋势斜率（每天变化量）
    volatility: float = 0.0    # 波动性（变异系数）
    consecutive_abnormal: int = 0  # 连续异常天数
    
    # 时间信息
    alert_time: datetime = field(default_factory=datetime.now)
    data_period: str = ""      # 数据周期描述
    
    def to_dict(self) -> Dict:
        return {
            'metric_name': self.metric_name,
            'alert_level': self.alert_level.value,
            'trend_direction': self.trend_direction.value,
            'message': self.message,
            'suggestion': self.suggestion,
            'current_value': float(self.current_value),
            'avg_value': float(self.avg_value),
            'trend_slope': float(self.trend_slope),
            'volatility': float(self.volatility),
            'consecutive_abnormal': int(self.consecutive_abnormal),
            'alert_time': self.alert_time.isoformat(),
            'data_period': self.data_period
        }


@dataclass
class MetricThreshold:
    """指标阈值配置"""
    name: str
    unit: str
    normal_low: float
    normal_high: float
    warning_low: float
    warning_high: float
    critical_low: float
    critical_high: float
    
    # 趋势阈值
    trend_slope_warning: float = 2.0    # 每天变化超过此值告警
    volatility_warning: float = 0.15    # 变异系数超过此值告警
    consecutive_days_warning: int = 3   # 连续异常天数告警


class HealthTrendAnalyzer:
    """
    健康趋势分析器
    
    核心功能：
    1. 检测指标上升/下降趋势
    2. 识别波动加剧
    3. 统计连续异常天数
    4. 生成分级告警
    """
    
    def __init__(self):
        # 初始化各指标阈值配置
        self.thresholds = self._init_thresholds()
    
    def _init_thresholds(self) -> Dict[str, MetricThreshold]:
        """初始化阈值配置（针对老年人）"""
        return {
            'systolic_bp': MetricThreshold(
                name='收缩压',
                unit='mmHg',
                normal_low=90,
                normal_high=140,
                warning_low=85,
                warning_high=160,
                critical_low=80,
                critical_high=180,
                trend_slope_warning=3.0,      # 每天上升3mmHg告警
                volatility_warning=0.12,
                consecutive_days_warning=3
            ),
            'diastolic_bp': MetricThreshold(
                name='舒张压',
                unit='mmHg',
                normal_low=60,
                normal_high=90,
                warning_low=55,
                warning_high=100,
                critical_low=50,
                critical_high=110,
                trend_slope_warning=2.0,
                volatility_warning=0.12,
                consecutive_days_warning=3
            ),
            'blood_sugar': MetricThreshold(
                name='血糖',
                unit='mmol/L',
                normal_low=3.9,
                normal_high=7.0,
                warning_low=3.5,
                warning_high=10.0,
                critical_low=3.0,
                critical_high=13.9,
                trend_slope_warning=0.5,      # 每天上升0.5mmol/L告警
                volatility_warning=0.20,
                consecutive_days_warning=3
            ),
            'heart_rate': MetricThreshold(
                name='心率',
                unit='次/分',
                normal_low=60,
                normal_high=100,
                warning_low=50,
                warning_high=110,
                critical_low=45,
                critical_high=120,
                trend_slope_warning=5.0,
                volatility_warning=0.15,
                consecutive_days_warning=2
            ),
            'spo2': MetricThreshold(
                name='血氧',
                unit='%',
                normal_low=95,
                normal_high=100,
                warning_low=92,
                warning_high=100,
                critical_low=90,
                critical_high=100,
                trend_slope_warning=1.0,      # 每天下降1%告警
                volatility_warning=0.05,
                consecutive_days_warning=2
            )
        }
    
    def analyze_trend(
        self,
        metric_name: str,
        values: List[float],
        timestamps: Optional[List[datetime]] = None,
        window_days: int = 7
    ) -> TrendAlert:
        """
        分析单个指标的趋势
        
        Args:
            metric_name: 指标名称
            values: 指标值列表（按时间顺序）
            timestamps: 时间戳列表
            window_days: 分析窗口天数
            
        Returns:
            TrendAlert: 趋势告警结果
        """
        if metric_name not in self.thresholds:
            raise ValueError(f"未知指标: {metric_name}")
        
        threshold = self.thresholds[metric_name]
        values = np.array(values)
        
        if len(values) < 3:
            return TrendAlert(
                metric_name=threshold.name,
                alert_level=AlertLevel.NORMAL,
                trend_direction=TrendDirection.STABLE,
                message="数据不足，无法分析趋势",
                suggestion="请继续记录健康数据",
                current_value=values[-1] if len(values) > 0 else 0
            )
        
        # 1. 计算基础统计量
        current_value = values[-1]
        avg_value = np.mean(values)
        std_value = np.std(values)
        volatility = std_value / avg_value if avg_value != 0 else 0
        
        # 2. 计算趋势斜率（线性回归）
        trend_slope = self._calculate_trend_slope(values)
        
        # 3. 统计连续异常天数
        consecutive_abnormal = self._count_consecutive_abnormal(
            values, threshold.normal_low, threshold.normal_high
        )
        
        # 4. 判断趋势方向
        trend_direction = self._determine_trend_direction(
            trend_slope, volatility, threshold
        )
        
        # 5. 确定告警级别
        alert_level, message, suggestion = self._determine_alert(
            current_value, trend_slope, volatility, 
            consecutive_abnormal, trend_direction, threshold
        )
        
        # 6. 构建告警结果
        return TrendAlert(
            metric_name=threshold.name,
            alert_level=alert_level,
            trend_direction=trend_direction,
            message=message,
            suggestion=suggestion,
            current_value=round(current_value, 1),
            avg_value=round(avg_value, 1),
            trend_slope=round(trend_slope, 2),
            volatility=round(volatility, 3),
            consecutive_abnormal=consecutive_abnormal,
            data_period=f"近{len(values)}次测量"
        )
    
    def _calculate_trend_slope(self, values: np.ndarray) -> float:
        """
        计算趋势斜率（简单线性回归）
        
        返回每个时间单位的变化量
        """
        n = len(values)
        x = np.arange(n)
        
        # 最小二乘法
        x_mean = np.mean(x)
        y_mean = np.mean(values)
        
        numerator = np.sum((x - x_mean) * (values - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def _count_consecutive_abnormal(
        self, 
        values: np.ndarray,
        normal_low: float,
        normal_high: float
    ) -> int:
        """统计末尾连续异常天数"""
        count = 0
        for value in reversed(values):
            if value < normal_low or value > normal_high:
                count += 1
            else:
                break
        return count
    
    def _determine_trend_direction(
        self,
        slope: float,
        volatility: float,
        threshold: MetricThreshold
    ) -> TrendDirection:
        """判断趋势方向"""
        # 波动性过高
        if volatility > threshold.volatility_warning:
            return TrendDirection.VOLATILE
        
        # 根据斜率判断
        slope_threshold = threshold.trend_slope_warning * 0.5  # 一半阈值作为判断标准
        
        if slope > slope_threshold:
            return TrendDirection.RISING
        elif slope < -slope_threshold:
            return TrendDirection.FALLING
        else:
            return TrendDirection.STABLE
    
    def _determine_alert(
        self,
        current_value: float,
        slope: float,
        volatility: float,
        consecutive_abnormal: int,
        trend_direction: TrendDirection,
        threshold: MetricThreshold
    ) -> Tuple[AlertLevel, str, str]:
        """确定告警级别、消息和建议"""
        
        name = threshold.name
        unit = threshold.unit
        
        # 紧急告警：当前值超出危险范围
        if current_value <= threshold.critical_low:
            return (
                AlertLevel.CRITICAL,
                f"⚠️ {name}过低！当前{current_value}{unit}，已低于安全下限",
                "请立即就医或联系家属！"
            )
        if current_value >= threshold.critical_high:
            return (
                AlertLevel.CRITICAL,
                f"⚠️ {name}过高！当前{current_value}{unit}，已超出安全上限",
                "请立即就医或联系家属！"
            )
        
        # 警告：连续多天异常
        if consecutive_abnormal >= threshold.consecutive_days_warning:
            direction_text = "偏高" if current_value > threshold.normal_high else "偏低"
            return (
                AlertLevel.WARNING,
                f"📊 {name}连续{consecutive_abnormal}天{direction_text}",
                f"建议尽快就医检查，调整治疗方案"
            )
        
        # 警告：趋势斜率过大
        if abs(slope) >= threshold.trend_slope_warning:
            if slope > 0:
                return (
                    AlertLevel.WARNING,
                    f"📈 {name}持续上升，平均每天上升{abs(slope):.1f}{unit}",
                    "请注意休息，避免情绪激动，必要时就医"
                )
            else:
                return (
                    AlertLevel.WARNING,
                    f"📉 {name}持续下降，平均每天下降{abs(slope):.1f}{unit}",
                    "请注意营养摄入，必要时就医检查"
                )
        
        # 关注：波动性过高
        if volatility >= threshold.volatility_warning:
            return (
                AlertLevel.ATTENTION,
                f"〰️ {name}波动较大，变异系数{volatility*100:.1f}%",
                "建议保持规律作息，定时测量，观察变化"
            )
        
        # 关注：当前值在警告范围
        if current_value <= threshold.warning_low or current_value >= threshold.warning_high:
            direction_text = "偏高" if current_value > threshold.normal_high else "偏低"
            return (
                AlertLevel.ATTENTION,
                f"📋 {name}当前{direction_text}：{current_value}{unit}",
                "请继续监测，注意生活方式调整"
            )
        
        # 正常
        return (
            AlertLevel.NORMAL,
            f"✅ {name}正常，当前{current_value}{unit}",
            "请继续保持良好的生活习惯"
        )
    
    def analyze_all_metrics(
        self,
        health_data: Dict[str, List[float]]
    ) -> List[TrendAlert]:
        """
        分析所有指标的趋势
        
        Args:
            health_data: 健康数据字典，key为指标名，value为值列表
            
        Returns:
            List[TrendAlert]: 所有告警列表（按严重程度排序）
        """
        alerts = []
        
        for metric_name, values in health_data.items():
            if metric_name in self.thresholds and len(values) >= 3:
                alert = self.analyze_trend(metric_name, values)
                alerts.append(alert)
        
        # 按告警级别排序（紧急 > 警告 > 关注 > 正常）
        level_order = {
            AlertLevel.CRITICAL: 0,
            AlertLevel.WARNING: 1,
            AlertLevel.ATTENTION: 2,
            AlertLevel.NORMAL: 3
        }
        alerts.sort(key=lambda x: level_order[x.alert_level])
        
        return alerts
    
    def generate_alert_summary(
        self,
        alerts: List[TrendAlert]
    ) -> Dict:
        """
        生成告警摘要
        
        Returns:
            包含统计信息和建议的摘要字典
        """
        summary = {
            'total_alerts': len(alerts),
            'critical_count': 0,
            'warning_count': 0,
            'attention_count': 0,
            'normal_count': 0,
            'overall_status': '正常',
            'priority_alerts': [],
            'suggestions': []
        }
        
        for alert in alerts:
            if alert.alert_level == AlertLevel.CRITICAL:
                summary['critical_count'] += 1
            elif alert.alert_level == AlertLevel.WARNING:
                summary['warning_count'] += 1
            elif alert.alert_level == AlertLevel.ATTENTION:
                summary['attention_count'] += 1
            else:
                summary['normal_count'] += 1
        
        # 确定整体状态
        if summary['critical_count'] > 0:
            summary['overall_status'] = '紧急'
            summary['suggestions'].append("存在紧急健康风险，请立即处理！")
        elif summary['warning_count'] > 0:
            summary['overall_status'] = '警告'
            summary['suggestions'].append("存在健康警告，建议尽快就医检查")
        elif summary['attention_count'] > 0:
            summary['overall_status'] = '关注'
            summary['suggestions'].append("部分指标需要关注，请继续监测")
        else:
            summary['overall_status'] = '正常'
            summary['suggestions'].append("各项指标正常，请继续保持")
        
        # 提取优先告警（非正常的）
        summary['priority_alerts'] = [
            alert.to_dict() for alert in alerts 
            if alert.alert_level != AlertLevel.NORMAL
        ][:5]  # 最多5条
        
        return summary


class ElderlyActivityMonitor:
    """
    老年人活动监测器
    
    检测异常活动模式：
    - 长时间未活动
    - 夜间频繁起床
    - 活动量骤降
    """
    
    def __init__(self):
        # 活动阈值配置
        self.inactive_threshold_hours = 4      # 白天超过4小时未活动告警
        self.night_wakeup_threshold = 3        # 夜间起床超过3次告警
        self.activity_drop_threshold = 0.5     # 活动量下降超过50%告警
    
    def check_inactivity(
        self,
        last_activity_time: datetime,
        current_time: Optional[datetime] = None
    ) -> Optional[TrendAlert]:
        """检查长时间未活动"""
        current_time = current_time or datetime.now()
        
        # 只在白天检测（6:00-22:00）
        if not (6 <= current_time.hour < 22):
            return None
        
        inactive_hours = (current_time - last_activity_time).total_seconds() / 3600
        
        if inactive_hours >= self.inactive_threshold_hours:
            return TrendAlert(
                metric_name="活动状态",
                alert_level=AlertLevel.WARNING,
                trend_direction=TrendDirection.STABLE,
                message=f"⚠️ 已超过{inactive_hours:.1f}小时未检测到活动",
                suggestion="请确认老人状态，必要时上门查看",
                current_value=inactive_hours
            )
        
        return None
    
    def check_night_wakeups(
        self,
        wakeup_times: List[datetime]
    ) -> Optional[TrendAlert]:
        """检查夜间频繁起床"""
        # 筛选夜间时段（22:00-6:00）
        night_wakeups = [
            t for t in wakeup_times 
            if t.hour >= 22 or t.hour < 6
        ]
        
        if len(night_wakeups) >= self.night_wakeup_threshold:
            return TrendAlert(
                metric_name="夜间活动",
                alert_level=AlertLevel.ATTENTION,
                trend_direction=TrendDirection.VOLATILE,
                message=f"📋 夜间起床{len(night_wakeups)}次，睡眠可能受影响",
                suggestion="建议关注睡眠质量，必要时咨询医生",
                current_value=len(night_wakeups)
            )
        
        return None
    
    def check_activity_drop(
        self,
        recent_steps: List[int],
        baseline_steps: float
    ) -> Optional[TrendAlert]:
        """检查活动量骤降"""
        if len(recent_steps) < 3:
            return None
        
        recent_avg = np.mean(recent_steps[-3:])
        
        if baseline_steps > 0:
            drop_ratio = (baseline_steps - recent_avg) / baseline_steps
            
            if drop_ratio >= self.activity_drop_threshold:
                return TrendAlert(
                    metric_name="活动量",
                    alert_level=AlertLevel.WARNING,
                    trend_direction=TrendDirection.FALLING,
                    message=f"📉 近期活动量下降{drop_ratio*100:.0f}%",
                    suggestion="请关注老人身体状况，了解活动减少原因",
                    current_value=recent_avg,
                    avg_value=baseline_steps
                )
        
        return None


# 便捷函数
def analyze_health_trends(health_data: Dict[str, List[float]]) -> Dict:
    """
    分析健康趋势的便捷函数
    
    Args:
        health_data: {
            'systolic_bp': [130, 135, 138, 142, 145],
            'blood_sugar': [6.5, 6.8, 7.0, 6.9, 7.2],
            ...
        }
        
    Returns:
        包含告警和摘要的字典
    """
    analyzer = HealthTrendAnalyzer()
    alerts = analyzer.analyze_all_metrics(health_data)
    summary = analyzer.generate_alert_summary(alerts)
    
    return {
        'alerts': [a.to_dict() for a in alerts],
        'summary': summary
    }


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("健康趋势预警模块测试")
    print("=" * 60)
    
    # 模拟数据：血压持续上升
    test_data = {
        'systolic_bp': [128, 132, 135, 138, 142, 145, 148],  # 上升趋势
        'diastolic_bp': [82, 84, 83, 85, 86, 85, 87],        # 相对稳定
        'blood_sugar': [6.2, 6.5, 7.8, 6.3, 8.1, 6.0, 7.5],  # 波动大
        'heart_rate': [72, 75, 73, 74, 76, 75, 74],          # 正常
    }
    
    result = analyze_health_trends(test_data)
    
    print("\n📊 分析结果：")
    print(f"整体状态: {result['summary']['overall_status']}")
    print(f"紧急告警: {result['summary']['critical_count']}")
    print(f"警告: {result['summary']['warning_count']}")
    print(f"关注: {result['summary']['attention_count']}")
    
    print("\n📋 详细告警：")
    for alert in result['alerts']:
        level_icon = {
            'critical': '🔴',
            'warning': '🟡', 
            'attention': '🟠',
            'normal': '🟢'
        }
        icon = level_icon.get(alert['alert_level'], '⚪')
        print(f"{icon} [{alert['metric_name']}] {alert['message']}")
        print(f"   建议: {alert['suggestion']}")
