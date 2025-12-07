"""测试核心控制功能"""
import sys
sys.path.insert(0, '.')

print('=' * 50)
print('核心控制功能测试')
print('=' * 50)

from services.voice_control_service import voice_control_service
from services.agents.intent_recognizer import intent_recognizer

tests = [
    # 查看数据
    ('查看血压', '📊 查看数据'),
    ('看看今天的数据', '📊 查看数据'),
    ('查看血糖记录', '📊 查看数据'),
    # 打开报告
    ('打开报告', '📋 打开报告'),
    ('看报告', '📋 打开报告'),
    ('健康报告', '📋 打开报告'),
    # 一键呼救
    ('一键呼救', '🚨 紧急呼救'),
    ('救命', '🚨 紧急呼救'),
    ('帮帮我', '🚨 紧急呼救'),
]

for text, category in tests:
    intent = intent_recognizer.recognize(text)
    intent_type = intent.intent.value
    
    if intent_type.startswith('control_'):
        cmd = voice_control_service.parse_control_command(text, intent_type)
        print(f'\n{category}')
        print(f'  输入: "{text}"')
        print(f'  事件: {cmd.frontend_event}')
        print(f'  数据: {cmd.frontend_data}')
        print(f'  回复: {cmd.response_text}')
    else:
        print(f'\n❌ "{text}" 未识别为控制命令 (识别为: {intent_type})')

print('\n' + '=' * 50)
print('✅ 测试完成')
print('=' * 50)
