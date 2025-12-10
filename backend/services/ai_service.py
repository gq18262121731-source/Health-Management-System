"""AI健康助手服务 - 集成多智能体协作系统"""
import logging
import httpx
from typing import Optional, Dict, Any
from config.settings import settings

# 导入知识库（延迟导入，避免循环依赖）
try:
    from services.knowledge_base import knowledge_base
    HAS_KNOWLEDGE_BASE = True
except ImportError:
    HAS_KNOWLEDGE_BASE = False
    knowledge_base = None

# 导入多智能体系统
try:
    from services.agents.multi_agent_service import multi_agent_service
    HAS_MULTI_AGENT = True
except ImportError as e:
    HAS_MULTI_AGENT = False
    multi_agent_service = None
    logging.warning(f"多智能体系统加载失败: {e}")

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类，支持国内主流AI服务提供商"""
    
    def __init__(self):
        """初始化AI服务"""
        # 支持的AI服务提供商
        self.provider = getattr(settings, 'AI_PROVIDER', 'deepseek').lower()  # deepseek, zhipu, qwen
        self.api_key = None
        self.api_base = None
        
        # 根据提供商配置API
        if self.provider == 'deepseek':
            self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            self.api_base = getattr(settings, 'DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
            self.model = 'deepseek-chat'
        elif self.provider == 'zhipu':
            self.api_key = getattr(settings, 'ZHIPU_API_KEY', None)
            self.api_base = getattr(settings, 'ZHIPU_API_BASE', 'https://open.bigmodel.cn/api/paas/v4')
            self.model = 'glm-4'
        elif self.provider == 'qwen':
            self.api_key = getattr(settings, 'QWEN_API_KEY', None)
            self.api_base = getattr(settings, 'QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
            self.model = 'qwen-turbo'
        else:
            logger.warning(f"不支持的AI提供商: {self.provider}，将使用模拟模式")
            self.provider = None
        
        if not self.api_key and self.provider:
            logger.warning(f"{self.provider} API_KEY未配置，AI服务将使用模拟模式")
            self.provider = None
    
    def _build_system_prompt(self, user_role: str = "elderly", health_data: Optional[Dict[str, Any]] = None) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位专业的AI健康助手，专门为老年人提供健康咨询和建议。

你的职责：
1. 根据用户的健康数据和问题，提供专业、安全、易懂的健康建议
2. 解释健康数据指标的含义
3. 提供生活方式的改善建议
4. 识别紧急情况并建议及时就医
5. 用温和、耐心、易懂的语言与老年人交流

重要原则：
- 提供的建议必须安全、可行
- 不能替代专业医生的诊断
- 遇到紧急情况必须明确建议就医
- 用简单易懂的语言，避免过多专业术语
- 每次回答要简洁明了，重点突出

"""
        
        if health_data:
            health_summary = f"""
用户当前健康状态：
- 血压: {health_data.get('blood_pressure', '未知')}
- 心率: {health_data.get('heart_rate', '未知')}
- 体温: {health_data.get('temperature', '未知')}
- 血氧: {health_data.get('blood_oxygen', '未知')}
- 血糖: {health_data.get('blood_sugar', '未知')}
- 睡眠质量: {health_data.get('sleep_quality', '未知')}

"""
            base_prompt += health_summary
        
        return base_prompt
    
    async def consult(
        self,
        user_input: str,
        user_role: str = "elderly",
        elderly_id: Optional[str] = None,
        health_data: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[list] = None,
        use_knowledge_base: bool = True,
        use_multi_agent: bool = True
    ) -> Dict[str, Any]:
        """
        进行AI健康咨询 - 集成多智能体协作系统
        
        Args:
            user_input: 用户输入的问题
            user_role: 用户角色 (elderly/children/community)
            elderly_id: 老人ID
            health_data: 用户健康数据
            conversation_history: 对话历史记录
            use_knowledge_base: 是否使用知识库
            use_multi_agent: 是否使用多智能体系统
        
        Returns:
            包含 response 和 agent 的字典
        """
        # ========== 多智能体系统处理 ==========
        # 优先使用多智能体系统处理专业健康问题
        if use_multi_agent and HAS_MULTI_AGENT and multi_agent_service:
            try:
                # 判断是否需要多智能体协作
                use_multi_mode = multi_agent_service.should_use_multi_agent(user_input)
                mode = "multi" if use_multi_mode else "single"
                
                result = multi_agent_service.process(
                    user_input=user_input,
                    user_id=elderly_id or "default",
                    health_data=health_data,
                    mode=mode
                )
                
                agent_response = result.get("response", "")
                agent_name = result.get("agent", "健康管家")
                confidence = result.get("confidence", 0)
                
                # 如果多智能体置信度高(>=0.7)，直接返回其回复
                if confidence >= 0.7 and agent_response:
                    logger.info(f"多智能体处理成功: agent={agent_name}, confidence={confidence:.2f}, mode={mode}")
                    
                    return {
                        "response": agent_response,
                        "agent": agent_name,
                        "confidence": confidence,
                        "mode": mode
                    }
                
                # 置信度较低时，将多智能体回复作为参考，继续调用大模型增强
                logger.info(f"多智能体置信度较低({confidence:.2f})，将调用大模型增强回复")
                
            except Exception as e:
                logger.warning(f"多智能体处理失败: {e}，将使用大模型回复")
        
        # ========== 大模型 API 调用 ==========
        # 如果API密钥未配置，返回模拟回复
        if not self.provider or not self.api_key:
            return {"response": self._get_mock_response(user_input), "agent": "健康管家"}
        
        try:
            # RAG: 从知识库检索相关知识
            knowledge_context = ""
            if use_knowledge_base and HAS_KNOWLEDGE_BASE and knowledge_base:
                try:
                    search_results = knowledge_base.search(user_input, top_k=3, elderly_id=elderly_id)
                    if search_results:
                        knowledge_context = "\n\n【相关知识库内容】\n"
                        for i, result in enumerate(search_results, 1):
                            knowledge_context += f"\n{i}. {result.get('content', '')[:300]}...\n"
                        knowledge_context += "\n请基于以上知识库内容回答问题。\n"
                        logger.info(f"从知识库检索到 {len(search_results)} 条相关内容")
                except Exception as e:
                    logger.warning(f"知识库检索失败: {str(e)}")
            
            # 构建系统提示词（包含知识库上下文）
            system_prompt = self._build_system_prompt(user_role, health_data)
            if knowledge_context:
                system_prompt += knowledge_context
            
            # 添加elderly_id参数用于知识库检索
            if elderly_id:
                pass  # elderly_id已在知识库检索中使用
            
            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
            
            # 添加历史对话
            if conversation_history:
                for msg in conversation_history[-6:]:  # 只保留最近6条对话
                    role = msg.get("role", "user")
                    # 统一角色名称（OpenAI兼容格式）
                    if role == "assistant":
                        role = "assistant"
                    elif role == "ai":
                        role = "assistant"
                    messages.append({
                        "role": role,
                        "content": msg.get("content", "")
                    })
            
            # 添加当前用户问题
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # 调用AI API（兼容OpenAI格式）
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # 智谱GLM需要特殊的Authorization格式
                if self.provider == 'zhipu':
                    headers["Authorization"] = self.api_key
                
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 0.9
                }
                
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = response.text
                    logger.error(f"AI API调用失败: {response.status_code} - {error_msg}")
                    return {"response": self._get_mock_response(user_input), "agent": "健康管家"}
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                logger.info(f"AI咨询成功 ({self.provider}): 用户问题长度={len(user_input)}, 回复长度={len(ai_response)}")
                
                return {"response": ai_response, "agent": "健康管家"}
            
        except httpx.TimeoutException:
            logger.error("AI API调用超时")
            return {"response": self._get_mock_response(user_input), "agent": "健康管家"}
        except Exception as e:
            logger.error(f"AI咨询失败: {str(e)}")
            # 发生错误时返回模拟回复作为备用
            return {"response": self._get_mock_response(user_input), "agent": "健康管家"}
    
    def _get_mock_response(self, user_input: str) -> str:
        """获取错误提示（当API不可用时）"""
        return "抱歉，AI服务暂时不可用，请检查API配置后重试。"


# 创建全局AI服务实例
ai_service = AIService()


