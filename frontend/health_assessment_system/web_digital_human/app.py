"""
Web版3D数字人后端API
====================

提供聊天API接口和健康数据API，供前端调用
"""

import os
import sys
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据处理服务
from core.health_data_service import (
    HealthDataService, 
    RawHealthRecord,
    get_health_data_service
)


# =============================================================================
# 健康数据模拟器 - 生成动态模拟数据（后续可替换为真实数据库查询）
# =============================================================================

class HealthDataSimulator:
    """健康数据模拟器 - 生成逼真的健康数据"""
    
    # 用户基线数据（模拟不同用户的健康状况）
    USER_PROFILES = {
        'elderly_001': {
            'name': '张秀英',
            'age': 68,
            'base_hr': 72,          # 基础心率
            'base_sbp': 135,        # 基础收缩压
            'base_dbp': 82,         # 基础舒张压
            'base_glucose': 6.2,    # 基础血糖
            'base_weight': 62.5,    # 基础体重
            'height': 158,          # 身高(cm)
            'health_score': 78,     # 健康基准分
        },
        'default': {
            'name': '测试用户',
            'age': 65,
            'base_hr': 75,
            'base_sbp': 128,
            'base_dbp': 78,
            'base_glucose': 5.8,
            'base_weight': 65.0,
            'height': 165,
            'health_score': 82,
        }
    }
    
    @classmethod
    def get_profile(cls, user_id: str) -> dict:
        return cls.USER_PROFILES.get(user_id, cls.USER_PROFILES['default'])
    
    @classmethod
    def generate_today_health(cls, user_id: str) -> dict:
        """生成今日健康数据"""
        profile = cls.get_profile(user_id)
        
        # 添加随机波动
        hr = profile['base_hr'] + random.randint(-8, 12)
        sbp = profile['base_sbp'] + random.randint(-10, 15)
        dbp = profile['base_dbp'] + random.randint(-5, 8)
        glucose = round(profile['base_glucose'] + random.uniform(-0.5, 0.8), 1)
        temp = round(36.3 + random.uniform(-0.2, 0.4), 1)
        spo2 = random.randint(96, 99)
        steps = random.randint(3000, 8000)
        weight = round(profile['base_weight'] + random.uniform(-0.3, 0.3), 1)
        
        # 计算 BMI
        height_m = profile['height'] / 100
        bmi = round(weight / (height_m ** 2), 1)
        
        # 状态判断
        def get_bp_status(s, d):
            if s >= 140 or d >= 90: return '偏高'
            if s < 120 and d < 80: return '正常'
            return '正常偏高'
        
        def get_glucose_status(g):
            if g >= 7.0: return '偏高'
            if g < 6.1: return '正常'
            return '正常偏高'
        
        def get_bmi_status(b):
            if b < 18.5: return '偏瘦'
            if b < 24: return '正常'
            if b < 28: return '超重'
            return '肥胖'
        
        return {
            'userId': user_id,
            'userName': profile['name'],
            'vitalSigns': {
                'temperature': {
                    'value': temp,
                    'unit': '°C',
                    'change': round(random.uniform(-0.2, 0.2), 1),
                    'status': '正常' if 36.0 <= temp <= 37.3 else '异常'
                },
                'bloodSugar': {
                    'value': glucose,
                    'unit': 'mmol/L',
                    'status': get_glucose_status(glucose),
                    'testType': '空腹'
                },
                'bloodPressure': {
                    'systolic': sbp,
                    'diastolic': dbp,
                    'unit': 'mmHg',
                    'status': get_bp_status(sbp, dbp)
                },
                'heartRate': {
                    'value': hr,
                    'unit': 'bpm',
                    'change': random.randint(-5, 5),
                    'status': '正常' if 60 <= hr <= 100 else '异常'
                },
                'spo2': {
                    'value': spo2,
                    'unit': '%',
                    'status': '正常' if spo2 >= 95 else '偏低'
                }
            },
            'activity': {
                'steps': steps,
                'goal': 6000,
                'percentage': min(100, round(steps / 6000 * 100)),
                'distance': round(steps * 0.7 / 1000, 2),  # km
                'calories': round(steps * 0.04)  # kcal
            },
            'weight': {
                'value': weight,
                'unit': 'kg',
                'bmi': bmi,
                'bmiStatus': get_bmi_status(bmi)
            }
        }
    
    @classmethod
    def generate_heart_rate_data(cls, user_id: str, hours: int = 24) -> list:
        """生成心率历史数据"""
        profile = cls.get_profile(user_id)
        base = profile['base_hr']
        data = []
        
        now = datetime.now()
        for i in range(0, hours, 2):
            time_point = now - timedelta(hours=hours - i)
            hour = time_point.hour
            
            # 模拟日变化：凌晨低，白天高
            if 0 <= hour < 6:
                variation = random.randint(-10, -5)
            elif 6 <= hour < 12:
                variation = random.randint(0, 10)
            elif 12 <= hour < 18:
                variation = random.randint(5, 15)
            else:
                variation = random.randint(-5, 5)
            
            data.append({
                'time': time_point.strftime('%H:%M'),
                'value': base + variation
            })
        
        return data
    
    @classmethod
    def generate_sleep_data(cls, user_id: str, days: int = 7) -> list:
        """生成睡眠历史数据"""
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        
        today = datetime.now().weekday()
        for i in range(days):
            idx = (today - days + 1 + i) % 7
            deep = round(random.uniform(1.5, 3.5), 1)
            light = round(random.uniform(3.5, 5.5), 1)
            total = deep + light
            
            # 睡眠质量分数
            quality = min(100, max(40, int(
                (deep / total * 50) +  # 深睡比例
                (min(total, 8) / 8 * 30) +  # 总时长
                random.randint(10, 20)  # 随机因素
            )))
            
            data.append({
                'day': weekdays[idx],
                'deepSleep': deep,
                'lightSleep': light,
                'quality': quality
            })
        
        return data
    
    @classmethod
    def generate_blood_pressure_data(cls, user_id: str, days: int = 7) -> list:
        """生成血压历史数据"""
        profile = cls.get_profile(user_id)
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        
        today = datetime.now().weekday()
        for i in range(days):
            idx = (today - days + 1 + i) % 7
            sbp = profile['base_sbp'] + random.randint(-8, 12)
            dbp = profile['base_dbp'] + random.randint(-5, 8)
            
            data.append({
                'day': weekdays[idx],
                'systolic': sbp,
                'diastolic': dbp,
                'normalHigh': 120,
                'normalLow': 80
            })
        
        return data
    
    @classmethod
    def generate_radar_data(cls, user_id: str) -> list:
        """生成健康雷达图数据"""
        profile = cls.get_profile(user_id)
        base = profile['health_score']
        
        dimensions = [
            ('心血管', 8),
            ('睡眠质量', 10),
            ('运动量', 12),
            ('营养均衡', 6),
            ('心理健康', 5),
            ('体重管理', 8)
        ]
        
        data = []
        for name, variance in dimensions:
            score = min(100, max(50, base + random.randint(-variance, variance)))
            last_month = min(100, max(45, score + random.randint(-8, 5)))
            data.append({
                'subject': name,
                'score': score,
                'lastMonth': last_month,
                'fullMark': 100
            })
        
        return data
    
    @classmethod
    def generate_chart_data(cls, user_id: str, days: int = 7) -> dict:
        """生成所有图表数据"""
        return {
            'heartRate': cls.generate_heart_rate_data(user_id, 24),
            'sleep': cls.generate_sleep_data(user_id, days),
            'bloodPressure': cls.generate_blood_pressure_data(user_id, days),
            'healthRadar': cls.generate_radar_data(user_id)
        }
    
    @classmethod
    def generate_visualization_data(cls, user_id: str) -> dict:
        """生成可视化数据（用于健康评估）"""
        profile = cls.get_profile(user_id)
        base = profile['health_score']
        
        return {
            'overall_score': base + random.randint(-3, 5),
            'health_level': 'good' if base >= 75 else 'suboptimal',
            'dimension_scores': {
                '慢病风险': base + random.randint(-5, 8),
                '生活方式': base + random.randint(-8, 5),
                '趋势分析': base + random.randint(-3, 10)
            },
            'top_risks': [
                '血压偏高需关注',
                '运动量不足',
                '睡眠质量待改善'
            ] if base < 80 else [],
            'recommendations': [
                '建议每天步行6000步以上',
                '保持低盐低脂饮食',
                '保证7-8小时充足睡眠',
                '按时服药，定期测量血压'
            ]
        }

app = Flask(__name__, static_folder='static')
CORS(app)

# 智能体系统
agent_system = None

def get_agent():
    global agent_system
    if agent_system is None:
        try:
            from agents.multi_agent_system import MultiAgentSystem
            agent_system = MultiAgentSystem(user_id="web_user", enable_assessment=False)
            print("✓ 多智能体系统初始化完成")
        except Exception as e:
            print(f"智能体初始化失败: {e}")
    return agent_system


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/models/<path:filename>')
def serve_model(filename):
    """提供VRM模型文件"""
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'little shark')
    return send_from_directory(models_dir, filename)


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    agent = get_agent()
    if agent:
        try:
            response = agent.chat(message)
            return jsonify({
                'response': response,
                'emotion': 'happy'  # 可以根据内容分析情绪
            })
        except Exception as e:
            return jsonify({'response': f'抱歉，出现了问题：{str(e)}', 'emotion': 'neutral'})
    else:
        return jsonify({'response': '系统正在初始化，请稍后再试', 'emotion': 'neutral'})


@app.route('/api/greeting', methods=['GET'])
def greeting():
    """获取问候语"""
    agent = get_agent()
    if agent:
        return jsonify({'message': agent.get_greeting()})
    return jsonify({'message': '你好！我是小康，很高兴见到你！'})


# =============================================================================
# 健康数据 API - 供前端图表和仪表盘调用
# =============================================================================

@app.route('/api/health/today', methods=['GET'])
def get_today_health():
    """获取今日健康数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    try:
        data = HealthDataSimulator.generate_today_health(user_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/charts', methods=['GET'])
def get_chart_data():
    """获取所有图表数据（心率、睡眠、血压、雷达图）"""
    user_id = request.args.get('user_id', 'elderly_001')
    days = request.args.get('days', 7, type=int)
    try:
        data = HealthDataSimulator.generate_chart_data(user_id, days)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/heart-rate', methods=['GET'])
def get_heart_rate():
    """获取心率历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    hours = request.args.get('hours', 24, type=int)
    try:
        data = HealthDataSimulator.generate_heart_rate_data(user_id, hours)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/sleep', methods=['GET'])
def get_sleep_data():
    """获取睡眠历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    days = request.args.get('days', 7, type=int)
    try:
        data = HealthDataSimulator.generate_sleep_data(user_id, days)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/blood-pressure', methods=['GET'])
def get_blood_pressure():
    """获取血压历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    days = request.args.get('days', 7, type=int)
    try:
        data = HealthDataSimulator.generate_blood_pressure_data(user_id, days)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/radar', methods=['GET'])
def get_radar_data():
    """获取健康雷达图数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    try:
        data = HealthDataSimulator.generate_radar_data(user_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/visualization', methods=['GET', 'OPTIONS'])
def get_visualization():
    """获取健康评估可视化数据"""
    if request.method == 'OPTIONS':
        return jsonify({'success': True})
    
    user_id = request.args.get('user_id', 'elderly_001')
    try:
        data = HealthDataSimulator.generate_visualization_data(user_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health/assessment', methods=['POST'])
def run_assessment():
    """运行健康评估（调用评估引擎）"""
    data = request.json or {}
    user_id = data.get('user_id', 'elderly_001')
    
    try:
        # 尝试使用真实评估引擎
        from core.assessment_engine import HealthAssessmentEngine
        from modules.assessment_config import AssessmentPeriod, TimeWindow
        
        engine = HealthAssessmentEngine()
        result = engine.run_scheduled_assessment(
            user_id=user_id,
            period=AssessmentPeriod.ON_DEMAND,
            time_window=TimeWindow.LAST_7_DAYS
        )
        
        return jsonify({
            'success': True,
            'data': {
                'assessment_id': result.assessment_id,
                'overall_score': result.overall_score,
                'health_level': result.health_level.value,
                'dimension_scores': result.dimension_scores,
                'top_risks': result.top_risks[:5] if result.top_risks else [],
                'recommendations': result.recommendations[:5] if result.recommendations else []
            }
        })
    except Exception as e:
        # 降级使用模拟数据
        print(f"评估引擎调用失败，使用模拟数据: {e}")
        data = HealthDataSimulator.generate_visualization_data(user_id)
        return jsonify({
            'success': True,
            'data': data,
            'note': '使用模拟数据'
        })


# =============================================================================
# 真实数据处理 API - 数据输入、清洗、分析
# =============================================================================

@app.route('/api/data/input', methods=['POST'])
def input_health_data():
    """
    输入健康数据（真实数据入口）
    
    请求体:
    {
        "user_id": "elderly_001",
        "data_type": "blood_pressure",  // blood_pressure, glucose, heart_rate, sleep, steps, weight
        "values": {"systolic": 135, "diastolic": 85},
        "timestamp": "2024-01-01T10:00:00",  // 可选，默认当前时间
        "source": "manual"  // manual, sensor, device
    }
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400
    
    user_id = data.get('user_id')
    data_type = data.get('data_type')
    values = data.get('values')
    
    if not all([user_id, data_type, values]):
        return jsonify({
            'success': False, 
            'error': '缺少必要字段: user_id, data_type, values'
        }), 400
    
    try:
        service = get_health_data_service()
        
        # 创建记录
        record = RawHealthRecord(
            user_id=user_id,
            timestamp=data.get('timestamp', datetime.now()),
            data_type=data_type,
            values=values,
            source=data.get('source', 'api')
        )
        
        # 添加数据
        success = service.add_raw_data(record)
        
        return jsonify({
            'success': success,
            'message': '数据已添加' if success else '添加失败',
            'data': {
                'user_id': user_id,
                'data_type': data_type,
                'timestamp': record.timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/batch', methods=['POST'])
def batch_input_data():
    """
    批量输入健康数据
    
    请求体:
    {
        "user_id": "elderly_001",
        "records": [
            {"data_type": "blood_pressure", "values": {"systolic": 135, "diastolic": 85}, "timestamp": "..."},
            {"data_type": "glucose", "values": {"value": 6.2}, "timestamp": "..."}
        ]
    }
    """
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400
    
    user_id = data.get('user_id')
    records = data.get('records', [])
    
    if not user_id or not records:
        return jsonify({'success': False, 'error': '缺少 user_id 或 records'}), 400
    
    try:
        service = get_health_data_service()
        success_count = 0
        
        for record_data in records:
            record = RawHealthRecord(
                user_id=user_id,
                timestamp=record_data.get('timestamp', datetime.now()),
                data_type=record_data.get('data_type'),
                values=record_data.get('values', {}),
                source=record_data.get('source', 'batch_api')
            )
            if service.add_raw_data(record):
                success_count += 1
        
        return jsonify({
            'success': True,
            'message': f'成功添加 {success_count}/{len(records)} 条记录',
            'data': {
                'total': len(records),
                'success': success_count,
                'failed': len(records) - success_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/clean', methods=['POST'])
def clean_user_data():
    """
    清洗用户数据（去除异常值）
    
    请求体:
    {
        "user_id": "elderly_001",
        "data_type": "blood_pressure",  // 可选，不指定则清洗所有类型
        "days": 30,
        "method": "iqr"  // iqr 或 zscore
    }
    """
    data = request.json or {}
    user_id = data.get('user_id', 'elderly_001')
    data_type = data.get('data_type')
    days = data.get('days', 30)
    method = data.get('method', 'iqr')
    
    try:
        service = get_health_data_service()
        service.outlier_method = method
        
        results = {}
        data_types = [data_type] if data_type else [
            'blood_pressure', 'glucose', 'heart_rate', 'sleep', 'steps', 'weight'
        ]
        
        for dtype in data_types:
            cleaned = service.clean_data(user_id, dtype, days)
            if cleaned:
                results[dtype] = {
                    'data_points': len(cleaned.values),
                    'outliers_removed': cleaned.outliers_removed,
                    'quality_score': cleaned.quality_score,
                    'method': cleaned.cleaning_method
                }
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'days': days,
                'cleaning_results': results
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/analyze', methods=['POST'])
def analyze_user_data():
    """
    分析用户健康数据（特征工程 + 健康评估）
    
    请求体:
    {
        "user_id": "elderly_001",
        "days": 7
    }
    
    返回完整的数据分析结果，包括：
    - 各指标特征（均值、标准差、趋势等）
    - 各维度健康评估（血压、血糖、心率、睡眠、运动）
    - 综合健康评分和等级
    """
    data = request.json or {}
    user_id = data.get('user_id', 'elderly_001')
    days = data.get('days', 7)
    
    try:
        service = get_health_data_service()
        
        # 构建特征并评估
        result = service.build_features(user_id, days)
        
        if result:
            return jsonify({
                'success': True,
                'data': result.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': '没有足够的数据进行分析',
                'hint': '请先通过 /api/data/input 添加健康数据'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/summary', methods=['GET'])
def get_data_summary():
    """获取用户数据摘要"""
    user_id = request.args.get('user_id', 'elderly_001')
    
    try:
        service = get_health_data_service()
        summary = service.get_user_data_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/init-demo', methods=['POST'])
def init_demo_data():
    """
    初始化演示数据（用于测试）
    
    生成30天的模拟健康数据，包含一些异常值用于测试清洗功能
    """
    data = request.json or {}
    user_id = data.get('user_id', 'demo_user')
    days = data.get('days', 30)
    
    try:
        service = get_health_data_service()
        count = 0
        
        for i in range(days):
            day = datetime.now() - timedelta(days=days-1-i)
            
            # 血压数据
            service.add_raw_data(RawHealthRecord(
                user_id=user_id,
                timestamp=day,
                data_type="blood_pressure",
                values={
                    "systolic": 130 + random.randint(-15, 20),
                    "diastolic": 80 + random.randint(-8, 12)
                },
                source="demo"
            ))
            count += 1
            
            # 血糖数据
            service.add_raw_data(RawHealthRecord(
                user_id=user_id,
                timestamp=day,
                data_type="glucose",
                values={"value": round(5.8 + random.uniform(-0.5, 1.2), 1)},
                source="demo"
            ))
            count += 1
            
            # 心率数据
            service.add_raw_data(RawHealthRecord(
                user_id=user_id,
                timestamp=day,
                data_type="heart_rate",
                values={"value": 72 + random.randint(-10, 15)},
                source="demo"
            ))
            count += 1
            
            # 睡眠数据
            service.add_raw_data(RawHealthRecord(
                user_id=user_id,
                timestamp=day,
                data_type="sleep",
                values={"duration": round(6.5 + random.uniform(-1, 1.5), 1)},
                source="demo"
            ))
            count += 1
            
            # 步数数据
            service.add_raw_data(RawHealthRecord(
                user_id=user_id,
                timestamp=day,
                data_type="steps",
                values={"value": random.randint(4000, 10000)},
                source="demo"
            ))
            count += 1
        
        # 添加异常值用于测试清洗
        service.add_raw_data(RawHealthRecord(
            user_id=user_id,
            timestamp=datetime.now() - timedelta(days=5),
            data_type="blood_pressure",
            values={"systolic": 250, "diastolic": 150},  # 异常值
            source="demo_outlier"
        ))
        count += 1
        
        return jsonify({
            'success': True,
            'message': f'已为用户 {user_id} 生成 {count} 条演示数据（含异常值）',
            'data': {
                'user_id': user_id,
                'days': days,
                'records_created': count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 55)
    print("  🌐 Web 3D数字人服务器")
    print("=" * 55)
    print()
    print("  访问: http://localhost:5000")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
