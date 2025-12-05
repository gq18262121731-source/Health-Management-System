"""
生成CSV格式的虚拟数据
为3位老人生成完整的健康监测数据，输出为CSV文件
"""
import random
import json
import pandas as pd
from datetime import datetime, timedelta, date

# 设置随机种子，保证可重复
random.seed(42)

# ========== 全局配置 ==========
BASE_START_DATE = datetime(2024, 1, 1)
BASE_END_DATE = datetime(2024, 12, 31)
RECORDS_PER_ELDER = 40  # 每位老人40条体征记录
ASSESSMENTS_PER_ELDER = 8  # 每位老人8次评估
AI_LOGS_PER_ELDER = 5  # 每位老人5次AI问诊

# ========== 3位老人的基础信息 ==========
ELDERS = [
    {
        "id": 1,
        "name": "张秀英",
        "gender": 0,
        "birthday": date(1945, 3, 12),
        "age": 79,
        "phone": "13812345678",
        "address": "广州市天河区天福路88号颐康花园小区3栋502",
        "height_cm": 155.20,
        "chronic_tags": "高血压;2型糖尿病",
        "status": 1,
        "remark": "行动稍慢，需扶手；日常能自理，女儿偶尔陪同复查"
    },
    {
        "id": 2,
        "name": "李强",
        "gender": 1,
        "birthday": date(1948, 11, 25),
        "age": 76,
        "phone": "13987654321",
        "address": "广州市天河区天福路88号颐康花园小区3栋402",
        "height_cm": 167.80,
        "chronic_tags": "高血压",
        "status": 1,
        "remark": "有30年以上吸烟史，已在逐步减量；偶尔晨练太极"
    },
    {
        "id": 3,
        "name": "王磊",
        "gender": 1,
        "birthday": date(1952, 7, 3),
        "age": 72,
        "phone": "13755556666",
        "address": "广州市天河区天福路88号颐康花园小区2栋1203",
        "height_cm": 170.50,
        "chronic_tags": "高脂血症",
        "status": 1,
        "remark": "BMI略高，体重控制一般；喜欢晚间散步45分钟"
    }
]

# ========== 辅助函数 ==========
def random_datetime(start: datetime, end: datetime):
    """生成随机时间"""
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)

def random_time_in_day(base_date: date, morning_prob=0.6):
    """在指定日期生成随机时间，倾向于早上"""
    if random.random() < morning_prob:
        hour = random.randint(7, 10)
        minute = random.randint(0, 59)
    else:
        hour = random.randint(18, 21)
        minute = random.randint(0, 59)
    return datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))

def get_bp_for_elder(elder_id, chronic_tags):
    """根据老人慢病情况生成血压"""
    has_hypertension = "高血压" in chronic_tags
    if has_hypertension:
        rand = random.random()
        if rand < 0.6:
            systolic = random.randint(140, 165)
            diastolic = random.randint(88, 100)
        elif rand < 0.9:
            systolic = random.randint(125, 139)
            diastolic = random.randint(80, 87)
        else:
            systolic = random.randint(166, 180)
            diastolic = random.randint(101, 110)
    else:
        if random.random() < 0.8:
            systolic = random.randint(110, 129)
            diastolic = random.randint(70, 84)
        else:
            systolic = random.randint(130, 139)
            diastolic = random.randint(85, 87)
    return systolic, diastolic

def get_blood_sugar_for_elder(elder_id, chronic_tags):
    """根据老人慢病情况生成血糖"""
    has_diabetes = "2型糖尿病" in chronic_tags
    if has_diabetes:
        rand = random.random()
        if rand < 0.7:
            sugar = round(random.uniform(7.0, 9.5), 1)
        elif rand < 0.9:
            sugar = round(random.uniform(6.1, 6.9), 1)
        else:
            sugar = round(random.uniform(9.6, 12.0), 1)
    else:
        if random.random() < 0.85:
            sugar = round(random.uniform(4.0, 6.0), 1)
        else:
            sugar = round(random.uniform(6.1, 7.0), 1)
    return sugar

# ========== 1. 生成 elder_info ==========
elder_rows = []
for elder in ELDERS:
    elder_rows.append({
        "id": elder["id"],
        "name": elder["name"],
        "gender": elder["gender"],
        "birthday": elder["birthday"],
        "age": elder["age"],
        "phone": elder["phone"],
        "address": elder["address"],
        "height_cm": elder["height_cm"],
        "chronic_tags": elder["chronic_tags"],
        "status": elder["status"],
        "remark": elder["remark"],
        "created_at": BASE_START_DATE,
        "updated_at": BASE_START_DATE + timedelta(days=random.randint(0, 30))
    })

df_elder = pd.DataFrame(elder_rows)

# ========== 2. 生成 health_record ==========
health_rows = []
record_id = 1

for elder in ELDERS:
    elder_id = elder["id"]
    chronic_tags = elder["chronic_tags"]
    
    # 生成40条记录，均匀分布在2024年
    dates = []
    start_date = BASE_START_DATE.date()
    end_date = BASE_END_DATE.date()
    days_diff = (end_date - start_date).days
    
    for i in range(RECORDS_PER_ELDER):
        day_offset = int(days_diff * i / RECORDS_PER_ELDER) + random.randint(-3, 3)
        check_date = start_date + timedelta(days=day_offset)
        check_date = max(start_date, min(end_date, check_date))
        dates.append(check_date)
    
    dates.sort()
    
    for check_date in dates:
        check_time = random_time_in_day(check_date)
        
        # 血氧
        if random.random() < 0.92:
            spo2 = random.randint(95, 100)
            spo2_status = "正常"
        elif random.random() < 0.98:
            spo2 = random.randint(90, 94)
            spo2_status = "偏低"
        else:
            spo2 = random.randint(88, 89)
            spo2_status = "严重偏低"
        
        # 血压
        systolic, diastolic = get_bp_for_elder(elder_id, chronic_tags)
        if systolic < 120 and diastolic < 80:
            bp_status = "正常"
        elif systolic < 140 and diastolic < 90:
            bp_status = "偏高"
        else:
            bp_status = "高血压"
        
        # 心率/脉率
        heart_rate = random.randint(65, 95)
        pulse_rate = heart_rate + random.randint(-3, 3)
        if 60 <= heart_rate <= 100:
            heart_rate_status = "正常"
        else:
            heart_rate_status = "异常"
        if 60 <= pulse_rate <= 100:
            pulse_rate_status = "正常"
        else:
            pulse_rate_status = "异常"
        
        # 体温
        if random.random() < 0.95:
            body_temp = round(random.uniform(36.3, 37.2), 1)
        else:
            body_temp = round(random.uniform(37.3, 38.2), 1)
        
        # 血糖
        blood_sugar = get_blood_sugar_for_elder(elder_id, chronic_tags)
        if blood_sugar < 6.1:
            blood_sugar_status = "正常"
        elif blood_sugar < 7.0:
            blood_sugar_status = "偏高"
        else:
            blood_sugar_status = "高血糖"
        
        # 血尿酸
        uric_acid = random.randint(280, 420)
        
        # 风险等级评估
        risk_score = 0
        if systolic >= 140 or diastolic >= 90:
            risk_score += 2
        if spo2 < 94:
            risk_score += 2
        if body_temp >= 37.5:
            risk_score += 1
        if blood_sugar >= 7.0:
            risk_score += 2
        
        if risk_score == 0:
            risk_level = "正常"
        elif risk_score <= 2:
            risk_level = "轻度风险"
        elif risk_score <= 4:
            risk_level = "中度风险"
        else:
            risk_level = "高风险"
        
        # 生活方式数据
        sleep_hours = round(random.uniform(5.5, 8.0), 1)
        if elder_id == 3:  # 王磊喜欢散步
            steps = random.randint(6000, 9000)
        else:
            steps = random.randint(3000, 6000)
        
        if elder_id == 3:  # 王磊BMI略高
            weight_kg = round(random.uniform(73, 76), 1)
        elif elder_id == 1:  # 张秀英
            weight_kg = round(random.uniform(57, 60), 1)
        else:  # 李强
            weight_kg = round(random.uniform(69, 72), 1)
        
        # 潜在风险备注
        risk_notes = []
        if systolic >= 150:
            risk_notes.append("血压明显偏高")
        if blood_sugar >= 8.0:
            risk_notes.append("血糖控制不佳")
        if spo2 < 94:
            risk_notes.append("血氧偏低")
        potential_risk_note = "；".join(risk_notes) if risk_notes else "无"
        
        health_rows.append({
            "id": record_id,
            "elder_id": elder_id,
            "elder_name": elder["name"],
            "tester_code": f"RCDJKUSER{random.randint(1, 10):04d}",
            "check_time": check_time,
            "phone": elder["phone"],
            "age": elder["age"],
            "spo2": spo2,
            "spo2_status": spo2_status,
            "heart_rate": heart_rate,
            "heart_rate_status": heart_rate_status,
            "diastolic_bp": diastolic,
            "diastolic_bp_status": bp_status,
            "systolic_bp": systolic,
            "systolic_bp_status": bp_status,
            "pulse_rate": pulse_rate,
            "pulse_rate_status": pulse_rate_status,
            "blood_sugar": blood_sugar,
            "blood_sugar_status": blood_sugar_status,
            "uric_acid": uric_acid,
            "body_temperature": body_temp,
            "health_risk_level": risk_level,
            "potential_risk_note": potential_risk_note,
            "sleep_hours": sleep_hours,
            "steps": steps,
            "weight_kg": weight_kg,
            "data_source": random.choice(["MANUAL", "DEVICE", "IMPORT"]),
            "created_at": check_time,
            "updated_at": check_time + timedelta(minutes=random.randint(0, 30))
        })
        record_id += 1

df_health = pd.DataFrame(health_rows)

# ========== 3. 生成综合数据表（合并老人信息和健康记录）==========
# 创建一个便于分析的合并表
merged_data = df_health.merge(df_elder[["id", "name", "gender", "chronic_tags", "address"]], 
                              left_on="elder_id", right_on="id", suffixes=("", "_elder"))
merged_data = merged_data.drop(columns=["id"])

# ========== 字段名到中文的映射 ==========
FIELD_MAPPING = {
    "id": "记录ID",
    "elder_id": "老人ID",
    "elder_name": "老人姓名",
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
    "created_at": "创建时间",
    "updated_at": "更新时间",
}

def save_csv_with_chinese_header(df, filename):
    """保存CSV文件，包含中文列索引"""
    columns = df.columns.tolist()
    chinese_columns = [FIELD_MAPPING.get(col, col) for col in columns]
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        # 写入英文字段名
        f.write(','.join(columns) + '\n')
        # 写入中文说明
        f.write(','.join(chinese_columns) + '\n')
        # 写入数据
        df.to_csv(f, index=False, header=False, lineterminator='\n')

# ========== 保存为CSV文件 ==========
print("=" * 60)
print("正在生成CSV文件（带中文列索引）...")
print("=" * 60)

# 1. 老人信息表
save_csv_with_chinese_header(df_elder, "elder_info.csv")
print(f"✓ elder_info.csv - {len(df_elder)} 条记录（第1行=英文，第2行=中文）")

# 2. 健康记录表
save_csv_with_chinese_header(df_health, "health_record.csv")
print(f"✓ health_record.csv - {len(df_health)} 条记录（第1行=英文，第2行=中文）")

# 3. 综合数据表（合并表，便于分析）
save_csv_with_chinese_header(merged_data, "elder_health_merged.csv")
print(f"✓ elder_health_merged.csv - {len(merged_data)} 条记录（合并表，第1行=英文，第2行=中文）")

# 4. 生成一个简化的主要数据表（只包含关键字段）
df_simple = df_health[[
    "elder_id", "elder_name", "check_time", 
    "systolic_bp", "diastolic_bp", "blood_sugar", 
    "spo2", "heart_rate", "body_temperature",
    "health_risk_level", "steps", "weight_kg"
]].copy()
save_csv_with_chinese_header(df_simple, "health_data_simple.csv")
print(f"✓ health_data_simple.csv - {len(df_simple)} 条记录（简化版，第1行=英文，第2行=中文）")

print("=" * 60)
print("CSV文件生成完成！")
print("=" * 60)
print("\n生成的文件：")
print("1. elder_info.csv - 老人基础信息")
print("2. health_record.csv - 完整健康记录（所有字段）")
print("3. elder_health_merged.csv - 合并表（健康记录+老人信息）")
print("4. health_data_simple.csv - 简化版（主要字段）")
print("\n文件格式说明：")
print("- 第1行：英文字段名")
print("- 第2行：中文列索引")
print("- 第3行起：数据内容")
print("\n所有文件使用 UTF-8-BOM 编码，可在Excel中正常打开显示中文。")

