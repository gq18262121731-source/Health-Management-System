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
        user_role: str = "elderly",
        elderly_id: str = None,
        use_rag: bool = True,
        session_id: str = None,
        use_tools: bool = True,
        intent: str = None,
        entities: Dict = None
    ) -> str:
        """
        调用讯飞星火大模型（集成RAG知识库检索 + 对话记忆 + 工具调用 + 多轮追问）
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词（智能体专业prompt）
            history: 对话历史
            user_role: 用户角色 (elderly/children/community)
            elderly_id: 老人ID（用于个性化RAG检索）
            use_rag: 是否使用RAG知识库增强
            session_id: 会话ID（用于对话记忆）
            use_tools: 是否使用工具调用
            intent: 识别的意图（用于多轮追问）
            entities: 提取的实体（用于多轮追问）
            
        Returns:
            大模型回复
        """
        try:
            from services.spark_service import spark_service
            
            # 根据用户角色生成适配的系统提示词
            if system_prompt is None:
                system_prompt = self.get_role_adapted_prompt(user_role)
            
            # ========== 对话记忆增强 ==========
            if session_id:
                memory_context = self._get_memory_context(session_id, user_input)
                if memory_context:
                    system_prompt = f"{system_prompt}\n\n{memory_context}"
                    logger.info(f"[{self.name}] 对话记忆已注入")
                
                # 获取历史对话（如果没有传入history）
                if history is None:
                    history = self._get_chat_history(session_id)
            
            # ========== 工具调用增强 ==========
            tool_context = ""
            if use_tools:
                tool_context = self._execute_tools_if_needed(user_input, session_id)
                if tool_context:
                    system_prompt = f"{system_prompt}\n\n{tool_context}"
                    logger.info(f"[{self.name}] 工具调用结果已注入")
            
            # ========== 多轮追问增强 ==========
            follow_up_prompt = ""
            if intent:
                follow_up_prompt = self._get_follow_up_prompt(user_input, intent, entities or {}, session_id)
                if follow_up_prompt:
                    system_prompt = f"{system_prompt}\n\n{follow_up_prompt}"
                    logger.info(f"[{self.name}] 追问提示已注入")
            
            # ========== RAG 知识库检索增强 ==========
            if use_rag:
                rag_context = self._retrieve_rag_context(user_input, elderly_id)
                if rag_context:
                    system_prompt = f"{system_prompt}\n\n{rag_context}"
                    logger.info(f"[{self.name}] RAG知识库已注入")
            
            response = spark_service.chat(
                user_input=user_input,
                system_prompt=system_prompt,
                history=history,
                temperature=0.7,
                max_tokens=2048
            )
            
            # ========== 回答质量检查 ==========
            response = self._check_response_quality(response, {
                "user_input": user_input,
                "intent": intent or ""
            })
            
            # ========== 保存对话到记忆 ==========
            if session_id:
                self._save_to_memory(session_id, user_input, response)
            
            logger.info(f"[{self.name}] LLM调用成功(角色:{user_role}, RAG:{use_rag}, 工具:{bool(tool_context)}, 追问:{bool(follow_up_prompt)}, 记忆:{bool(session_id)})，回复长度: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"[{self.name}] LLM调用失败: {e}")
            return self.get_fallback_response(user_input)
    
    def _get_follow_up_prompt(self, user_input: str, intent: str, entities: Dict, session_id: str = None) -> str:
        """
        获取多轮追问提示
        
        Args:
            user_input: 用户输入
            intent: 识别的意图
            entities: 提取的实体
            session_id: 会话ID
            
        Returns:
            追问提示词
        """
        try:
            from services.agents.follow_up import follow_up_manager
            
            should_ask, prompt = follow_up_manager.should_follow_up(
                user_input=user_input,
                intent=intent,
                entities=entities,
                session_id=session_id
            )
            
            return prompt if should_ask else ""
        except Exception as e:
            logger.debug(f"[{self.name}] 追问检查失败: {e}")
            return ""
    
    def _check_response_quality(self, response: str, context: Dict = None) -> str:
        """
        检查回答质量，确保安全性
        
        Args:
            response: AI的回答
            context: 上下文信息
            
        Returns:
            检查/修改后的回答
        """
        try:
            from services.agents.response_checker import response_checker
            
            result = response_checker.check(response, context)
            
            if not result.passed:
                logger.warning(f"[{self.name}] 回答质量检查未通过: {result.issues}")
            
            # 返回修改后的回答（添加了安全提醒等）
            return result.modified_response
        except Exception as e:
            logger.debug(f"[{self.name}] 质量检查失败: {e}")
            return response
    
    def _execute_tools_if_needed(self, user_input: str, session_id: str = None) -> str:
        """
        根据用户输入判断是否需要调用工具
        
        Args:
            user_input: 用户输入
            session_id: 会话ID
            
        Returns:
            工具调用结果上下文
        """
        try:
            from services.agents.agent_tools import agent_tools
            
            # 判断是否需要查询健康数据
            tool_triggers = {
                "query_health_records": ["最近血压", "血压记录", "血糖记录", "健康数据", "最近的数据", "查一下"],
                "query_health_trend": ["血压趋势", "变化趋势", "这段时间", "最近怎么样"],
                "query_recent_alerts": ["预警", "警报", "异常", "有什么问题"],
                "query_medications": ["吃什么药", "用药", "药物", "提醒吃药"],
            }
            
            results = []
            for tool_name, triggers in tool_triggers.items():
                if any(t in user_input for t in triggers):
                    result = agent_tools.call(tool_name, user_id=session_id)
                    if result.success:
                        results.append(f"【{tool_name}查询结果】\n{result.to_context()}")
            
            if results:
                return "【用户健康数据】\n以下是从系统中查询到的用户健康数据，请基于这些数据回答：\n\n" + "\n\n".join(results)
            
            return ""
        except Exception as e:
            logger.debug(f"[{self.name}] 工具调用失败: {e}")
            return ""
    
    def _get_memory_context(self, session_id: str, user_input: str) -> str:
        """
        获取对话记忆上下文
        
        Args:
            session_id: 会话ID
            user_input: 当前用户输入
            
        Returns:
            记忆上下文字符串
        """
        try:
            from services.conversation_memory import conversation_memory
            
            context = conversation_memory.get_context_summary(session_id)
            if context:
                return f"【用户记忆档案】\n{context}\n\n请根据以上用户信息，提供个性化的回答。"
            return ""
        except Exception as e:
            logger.debug(f"[{self.name}] 获取记忆失败: {e}")
            return ""
    
    def _get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            对话历史列表
        """
        try:
            from services.conversation_memory import conversation_memory
            return conversation_memory.get_chat_history_for_llm(session_id, limit=5)
        except Exception as e:
            logger.debug(f"[{self.name}] 获取对话历史失败: {e}")
            return []
    
    def _save_to_memory(self, session_id: str, user_input: str, response: str):
        """
        保存对话到记忆
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            response: AI回复
        """
        try:
            from services.conversation_memory import conversation_memory
            
            # 保存用户消息
            conversation_memory.add_message(
                session_id=session_id,
                role="user",
                content=user_input,
                metadata={"agent": self.name}
            )
            
            # 保存AI回复
            conversation_memory.add_message(
                session_id=session_id,
                role="assistant",
                content=response,
                metadata={"agent": self.name}
            )
        except Exception as e:
            logger.debug(f"[{self.name}] 保存记忆失败: {e}")
    
    def _retrieve_rag_context(self, user_input: str, elderly_id: str = None) -> str:
        """
        从RAG知识库检索相关内容（优先使用LangChain版本）
        
        Args:
            user_input: 用户输入
            elderly_id: 老人ID（可选，用于个性化检索）
            
        Returns:
            RAG上下文字符串，如果无结果返回空字符串
        """
        # 优先尝试 LangChain 知识库
        try:
            from services.knowledge_base_langchain import langchain_knowledge_base
            
            if langchain_knowledge_base and langchain_knowledge_base.vectorstore:
                context = langchain_knowledge_base.search_with_context(user_input, top_k=3)
                if context:
                    logger.debug(f"[{self.name}] 使用 LangChain RAG")
                    return context
        except Exception as e:
            logger.debug(f"[{self.name}] LangChain RAG 失败，回退到原版: {e}")
        
        # 回退到原版知识库
        try:
            from services.knowledge_base import knowledge_base
            
            if knowledge_base is None:
                return ""
            
            # 检索相关知识
            search_results = knowledge_base.search(
                query=user_input,
                top_k=3,
                elderly_id=elderly_id
            )
            
            if not search_results:
                return ""
            
            # 构建RAG上下文
            rag_parts = ["【RAG知识库参考】"]
            rag_parts.append("以下是从医学知识库中检索到的相关内容，请参考回答：")
            rag_parts.append("")
            
            for i, result in enumerate(search_results, 1):
                content = result.get('content', '')[:400]  # 限制长度
                title = result.get('title', f'知识{i}')
                category = result.get('category', '')
                score = result.get('score', 0)
                
                rag_parts.append(f"📚 {i}. 【{category}】{title}")
                rag_parts.append(f"   {content}")
                rag_parts.append(f"   (相关度: {score:.2f})")
                rag_parts.append("")
            
            rag_parts.append("请基于以上知识库内容，结合你的专业知识回答用户问题。")
            rag_parts.append("如果知识库内容与问题不相关，可以忽略。")
            
            logger.info(f"[{self.name}] RAG检索到 {len(search_results)} 条相关知识")
            return "\n".join(rag_parts)
            
        except ImportError:
            logger.debug(f"[{self.name}] 知识库模块未加载，跳过RAG")
            return ""
        except Exception as e:
            logger.warning(f"[{self.name}] RAG检索失败: {e}")
            return ""
    
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
