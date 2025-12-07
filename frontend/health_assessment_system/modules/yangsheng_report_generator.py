"""
养生之道·智能健康报告生成器
YangSheng Health Report Generator

负责生成符合模板格式的健康报告
"""

import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from .health_report_models import (
    HealthReportData, ElderBasicInfo, VitalSigns, MetabolicIndicators,
    TrendAnalysis, TrendStatistics, FeatureRecognition, BaselineComparison,
    VitalSignIndicator, IndicatorStatus
)
from .indicator_evaluator import IndicatorEvaluator, PersonalizedEvaluator
from scipy import stats as scipy_stats

# 尝试导入ruptures，如果没有则使用简化版本
try:
    import ruptures as rpt
    RUPTURES_AVAILABLE = True
except ImportError:
    RUPTURES_AVAILABLE = False


class YangShengReportGenerator:
    """
    养生之道健康报告生成器
    
    整合各模块数据，生成完整的健康报告
    """
    
    def __init__(self):
        self.evaluator = IndicatorEvaluator()
        self.personalized_evaluator = None
    
    def generate_report(
        self,
        elder_info: ElderBasicInfo,
        current_measurements: Dict,
        historical_data: Optional[Dict] = None,
        baseline_data: Optional[Dict] = None,
        trend_window_days: int = 30
    ) -> HealthReportData:
        """
        生成完整健康报告
        
        Args:
            elder_info: 老人基本信息
            current_measurements: 当前测量数据
            historical_data: 历史数据（用于趋势分析）
            baseline_data: 基线数据（用于对比）
            trend_window_days: 趋势分析时间窗口
        
        Returns:
            HealthReportData 完整报告数据
        """
        # 设置个性化评估器
        if baseline_data:
            self.personalized_evaluator = PersonalizedEvaluator(baseline_data)
        
        # 生成报告ID
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{elder_info.elder_id}"
        
        # 构建各部分数据
        vital_signs = self._build_vital_signs(current_measurements, elder_info.elder_gender)
        metabolic_indicators = self._build_metabolic_indicators(current_measurements, elder_info.elder_gender)
        trend_analysis = self._build_trend_analysis(historical_data, trend_window_days)
        feature_recognition = self._build_feature_recognition(
            current_measurements, historical_data, baseline_data
        )
        baseline_comparison = self._build_baseline_comparison(
            current_measurements, baseline_data
        )
        
        # 组装完整报告
        report = HealthReportData(
            report_id=report_id,
            report_date=datetime.now(),
            elder_info=elder_info,
            vital_signs=vital_signs,
            metabolic_indicators=metabolic_indicators,
            trend_analysis=trend_analysis,
            feature_recognition=feature_recognition,
            baseline_comparison=baseline_comparison
        )
        
        return report
    
    def _build_vital_signs(self, measurements: Dict, gender: str) -> VitalSigns:
        """构建生命体征数据"""
        vital_signs = VitalSigns()
        
        # 血氧
        if 'spo2' in measurements:
            vital_signs.spo2 = self.evaluator.create_vital_sign_indicator(
                'spo2', measurements['spo2'], gender
            )
        
        # 心率
        if 'heart_rate' in measurements:
            vital_signs.heart_rate = self.evaluator.create_vital_sign_indicator(
                'heart_rate', measurements['heart_rate'], gender
            )
        
        # 收缩压
        if 'systolic_bp' in measurements:
            vital_signs.systolic_bp = self.evaluator.create_vital_sign_indicator(
                'systolic_bp', measurements['systolic_bp'], gender
            )
        
        # 舒张压
        if 'diastolic_bp' in measurements:
            vital_signs.diastolic_bp = self.evaluator.create_vital_sign_indicator(
                'diastolic_bp', measurements['diastolic_bp'], gender
            )
        
        # 脉率
        if 'pulse_rate' in measurements:
            vital_signs.pulse_rate = self.evaluator.create_vital_sign_indicator(
                'pulse_rate', measurements['pulse_rate'], gender
            )
        
        # 体温
        if 'body_temperature' in measurements:
            vital_signs.body_temperature = self.evaluator.create_vital_sign_indicator(
                'body_temperature', measurements['body_temperature'], gender
            )
        
        return vital_signs
    
    def _build_metabolic_indicators(self, measurements: Dict, gender: str) -> MetabolicIndicators:
        """构建代谢指标数据"""
        metabolic = MetabolicIndicators()
        
        # 血糖
        if 'blood_sugar' in measurements:
            # 默认使用空腹血糖标准
            sugar_key = 'blood_sugar_fasting'
            if measurements.get('blood_sugar_type') == 'random':
                sugar_key = 'blood_sugar_random'
            
            status, status_text = self.evaluator.evaluate(sugar_key, measurements['blood_sugar'])
            metabolic.blood_sugar = VitalSignIndicator(
                name='血糖',
                value=measurements['blood_sugar'],
                unit='mmol/L',
                status=status,
                status_text=status_text
            )
        
        # 血尿酸
        if 'uric_acid' in measurements:
            metabolic.uric_acid = self.evaluator.create_vital_sign_indicator(
                'uric_acid', measurements['uric_acid'], gender
            )
        
        # 体重
        if 'weight' in measurements:
            metabolic.weight = VitalSignIndicator(
                name='体重',
                value=measurements['weight'],
                unit='kg',
                status=IndicatorStatus.NORMAL,
                status_text="已记录"
            )
        
        # BMI
        if 'bmi' in measurements:
            metabolic.bmi = self.evaluator.create_vital_sign_indicator(
                'bmi', measurements['bmi'], gender
            )
        elif 'weight' in measurements and 'height' in measurements:
            # 自动计算BMI
            height_m = measurements['height'] / 100
            bmi_value = measurements['weight'] / (height_m ** 2)
            metabolic.bmi = self.evaluator.create_vital_sign_indicator(
                'bmi', round(bmi_value, 1), gender
            )
        
        return metabolic
    
    def _build_trend_analysis(
        self, 
        historical_data: Optional[Dict],
        window_days: int
    ) -> TrendAnalysis:
        """构建趋势分析数据"""
        trend = TrendAnalysis()
        
        if not historical_data:
            trend.trend_overall_text = "暂无足够的历史数据进行趋势分析"
            return trend
        
        # 设置时间窗口
        trend.trend_window_end = date.today()
        trend.trend_window_start = date.today() - timedelta(days=window_days)
        
        # 统计有效检测次数
        trend.valid_check_count = historical_data.get('check_count', 0)
        
        # 收缩压趋势
        if 'systolic_bp_history' in historical_data:
            bp_data = historical_data['systolic_bp_history']
            trend.bp_trend = self._calculate_trend_statistics(
                'systolic_bp', bp_data, 'mmHg'
            )
        
        # 舒张压趋势
        if 'diastolic_bp_history' in historical_data:
            dbp_data = historical_data['diastolic_bp_history']
            trend.dbp_trend = self._calculate_trend_statistics(
                'diastolic_bp', dbp_data, 'mmHg'
            )
        
        # 血糖趋势
        if 'blood_sugar_history' in historical_data:
            sugar_data = historical_data['blood_sugar_history']
            trend.sugar_trend = self._calculate_trend_statistics(
                'blood_sugar', sugar_data, 'mmol/L'
            )
        
        # 心率趋势
        if 'heart_rate_history' in historical_data:
            hr_data = historical_data['heart_rate_history']
            trend.hr_trend = self._calculate_trend_statistics(
                'heart_rate', hr_data, '次/分'
            )
        
        # 体温趋势
        if 'body_temperature_history' in historical_data:
            temp_data = historical_data['body_temperature_history']
            trend.temp_trend = self._calculate_trend_statistics(
                'body_temperature', temp_data, '℃'
            )
        
        # 体重趋势
        if 'weight_history' in historical_data:
            weight_data = historical_data['weight_history']
            trend.weight_trend = self._calculate_trend_statistics(
                'weight', weight_data, 'kg'
            )
        
        # 血尿酸趋势
        if 'uric_acid_history' in historical_data:
            uric_data = historical_data['uric_acid_history']
            trend.uric_acid_trend = self._calculate_trend_statistics(
                'uric_acid', uric_data, 'μmol/L'
            )
        
        # 生成综合描述
        trend.trend_overall_text = self._generate_trend_overall_text(trend)
        
        return trend
    
    def _calculate_trend_statistics(
        self, 
        metric_name: str,
        data: List[float],
        unit: str
    ) -> TrendStatistics:
        """计算趋势统计数据"""
        if not data or len(data) == 0:
            return TrendStatistics(
                metric_name=metric_name,
                trend_desc="暂无数据"
            )
        
        values = np.array(data)
        avg_val = float(np.mean(values))
        max_val = float(np.max(values))
        min_val = float(np.min(values))
        std_val = float(np.std(values))
        
        # 生成统计文本
        stat_text = f"平均值 {avg_val:.1f} {unit}，最大值 {max_val:.1f} {unit}，最小值 {min_val:.1f} {unit}"
        
        # 判断趋势
        trend_desc = self._determine_trend_description(values)
        
        return TrendStatistics(
            metric_name=metric_name,
            avg_value=avg_val,
            max_value=max_val,
            min_value=min_val,
            std_value=std_val,
            stat_text=stat_text,
            trend_desc=trend_desc
        )
    
    def _determine_trend_description(self, values: np.ndarray) -> str:
        """判断趋势描述"""
        if len(values) < 3:
            return "数据点不足，无法判断趋势"
        
        # 计算变异系数
        cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        
        # 计算趋势斜率
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # 判断趋势
        if cv < 0.05:
            stability = "整体波动不大"
        elif cv < 0.1:
            stability = "存在一定波动"
        else:
            stability = "波动较为明显"
        
        if abs(slope) < 0.5:
            direction = "保持相对稳定"
        elif slope > 0:
            direction = "呈上升趋势"
        else:
            direction = "呈下降趋势"
        
        return f"{stability}，{direction}"
    
    def _generate_trend_overall_text(self, trend: TrendAnalysis) -> str:
        """生成趋势综合描述"""
        descriptions = []
        
        # 收缩压趋势
        if trend.bp_trend and trend.bp_trend.avg_value:
            descriptions.append(f"收缩压{trend.bp_trend.trend_desc}")
        
        # 舒张压趋势
        if trend.dbp_trend and trend.dbp_trend.avg_value:
            descriptions.append(f"舒张压{trend.dbp_trend.trend_desc}")
        
        # 血糖趋势
        if trend.sugar_trend and trend.sugar_trend.avg_value:
            descriptions.append(f"血糖{trend.sugar_trend.trend_desc}")
        
        # 心率趋势
        if trend.hr_trend and trend.hr_trend.avg_value:
            descriptions.append(f"心率{trend.hr_trend.trend_desc}")
        
        # 体重趋势
        if trend.weight_trend and trend.weight_trend.avg_value:
            descriptions.append(f"体重{trend.weight_trend.trend_desc}")
        
        # 血尿酸趋势
        if trend.uric_acid_trend and trend.uric_acid_trend.avg_value:
            descriptions.append(f"血尿酸{trend.uric_acid_trend.trend_desc}")
        
        if not descriptions:
            return "在当前统计区间内，暂无足够数据进行趋势分析。"
        
        return "在当前统计区间内，" + "；".join(descriptions) + "。"
    
    def _build_feature_recognition(
        self,
        current_measurements: Dict,
        historical_data: Optional[Dict],
        baseline_data: Optional[Dict]
    ) -> FeatureRecognition:
        """构建特征识别小结"""
        feature = FeatureRecognition()
        
        overview_items = []
        combined_items = []
        focus_points = []
        
        # 分析当前指标特征
        if baseline_data:
            # 血压特征
            if 'systolic_bp' in current_measurements and 'systolic_bp' in baseline_data:
                current_bp = current_measurements['systolic_bp']
                baseline_bp = baseline_data['systolic_bp']
                if isinstance(baseline_bp, dict):
                    baseline_mean = baseline_bp.get('mean', baseline_bp.get('value', 130))
                    baseline_p75 = baseline_bp.get('p75', baseline_mean * 1.1)
                    baseline_p25 = baseline_bp.get('p25', baseline_mean * 0.9)
                else:
                    baseline_mean = baseline_bp
                    baseline_p75 = baseline_bp * 1.1
                    baseline_p25 = baseline_bp * 0.9
                
                # 判断当前值在个人历史中的位置
                if current_bp > baseline_p75:
                    overview_items.append(
                        f"与个人历史记录相比，本次收缩压数值（{current_bp} mmHg）处于个人记录的中高位置"
                    )
                    focus_points.append("收缩压在统计区间内多次接近预警区间")
                elif current_bp < baseline_p25:
                    overview_items.append(
                        f"与个人历史记录相比，本次收缩压数值（{current_bp} mmHg）处于个人记录的较低位置"
                    )
            
            # 血糖特征
            if 'blood_sugar' in current_measurements:
                current_sugar = current_measurements['blood_sugar']
                if 'blood_sugar' in baseline_data:
                    bs_baseline = baseline_data['blood_sugar']
                    if isinstance(bs_baseline, dict):
                        bs_mean = bs_baseline.get('mean', 5.5)
                        bs_p75 = bs_baseline.get('p75', 6.1)
                    else:
                        bs_mean = bs_baseline
                        bs_p75 = bs_baseline * 1.1
                    
                    if current_sugar > bs_p75:
                        overview_items.append(
                            f"近期血糖值（{current_sugar} mmol/L）高于个人历史75分位值"
                        )
                        focus_points.append("血糖波动范围较大，个别记录明显高于个人平均值")
                elif current_sugar > 6.0:
                    overview_items.append(
                        f"近期血糖值（{current_sugar} mmol/L）接近系统预设上限"
                    )
        
        # 分析组合特征（使用增强的检测算法）
        if historical_data:
            combined_patterns = self._detect_combined_patterns(historical_data, current_measurements)
            combined_items.extend(combined_patterns)
        
        # 组装文本
        feature.feature_overview_text = "；".join(overview_items) if overview_items else "各项指标处于正常波动范围内"
        feature.combined_feature_text = "；".join(combined_items) if combined_items else "暂未发现明显的指标组合特征"
        feature.system_focus_points = focus_points if focus_points else ["当前各项指标未触发系统关注点"]
        
        return feature
    
    def _detect_combined_patterns(
        self,
        historical_data: Dict,
        current_measurements: Dict
    ) -> List[str]:
        """
        检测组合特征模式
        
        分析多个指标之间的关联性，识别常见的健康模式
        """
        patterns = []
        
        # 1. 血压与睡眠关联检测
        if ('systolic_bp_history' in historical_data and 
            'sleep_duration_history' in historical_data):
            bp_data = np.array(historical_data['systolic_bp_history'])
            sleep_data = np.array(historical_data['sleep_duration_history'])
            
            if len(bp_data) == len(sleep_data) and len(bp_data) >= 5:
                # 计算相关系数
                correlation, p_value = scipy_stats.pearsonr(bp_data, sleep_data)
                
                # 负相关表示睡眠少时血压高
                if correlation < -0.3 and p_value < 0.1:
                    patterns.append("在多次记录中，血压偏高与睡眠时间较短经常同时出现")
                
                # 检测同时异常的天数
                bp_high = bp_data > 140
                sleep_short = sleep_data < 6
                co_occurrence_rate = np.sum(bp_high & sleep_short) / len(bp_data)
                
                if co_occurrence_rate > 0.3:
                    patterns.append(
                        f"约{co_occurrence_rate*100:.0f}%的记录中，血压偏高与睡眠不足同时出现"
                    )
        
        # 2. 心率与检测时间关联
        if ('heart_rate_history' in historical_data and 
            'measurement_hours' in historical_data):
            hr_data = np.array(historical_data['heart_rate_history'])
            hours = np.array(historical_data['measurement_hours'])
            
            if len(hr_data) == len(hours) and len(hr_data) >= 5:
                # 分析下午/晚间（14:00-22:00）的心率
                afternoon_evening = (hours >= 14) & (hours <= 22)
                morning = hours < 14
                
                if np.sum(afternoon_evening) > 0 and np.sum(morning) > 0:
                    hr_afternoon = np.mean(hr_data[afternoon_evening])
                    hr_morning = np.mean(hr_data[morning])
                    
                    if hr_afternoon > hr_morning + 5:
                        patterns.append("心率偏快多见于下午或晚间的检测记录")
        
        # 3. 血糖与饮食/运动关联
        if ('blood_sugar_history' in historical_data and
            'steps_history' in historical_data):
            sugar_data = np.array(historical_data['blood_sugar_history'])
            steps_data = np.array(historical_data['steps_history'])
            
            if len(sugar_data) == len(steps_data) and len(sugar_data) >= 5:
                correlation, p_value = scipy_stats.pearsonr(sugar_data, steps_data)
                
                # 负相关表示运动多时血糖低
                if correlation < -0.3 and p_value < 0.1:
                    patterns.append("运动量较大的日期，血糖值相对较低")
        
        # 4. 血压波动与体重关联
        if ('systolic_bp_history' in historical_data and
            'weight_history' in historical_data):
            bp_data = np.array(historical_data['systolic_bp_history'])
            weight_data = np.array(historical_data['weight_history'])
            
            if len(bp_data) == len(weight_data) and len(bp_data) >= 5:
                correlation, p_value = scipy_stats.pearsonr(bp_data, weight_data)
                
                if correlation > 0.3 and p_value < 0.1:
                    patterns.append("体重增加时，血压也呈现上升趋势")
        
        # 5. 检测血压晨峰现象
        if ('systolic_bp_history' in historical_data and
            'measurement_hours' in historical_data):
            bp_data = np.array(historical_data['systolic_bp_history'])
            hours = np.array(historical_data['measurement_hours'])
            
            if len(bp_data) == len(hours) and len(bp_data) >= 5:
                morning_bp = bp_data[(hours >= 6) & (hours <= 10)]
                other_bp = bp_data[(hours < 6) | (hours > 10)]
                
                if len(morning_bp) > 0 and len(other_bp) > 0:
                    if np.mean(morning_bp) > np.mean(other_bp) + 10:
                        patterns.append("清晨时段血压明显高于其他时段，存在晨峰现象")
        
        # 如果历史数据中有预设的关联标记，也加入
        if historical_data.get('bp_sleep_correlation'):
            if "血压偏高与睡眠时间较短" not in str(patterns):
                patterns.append("在多次记录中，血压偏高与睡眠时间较短经常同时出现")
        
        if historical_data.get('hr_time_pattern'):
            if "心率偏快多见于下午" not in str(patterns):
                patterns.append("心率偏快多见于下午或晚间的检测记录")
        
        return patterns
    
    def calculate_personal_baseline(
        self,
        historical_data: Dict,
        days: int = 90
    ) -> Dict:
        """
        计算个人基线区间
        
        基于历史数据计算各指标的个人参考区间
        
        Args:
            historical_data: 历史数据字典
            days: 基线计算天数
        
        Returns:
            个人基线数据字典
        """
        baseline = {'baseline_days': days}
        
        # 计算血压基线
        if 'systolic_bp_history' in historical_data:
            bp_data = np.array(historical_data['systolic_bp_history'])
            if len(bp_data) >= 3:
                baseline['systolic_bp'] = {
                    'mean': float(np.mean(bp_data)),
                    'std': float(np.std(bp_data)),
                    'p25': float(np.percentile(bp_data, 25)),
                    'p75': float(np.percentile(bp_data, 75)),
                    'min': float(np.min(bp_data)),
                    'max': float(np.max(bp_data)),
                    'cv': float(np.std(bp_data) / np.mean(bp_data)) if np.mean(bp_data) != 0 else 0
                }
        
        if 'diastolic_bp_history' in historical_data:
            dbp_data = np.array(historical_data['diastolic_bp_history'])
            if len(dbp_data) >= 3:
                baseline['diastolic_bp'] = {
                    'mean': float(np.mean(dbp_data)),
                    'std': float(np.std(dbp_data)),
                    'p25': float(np.percentile(dbp_data, 25)),
                    'p75': float(np.percentile(dbp_data, 75)),
                    'min': float(np.min(dbp_data)),
                    'max': float(np.max(dbp_data))
                }
        
        # 计算血糖基线
        if 'blood_sugar_history' in historical_data:
            sugar_data = np.array(historical_data['blood_sugar_history'])
            if len(sugar_data) >= 3:
                baseline['blood_sugar'] = {
                    'mean': float(np.mean(sugar_data)),
                    'std': float(np.std(sugar_data)),
                    'p25': float(np.percentile(sugar_data, 25)),
                    'p75': float(np.percentile(sugar_data, 75)),
                    'min': float(np.min(sugar_data)),
                    'max': float(np.max(sugar_data)),
                    'cv': float(np.std(sugar_data) / np.mean(sugar_data)) if np.mean(sugar_data) != 0 else 0
                }
        
        # 计算心率基线
        if 'heart_rate_history' in historical_data:
            hr_data = np.array(historical_data['heart_rate_history'])
            if len(hr_data) >= 3:
                baseline['heart_rate'] = {
                    'mean': float(np.mean(hr_data)),
                    'std': float(np.std(hr_data)),
                    'p25': float(np.percentile(hr_data, 25)),
                    'p75': float(np.percentile(hr_data, 75)),
                    'min': float(np.min(hr_data)),
                    'max': float(np.max(hr_data))
                }
        
        # 计算体重基线
        if 'weight_history' in historical_data:
            weight_data = np.array(historical_data['weight_history'])
            if len(weight_data) >= 3:
                baseline['weight'] = {
                    'mean': float(np.mean(weight_data)),
                    'std': float(np.std(weight_data)),
                    'min': float(np.min(weight_data)),
                    'max': float(np.max(weight_data)),
                    'trend': float(np.polyfit(range(len(weight_data)), weight_data, 1)[0])
                }
        
        # 计算睡眠基线
        if 'sleep_duration_history' in historical_data:
            sleep_data = np.array(historical_data['sleep_duration_history'])
            if len(sleep_data) >= 3:
                baseline['sleep_duration'] = {
                    'mean': float(np.mean(sleep_data)),
                    'std': float(np.std(sleep_data)),
                    'insufficient_rate': float(np.sum(sleep_data < 6) / len(sleep_data))
                }
        
        # 计算血尿酸基线
        if 'uric_acid_history' in historical_data:
            uric_data = np.array(historical_data['uric_acid_history'])
            if len(uric_data) >= 3:
                baseline['uric_acid'] = {
                    'mean': float(np.mean(uric_data)),
                    'std': float(np.std(uric_data)),
                    'p25': float(np.percentile(uric_data, 25)),
                    'p75': float(np.percentile(uric_data, 75)),
                    'min': float(np.min(uric_data)),
                    'max': float(np.max(uric_data))
                }
        
        return baseline
    
    def detect_change_points(
        self,
        data: List[float],
        metric_name: str = "指标",
        threshold: float = 5.0
    ) -> Dict:
        """
        变点检测 - 识别数据中的突然变化点
        
        Args:
            data: 时间序列数据
            metric_name: 指标名称
            threshold: CUSUM阈值
        
        Returns:
            变点检测结果字典
        """
        if len(data) < 5:
            return {
                'has_change_point': False,
                'change_points': [],
                'description': "数据点不足，无法进行变点检测"
            }
        
        values = np.array(data)
        
        # 优先使用ruptures库（更精确）
        if RUPTURES_AVAILABLE:
            change_points = self._detect_with_ruptures(values)
        else:
            change_points = self._detect_with_cusum(values, threshold)
        
        # 生成描述
        if not change_points:
            return {
                'has_change_point': False,
                'change_points': [],
                'description': f"{metric_name}在统计区间内保持相对稳定，未检测到明显突变"
            }
        
        # 分析变点
        descriptions = []
        for cp in change_points:
            idx = cp['index']
            direction = cp['direction']
            
            if idx > 0 and idx < len(values):
                before_mean = np.mean(values[:idx])
                after_mean = np.mean(values[idx:])
                change_pct = abs(after_mean - before_mean) / before_mean * 100 if before_mean != 0 else 0
                
                if direction == 'up':
                    descriptions.append(
                        f"第{idx+1}天起{metric_name}明显上升（从{before_mean:.1f}升至{after_mean:.1f}，变化{change_pct:.0f}%）"
                    )
                else:
                    descriptions.append(
                        f"第{idx+1}天起{metric_name}明显下降（从{before_mean:.1f}降至{after_mean:.1f}，变化{change_pct:.0f}%）"
                    )
        
        return {
            'has_change_point': True,
            'change_points': change_points,
            'description': "；".join(descriptions) if descriptions else f"{metric_name}存在变化点"
        }
    
    def _detect_with_ruptures(self, values: np.ndarray) -> List[Dict]:
        """使用Ruptures库检测变点"""
        try:
            # 使用Pelt算法
            algo = rpt.Pelt(model="rbf").fit(values.reshape(-1, 1))
            change_indices = algo.predict(pen=10)
            
            # 移除最后一个（数据结尾）
            change_indices = [i for i in change_indices if i < len(values)]
            
            change_points = []
            for idx in change_indices:
                if idx > 0 and idx < len(values):
                    before_mean = np.mean(values[:idx])
                    after_mean = np.mean(values[idx:])
                    direction = 'up' if after_mean > before_mean else 'down'
                    
                    # 只记录显著变化（>10%）
                    change_pct = abs(after_mean - before_mean) / before_mean * 100 if before_mean != 0 else 0
                    if change_pct > 10:
                        change_points.append({
                            'index': idx,
                            'direction': direction,
                            'before_mean': float(before_mean),
                            'after_mean': float(after_mean),
                            'change_percent': float(change_pct)
                        })
            
            return change_points
        except Exception:
            # 出错时回退到CUSUM
            return self._detect_with_cusum(values, 5.0)
    
    def _detect_with_cusum(self, values: np.ndarray, threshold: float) -> List[Dict]:
        """
        使用CUSUM（累积和控制图）检测变点
        
        CUSUM是一种经典的变点检测算法，能够检测均值的持续偏移
        """
        n = len(values)
        if n < 5:
            return []
        
        change_points = []
        
        # 方法1：滑动窗口检测突变
        window_size = max(3, n // 4)
        
        for i in range(window_size, n - window_size + 1):
            before = values[:i]
            after = values[i:]
            
            before_mean = np.mean(before)
            after_mean = np.mean(after)
            
            # 计算变化幅度
            if before_mean != 0:
                change_pct = abs(after_mean - before_mean) / before_mean * 100
            else:
                change_pct = 0
            
            # 使用t检验判断是否显著
            if len(before) >= 3 and len(after) >= 3:
                t_stat, p_value = scipy_stats.ttest_ind(before, after)
                
                # 显著性检验 + 变化幅度检验
                if p_value < 0.05 and change_pct > 8:
                    direction = 'up' if after_mean > before_mean else 'down'
                    
                    # 避免重复检测（与已有变点距离太近）
                    if not change_points or abs(i - change_points[-1]['index']) > window_size:
                        change_points.append({
                            'index': i,
                            'direction': direction,
                            'before_mean': float(before_mean),
                            'after_mean': float(after_mean),
                            'change_percent': float(change_pct),
                            'p_value': float(p_value)
                        })
        
        # 只保留最显著的变点（如果有多个）
        if len(change_points) > 2:
            change_points = sorted(change_points, key=lambda x: x['change_percent'], reverse=True)[:2]
            change_points = sorted(change_points, key=lambda x: x['index'])
        
        return change_points
    
    def analyze_all_change_points(self, historical_data: Dict) -> Dict[str, Dict]:
        """
        分析所有指标的变点
        
        Args:
            historical_data: 历史数据字典
        
        Returns:
            各指标的变点分析结果
        """
        results = {}
        
        indicator_mapping = {
            'systolic_bp_history': ('收缩压', 'mmHg'),
            'diastolic_bp_history': ('舒张压', 'mmHg'),
            'blood_sugar_history': ('血糖', 'mmol/L'),
            'heart_rate_history': ('心率', '次/分'),
            'weight_history': ('体重', 'kg'),
            'uric_acid_history': ('血尿酸', 'μmol/L')
        }
        
        for key, (name, unit) in indicator_mapping.items():
            if key in historical_data and len(historical_data[key]) >= 5:
                results[key] = self.detect_change_points(
                    historical_data[key],
                    metric_name=name
                )
        
        return results
    
    def _build_baseline_comparison(
        self,
        current_measurements: Dict,
        baseline_data: Optional[Dict]
    ) -> BaselineComparison:
        """构建基线对比数据"""
        comparison = BaselineComparison()
        
        if not baseline_data:
            comparison.personal_baseline_desc = "暂无足够的历史数据生成个人基线"
            return comparison
        
        comparison.baseline_days = baseline_data.get('baseline_days', 90)
        
        # 生成基线描述
        baseline_desc_parts = []
        
        if 'systolic_bp' in baseline_data:
            bp_baseline = baseline_data['systolic_bp']
            if isinstance(bp_baseline, dict):
                bp_mean = bp_baseline.get('mean', 130)
                bp_low = bp_baseline.get('p25', bp_mean - 10)
                bp_high = bp_baseline.get('p75', bp_mean + 10)
                bp_cv = bp_baseline.get('cv', 0)
                
                # 根据波动系数评估稳定性
                if bp_cv < 0.08:
                    stability = "波动较小"
                elif bp_cv < 0.12:
                    stability = "波动适中"
                else:
                    stability = "波动较大"
                
                baseline_desc_parts.append(
                    f"收缩压参考区间为 {bp_low:.0f}～{bp_high:.0f} mmHg"
                    f"（平均 {bp_mean:.0f} mmHg，{stability}）"
                )
            else:
                bp_low = bp_baseline - 10
                bp_high = bp_baseline + 10
                baseline_desc_parts.append(f"血压参考区间为 {bp_low:.0f}～{bp_high:.0f} mmHg")
        
        if 'blood_sugar' in baseline_data:
            sugar_baseline = baseline_data['blood_sugar']
            if isinstance(sugar_baseline, dict):
                sugar_mean = sugar_baseline.get('mean', 5.5)
                sugar_low = sugar_baseline.get('p25', sugar_mean - 0.5)
                sugar_high = sugar_baseline.get('p75', sugar_mean + 0.5)
                sugar_cv = sugar_baseline.get('cv', 0)
                
                # 根据波动系数评估稳定性
                if sugar_cv < 0.1:
                    stability = "波动较小"
                elif sugar_cv < 0.2:
                    stability = "波动适中"
                else:
                    stability = "波动较大"
                
                baseline_desc_parts.append(
                    f"血糖参考区间为 {sugar_low:.1f}～{sugar_high:.1f} mmol/L"
                    f"（平均 {sugar_mean:.1f} mmol/L，{stability}）"
                )
            else:
                sugar_low = sugar_baseline - 0.5
                sugar_high = sugar_baseline + 0.5
                baseline_desc_parts.append(f"血糖参考区间为 {sugar_low:.1f}～{sugar_high:.1f} mmol/L")
        
        # 添加心率基线
        if 'heart_rate' in baseline_data:
            hr_baseline = baseline_data['heart_rate']
            if isinstance(hr_baseline, dict):
                hr_mean = hr_baseline.get('mean', 75)
                hr_low = hr_baseline.get('p25', hr_mean - 10)
                hr_high = hr_baseline.get('p75', hr_mean + 10)
                baseline_desc_parts.append(
                    f"心率参考区间为 {hr_low:.0f}～{hr_high:.0f} 次/分"
                )
        
        comparison.personal_baseline_desc = (
            f"根据过去 {comparison.baseline_days} 天记录，系统为该用户生成的" +
            "；".join(baseline_desc_parts) + "。"
        ) if baseline_desc_parts else "暂无基线数据"
        
        # 血压对比
        if 'systolic_bp' in current_measurements and 'systolic_bp' in baseline_data:
            comparison.bp_vs_baseline_text = self._generate_comparison_text(
                current_measurements['systolic_bp'],
                baseline_data['systolic_bp'],
                "收缩压"
            )
        
        # 血糖对比
        if 'blood_sugar' in current_measurements and 'blood_sugar' in baseline_data:
            comparison.sugar_vs_baseline_text = self._generate_comparison_text(
                current_measurements['blood_sugar'],
                baseline_data['blood_sugar'],
                "血糖"
            )
        
        # 其他指标对比（心率、体重、血尿酸）
        others_comparisons = []
        
        if 'heart_rate' in current_measurements and 'heart_rate' in baseline_data:
            hr_comparison = self._generate_comparison_text(
                current_measurements['heart_rate'],
                baseline_data['heart_rate'],
                "心率"
            )
            others_comparisons.append(hr_comparison)
        
        if 'weight' in current_measurements and 'weight' in baseline_data:
            weight_comparison = self._generate_comparison_text(
                current_measurements['weight'],
                baseline_data['weight'],
                "体重"
            )
            others_comparisons.append(weight_comparison)
        
        if 'uric_acid' in current_measurements and 'uric_acid' in baseline_data:
            uric_comparison = self._generate_comparison_text(
                current_measurements['uric_acid'],
                baseline_data['uric_acid'],
                "血尿酸"
            )
            others_comparisons.append(uric_comparison)
        
        if others_comparisons:
            comparison.others_vs_baseline_text = "；".join(others_comparisons)
        else:
            comparison.others_vs_baseline_text = "暂无其他指标对比数据"
        
        return comparison
    
    def _generate_comparison_text(
        self, 
        current_value: float, 
        baseline: any,
        metric_name: str
    ) -> str:
        """
        生成对比文本
        
        基于当前值与个人基线的对比，生成描述性文本
        """
        if isinstance(baseline, dict):
            baseline_mean = baseline.get('mean', baseline.get('value', current_value))
            baseline_p25 = baseline.get('p25', baseline_mean * 0.9)
            baseline_p75 = baseline.get('p75', baseline_mean * 1.1)
            baseline_std = baseline.get('std', baseline_mean * 0.1)
        else:
            baseline_mean = baseline
            baseline_p25 = baseline * 0.9
            baseline_p75 = baseline * 1.1
            baseline_std = baseline * 0.1
        
        diff = current_value - baseline_mean
        diff_percent = (diff / baseline_mean * 100) if baseline_mean != 0 else 0
        
        # 判断当前值在个人历史分布中的位置
        if baseline_p25 <= current_value <= baseline_p75:
            position = "处于个人常见波动范围内"
        elif current_value < baseline_p25:
            position = "处于个人历史记录的较低水平"
        else:
            position = "处于个人历史记录的较高水平"
        
        # 生成对比文本
        if abs(diff_percent) < 5:
            return f"本次{metric_name}与个人基线水平相近，{position}"
        elif diff > 0:
            # 判断偏离程度
            if diff > 2 * baseline_std:
                severity = "明显"
            else:
                severity = "略"
            return f"本次{metric_name}{severity}高于个人基线平均值（+{abs(diff_percent):.1f}%），{position}"
        else:
            if abs(diff) > 2 * baseline_std:
                severity = "明显"
            else:
                severity = "略"
            return f"本次{metric_name}{severity}低于个人基线平均值（-{abs(diff_percent):.1f}%），{position}"
    
    def render_text_report(self, report_data: HealthReportData) -> str:
        """
        渲染文本格式报告
        
        Args:
            report_data: 报告数据
        
        Returns:
            格式化的文本报告
        """
        vars = report_data.to_template_vars()
        vs = report_data.vital_signs
        mi = report_data.metabolic_indicators
        ta = report_data.trend_analysis
        fr = report_data.feature_recognition
        bc = report_data.baseline_comparison
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                  养生之道 · 智能健康报告                           ║
╚══════════════════════════════════════════════════════════════════╝

报告对象：{vars['elder_name']}（{vars['elder_age']} 岁）
报告时间：{vars['report_date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

一、基本信息

  姓名：{vars['elder_name']}
  性别：{vars['elder_gender']}
  年龄：{vars['elder_age']} 岁
  联系电话：{vars['elder_phone'] or '未填写'}
  居住地区：{vars['elder_address'] or '未填写'}
  既往记录标签：{vars['elder_chronic_tags']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

二、关键指标一览

2.1 生命体征
┌──────────┬────────────────┬──────────────────────────────────────┐
│   指标   │    本次结果    │           系统状态描述               │
├──────────┼────────────────┼──────────────────────────────────────┤
│   血氧   │ {self._format_value(vs.spo2.value, vs.spo2.unit):^14} │ {vs.spo2.status_text:<36} │
│   心率   │ {self._format_value(vs.heart_rate.value, vs.heart_rate.unit):^14} │ {vs.heart_rate.status_text:<36} │
│  收缩压  │ {self._format_value(vs.systolic_bp.value, vs.systolic_bp.unit):^14} │ {vs.systolic_bp.status_text:<36} │
│  舒张压  │ {self._format_value(vs.diastolic_bp.value, vs.diastolic_bp.unit):^14} │ {vs.diastolic_bp.status_text:<36} │
│   脉率   │ {self._format_value(vs.pulse_rate.value, vs.pulse_rate.unit):^14} │ {vs.pulse_rate.status_text:<36} │
│   体温   │ {self._format_value(vs.body_temperature.value, vs.body_temperature.unit):^14} │ {vs.body_temperature.status_text:<36} │
└──────────┴────────────────┴──────────────────────────────────────┘

2.2 代谢相关指标
┌──────────┬────────────────┬──────────────────────────────────────┐
│   指标   │    本次结果    │           系统状态描述               │
├──────────┼────────────────┼──────────────────────────────────────┤
│   血糖   │ {self._format_value(mi.blood_sugar.value, mi.blood_sugar.unit):^14} │ {mi.blood_sugar.status_text:<36} │
│  血尿酸  │ {self._format_value(mi.uric_acid.value, mi.uric_acid.unit):^14} │ {mi.uric_acid.status_text:<36} │
│   体重   │ {self._format_value(mi.weight.value, mi.weight.unit):^14} │ {mi.weight.status_text:<36} │
│   BMI    │ {self._format_value(mi.bmi.value, mi.bmi.unit):^14} │ {mi.bmi.status_text:<36} │
└──────────┴────────────────┴──────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

三、近期变化趋势（如有历史数据）

  统计时间范围：{vars['trend_window_start']} ～ {vars['trend_window_end']}
  本阶段内有效检测次数：{vars['valid_check_count']}

  3.1 血压趋势
      统计结果：{vars['bp_trend_stat_text']}
      趋势描述：{vars['bp_trend_desc']}

  3.2 血糖趋势
      统计结果：{vars['sugar_trend_stat_text']}
      趋势描述：{vars['sugar_trend_desc']}

  3.3 心率与其他指标趋势
      心率：{vars['hr_trend_desc']}
      体温/其他：{vars['temp_trend_desc']}

  趋势综合描述：
      {vars['trend_overall_text']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

四、系统特征识别小结（纯描述，无建议）

  【指标特征概览】
      {vars['feature_overview_text']}

  【组合特征说明】
      {vars['combined_feature_text']}

  【系统标记的关注点】
{self._format_focus_points(vars['system_focus_points'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

五、历史对比与个体基线

  个人基线区间说明：
      {vars['personal_baseline_desc']}

  本次检测与个人基线对比：
      • 血压对比：{vars['bp_vs_baseline_text']}
      • 血糖对比：{vars['sugar_vs_baseline_text']}
      • 其他对比：{vars['others_vs_baseline_text']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

六、报告说明

  {vars['disclaimer']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
    
    def _format_value(self, value: any, unit: str) -> str:
        """格式化数值显示"""
        if value is None:
            return "暂无数据"
        if isinstance(value, float):
            return f"{value:.1f} {unit}"
        return f"{value} {unit}"
    
    def _format_focus_points(self, points: List[str]) -> str:
        """格式化关注点列表"""
        if not points:
            return "      • 当前各项指标未触发系统关注点"
        return "\n".join([f"      • {p}" for p in points])
    
    def render_json_report(self, report_data: HealthReportData) -> str:
        """渲染JSON格式报告"""
        return json.dumps(report_data.to_dict(), ensure_ascii=False, indent=2)
    
    def render_html_report(self, report_data: HealthReportData) -> str:
        """渲染HTML格式报告"""
        vars = report_data.to_template_vars()
        vs = report_data.vital_signs
        mi = report_data.metabolic_indicators
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>养生之道 · 智能健康报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .report-container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #4CAF50;
            margin: 0;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #333;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
            font-size: 18px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        .info-item {{
            padding: 8px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .info-label {{
            color: #666;
            font-size: 14px;
        }}
        .info-value {{
            color: #333;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .status-normal {{
            color: #4CAF50;
        }}
        .status-warning {{
            color: #FF9800;
        }}
        .status-danger {{
            color: #f44336;
        }}
        .disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            font-size: 14px;
            color: #856404;
        }}
        .focus-point {{
            background: #e3f2fd;
            border-left: 3px solid #2196F3;
            padding: 10px;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>🌿 养生之道 · 智能健康报告</h1>
            <p>报告对象：{vars['elder_name']}（{vars['elder_age']} 岁）</p>
            <p>报告时间：{vars['report_date']}</p>
        </div>
        
        <div class="section">
            <h2>一、基本信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">姓名：</span>
                    <span class="info-value">{vars['elder_name']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">性别：</span>
                    <span class="info-value">{vars['elder_gender']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">年龄：</span>
                    <span class="info-value">{vars['elder_age']} 岁</span>
                </div>
                <div class="info-item">
                    <span class="info-label">联系电话：</span>
                    <span class="info-value">{vars['elder_phone'] or '未填写'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">居住地区：</span>
                    <span class="info-value">{vars['elder_address'] or '未填写'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">既往记录：</span>
                    <span class="info-value">{vars['elder_chronic_tags']}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>二、关键指标一览</h2>
            <h3>2.1 生命体征</h3>
            <table>
                <tr>
                    <th>指标</th>
                    <th>本次结果</th>
                    <th>系统状态描述</th>
                </tr>
                <tr>
                    <td>血氧</td>
                    <td>{self._format_value(vs.spo2.value, vs.spo2.unit)}</td>
                    <td class="{self._get_status_class(vs.spo2.status)}">{vs.spo2.status_text}</td>
                </tr>
                <tr>
                    <td>心率</td>
                    <td>{self._format_value(vs.heart_rate.value, vs.heart_rate.unit)}</td>
                    <td class="{self._get_status_class(vs.heart_rate.status)}">{vs.heart_rate.status_text}</td>
                </tr>
                <tr>
                    <td>收缩压</td>
                    <td>{self._format_value(vs.systolic_bp.value, vs.systolic_bp.unit)}</td>
                    <td class="{self._get_status_class(vs.systolic_bp.status)}">{vs.systolic_bp.status_text}</td>
                </tr>
                <tr>
                    <td>舒张压</td>
                    <td>{self._format_value(vs.diastolic_bp.value, vs.diastolic_bp.unit)}</td>
                    <td class="{self._get_status_class(vs.diastolic_bp.status)}">{vs.diastolic_bp.status_text}</td>
                </tr>
                <tr>
                    <td>脉率</td>
                    <td>{self._format_value(vs.pulse_rate.value, vs.pulse_rate.unit)}</td>
                    <td class="{self._get_status_class(vs.pulse_rate.status)}">{vs.pulse_rate.status_text}</td>
                </tr>
                <tr>
                    <td>体温</td>
                    <td>{self._format_value(vs.body_temperature.value, vs.body_temperature.unit)}</td>
                    <td class="{self._get_status_class(vs.body_temperature.status)}">{vs.body_temperature.status_text}</td>
                </tr>
            </table>
            
            <h3>2.2 代谢相关指标</h3>
            <table>
                <tr>
                    <th>指标</th>
                    <th>本次结果</th>
                    <th>系统状态描述</th>
                </tr>
                <tr>
                    <td>血糖</td>
                    <td>{self._format_value(mi.blood_sugar.value, mi.blood_sugar.unit)}</td>
                    <td class="{self._get_status_class(mi.blood_sugar.status)}">{mi.blood_sugar.status_text}</td>
                </tr>
                <tr>
                    <td>血尿酸</td>
                    <td>{self._format_value(mi.uric_acid.value, mi.uric_acid.unit)}</td>
                    <td class="{self._get_status_class(mi.uric_acid.status)}">{mi.uric_acid.status_text}</td>
                </tr>
                <tr>
                    <td>体重</td>
                    <td>{self._format_value(mi.weight.value, mi.weight.unit)}</td>
                    <td>{mi.weight.status_text}</td>
                </tr>
                <tr>
                    <td>BMI</td>
                    <td>{self._format_value(mi.bmi.value, mi.bmi.unit)}</td>
                    <td class="{self._get_status_class(mi.bmi.status)}">{mi.bmi.status_text}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>三、近期变化趋势</h2>
            <p><strong>统计时间范围：</strong>{vars['trend_window_start']} ～ {vars['trend_window_end']}</p>
            <p><strong>有效检测次数：</strong>{vars['valid_check_count']}</p>
            
            <h3>3.1 血压趋势</h3>
            <p>统计结果：{vars['bp_trend_stat_text']}</p>
            <p>趋势描述：{vars['bp_trend_desc']}</p>
            
            <h3>3.2 血糖趋势</h3>
            <p>统计结果：{vars['sugar_trend_stat_text']}</p>
            <p>趋势描述：{vars['sugar_trend_desc']}</p>
            
            <p><strong>趋势综合描述：</strong>{vars['trend_overall_text']}</p>
        </div>
        
        <div class="section">
            <h2>四、系统特征识别小结</h2>
            <p><strong>指标特征概览：</strong>{vars['feature_overview_text']}</p>
            <p><strong>组合特征说明：</strong>{vars['combined_feature_text']}</p>
            <p><strong>系统标记的关注点：</strong></p>
            {''.join([f'<div class="focus-point">{p}</div>' for p in vars['system_focus_points']])}
        </div>
        
        <div class="section">
            <h2>五、历史对比与个体基线</h2>
            <p>{vars['personal_baseline_desc']}</p>
            <ul>
                <li><strong>血压对比：</strong>{vars['bp_vs_baseline_text']}</li>
                <li><strong>血糖对比：</strong>{vars['sugar_vs_baseline_text']}</li>
                <li><strong>其他对比：</strong>{vars['others_vs_baseline_text']}</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>六、报告说明</h2>
            <div class="disclaimer">
                {vars['disclaimer'].replace(chr(10), '<br>')}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _get_status_class(self, status: IndicatorStatus) -> str:
        """获取状态对应的CSS类"""
        if status in [IndicatorStatus.NORMAL]:
            return "status-normal"
        elif status in [IndicatorStatus.SLIGHTLY_HIGH, IndicatorStatus.SLIGHTLY_LOW]:
            return "status-warning"
        elif status in [IndicatorStatus.HIGH, IndicatorStatus.LOW, 
                        IndicatorStatus.CRITICAL_HIGH, IndicatorStatus.CRITICAL_LOW]:
            return "status-danger"
        return ""


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    elder_info = ElderBasicInfo(
        elder_id="E001",
        elder_name="张三",
        elder_gender="男",
        elder_age=72,
        elder_phone="13800138000",
        elder_address="北京市朝阳区",
        elder_chronic_tags=["高血压", "血糖偏高倾向"]
    )
    
    current_measurements = {
        'spo2': 97,
        'heart_rate': 78,
        'systolic_bp': 145,
        'diastolic_bp': 88,
        'pulse_rate': 76,
        'body_temperature': 36.5,
        'blood_sugar': 6.8,
        'uric_acid': 380,
        'weight': 68,
        'height': 170
    }
    
    historical_data = {
        'check_count': 15,
        'systolic_bp_history': [138, 142, 145, 140, 148, 135, 142, 144, 146, 141],
        'blood_sugar_history': [6.2, 6.5, 6.8, 6.4, 7.0, 6.3, 6.6, 6.9, 6.5, 6.7],
        'heart_rate_history': [72, 75, 78, 74, 80, 73, 76, 79, 75, 77]
    }
    
    baseline_data = {
        'baseline_days': 90,
        'systolic_bp': {'mean': 138, 'p25': 132, 'p75': 145},
        'blood_sugar': {'mean': 6.3, 'p25': 5.9, 'p75': 6.8}
    }
    
    # 生成报告
    generator = YangShengReportGenerator()
    report = generator.generate_report(
        elder_info=elder_info,
        current_measurements=current_measurements,
        historical_data=historical_data,
        baseline_data=baseline_data
    )
    
    # 输出文本报告
    text_report = generator.render_text_report(report)
    print(text_report)
    
    # 保存HTML报告
    html_report = generator.render_html_report(report)
    with open("health_report_demo.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("\nHTML报告已保存到 health_report_demo.html")
