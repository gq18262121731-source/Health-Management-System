"""语音服务 - ASR(语音识别) + TTS(语音合成)"""
import logging
import os
import uuid
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import edge_tts

logger = logging.getLogger(__name__)

# 音频文件存储目录
AUDIO_DIR = Path("./audio_cache")
AUDIO_DIR.mkdir(exist_ok=True)

# 尝试导入 FunASR (SenseVoice)
try:
    from funasr import AutoModel
    HAS_FUNASR = True
except ImportError:
    HAS_FUNASR = False
    logger.warning("funasr 未安装，ASR 功能不可用。请运行: pip install funasr")


class VoiceService:
    """语音服务类 - 支持语音识别和语音合成"""
    
    # Edge-TTS 中文语音列表
    VOICES = {
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 女声，温柔
        "xiaoyi": "zh-CN-XiaoyiNeural",          # 女声，活泼
        "yunjian": "zh-CN-YunjianNeural",        # 男声，稳重
        "yunxi": "zh-CN-YunxiNeural",            # 男声，年轻
        "yunxia": "zh-CN-YunxiaNeural",          # 女声，儿童
        "yunyang": "zh-CN-YunyangNeural",        # 男声，新闻播报
    }
    
    def __init__(self):
        """初始化语音服务"""
        self.default_voice = "xiaoxiao"  # 默认使用温柔女声，适合老年人
        self.asr_model = None
        self._init_asr()
    
    def _init_asr(self):
        """初始化 ASR 模型 (SenseVoice)"""
        if not HAS_FUNASR:
            logger.info("ASR 模型未配置，将使用浏览器端语音识别")
            return
            
        try:
            logger.info("正在加载 SenseVoice ASR 模型...")
            # 使用 SenseVoiceSmall 模型（会自动从 ModelScope 下载）
            self.asr_model = AutoModel(
                model="iic/SenseVoiceSmall",
                vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},
                trust_remote_code=True,
                device="cuda:0"  # 使用 GPU
            )
            logger.info("SenseVoice ASR 模型加载成功！")
        except Exception as e:
            logger.error(f"ASR 模型加载失败: {e}")
            self.asr_model = None
    
    async def text_to_speech(
        self,
        text: str,
        voice: str = None,
        rate: str = "+0%",  # 正常语速
        volume: str = "+10%"  # 音量稍大
    ) -> Tuple[str, str]:
        """
        文本转语音 (TTS)
        
        Args:
            text: 要转换的文本
            voice: 语音类型 (xiaoxiao/xiaoyi/yunjian/yunxi/yunxia/yunyang)
            rate: 语速 (-50% ~ +50%)
            volume: 音量 (-50% ~ +50%)
        
        Returns:
            (audio_id, audio_path): 音频ID和文件路径
        """
        try:
            # 选择语音
            voice_name = self.VOICES.get(voice or self.default_voice, self.VOICES["xiaoxiao"])
            
            # 生成唯一文件名
            audio_id = str(uuid.uuid4())
            audio_path = AUDIO_DIR / f"{audio_id}.mp3"
            
            # 使用 Edge-TTS 生成语音
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_name,
                rate=rate,
                volume=volume
            )
            
            await communicate.save(str(audio_path))
            
            logger.info(f"TTS 生成成功: {audio_id}, 文本长度: {len(text)}")
            return audio_id, str(audio_path)
            
        except Exception as e:
            logger.error(f"TTS 生成失败: {e}")
            raise
    
    async def speech_to_text(self, audio_data: bytes, language: str = "zh") -> str:
        """
        语音转文本 (ASR) - 使用 SenseVoice
        
        Args:
            audio_data: 音频二进制数据 (WAV/MP3/WEBM 等格式)
            language: 语言代码 (zh/en/ja/ko 等)
        
        Returns:
            识别出的文本
        """
        if self.asr_model is None:
            raise NotImplementedError("ASR 模型未配置，请安装 funasr: pip install funasr==1.1.12")
        
        try:
            # 将音频数据保存为临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # 使用 SenseVoice 进行语音识别
                result = self.asr_model.generate(
                    input=tmp_path,
                    cache={},
                    language=language,  # "zh", "en", "ja", "ko" 等
                    use_itn=True,       # 智能文本规范化
                    batch_size_s=60
                )
                
                # 提取识别文本
                if result and len(result) > 0:
                    text = result[0].get("text", "")
                    # 清理特殊标记
                    text = text.replace("<|zh|>", "").replace("<|en|>", "")
                    text = text.replace("<|NEUTRAL|>", "").replace("<|EMO_UNKNOWN|>", "")
                    text = text.replace("<|Speech|>", "").replace("<|Event_UNK|>", "")
                    text = text.strip()
                    
                    logger.info(f"ASR 识别成功: {text[:50]}...")
                    return text
                else:
                    return ""
                    
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            logger.error(f"ASR 识别失败: {e}")
            raise
    
    def get_available_voices(self) -> dict:
        """获取可用的语音列表"""
        return {
            "voices": [
                {"id": "xiaoxiao", "name": "晓晓", "gender": "女", "style": "温柔亲切"},
                {"id": "xiaoyi", "name": "晓伊", "gender": "女", "style": "活泼开朗"},
                {"id": "yunjian", "name": "云健", "gender": "男", "style": "稳重大气"},
                {"id": "yunxi", "name": "云希", "gender": "男", "style": "年轻活力"},
                {"id": "yunxia", "name": "云夏", "gender": "女", "style": "童声可爱"},
                {"id": "yunyang", "name": "云扬", "gender": "男", "style": "新闻播报"},
            ],
            "default": "xiaoxiao"
        }
    
    def cleanup_old_audio(self, max_age_hours: int = 24):
        """清理过期的音频文件"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for audio_file in AUDIO_DIR.glob("*.mp3"):
            if current_time - audio_file.stat().st_mtime > max_age_seconds:
                try:
                    audio_file.unlink()
                    logger.info(f"清理过期音频: {audio_file.name}")
                except Exception as e:
                    logger.warning(f"清理音频失败: {e}")


# 全局语音服务实例
voice_service = VoiceService()
