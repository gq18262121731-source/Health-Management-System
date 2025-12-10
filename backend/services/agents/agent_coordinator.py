"""
智能体协调器
============

负责协调多个智能体之间的协作，路由消息，整合响应。
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    智能体协调器
    
    职责：
    - 管理所有注册的智能体
    - 根据消息内容路由到合适的智能体
    - 协调多智能体协作
    - 整合多个智能体的响应
    """
    
    def __init__(self):
        self.agents: Dict[AgentRole, BaseAgent] = {}
        self.default_agent: Optional[AgentRole] = None
        self.conversation_history: List[AgentMessage] = []
        
    def register_agent(self, agent: BaseAgent, is_default: bool = False):
        """注册智能体"""
        self.agents[agent.role] = agent
        if is_default:
            self.default_agent = agent.role
        logger.info(f"注册智能体: {agent}")
    
    def get_agent(self, role: AgentRole) -> Optional[BaseAgent]:
        """获取指定角色的智能体"""
        return self.agents.get(role)
    
    def route_message(
        self, 
        message: AgentMessage, 
        context: Dict = None
    ) -> Tuple[BaseAgent, float]:
        """
        路由消息到最合适的智能体
        
        基于置信度评分机制自动选择
        
        Returns:
            (最合适的智能体, 置信度)
        """
        context = context or {}
        best_agent = None
        best_confidence = 0.0
        
        # 遍历所有智能体，计算处理置信度
        for role, agent in self.agents.items():
            if agent.is_active:
                confidence = agent.can_handle(message, context)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_agent = agent
        
        # 如果没有找到合适的智能体，使用默认智能体
        if best_agent is None and self.default_agent:
            best_agent = self.agents.get(self.default_agent)
            best_confidence = 0.5
        
        return best_agent, best_confidence
    
    def process_message(
        self,
        user_input: str,
        memory: AgentMemory,
        context: Dict = None,
        user_role: str = "elderly",
        session_id: str = None
    ) -> AgentMessage:
        """
        处理用户消息（单智能体模式，支持角色适配 + 对话记忆）
        """
        context = context or {}
        
        # 创建用户消息
        user_message = AgentMessage(
            type=MessageType.USER_INPUT,
            content=user_input,
            metadata={"timestamp": datetime.now().isoformat(), "user_role": user_role}
        )
        
        # 记录用户消息
        memory.add_message(user_message)
        
        # 路由到合适的智能体
        agent, confidence = self.route_message(user_message, context)
        
        if agent is None:
            return AgentMessage(
                type=MessageType.SYSTEM_INFO,
                content="抱歉，我暂时无法处理您的请求。",
                emotion=EmotionState.NEUTRAL
            )
        
        # 智能体处理消息（传递用户角色和会话ID）
        response = agent.process(user_message, memory, user_role=user_role, session_id=session_id)
        
        # 添加处理信息
        response.metadata["processed_by"] = agent.role.value
        response.metadata["agent_name"] = agent.name
        response.metadata["confidence"] = confidence
        response.metadata["user_role"] = user_role
        
        # 记录响应
        memory.add_message(response)
        
        return response
    
    def multi_agent_process(
        self,
        user_input: str,
        memory: AgentMemory,
        agent_roles: List[AgentRole] = None,
        confidence_threshold: float = 0.6,
        user_role: str = "elderly",
        session_id: str = None
    ) -> List[AgentMessage]:
        """
        多智能体协作处理（支持角色适配 + 对话记忆）
        
        让多个智能体同时处理消息，收集所有响应
        """
        user_message = AgentMessage(
            type=MessageType.USER_INPUT,
            content=user_input,
            metadata={"user_role": user_role}
        )
        
        responses = []
        
        if agent_roles:
            # 使用指定的智能体
            for role in agent_roles:
                agent = self.agents.get(role)
                if agent and agent.is_active:
                    response = agent.process(user_message, memory, user_role=user_role, session_id=session_id)
                    response.metadata["processed_by"] = agent.role.value
                    response.metadata["agent_name"] = agent.name
                    responses.append(response)
        else:
            # 自动选择相关的智能体（置信度 >= threshold）
            for role, agent in self.agents.items():
                if agent.is_active:
                    confidence = agent.can_handle(user_message, {})
                    if confidence >= confidence_threshold:
                        response = agent.process(user_message, memory, user_role=user_role, session_id=session_id)
                        response.metadata["processed_by"] = agent.role.value
                        response.metadata["agent_name"] = agent.name
                        response.metadata["confidence"] = confidence
                        responses.append(response)
        
        return responses
    
    def synthesize_responses(
        self,
        responses: List[AgentMessage],
        strategy: str = "merge"
    ) -> str:
        """
        整合多个智能体的响应
        
        Args:
            responses: 响应列表
            strategy: 整合策略 (merge, select_best, all)
        """
        if not responses:
            return "暂无响应"
        
        if strategy == "select_best":
            # 选择置信度最高的响应
            best_response = max(
                responses, 
                key=lambda r: r.metadata.get("confidence", 0)
            )
            return best_response.content
        
        elif strategy == "merge":
            # 合并所有响应
            merged = []
            for response in responses:
                agent_name = response.metadata.get("agent_name", "专家")
                merged.append(f"【{agent_name}】\n{response.content}")
            return "\n\n".join(merged)
        
        elif strategy == "all":
            return "\n\n".join([r.content for r in responses])
        
        return responses[0].content if responses else ""
    
    def get_all_agents_info(self) -> List[Dict]:
        """获取所有智能体信息"""
        return [
            {
                "name": agent.name,
                "role": agent.role.value,
                "avatar": agent.avatar,
                "description": agent.description,
                "is_active": agent.is_active,
                "capabilities": agent.capabilities
            }
            for agent in self.agents.values()
        ]
