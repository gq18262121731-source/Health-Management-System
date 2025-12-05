"""
为3位老人生成完整的虚拟数据
包括：elder_info, user_account, elder_user_relation, health_record, assessment_result, ai_consult_log
"""
import random
import json
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
        # 高血压患者：60%概率偏高，30%正常，10%明显高
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
        # 非高血压：80%正常，20%偏高
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
        # 糖尿病患者：70%偏高，20%正常，10%明显高
        rand = random.random()
        if rand < 0.7:
            sugar = round(random.uniform(7.0, 9.5), 1)
        elif rand < 0.9:
            sugar = round(random.uniform(6.1, 6.9), 1)
        else:
            sugar = round(random.uniform(9.6, 12.0), 1)
    else:
        # 非糖尿病：85%正常，15%偏高
        if random.random() < 0.85:
            sugar = round(random.uniform(4.0, 6.0), 1)
        else:
            sugar = round(random.uniform(6.1, 7.0), 1)
    return sugar

def get_status_for_value(value, thresholds, statuses):
    """根据数值返回状态"""
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return statuses[i]
    return statuses[-1]

# ========== 1. 生成 user_account ==========
user_accounts = []
user_id_counter = 1
elder_user_relations = []
relation_id_counter = 1

for elder in ELDERS:
    elder_id = elder["id"]
    
    # 老人自己的账号
    user_accounts.append({
        "id": user_id_counter,
        "username": elder["phone"],
        "password_hash": "$2b$12$example_hash_here",
        "role": "ELDER",
        "display_name": elder["name"],
        "phone": elder["phone"],
        "email": f"elder{elder_id}@example.com",
        "status": 1,
        "last_login_at": random_datetime(BASE_START_DATE, BASE_END_DATE),
        "created_at": datetime(2024, 1, 1, 9, 0, 0),
        "updated_at": datetime(2024, 1, 1, 9, 0, 0)
    })
    elder_user_relations.append({
        "id": relation_id_counter,
        "elder_id": elder_id,
        "user_id": user_id_counter,
        "relation_type": "SELF",
        "is_primary": 1,
        "created_at": datetime(2024, 1, 1, 9, 0, 0)
    })
    relation_id_counter += 1
    user_id_counter += 1
    
    # 为张秀英添加女儿账号
    if elder_id == 1:
        daughter_phone = "13812345679"
        user_accounts.append({
            "id": user_id_counter,
            "username": daughter_phone,
            "password_hash": "$2b$12$example_hash_here",
            "role": "FAMILY",
            "display_name": "张秀英女儿",
            "phone": daughter_phone,
            "email": f"family{elder_id}@example.com",
            "status": 1,
            "last_login_at": random_datetime(BASE_START_DATE, BASE_END_DATE),
            "created_at": datetime(2024, 1, 1, 9, 0, 0),
            "updated_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        elder_user_relations.append({
            "id": relation_id_counter,
            "elder_id": elder_id,
            "user_id": user_id_counter,
            "relation_type": "CHILD",
            "is_primary": 0,
            "created_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        relation_id_counter += 1
        user_id_counter += 1
    
    # 为李强添加儿子账号
    if elder_id == 2:
        son_phone = "13987654322"
        user_accounts.append({
            "id": user_id_counter,
            "username": son_phone,
            "password_hash": "$2b$12$example_hash_here",
            "role": "FAMILY",
            "display_name": "李强儿子",
            "phone": son_phone,
            "email": f"family{elder_id}@example.com",
            "status": 1,
            "last_login_at": random_datetime(BASE_START_DATE, BASE_END_DATE),
            "created_at": datetime(2024, 1, 1, 9, 0, 0),
            "updated_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        elder_user_relations.append({
            "id": relation_id_counter,
            "elder_id": elder_id,
            "user_id": user_id_counter,
            "relation_type": "CHILD",
            "is_primary": 0,
            "created_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        relation_id_counter += 1
        user_id_counter += 1
    
    # 为3位老人添加一个社区医生账号（共享）
    if elder_id == 1:
        community_phone = "13800000001"
        user_accounts.append({
            "id": user_id_counter,
            "username": community_phone,
            "password_hash": "$2b$12$example_hash_here",
            "role": "COMMUNITY",
            "display_name": "社区医生-王医生",
            "phone": community_phone,
            "email": "doctor@community.com",
            "status": 1,
            "last_login_at": random_datetime(BASE_START_DATE, BASE_END_DATE),
            "created_at": datetime(2024, 1, 1, 9, 0, 0),
            "updated_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        community_user_id = user_id_counter
        user_id_counter += 1
    
    if elder_id <= 3:
        elder_user_relations.append({
            "id": relation_id_counter,
            "elder_id": elder_id,
            "user_id": community_user_id,
            "relation_type": "DOCTOR",
            "is_primary": 0,
            "created_at": datetime(2024, 1, 1, 9, 0, 0)
        })
        relation_id_counter += 1

# ========== 2. 生成 health_record ==========
health_records = []
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
        
        health_records.append({
            "id": record_id,
            "elder_id": elder_id,
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

# ========== 3. 生成 assessment_result ==========
assessment_results = []
assessment_id = 1

for elder in ELDERS:
    elder_id = elder["id"]
    chronic_tags = elder["chronic_tags"]
    
    # 获取该老人的所有健康记录
    elder_records = [r for r in health_records if r["elder_id"] == elder_id]
    if not elder_records:
        continue
    
    # 生成8次评估，均匀分布
    assessment_times = []
    start_date = BASE_START_DATE.date()
    end_date = BASE_END_DATE.date()
    days_diff = (end_date - start_date).days
    
    for i in range(ASSESSMENTS_PER_ELDER):
        day_offset = int(days_diff * (i + 1) / (ASSESSMENTS_PER_ELDER + 1))
        assess_date = start_date + timedelta(days=day_offset)
        assessment_times.append(datetime.combine(assess_date, datetime.min.time().replace(hour=10, minute=0)))
    
    for assess_time in assessment_times:
        # 评估窗口：往前推30天
        window_end = assess_time.date()
        window_start = window_end - timedelta(days=30)
        
        # 计算窗口内的记录统计
        window_records = [r for r in elder_records 
                          if window_start <= r["check_time"].date() <= window_end]
        
        if window_records:
            avg_systolic = sum(r["systolic_bp"] for r in window_records) / len(window_records)
            avg_diastolic = sum(r["diastolic_bp"] for r in window_records) / len(window_records)
            avg_blood_sugar = sum(r["blood_sugar"] for r in window_records) / len(window_records)
            avg_sleep = sum(r["sleep_hours"] for r in window_records) / len(window_records)
            avg_steps = int(sum(r["steps"] for r in window_records) / len(window_records))
        else:
            avg_systolic = 130
            avg_diastolic = 85
            avg_blood_sugar = 6.0
            avg_sleep = 6.5
            avg_steps = 5000
        
        # 综合风险评分（0-100）
        risk_score = 0
        if avg_systolic >= 140:
            risk_score += 25
        elif avg_systolic >= 130:
            risk_score += 15
        if avg_diastolic >= 90:
            risk_score += 20
        elif avg_diastolic >= 85:
            risk_score += 10
        if avg_blood_sugar >= 7.0:
            risk_score += 25
        elif avg_blood_sugar >= 6.1:
            risk_score += 15
        
        # 根据慢病数量增加风险
        comorbidity_count = len([t for t in chronic_tags.split(";") if t])
        risk_score += comorbidity_count * 10
        
        # 生活方式风险
        if avg_sleep < 6:
            risk_score += 10
        if avg_steps < 4000:
            risk_score += 10
        
        overall_risk_score = min(100, max(0, risk_score + random.randint(-10, 10)))
        
        if overall_risk_score < 40:
            overall_risk_level = "LOW"
        elif overall_risk_score < 70:
            overall_risk_level = "MEDIUM"
        else:
            overall_risk_level = "HIGH"
        
        # 各维度评分
        disease_score = round(min(100, overall_risk_score * 0.6 + random.uniform(-5, 5)), 2)
        lifestyle_score = round(min(100, overall_risk_score * 0.3 + random.uniform(-5, 5)), 2)
        trend_score = round(min(100, overall_risk_score * 0.1 + random.uniform(-5, 5)), 2)
        
        # AHP权重
        w_disease = round(random.uniform(0.45, 0.55), 3)
        w_lifestyle = round(random.uniform(0.25, 0.35), 3)
        w_trend = round(1 - w_disease - w_lifestyle, 3)
        
        # TOPSIS分数
        topsis_score = round(random.uniform(0.3, 0.9), 3)
        
        # 趋势判断
        if len(window_records) >= 2:
            recent_records = sorted(window_records, key=lambda x: x["check_time"])[-5:]
            early_records = sorted(window_records, key=lambda x: x["check_time"])[:5]
            if recent_records and early_records:
                recent_avg_bp = sum(r["systolic_bp"] for r in recent_records) / len(recent_records)
                early_avg_bp = sum(r["systolic_bp"] for r in early_records) / len(early_records)
                if recent_avg_bp > early_avg_bp + 5:
                    trend_flag = "UP"
                    trend_notes = "近期血压呈上升趋势，需加强监测"
                elif recent_avg_bp < early_avg_bp - 5:
                    trend_flag = "DOWN"
                    trend_notes = "近期血压有所改善，继续保持"
                else:
                    trend_flag = "STABLE"
                    trend_notes = "整体指标相对稳定"
            else:
                trend_flag = random.choice(["UP", "STABLE", "DOWN"])
                trend_notes = "数据不足，趋势判断需更多数据支撑"
        else:
            trend_flag = "STABLE"
            trend_notes = "数据量较少，无法准确判断趋势"
        
        # 生活方式异常评分
        lifestyle_anomaly = 0
        if avg_sleep < 6:
            lifestyle_anomaly += 0.3
        if avg_steps < 4000:
            lifestyle_anomaly += 0.3
        lifestyle_anomaly_score = round(min(1.0, lifestyle_anomaly + random.uniform(0, 0.2)), 3)
        
        # 生活方式危险因素
        risk_factors = []
        if avg_steps < 4000:
            risk_factors.append("缺乏运动")
        if avg_sleep < 6:
            risk_factors.append("睡眠不足")
        if elder_id == 2:  # 李强有吸烟史
            risk_factors.append("吸烟")
        lifestyle_risk_factors = "；".join(risk_factors) if risk_factors else "无明显危险因素"
        
        # 建议等级
        if overall_risk_score >= 70:
            advice_level = "OUTPATIENT"
        elif overall_risk_score >= 40:
            advice_level = "OBSERVE"
        else:
            advice_level = "OBSERVE"
        
        # 建议话术
        if elder_id == 1:  # 张秀英
            advice_elder = "您目前血压和血糖控制需要加强，请按时服药，注意饮食，如有不适及时就医。"
            advice_family = "建议家属协助监测老人血压和血糖，督促按时服药，定期复查。"
        elif elder_id == 2:  # 李强
            advice_elder = "您的血压波动较大，建议继续控制盐摄入，减少吸烟，保持规律作息。"
            advice_family = "建议家属关注老人血压变化，协助记录测量数据，鼓励戒烟。"
        else:  # 王磊
            advice_elder = "您目前整体情况良好，继续保持规律运动和健康饮食，定期监测。"
            advice_family = "老人健康状况良好，建议继续保持当前生活方式，定期体检。"
        
        # 关键风险因素
        key_factors = []
        if avg_systolic >= 140:
            key_factors.append("血压偏高")
        if avg_blood_sugar >= 7.0:
            key_factors.append("血糖控制不佳")
        if comorbidity_count >= 2:
            key_factors.append("多病共存")
        key_risk_factors = "；".join(key_factors) if key_factors else "无明显关键风险"
        
        reason_summary = f"综合考虑血压、血糖及生活方式因素，当前风险评分为{overall_risk_score:.1f}分。"
        
        # JSON字段
        disease_summary_json = json.dumps({
            "overall_risk_level": overall_risk_level,
            "score": round(overall_risk_score, 2),
            "hypertension": {
                "level": "2级" if avg_systolic >= 160 else "1级" if avg_systolic >= 140 else "正常",
                "score": round(min(100, (avg_systolic - 120) * 2), 2)
            },
            "diabetes": {
                "level": "高血糖" if avg_blood_sugar >= 7.0 else "正常",
                "score": round(min(100, (avg_blood_sugar - 5.0) * 10), 2) if avg_blood_sugar > 5.0 else 0
            }
        }, ensure_ascii=False)
        
        reason_struct_json = json.dumps({
            "top_factors": key_factors[:3] if key_factors else ["无明显异常"],
            "note": reason_summary
        }, ensure_ascii=False)
        
        extra_meta_json = json.dumps({
            "source": "SIMULATED",
            "record_count": len(window_records)
        }, ensure_ascii=False)
        
        assessment_results.append({
            "id": assessment_id,
            "elder_id": elder_id,
            "assessment_time": assess_time,
            "window_start_date": window_start,
            "window_end_date": window_end,
            "data_quality_flag": "OK" if len(window_records) >= 10 else "LACK",
            "data_quality_notes": f"窗口期内有{len(window_records)}条记录",
            "overall_risk_level": overall_risk_level,
            "overall_risk_score": round(overall_risk_score, 2),
            "disease_overall_score": disease_score,
            "lifestyle_risk_score": lifestyle_score,
            "trend_risk_score": trend_score,
            "comorbidity_count": comorbidity_count,
            "main_diseases": chronic_tags,
            "topsis_score": topsis_score,
            "ahp_weight_disease": w_disease,
            "ahp_weight_lifestyle": w_lifestyle,
            "ahp_weight_trend": w_trend,
            "disease_summary_json": disease_summary_json,
            "lifestyle_anomaly_score": lifestyle_anomaly_score,
            "sleep_mean_hours": round(avg_sleep, 1),
            "steps_mean": avg_steps,
            "lifestyle_risk_factors": lifestyle_risk_factors,
            "trend_risk_flag": trend_flag,
            "trend_notes": trend_notes,
            "advice_level": advice_level,
            "advice_text_elder": advice_elder,
            "advice_text_family": advice_family,
            "key_risk_factors": key_risk_factors,
            "reason_summary": reason_summary,
            "reason_struct_json": reason_struct_json,
            "pipeline_version": "PIPELINE_v1.0",
            "disease_model_version": "DISEASE_v1.0",
            "lifestyle_model_version": "LIFESTYLE_v1.0",
            "trend_model_version": "TREND_v1.0",
            "fuse_strategy": "AHP+TOPSIS_v1",
            "extra_meta_json": extra_meta_json,
            "created_at": assess_time
        })
        assessment_id += 1

# ========== 4. 生成 ai_consult_log ==========
ai_consult_logs = []
ai_id = 1

questions_pool = [
    "最近几天老是头晕，是不是血压太高了？",
    "我晚上老睡不着觉，会不会有大问题？",
    "测出来血糖有点高，需要马上吃药吗？",
    "最近走路有点喘，是不是心脏不好？",
    "我的血压一直控制不好，怎么办？",
    "血糖多少算正常？",
    "需要多久测一次血压？",
    "最近感觉身体有点累，是不是有什么问题？"
]

answers_pool = [
    "根据您最近的监测数据，血压确实偏高，建议您按时服药，控制盐摄入，如持续异常请到医院进一步检查。",
    "睡眠问题可能与情绪和作息有关，建议调整作息时间，避免睡前饮用咖啡或茶，如仍无改善请咨询医生。",
    "血糖略高，建议控制饮食并增加适量运动，如多次复测仍高应尽快就诊内分泌科。",
    "如果出现持续胸闷或胸痛，应立即就医，避免剧烈活动，建议做心电图检查。",
    "血压控制需要综合管理，包括规律服药、低盐饮食、适量运动，建议定期监测并记录数据。",
    "正常空腹血糖应在3.9-6.1mmol/L之间，餐后2小时应小于7.8mmol/L，建议定期监测。",
    "建议每天早晚各测一次血压，最好在固定时间测量，记录数据以便医生参考。",
    "如果持续感到疲劳，可能与多种因素有关，建议结合最近的体检数据，必要时到医院做全面检查。"
]

for elder in ELDERS:
    elder_id = elder["id"]
    
    # 获取该老人的评估结果
    elder_assessments = [a for a in assessment_results if a["elder_id"] == elder_id]
    if not elder_assessments:
        continue
    
    # 获取该老人关联的用户ID
    elder_users = [r["user_id"] for r in elder_user_relations if r["elder_id"] == elder_id]
    
    # 生成5次问诊
    for i in range(AI_LOGS_PER_ELDER):
        # 随机选择一个评估时间作为问诊时间
        if elder_assessments:
            ref_assessment = random.choice(elder_assessments)
            consult_time = ref_assessment["assessment_time"] + timedelta(days=random.randint(0, 7))
            ref_assessment_id = ref_assessment["id"]
            risk_level_at_time = ref_assessment["overall_risk_level"]
        else:
            consult_time = random_datetime(BASE_START_DATE, BASE_END_DATE)
            ref_assessment_id = None
            risk_level_at_time = random.choice(["LOW", "MEDIUM", "HIGH"])
        
        # 随机选择用户
        user_id = random.choice(elder_users) if elder_users else None
        
        # 根据用户角色确定channel
        if user_id:
            user = next((u for u in user_accounts if u["id"] == user_id), None)
            if user:
                channel = user["role"]
            else:
                channel = random.choice(["ELDER", "FAMILY", "COMMUNITY"])
        else:
            channel = "ELDER"
        
        question = random.choice(questions_pool)
        answer = random.choice(answers_pool)
        
        ai_consult_logs.append({
            "id": ai_id,
            "elder_id": elder_id,
            "user_id": user_id,
            "consult_time": consult_time,
            "channel": channel,
            "question": question,
            "answer": answer,
            "ref_assessment_id": ref_assessment_id,
            "risk_level_at_time": risk_level_at_time,
            "model_version": "LLM_v1.0",
            "created_at": consult_time
        })
        ai_id += 1

# ========== 5. 生成SQL文件 ==========
def generate_sql_insert(table_name, records, field_names):
    """生成SQL INSERT语句"""
    sql_lines = [f"-- {table_name} 表数据\n"]
    sql_lines.append(f"INSERT INTO {table_name} ({', '.join(field_names)}) VALUES\n")
    
    for i, record in enumerate(records):
        values = []
        for field in field_names:
            value = record.get(field)
            if value is None:
                values.append("NULL")
            elif isinstance(value, str):
                # 转义单引号
                escaped = value.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(value, (datetime, date)):
                values.append(f"'{value}'")
            elif isinstance(value, bool):
                values.append("1" if value else "0")
            else:
                values.append(str(value))
        
        sql_line = f"({', '.join(values)})"
        if i < len(records) - 1:
            sql_line += ","
        sql_lines.append(sql_line)
    
    sql_lines.append(";\n\n")
    return "\n".join(sql_lines)

# 生成所有SQL
sql_content = []
sql_content.append("-- ========================================\n")
sql_content.append("-- 3位老人的完整虚拟数据\n")
sql_content.append("-- 生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
sql_content.append("-- ========================================\n\n")

# elder_info
elder_info_records = []
for elder in ELDERS:
    elder_info_records.append({
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
        "created_at": datetime(2024, 1, 1, 9, 0, 0),
        "updated_at": datetime(2024, 1, 15, 10, 0, 0)
    })

sql_content.append(generate_sql_insert(
    "elder_info",
    elder_info_records,
    ["id", "name", "gender", "birthday", "age", "phone", "address", "height_cm", 
     "chronic_tags", "status", "remark", "created_at", "updated_at"]
))

# user_account
sql_content.append(generate_sql_insert(
    "user_account",
    user_accounts,
    ["id", "username", "password_hash", "role", "display_name", "phone", "email",
     "status", "last_login_at", "created_at", "updated_at"]
))

# elder_user_relation
sql_content.append(generate_sql_insert(
    "elder_user_relation",
    elder_user_relations,
    ["id", "elder_id", "user_id", "relation_type", "is_primary", "created_at"]
))

# health_record
sql_content.append(generate_sql_insert(
    "health_record",
    health_records,
    ["id", "elder_id", "tester_code", "check_time", "phone", "age",
     "spo2", "spo2_status", "heart_rate", "heart_rate_status",
     "diastolic_bp", "diastolic_bp_status", "systolic_bp", "systolic_bp_status",
     "pulse_rate", "pulse_rate_status", "blood_sugar", "blood_sugar_status",
     "uric_acid", "body_temperature", "health_risk_level", "potential_risk_note",
     "sleep_hours", "steps", "weight_kg", "data_source", "created_at", "updated_at"]
))

# assessment_result
sql_content.append(generate_sql_insert(
    "assessment_result",
    assessment_results,
    ["id", "elder_id", "assessment_time", "window_start_date", "window_end_date",
     "data_quality_flag", "data_quality_notes", "overall_risk_level", "overall_risk_score",
     "disease_overall_score", "lifestyle_risk_score", "trend_risk_score",
     "comorbidity_count", "main_diseases", "topsis_score",
     "ahp_weight_disease", "ahp_weight_lifestyle", "ahp_weight_trend",
     "disease_summary_json", "lifestyle_anomaly_score", "sleep_mean_hours", "steps_mean",
     "lifestyle_risk_factors", "trend_risk_flag", "trend_notes",
     "advice_level", "advice_text_elder", "advice_text_family",
     "key_risk_factors", "reason_summary", "reason_struct_json",
     "pipeline_version", "disease_model_version", "lifestyle_model_version",
     "trend_model_version", "fuse_strategy", "extra_meta_json", "created_at"]
))

# ai_consult_log
sql_content.append(generate_sql_insert(
    "ai_consult_log",
    ai_consult_logs,
    ["id", "elder_id", "user_id", "consult_time", "channel", "question", "answer",
     "ref_assessment_id", "risk_level_at_time", "model_version", "created_at"]
))

# 写入文件
with open("fake_data.sql", "w", encoding="utf-8") as f:
    f.write("".join(sql_content))

print("=" * 60)
print("数据生成完成！")
print("=" * 60)
print(f"老人信息 (elder_info): {len(elder_info_records)} 条")
print(f"用户账号 (user_account): {len(user_accounts)} 条")
print(f"关系表 (elder_user_relation): {len(elder_user_relations)} 条")
print(f"健康记录 (health_record): {len(health_records)} 条")
print(f"评估结果 (assessment_result): {len(assessment_results)} 条")
print(f"AI问诊 (ai_consult_log): {len(ai_consult_logs)} 条")
print("=" * 60)
print("\nSQL文件已保存为: fake_data.sql")
print("你可以直接在MySQL中执行这个SQL文件来导入数据。")




