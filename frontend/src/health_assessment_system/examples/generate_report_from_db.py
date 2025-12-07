"""
从数据库生成养生之道·智能健康报告
Generate YangSheng Report from Database

演示如何从MySQL数据库读取真实数据并生成健康报告
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database_manager import DatabaseManager
from modules.health_report_models import ElderBasicInfo
from modules.yangsheng_report_generator import YangShengReportGenerator


def get_elder_data(db: DatabaseManager, elder_id: int):
    """从数据库获取老人数据"""
    # 1. 获取老人基本信息
    elder_row = db.get_elder_info(elder_id)
    if not elder_row:
        print(f"找不到ID为 {elder_id} 的老人")
        return None, None, None, None
    
    # 转换性别 (0->女, 1->男)
    gender_map = {0: "女", 1: "男", 2: "未知"}
    
    # 处理慢病标签
    chronic_tags = []
    if elder_row.get('chronic_tags'):
        chronic_tags = elder_row['chronic_tags'].split(';')
    
    elder_info = ElderBasicInfo(
        elder_id=str(elder_row['id']),
        elder_name=elder_row['name'],
        elder_gender=gender_map.get(elder_row['gender'], "未知"),
        elder_age=elder_row['age'] or 0,
        elder_phone=elder_row['phone'] or "",
        elder_address=elder_row['address'] or "",
        elder_chronic_tags=chronic_tags
    )
    
    # 2. 获取最新健康记录
    # 由于DatabaseManager没有直接获取最新记录的方法，我们用SQL查询
    sql = "SELECT * FROM health_record WHERE elder_id = %s ORDER BY check_time DESC LIMIT 1"
    latest_records = db.execute_query(sql, (elder_id,))
    
    if not latest_records:
        print(f"老人 {elder_row['name']} 没有健康记录")
        current_measurements = {}
    else:
        record = latest_records[0]
        # 转换为生成器所需的字典格式
        current_measurements = {
            'spo2': record.get('spo2'),
            'heart_rate': record.get('heart_rate'),
            'systolic_bp': record.get('systolic_bp'),
            'diastolic_bp': record.get('diastolic_bp'),
            'pulse_rate': record.get('pulse_rate') or record.get('heart_rate'), # 如果没有脉率，用心率代替
            'body_temperature': float(record['body_temperature']) if record.get('body_temperature') else None,
            'blood_sugar': float(record['blood_sugar']) if record.get('blood_sugar') else None,
            'blood_sugar_type': 'fasting', # 假设为空腹
            'uric_acid': record.get('uric_acid'),
            'weight': float(record['weight_kg']) if record.get('weight_kg') else None,
            'height': float(elder_row['height_cm']) if elder_row.get('height_cm') else None
        }
    
    # 3. 获取历史数据 (过去700天，覆盖2024年数据)
    history_records = db.get_health_history(elder_id, days=700)
    
    # 提取数据序列
    systolic_bp_history = [r['systolic_bp'] for r in history_records if r.get('systolic_bp')]
    blood_sugar_history = [float(r['blood_sugar']) for r in history_records if r.get('blood_sugar')]
    heart_rate_history = [r['heart_rate'] for r in history_records if r.get('heart_rate')]
    temp_history = [float(r['body_temperature']) for r in history_records if r.get('body_temperature')]
    
    historical_data = {
        'check_count': len(history_records),
        'systolic_bp_history': systolic_bp_history,
        'blood_sugar_history': blood_sugar_history,
        'heart_rate_history': heart_rate_history,
        'body_temperature_history': temp_history,
        # 简单模拟组合特征
        'bp_sleep_correlation': False,
        'hr_time_pattern': False
    }
    
    # 4. 计算基线数据 (基于历史数据)
    # 如果数据量足够，计算统计值
    baseline_data = {'baseline_days': 90}
    
    if len(systolic_bp_history) >= 3:
        baseline_data['systolic_bp'] = {
            'mean': float(np.mean(systolic_bp_history)),
            'std': float(np.std(systolic_bp_history)),
            'p25': float(np.percentile(systolic_bp_history, 25)),
            'p75': float(np.percentile(systolic_bp_history, 75))
        }
    
    if len(blood_sugar_history) >= 3:
        baseline_data['blood_sugar'] = {
            'mean': float(np.mean(blood_sugar_history)),
            'std': float(np.std(blood_sugar_history)),
            'p25': float(np.percentile(blood_sugar_history, 25)),
            'p75': float(np.percentile(blood_sugar_history, 75))
        }
        
    if len(heart_rate_history) >= 3:
        baseline_data['heart_rate'] = {
            'mean': float(np.mean(heart_rate_history)),
            'std': float(np.std(heart_rate_history)),
            'p25': float(np.percentile(heart_rate_history, 25)),
            'p75': float(np.percentile(heart_rate_history, 75))
        }
        
    return elder_info, current_measurements, historical_data, baseline_data


def main():
    """主函数"""
    print("=" * 70)
    print("养生之道·智能健康报告生成器 (数据库版)")
    print("=" * 70)
    
    # 1. 连接数据库
    # 这里的密码需要在实际运行时提供，或者配置环境变量
    # 为演示方便，尝试使用默认无密码或常用密码，如果不成功会报错
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '', # 请根据实际情况修改
        'database': 'health_assessment_db'
    }
    
    # 尝试从命令行获取密码
    if len(sys.argv) > 1:
        db_config['password'] = sys.argv[1]
    else:
        # 尝试硬编码一个常用的开发密码 (根据之前的上下文)
        db_config['password'] = '123456'
        
    print(f"正在连接数据库 ({db_config['host']}:{db_config['port']})...")
    db = DatabaseManager(db_config)
    
    if not hasattr(db, 'pool') or not db.pool:
        print("❌ 数据库连接失败，请检查配置")
        return
        
    # 2. 获取老人数据 (以ID=1 张秀英为例)
    elder_id = 1
    print(f"\n正在获取老人 (ID={elder_id}) 的数据...")
    
    elder_info, current_measurements, historical_data, baseline_data = get_elder_data(db, elder_id)
    
    if not elder_info:
        print("❌ 获取数据失败")
        return
        
    print(f"老人姓名: {elder_info.elder_name}")
    print(f"最近检测时间: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"历史记录数: {historical_data['check_count']}")
    
    # 3. 生成报告
    print("\n正在生成报告...")
    generator = YangShengReportGenerator()
    
    report_data = generator.generate_report(
        elder_info=elder_info,
        current_measurements=current_measurements,
        historical_data=historical_data,
        baseline_data=baseline_data,
        trend_window_days=700 # 使用700天窗口以匹配我们的数据
    )
    
    # 4. 保存报告
    output_dir = Path(__file__).parent
    
    # 保存HTML
    html_filename = f"report_db_{elder_info.elder_id}_{elder_info.elder_name}.html"
    html_path = output_dir / html_filename
    html_content = generator.render_html_report(report_data)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n✅ HTML报告已保存: {html_path}")
    
    # 保存JSON
    json_filename = f"report_db_{elder_info.elder_id}_{elder_info.elder_name}.json"
    json_path = output_dir / json_filename
    json_content = generator.render_json_report(report_data)
    
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_content)
    print(f"✅ JSON数据已保存: {json_path}")
    
    # 5. 显示预览
    print("\n" + "=" * 70)
    print("文本报告预览")
    print("=" * 70)
    print(generator.render_text_report(report_data))
    
    print("\n" + "=" * 70)
    print("完成！")


if __name__ == "__main__":
    main()
