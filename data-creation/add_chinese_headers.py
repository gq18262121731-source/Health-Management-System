"""
为CSV文件添加中文列索引
在每个CSV文件的字段名下方添加一行中文说明
"""
import pandas as pd
import os

# 字段名到中文的映射字典
FIELD_MAPPING = {
    # 老人信息表
    "id": "记录ID",
    "name": "姓名",
    "gender": "性别（0女/1男）",
    "birthday": "出生日期",
    "age": "年龄",
    "phone": "联系电话",
    "address": "居住地址",
    "height_cm": "身高（厘米）",
    "chronic_tags": "慢病标签",
    "status": "状态（1在管/0已离开）",
    "remark": "备注",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    
    # 健康记录表
    "elder_id": "老人ID",
    "elder_name": "老人姓名",
    "tester_code": "检测人/设备编号",
    "check_time": "检查时间",
    "spo2": "血氧饱和度（%）",
    "spo2_status": "血氧情况",
    "heart_rate": "心率（次/分）",
    "heart_rate_status": "心率情况",
    "diastolic_bp": "舒张压（mmHg）",
    "diastolic_bp_status": "舒张压情况",
    "systolic_bp": "收缩压（mmHg）",
    "systolic_bp_status": "收缩压情况",
    "pulse_rate": "脉率（次/分）",
    "pulse_rate_status": "脉率情况",
    "blood_sugar": "血糖（mmol/L）",
    "blood_sugar_status": "血糖情况",
    "uric_acid": "血尿酸（μmol/L）",
    "body_temperature": "体温（℃）",
    "health_risk_level": "健康风险等级",
    "potential_risk_note": "潜在风险备注",
    "sleep_hours": "睡眠时长（小时）",
    "steps": "步数",
    "weight_kg": "体重（公斤）",
    "data_source": "数据来源",
}

def add_chinese_header_to_csv(csv_file):
    """为CSV文件添加中文列索引"""
    print(f"处理文件: {csv_file}")
    
    # 读取CSV文件
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # 获取字段名列表
    columns = df.columns.tolist()
    
    # 创建中文列名列表
    chinese_columns = []
    for col in columns:
        # 处理合并字段名（如 name_elder）
        base_col = col.split('_')[0] if '_' in col else col
        chinese_name = FIELD_MAPPING.get(col, FIELD_MAPPING.get(base_col, col))
        chinese_columns.append(chinese_name)
    
    # 创建新的DataFrame，第一行是英文字段名，第二行是中文说明
    # 方法：在数据前插入一行中文说明
    chinese_row = pd.DataFrame([chinese_columns], columns=columns)
    
    # 合并中文行和数据
    df_with_header = pd.concat([chinese_row, df], ignore_index=True)
    
    # 保存文件（添加_chinese后缀）
    output_file = csv_file.replace('.csv', '_chinese.csv')
    df_with_header.to_csv(output_file, index=False, encoding='utf-8-sig', header=False)
    
    print(f"  ✓ 已生成: {output_file}")
    print(f"    总行数: {len(df_with_header)} (包含1行中文说明 + {len(df)} 条数据)")
    
    return output_file

def create_csv_with_dual_headers(csv_file):
    """创建带双行表头的CSV（第一行英文，第二行中文）"""
    print(f"处理文件: {csv_file}")
    
    # 读取CSV文件
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # 获取字段名列表
    columns = df.columns.tolist()
    
    # 创建中文列名列表
    chinese_columns = []
    for col in columns:
        base_col = col.split('_')[0] if '_' in col else col
        chinese_name = FIELD_MAPPING.get(col, FIELD_MAPPING.get(base_col, col))
        chinese_columns.append(chinese_name)
    
    # 创建输出文件
    output_file = csv_file.replace('.csv', '_chinese.csv')
    
    # 写入文件：先写英文字段名，再写中文说明，然后写数据
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        # 写入英文字段名
        f.write(','.join(columns) + '\n')
        # 写入中文说明
        f.write(','.join(chinese_columns) + '\n')
        # 写入数据
        df.to_csv(f, index=False, header=False, lineterminator='\n')
    
    print(f"  ✓ 已生成: {output_file}")
    print(f"    格式: 第1行=英文字段名, 第2行=中文说明, 第3行起=数据")
    
    return output_file

# 主程序
if __name__ == "__main__":
    print("=" * 60)
    print("为CSV文件添加中文列索引")
    print("=" * 60)
    print()
    
    # 要处理的CSV文件列表
    csv_files = [
        "health_data_simple.csv",
        "health_record.csv",
        "elder_health_merged.csv",
        "老人基础信息表.csv"
    ]
    
    # 检查文件是否存在
    existing_files = []
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            existing_files.append(csv_file)
        else:
            print(f"⚠️  文件不存在: {csv_file}")
    
    if not existing_files:
        print("❌ 没有找到要处理的CSV文件")
        exit(1)
    
    print(f"找到 {len(existing_files)} 个文件待处理\n")
    
    # 处理每个文件
    for csv_file in existing_files:
        try:
            create_csv_with_dual_headers(csv_file)
            print()
        except Exception as e:
            print(f"  ❌ 处理失败: {e}\n")
    
    print("=" * 60)
    print("处理完成！")
    print("=" * 60)
    print("\n生成的文件说明：")
    print("- 文件名格式: 原文件名_chinese.csv")
    print("- 第1行: 英文字段名")
    print("- 第2行: 中文列索引")
    print("- 第3行起: 数据内容")
    print("\n这些文件可以在Excel中正常打开，中文说明会显示在第二行。")

