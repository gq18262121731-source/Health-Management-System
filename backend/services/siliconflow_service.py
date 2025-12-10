"""
硅基流动 API 服务
兼容 OpenAI 接口格式
"""
import os
import logging
from typing import List, Dict, Optional, Generator
import httpx

logger = logging.getLogger(__name__)


class SiliconFlowService:
    """硅基流动 API 服务"""
    
    def __init__(self):
        self.api_key = os.getenv("SILICONFLOW_API_KEY", "")
        self.base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        
        # 可用模型列表
        self.models = {
            # 对话模型
            "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
            "qwen2.5-14b": "Qwen/Qwen2.5-14B-Instruct",
            "qwen2.5-32b": "Qwen/Qwen2.5-32B-Instruct",
            "qwen2.5-72b": "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-v2.5": "deepseek-ai/DeepSeek-V2.5",
            "glm-4-9b": "THUDM/glm-4-9b-chat",
            # 嵌入模型
            "bge-m3": "BAAI/bge-m3",
            "bce-embedding": "netease-youdao/bce-embedding-base_v1",
        }
        
        if not self.api_key:
            logger.warning("SILICONFLOW_API_KEY 未配置")
    
    @property
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return bool(self.api_key)
    
    def chat(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        model: str = "qwen2.5-7b",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        调用对话模型
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词
            history: 对话历史 [{"role": "user/assistant", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成长度
            
        Returns:
            模型回复
        """
        if not self.is_available:
            raise ValueError("硅基流动 API Key 未配置")
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        
        # 获取模型全名
        model_name = self.models.get(model, model)
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"]
                logger.info(f"[SiliconFlow] {model} 调用成功，回复长度: {len(content)}")
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"[SiliconFlow] API 错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[SiliconFlow] 调用失败: {e}")
            raise
    
    def chat_stream(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        model: str = "qwen2.5-7b",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Generator[str, None, None]:
        """
        流式调用对话模型
        
        Yields:
            模型回复的文本片段
        """
        if not self.is_available:
            raise ValueError("硅基流动 API Key 未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        
        model_name = self.models.get(model, model)
        
        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except:
                                continue
                                
        except Exception as e:
            logger.error(f"[SiliconFlow] 流式调用失败: {e}")
            raise
    
    def get_embedding(
        self,
        text: str,
        model: str = "bce-embedding",
    ) -> List[float]:
        """
        获取文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型名称
            
        Returns:
            嵌入向量
        """
        if not self.is_available:
            raise ValueError("硅基流动 API Key 未配置")
        
        model_name = self.models.get(model, model)
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "input": text,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
                embedding = result["data"][0]["embedding"]
                logger.debug(f"[SiliconFlow] 嵌入生成成功，维度: {len(embedding)}")
                return embedding
                
        except Exception as e:
            logger.error(f"[SiliconFlow] 嵌入生成失败: {e}")
            raise
    
    def get_embeddings_batch(
        self,
        texts: List[str],
        model: str = "bce-embedding",
    ) -> List[List[float]]:
        """
        批量获取文本嵌入向量
        
        Args:
            texts: 输入文本列表
            model: 嵌入模型名称
            
        Returns:
            嵌入向量列表
        """
        if not self.is_available:
            raise ValueError("硅基流动 API Key 未配置")
        
        model_name = self.models.get(model, model)
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "input": texts,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
                embeddings = [item["embedding"] for item in result["data"]]
                logger.info(f"[SiliconFlow] 批量嵌入成功，数量: {len(embeddings)}")
                return embeddings
                
        except Exception as e:
            logger.error(f"[SiliconFlow] 批量嵌入失败: {e}")
            raise


# 创建全局实例
siliconflow_service = SiliconFlowService()
