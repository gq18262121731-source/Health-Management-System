"""
智能体协调器
============

负责协调多个智能体之间的协作，路由消息，整合响应。
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


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
        """
        注册智能体
        
        Args:
            agent: 要注册的智能体
            is_default: 是否设为默认智能体
        """
        self.agents[agent.role] = agent
        if is_default:
            self.default_agent = agent.role
        print(f"✓ 注册智能体: {agent}")
    
    def unregister_agent(self, role: AgentRole):
        """注销智能体"""
        if role in self.agents:
            del self.agents[role]
            if self.default_agent == role:
                self.default_agent = None
    
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
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            (最合适的智能体, 置信度)
        """
        context = context or {}
        best_agent = None
        best_confidence = 0.0
        
        # 遍历所有智能体，计算处理置信度
        confidence_scores = []
        for role, agent in self.agents.items():
            if agent.is_active:
                confidence = agent.can_handle(message, context)
                confidence_scores.append((agent, confidence))
                
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
        context: Dict = None
    ) -> AgentMessage:
        """
        处理用户消息
        
        Args:
            user_input: 用户输入文本
            memory: 智能体记忆
            context: 上下文信息
            
        Returns:
            智能体响应消息
        """
        context = context or {}
        
        # 创建用户消息
        user_message = AgentMessage(
            type=MessageType.USER_INPUT,
            content=user_input,
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        # 记录用户消息
        memory.add_message(user_message)
        self.conversation_history.append(user_message)
        
        # 路由到合适的智能体
        agent, confidence = self.route_message(user_message, context)
        
        if agent is None:
            return AgentMessage(
                type=MessageType.SYSTEM_INFO,
                content="抱歉，我暂时无法处理您的请求。",
                emotion=EmotionState.NEUTRAL
            )
        
        # 智能体处理消息
        response = agent.process(user_message, memory)
        
        # 添加处理信息
        response.metadata["processed_by"] = agent.role.value
        response.metadata["confidence"] = confidence
        
        # 记录响应
        memory.add_message(response)
        self.conversation_history.append(response)
        
        return response
    
    def multi_agent_process(
        self,
        user_input: str,
        memory: AgentMemory,
        agent_roles: List[AgentRole] = None
    ) -> List[AgentMessage]:
        """
        多智能体协作处理
        
        让多个智能体同时处理消息，收集所有响应
        
        Args:
            user_input: 用户输入
            memory: 智能体记忆
            agent_roles: 指定参与的智能体角色，None表示自动选择
            
        Returns:
            各智能体的响应列表
        """
        user_message = AgentMessage(
            type=MessageType.USER_INPUT,
            content=user_input
        )
        
        responses = []
        
        if agent_roles:
            # 使用指定的智能体
            for role in agent_roles:
                agent = self.agents.get(role)
                if agent and agent.is_active:
                    response = agent.process(user_message, memory)
                    responses.append(response)
        else:
            # 自动选择相关的智能体
            for role, agent in self.agents.items():
                if agent.is_active:
                    confidence = agent.can_handle(user_message, {})
                    if confidence >= 0.6:  # 只选择置信度较高的智能体
                        response = agent.process(user_message, memory)
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
            
        Returns:
            整合后的响应文本
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
                agent_name = response.metadata.get("processed_by", "unknown")
                merged.append(f"**{self._get_agent_name(agent_name)}的建议：**\n{response.content}")
            return "\n\n---\n\n".join(merged)
        
        elif strategy == "all":
            # 返回所有响应（用于调试）
            return "\n\n".join([r.content for r in responses])
        
        return responses[0].content if responses else ""
    
    def _get_agent_name(self, role_value: str) -> str:
        """根据角色值获取智能体名称"""
        role_names = {
            "health_butler": "健康管家",
            "chronic_expert": "慢病专家",
            "lifestyle_coach": "生活教练",
            "emotional_care": "心理关怀师"
        }
        return role_names.get(role_value, role_value)
    
    def get_agent_status(self) -> Dict[str, bool]:
        """获取所有智能体状态"""
        return {
            agent.name: agent.is_active 
            for agent in self.agents.values()
        }
    
    def set_agent_active(self, role: AgentRole, active: bool):
        """设置智能体活跃状态"""
        if role in self.agents:
            self.agents[role].is_active = active
    
    def get_conversation_summary(self) -> Dict:
        """获取对话摘要"""
        if not self.conversation_history:
            return {"total_messages": 0, "user_messages": 0, "agent_responses": 0}
        
        user_count = sum(
            1 for m in self.conversation_history 
            if m.type == MessageType.USER_INPUT
        )
        agent_count = sum(
            1 for m in self.conversation_history 
            if m.type == MessageType.AGENT_RESPONSE
        )
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_count,
            "agent_responses": agent_count
        }
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
    
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
