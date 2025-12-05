"""
流式语音识别服务
前端实时采集音频流 → WebSocket传输 → faster-whisper实时识别
"""

import asyncio
import logging
import tempfile
import os
import wave
import io
import numpy as np
from typing import Optional, Callable, AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)

# 尝试导入 faster-whisper
try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    HAS_FASTER_WHISPER = False
    logger.warning("faster-whisper 未安装，请运行: pip install faster-whisper")


class StreamingASRService:
    """流式语音识别服务"""
    
    def __init__(self):
        self.model: Optional[WhisperModel] = None
        self.model_size = "tiny"  # tiny/base/small/medium/large
        self.is_initialized = False
        
    def init_model(self) -> bool:
        """初始化 Whisper 模型"""
        if not HAS_FASTER_WHISPER:
            logger.error("faster-whisper 未安装")
            return False
            
        if self.is_initialized:
            return True
            
        try:
            logger.info(f"正在加载 Whisper 模型: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # 或 "cuda" 如果有GPU
                compute_type="int8"  # 量化以提高速度
            )
            self.is_initialized = True
            logger.info("Whisper 模型加载成功")
            return True
        except Exception as e:
            logger.error(f"Whisper 模型加载失败: {e}")
            return False
    
    def transcribe_audio(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """
        识别音频数据
        
        Args:
            audio_data: PCM 音频数据 (16-bit, mono)
            sample_rate: 采样率
            
        Returns:
            识别的文本
        """
        if not self.is_initialized:
            if not self.init_model():
                return ""
        
        try:
            # 将音频数据转换为临时 WAV 文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                
                # 写入 WAV 格式
                with wave.open(f, 'wb') as wav:
                    wav.setnchannels(1)  # 单声道
                    wav.setsampwidth(2)  # 16-bit
                    wav.setframerate(sample_rate)
                    wav.writeframes(audio_data)
            
            # 使用 faster-whisper 识别
            segments, info = self.model.transcribe(
                temp_path,
                language="zh",
                beam_size=5,
                vad_filter=True,  # 启用 VAD 过滤静音
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                ),
            )
            
            # 收集所有文本
            text = "".join([segment.text for segment in segments])
            
            # 清理临时文件
            os.unlink(temp_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return ""
    
    async def transcribe_stream(
        self, 
        audio_chunks: AsyncGenerator[bytes, None],
        sample_rate: int = 16000,
        chunk_duration: float = 2.0,  # 每2秒识别一次
        on_partial: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        流式识别音频
        
        Args:
            audio_chunks: 音频数据流
            sample_rate: 采样率
            chunk_duration: 每次识别的时长(秒)
            on_partial: 部分结果回调
            on_final: 最终结果回调
            
        Returns:
            完整识别文本
        """
        if not self.is_initialized:
            if not self.init_model():
                return ""
        
        buffer = b""
        chunk_size = int(sample_rate * 2 * chunk_duration)  # 16-bit = 2 bytes per sample
        all_text = []
        
        try:
            async for chunk in audio_chunks:
                buffer += chunk
                
                # 当缓冲区足够大时进行识别
                if len(buffer) >= chunk_size:
                    text = self.transcribe_audio(buffer, sample_rate)
                    if text:
                        all_text.append(text)
                        if on_partial:
                            on_partial(text)
                    buffer = b""  # 清空缓冲区
            
            # 处理剩余数据
            if len(buffer) > sample_rate:  # 至少0.5秒
                text = self.transcribe_audio(buffer, sample_rate)
                if text:
                    all_text.append(text)
            
            final_text = "".join(all_text)
            if on_final and final_text:
                on_final(final_text)
                
            return final_text
            
        except Exception as e:
            logger.error(f"流式识别失败: {e}")
            return "".join(all_text)


# 全局实例
streaming_asr_service = StreamingASRService()
