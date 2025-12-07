"""
健康管家智能体
==============

作为默认智能体，处理日常健康问答和数据解读。
"""

from typing import Dict, List
from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class HealthButlerAgent(BaseAgent):
    """
    健康管家智能体 - 默认主交互智能体
    
    职责：
    - 日常健康问答
    - 健康数据解读
    - 健康提醒
    - 路由复杂问题到专家
    """
    
    def __init__(self, name: str = "小康"):
        super().__init__(
            name=name,
            role=AgentRole.HEALTH_BUTLER,
            description="您的专属健康管家，为您解答日常健康问题",
            avatar="🏠",
            personality="温和、耐心、细心"
        )
        
        self.capabilities = [
            "日常健康问答",
            "健康数据解读",
            "健康提醒",
            "生活建议"
        ]
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """健康管家是默认智能体，总能处理消息，但给予较低置信度"""
        text = message.content.lower()
        keywords = self.extract_keywords(text)
        
        # 一般性健康问题
        general_keywords = ["健康", "身体", "检查", "报告", "数据", "指标"]
        if any(kw in text for kw in general_keywords):
            return 0.7
        
        # 问候语
        greetings = ["你好", "您好", "早上好", "晚上好", "hi", "hello"]
        if any(g in text for g in greetings):
            return 0.9
        
        # 作为默认智能体，基础置信度
        return 0.5
    
    def get_system_prompt(self) -> str:
        """健康管家专业系统提示词"""
        return """你是"健康管家"，一位专业、温和、耐心的AI健康助手，专门服务老年用户。

【你的职责】
1. 解答日常健康问题
2. 解读健康数据和体检报告
3. 提供健康生活建议
4. 给予健康提醒

【回答原则】
1. 语言简洁明了，避免专业术语，适合老年人理解
2. 态度温和耐心，像家人一样关心用户
3. 回答要有条理，使用编号或分点
4. 遇到严重症状时，提醒及时就医
5. 不做诊断，只提供健康建议

【回答格式】
- 保持简短，控制在200字以内
- 使用emoji增加亲和力（适量）
- 重要提醒用【】标注"""
    
    def process(self, message: AgentMessage, memory: AgentMemory, user_role: str = "elderly") -> AgentMessage:
        """处理消息 - 调用讯飞星火（支持角色适配）"""
        text = message.content.strip()
        
        # 构建对话历史
        history = []
        for msg in memory.get_recent_context(5):
            role = "user" if msg.type == MessageType.USER_INPUT else "assistant"
            history.append({"role": role, "content": msg.content})
        
        # 调用大模型（传递用户角色以适配回复风格）
        response_text = self.call_llm(
            user_input=text,
            history=history,
            user_role=user_role
        )
        
        return AgentMessage(
            type=MessageType.AGENT_RESPONSE,
            role=self.role,
            content=response_text,
            emotion=EmotionState.CARING
        )
    
    def _get_greeting_response(self, memory: AgentMemory) -> str:
        user_name = memory.long_term.get("name", "您")
        return f"您好{user_name}！我是您的健康管家小康。今天感觉怎么样？有什么健康问题需要我帮您解答吗？"
    
    def _interpret_health_data(self, text: str, memory: AgentMemory) -> str:
        return """好的，让我帮您解读一下健康数据。

一般来说，我们需要关注以下几个关键指标：
1. **血压**：正常范围是收缩压90-140mmHg，舒张压60-90mmHg
2. **心率**：正常成人静息心率60-100次/分
3. **血糖**：空腹血糖3.9-6.1mmol/L为正常

如果您有具体的数值，可以告诉我，我来帮您详细分析。"""
    
    def _health_reminder(self, text: str, memory: AgentMemory) -> str:
        return """好的，我来帮您设置健康提醒：

📌 日常健康小贴士：
1. 按时服药，不要漏服
2. 定期测量血压、血糖
3. 保持规律作息
4. 适量运动，量力而行

需要我帮您设置具体的提醒时间吗？"""
    
    def _general_health_advice(self, text: str, memory: AgentMemory) -> str:
        return """感谢您的咨询！作为您的健康管家，我建议：

1. 保持良好的生活习惯
2. 均衡饮食，少盐少油
3. 适量运动，每天30分钟
4. 保持心情愉悦
5. 定期体检，及时就医

如果您有具体的健康问题，请详细描述，我会为您提供更专业的建议。"""
