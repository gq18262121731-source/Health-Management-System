"""
语音智能体API路由
==================

提供语音与多Agent系统集成的接口：
- 语音对话（ASR + 多Agent + TTS）
- 语音情感分析
- 唤醒词检测
- 适老化语音设置
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 导入服务
try:
    from services.voice_agent_service import voice_agent_service, VoiceEmotion
    HAS_SERVICE = True
except ImportError as e:
    HAS_SERVICE = False
    logger.error(f"语音智能体服务导入失败: {e}")


# ============================================================================
# 请求/响应模型
# ============================================================================

class TextToSpeechRequest(BaseModel):
    """情感感知TTS请求"""
    text: str = Field(..., description="要转换的文本", min_length=1)
    voice_style: str = Field("default", description="语音风格")
    emotion: Optional[str] = Field(None, description="情感类型")


class TextCommandRequest(BaseModel):
    """文本命令请求（用于浏览器语音识别后的处理）"""
    text: str = Field(..., description="语音识别后的文本")
    user_role: str = Field("elderly", description="用户角色")
    voice_style: str = Field("default", description="语音风格")


class VoiceDialogResponse(BaseModel):
    """语音对话响应"""
    success: bool
    text: str = Field("", description="识别的文本")
    response: str = Field("", description="AI回复")
    audio_url: Optional[str] = Field(None, description="TTS音频URL")
    emotion: str = Field("neutral", description="识别的情感")
    emotion_confidence: float = Field(0.0, description="情感置信度")
    agent: Optional[str] = Field(None, description="处理的智能体")
    intent: Optional[dict] = Field(None, description="识别的意图")
    wake_word_detected: bool = Field(False, description="是否检测到唤醒词")
    wake_word: Optional[str] = Field(None, description="检测到的唤醒词")
    error: Optional[str] = Field(None, description="错误信息")


# ============================================================================
# API 路由
# ============================================================================

@router.post("/text-command")
async def text_command(request: TextCommandRequest):
    """
    文本命令接口（浏览器语音识别后调用）
    
    用于浏览器使用Web Speech API识别语音后，发送文本到后端处理。
    支持意图识别、控制命令、多Agent问答。
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        text = request.text.strip()
        if not text:
            return {"success": False, "error": "文本为空"}
        
        # 情感分析
        emotion, emotion_conf = voice_agent_service.emotion_analyzer.analyze(text)
        
        result = {
            "success": True,
            "text": text,
            "response": "",
            "audio_url": None,
            "emotion": emotion.value,
            "is_control": False,
            "is_automation": False,
            "control_event": None,
            "control_data": None,
            "frontend_events": [],
            "agent": None,
            "intent": None
        }
        
        # 1. 先检查自动化场景
        try:
            from services.automation_service import automation_service
            matched_scene = automation_service.match_scene(text)
            if matched_scene:
                scene_result = await automation_service.execute_scene(matched_scene)
                combined_speech = " ".join(scene_result.get("speak_texts", []))
                
                result["response"] = combined_speech or f"正在执行{matched_scene.name}"
                result["agent"] = "自动化助手"
                result["is_automation"] = True
                result["automation_scene"] = matched_scene.name
                result["frontend_events"] = scene_result.get("frontend_events", [])
                
                # 生成TTS
                if result["response"]:
                    try:
                        from services.voice_service import voice_service
                        voice_params = voice_agent_service.voice_settings.get_voice_settings(
                            style=request.voice_style,
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
                        logger.warning(f"TTS生成失败: {e}")
                
                return result
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"自动化场景匹配失败: {e}")
        
        # 2. 意图识别
        from services.agents.intent_recognizer import intent_recognizer
        intent_result = intent_recognizer.recognize(text)
        intent_type = intent_result.intent.value
        result["intent"] = intent_result.to_dict()
        
        # 3. 如果是控制命令
        if intent_type.startswith("control_"):
            from services.voice_control_service import voice_control_service
            
            control_cmd = voice_control_service.parse_control_command(text, intent_type)
            result["response"] = control_cmd.response_text
            result["is_control"] = True
            result["control_event"] = control_cmd.frontend_event
            result["control_data"] = control_cmd.frontend_data
            result["agent"] = "语音控制"
        else:
            # 非控制命令，走多Agent
            try:
                from services.agents.multi_agent_service import multi_agent_service
                agent_result = multi_agent_service.process(
                    user_input=text,
                    user_id="default",
                    user_role=request.user_role,
                    mode="auto"
                )
                result["response"] = agent_result.get("response", "")
                result["agent"] = agent_result.get("agent", "")
            except Exception as e:
                logger.error(f"多Agent处理失败: {e}")
                result["response"] = "抱歉，我暂时无法回答，请稍后再试"
        
        # 生成TTS
        if result["response"]:
            try:
                from services.voice_service import voice_service
                voice_params = voice_agent_service.voice_settings.get_voice_settings(
                    style=request.voice_style,
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
                logger.warning(f"TTS生成失败: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"文本命令处理失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "response": "处理失败，请重试"
        }


@router.post("/dialog", response_model=VoiceDialogResponse)
async def voice_dialog(
    audio: UploadFile = File(..., description="音频文件"),
    user_id: str = Form("default", description="用户ID"),
    user_role: str = Form("elderly", description="用户角色"),
    voice_style: str = Form("default", description="语音风格"),
    require_wake_word: bool = Form(False, description="是否需要唤醒词")
):
    """
    语音对话接口（完整流程）
    
    流程：语音输入 → ASR识别 → 唤醒词检测 → 情感分析 → 多Agent处理 → TTS输出
    
    - **audio**: 音频文件 (WAV/MP3/WEBM)
    - **user_id**: 用户ID
    - **user_role**: 用户角色 (elderly/children/community)
    - **voice_style**: 语音风格 (default/calm/energetic/news)
    - **require_wake_word**: 是否需要先说唤醒词
    
    返回:
    - 识别的文本、AI回复、TTS音频URL
    - 情感分析结果
    - 处理的智能体信息
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        if len(audio_data) < 1000:
            return VoiceDialogResponse(
                success=False,
                error="音频数据太短"
            )
        
        # 处理语音对话
        result = await voice_agent_service.process_voice_input(
            audio_data=audio_data,
            user_id=user_id,
            user_role=user_role,
            voice_style=voice_style,
            require_wake_word=require_wake_word
        )
        
        return VoiceDialogResponse(**result)
        
    except Exception as e:
        logger.error(f"语音对话处理失败: {e}", exc_info=True)
        return VoiceDialogResponse(
            success=False,
            error=f"处理失败: {str(e)}"
        )


@router.post("/tts/emotional")
async def emotional_tts(request: TextToSpeechRequest):
    """
    情感感知TTS
    
    根据文本内容和指定情感，自动调整语音参数（语速、音量）
    适合老年人使用：默认语速较慢、音量较大
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        # 转换情感枚举
        emotion = None
        if request.emotion:
            try:
                emotion = VoiceEmotion(request.emotion)
            except ValueError:
                pass
        
        audio_id, _ = await voice_agent_service.text_to_speech_with_emotion(
            text=request.text,
            emotion=emotion,
            voice_style=request.voice_style
        )
        
        return {
            "success": True,
            "audio_id": audio_id,
            "audio_url": f"/api/v1/voice/audio/{audio_id}",
            "voice_style": request.voice_style,
            "emotion": request.emotion or "auto"
        }
        
    except Exception as e:
        logger.error(f"情感TTS失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@router.post("/analyze/emotion")
async def analyze_voice_emotion(
    audio: UploadFile = File(..., description="音频文件")
):
    """
    语音情感分析
    
    分析语音中的情感：平静、开心、悲伤、焦虑、生气、疲惫、紧急
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        from services.voice_service import voice_service
        
        # ASR识别
        audio_data = await audio.read()
        text = await voice_service.speech_to_text(audio_data)
        
        if not text:
            return {
                "success": False,
                "error": "未检测到语音"
            }
        
        # 情感分析
        emotion, confidence = voice_agent_service.emotion_analyzer.analyze(text)
        
        return {
            "success": True,
            "text": text,
            "emotion": emotion.value,
            "emotion_label": {
                "neutral": "平静",
                "happy": "开心",
                "sad": "悲伤",
                "anxious": "焦虑",
                "angry": "生气",
                "tired": "疲惫",
                "urgent": "紧急"
            }.get(emotion.value, "未知"),
            "confidence": round(confidence, 2)
        }
        
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.post("/detect/wake-word")
async def detect_wake_word(
    audio: UploadFile = File(..., description="音频文件")
):
    """
    唤醒词检测
    
    支持的唤醒词：小康小康、小康、健康助手、你好小康
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        from services.voice_service import voice_service
        
        # ASR识别
        audio_data = await audio.read()
        text = await voice_service.speech_to_text(audio_data)
        
        if not text:
            return {
                "success": False,
                "detected": False,
                "error": "未检测到语音"
            }
        
        # 唤醒词检测
        is_wake, wake_word = voice_agent_service.wake_word_detector.detect(text)
        
        return {
            "success": True,
            "text": text,
            "detected": is_wake,
            "wake_word": wake_word,
            "supported_wake_words": voice_agent_service.get_wake_words()
        }
        
    except Exception as e:
        logger.error(f"唤醒词检测失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测失败: {str(e)}"
        )


@router.get("/settings/voices")
async def get_voice_settings():
    """
    获取适老化语音设置
    
    返回可用的语音风格列表，包括：
    - default: 温柔亲切（推荐）
    - calm: 稳重舒缓
    - energetic: 活泼开朗
    - news: 专业播报
    """
    if not HAS_SERVICE:
        return {
            "success": False,
            "error": "服务不可用"
        }
    
    return {
        "success": True,
        "data": voice_agent_service.get_voice_styles()
    }


@router.get("/settings/wake-words")
async def get_wake_words():
    """获取支持的唤醒词列表"""
    if not HAS_SERVICE:
        return {
            "success": False,
            "error": "服务不可用"
        }
    
    return {
        "success": True,
        "wake_words": voice_agent_service.get_wake_words(),
        "description": "说出唤醒词后，即可开始语音对话"
    }


@router.post("/control")
async def voice_control(
    audio: UploadFile = File(..., description="音频文件"),
    user_id: str = Form("default", description="用户ID")
):
    """
    语音控制接口
    
    支持的语音控制命令：
    - 导航: "打开首页"、"去设置"、"返回"
    - 查询: "查看血压"、"看看今天的数据"
    - 提醒: "8点提醒我吃药"、"取消提醒"
    - 通话: "打给儿子"、"联系医生"
    - 设备: "测血压"、"连接设备"
    - 播放: "放音乐"、"播放养生操"
    - 音量: "大声点"、"小声点"
    - 停止: "停止"、"暂停"
    
    返回:
    - is_control: 是否为控制命令
    - control_event: 前端事件名称
    - control_data: 前端事件数据
    """
    if not HAS_SERVICE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音智能体服务不可用"
        )
    
    try:
        audio_data = await audio.read()
        
        result = await voice_agent_service.process_voice_input(
            audio_data=audio_data,
            user_id=user_id,
            user_role="elderly",
            voice_style="default",
            require_wake_word=False
        )
        
        return {
            "success": result.get("success", False),
            "text": result.get("text", ""),
            "response": result.get("response", ""),
            "audio_url": result.get("audio_url"),
            "is_control": result.get("is_control", False),
            "control_action": result.get("control_action"),
            "control_event": result.get("control_event"),
            "control_data": result.get("control_data"),
            "intent": result.get("intent")
        }
        
    except Exception as e:
        logger.error(f"语音控制处理失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理失败: {str(e)}"
        )


@router.get("/control/commands")
async def get_control_commands():
    """获取支持的语音控制命令列表"""
    try:
        from services.voice_control_service import voice_control_service
        
        return {
            "success": True,
            "commands": voice_control_service.get_supported_commands(),
            "description": "说出以下命令即可控制系统"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/automation/scenes")
async def get_automation_scenes():
    """
    获取可用的自动化场景列表
    
    自动化场景支持通过语音关键词触发多步骤操作，例如：
    - "早安" → 播报睡眠情况 + 测量血压 + 设置吃药提醒
    - "晚安" → 今日健康总结 + 播放助眠音乐
    - "生成报告发给家人" → 生成报告 + 发送给子女
    """
    if not HAS_SERVICE:
        return {
            "success": False,
            "error": "服务不可用"
        }
    
    return {
        "success": True,
        "data": voice_agent_service.get_automation_scenes(),
        "description": "说出关键词即可触发自动化场景"
    }


@router.get("/health")
async def voice_agent_health():
    """语音智能体服务健康检查"""
    return {
        "status": "ok" if HAS_SERVICE else "unavailable",
        "features": {
            "voice_dialog": HAS_SERVICE,
            "voice_control": HAS_SERVICE,
            "emotion_analysis": HAS_SERVICE,
            "wake_word_detection": HAS_SERVICE,
            "elderly_voice_settings": HAS_SERVICE
        }
    }
