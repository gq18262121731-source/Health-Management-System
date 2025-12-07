"""
多智能体系统
============

整合健康管家、慢病专家、生活教练、心理关怀师等多个智能体，
通过协调器进行消息路由和响应整合。
"""

from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)
from .agent_coordinator import AgentCoordinator
from .health_butler import HealthButlerAgent
from .chronic_disease_expert import ChronicDiseaseExpertAgent
from .lifestyle_coach import LifestyleCoachAgent
from .emotional_care import EmotionalCareAgent
from .multi_agent_service import MultiAgentService
from .intent_recognizer import IntentRecognizer, IntentType, IntentResult, intent_recognizer

__all__ = [
    "BaseAgent",
    "AgentRole", 
    "AgentMessage",
    "AgentMemory",
    "MessageType",
    "EmotionState",
    "AgentCoordinator",
    "HealthButlerAgent",
    "ChronicDiseaseExpertAgent", 
    "LifestyleCoachAgent",
    "EmotionalCareAgent",
    "MultiAgentService",
    "IntentRecognizer",
    "IntentType",
    "IntentResult",
    "intent_recognizer"
]
