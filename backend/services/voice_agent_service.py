"""
语音智能体服务
==============

将语音交互与多Agent系统集成，支持：
1. 语音输入 → ASR → 多Agent处理 → TTS语音输出
2. 语音情感分析
3. 唤醒词检测
4. 适老化语音播报
"""

import logging
import asyncio
import re
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# 导入语音服务
try:
    from services.voice_service import voice_service
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False
    voice_service = None

# 导入多Agent服务
try:
    from services.agents.multi_agent_service import multi_agent_service
    HAS_MULTI_AGENT = True
except ImportError:
    HAS_MULTI_AGENT = False
    multi_agent_service = None

# 导入自动化服务
try:
    from services.automation_service import automation_service
    HAS_AUTOMATION = True
except ImportError:
    HAS_AUTOMATION = False
    automation_service = None


class VoiceEmotion(Enum):
    """语音情感类型"""
    NEUTRAL = "neutral"      # 平静
    HAPPY = "happy"          # 开心
    SAD = "sad"              # 悲伤
    ANXIOUS = "anxious"      # 焦虑
    ANGRY = "angry"          # 生气
    TIRED = "tired"          # 疲惫
    URGENT = "urgent"        # 紧急


@dataclass
class VoiceAnalysisResult:
    """语音分析结果"""
    text: str                          # 识别的文本
    emotion: VoiceEmotion              # 识别的情感
    emotion_confidence: float          # 情感置信度
    speech_rate: str                   # 语速 (slow/normal/fast)
    volume_level: str                  # 音量 (low/normal/high)
    is_wake_word: bool                 # 是否是唤醒词
    wake_word_detected: Optional[str]  # 检测到的唤醒词


class WakeWordDetector:
    """唤醒词检测器"""
    
    # 支持的唤醒词列表
    WAKE_WORDS = [
        "糖豆糖豆",
        "糖豆",
        "你好糖豆",
        "嘿糖豆",
        "糖豆你好",
        "健康助手",
    ]
    
    # 唤醒词的模糊匹配变体（应对ASR识别偏差）
    WAKE_WORD_VARIANTS = {
        "糖豆": ["糖豆", "唐豆", "糖斗", "汤豆", "堂豆"],
        "健康助手": ["健康助手", "建康助手", "健康住手"],
    }
    
    @classmethod
    def detect(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        检测唤醒词
        
        Returns:
            (是否检测到唤醒词, 检测到的唤醒词)
        """
        text = text.strip().lower()
        
        # 精确匹配
        for wake_word in cls.WAKE_WORDS:
            if text.startswith(wake_word) or text == wake_word:
                return True, wake_word
        
        # 模糊匹配（应对ASR识别偏差）
        for base_word, variants in cls.WAKE_WORD_VARIANTS.items():
            for variant in variants:
                if text.startswith(variant) or text == variant:
                    return True, base_word
        
        return False, None
    
    @classmethod
    def remove_wake_word(cls, text: str) -> str:
        """移除文本开头的唤醒词"""
        for wake_word in cls.WAKE_WORDS:
            if text.startswith(wake_word):
                return text[len(wake_word):].strip()
        
        for base_word, variants in cls.WAKE_WORD_VARIANTS.items():
            for variant in variants:
                if text.startswith(variant):
                    return text[len(variant):].strip()
        
        return text


class VoiceEmotionAnalyzer:
    """语音情感分析器（基于文本 + 语音特征）"""
    
    # 情感关键词
    EMOTION_KEYWORDS = {
        VoiceEmotion.HAPPY: ["开心", "高兴", "快乐", "太好了", "棒", "谢谢"],
        VoiceEmotion.SAD: ["难过", "伤心", "不开心", "郁闷", "唉"],
        VoiceEmotion.ANXIOUS: ["担心", "害怕", "焦虑", "紧张", "不安", "怎么办"],
        VoiceEmotion.ANGRY: ["生气", "烦", "气死", "讨厌", "受不了"],
        VoiceEmotion.TIRED: ["累", "疲惫", "困", "没劲", "乏力"],
        VoiceEmotion.URGENT: ["急", "快", "赶紧", "马上", "救命", "疼死了", "难受死了"],
    }
    
    # 语气词情感映射
    TONE_MARKERS = {
        VoiceEmotion.SAD: ["唉", "哎", "呜"],
        VoiceEmotion.ANXIOUS: ["啊", "哎呀", "天哪"],
        VoiceEmotion.HAPPY: ["哈", "嘿", "耶"],
        VoiceEmotion.ANGRY: ["哼", "切"],
    }
    
    @classmethod
    def analyze(cls, text: str, audio_features: Dict = None) -> Tuple[VoiceEmotion, float]:
        """
        分析语音情感
        
        Args:
            text: 识别的文本
            audio_features: 音频特征（可选，包含语速、音量等）
            
        Returns:
            (情感类型, 置信度)
        """
        text = text.lower()
        emotion_scores = {e: 0.0 for e in VoiceEmotion}
        
        # 1. 基于关键词分析
        for emotion, keywords in cls.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    emotion_scores[emotion] += 0.3
        
        # 2. 基于语气词分析
        for emotion, markers in cls.TONE_MARKERS.items():
            for marker in markers:
                if marker in text:
                    emotion_scores[emotion] += 0.2
        
        # 3. 基于标点符号分析
        if "！" in text or "!" in text:
            # 感叹号可能表示强烈情感
            if emotion_scores[VoiceEmotion.HAPPY] > 0:
                emotion_scores[VoiceEmotion.HAPPY] += 0.1
            elif emotion_scores[VoiceEmotion.ANGRY] > 0:
                emotion_scores[VoiceEmotion.ANGRY] += 0.1
            elif emotion_scores[VoiceEmotion.URGENT] > 0:
                emotion_scores[VoiceEmotion.URGENT] += 0.2
        
        if "？" in text or "?" in text:
            # 问号可能表示焦虑或担心
            emotion_scores[VoiceEmotion.ANXIOUS] += 0.1
        
        # 4. 基于音频特征分析（如果有）
        if audio_features:
            speech_rate = audio_features.get("speech_rate", "normal")
            volume = audio_features.get("volume", "normal")
            
            if speech_rate == "fast":
                emotion_scores[VoiceEmotion.ANXIOUS] += 0.15
                emotion_scores[VoiceEmotion.URGENT] += 0.15
            elif speech_rate == "slow":
                emotion_scores[VoiceEmotion.SAD] += 0.1
                emotion_scores[VoiceEmotion.TIRED] += 0.1
            
            if volume == "high":
                emotion_scores[VoiceEmotion.ANGRY] += 0.1
                emotion_scores[VoiceEmotion.URGENT] += 0.1
            elif volume == "low":
                emotion_scores[VoiceEmotion.SAD] += 0.1
                emotion_scores[VoiceEmotion.TIRED] += 0.1
        
        # 找出最高分的情感
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[max_emotion]
        
        # 如果没有明显情感，返回中性
        if max_score < 0.2:
            return VoiceEmotion.NEUTRAL, 0.8
        
        # 计算置信度（归一化）
        confidence = min(max_score / 0.6, 1.0)
        
        return max_emotion, confidence


class ElderlyVoiceSettings:
    """适老化语音设置"""
    
    # 语音角色推荐
    VOICE_RECOMMENDATIONS = {
        "default": {
            "voice": "xiaoxiao",     # 温柔女声
            "rate": "-10%",          # 稍慢语速
            "volume": "+20%",        # 稍大音量
            "description": "温柔亲切的女声，语速适中，音量较大"
        },
        "calm": {
            "voice": "yunjian",      # 稳重男声
            "rate": "-15%",          # 较慢语速
            "volume": "+15%",        # 较大音量
            "description": "稳重大气的男声，语速较慢，适合放松场景"
        },
        "energetic": {
            "voice": "xiaoyi",       # 活泼女声
            "rate": "+0%",           # 正常语速
            "volume": "+10%",        # 稍大音量
            "description": "活泼开朗的女声，语速正常，适合运动提醒"
        },
        "news": {
            "voice": "yunyang",      # 新闻播报
            "rate": "-5%",           # 稍慢语速
            "volume": "+10%",        # 稍大音量
            "description": "专业播报风格，清晰准确"
        }
    }
    
    # 根据场景和情感调整语音
    EMOTION_VOICE_ADJUSTMENTS = {
        VoiceEmotion.ANXIOUS: {"rate": "-20%", "volume": "+0%"},   # 焦虑时放慢语速
        VoiceEmotion.SAD: {"rate": "-15%", "volume": "+10%"},      # 悲伤时温和一些
        VoiceEmotion.URGENT: {"rate": "+0%", "volume": "+25%"},    # 紧急时清晰响亮
        VoiceEmotion.HAPPY: {"rate": "+5%", "volume": "+15%"},     # 开心时稍快一点
        VoiceEmotion.TIRED: {"rate": "-20%", "volume": "+15%"},    # 疲惫时放慢
    }
    
    @classmethod
    def get_voice_settings(
        cls, 
        style: str = "default",
        emotion: VoiceEmotion = None
    ) -> Dict[str, str]:
        """
        获取语音设置
        
        Args:
            style: 语音风格 (default/calm/energetic/news)
            emotion: 用户当前情感（会微调语速音量）
        """
        settings = cls.VOICE_RECOMMENDATIONS.get(style, cls.VOICE_RECOMMENDATIONS["default"]).copy()
        
        # 根据情感微调
        if emotion and emotion in cls.EMOTION_VOICE_ADJUSTMENTS:
            adjustments = cls.EMOTION_VOICE_ADJUSTMENTS[emotion]
            # 合并调整（简单起见直接覆盖）
            settings["rate"] = adjustments.get("rate", settings["rate"])
            # 音量叠加
            base_vol = int(settings["volume"].replace("%", "").replace("+", ""))
            adj_vol = int(adjustments.get("volume", "+0%").replace("%", "").replace("+", ""))
            settings["volume"] = f"+{min(base_vol + adj_vol, 50)}%"
        
        return settings


class VoiceAgentService:
    """
    语音智能体服务
    
    整合语音交互与多Agent系统，提供完整的语音对话能力。
    """
    
    def __init__(self):
        self.wake_word_detector = WakeWordDetector()
        self.emotion_analyzer = VoiceEmotionAnalyzer()
        self.voice_settings = ElderlyVoiceSettings()
        
        # 会话状态
        self.is_awake = False  # 是否已唤醒
        self.awake_timeout = 30  # 唤醒后保持激活的时间（秒）
        self.last_interaction_time = 0
    
    async def process_voice_input(
        self,
        audio_data: bytes,
        user_id: str = "default",
        user_role: str = "elderly",
        voice_style: str = "default",
        require_wake_word: bool = False
    ) -> Dict[str, Any]:
        """
        处理语音输入（完整流程）
        
        流程：语音 → ASR → 唤醒词检测 → 情感分析 → 多Agent处理 → TTS
        
        Args:
            audio_data: 音频二进制数据
            user_id: 用户ID
            user_role: 用户角色 (elderly/children/community)
            voice_style: 语音风格
            require_wake_word: 是否需要唤醒词
            
        Returns:
            {
                "text": 识别的文本,
                "response": AI回复文本,
                "audio_url": TTS音频URL,
                "emotion": 识别的情感,
                "agent": 处理的智能体,
                "wake_word_detected": 是否检测到唤醒词
            }
        """
        result = {
            "success": False,
            "text": "",
            "response": "",
            "audio_url": None,
            "emotion": VoiceEmotion.NEUTRAL.value,
            "emotion_confidence": 0.0,
            "agent": None,
            "intent": None,
            "wake_word_detected": False,
            "wake_word": None
        }
        
        # 1. 语音识别 (ASR)
        if not HAS_VOICE or voice_service is None:
            result["error"] = "语音服务不可用"
            return result
        
        try:
            text = await voice_service.speech_to_text(audio_data)
            result["text"] = text
            
            if not text.strip():
                result["error"] = "未检测到语音"
                return result
                
        except Exception as e:
            logger.error(f"ASR失败: {e}")
            result["error"] = f"语音识别失败: {str(e)}"
            return result
        
        # 2. 唤醒词检测
        is_wake, wake_word = self.wake_word_detector.detect(text)
        result["wake_word_detected"] = is_wake
        result["wake_word"] = wake_word
        
        if require_wake_word and not is_wake and not self.is_awake:
            result["error"] = "请先说唤醒词（如：小康小康）"
            return result
        
        # 如果检测到唤醒词，激活状态
        if is_wake:
            self.is_awake = True
            import time
            self.last_interaction_time = time.time()
            
            # 移除唤醒词，获取实际问题
            text = self.wake_word_detector.remove_wake_word(text)
            
            # 如果只有唤醒词，返回问候
            if not text.strip():
                result["response"] = "我在呢，有什么可以帮您的吗？"
                result["success"] = True
                # 生成TTS
                audio_id, _ = await voice_service.text_to_speech(
                    result["response"],
                    **self.voice_settings.get_voice_settings(voice_style)
                )
                result["audio_url"] = f"/api/v1/voice/audio/{audio_id}"
                return result
        
        # 3. 情感分析
        emotion, emotion_conf = self.emotion_analyzer.analyze(text)
        result["emotion"] = emotion.value
        result["emotion_confidence"] = emotion_conf
        
        # 4. 自动化场景匹配（优先级最高）
        if HAS_AUTOMATION and automation_service:
            matched_scene = automation_service.match_scene(text)
            if matched_scene:
                try:
                    scene_result = await automation_service.execute_scene(matched_scene)
                    
                    # 合并所有语音文本
                    combined_speech = " ".join(scene_result.get("speak_texts", []))
                    
                    result["response"] = combined_speech or f"正在执行{matched_scene.name}"
                    result["agent"] = "自动化助手"
                    result["is_automation"] = True
                    result["automation_scene"] = matched_scene.name
                    result["frontend_events"] = scene_result.get("frontend_events", [])
                    result["success"] = True
                    
                    logger.info(f"执行自动化场景: {matched_scene.name}")
                    
                    # 生成TTS
                    if result["response"]:
                        voice_params = self.voice_settings.get_voice_settings(voice_style, emotion)
                        audio_id, _ = await voice_service.text_to_speech(
                            result["response"],
                            voice=voice_params["voice"],
                            rate=voice_params["rate"],
                            volume=voice_params["volume"]
                        )
                        result["audio_url"] = f"/api/v1/voice/audio/{audio_id}"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"自动化场景执行失败: {e}")
        
        # 5. 意图识别（判断是否为控制命令）
        from services.agents.intent_recognizer import intent_recognizer
        intent_result = intent_recognizer.recognize(text)
        intent_type = intent_result.intent.value
        result["intent"] = intent_result.to_dict()
        
        # 6. 如果是控制命令，走控制逻辑
        if intent_type.startswith("control_"):
            try:
                from services.voice_control_service import voice_control_service
                
                control_cmd = voice_control_service.parse_control_command(text, intent_type)
                
                result["response"] = control_cmd.response_text
                result["agent"] = "语音控制"
                result["is_control"] = True
                result["control_action"] = control_cmd.action.value
                result["control_event"] = control_cmd.frontend_event
                result["control_data"] = control_cmd.frontend_data
                result["success"] = True
                
                logger.info(f"语音控制命令: {control_cmd.action.value}, 事件: {control_cmd.frontend_event}")
                
            except Exception as e:
                logger.error(f"控制命令处理失败: {e}")
                result["response"] = "抱歉，控制命令执行失败，请再试一次"
        
        # 7. 非控制命令，走多Agent处理
        elif HAS_MULTI_AGENT and multi_agent_service:
            try:
                agent_result = multi_agent_service.process(
                    user_input=text,
                    user_id=user_id,
                    user_role=user_role,
                    mode="auto"
                )
                
                result["response"] = agent_result.get("response", "")
                result["agent"] = agent_result.get("agent", "")
                result["intent"] = agent_result.get("intent", {})
                result["is_control"] = False
                result["success"] = True
                
            except Exception as e:
                logger.error(f"多Agent处理失败: {e}")
                result["response"] = "抱歉，我暂时无法处理您的请求，请稍后再试。"
        else:
            result["response"] = "AI服务暂时不可用"
        
        # 5. TTS语音合成（根据情感调整语音）
        if result["response"]:
            try:
                voice_params = self.voice_settings.get_voice_settings(
                    style=voice_style,
                    emotion=emotion
                )
                
                audio_id, _ = await voice_service.text_to_speech(
                    result["response"],
                    voice=voice_params["voice"],
                    rate=voice_params["rate"],
                    volume=voice_params["volume"]
                )
                result["audio_url"] = f"/api/v1/voice/audio/{audio_id}"
                
            except Exception as e:
                logger.error(f"TTS失败: {e}")
        
        return result
    
    async def text_to_speech_with_emotion(
        self,
        text: str,
        emotion: VoiceEmotion = None,
        voice_style: str = "default"
    ) -> Tuple[str, str]:
        """
        情感感知的TTS
        
        根据回复内容和用户情感，自动调整语音参数
        """
        # 分析回复文本的情感（如果未指定）
        if emotion is None:
            emotion, _ = self.emotion_analyzer.analyze(text)
        
        voice_params = self.voice_settings.get_voice_settings(
            style=voice_style,
            emotion=emotion
        )
        
        audio_id, audio_path = await voice_service.text_to_speech(
            text,
            voice=voice_params["voice"],
            rate=voice_params["rate"],
            volume=voice_params["volume"]
        )
        
        return audio_id, audio_path
    
    def get_voice_styles(self) -> Dict:
        """获取可用的语音风格"""
        return {
            "styles": [
                {
                    "id": style_id,
                    "voice": settings["voice"],
                    "description": settings["description"]
                }
                for style_id, settings in self.voice_settings.VOICE_RECOMMENDATIONS.items()
            ],
            "default": "default"
        }
    
    def get_wake_words(self) -> list:
        """获取支持的唤醒词"""
        return self.wake_word_detector.WAKE_WORDS
    
    def get_automation_scenes(self) -> Dict[str, Any]:
        """获取可用的自动化场景"""
        if not HAS_AUTOMATION or automation_service is None:
            return {"available": False, "scenes": []}
        
        return {
            "available": True,
            "scenes": automation_service.get_available_scenes(),
            "keywords": automation_service.get_scene_keywords()
        }


# 单例实例
voice_agent_service = VoiceAgentService()
