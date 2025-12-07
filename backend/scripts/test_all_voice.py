"""语音智能体完整功能测试"""
import sys
sys.path.insert(0, '.')

print('=' * 60)
print('语音智能体完整功能测试')
print('=' * 60)

# 1. 唤醒词测试
print('\n[1] 唤醒词检测 (糖豆)')
print('-' * 40)
from services.voice_agent_service import WakeWordDetector
tests = ['糖豆糖豆你好', '糖豆我要测血压', '你好']
for t in tests:
    r = WakeWordDetector.detect(t)
    print(f'  "{t}" → {"✅ " + r[1] if r[0] else "❌ 不是唤醒词"}')

# 2. 情感分析测试
print('\n[2] 情感分析')
print('-' * 40)
from services.voice_agent_service import VoiceEmotionAnalyzer
tests = [
    ('我今天很开心', '😊'),
    ('好担心我的血压', '😰'),
    ('累死了睡不好', '😫'),
]
for t, emoji in tests:
    e, c = VoiceEmotionAnalyzer.analyze(t)
    print(f'  "{t}" → {emoji} {e.value} ({c:.2f})')

# 3. 语音控制测试
print('\n[3] 语音控制命令')
print('-' * 40)
from services.voice_control_service import voice_control_service
from services.agents.intent_recognizer import intent_recognizer

controls = [
    '打开首页',
    '查看血压', 
    '测一下血糖',
    '打给儿子',
    '放音乐',
    '大声点',
    '停止',
]
for text in controls:
    intent = intent_recognizer.recognize(text)
    if intent.intent.value.startswith('control_'):
        cmd = voice_control_service.parse_control_command(text, intent.intent.value)
        print(f'  ✅ "{text}"')
        print(f'     事件: {cmd.frontend_event} → {cmd.frontend_data}')
        print(f'     回复: {cmd.response_text}')
    else:
        print(f'  ❌ "{text}" → 非控制命令')

# 4. 多Agent问答测试
print('\n[4] 多Agent问答 (非控制命令走AI)')
print('-' * 40)
from services.agents.multi_agent_service import multi_agent_service

queries = [
    ('血压150高吗', 'elderly'),
    ('睡眠不好怎么办', 'elderly'),
]
for q, role in queries:
    r = multi_agent_service.process(q, user_role=role, mode='single')
    print(f'  问: "{q}"')
    print(f'  智能体: {r["agent"]}')
    resp = r["response"][:80].replace('\n', ' ')
    print(f'  回复: {resp}...\n')

print('=' * 60)
print('✅ 所有功能测试完成!')
print('=' * 60)
