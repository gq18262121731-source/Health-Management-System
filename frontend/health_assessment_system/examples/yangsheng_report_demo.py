"""
养生之道·智能健康报告 完整演示
YangSheng Health Report Demo

演示如何生成符合模板的健康报告
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.health_report_models import ElderBasicInfo
from modules.yangsheng_report_generator import YangShengReportGenerator


def create_demo_data():
    """创建演示数据"""
    
    # 1. 老人基本信息
    elder_info = ElderBasicInfo(
        elder_id="E20231127001",
        elder_name="王大爷",
        elder_gender="男",
        elder_age=75,
        elder_phone="13912345678",
        elder_address="上海市浦东新区康桥镇",
        elder_chronic_tags=["高血压", "血糖偏高倾向", "长期睡眠不足"]
    )
    
    # 2. 当前测量数据
    current_measurements = {
        # 生命体征
        'spo2': 96,              # 血氧 %
        'heart_rate': 82,        # 心率 次/分
        'systolic_bp': 148,      # 收缩压 mmHg
        'diastolic_bp': 92,      # 舒张压 mmHg
        'pulse_rate': 80,        # 脉率 次/分
        'body_temperature': 36.6, # 体温 ℃
        
        # 代谢指标
        'blood_sugar': 7.2,      # 血糖 mmol/L
        'blood_sugar_type': 'fasting',  # 空腹血糖
        'uric_acid': 420,        # 血尿酸 μmol/L
        'weight': 72,            # 体重 kg
        'height': 168            # 身高 cm (用于计算BMI)
    }
    
    # 3. 历史数据（用于趋势分析）
    historical_data = {
        'check_count': 18,  # 有效检测次数
        
        # 收缩压历史记录
        'systolic_bp_history': [
            142, 145, 148, 140, 152, 138, 146, 150, 144, 148,
            141, 147, 149, 143, 151, 139, 145, 148
        ],
        
        # 血糖历史记录
        'blood_sugar_history': [
            6.5, 6.8, 7.0, 6.6, 7.2, 6.4, 6.9, 7.1, 6.7, 7.0,
            6.5, 6.8, 7.0, 6.6, 7.1, 6.4, 6.9, 7.2
        ],
        
        # 心率历史记录
        'heart_rate_history': [
            76, 78, 82, 74, 85, 72, 80, 83, 77, 81,
            75, 79, 82, 76, 84, 73, 80, 82
        ],
        
        # 体温历史记录
        'body_temperature_history': [
            36.4, 36.5, 36.6, 36.3, 36.7, 36.4, 36.5, 36.6,
            36.4, 36.5, 36.6, 36.4, 36.7, 36.5, 36.6, 36.5,
            36.4, 36.6
        ],
        
        # 组合特征标记
        'bp_sleep_correlation': True,  # 血压与睡眠相关
        'hr_time_pattern': True        # 心率与时间相关
    }
    
    # 4. 个人基线数据（基于过去90天）
    baseline_data = {
        'baseline_days': 90,
        
        'systolic_bp': {
            'mean': 144,
            'std': 5.2,
            'p25': 140,
            'p75': 149
        },
        
        'diastolic_bp': {
            'mean': 88,
            'std': 4.1,
            'p25': 85,
            'p75': 92
        },
        
        'blood_sugar': {
            'mean': 6.7,
            'std': 0.3,
            'p25': 6.4,
            'p75': 7.0
        },
        
        'heart_rate': {
            'mean': 78,
            'std': 4.0,
            'p25': 75,
            'p75': 82
        }
    }
    
    return elder_info, current_measurements, historical_data, baseline_data


def main():
    """主函数"""
    print("=" * 70)
    print("养生之道·智能健康报告 生成演示")
    print("=" * 70)
    
    # 创建演示数据
    elder_info, current_measurements, historical_data, baseline_data = create_demo_data()
    
    # 创建报告生成器
    generator = YangShengReportGenerator()
    
    # 生成报告数据
    print("\n正在生成报告...")
    report_data = generator.generate_report(
        elder_info=elder_info,
        current_measurements=current_measurements,
        historical_data=historical_data,
        baseline_data=baseline_data,
        trend_window_days=30
    )
    
    print(f"报告ID: {report_data.report_id}")
    print(f"报告时间: {report_data.report_date}")
    
    # 生成文本格式报告
    print("\n" + "=" * 70)
    print("文本格式报告")
    print("=" * 70)
    text_report = generator.render_text_report(report_data)
    print(text_report)
    
    # 保存HTML报告
    html_report = generator.render_html_report(report_data)
    html_path = Path(__file__).parent / "yangsheng_report_demo.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"\nHTML报告已保存到: {html_path}")
    
    # 保存JSON数据
    json_report = generator.render_json_report(report_data)
    json_path = Path(__file__).parent / "yangsheng_report_demo.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_report)
    print(f"JSON数据已保存到: {json_path}")
    
    # 输出模板变量（用于调试）
    print("\n" + "=" * 70)
    print("模板变量预览")
    print("=" * 70)
    template_vars = report_data.to_template_vars()
    for key, value in template_vars.items():
        if not isinstance(value, list):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value[:3]}..." if len(value) > 3 else f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
