"""
多智能体数字人系统
=================

本模块实现了一个多智能体协作系统，用于健康管理和用户交互。

智能体角色：
- HealthButler（健康管家）：主要交互入口，亲切友好的数字人
- ChronicDiseaseExpert（慢病专家）：专业的慢病风险分析和建议
- LifestyleCoach（生活方式教练）：运动、睡眠、饮食指导
- EmotionalCare（心理关怀师）：情感支持和心理疏导
- AgentCoordinator（智能体协调器）：协调多智能体协作

使用示例：
---------
```python
from agents import MultiAgentSystem

# 创建多智能体系统
system = MultiAgentSystem(user_id="USER001")

# 与数字人对话
response = system.chat("我最近血压有点高，该怎么办？")
print(response)

# 获取健康报告
report = system.get_health_report()
```
"""

from .base_agent import BaseAgent, AgentMessage, AgentMemory
from .health_butler import HealthButlerAgent
from .chronic_disease_expert import ChronicDiseaseExpertAgent
from .lifestyle_coach import LifestyleCoachAgent
from .emotional_care import EmotionalCareAgent
from .agent_coordinator import AgentCoordinator
from .multi_agent_system import MultiAgentSystem

__all__ = [
    'BaseAgent',
    'AgentMessage',
    'AgentMemory',
    'HealthButlerAgent',
    'ChronicDiseaseExpertAgent',
    'LifestyleCoachAgent',
    'EmotionalCareAgent',
    'AgentCoordinator',
    'MultiAgentSystem',
]
