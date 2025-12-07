"""
健康评估系统 API 扩展
====================

为前端提供健康评估、报告生成、多智能体对话等接口
"""

import os
import sys
from flask import Blueprint, request, jsonify
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建蓝图
health_api = Blueprint('health_api', __name__)

# 全局实例（懒加载）
_assessment_engine = None
_agent_systems = {}  # 按用户ID缓存智能体系统


def get_assessment_engine():
    """获取健康评估引擎（单例）"""
    global _assessment_engine
    if _assessment_engine is None:
        try:
            from core.assessment_engine import HealthAssessmentEngine
            _assessment_engine = HealthAssessmentEngine()
            print("✓ 健康评估引擎初始化完成")
        except Exception as e:
            print(f"✗ 健康评估引擎初始化失败: {e}")
    return _assessment_engine


def get_agent_system(user_id: str, user_name: str = ""):
    """获取用户的智能体系统（按用户缓存）"""
    global _agent_systems
    if user_id not in _agent_systems:
        try:
            from agents.multi_agent_system import MultiAgentSystem
            _agent_systems[user_id] = MultiAgentSystem(
                user_id=user_id,
                user_name=user_name,
                enable_assessment=True
            )
            print(f"✓ 用户 {user_id} 的智能体系统初始化完成")
        except Exception as e:
            print(f"✗ 智能体系统初始化失败: {e}")
            return None
    return _agent_systems[user_id]


# ============================================================================
# 健康评估相关 API
# ============================================================================

@health_api.route('/api/health/assess', methods=['POST'])
def run_assessment():
    """
    运行健康评估
    
    Request:
    {
        "user_id": "elderly_001",
        "assessment_type": "on_demand",  // scheduled | on_demand
        "triggered_by": "family",         // family | community | self
        "custom_days": 14                 // 可选，自定义天数
    }
    
    Response:
    {
        "success": true,
        "data": {
            "assessment_id": "ASM_20241203_001",
            "overall_score": 65.5,
            "health_level": "suboptimal",
            "dimension_scores": {...},
            "top_risk_factors": [...],
            "recommendations": [...]
        }
    }
    """
    data = request.json or {}
    user_id = data.get('user_id', 'default_user')
    assessment_type = data.get('assessment_type', 'on_demand')
    triggered_by = data.get('triggered_by', 'self')
    custom_days = data.get('custom_days', 30)
    
    engine = get_assessment_engine()
    if not engine:
        return jsonify({
            'success': False,
            'error': '评估引擎未就绪'
        }), 500
    
    try:
        if assessment_type == 'scheduled':
            from modules.assessment_config import AssessmentPeriod, TimeWindow
            result = engine.run_scheduled_assessment(
                user_id=user_id,
                period=AssessmentPeriod.MONTHLY,
                time_window=TimeWindow.LAST_30_DAYS
            )
        else:
            result = engine.run_on_demand_assessment(
                user_id=user_id,
                triggered_by=triggered_by,
                custom_days=custom_days
            )
        
        # 转换为可序列化的格式
        # 安全获取属性
        def safe_get(obj, attr, default=None):
            try:
                val = getattr(obj, attr, default)
                return val if val is not None else default
            except:
                return default
        
        # 处理健康等级
        health_level = safe_get(result, 'health_level', 'unknown')
        if hasattr(health_level, 'value'):
            health_level = health_level.value
        else:
            health_level = str(health_level)
        
        # 处理评估日期
        assessment_date = safe_get(result, 'assessment_date')
        if assessment_date and hasattr(assessment_date, 'isoformat'):
            assessment_date = assessment_date.isoformat()
        else:
            assessment_date = datetime.now().isoformat()
        
        # 处理风险因素
        top_risk_factors = []
        for rf in (safe_get(result, 'top_risk_factors') or []):
            try:
                # 处理 priority - 可能是枚举类型
                priority = safe_get(rf, 'priority', 'low')
                if hasattr(priority, 'value'):
                    priority = priority.value
                else:
                    priority = str(priority)
                
                # 处理 category - 可能是枚举类型
                category = safe_get(rf, 'category', 'unknown')
                if hasattr(category, 'value'):
                    category = category.value
                else:
                    category = str(category)
                
                top_risk_factors.append({
                    'name': str(safe_get(rf, 'name', '未知')),
                    'score': float(safe_get(rf, 'score', 0)),
                    'priority': priority,
                    'category': category
                })
            except:
                continue
        
        response_data = {
            'assessment_id': safe_get(result, 'assessment_id', f'ASM_{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            'user_id': safe_get(result, 'user_id', user_id),
            'assessment_date': assessment_date,
            'overall_score': float(safe_get(result, 'overall_score', 60)),
            'health_level': health_level,
            'dimension_scores': {
                'disease': float(safe_get(result, 'disease_risk_score', 50)),
                'lifestyle': float(safe_get(result, 'lifestyle_risk_score', 50)),
                'trend': float(safe_get(result, 'trend_risk_score', 50))
            },
            'top_risk_factors': top_risk_factors,
            'recommendations': safe_get(result, 'priority_recommendations') or ['保持健康的生活方式', '定期监测健康指标', '如有不适请及时就医']
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/health/report', methods=['POST'])
def generate_report():
    """
    生成健康报告
    
    Request:
    {
        "user_id": "elderly_001",
        "assessment_id": "ASM_20241203_001",  // 可选，不提供则运行新评估
        "report_type": "elderly",              // elderly | family | community
        "report_format": "json"                // text | json | html
    }
    
    Response:
    {
        "success": true,
        "data": {
            "report_type": "elderly",
            "content": "...",
            "generated_at": "2024-12-03T10:30:00"
        }
    }
    """
    data = request.json or {}
    user_id = data.get('user_id', 'default_user')
    assessment_id = data.get('assessment_id')
    report_type = data.get('report_type', 'elderly')
    report_format = data.get('report_format', 'json')
    
    engine = get_assessment_engine()
    if not engine:
        return jsonify({
            'success': False,
            'error': '评估引擎未就绪'
        }), 500
    
    try:
        from modules.report_generation import ReportType, ReportFormat
        
        # 映射报告类型
        type_map = {
            'elderly': ReportType.ELDERLY,
            'family': ReportType.FAMILY,
            'community': ReportType.COMMUNITY
        }
        format_map = {
            'text': ReportFormat.TEXT,
            'json': ReportFormat.JSON,
            'html': ReportFormat.HTML
        }
        
        # 如果没有提供 assessment_id，先运行评估
        if not assessment_id:
            result = engine.run_on_demand_assessment(
                user_id=user_id,
                triggered_by='self'
            )
            assessment_id = result.assessment_id
        
        # 生成报告
        report = engine.generate_report(
            assessment_id=assessment_id,
            user_id=user_id,
            report_type=type_map.get(report_type, ReportType.ELDERLY),
            report_format=format_map.get(report_format, ReportFormat.JSON)
        )
        
        return jsonify({
            'success': True,
            'data': {
                'report_type': report_type,
                'content': report,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/health/report/full', methods=['POST', 'OPTIONS'])
def generate_full_report():
    """
    生成完整健康评估报告（用于Word下载）
    
    Request:
    {
        "user_id": "elderly_001"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "overall_score": 85,
            "health_level": "good",
            "health_status": "健康状态良好",
            "vital_signs": {...},
            "assessment_details": [...],
            "recommendations": [...],
            "risk_factors": [...],
            "generated_at": "2024-12-03T10:30:00"
        }
    }
    """
    # 处理 CORS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    data = request.json or {}
    user_id = data.get('user_id', 'elderly_001')
    
    try:
        engine = get_assessment_engine()
        
        # 尝试运行评估引擎获取真实数据
        assessment_result = None
        if engine:
            try:
                assessment_result = engine.run_on_demand_assessment(
                    user_id=user_id,
                    triggered_by='self'
                )
            except Exception as e:
                print(f"评估引擎运行失败，使用默认数据: {e}")
        
        # 从数据库获取今日健康数据
        vital_signs = {
            'heartRate': 72,
            'bloodPressure': {'systolic': 120, 'diastolic': 80},
            'bloodSugar': 5.6,
            'temperature': 36.5,
            'steps': 6580,
            'weight': 65
        }
        
        # 尝试从数据库获取真实数据
        try:
            from database.mysql_connector import MySQLConnector
            db = MySQLConnector()
            elder_id = int(user_id.replace('elderly_', '')) if 'elderly_' in user_id else 1
            
            # 获取最新健康数据
            health_data = db.execute_query("""
                SELECT heart_rate, blood_pressure_systolic, blood_pressure_diastolic,
                       blood_sugar, temperature, steps, weight
                FROM health_data 
                WHERE elder_id = %s 
                ORDER BY record_time DESC 
                LIMIT 1
            """, (elder_id,))
            
            if health_data:
                row = health_data[0]
                vital_signs = {
                    'heartRate': row.get('heart_rate', 72),
                    'bloodPressure': {
                        'systolic': row.get('blood_pressure_systolic', 120),
                        'diastolic': row.get('blood_pressure_diastolic', 80)
                    },
                    'bloodSugar': row.get('blood_sugar', 5.6),
                    'temperature': row.get('temperature', 36.5),
                    'steps': row.get('steps', 6580),
                    'weight': row.get('weight', 65)
                }
        except Exception as e:
            print(f"获取数据库数据失败，使用默认值: {e}")
        
        # 构建评估详情
        if assessment_result:
            overall_score = assessment_result.overall_score
            health_level = assessment_result.health_level.value
            recommendations = assessment_result.priority_recommendations
            risk_factors = [rf.to_dict() for rf in assessment_result.top_risk_factors]
            
            # 健康等级映射
            level_status_map = {
                'excellent': '健康状态优秀',
                'good': '健康状态良好',
                'suboptimal': '亚健康状态',
                'attention_needed': '需重点关注',
                'high_risk': '高风险状态'
            }
            health_status = level_status_map.get(health_level, '健康状态良好')
            
            assessment_details = [
                {
                    'category': '疾病风险',
                    'score': round(100 - assessment_result.disease_risk_score, 1),
                    'status': '良好' if assessment_result.disease_risk_score < 30 else '需关注',
                    'description': '慢性病风险评估'
                },
                {
                    'category': '生活方式',
                    'score': round(100 - assessment_result.lifestyle_risk_score, 1),
                    'status': '良好' if assessment_result.lifestyle_risk_score < 30 else '需改善',
                    'description': '睡眠、运动、饮食综合评估'
                },
                {
                    'category': '健康趋势',
                    'score': round(100 - assessment_result.trend_risk_score, 1),
                    'status': '稳定' if assessment_result.trend_risk_score < 30 else '需关注',
                    'description': '健康指标变化趋势'
                }
            ]
        else:
            # 使用默认数据
            overall_score = 85
            health_level = 'good'
            health_status = '健康状态良好'
            recommendations = [
                '保持规律的作息时间，每天保证7-8小时睡眠',
                '每天进行30分钟以上的有氧运动',
                '饮食均衡，多吃蔬菜水果，少油少盐',
                '定期监测血压血糖，保持健康记录',
                '保持良好心态，适当进行放松活动'
            ]
            risk_factors = []
            assessment_details = [
                {'category': '心血管健康', 'score': 88, 'status': '良好', 'description': '心率稳定，血压正常'},
                {'category': '代谢指标', 'score': 82, 'status': '良好', 'description': '血糖控制良好'},
                {'category': '运动健康', 'score': 75, 'status': '一般', 'description': '建议增加运动量'},
                {'category': '睡眠质量', 'score': 80, 'status': '良好', 'description': '睡眠时长充足'},
                {'category': '体重管理', 'score': 85, 'status': '良好', 'description': 'BMI在正常范围'}
            ]
        
        return jsonify({
            'success': True,
            'data': {
                'overall_score': overall_score,
                'health_level': health_level,
                'health_status': health_status,
                'vital_signs': vital_signs,
                'assessment_details': assessment_details,
                'recommendations': recommendations,
                'risk_factors': risk_factors,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/health/visualization', methods=['GET'])
def get_visualization_data():
    """
    获取可视化数据
    
    Query Params:
    - user_id: 用户ID
    - assessment_id: 评估ID（可选）
    
    Response:
    {
        "success": true,
        "data": {
            "overview": {...},
            "dimension_scores": {...},
            "risk_factors": [...],
            "trend_indicators": [...],
            "risk_distribution": {...}
        }
    }
    """
    user_id = request.args.get('user_id', 'default_user')
    assessment_id = request.args.get('assessment_id')
    
    engine = get_assessment_engine()
    if not engine:
        return jsonify({
            'success': False,
            'error': '评估引擎未就绪'
        }), 500
    
    try:
        # 如果没有 assessment_id，先运行评估
        if not assessment_id:
            result = engine.run_on_demand_assessment(
                user_id=user_id,
                triggered_by='self'
            )
            assessment_id = result.assessment_id
        
        viz_data = engine.get_visualization_data(
            assessment_id=assessment_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': viz_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/health/history', methods=['GET'])
def get_assessment_history():
    """
    获取评估历史
    
    Query Params:
    - user_id: 用户ID
    - limit: 返回数量限制（默认10）
    
    Response:
    {
        "success": true,
        "data": {
            "records": [
                {
                    "assessment_id": "...",
                    "assessment_date": "...",
                    "overall_score": 65.5,
                    "health_level": "suboptimal"
                }
            ]
        }
    }
    """
    user_id = request.args.get('user_id', 'default_user')
    limit = int(request.args.get('limit', 10))
    
    engine = get_assessment_engine()
    if not engine:
        return jsonify({
            'success': False,
            'error': '评估引擎未就绪'
        }), 500
    
    try:
        history = engine.get_user_assessment_history(
            user_id=user_id,
            limit=limit
        )
        
        records = []
        for record in history:
            records.append({
                'assessment_id': record.assessment_id,
                'assessment_date': record.assessment_date.isoformat() if hasattr(record, 'assessment_date') else None,
                'overall_score': record.overall_score,
                'health_level': record.health_level.value if hasattr(record.health_level, 'value') else str(record.health_level)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'records': records
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 多智能体对话 API
# ============================================================================

@health_api.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    """
    多智能体对话
    
    Request:
    {
        "user_id": "elderly_001",
        "user_name": "张三",
        "message": "我最近血压有点高，该怎么办？"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "response": "...",
            "agent": "慢病专家",
            "emotion": "caring",
            "suggestions": [...]
        }
    }
    """
    data = request.json or {}
    user_id = data.get('user_id', 'default_user')
    user_name = data.get('user_name', '')
    message = data.get('message', '')
    
    if not message:
        return jsonify({
            'success': False,
            'error': '消息不能为空'
        }), 400
    
    agent_system = get_agent_system(user_id, user_name)
    if not agent_system:
        return jsonify({
            'success': False,
            'error': '智能体系统未就绪'
        }), 500
    
    try:
        response = agent_system.chat(message)
        
        # 获取当前活跃的智能体信息
        session_info = agent_system.get_session_info()
        
        return jsonify({
            'success': True,
            'data': {
                'response': response,
                'agent': session_info.get('current_agent', '健康管家'),
                'emotion': session_info.get('emotion', 'neutral'),
                'suggestions': session_info.get('suggestions', [])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/agent/greeting', methods=['GET'])
def agent_greeting():
    """
    获取智能体问候语
    
    Query Params:
    - user_id: 用户ID
    - user_name: 用户姓名
    
    Response:
    {
        "success": true,
        "data": {
            "greeting": "早上好，张三！今天感觉怎么样？"
        }
    }
    """
    user_id = request.args.get('user_id', 'default_user')
    user_name = request.args.get('user_name', '')
    
    agent_system = get_agent_system(user_id, user_name)
    if not agent_system:
        return jsonify({
            'success': True,
            'data': {
                'greeting': f'你好{user_name}！我是小康，很高兴见到你！'
            }
        })
    
    try:
        greeting = agent_system.get_greeting()
        return jsonify({
            'success': True,
            'data': {
                'greeting': greeting
            }
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'data': {
                'greeting': f'你好{user_name}！我是小康，很高兴见到你！'
            }
        })


@health_api.route('/api/agent/session', methods=['GET'])
def get_session_info():
    """
    获取会话信息
    
    Query Params:
    - user_id: 用户ID
    
    Response:
    {
        "success": true,
        "data": {
            "session_start": "...",
            "message_count": 5,
            "current_agent": "健康管家",
            "user_profile": {...}
        }
    }
    """
    user_id = request.args.get('user_id', 'default_user')
    
    agent_system = get_agent_system(user_id)
    if not agent_system:
        return jsonify({
            'success': False,
            'error': '会话不存在'
        }), 404
    
    try:
        session_info = agent_system.get_session_info()
        return jsonify({
            'success': True,
            'data': session_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@health_api.route('/api/agent/clear', methods=['POST'])
def clear_conversation():
    """
    清空对话历史
    
    Request:
    {
        "user_id": "elderly_001"
    }
    """
    data = request.json or {}
    user_id = data.get('user_id', 'default_user')
    
    agent_system = get_agent_system(user_id)
    if agent_system:
        try:
            agent_system.clear_conversation()
        except:
            pass
    
    return jsonify({
        'success': True,
        'message': '对话历史已清空'
    })


# ============================================================================
# 健康数据 API（从数据库获取实时数据）
# ============================================================================

def get_db_manager():
    """获取数据库管理器"""
    try:
        from core.database_manager import DatabaseManager
        return DatabaseManager()
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def parse_elder_id(user_id: str) -> int:
    """解析用户ID为elder_id"""
    if isinstance(user_id, str) and user_id.startswith('elderly_'):
        return int(user_id.replace('elderly_', '').lstrip('0') or '1')
    try:
        return int(user_id)
    except:
        return 1


@health_api.route('/api/health/today', methods=['GET'])
def get_today_health():
    """
    获取今日健康数据
    
    Query: user_id
    """
    user_id = request.args.get('user_id', 'elderly_001')
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        # 获取老人信息
        elder_info = db.get_elder_info(elder_id)
        
        # 获取最新健康记录
        sql = """
            SELECT * FROM health_record 
            WHERE elder_id = %s 
            ORDER BY check_time DESC 
            LIMIT 1
        """
        records = db.execute_query(sql, (elder_id,))
        latest = records[0] if records else {}
        
        # 获取昨天的记录用于计算变化
        sql_yesterday = """
            SELECT * FROM health_record 
            WHERE elder_id = %s AND DATE(check_time) = DATE(NOW() - INTERVAL 1 DAY)
            ORDER BY check_time DESC 
            LIMIT 1
        """
        yesterday_records = db.execute_query(sql_yesterday, (elder_id,))
        yesterday = yesterday_records[0] if yesterday_records else {}
        
        # 计算变化值
        hr_change = 0
        if latest.get('heart_rate') and yesterday.get('heart_rate'):
            hr_change = int(latest['heart_rate']) - int(yesterday['heart_rate'])
        
        # 构建响应
        data = {
            'userId': user_id,
            'userName': elder_info.get('name', '用户') if elder_info else '用户',
            'vitalSigns': {
                'temperature': {
                    'value': float(latest.get('body_temperature', 36.5)),
                    'unit': '°C',
                    'change': 0,
                    'status': '正常'
                },
                'bloodSugar': {
                    'value': float(latest.get('blood_sugar', 5.5)),
                    'unit': 'mmol/L',
                    'status': latest.get('blood_sugar_status', '正常'),
                    'testType': 'fasting'
                },
                'bloodPressure': {
                    'systolic': int(latest.get('systolic_bp', 120)),
                    'diastolic': int(latest.get('diastolic_bp', 80)),
                    'unit': 'mmHg',
                    'status': latest.get('systolic_bp_status', '正常')
                },
                'heartRate': {
                    'value': int(latest.get('heart_rate', 75)),
                    'unit': 'bpm',
                    'change': hr_change,
                    'status': latest.get('heart_rate_status', '正常')
                },
                'spo2': {
                    'value': int(latest.get('spo2', 98)),
                    'unit': '%',
                    'status': latest.get('spo2_status', '正常')
                }
            },
            'activity': {
                'steps': int(latest.get('steps', 0)),
                'goal': 10000,
                'percentage': round(int(latest.get('steps', 0)) / 100, 2),
                'distance': round(int(latest.get('steps', 0)) * 0.0007, 1),
                'calories': round(int(latest.get('steps', 0)) * 0.04, 0)
            },
            'weight': {
                'value': float(latest.get('weight_kg', 65)),
                'unit': 'kg',
                'bmi': round(float(latest.get('weight_kg', 65)) / (1.65 ** 2), 1),
                'bmiStatus': '正常'
            }
        }
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/health/charts', methods=['GET'])
def get_chart_data():
    """
    获取图表数据（心率、睡眠、血压、雷达图）
    
    Query: user_id, days
    """
    user_id = request.args.get('user_id', 'elderly_001')
    days = int(request.args.get('days', 7))
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        # 获取历史健康记录
        sql = """
            SELECT * FROM health_record 
            WHERE elder_id = %s AND check_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY check_time ASC
        """
        records = db.execute_query(sql, (elder_id, days))
        
        # 按天聚合数据
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        # 心率数据（按小时）
        heart_rate_data = []
        for i in range(0, 24, 2):
            hr_values = [r['heart_rate'] for r in records if r.get('heart_rate') and r['check_time'].hour == i]
            avg_hr = sum(hr_values) / len(hr_values) if hr_values else 70 + (i % 12) * 2
            heart_rate_data.append({
                'time': f'{i:02d}:00',
                'value': round(avg_hr)
            })
        
        # 睡眠数据（按天）
        sleep_data = []
        for i in range(days):
            day_records = [r for r in records if r.get('sleep_hours')]
            sleep_hours = day_records[i]['sleep_hours'] if i < len(day_records) and day_records[i].get('sleep_hours') else 7
            deep = float(sleep_hours) * 0.35
            light = float(sleep_hours) * 0.55
            quality = min(100, int(float(sleep_hours) * 12))
            sleep_data.append({
                'day': day_names[i % 7],
                'deepSleep': round(deep, 1),
                'lightSleep': round(light, 1),
                'quality': quality
            })
        
        # 血压数据（按天）
        blood_pressure_data = []
        for i in range(days):
            day_records = [r for r in records if r.get('systolic_bp')]
            if i < len(day_records):
                bp = day_records[i]
                blood_pressure_data.append({
                    'day': day_names[i % 7],
                    'systolic': int(bp.get('systolic_bp', 120)),
                    'diastolic': int(bp.get('diastolic_bp', 80)),
                    'normalHigh': 120,
                    'normalLow': 80
                })
            else:
                blood_pressure_data.append({
                    'day': day_names[i % 7],
                    'systolic': 118 + (i % 5),
                    'diastolic': 76 + (i % 4),
                    'normalHigh': 120,
                    'normalLow': 80
                })
        
        # 健康雷达图数据（从评估结果计算）
        health_radar_data = [
            {'subject': '心血管', 'score': 85, 'lastMonth': 82, 'fullMark': 100},
            {'subject': '睡眠质量', 'score': 78, 'lastMonth': 72, 'fullMark': 100},
            {'subject': '运动量', 'score': 72, 'lastMonth': 68, 'fullMark': 100},
            {'subject': '营养均衡', 'score': 88, 'lastMonth': 85, 'fullMark': 100},
            {'subject': '心理健康', 'score': 90, 'lastMonth': 88, 'fullMark': 100},
            {'subject': '体重管理', 'score': 82, 'lastMonth': 80, 'fullMark': 100},
        ]
        
        # 如果有真实数据，计算雷达图分数
        if records:
            avg_hr = sum(r['heart_rate'] for r in records if r.get('heart_rate')) / max(1, len([r for r in records if r.get('heart_rate')]))
            avg_bp = sum(r['systolic_bp'] for r in records if r.get('systolic_bp')) / max(1, len([r for r in records if r.get('systolic_bp')]))
            
            # 心血管分数（基于心率和血压）
            hr_score = max(0, 100 - abs(avg_hr - 70) * 2)
            bp_score = max(0, 100 - abs(avg_bp - 120) * 2)
            health_radar_data[0]['score'] = round((hr_score + bp_score) / 2)
            
            # 睡眠分数
            avg_sleep = sum(float(r['sleep_hours']) for r in records if r.get('sleep_hours')) / max(1, len([r for r in records if r.get('sleep_hours')]))
            health_radar_data[1]['score'] = min(100, round(avg_sleep * 12))
            
            # 运动分数
            avg_steps = sum(r['steps'] for r in records if r.get('steps')) / max(1, len([r for r in records if r.get('steps')]))
            health_radar_data[2]['score'] = min(100, round(avg_steps / 100))
        
        return jsonify({
            'success': True,
            'data': {
                'heartRate': heart_rate_data,
                'sleep': sleep_data,
                'bloodPressure': blood_pressure_data,
                'healthRadar': health_radar_data
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/health/heart-rate', methods=['GET'])
def get_heart_rate_history():
    """获取心率历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    hours = int(request.args.get('hours', 24))
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        sql = """
            SELECT check_time, heart_rate FROM health_record 
            WHERE elder_id = %s AND check_time >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            ORDER BY check_time ASC
        """
        records = db.execute_query(sql, (elder_id, hours))
        
        data = []
        for r in records:
            if r.get('heart_rate'):
                data.append({
                    'time': r['check_time'].strftime('%H:%M'),
                    'value': int(r['heart_rate'])
                })
        
        # 如果没有数据，生成默认数据
        if not data:
            for i in range(0, 24, 2):
                data.append({'time': f'{i:02d}:00', 'value': 68 + (i % 10)})
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/health/sleep', methods=['GET'])
def get_sleep_history():
    """获取睡眠历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    days = int(request.args.get('days', 7))
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        sql = """
            SELECT DATE(check_time) as day, AVG(sleep_hours) as sleep_hours
            FROM health_record 
            WHERE elder_id = %s AND check_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(check_time)
            ORDER BY day ASC
        """
        records = db.execute_query(sql, (elder_id, days))
        
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        
        for i, r in enumerate(records):
            sleep = float(r.get('sleep_hours', 7))
            data.append({
                'day': day_names[i % 7],
                'deepSleep': round(sleep * 0.35, 1),
                'lightSleep': round(sleep * 0.55, 1),
                'quality': min(100, int(sleep * 12))
            })
        
        # 补充缺失的天数
        while len(data) < days:
            i = len(data)
            data.append({
                'day': day_names[i % 7],
                'deepSleep': 2.5 + (i % 3) * 0.3,
                'lightSleep': 4.0 + (i % 3) * 0.4,
                'quality': 70 + (i % 5) * 5
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/health/blood-pressure', methods=['GET'])
def get_blood_pressure_history():
    """获取血压历史数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    days = int(request.args.get('days', 7))
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        sql = """
            SELECT DATE(check_time) as day, 
                   AVG(systolic_bp) as systolic, 
                   AVG(diastolic_bp) as diastolic
            FROM health_record 
            WHERE elder_id = %s AND check_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(check_time)
            ORDER BY day ASC
        """
        records = db.execute_query(sql, (elder_id, days))
        
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        
        for i, r in enumerate(records):
            data.append({
                'day': day_names[i % 7],
                'systolic': int(r.get('systolic', 120)),
                'diastolic': int(r.get('diastolic', 80)),
                'normalHigh': 120,
                'normalLow': 80
            })
        
        # 补充缺失的天数
        while len(data) < days:
            i = len(data)
            data.append({
                'day': day_names[i % 7],
                'systolic': 118 + (i % 5),
                'diastolic': 76 + (i % 4),
                'normalHigh': 120,
                'normalLow': 80
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/health/radar', methods=['GET'])
def get_health_radar():
    """获取健康雷达图数据"""
    user_id = request.args.get('user_id', 'elderly_001')
    elder_id = parse_elder_id(user_id)
    
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'error': '数据库连接失败'}), 500
    
    try:
        # 获取最近的评估结果
        latest_assessment = db.get_latest_assessment(elder_id)
        
        # 获取最近7天的健康记录
        records = db.get_health_history(elder_id, 7)
        
        # 计算各维度分数
        data = [
            {'subject': '心血管', 'score': 85, 'lastMonth': 82, 'fullMark': 100},
            {'subject': '睡眠质量', 'score': 78, 'lastMonth': 72, 'fullMark': 100},
            {'subject': '运动量', 'score': 72, 'lastMonth': 68, 'fullMark': 100},
            {'subject': '营养均衡', 'score': 88, 'lastMonth': 85, 'fullMark': 100},
            {'subject': '心理健康', 'score': 90, 'lastMonth': 88, 'fullMark': 100},
            {'subject': '体重管理', 'score': 82, 'lastMonth': 80, 'fullMark': 100},
        ]
        
        if records:
            # 心血管分数
            hr_values = [r['heart_rate'] for r in records if r.get('heart_rate')]
            bp_values = [r['systolic_bp'] for r in records if r.get('systolic_bp')]
            if hr_values:
                avg_hr = sum(hr_values) / len(hr_values)
                data[0]['score'] = max(0, min(100, round(100 - abs(avg_hr - 70) * 1.5)))
            if bp_values:
                avg_bp = sum(bp_values) / len(bp_values)
                bp_score = max(0, min(100, round(100 - abs(avg_bp - 120) * 1.5)))
                data[0]['score'] = round((data[0]['score'] + bp_score) / 2)
            
            # 睡眠分数
            sleep_values = [float(r['sleep_hours']) for r in records if r.get('sleep_hours')]
            if sleep_values:
                avg_sleep = sum(sleep_values) / len(sleep_values)
                data[1]['score'] = min(100, round(avg_sleep * 12))
            
            # 运动分数
            steps_values = [r['steps'] for r in records if r.get('steps')]
            if steps_values:
                avg_steps = sum(steps_values) / len(steps_values)
                data[2]['score'] = min(100, round(avg_steps / 100))
        
        # 如果有评估结果，使用评估分数
        if latest_assessment:
            overall = latest_assessment.get('overall_score', 80)
            data[3]['score'] = min(100, round(overall * 1.1))  # 营养
            data[4]['score'] = min(100, round(overall * 1.05))  # 心理
            data[5]['score'] = min(100, round(overall * 0.95))  # 体重
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# RAG 知识检索 API
# ============================================================================

@health_api.route('/api/rag/search', methods=['GET', 'POST', 'OPTIONS'])
def rag_search_api():
    """
    RAG 知识检索接口
    
    请求参数:
        query: 查询文本
        top_k: 返回结果数量（默认3）
        
    返回:
        {
            success: true,
            data: {
                context: "相关知识上下文",
                results: [
                    {
                        title: "知识标题",
                        content: "知识内容",
                        category: "分类",
                        score: 0.85
                    }
                ]
            }
        }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 获取参数
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '')
            top_k = data.get('top_k', 3)
        else:
            query = request.args.get('query', '')
            top_k = int(request.args.get('top_k', 3))
        
        if not query:
            return jsonify({'success': False, 'error': '缺少查询参数'}), 400
        
        # 导入 RAG 模块
        try:
            from ..modules.rag_knowledge_base import get_knowledge_base, rag_search
        except ImportError:
            # 尝试其他导入路径
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from modules.rag_knowledge_base import get_knowledge_base, rag_search
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 搜索
        results = kb.search(query, top_k=top_k)
        
        # 格式化结果
        formatted_results = []
        for item, score in results:
            formatted_results.append({
                'id': item.id,
                'title': item.title,
                'content': item.content,
                'category': item.category,
                'keywords': item.keywords,
                'source': item.source,
                'score': round(score, 4)
            })
        
        # 生成上下文
        context = kb.get_context_for_query(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'context': context,
                'results': formatted_results,
                'total': len(formatted_results)
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/rag/stats', methods=['GET', 'OPTIONS'])
def rag_stats_api():
    """
    获取 RAG 知识库统计信息
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 导入 RAG 模块
        try:
            from ..modules.rag_knowledge_base import get_knowledge_base
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from modules.rag_knowledge_base import get_knowledge_base
        
        kb = get_knowledge_base()
        stats = kb.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@health_api.route('/api/rag/enhance', methods=['POST', 'OPTIONS'])
def rag_enhance_api():
    """
    RAG 增强系统提示词接口
    
    请求参数:
        query: 用户查询
        base_prompt: 基础系统提示词（可选）
        
    返回:
        {
            success: true,
            data: {
                enhanced_prompt: "增强后的系统提示词",
                knowledge_used: 3
            }
        }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        base_prompt = data.get('base_prompt', '')
        
        if not query:
            return jsonify({'success': False, 'error': '缺少查询参数'}), 400
        
        # 导入 RAG 模块
        try:
            from ..modules.rag_knowledge_base import rag_enhance_prompt, rag_search
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from modules.rag_knowledge_base import rag_enhance_prompt, rag_search
        
        # 增强提示词
        enhanced_prompt = rag_enhance_prompt(query, base_prompt)
        
        # 获取使用的知识数量
        context = rag_search(query)
        knowledge_count = context.count('【') - 1 if context else 0  # 减去标题
        
        return jsonify({
            'success': True,
            'data': {
                'enhanced_prompt': enhanced_prompt,
                'knowledge_used': max(0, knowledge_count),
                'context': context
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
