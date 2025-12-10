"""
讯飞星火大模型服务 - HTTP API 版本
================================

使用新版 HTTP API（OpenAI 兼容格式）调用星火大模型。
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SparkConfig:
    """讯飞星火配置"""
    # 从控制台获取的密钥 (APIKey:APISecret 格式)
    API_PASSWORD = "aYiPcrrNPPRaoOZaJwgH:XUNRUshRchZDjNiYfAnk"
    
    # HTTP API 地址 (截图显示的地址)
    API_URL = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    
    # 模型名称
    MODEL = "x1"  # Spark X1.5


class SparkServiceHTTP:
    """讯飞星火服务 - HTTP API"""
    
    def __init__(self):
        self.api_url = SparkConfig.API_URL
        self.api_password = SparkConfig.API_PASSWORD
        self.model = SparkConfig.MODEL
    
    def chat(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        调用讯飞星火 HTTP API
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词
            history: 对话历史
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AI回复文本
        """
        try:
            # 构建消息
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if history:
                messages.extend(history)
            
            messages.append({"role": "user", "content": user_input})
            
            # 请求体
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_password}"
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Spark API error: {error_msg}")
                return f"抱歉，AI服务暂时不可用: {error_msg}"
                
        except Exception as e:
            logger.error(f"Spark API exception: {e}")
            return f"抱歉，AI服务暂时不可用: {str(e)}"


# 创建全局实例
spark_service = SparkServiceHTTP()
