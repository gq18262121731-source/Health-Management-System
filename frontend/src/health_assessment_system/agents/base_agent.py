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
import json
import uuid


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
    TASK_REQUEST = "task_request"        # 任务请求
    TASK_RESULT = "task_result"          # 任务结果


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
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            type=MessageType(data.get("type", "agent_response")),
            role=AgentRole(data.get("role", "health_butler")),
            content=data.get("content", ""),
            emotion=EmotionState(data.get("emotion", "neutral")),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


@dataclass
class AgentMemory:
    """智能体记忆"""
    user_id: str
    short_term: List[AgentMessage] = field(default_factory=list)  # 短期记忆（当前对话）
    long_term: Dict[str, Any] = field(default_factory=dict)       # 长期记忆（用户画像）
    context: Dict[str, Any] = field(default_factory=dict)          # 上下文信息
    
    def add_message(self, message: AgentMessage):
        """添加消息到短期记忆"""
        self.short_term.append(message)
        # 保留最近20条消息
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def get_recent_context(self, n: int = 5) -> List[AgentMessage]:
        """获取最近n条消息"""
        return self.short_term[-n:] if self.short_term else []
    
    def update_user_profile(self, key: str, value: Any):
        """更新用户画像"""
        self.long_term[key] = value
    
    def get_user_profile(self, key: str, default: Any = None) -> Any:
        """获取用户画像信息"""
        return self.long_term.get(key, default)
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self.context.get(key, default)
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term.clear()
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "short_term": [m.to_dict() for m in self.short_term],
            "long_term": self.long_term,
            "context": self.context
        }


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
        """
        处理消息并生成响应
        
        Args:
            message: 输入消息
            memory: 智能体记忆
            
        Returns:
            响应消息
        """
        pass
    
    @abstractmethod
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """
        判断是否能处理该消息，返回置信度(0-1)
        
        Args:
            message: 输入消息
            context: 上下文信息
            
        Returns:
            处理置信度，越高表示越适合处理
        """
        pass
    
    def think(self, message: AgentMessage, memory: AgentMemory) -> str:
        """
        思考过程（可选实现）
        
        Args:
            message: 输入消息
            memory: 智能体记忆
            
        Returns:
            思考过程描述
        """
        return f"[{self.name}] 正在分析用户需求..."
    
    def get_greeting(self, user_name: str = "您") -> str:
        """获取问候语"""
        return f"您好，{user_name}！我是{self.name}，{self.description}"
    
    def create_response(
        self,
        content: str,
        emotion: EmotionState = EmotionState.NEUTRAL,
        metadata: Dict = None
    ) -> AgentMessage:
        """创建响应消息"""
        return AgentMessage(
            type=MessageType.AGENT_RESPONSE,
            role=self.role,
            content=content,
            emotion=emotion,
            metadata=metadata or {}
        )
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 健康相关关键词库
        health_keywords = {
            # 症状
            "血压", "血糖", "血脂", "心率", "头晕", "头痛", "胸闷", 
            "乏力", "失眠", "疲劳", "食欲", "体重",
            # 疾病
            "高血压", "糖尿病", "高血脂", "心脏病", "冠心病",
            # 生活方式
            "运动", "锻炼", "步数", "睡眠", "饮食", "吃饭", "喝水",
            # 情绪
            "焦虑", "担心", "害怕", "紧张", "压力", "心情", "情绪",
            # 药物
            "吃药", "服药", "药物", "降压药", "降糖药",
            # 检查
            "检查", "体检", "复查", "化验",
            # 其他
            "建议", "怎么办", "注意", "帮助"
        }
        
        found_keywords = []
        for keyword in health_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def detect_intent(self, text: str) -> str:
        """检测用户意图"""
        intents = {
            "health_query": ["怎么样", "好不好", "正常吗", "高了", "低了", "偏高", "偏低"],
            "advice_request": ["怎么办", "该如何", "建议", "应该", "需要", "要不要"],
            "symptom_report": ["不舒服", "难受", "疼", "痛", "头晕", "胸闷", "乏力"],
            "lifestyle_query": ["运动", "睡眠", "饮食", "锻炼", "吃什么", "怎么吃"],
            "emotional_support": ["担心", "害怕", "焦虑", "紧张", "压力", "心情不好"],
            "greeting": ["你好", "早上好", "下午好", "晚上好", "在吗", "您好"],
            "report_request": ["报告", "评估", "分析", "总结", "看看"],
            "medication": ["吃药", "服药", "药物", "降压药", "忘吃"]
        }
        
        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        
        return "general"
    
    def __str__(self) -> str:
        return f"{self.avatar} {self.name}（{self.role.value}）"
    
    def __repr__(self) -> str:
        return f"<Agent: {self.name}, role={self.role.value}>"
