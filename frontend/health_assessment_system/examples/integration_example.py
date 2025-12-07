#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统融合示例代码
Integration Example Code

本文件展示了如何将健康评估系统集成到其他应用中。
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# 示例1: 基础集成 - 健康评估引擎
# ============================================================

def example_basic_assessment():
    """
    基础健康评估示例
    
    展示如何使用健康评估引擎进行基本的健康评估。
    """
    print("=" * 60)
    print("示例1: 基础健康评估")
    print("=" * 60)
    
    from health_assessment_system import HealthAssessmentEngine
    from modules.assessment_config import AssessmentPeriod, TimeWindow
    from modules.report_generation import ReportType, ReportFormat
    
    # 1. 创建评估引擎
    engine = HealthAssessmentEngine()
    
    # 2. 运行评估
    result = engine.run_scheduled_assessment(
        user_id="USER001",
        period=AssessmentPeriod.MONTHLY,
        time_window=TimeWindow.LAST_30_DAYS
    )
    
    # 3. 获取评估结果
    print(f"\n评估结果:")
    print(f"  - 评估ID: {result.assessment_id}")
    print(f"  - 综合评分: {result.overall_score:.1f}/100")
    print(f"  - 健康等级: {result.health_level.value}")
    print(f"  - 疾病风险分: {result.disease_risk_score:.1f}")
    print(f"  - 生活方式分: {result.lifestyle_risk_score:.1f}")
    print(f"  - 趋势风险分: {result.trend_risk_score:.1f}")
    
    # 4. 获取TOP风险因素
    print(f"\nTOP风险因素:")
    for i, rf in enumerate(result.top_risk_factors[:3], 1):
        print(f"  {i}. {rf.name} (优先级: {rf.priority.value})")
    
    # 5. 获取优先建议
    print(f"\n优先建议:")
    for i, rec in enumerate(result.priority_recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    # 6. 生成不同版本的报告
    print(f"\n生成报告...")
    
    # 老人版报告
    elderly_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.ELDERLY,
        report_format=ReportFormat.TEXT
    )
    print(f"\n--- 老人版报告 ---")
    print(elderly_report[:500] + "..." if len(elderly_report) > 500 else elderly_report)
    
    # 7. 获取可视化数据
    viz_data = engine.get_visualization_data(
        assessment_id=result.assessment_id,
        user_id=result.user_id
    )
    print(f"\n可视化数据: {list(viz_data.keys())}")
    
    return result


# ============================================================
# 示例2: 多智能体对话集成
# ============================================================

def example_multi_agent_chat():
    """
    多智能体对话示例
    
    展示如何使用多智能体系统进行健康咨询对话。
    """
    print("\n" + "=" * 60)
    print("示例2: 多智能体对话")
    print("=" * 60)
    
    from agents import MultiAgentSystem
    
    # 1. 创建多智能体系统
    system = MultiAgentSystem(
        user_id="USER001",
        user_name="张三",
        enable_assessment=False  # 可以设为True启用评估集成
    )
    
    # 2. 获取问候语
    greeting = system.get_greeting()
    print(f"\n数字人: {greeting}")
    
    # 3. 进行对话
    conversations = [
        "我最近血压有点高，该怎么办？",
        "晚上睡不好觉怎么办？",
        "我有点担心自己的身体"
    ]
    
    for user_msg in conversations:
        print(f"\n用户: {user_msg}")
        response = system.chat(user_msg)
        # 截取响应
        short_response = response[:300] + "..." if len(response) > 300 else response
        print(f"数字人: {short_response}")
    
    # 4. 更新健康数据
    system.update_health_data("blood_pressure", {
        "systolic": 135,
        "diastolic": 85,
        "time": datetime.now().isoformat()
    })
    print(f"\n已更新血压数据")
    
    # 5. 设置用户画像
    system.set_user_profile("chronic_diseases", ["高血压"])
    system.set_user_profile("age", 65)
    print(f"已设置用户画像: {system.get_user_profile()}")
    
    return system


# ============================================================
# 示例3: Web服务集成
# ============================================================

def example_web_service():
    """
    Web服务集成示例
    
    展示如何将系统集成到Flask Web应用中。
    """
    print("\n" + "=" * 60)
    print("示例3: Web服务集成")
    print("=" * 60)
    
    # 这是一个示例代码，展示如何在Flask应用中集成
    example_code = '''
from flask import Flask, request, jsonify
from agents import MultiAgentSystem
from health_assessment_system import HealthAssessmentEngine

app = Flask(__name__)

# 全局实例
assessment_engine = HealthAssessmentEngine()
agent_sessions = {}

def get_agent(user_id):
    """获取或创建用户的智能体会话"""
    if user_id not in agent_sessions:
        agent_sessions[user_id] = MultiAgentSystem(user_id=user_id)
    return agent_sessions[user_id]

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    message = data.get('message', '')
    
    agent = get_agent(user_id)
    response = agent.chat(message)
    
    return jsonify({
        'response': response,
        'user_id': user_id
    })

@app.route('/api/assess', methods=['POST'])
def assess():
    """健康评估接口"""
    data = request.json
    user_id = data.get('user_id')
    
    result = assessment_engine.run_on_demand_assessment(
        user_id=user_id,
        triggered_by='api'
    )
    
    return jsonify({
        'assessment_id': result.assessment_id,
        'overall_score': result.overall_score,
        'health_level': result.health_level.value,
        'recommendations': result.priority_recommendations
    })

@app.route('/api/report/<assessment_id>', methods=['GET'])
def get_report(assessment_id):
    """获取报告接口"""
    user_id = request.args.get('user_id')
    report_type = request.args.get('type', 'family')
    
    report = assessment_engine.generate_report(
        assessment_id=assessment_id,
        user_id=user_id,
        report_type=ReportType[report_type.upper()]
    )
    
    return jsonify({'report': report})

if __name__ == '__main__':
    app.run(port=5000)
'''
    
    print("\nFlask集成示例代码:")
    print("-" * 40)
    print(example_code)
    print("-" * 40)
    print("\n此代码展示了如何创建REST API接口")


# ============================================================
# 示例4: 数据库集成
# ============================================================

def example_database_integration():
    """
    数据库集成示例
    
    展示如何从数据库读取数据并进行评估。
    """
    print("\n" + "=" * 60)
    print("示例4: 数据库集成")
    print("=" * 60)
    
    # 这是一个示例代码，展示如何与数据库集成
    example_code = '''
import mysql.connector
from health_assessment_system import HealthAssessmentEngine
from modules.data_preparation import HealthMetrics
from datetime import datetime, timedelta

class DatabaseHealthService:
    """数据库健康服务"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.engine = HealthAssessmentEngine()
    
    def get_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def get_elder_health_data(self, elder_id, days=30):
        """从数据库获取老人健康数据"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT check_time, systolic_bp, diastolic_bp, 
                   blood_sugar, heart_rate, spo2,
                   sleep_hours, steps
            FROM health_record
            WHERE elder_id = %s 
              AND check_time BETWEEN %s AND %s
            ORDER BY check_time
        """
        
        cursor.execute(query, (elder_id, start_date, end_date))
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return self._convert_to_health_metrics(records)
    
    def _convert_to_health_metrics(self, records):
        """转换为HealthMetrics格式"""
        if not records:
            return {}
        
        timestamps = [r['check_time'] for r in records]
        
        metrics = {}
        
        # 血压数据
        sbp_values = [r['systolic_bp'] for r in records if r['systolic_bp']]
        if sbp_values:
            metrics['blood_pressure'] = HealthMetrics(
                metric_name='blood_pressure',
                timestamps=timestamps[:len(sbp_values)],
                values=sbp_values,
                unit='mmHg'
            )
        
        # 血糖数据
        glucose_values = [r['blood_sugar'] for r in records if r['blood_sugar']]
        if glucose_values:
            metrics['blood_glucose'] = HealthMetrics(
                metric_name='blood_glucose',
                timestamps=timestamps[:len(glucose_values)],
                values=glucose_values,
                unit='mmol/L'
            )
        
        return metrics
    
    def assess_elder(self, elder_id):
        """评估老人健康状况"""
        # 获取数据
        health_data = self.get_elder_health_data(elder_id)
        
        # 运行评估
        result = self.engine.run_on_demand_assessment(
            user_id=str(elder_id),
            triggered_by='database_service'
        )
        
        # 保存评估结果到数据库
        self.save_assessment_result(elder_id, result)
        
        return result
    
    def save_assessment_result(self, elder_id, result):
        """保存评估结果到数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO assessment_result 
            (elder_id, assessment_time, overall_risk_score, 
             overall_risk_level, disease_overall_score,
             lifestyle_risk_score, trend_risk_score,
             advice_text_elder)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            elder_id,
            datetime.now(),
            result.overall_score,
            result.health_level.value,
            result.disease_risk_score,
            result.lifestyle_risk_score,
            result.trend_risk_score,
            '\\n'.join(result.priority_recommendations)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()

# 使用示例
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'health_assessment_db'
}

service = DatabaseHealthService(db_config)
result = service.assess_elder(elder_id=1)
print(f"评估完成: {result.overall_score}")
'''
    
    print("\n数据库集成示例代码:")
    print("-" * 40)
    print(example_code)
    print("-" * 40)
    print("\n此代码展示了如何从MySQL数据库读取数据并进行评估")


# ============================================================
# 示例5: 自定义评估器扩展
# ============================================================

def example_custom_assessor():
    """
    自定义评估器示例
    
    展示如何扩展系统添加新的评估器。
    """
    print("\n" + "=" * 60)
    print("示例5: 自定义评估器扩展")
    print("=" * 60)
    
    from modules.disease_assessment import DiseaseRiskResult, RiskLevel, ControlStatus
    from typing import Dict, Optional
    
    class HeartDiseaseAssessor:
        """
        心脏病风险评估器
        
        这是一个自定义评估器的示例，展示如何扩展系统。
        """
        
        def __init__(self):
            # 定义阈值
            self.thresholds = {
                'heart_rate': {
                    'bradycardia': 60,
                    'normal_low': 60,
                    'normal_high': 100,
                    'tachycardia': 100
                },
                'spo2': {
                    'normal': 95,
                    'mild_hypoxia': 90,
                    'moderate_hypoxia': 85
                }
            }
        
        def assess(
            self,
            features: Dict,
            baseline: Optional[Dict] = None
        ) -> DiseaseRiskResult:
            """
            评估心脏病风险
            
            Args:
                features: 特征字典
                baseline: 基线数据
            
            Returns:
                DiseaseRiskResult: 评估结果
            """
            # 获取特征
            heart_rate = features.get('heart_rate_mean', 75)
            spo2 = features.get('spo2_mean', 98)
            heart_rate_std = features.get('heart_rate_std', 5)
            
            # 计算风险评分
            risk_score = 0
            key_findings = []
            recommendations = []
            
            # 心率评估
            if heart_rate < self.thresholds['heart_rate']['bradycardia']:
                risk_score += 30
                key_findings.append("心率过缓")
                recommendations.append("建议心电图检查")
            elif heart_rate > self.thresholds['heart_rate']['tachycardia']:
                risk_score += 25
                key_findings.append("心率过快")
                recommendations.append("注意休息，避免剧烈运动")
            
            # 心率变异性评估
            if heart_rate_std > 15:
                risk_score += 20
                key_findings.append("心率波动较大")
            
            # 血氧评估
            if spo2 < self.thresholds['spo2']['moderate_hypoxia']:
                risk_score += 40
                key_findings.append("血氧严重偏低")
                recommendations.append("立即就医")
            elif spo2 < self.thresholds['spo2']['mild_hypoxia']:
                risk_score += 25
                key_findings.append("血氧偏低")
                recommendations.append("注意通风，必要时吸氧")
            elif spo2 < self.thresholds['spo2']['normal']:
                risk_score += 10
                key_findings.append("血氧轻度偏低")
            
            # 确定风险等级
            if risk_score >= 60:
                risk_level = RiskLevel.HIGH
                control_status = ControlStatus.POOR
            elif risk_score >= 40:
                risk_level = RiskLevel.MEDIUM
                control_status = ControlStatus.FAIR
            elif risk_score >= 20:
                risk_level = RiskLevel.LOW
                control_status = ControlStatus.GOOD
            else:
                risk_level = RiskLevel.LOW
                control_status = ControlStatus.EXCELLENT
            
            # 默认建议
            if not recommendations:
                recommendations.append("继续保持良好的心脏健康")
            
            if not key_findings:
                key_findings.append("心脏指标正常")
            
            return DiseaseRiskResult(
                disease_name="心脏病风险",
                control_status=control_status,
                risk_level=risk_level,
                risk_score=risk_score,
                control_quality_score=100 - risk_score,
                key_findings=key_findings,
                recommendations=recommendations,
                details={
                    'heart_rate': heart_rate,
                    'spo2': spo2,
                    'heart_rate_std': heart_rate_std
                }
            )
    
    # 测试自定义评估器
    print("\n测试自定义心脏病评估器:")
    
    assessor = HeartDiseaseAssessor()
    
    # 测试用例1: 正常情况
    result1 = assessor.assess({
        'heart_rate_mean': 72,
        'spo2_mean': 98,
        'heart_rate_std': 5
    })
    print(f"\n测试1 (正常):")
    print(f"  风险等级: {result1.risk_level.value}")
    print(f"  风险评分: {result1.risk_score}")
    print(f"  发现: {result1.key_findings}")
    
    # 测试用例2: 异常情况
    result2 = assessor.assess({
        'heart_rate_mean': 110,
        'spo2_mean': 88,
        'heart_rate_std': 20
    })
    print(f"\n测试2 (异常):")
    print(f"  风险等级: {result2.risk_level.value}")
    print(f"  风险评分: {result2.risk_score}")
    print(f"  发现: {result2.key_findings}")
    print(f"  建议: {result2.recommendations}")
    
    return assessor


# ============================================================
# 示例6: 完整集成流程
# ============================================================

def example_full_integration():
    """
    完整集成流程示例
    
    展示一个完整的健康管理服务类。
    """
    print("\n" + "=" * 60)
    print("示例6: 完整集成流程")
    print("=" * 60)
    
    from health_assessment_system import HealthAssessmentEngine
    from agents import MultiAgentSystem
    from modules.assessment_config import AssessmentPeriod, TimeWindow
    from modules.report_generation import ReportType, ReportFormat
    
    class HealthManagementService:
        """
        健康管理服务
        
        整合健康评估和智能对话功能的完整服务类。
        """
        
        def __init__(self):
            self.assessment_engine = HealthAssessmentEngine()
            self.agent_sessions: Dict[str, MultiAgentSystem] = {}
        
        def get_agent(self, user_id: str, user_name: str = "") -> MultiAgentSystem:
            """获取或创建用户的智能体会话"""
            if user_id not in self.agent_sessions:
                self.agent_sessions[user_id] = MultiAgentSystem(
                    user_id=user_id,
                    user_name=user_name,
                    enable_assessment=True
                )
            return self.agent_sessions[user_id]
        
        def chat(self, user_id: str, message: str) -> str:
            """与AI对话"""
            agent = self.get_agent(user_id)
            return agent.chat(message)
        
        def assess(self, user_id: str, triggered_by: str = "system"):
            """进行健康评估"""
            return self.assessment_engine.run_on_demand_assessment(
                user_id=user_id,
                triggered_by=triggered_by
            )
        
        def get_report(
            self,
            user_id: str,
            assessment_id: str,
            report_type: str = "family"
        ) -> str:
            """获取评估报告"""
            rt = ReportType[report_type.upper()]
            return self.assessment_engine.generate_report(
                assessment_id=assessment_id,
                user_id=user_id,
                report_type=rt,
                report_format=ReportFormat.TEXT
            )
        
        def update_health_data(
            self,
            user_id: str,
            data_type: str,
            data: Dict
        ):
            """更新健康数据"""
            agent = self.get_agent(user_id)
            agent.update_health_data(data_type, data)
        
        def get_visualization_data(
            self,
            user_id: str,
            assessment_id: str
        ) -> Dict:
            """获取可视化数据"""
            return self.assessment_engine.get_visualization_data(
                assessment_id=assessment_id,
                user_id=user_id
            )
        
        def get_history(self, user_id: str, limit: int = 10) -> List:
            """获取评估历史"""
            return self.assessment_engine.get_user_assessment_history(
                user_id=user_id,
                limit=limit
            )
    
    # 测试完整服务
    print("\n测试完整健康管理服务:")
    
    service = HealthManagementService()
    user_id = "DEMO_USER"
    
    # 1. 对话
    print("\n1. 对话测试:")
    response = service.chat(user_id, "你好，我想了解一下我的健康状况")
    print(f"   AI: {response[:200]}...")
    
    # 2. 评估
    print("\n2. 健康评估:")
    result = service.assess(user_id, "demo")
    print(f"   评估ID: {result.assessment_id}")
    print(f"   综合评分: {result.overall_score:.1f}")
    
    # 3. 获取报告
    print("\n3. 获取报告:")
    report = service.get_report(user_id, result.assessment_id, "elderly")
    print(f"   报告长度: {len(report)} 字符")
    
    # 4. 更新数据
    print("\n4. 更新健康数据:")
    service.update_health_data(user_id, "blood_pressure", {
        "systolic": 130,
        "diastolic": 80
    })
    print("   已更新血压数据")
    
    print("\n✓ 完整集成流程测试完成")
    
    return service


# ============================================================
# 主函数
# ============================================================

def main():
    """运行所有示例"""
    print("=" * 60)
    print("  系统融合示例代码")
    print("=" * 60)
    
    try:
        # 示例1: 基础评估
        example_basic_assessment()
        
        # 示例2: 多智能体对话
        example_multi_agent_chat()
        
        # 示例3: Web服务集成
        example_web_service()
        
        # 示例4: 数据库集成
        example_database_integration()
        
        # 示例5: 自定义评估器
        example_custom_assessor()
        
        # 示例6: 完整集成
        example_full_integration()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
