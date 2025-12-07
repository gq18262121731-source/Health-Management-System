"""
多智能体服务
============

整合多个智能体，提供统一的接口供AI服务调用。
支持单Agent模式和多Agent协作模式。
包含意图识别功能。
"""

import logging
from typing import Dict, List, Optional, Any

from .base_agent import AgentRole, AgentMessage, AgentMemory, MessageType
from .agent_coordinator import AgentCoordinator
from .health_butler import HealthButlerAgent
from .chronic_disease_expert import ChronicDiseaseExpertAgent
from .lifestyle_coach import LifestyleCoachAgent
from .emotional_care import EmotionalCareAgent
from .intent_recognizer import intent_recognizer, IntentType

logger = logging.getLogger(__name__)


class MultiAgentService:
    """
    多智能体服务
    
    整合健康管家、慢病专家、生活教练、心理关怀师等多个智能体，
    提供统一的对话接口。
    
    使用示例：
    ```python
    service = MultiAgentService()
    response = service.process("我最近血压有点高", user_id="USER001")
    ```
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.coordinator = AgentCoordinator()
        self.memories: Dict[str, AgentMemory] = {}  # 用户记忆缓存
        
        # 注册智能体
        self._register_agents()
        self._initialized = True
        
        logger.info(f"多智能体服务初始化完成，共注册 {len(self.coordinator.agents)} 个智能体")
    
    def _register_agents(self):
        """注册所有智能体"""
        # 健康管家（默认智能体）
        butler = HealthButlerAgent(name="健康管家")
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
    
    def get_memory(self, user_id: str) -> AgentMemory:
        """获取或创建用户记忆"""
        if user_id not in self.memories:
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]
    
    def process(
        self,
        user_input: str,
        user_id: str = "default",
        user_role: str = "elderly",
        health_data: Optional[Dict[str, Any]] = None,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        处理用户输入（含意图识别 + 角色适配）
        
        Args:
            user_input: 用户输入文本
            user_id: 用户ID
            user_role: 用户角色 ("elderly": 老年人, "children": 子女, "community": 社区)
            health_data: 用户健康数据
            mode: 处理模式 ("auto": 自动, "single": 单智能体, "multi": 多智能体协作)
        
        Returns:
            {
                "response": 响应文本,
                "agent": 处理的智能体名称,
                "confidence": 置信度,
                "mode": 处理模式,
                "intent": 识别的意图,
                "user_role": 用户角色
            }
        """
        if not user_input.strip():
            return {
                "response": "请问有什么可以帮您的吗？",
                "agent": "系统",
                "confidence": 1.0,
                "mode": mode,
                "intent": None,
                "user_role": user_role
            }
        
        # ========== 意图识别 ==========
        intent_result = intent_recognizer.recognize(user_input, use_llm=False)
        
        logger.info(f"意图识别: {intent_result.intent.value}, 置信度: {intent_result.confidence:.2f}, 角色: {user_role}")
        
        # 紧急情况特殊处理（根据角色调整提示）
        if intent_result.intent == IntentType.EMERGENCY:
            emergency_responses = {
                "elderly": "⚠️ 【紧急】请立即拨打120！或让家人陪您去医院！",
                "children": "⚠️ 检测到紧急情况！请立即：\n1. 拨打120急救电话\n2. 陪同老人前往最近医院急诊\n3. 准备好老人的病历和常用药物\n4. 保持老人情绪稳定",
                "community": "⚠️ 紧急预警｜风险等级：高危\n处置建议：立即启动急救流程，联系120，通知家属，做好转运准备。"
            }
            return {
                "response": emergency_responses.get(user_role, emergency_responses["elderly"]),
                "agent": "系统",
                "confidence": 1.0,
                "mode": "emergency",
                "intent": intent_result.to_dict(),
                "user_role": user_role
            }
        
        memory = self.get_memory(user_id)
        
        # 设置上下文
        if health_data:
            memory.set_context("health_data", health_data)
        memory.set_context("intent", intent_result.to_dict())
        memory.set_context("entities", intent_result.entities)
        memory.set_context("user_role", user_role)  # 保存用户角色
        
        # ========== 自动选择处理模式 ==========
        if mode == "auto":
            mode = "multi" if intent_result.requires_multi_agent else "single"
        
        if mode == "multi":
            result = self._multi_agent_process(user_input, memory, user_role)
        else:
            result = self._single_agent_process(user_input, memory, user_role)
        
        # 添加意图和角色信息到返回结果
        result["intent"] = intent_result.to_dict()
        result["user_role"] = user_role
        return result
    
    def _single_agent_process(
        self,
        user_input: str,
        memory: AgentMemory,
        user_role: str = "elderly"
    ) -> Dict[str, Any]:
        """单智能体处理模式"""
        response = self.coordinator.process_message(user_input, memory, user_role=user_role)
        
        return {
            "response": response.content,
            "agent": response.metadata.get("agent_name", "健康管家"),
            "confidence": response.metadata.get("confidence", 0.5),
            "mode": "single",
            "emotion": response.emotion.value
        }
    
    def _multi_agent_process(
        self,
        user_input: str,
        memory: AgentMemory,
        user_role: str = "elderly"
    ) -> Dict[str, Any]:
        """多智能体协作模式"""
        responses = self.coordinator.multi_agent_process(
            user_input, 
            memory,
            confidence_threshold=0.6,
            user_role=user_role
        )
        
        if not responses:
            # 没有找到合适的智能体，使用默认智能体
            return self._single_agent_process(user_input, memory, user_role)
        
        # 整合多个智能体的响应
        synthesized = self.coordinator.synthesize_responses(responses, strategy="merge")
        
        agents = [r.metadata.get("agent_name", "专家") for r in responses]
        
        return {
            "response": synthesized,
            "agent": ", ".join(agents),
            "confidence": max(r.metadata.get("confidence", 0) for r in responses),
            "mode": "multi",
            "agent_count": len(responses)
        }
    
    def get_agents_info(self) -> List[Dict]:
        """获取所有智能体信息"""
        return self.coordinator.get_all_agents_info()
    
    def should_use_multi_agent(self, user_input: str) -> bool:
        """
        判断是否应该使用多智能体模式
        
        复杂问题（涉及多个领域）建议使用多智能体模式
        """
        keywords_count = 0
        
        # 慢病关键词
        if any(kw in user_input for kw in ["血压", "血糖", "血脂", "糖尿病", "高血压"]):
            keywords_count += 1
        
        # 生活方式关键词
        if any(kw in user_input for kw in ["运动", "饮食", "睡眠", "锻炼"]):
            keywords_count += 1
        
        # 情绪关键词
        if any(kw in user_input for kw in ["担心", "焦虑", "害怕", "压力", "心情"]):
            keywords_count += 1
        
        # 涉及2个或以上领域，建议多智能体协作
        return keywords_count >= 2


# 单例实例
multi_agent_service = MultiAgentService()
