"""语音服务测试脚本"""
import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_tts():
    """测试 TTS 语音合成"""
    print("\n" + "="*50)
    print("🔊 测试 TTS (文本转语音)")
    print("="*50)
    
    from services.voice_service import voice_service
    
    test_text = "您好，我是您的AI健康助手。今天天气不错，记得多喝水，保持心情愉快。"
    print(f"测试文本: {test_text}")
    
    try:
        audio_id, audio_path = await voice_service.text_to_speech(
            text=test_text,
            voice="xiaoxiao",  # 温柔女声
            rate="-10%",
            volume="+10%"
        )
        print(f"✅ TTS 成功!")
        print(f"   音频ID: {audio_id}")
        print(f"   文件路径: {audio_path}")
        print(f"   文件大小: {os.path.getsize(audio_path) / 1024:.1f} KB")
        
        # 尝试播放
        try:
            import subprocess
            print("\n🎵 正在播放音频...")
            subprocess.Popen(['start', '', audio_path], shell=True)
        except:
            print("   (请手动打开音频文件播放)")
            
        return True
    except Exception as e:
        print(f"❌ TTS 失败: {e}")
        return False


async def test_asr():
    """测试 ASR 语音识别"""
    print("\n" + "="*50)
    print("🎤 测试 ASR (语音转文本)")
    print("="*50)
    
    from services.voice_service import voice_service
    
    if voice_service.asr_model is None:
        print("⚠️  ASR 模型未加载")
        print("   首次运行需要下载模型，请稍等...")
        
        # 尝试初始化
        voice_service._init_asr()
        
        if voice_service.asr_model is None:
            print("❌ ASR 模型加载失败")
            print("   请确保已安装: pip install funasr==1.1.12")
            return False
    
    print("✅ ASR 模型已就绪!")
    
    # 检查是否有测试音频
    test_audio = "./audio_cache/test.wav"
    if os.path.exists(test_audio):
        print(f"\n正在识别测试音频: {test_audio}")
        with open(test_audio, 'rb') as f:
            audio_data = f.read()
        
        try:
            text = await voice_service.speech_to_text(audio_data)
            print(f"✅ 识别结果: {text}")
            return True
        except Exception as e:
            print(f"❌ 识别失败: {e}")
            return False
    else:
        print(f"   提示: 将测试音频放到 {test_audio} 可进行识别测试")
        return True


def test_voices():
    """测试可用语音列表"""
    print("\n" + "="*50)
    print("📋 可用语音列表")
    print("="*50)
    
    from services.voice_service import voice_service
    
    voices = voice_service.get_available_voices()
    for v in voices["voices"]:
        print(f"   {v['id']:10} - {v['name']} ({v['gender']}) - {v['style']}")
    
    print(f"\n   默认语音: {voices['default']}")


async def main():
    print("\n" + "🎙️ "*10)
    print("   语音服务测试")
    print("🎙️ "*10)
    
    # 测试可用语音
    test_voices()
    
    # 测试 TTS
    tts_ok = await test_tts()
    
    # 测试 ASR
    asr_ok = await test_asr()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果")
    print("="*50)
    print(f"   TTS (语音合成): {'✅ 正常' if tts_ok else '❌ 异常'}")
    print(f"   ASR (语音识别): {'✅ 正常' if asr_ok else '⚠️ 需要配置'}")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
