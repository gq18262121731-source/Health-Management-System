"""
语音交互 API 服务
==================

集成 ASR-LLM-TTS 功能：
- ASR (语音识别): SenseVoice
- LLM (大语言模型): 讯飞星火 / Qwen
- TTS (语音合成): Edge-TTS

提供 WebSocket 和 REST API 接口
"""

import os
import sys
import asyncio
import tempfile
import base64
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime

# 添加 ASR-LLM-TTS 路径
ASR_LLM_TTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ASR-LLM-TTS-master')
sys.path.insert(0, ASR_LLM_TTS_PATH)

# 创建蓝图
voice_api = Blueprint('voice_api', __name__)

# 全局模型实例（懒加载）
_asr_model = None
_tts_initialized = False

# TTS 语音配置
TTS_VOICES = {
    "zh-CN-XiaoyiNeural": "晓伊 (女声-温柔)",
    "zh-CN-YunxiNeural": "云希 (男声-阳光)",
    "zh-CN-XiaoxiaoNeural": "晓晓 (女声-活泼)",
    "zh-CN-YunyangNeural": "云扬 (男声-新闻)",
    "zh-CN-XiaochenNeural": "晓辰 (女声-客服)",
}

DEFAULT_VOICE = "zh-CN-XiaoyiNeural"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'voice_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_asr_model():
    """获取语音识别模型（懒加载）"""
    global _asr_model
    if _asr_model is None:
        try:
            from funasr import AutoModel
            # 尝试使用本地模型或自动下载
            model_dir = "iic/SenseVoiceSmall"
            _asr_model = AutoModel(model=model_dir, trust_remote_code=True)
            print("✓ SenseVoice 语音识别模型加载成功")
        except Exception as e:
            print(f"✗ SenseVoice 模型加载失败: {e}")
            print("  请确保已安装 funasr: pip install funasr")
    return _asr_model


async def text_to_speech_async(text: str, voice: str, output_file: str):
    """异步文本转语音"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"TTS 合成失败: {e}")
        return False


def text_to_speech(text: str, voice: str = DEFAULT_VOICE) -> str:
    """文本转语音，返回音频文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"tts_{timestamp}.mp3")
    
    try:
        # 运行异步 TTS
        asyncio.run(text_to_speech_async(text, voice, output_file))
        if os.path.exists(output_file):
            return output_file
    except Exception as e:
        print(f"TTS 失败: {e}")
    
    return None


def speech_to_text(audio_file: str) -> str:
    """语音转文本"""
    model = get_asr_model()
    if model is None:
        return None
    
    try:
        result = model.generate(
            input=audio_file,
            cache={},
            language="auto",
            use_itn=False,
        )
        if result and len(result) > 0:
            text = result[0]['text'].split(">")[-1]
            return text.strip()
    except Exception as e:
        print(f"ASR 失败: {e}")
    
    return None


# ============================================================================
# REST API 端点
# ============================================================================

@voice_api.route('/api/voice/tts', methods=['POST', 'OPTIONS'])
def api_text_to_speech():
    """
    文本转语音 API
    
    Request:
    {
        "text": "你好，我是健康助手",
        "voice": "zh-CN-XiaoyiNeural"  // 可选
    }
    
    Response:
    {
        "success": true,
        "data": {
            "audio_url": "/api/voice/audio/tts_20241203_123456.mp3",
            "audio_base64": "...",  // 可选，如果请求中 include_base64=true
            "duration": 2.5
        }
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    data = request.json or {}
    text = data.get('text', '')
    voice = data.get('voice', DEFAULT_VOICE)
    include_base64 = data.get('include_base64', False)
    
    if not text:
        return jsonify({'success': False, 'error': '文本不能为空'}), 400
    
    try:
        audio_file = text_to_speech(text, voice)
        
        if audio_file and os.path.exists(audio_file):
            result = {
                'audio_url': f"/api/voice/audio/{os.path.basename(audio_file)}",
                'filename': os.path.basename(audio_file)
            }
            
            # 如果需要 base64
            if include_base64:
                with open(audio_file, 'rb') as f:
                    result['audio_base64'] = base64.b64encode(f.read()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({'success': False, 'error': 'TTS 合成失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@voice_api.route('/api/voice/asr', methods=['POST', 'OPTIONS'])
def api_speech_to_text():
    """
    语音转文本 API
    
    Request (multipart/form-data):
        audio: 音频文件
    
    或 Request (JSON):
    {
        "audio_base64": "..."  // base64 编码的音频
    }
    
    Response:
    {
        "success": true,
        "data": {
            "text": "识别出的文本"
        }
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    audio_file = None
    temp_file = None
    
    try:
        # 处理文件上传
        if 'audio' in request.files:
            audio = request.files['audio']
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.save(temp_file.name)
            audio_file = temp_file.name
        
        # 处理 base64 音频
        elif request.json and 'audio_base64' in request.json:
            audio_data = base64.b64decode(request.json['audio_base64'])
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.write(audio_data)
            temp_file.close()
            audio_file = temp_file.name
        
        else:
            return jsonify({'success': False, 'error': '请提供音频文件'}), 400
        
        # 执行语音识别
        text = speech_to_text(audio_file)
        
        if text:
            return jsonify({
                'success': True,
                'data': {'text': text}
            })
        else:
            return jsonify({'success': False, 'error': 'ASR 识别失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


@voice_api.route('/api/voice/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """提供音频文件下载"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='audio/mpeg')
    else:
        return jsonify({'error': '文件不存在'}), 404


@voice_api.route('/api/voice/voices', methods=['GET'])
def get_available_voices():
    """获取可用的语音列表"""
    return jsonify({
        'success': True,
        'data': {
            'voices': [
                {'id': k, 'name': v} for k, v in TTS_VOICES.items()
            ],
            'default': DEFAULT_VOICE
        }
    })


@voice_api.route('/api/voice/chat', methods=['POST', 'OPTIONS'])
def voice_chat():
    """
    语音对话 API（ASR + LLM + TTS 一体化）
    
    Request (multipart/form-data):
        audio: 音频文件
        voice: TTS 语音（可选）
    
    Response:
    {
        "success": true,
        "data": {
            "input_text": "用户说的话",
            "response_text": "AI 回复",
            "audio_url": "/api/voice/audio/xxx.mp3"
        }
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    voice = request.form.get('voice', DEFAULT_VOICE)
    temp_file = None
    
    try:
        # 1. 获取音频并进行 ASR
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': '请提供音频文件'}), 400
        
        audio = request.files['audio']
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio.save(temp_file.name)
        
        input_text = speech_to_text(temp_file.name)
        if not input_text:
            return jsonify({'success': False, 'error': 'ASR 识别失败'}), 500
        
        # 2. 调用 LLM 获取回复（使用讯飞星火或本地模型）
        response_text = call_llm_for_response(input_text)
        
        # 3. TTS 合成语音
        audio_file = text_to_speech(response_text, voice)
        
        result = {
            'input_text': input_text,
            'response_text': response_text,
        }
        
        if audio_file:
            result['audio_url'] = f"/api/voice/audio/{os.path.basename(audio_file)}"
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def call_llm_for_response(user_input: str) -> str:
    """调用 LLM 获取回复"""
    # 优先尝试使用讯飞星火 API
    try:
        from agents.spark_agent import SparkAgent
        agent = SparkAgent()
        response = agent.chat(user_input)
        if response:
            return response
    except Exception as e:
        print(f"讯飞星火调用失败: {e}")
    
    # 备用：使用简单回复
    health_keywords = ['健康', '血压', '心率', '血糖', '睡眠', '运动', '饮食']
    
    if any(kw in user_input for kw in health_keywords):
        return f"关于您提到的健康问题，我建议您保持规律作息，适量运动，均衡饮食。如有具体症状，建议咨询专业医生。"
    else:
        return f"您好！我是您的健康助手。您刚才说：{user_input}。请问有什么健康方面的问题需要我帮助吗？"


# 注册蓝图的函数
def register_voice_api(app):
    """注册语音 API 蓝图"""
    app.register_blueprint(voice_api)
    print("✓ 语音交互API蓝图注册成功")
