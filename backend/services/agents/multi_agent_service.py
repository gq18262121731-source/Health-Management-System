"""
多智能体服务
============

整合多个智能体，提供统一的接口供AI服务调用。
支持单Agent模式和多Agent协作模式。
包含意图识别功能。
"""

import logging
import json
from typing import Dict, List, Optional, Any

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None

from config.settings import settings
from .base_agent import AgentRole, AgentMessage, AgentMemory, MessageType
from .agent_coordinator import AgentCoordinator
from .health_butler import HealthButlerAgent
from .chronic_disease_expert import ChronicDiseaseExpertAgent
from .lifestyle_coach import LifestyleCoachAgent
from .emotional_care import EmotionalCareAgent
from .intent_recognizer import intent_recognizer, IntentType
from .agent_tools import agent_tools

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
        self.conversation_states: Dict[str, List[Dict]] = {}  # 多轮对话状态（内存备用）
        
        # Redis 连接（用于持久化对话状态）
        self.redis_client = None
        self.redis_ttl = 86400  # 1天过期
        if HAS_REDIS:
            try:
                redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()  # 测试连接
                logger.info(f"Redis 连接成功，对话状态将持久化存储（TTL: {self.redis_ttl}秒）")
            except Exception as e:
                logger.warning(f"Redis 连接失败: {e}，将使用内存存储")
                self.redis_client = None
        
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
    
    def _get_conversation_key(self, user_id: str, session_id: str = None) -> str:
        """生成对话状态的存储键"""
        return f"conv:{user_id}:{session_id or 'default'}"
    
    def _get_conversation_state(self, user_id: str, session_id: str = None) -> List[Dict]:
        """获取对话状态（优先从 Redis 读取）"""
        key = self._get_conversation_key(user_id, session_id)
        
        # 优先从 Redis 读取
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis 读取失败: {e}")
        
        # 降级到内存
        return self.conversation_states.get(key, [])
    
    def _save_conversation_state(self, user_id: str, session_id: str, state: List[Dict]):
        """保存对话状态（优先存入 Redis）"""
        key = self._get_conversation_key(user_id, session_id)
        
        # 优先存入 Redis
        if self.redis_client:
            try:
                self.redis_client.setex(key, self.redis_ttl, json.dumps(state, ensure_ascii=False))
                return
            except Exception as e:
                logger.warning(f"Redis 写入失败: {e}")
        
        # 降级到内存
        self.conversation_states[key] = state
    
    def _clear_conversation_state(self, user_id: str, session_id: str = None):
        """清除对话状态"""
        key = self._get_conversation_key(user_id, session_id)
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis 删除失败: {e}")
        
        if key in self.conversation_states:
            del self.conversation_states[key]
    
    def process(
        self,
        user_input: str,
        user_id: str = "default",
        user_role: str = "elderly",
        health_data: Optional[Dict[str, Any]] = None,
        mode: str = "auto",
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        处理用户输入（含意图识别 + 角色适配 + 对话记忆）
        
        Args:
            user_input: 用户输入文本
            user_id: 用户ID
            user_role: 用户角色 ("elderly": 老年人, "children": 子女, "community": 社区)
            health_data: 用户健康数据
            mode: 处理模式 ("auto": 自动, "single": 单智能体, "multi": 多智能体协作)
            session_id: 会话ID（用于对话记忆，不传则使用user_id）
        
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
        
        # 获取用户记忆
        memory = self.get_memory(user_id)
        
        # ========== 多轮对话处理（反问逻辑）==========
        conversation_history = self._get_conversation_state(user_id, session_id)
        
        # 使用 agent_tools 处理多轮对话
        conv_result = agent_tools.process_conversation(user_input, conversation_history)
        
        logger.info(f"多轮对话分析: action={conv_result['action']}, topic={conv_result.get('topic')}")
        
        # 如果是反问或工具调用，直接返回结果
        if conv_result["action"] in ["ask_for_data", "call_tool", "analyze_data"]:
            # 保存对话状态（使用 Redis 持久化）
            self._save_conversation_state(user_id, session_id, conversation_history + [conv_result])
            
            # 保存到智能体记忆
            memory.add_message(AgentMessage(
                type=MessageType.USER_INPUT,
                content=user_input
            ))
            memory.add_message(AgentMessage(
                type=MessageType.AGENT_RESPONSE,
                content=conv_result["response"]
            ))
            
            # 保存健康上下文
            if conv_result.get("tool_result"):
                memory.set_context("last_health_query", {
                    "topic": conv_result.get("topic"),
                    "tool_called": conv_result.get("tool_called"),
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                })
            
            logger.info(f"多轮对话处理: action={conv_result['action']}, topic={conv_result.get('topic')}")
            
            return {
                "response": conv_result["response"],
                "agent": "健康管家",
                "confidence": 1.0,
                "mode": "conversation",
                "intent": {"type": conv_result["action"], "topic": conv_result.get("topic")},
                "user_role": user_role,
                "tool_called": conv_result.get("tool_called", False)
            }
        
        # 清除对话状态（新话题）
        self._clear_conversation_state(user_id, session_id)
        
        # ========== 智能体切换指令检测 ==========
        switch_result = self._check_agent_switch(user_input, user_id)
        if switch_result:
            return switch_result
        
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
        
        # 使用 session_id 或 user_id 作为会话标识
        effective_session_id = session_id or user_id
        
        # 设置上下文
        if health_data:
            memory.set_context("health_data", health_data)
        memory.set_context("intent", intent_result.to_dict())
        memory.set_context("entities", intent_result.entities)
        memory.set_context("user_role", user_role)  # 保存用户角色
        memory.set_context("session_id", effective_session_id)  # 保存会话ID
        
        # ========== 自动选择处理模式 ==========
        if mode == "auto":
            mode = "multi" if intent_result.requires_multi_agent else "single"
        
        if mode == "multi":
            result = self._multi_agent_process(user_input, memory, user_role, effective_session_id)
        else:
            result = self._single_agent_process(user_input, memory, user_role, effective_session_id)
        
        # 添加意图和角色信息到返回结果
        result["intent"] = intent_result.to_dict()
        result["user_role"] = user_role
        return result
    
    def _single_agent_process(
        self,
        user_input: str,
        memory: AgentMemory,
        user_role: str = "elderly",
        session_id: str = None
    ) -> Dict[str, Any]:
        """单智能体处理模式"""
        response = self.coordinator.process_message(
            user_input, memory, user_role=user_role, session_id=session_id
        )
        
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
        user_role: str = "elderly",
        session_id: str = None
    ) -> Dict[str, Any]:
        """多智能体协作模式"""
        responses = self.coordinator.multi_agent_process(
            user_input, 
            memory,
            confidence_threshold=0.6,
            user_role=user_role,
            session_id=session_id
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
    
    def _check_agent_switch(self, user_input: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        检测用户是否想切换智能体
        
        支持的指令：
        - "转到慢病专家" / "切换到慢病专家" / "我要找慢病专家"
        - "转到生活教练" / "帮我转到生活教练"
        - "转到心理关怀师" / "我想和心理关怀师聊聊"
        - "转到健康管家" / "回到健康管家"
        """
        import re
        
        # 智能体名称映射
        agent_mapping = {
            "慢病专家": ("慢病专家", ChronicDiseaseExpertAgent),
            "慢病": ("慢病专家", ChronicDiseaseExpertAgent),
            "生活教练": ("生活教练", LifestyleCoachAgent),
            "生活": ("生活教练", LifestyleCoachAgent),
            "心理关怀师": ("心理关怀师", EmotionalCareAgent),
            "心理关怀": ("心理关怀师", EmotionalCareAgent),
            "心理": ("心理关怀师", EmotionalCareAgent),
            "情感关怀": ("心理关怀师", EmotionalCareAgent),
            "健康管家": ("健康管家", HealthButlerAgent),
            "管家": ("健康管家", HealthButlerAgent),
        }
        
        # 切换指令模式
        switch_patterns = [
            r"(?:转到|切换到|帮我转到|我要找|我想找|找|呼叫|叫|换成|换到|我想和|让我和)(.+?)(?:聊聊|聊天|说话|$)",
            r"(.+?)(?:在吗|来一下|帮帮我)",
        ]
        
        for pattern in switch_patterns:
            match = re.search(pattern, user_input)
            if match:
                target = match.group(1).strip()
                for key, (agent_name, agent_class) in agent_mapping.items():
                    if key in target:
                        # 找到目标智能体
                        logger.info(f"用户请求切换到智能体: {agent_name}")
                        
                        # 设置当前活跃智能体
                        memory = self.get_memory(user_id)
                        memory.set_context("active_agent", agent_name)
                        
                        # 获取智能体实例（通过名称查找）
                        agent = None
                        for role, ag in self.coordinator.agents.items():
                            if ag.name == agent_name:
                                agent = ag
                                break
                        
                        if agent:
                            # 生成欢迎语
                            welcome_messages = {
                                "慢病专家": "🩺 您好！我是慢病专家，专注于高血压、糖尿病、心脏病等慢性疾病的管理。\n\n请问您有什么慢病相关的问题想咨询？比如：\n• 血压/血糖数值解读\n• 用药注意事项\n• 慢病日常管理",
                                "生活教练": "🥗 您好！我是生活教练，专注于健康饮食、运动锻炼和睡眠改善。\n\n请问您想了解哪方面的内容？比如：\n• 每日饮食搭配\n• 适合的运动方式\n• 改善睡眠质量",
                                "心理关怀师": "💜 您好！我是心理关怀师，随时倾听您的心声。\n\n无论是焦虑、压力还是情绪低落，都可以和我聊聊。\n我会陪伴您，一起找到让心情变好的方法~",
                                "健康管家": "🏠 您好！我是健康管家，您的全能健康助手。\n\n我可以帮您：\n• 解读健康数据\n• 提供日常健康建议\n• 转接专业智能体\n\n请问有什么可以帮您的？"
                            }
                            
                            return {
                                "response": welcome_messages.get(agent_name, f"已切换到{agent_name}，请问有什么可以帮您的？"),
                                "agent": agent_name,
                                "confidence": 1.0,
                                "mode": "switch",
                                "intent": {"type": "agent_switch", "target": agent_name},
                                "user_role": "elderly"
                            }
        
        return None


# 单例实例
multi_agent_service = MultiAgentService()
