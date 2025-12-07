"""
智能体基类
==========

定义所有智能体的基础接口和共享功能。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """智能体角色枚举"""
    HEALTH_BUTLER = "health_butler"      # 健康管家（主交互）
    CHRONIC_EXPERT = "chronic_expert"    # 慢病专家
    LIFESTYLE_COACH = "lifestyle_coach"  # 生活方式教练
    EMOTIONAL_CARE = "emotional_care"    # 心理关怀师
    COORDINATOR = "coordinator"          # 协调器


class MessageType(Enum):
    """消息类型"""
    USER_INPUT = "user_input"            # 用户输入
    AGENT_RESPONSE = "agent_response"    # 智能体响应
    AGENT_THOUGHT = "agent_thought"      # 智能体思考过程
    SYSTEM_INFO = "system_info"          # 系统信息


class EmotionState(Enum):
    """情绪状态"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    CONCERNED = "concerned"
    ENCOURAGING = "encouraging"
    CARING = "caring"
    SERIOUS = "serious"


@dataclass
class AgentMessage:
    """智能体消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: MessageType = MessageType.AGENT_RESPONSE
    role: AgentRole = AgentRole.HEALTH_BUTLER
    content: str = ""
    emotion: EmotionState = EmotionState.NEUTRAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "role": self.role.value,
            "content": self.content,
            "emotion": self.emotion.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class AgentMemory:
    """智能体记忆"""
    user_id: str
    short_term: List[AgentMessage] = field(default_factory=list)  # 短期记忆（当前对话）
    long_term: Dict[str, Any] = field(default_factory=dict)       # 长期记忆（用户画像）
    context: Dict[str, Any] = field(default_factory=dict)         # 上下文信息
    
    def add_message(self, message: AgentMessage):
        """添加消息到短期记忆"""
        self.short_term.append(message)
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def get_recent_context(self, n: int = 5) -> List[AgentMessage]:
        """获取最近n条消息"""
        return self.short_term[-n:] if self.short_term else []
    
    def update_user_profile(self, key: str, value: Any):
        """更新用户画像"""
        self.long_term[key] = value
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self.context[key] = value


class BaseAgent(ABC):
    """
    智能体基类
    
    所有智能体都继承此类，实现各自的专业能力。
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str,
        avatar: str = "🤖",
        personality: str = "友好、专业"
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.description = description
        self.avatar = avatar
        self.personality = personality
        self.is_active = True
        self.capabilities: List[str] = []
        
    @abstractmethod
    def process(self, message: AgentMessage, memory: AgentMemory) -> AgentMessage:
        """处理消息并生成响应"""
        pass
    
    @abstractmethod
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """判断是否能处理该消息，返回置信度(0-1)"""
        pass
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        # 健康相关关键词
        health_keywords = [
            "血压", "高血压", "降压", "血糖", "糖尿病", "血脂", "胆固醇",
            "心率", "心脏", "心血管", "头晕", "头痛", "失眠", "睡眠",
            "运动", "锻炼", "饮食", "吃", "喝", "药", "吃药", "服药",
            "焦虑", "担心", "害怕", "情绪", "心情", "压力", "紧张"
        ]
        for kw in health_keywords:
            if kw in text:
                keywords.append(kw)
        return keywords
    
    def detect_intent(self, text: str) -> str:
        """检测用户意图"""
        if any(kw in text for kw in ["怎么办", "怎么治", "怎么控制", "如何"]):
            return "seek_advice"
        elif any(kw in text for kw in ["正常吗", "高吗", "低吗", "危险吗"]):
            return "seek_evaluation"
        elif any(kw in text for kw in ["难受", "不舒服", "疼", "痛"]):
            return "report_symptom"
        elif any(kw in text for kw in ["担心", "害怕", "焦虑", "紧张"]):
            return "emotional_support"
        else:
            return "general_query"
    
    def call_llm(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        user_role: str = "elderly"
    ) -> str:
        """
        调用讯飞星火大模型
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词（智能体专业prompt）
            history: 对话历史
            user_role: 用户角色 (elderly/children/community)
            
        Returns:
            大模型回复
        """
        try:
            from services.spark_service import spark_service
            
            # 根据用户角色生成适配的系统提示词
            if system_prompt is None:
                system_prompt = self.get_role_adapted_prompt(user_role)
            
            response = spark_service.chat(
                user_input=user_input,
                system_prompt=system_prompt,
                history=history,
                temperature=0.7,
                max_tokens=2048
            )
            
            logger.info(f"[{self.name}] LLM调用成功(角色:{user_role})，回复长度: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"[{self.name}] LLM调用失败: {e}")
            return self.get_fallback_response(user_input)
    
    def get_system_prompt(self) -> str:
        """获取智能体专业系统提示词（子类重写）"""
        return f"""你是{self.name}，{self.description}。
你的性格特点是：{self.personality}。
你的专业能力包括：{', '.join(self.capabilities)}。

请用温和、专业、易懂的语言回答老年用户的问题。
回答要简洁明了，重点突出，适合老年人阅读。
如遇紧急情况，请提醒用户及时就医。"""
    
    def get_role_style_prompt(self, user_role: str) -> str:
        """
        根据用户角色返回回复风格要求
        
        - elderly: 简洁易懂，大字体友好
        - children: 全面详细，情况讲清楚
        - community: 大局观，抓重点，专业术语
        """
        style_prompts = {
            "elderly": """
【回复风格要求 - 老年人模式】
1. 语言简洁易懂，避免专业术语
2. 句子简短，每句不超过20字
3. 使用口语化表达，像家人说话
4. 重点内容用【】标注
5. 总字数控制在150字以内
6. 使用适量emoji增加亲和力
7. 如有数值，直接给出结论（高/正常/低）
8. 给出1-2条最重要的建议即可""",
            
            "children": """
【回复风格要求 - 子女模式】
1. 全面详细，把情况讲清楚
2. 包含数据解读、风险分析、建议措施
3. 使用结构化格式（分段、编号）
4. 说明为什么（原因）和怎么办（措施）
5. 提供具体的监测指标和预警信号
6. 总字数300-500字
7. 可使用适度专业术语，但要解释
8. 列出需要子女关注和协助的事项
9. 提供就医建议和复诊提醒""",
            
            "community": """
【回复风格要求 - 社区工作者模式】
1. 大局观，抓重点，突出关键信息
2. 使用专业术语，便于记录归档
3. 按照"评估-风险-建议-随访"结构
4. 标注风险等级（低/中/高危）
5. 提供具体的干预措施和转介建议
6. 总字数200-300字
7. 包含随访时间和关注指标
8. 适合写入健康档案的格式"""
        }
        
        return style_prompts.get(user_role, style_prompts["elderly"])
    
    def get_role_adapted_prompt(self, user_role: str) -> str:
        """
        获取角色适配的完整系统提示词
        
        Args:
            user_role: 用户角色 (elderly/children/community)
        """
        base_prompt = self.get_system_prompt()
        style_prompt = self.get_role_style_prompt(user_role)
        
        return f"{base_prompt}\n\n{style_prompt}"
    
    def get_fallback_response(self, user_input: str) -> str:
        """获取备用回复（当LLM调用失败时）"""
        return f"抱歉，{self.name}暂时无法处理您的请求，请稍后再试。"
    
    def __str__(self):
        return f"{self.avatar} {self.name}({self.role.value})"
