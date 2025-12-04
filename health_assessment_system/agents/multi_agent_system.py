"""
多智能体系统
============

整合所有智能体，提供统一的对话接口。
集成健康评估系统能力。
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_agent import (
    AgentRole, AgentMessage, AgentMemory, 
    MessageType, EmotionState
)
from .health_butler import HealthButlerAgent
from .chronic_disease_expert import ChronicDiseaseExpertAgent
from .lifestyle_coach import LifestyleCoachAgent
from .emotional_care import EmotionalCareAgent
from .agent_coordinator import AgentCoordinator


class MultiAgentSystem:
    """
    多智能体数字人系统
    
    整合健康管家、慢病专家、生活教练、心理关怀师等多个智能体，
    提供全方位的健康管理服务。
    
    使用示例：
    ```python
    system = MultiAgentSystem(user_id="USER001")
    response = system.chat("我最近血压有点高")
    print(response)
    ```
    """
    
    def __init__(
        self,
        user_id: str,
        user_name: str = "",
        enable_assessment: bool = True
    ):
        """
        初始化多智能体系统
        
        Args:
            user_id: 用户ID
            user_name: 用户姓名
            enable_assessment: 是否启用健康评估集成
        """
        self.user_id = user_id
        self.user_name = user_name
        self.enable_assessment = enable_assessment
        
        # 初始化记忆系统
        self.memory = AgentMemory(user_id=user_id)
        if user_name:
            self.memory.update_user_profile("name", user_name)
        
        # 初始化协调器
        self.coordinator = AgentCoordinator()
        
        # 注册智能体
        self._register_agents()
        
        # 健康评估引擎（懒加载）
        self._assessment_engine = None
        
        # 会话状态
        self.session_start = datetime.now()
        self.is_active = True
        
        print(f"✓ 多智能体系统初始化完成")
        print(f"  用户: {user_id}")
        print(f"  智能体数量: {len(self.coordinator.agents)}")
    
    def _register_agents(self):
        """注册所有智能体"""
        # 健康管家（默认智能体）
        butler = HealthButlerAgent(name="小康")
        self.coordinator.register_agent(butler, is_default=True)
        
        # 慢病专家
        chronic_expert = ChronicDiseaseExpertAgent(name="慢病专家")
        self.coordinator.register_agent(chronic_expert)
        
        # 生活教练
        lifestyle_coach = LifestyleCoachAgent(name="生活教练")
        self.coordinator.register_agent(lifestyle_coach)
        
        # 心理关怀师
        emotional_care = EmotionalCareAgent(name="心理关怀师")
        self.coordinator.register_agent(emotional_care)
    
    @property
    def assessment_engine(self):
        """懒加载健康评估引擎"""
        if self._assessment_engine is None and self.enable_assessment:
            try:
                from core.assessment_engine import HealthAssessmentEngine
                self._assessment_engine = HealthAssessmentEngine()
                print("✓ 健康评估引擎加载成功")
            except ImportError as e:
                print(f"⚠ 健康评估引擎加载失败: {e}")
                self._assessment_engine = None
        return self._assessment_engine
    
    def chat(self, user_input: str) -> str:
        """
        与数字人对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            智能体响应文本
        """
        if not user_input.strip():
            return "请问有什么可以帮您的吗？"
        
        # 检查是否需要生成健康报告
        if self._should_generate_report(user_input):
            return self._generate_health_report()
        
        # 检查是否需要专家会诊（多智能体协作）
        if self._should_consult_experts(user_input):
            return self._expert_consultation(user_input)
        
        # 常规对话处理
        response = self.coordinator.process_message(
            user_input=user_input,
            memory=self.memory,
            context=self._get_context()
        )
        
        return self._format_response(response)
    
    def _should_generate_report(self, text: str) -> bool:
        """判断是否需要生成健康报告"""
        report_keywords = ["评估", "报告", "分析", "总结", "看看情况"]
        return any(k in text for k in report_keywords)
    
    def _should_consult_experts(self, text: str) -> bool:
        """判断是否需要专家会诊"""
        # 复杂问题需要多个专家
        complex_keywords = ["全面", "综合", "详细分析", "专家"]
        return any(k in text for k in complex_keywords)
    
    def _generate_health_report(self) -> str:
        """生成健康报告"""
        if self.assessment_engine is None:
            return self._generate_simple_report()
        
        try:
            # 使用健康评估引擎
            from modules.assessment_config import AssessmentPeriod, TimeWindow
            
            result = self.assessment_engine.run_scheduled_assessment(
                user_id=self.user_id,
                period=AssessmentPeriod.ON_DEMAND,
                time_window=TimeWindow.LAST_7_DAYS
            )
            
            # 格式化报告
            report = f"""📊 **健康评估报告**

**用户**: {self.user_id}
**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

**🏆 综合评分**: {result.overall_score:.1f}/100
**健康等级**: {result.health_level.value}

**📋 各维度评分**:
"""
            for dim, score in result.dimension_scores.items():
                report += f"- {dim}: {score:.1f}分\n"
            
            if result.top_risks:
                report += "\n**⚠️ 主要风险因素**:\n"
                for risk in result.top_risks[:3]:
                    report += f"- {risk}\n"
            
            if result.recommendations:
                report += "\n**💡 建议**:\n"
                for rec in result.recommendations[:3]:
                    report += f"- {rec}\n"
            
            return report
            
        except Exception as e:
            print(f"评估失败: {e}")
            return self._generate_simple_report()
    
    def _generate_simple_report(self) -> str:
        """生成简单报告（无评估引擎时）"""
        return f"""📊 **健康状况简报**

**用户**: {self.user_id}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

**📌 健康建议**:

1. **血压管理**
   - 建议每天测量血压并记录
   - 保持低盐饮食
   - 按医嘱服药

2. **血糖控制**
   - 定期监测空腹和餐后血糖
   - 控制饮食，少吃高糖食物

3. **生活方式**
   - 每天步行6000步以上
   - 保证7-8小时睡眠
   - 保持心情愉悦

**🔔 提醒**:
- 定期体检
- 有不适及时就医

如需详细评估，请提供健康数据。"""
    
    def _expert_consultation(self, user_input: str) -> str:
        """专家会诊（多智能体协作）"""
        # 让多个智能体同时处理
        responses = self.coordinator.multi_agent_process(
            user_input=user_input,
            memory=self.memory
        )
        
        if not responses:
            return "暂时无法提供专家建议，请稍后再试。"
        
        # 整合响应
        result = "🏥 **专家会诊结果**\n\n"
        result += f"针对您的问题「{user_input}」，我们的专家团队为您分析如下：\n\n"
        
        for response in responses:
            agent_role = response.metadata.get("processed_by", "unknown")
            agent_name = self._get_agent_display_name(agent_role)
            
            result += f"---\n\n**{agent_name}** 的建议：\n\n"
            result += response.content + "\n\n"
        
        result += "---\n\n💡 **综合建议**: 请结合各位专家的意见，根据自身情况选择最适合的方案。如有疑问，建议咨询医生。"
        
        return result
    
    def _get_agent_display_name(self, role_value: str) -> str:
        """获取智能体显示名称"""
        names = {
            "health_butler": "👨‍⚕️ 健康管家",
            "chronic_expert": "🩺 慢病专家",
            "lifestyle_coach": "🏃 生活教练",
            "emotional_care": "🤗 心理关怀师"
        }
        return names.get(role_value, role_value)
    
    def _get_context(self) -> Dict:
        """获取当前上下文"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "session_duration": (datetime.now() - self.session_start).seconds,
            "message_count": len(self.memory.short_term)
        }
    
    def _format_response(self, response: AgentMessage) -> str:
        """格式化响应"""
        # 获取处理智能体信息
        agent_role = response.metadata.get("processed_by", "")
        agent_name = self._get_agent_display_name(agent_role)
        
        # 添加智能体标识
        if agent_role:
            return f"{agent_name}:\n\n{response.content}"
        return response.content
    
    def get_greeting(self) -> str:
        """获取问候语"""
        butler = self.coordinator.get_agent(AgentRole.HEALTH_BUTLER)
        if butler:
            return butler.get_greeting(self.user_name)
        return f"您好{('，' + self.user_name) if self.user_name else ''}！有什么可以帮您的吗？"
    
    def get_agents_info(self) -> List[Dict]:
        """获取所有智能体信息"""
        return self.coordinator.get_all_agents_info()
    
    def get_session_info(self) -> Dict:
        """获取会话信息"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "session_start": self.session_start.isoformat(),
            "duration_seconds": (datetime.now() - self.session_start).seconds,
            "conversation": self.coordinator.get_conversation_summary()
        }
    
    def clear_conversation(self):
        """清空对话历史"""
        self.memory.clear_short_term()
        self.coordinator.clear_history()
    
    def update_health_data(self, data_type: str, data: Dict):
        """
        更新健康数据到记忆
        
        Args:
            data_type: 数据类型 (blood_pressure, glucose, etc.)
            data: 数据内容
        """
        self.memory.set_context(f"{data_type}_data", data)
        
        # 特殊处理某些数据类型
        if data_type == "blood_pressure":
            self.memory.set_context("recent_blood_pressure", data)
        elif data_type == "glucose":
            self.memory.set_context("glucose_data", data)
    
    def set_user_profile(self, key: str, value: Any):
        """设置用户画像"""
        self.memory.update_user_profile(key, value)
    
    def get_user_profile(self) -> Dict:
        """获取用户画像"""
        return self.memory.long_term.copy()


def create_digital_human(
    user_id: str,
    user_name: str = "",
    **kwargs
) -> MultiAgentSystem:
    """
    创建数字人实例的便捷函数
    
    Args:
        user_id: 用户ID
        user_name: 用户姓名
        **kwargs: 其他参数
        
    Returns:
        MultiAgentSystem实例
    """
    return MultiAgentSystem(
        user_id=user_id,
        user_name=user_name,
        **kwargs
    )


# 命令行测试
if __name__ == "__main__":
    print("=" * 60)
    print("多智能体数字人系统 - 测试模式")
    print("=" * 60)
    
    # 创建系统
    system = MultiAgentSystem(user_id="TEST001", user_name="测试用户")
    
    # 显示问候
    print("\n" + system.get_greeting())
    print("\n" + "-" * 40)
    
    # 测试对话
    test_messages = [
        "你好",
        "我最近血压有点高，该怎么办？",
        "晚上睡不好觉怎么办？",
        "我有点担心自己的身体",
        "帮我做个健康评估"
    ]
    
    for msg in test_messages:
        print(f"\n👤 用户: {msg}")
        print("-" * 40)
        response = system.chat(msg)
        print(response)
        print()
