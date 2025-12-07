"""
讯飞星火大模型服务
==================

为多智能体系统提供统一的讯飞星火API调用接口。
每个智能体可以使用自己的系统提示词调用此服务。
"""

import json
import hmac
import hashlib
import base64
import ssl
import websocket
import logging
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from typing import List, Dict, Optional, Callable
import threading

logger = logging.getLogger(__name__)


class SparkConfig:
    """讯飞星火配置"""
    APPID = "136dab64"
    API_SECRET = "NDFlZjcyMTRhMjUzMjk3ZDQwM2I5ZGE3"
    API_KEY = "0c1dc672ab3c5cdad820eae1aa22841c"
    VERSION = "v3.5"
    
    # 版本对应的URL和domain
    VERSION_MAP = {
        "v1.5": {"url": "wss://spark-api.xf-yun.com/v1.1/chat", "domain": "general"},
        "v2.0": {"url": "wss://spark-api.xf-yun.com/v2.1/chat", "domain": "generalv2"},
        "v3.0": {"url": "wss://spark-api.xf-yun.com/v3.1/chat", "domain": "generalv3"},
        "v3.5": {"url": "wss://spark-api.xf-yun.com/v3.5/chat", "domain": "generalv3.5"},
        "v4.0": {"url": "wss://spark-api.xf-yun.com/v4.0/chat", "domain": "4.0Ultra"},
    }
    
    @classmethod
    def get_url_and_domain(cls):
        config = cls.VERSION_MAP.get(cls.VERSION, cls.VERSION_MAP["v3.5"])
        return config["url"], config["domain"]


class SparkService:
    """讯飞星火服务 - 同步调用"""
    
    def __init__(self):
        self.appid = SparkConfig.APPID
        self.api_secret = SparkConfig.API_SECRET
        self.api_key = SparkConfig.API_KEY
        self.url, self.domain = SparkConfig.get_url_and_domain()
        
    def _create_auth_url(self) -> str:
        """生成鉴权URL"""
        from urllib.parse import urlparse
        
        parsed = urlparse(self.url)
        host = parsed.netloc
        path = parsed.path
        
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        # 构建签名原文
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # HMAC-SHA256签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构建authorization
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 构建最终URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        return f"{self.url}?{urlencode(params)}"
    
    def _build_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> dict:
        """构建请求体"""
        # 构建消息列表
        text_messages = []
        
        # 添加系统提示词
        if system_prompt:
            text_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加对话消息
        for msg in messages:
            text_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        return {
            "header": {
                "app_id": self.appid,
                "uid": "health_agent"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_k": 4
                }
            },
            "payload": {
                "message": {
                    "text": text_messages
                }
            }
        }
    
    def chat(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        同步调用讯飞星火API
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词（智能体专业prompt）
            history: 对话历史 [{"role": "user", "content": "..."}, ...]
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AI回复文本
        """
        # 构建消息
        messages = history or []
        messages.append({"role": "user", "content": user_input})
        
        # 构建请求
        request_data = self._build_request(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 同步调用
        result = {"response": "", "error": None}
        
        def on_message(ws, message):
            data = json.loads(message)
            code = data.get("header", {}).get("code", 0)
            
            if code != 0:
                result["error"] = f"Error code: {code}, message: {data.get('header', {}).get('message', 'Unknown error')}"
                ws.close()
                return
            
            # 提取文本
            choices = data.get("payload", {}).get("choices", {})
            text = choices.get("text", [])
            if text:
                result["response"] += text[0].get("content", "")
            
            # 检查是否结束
            status = choices.get("status", 0)
            if status == 2:
                ws.close()
        
        def on_error(ws, error):
            result["error"] = str(error)
            logger.error(f"Spark WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            pass
        
        def on_open(ws):
            ws.send(json.dumps(request_data))
        
        try:
            auth_url = self._create_auth_url()
            ws = websocket.WebSocketApp(
                auth_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            if result["error"]:
                logger.error(f"Spark API error: {result['error']}")
                return f"抱歉，AI服务暂时不可用: {result['error']}"
            
            return result["response"]
            
        except Exception as e:
            logger.error(f"Spark API call failed: {e}")
            return f"抱歉，AI服务调用失败: {str(e)}"
    
    def chat_stream(
        self,
        user_input: str,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        on_message: Callable[[str], None] = None,
        on_complete: Callable[[str], None] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        流式调用讯飞星火API
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词
            history: 对话历史
            on_message: 收到消息回调（增量文本）
            on_complete: 完成回调（完整文本）
            temperature: 温度参数
            max_tokens: 最大token数
        """
        messages = history or []
        messages.append({"role": "user", "content": user_input})
        
        request_data = self._build_request(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        full_response = []
        
        def ws_on_message(ws, message):
            data = json.loads(message)
            code = data.get("header", {}).get("code", 0)
            
            if code != 0:
                logger.error(f"Spark error: {code}")
                ws.close()
                return
            
            choices = data.get("payload", {}).get("choices", {})
            text = choices.get("text", [])
            if text:
                content = text[0].get("content", "")
                full_response.append(content)
                if on_message:
                    on_message(content)
            
            status = choices.get("status", 0)
            if status == 2:
                if on_complete:
                    on_complete("".join(full_response))
                ws.close()
        
        def ws_on_error(ws, error):
            logger.error(f"Spark WebSocket error: {error}")
        
        def ws_on_open(ws):
            ws.send(json.dumps(request_data))
        
        try:
            auth_url = self._create_auth_url()
            ws = websocket.WebSocketApp(
                auth_url,
                on_message=ws_on_message,
                on_error=ws_on_error,
                on_open=ws_on_open
            )
            
            # 在新线程中运行
            wst = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            wst.daemon = True
            wst.start()
            
        except Exception as e:
            logger.error(f"Spark stream call failed: {e}")


# 单例实例
spark_service = SparkService()
