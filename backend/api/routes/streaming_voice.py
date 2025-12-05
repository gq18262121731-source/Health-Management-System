"""
流式语音 WebSocket 路由
前端实时采集音频流 → WebSocket传输 → faster-whisper实时识别
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging
import base64
import edge_tts
import tempfile
import os

from services.streaming_asr_service import streaming_asr_service, HAS_FASTER_WHISPER

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/stream")
async def stream_voice_websocket(websocket: WebSocket):
    """
    流式语音 WebSocket 端点
    
    客户端消息格式:
    - {"type": "audio", "data": "<base64音频数据>"} - 音频数据块
    - {"type": "start"} - 开始录音
    - {"type": "stop"} - 停止录音
    - {"type": "speak", "text": "..."} - TTS播放
    - {"type": "stop_speak"} - 停止TTS
    
    服务端消息格式:
    - {"type": "partial", "text": "..."} - 部分识别结果（实时）
    - {"type": "final", "text": "..."} - 最终识别结果
    - {"type": "tts_audio", "data": "<base64音频>"} - TTS音频数据
    - {"type": "tts_done"} - TTS播放完成
    - {"type": "error", "message": "..."} - 错误
    - {"type": "status", ...} - 状态信息
    """
    await websocket.accept()
    logger.info("流式语音 WebSocket 已连接")
    
    # 音频缓冲区
    audio_buffer = b""
    is_recording = False
    is_speaking = False
    tts_task = None
    
    # 初始化 ASR 模型
    if HAS_FASTER_WHISPER:
        streaming_asr_service.init_model()
    
    async def send_json(data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def process_audio_buffer():
        """处理音频缓冲区"""
        nonlocal audio_buffer
        
        if len(audio_buffer) < 32000:  # 至少1秒数据 (16000Hz * 2bytes)
            return
            
        # 识别
        text = streaming_asr_service.transcribe_audio(audio_buffer)
        if text:
            await send_json({"type": "partial", "text": text})
        
        # 保留最后0.5秒作为上下文
        audio_buffer = audio_buffer[-16000:]
    
    async def tts_stream(text: str):
        """流式TTS"""
        nonlocal is_speaking
        is_speaking = True
        
        try:
            communicate = edge_tts.Communicate(
                text,
                voice="zh-CN-XiaoxiaoNeural",
                rate="-10%",
                volume="+10%"
            )
            
            # 收集所有音频数据
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                    
                    # 每收集一定量就发送（流式播放）
                    if len(audio_data) >= 8000:
                        await send_json({
                            "type": "tts_audio",
                            "data": base64.b64encode(audio_data).decode()
                        })
                        audio_data = b""
                        
                        if not is_speaking:  # 被打断
                            break
            
            # 发送剩余数据
            if audio_data and is_speaking:
                await send_json({
                    "type": "tts_audio", 
                    "data": base64.b64encode(audio_data).decode()
                })
            
            await send_json({"type": "tts_done"})
            
        except Exception as e:
            logger.error(f"TTS 错误: {e}")
            await send_json({"type": "error", "message": str(e)})
        finally:
            is_speaking = False
    
    try:
        # 发送初始状态
        await send_json({
            "type": "status",
            "asr_available": HAS_FASTER_WHISPER,
            "message": "已连接" if HAS_FASTER_WHISPER else "ASR服务未就绪"
        })
        
        while True:
            # 接收消息
            message = await websocket.receive()
            
            if message["type"] == "websocket.disconnect":
                break
                
            if "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")
                
                if msg_type == "start":
                    # 开始录音
                    is_recording = True
                    audio_buffer = b""
                    await send_json({"type": "status", "recording": True})
                    logger.info("开始接收音频流")
                    
                elif msg_type == "stop":
                    # 停止录音，处理最后的音频
                    is_recording = False
                    
                    if len(audio_buffer) > 8000:  # 至少0.25秒
                        text = streaming_asr_service.transcribe_audio(audio_buffer)
                        if text:
                            await send_json({"type": "final", "text": text})
                    
                    audio_buffer = b""
                    await send_json({"type": "status", "recording": False})
                    logger.info("停止接收音频流")
                    
                elif msg_type == "audio":
                    # 接收音频数据
                    if is_recording:
                        audio_data = base64.b64decode(data.get("data", ""))
                        audio_buffer += audio_data
                        
                        # 实时处理
                        await process_audio_buffer()
                        
                elif msg_type == "speak":
                    # TTS播放
                    text = data.get("text", "")
                    if text:
                        if tts_task and not tts_task.done():
                            is_speaking = False  # 打断当前播放
                            await asyncio.sleep(0.1)
                        tts_task = asyncio.create_task(tts_stream(text))
                        
                elif msg_type == "stop_speak":
                    # 停止TTS
                    is_speaking = False
                    await send_json({"type": "tts_stopped"})
                    
            elif "bytes" in message:
                # 直接接收二进制音频数据
                if is_recording:
                    audio_buffer += message["bytes"]
                    await process_audio_buffer()
                    
    except WebSocketDisconnect:
        logger.info("WebSocket 断开")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
    finally:
        is_recording = False
        is_speaking = False
        logger.info("流式语音 WebSocket 已关闭")


@router.get("/status")
async def get_streaming_status():
    """获取流式语音服务状态"""
    return {
        "status": "ok",
        "asr_available": HAS_FASTER_WHISPER,
        "model_initialized": streaming_asr_service.is_initialized,
        "model_size": streaming_asr_service.model_size,
    }
