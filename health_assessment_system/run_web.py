#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动Web服务 - 健康评估API服务器
"""

import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_flask():
    """检查Flask是否安装"""
    try:
        import flask
        import flask_cors
        return True
    except ImportError:
        print("缺少依赖，正在安装...")
        os.system("pip install flask flask-cors")
        return True

def generate_mock_data():
    """生成模拟健康数据 - 匹配前端 TodayHealthData 接口"""
    now = datetime.now()
    
    steps = random.randint(3000, 8000)
    goal = 10000
    weight = round(65 + random.random() * 5, 1)
    height = 1.70  # 假设身高
    bmi = round(weight / (height * height), 1)
    
    # 今日健康数据 - 匹配前端接口
    today_data = {
        'userId': 'elderly_001',
        'userName': '张三',
        'vitalSigns': {
            'temperature': {
                'value': round(36.2 + random.random() * 0.8, 1),
                'unit': '°C',
                'change': round(-0.2 + random.random() * 0.4, 1),
                'status': '正常'
            },
            'bloodSugar': {
                'value': round(4.5 + random.random() * 2, 1),
                'unit': 'mmol/L',
                'status': '正常',
                'testType': '空腹'
            },
            'bloodPressure': {
                'systolic': random.randint(110, 130),
                'diastolic': random.randint(70, 85),
                'unit': 'mmHg',
                'status': '正常'
            },
            'heartRate': {
                'value': random.randint(65, 85),
                'unit': 'bpm',
                'change': random.randint(-5, 5),
                'status': '正常'
            },
            'spo2': {
                'value': random.randint(96, 99),
                'unit': '%',
                'status': '正常'
            }
        },
        'activity': {
            'steps': steps,
            'goal': goal,
            'percentage': round(steps / goal * 100, 1),
            'distance': round(steps * 0.7 / 1000, 2),
            'calories': round(steps * 0.04, 0)
        },
        'weight': {
            'value': weight,
            'unit': 'kg',
            'bmi': bmi,
            'bmiStatus': '正常' if 18.5 <= bmi <= 24 else ('偏瘦' if bmi < 18.5 else '偏重')
        },
        'lastUpdate': now.isoformat()
    }
    
    return today_data

def generate_chart_data(days=7):
    """生成图表数据"""
    now = datetime.now()
    
    # 心率数据
    heart_rate = []
    for i in range(days * 24):
        time = now - timedelta(hours=days*24-i)
        heart_rate.append({
            'time': time.strftime('%H:%M'),
            'date': time.strftime('%Y-%m-%d'),
            'value': random.randint(60, 90)
        })
    
    # 睡眠数据 - 匹配前端 SleepDataPoint 接口
    days_of_week = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    sleep = []
    for i in range(days):
        deep = round(1.5 + random.random() * 2, 1)
        light = round(3 + random.random() * 2.5, 1)
        quality = random.randint(60, 95)
        sleep.append({
            'day': days_of_week[i % 7],
            'deepSleep': deep,
            'lightSleep': light,
            'quality': quality
        })
    
    # 血压数据 - 匹配前端 BloodPressureDataPoint 接口
    blood_pressure = []
    for i in range(days):
        blood_pressure.append({
            'day': days_of_week[i % 7],
            'systolic': random.randint(110, 135),
            'diastolic': random.randint(70, 90),
            'normalHigh': 120,
            'normalLow': 80
        })
    
    # 雷达图数据 - 匹配前端 HealthRadarDataPoint 接口，需要6个维度
    health_radar = [
        {'subject': '心血管', 'score': random.randint(70, 95), 'lastMonth': random.randint(65, 90), 'fullMark': 100},
        {'subject': '睡眠质量', 'score': random.randint(60, 90), 'lastMonth': random.randint(55, 85), 'fullMark': 100},
        {'subject': '运动量', 'score': random.randint(50, 85), 'lastMonth': random.randint(45, 80), 'fullMark': 100},
        {'subject': '营养均衡', 'score': random.randint(65, 90), 'lastMonth': random.randint(60, 85), 'fullMark': 100},
        {'subject': '心理健康', 'score': random.randint(70, 95), 'lastMonth': random.randint(65, 90), 'fullMark': 100},
        {'subject': '体重管理', 'score': random.randint(70, 90), 'lastMonth': random.randint(65, 85), 'fullMark': 100},
    ]
    
    return {
        'heartRate': heart_rate[-48:],  # 最近48小时
        'sleep': sleep,
        'bloodPressure': blood_pressure,
        'healthRadar': health_radar
    }

def main():
    """启动Web服务"""
    print("=" * 60)
    print("  健康评估系统 - Web API 服务")
    print("=" * 60)
    
    if not check_flask():
        return
    
    from flask import Flask, jsonify, request, make_response
    from flask_cors import CORS
    
    app = Flask(__name__)
    
    # 手动处理 CORS（不使用 flask_cors 避免重复头）
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response('', 200)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response
    
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response
    
    # ============================================================================
    # 健康数据 API
    # ============================================================================
    
    # 健康检查接口
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': '健康评估服务运行正常'
        })
    
    # 获取今日健康数据
    @app.route('/api/health/today', methods=['GET'])
    def get_today_health():
        user_id = request.args.get('user_id', 'default')
        return jsonify({
            'success': True,
            'data': generate_mock_data()
        })
    
    # 获取图表数据 (支持两种路径)
    @app.route('/api/health/charts', methods=['GET'])
    @app.route('/api/health/chart-data', methods=['GET'])
    def get_chart_data():
        user_id = request.args.get('user_id', 'default')
        days = int(request.args.get('days', 7))
        return jsonify({
            'success': True,
            'data': generate_chart_data(days)
        })
    
    # 获取可视化数据
    @app.route('/api/health/visualization', methods=['GET'])
    def get_visualization():
        user_id = request.args.get('user_id', 'default')
        return jsonify({
            'success': True,
            'data': {
                'radarData': [
                    {'dimension': '心血管健康', 'score': random.randint(70, 95)},
                    {'dimension': '睡眠质量', 'score': random.randint(60, 90)},
                    {'dimension': '运动健康', 'score': random.randint(50, 85)},
                    {'dimension': '代谢健康', 'score': random.randint(65, 90)},
                    {'dimension': '心理健康', 'score': random.randint(70, 95)},
                ],
                'overallScore': random.randint(75, 90),
                'healthLevel': '良好'
            }
        })
    
    # 健康评估接口
    @app.route('/api/health/assess', methods=['POST'])
    def run_assessment():
        
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id', 'default')
            
            # 返回模拟评估结果 - 匹配前端 AssessmentResult 接口
            overall_score = random.randint(75, 92)
            health_level = 'excellent' if overall_score >= 90 else ('good' if overall_score >= 80 else ('suboptimal' if overall_score >= 70 else 'attention'))
            
            return jsonify({
                'success': True,
                'data': {
                    'assessment_id': f'assess_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'user_id': user_id,
                    'assessment_date': datetime.now().isoformat(),
                    'overall_score': overall_score,
                    'health_level': health_level,
                    'dimension_scores': {
                        'disease': random.randint(70, 95),
                        'lifestyle': random.randint(60, 90),
                        'trend': random.randint(65, 90)
                    },
                    'top_risk_factors': [
                        {'name': '血压偏高', 'score': random.randint(60, 80), 'priority': 'medium', 'category': 'disease'},
                        {'name': '睡眠不足', 'score': random.randint(50, 70), 'priority': 'low', 'category': 'lifestyle'}
                    ],
                    'recommendations': [
                        '建议保持规律作息，每天睡眠7-8小时',
                        '适当增加有氧运动，每周3-5次',
                        '注意饮食均衡，减少盐分摄入'
                    ]
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ============================================================================
    # AI 对话 API
    # ============================================================================
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        try:
            from agents import MultiAgentSystem
            
            data = request.get_json()
            message = data.get('message', '')
            user_id = data.get('user_id', 'default_user')
            
            system = MultiAgentSystem(
                user_id=user_id,
                user_name="用户",
                enable_assessment=False
            )
            
            response = system.chat(message)
            
            return jsonify({
                'success': True,
                'data': {
                    'response': response
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    print()
    print("  🌐 API服务已启动")
    print("  访问地址: http://localhost:5000")
    print("  健康检查: http://localhost:5000/api/health")
    print()
    print("  可用接口:")
    print("  - GET  /api/health/today?user_id=xxx")
    print("  - GET  /api/health/charts?user_id=xxx&days=7")
    print("  - GET  /api/health/visualization?user_id=xxx")
    print("  - POST /api/health/assess")
    print("  - POST /api/chat")
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
