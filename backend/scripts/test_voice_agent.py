"""测试语音智能体服务"""
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("语音智能体服务测试")
print("=" * 70)

from services.voice_agent_service import (
    voice_agent_service, 
    WakeWordDetector,
    VoiceEmotionAnalyzer,
    ElderlyVoiceSettings,
    VoiceEmotion
)

# ============================================================================
# 1. 唤醒词检测测试
# ============================================================================
print("\n[1] 唤醒词检测测试")
print("-" * 50)

wake_word_tests = [
    "小康小康，今天天气怎么样",
    "小康，我血压有点高",
    "健康助手帮我查一下",
    "你好",  # 不是唤醒词
    "晓康帮帮我",  # 模糊匹配
]

for text in wake_word_tests:
    is_wake, wake_word = WakeWordDetector.detect(text)
    status = "✅" if is_wake else "❌"
    print(f"{status} '{text}' → 唤醒词: {wake_word}")
    if is_wake:
        cleaned = WakeWordDetector.remove_wake_word(text)
        print(f"   移除唤醒词后: '{cleaned}'")

# ============================================================================
# 2. 语音情感分析测试
# ============================================================================
print("\n[2] 语音情感分析测试")
print("-" * 50)

emotion_tests = [
    "我今天感觉很开心，血压也正常",
    "唉，我好担心我的血糖",
    "哎呀，我头疼得厉害，怎么办",
    "我最近太累了，睡不好",
    "烦死了，药总是忘记吃",
    "救命啊，胸口好痛",
]

emotion_labels = {
    "neutral": "😐 平静",
    "happy": "😊 开心",
    "sad": "😢 悲伤",
    "anxious": "😰 焦虑",
    "angry": "😠 生气",
    "tired": "😫 疲惫",
    "urgent": "🚨 紧急",
}

for text in emotion_tests:
    emotion, confidence = VoiceEmotionAnalyzer.analyze(text)
    label = emotion_labels.get(emotion.value, emotion.value)
    print(f"'{text}'")
    print(f"   → {label} (置信度: {confidence:.2f})")

# ============================================================================
# 3. 适老化语音设置测试
# ============================================================================
print("\n[3] 适老化语音设置测试")
print("-" * 50)

styles = ["default", "calm", "energetic", "news"]
emotions = [None, VoiceEmotion.ANXIOUS, VoiceEmotion.HAPPY, VoiceEmotion.URGENT]

print("基础语音风格:")
for style in styles:
    settings = ElderlyVoiceSettings.get_voice_settings(style)
    print(f"  {style}: voice={settings['voice']}, rate={settings['rate']}, volume={settings['volume']}")

print("\n情感调整后的语音设置 (default风格):")
for emotion in emotions:
    settings = ElderlyVoiceSettings.get_voice_settings("default", emotion)
    emotion_name = emotion.value if emotion else "无"
    print(f"  情感={emotion_name}: rate={settings['rate']}, volume={settings['volume']}")

# ============================================================================
# 4. 完整语音对话流程测试（模拟）
# ============================================================================
print("\n[4] 完整语音对话流程测试（模拟文本输入）")
print("-" * 50)

# 模拟文本输入（实际应该是语音ASR后的结果）
test_inputs = [
    ("小康小康", "elderly"),
    ("小康小康，我血压150高吗", "elderly"),
    ("健康助手，老人血压150/95需要注意什么", "children"),
    ("我最近很焦虑睡不好怎么办", "elderly"),
]

from services.agents.multi_agent_service import multi_agent_service

for text, role in test_inputs:
    print(f"\n输入: '{text}' (角色: {role})")
    
    # 1. 唤醒词检测
    is_wake, wake_word = WakeWordDetector.detect(text)
    if is_wake:
        text = WakeWordDetector.remove_wake_word(text)
        print(f"  ✓ 检测到唤醒词: {wake_word}")
    
    if not text.strip():
        print(f"  → 回复: 我在呢，有什么可以帮您的吗？")
        continue
    
    # 2. 情感分析
    emotion, conf = VoiceEmotionAnalyzer.analyze(text)
    print(f"  ✓ 情感分析: {emotion.value} (置信度: {conf:.2f})")
    
    # 3. 多Agent处理
    result = multi_agent_service.process(text, user_id="test", user_role=role)
    print(f"  ✓ 智能体: {result.get('agent')}")
    print(f"  ✓ 意图: {result.get('intent', {}).get('intent', 'unknown')}")
    
    # 4. 获取语音设置
    voice_settings = ElderlyVoiceSettings.get_voice_settings("default", emotion)
    print(f"  ✓ 语音设置: {voice_settings['voice']}, rate={voice_settings['rate']}")
    
    # 5. 回复预览
    response = result.get("response", "")[:100]
    print(f"  → 回复预览: {response}...")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)

# ============================================================================
# 5. API接口列表
# ============================================================================
print("\n[5] 语音智能体API接口")
print("-" * 50)
apis = [
    ("POST", "/api/v1/voice-agent/dialog", "语音对话（完整流程）"),
    ("POST", "/api/v1/voice-agent/tts/emotional", "情感感知TTS"),
    ("POST", "/api/v1/voice-agent/analyze/emotion", "语音情感分析"),
    ("POST", "/api/v1/voice-agent/detect/wake-word", "唤醒词检测"),
    ("GET", "/api/v1/voice-agent/settings/voices", "获取语音风格"),
    ("GET", "/api/v1/voice-agent/settings/wake-words", "获取唤醒词列表"),
]

for method, path, desc in apis:
    print(f"  {method:6} {path:45} - {desc}")
