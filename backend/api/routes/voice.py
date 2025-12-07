"""语音服务路由 - TTS语音合成 + ASR语音识别"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import logging
import os

from services.voice_service import voice_service
from api.auth import get_current_active_user
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# 请求/响应模型
# ============================================================================

class TTSRequest(BaseModel):
    """TTS 请求"""
    text: str = Field(..., description="要转换的文本", min_length=1, max_length=5000)
    voice: Optional[str] = Field("xiaoxiao", description="语音类型")
    rate: Optional[str] = Field("+0%", description="语速 (-50% ~ +50%)")
    volume: Optional[str] = Field("+10%", description="音量 (-50% ~ +50%)")


class TTSStreamRequest(BaseModel):
    """流式TTS请求"""
    text: str = Field(..., description="要转换的文本", min_length=1, max_length=500)
    voice: Optional[str] = Field("xiaoxiao", description="语音类型")
    rate: Optional[str] = Field("+15%", description="语速，默认加快15%")
    volume: Optional[str] = Field("+10%", description="音量")


class TTSResponse(BaseModel):
    """TTS 响应"""
    status: str = "success"
    audio_id: str
    audio_url: str
    message: str = "语音合成成功"


class VoicesResponse(BaseModel):
    """可用语音列表响应"""
    status: str = "success"
    data: dict


# ============================================================================
# API 路由
# ============================================================================

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    文本转语音 (TTS)
    
    将文本转换为语音音频文件，返回音频下载链接。
    适合老年人使用：默认语速稍慢、音量稍大、使用温柔女声。
    """
    try:
        audio_id, audio_path = await voice_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume
        )
        
        return {
            "success": True,
            "status": "success",
            "data": {
                "audio_id": audio_id,
                "audio_url": f"/api/v1/voice/audio/{audio_id}",
            },
            "message": "语音合成成功"
        }
        
    except Exception as e:
        logger.error(f"TTS 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@router.post("/tts/stream")
async def text_to_speech_stream(request: TTSStreamRequest):
    """
    流式TTS - 直接返回音频流（更快）
    
    特点：
    - 不保存文件，直接返回音频流
    - 边生成边传输，首字节延迟更低
    - 适合实时语音播报
    """
    try:
        async def generate():
            async for chunk in voice_service.text_to_speech_stream(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                volume=request.volume
            ):
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
            }
        )
        
    except Exception as e:
        logger.error(f"流式TTS失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@router.post("/tts/fast")
async def text_to_speech_fast(request: TTSStreamRequest):
    """
    快速TTS - 直接返回完整音频（不保存文件）
    
    比普通TTS快，因为：
    - 不写入磁盘
    - 直接返回字节流
    - 默认语速加快15%
    """
    try:
        audio_data = await voice_service.text_to_speech_fast(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume
        )
        
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
            }
        )
        
    except Exception as e:
        logger.error(f"快速TTS失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    获取音频文件
    
    根据音频ID返回音频文件，支持流式传输。
    """
    audio_path = Path(f"./audio_cache/{audio_id}.mp3")
    
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频文件不存在或已过期"
        )
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=f"{audio_id}.mp3"
    )


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """
    获取可用语音列表
    
    返回所有可用的语音类型及其特点。
    """
    voices = voice_service.get_available_voices()
    return VoicesResponse(data=voices)


class ASRRequest(BaseModel):
    """ASR 请求参数"""
    language: Optional[str] = Field("zh", description="语言代码 (zh/en/ja/ko)")


@router.post("/asr")
async def speech_to_text(
    audio: UploadFile = File(..., description="音频文件 (WAV/MP3/WEBM)"),
    language: str = "zh"
):
    """
    语音转文本 (ASR) - 使用 SenseVoice 模型
    
    将音频文件转换为文本，支持中文、英文、日语、韩语等。
    需要 GPU 支持，首次使用会自动下载模型。
    
    支持格式: WAV, MP3, WEBM, OGG 等
    """
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        # 进行语音识别
        text = await voice_service.speech_to_text(audio_data, language=language)
        
        return {
            "success": True,
            "status": "success",
            "data": {
                "text": text,
            },
            "filename": audio.filename,
            "language": language,
            "message": "语音识别成功"
        }
        
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ASR 功能未配置。请安装依赖: pip install funasr==1.1.12 PyAudio==0.2.14"
        )
    except Exception as e:
        logger.error(f"ASR 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )


@router.get("/asr/status")
async def asr_status():
    """检查 ASR 服务状态"""
    return {
        "status": "success",
        "asr_available": voice_service.asr_model is not None,
        "message": "ASR 已就绪" if voice_service.asr_model else "ASR 未配置，使用浏览器端识别"
    }


@router.delete("/audio/{audio_id}")
async def delete_audio(
    audio_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """删除音频文件"""
    audio_path = Path(f"./audio_cache/{audio_id}.mp3")
    
    if audio_path.exists():
        audio_path.unlink()
        return {"status": "success", "message": "音频已删除"}
    
    return {"status": "success", "message": "音频不存在"}


@router.post("/cleanup")
async def cleanup_audio(
    current_user: User = Depends(get_current_active_user)
):
    """清理过期音频文件（管理员功能）"""
    voice_service.cleanup_old_audio(max_age_hours=24)
    return {"status": "success", "message": "清理完成"}
