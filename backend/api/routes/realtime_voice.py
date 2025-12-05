"""
实时语音 WebSocket 路由
支持：实时转写、自动VAD、流式TTS、打断
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging

from services.realtime_voice_service import realtime_voice_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新连接，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"断开连接，当前连接数: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await self.send_message(connection, message)


manager = ConnectionManager()


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """
    实时语音 WebSocket 端点
    
    客户端消息格式:
    - {"action": "start_listening"} - 开始监听（自动VAD）
    - {"action": "stop_listening"} - 停止监听
    - {"action": "speak", "text": "..."} - 播放语音
    - {"action": "stop_speaking"} - 停止播放（打断）
    - {"action": "get_status"} - 获取状态
    
    服务端消息格式:
    - {"type": "realtime_text", "text": "..."} - 实时转写文本
    - {"type": "final_text", "text": "..."} - 最终识别文本
    - {"type": "recording_start"} - 开始录音
    - {"type": "recording_stop"} - 停止录音
    - {"type": "vad_start"} - 检测到语音开始
    - {"type": "vad_stop"} - 检测到语音结束
    - {"type": "tts_start"} - 开始播放
    - {"type": "tts_end"} - 播放结束
    - {"type": "tts_interrupted"} - 播放被打断
    - {"type": "error", "message": "..."} - 错误
    - {"type": "status", ...} - 状态信息
    """
    await manager.connect(websocket)
    
    # 消息推送任务
    async def push_messages():
        while True:
            try:
                messages = realtime_voice_service.get_messages()
                for msg in messages:
                    await manager.send_message(websocket, msg)
                await asyncio.sleep(0.05)  # 50ms 检查一次
            except Exception as e:
                logger.error(f"推送消息错误: {e}")
                break
    
    push_task = asyncio.create_task(push_messages())
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "start_listening":
                # 开始监听（自动VAD）
                success = realtime_voice_service.start_listening()
                await manager.send_message(websocket, {
                    "type": "status",
                    "action": "start_listening",
                    "success": success,
                    "message": "开始监听" if success else "启动失败"
                })
            
            elif action == "stop_listening":
                # 停止监听
                realtime_voice_service.stop_listening()
                await manager.send_message(websocket, {
                    "type": "status",
                    "action": "stop_listening",
                    "success": True,
                    "message": "已停止监听"
                })
            
            elif action == "speak":
                # 播放语音
                text = data.get("text", "")
                if text:
                    realtime_voice_service.speak(text, interrupt=True)
                    await manager.send_message(websocket, {
                        "type": "status",
                        "action": "speak",
                        "success": True,
                        "message": "开始播放"
                    })
            
            elif action == "stop_speaking":
                # 停止播放（打断）
                realtime_voice_service.stop_speaking()
                await manager.send_message(websocket, {
                    "type": "status",
                    "action": "stop_speaking",
                    "success": True,
                    "message": "已停止播放"
                })
            
            elif action == "get_status":
                # 获取状态
                await manager.send_message(websocket, {
                    "type": "status",
                    "is_recording": realtime_voice_service.is_recording,
                    "is_speaking": realtime_voice_service.is_speaking,
                })
            
            else:
                await manager.send_message(websocket, {
                    "type": "error",
                    "message": f"未知操作: {action}"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket 断开")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
    finally:
        push_task.cancel()
        manager.disconnect(websocket)
        realtime_voice_service.stop_listening()
        realtime_voice_service.stop_speaking()


@router.get("/realtime/status")
async def get_realtime_status():
    """获取实时语音服务状态"""
    from services.realtime_voice_service import HAS_REALTIME_STT, HAS_REALTIME_TTS
    
    return {
        "status": "ok",
        "realtime_stt_available": HAS_REALTIME_STT,
        "realtime_tts_available": HAS_REALTIME_TTS,
        "is_recording": realtime_voice_service.is_recording,
        "is_speaking": realtime_voice_service.is_speaking,
    }
