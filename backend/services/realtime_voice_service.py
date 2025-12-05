"""
实时语音服务 - 使用 RealtimeSTT + RealtimeTTS
支持：实时转写、自动语音检测、流式TTS、打断功能
"""

import asyncio
import json
import logging
import threading
import queue
from typing import Optional, Callable
import edge_tts

logger = logging.getLogger(__name__)

# 尝试导入 RealtimeSTT
try:
    from RealtimeSTT import AudioToTextRecorder
    HAS_REALTIME_STT = True
except ImportError:
    HAS_REALTIME_STT = False
    logger.warning("RealtimeSTT 未安装")

# 尝试导入 RealtimeTTS
try:
    from RealtimeTTS import TextToAudioStream, EdgeEngine
    HAS_REALTIME_TTS = True
except ImportError:
    HAS_REALTIME_TTS = False
    logger.warning("RealtimeTTS 未安装")


class RealtimeVoiceService:
    """实时语音服务"""
    
    def __init__(self):
        self.recorder: Optional[AudioToTextRecorder] = None
        self.tts_stream: Optional[TextToAudioStream] = None
        self.is_recording = False
        self.is_speaking = False
        
        # 回调函数
        self.on_realtime_text: Optional[Callable[[str], None]] = None
        self.on_final_text: Optional[Callable[[str], None]] = None
        self.on_recording_start: Optional[Callable[[], None]] = None
        self.on_recording_stop: Optional[Callable[[], None]] = None
        self.on_vad_start: Optional[Callable[[], None]] = None
        self.on_vad_stop: Optional[Callable[[], None]] = None
        
        # 消息队列（用于线程间通信）
        self.message_queue = queue.Queue()
        
    def init_stt(self):
        """初始化语音识别"""
        if not HAS_REALTIME_STT:
            logger.error("RealtimeSTT 未安装，无法使用实时语音识别")
            return False
            
        try:
            self.recorder = AudioToTextRecorder(
                model="tiny",  # 使用小模型，速度快
                language="zh",  # 中文
                silero_sensitivity=0.4,  # VAD 灵敏度
                webrtc_sensitivity=2,
                post_speech_silence_duration=0.4,  # 说话后静默时间
                min_length_of_recording=0.5,  # 最小录音时长
                min_gap_between_recordings=0,
                enable_realtime_transcription=True,  # 启用实时转写
                realtime_processing_pause=0.1,  # 实时处理间隔
                realtime_model_type="tiny",
                on_realtime_transcription_update=self._on_realtime_update,
                on_recording_start=self._on_recording_start,
                on_recording_stop=self._on_recording_stop,
                on_vad_detect_start=self._on_vad_start,
                on_vad_detect_stop=self._on_vad_stop,
            )
            logger.info("RealtimeSTT 初始化成功")
            return True
        except Exception as e:
            logger.error(f"RealtimeSTT 初始化失败: {e}")
            return False
    
    def init_tts(self):
        """初始化语音合成"""
        if not HAS_REALTIME_TTS:
            logger.error("RealtimeTTS 未安装，无法使用流式语音合成")
            return False
            
        try:
            # 使用 Edge TTS 引擎
            engine = EdgeEngine(
                voice="zh-CN-XiaoxiaoNeural",
                rate="-10%",  # 稍慢语速
                volume="+10%"  # 稍大音量
            )
            self.tts_stream = TextToAudioStream(engine)
            logger.info("RealtimeTTS 初始化成功")
            return True
        except Exception as e:
            logger.error(f"RealtimeTTS 初始化失败: {e}")
            return False
    
    def _on_realtime_update(self, text: str):
        """实时转写回调"""
        self.message_queue.put({
            "type": "realtime_text",
            "text": text
        })
        if self.on_realtime_text:
            self.on_realtime_text(text)
    
    def _on_recording_start(self):
        """开始录音回调"""
        self.is_recording = True
        self.message_queue.put({"type": "recording_start"})
        if self.on_recording_start:
            self.on_recording_start()
    
    def _on_recording_stop(self):
        """停止录音回调"""
        self.is_recording = False
        self.message_queue.put({"type": "recording_stop"})
        if self.on_recording_stop:
            self.on_recording_stop()
    
    def _on_vad_start(self):
        """检测到语音开始"""
        self.message_queue.put({"type": "vad_start"})
        if self.on_vad_start:
            self.on_vad_start()
    
    def _on_vad_stop(self):
        """检测到语音结束"""
        self.message_queue.put({"type": "vad_stop"})
        if self.on_vad_stop:
            self.on_vad_stop()
    
    def start_listening(self) -> bool:
        """开始监听（自动语音检测）"""
        if not self.recorder:
            if not self.init_stt():
                return False
        
        try:
            # 在后台线程运行
            def listen_thread():
                while self.is_recording or True:
                    try:
                        text = self.recorder.text()
                        if text:
                            self.message_queue.put({
                                "type": "final_text",
                                "text": text
                            })
                            if self.on_final_text:
                                self.on_final_text(text)
                    except Exception as e:
                        logger.error(f"监听错误: {e}")
                        break
            
            self.listen_thread = threading.Thread(target=listen_thread, daemon=True)
            self.listen_thread.start()
            return True
        except Exception as e:
            logger.error(f"开始监听失败: {e}")
            return False
    
    def stop_listening(self):
        """停止监听"""
        if self.recorder:
            try:
                self.recorder.stop()
            except:
                pass
    
    def speak(self, text: str, interrupt: bool = True):
        """
        流式语音播放
        
        Args:
            text: 要播放的文本
            interrupt: 是否打断当前播放
        """
        if interrupt and self.is_speaking:
            self.stop_speaking()
        
        if not self.tts_stream:
            if not self.init_tts():
                return
        
        try:
            self.is_speaking = True
            self.message_queue.put({"type": "tts_start"})
            
            # 流式播放
            self.tts_stream.feed(text)
            self.tts_stream.play_async(
                on_audio_chunk=lambda chunk: None,
                on_sentence_end=lambda: None,
            )
            
            # 等待播放完成
            def wait_finish():
                self.tts_stream.wait()
                self.is_speaking = False
                self.message_queue.put({"type": "tts_end"})
            
            threading.Thread(target=wait_finish, daemon=True).start()
            
        except Exception as e:
            logger.error(f"语音播放失败: {e}")
            self.is_speaking = False
    
    def stop_speaking(self):
        """停止语音播放（打断）"""
        if self.tts_stream and self.is_speaking:
            try:
                self.tts_stream.stop()
                self.is_speaking = False
                self.message_queue.put({"type": "tts_interrupted"})
            except Exception as e:
                logger.error(f"停止播放失败: {e}")
    
    def get_messages(self) -> list:
        """获取所有待处理消息"""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def cleanup(self):
        """清理资源"""
        self.stop_listening()
        self.stop_speaking()
        if self.recorder:
            try:
                self.recorder.shutdown()
            except:
                pass


# 全局实例
realtime_voice_service = RealtimeVoiceService()
