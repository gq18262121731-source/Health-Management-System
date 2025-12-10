"""测试 LLM 意图识别"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.agents.intent_recognizer import intent_recognizer

print("=" * 60)
print("LLM 意图识别测试")
print("=" * 60)

# 测试用例
test_cases = [
    # 简单明确的
    "我血压150/95",
    "最近睡不好",
    "吃什么能降血糖",
    
    # 复杂多意图的
    "我血压有点高，而且最近心情也不好，晚上睡不着",
    "糖尿病人能吃什么水果，运动有什么要注意的",
    
    # 模糊的
    "感觉不太舒服",
    "最近身体不太好",
    
    # 情绪类
    "一个人在家好无聊",
    "最近压力好大，感觉撑不住了",
]

print("\n【规则匹配 vs LLM识别 对比】\n")

for text in test_cases:
    print(f"输入: {text}")
    print("-" * 50)
    
    # 规则匹配
    rule_result = intent_recognizer.recognize(text, use_llm=False)
    print(f"  规则匹配: {rule_result.intent.value} ({rule_result.confidence:.2f})")
    print(f"    次要意图: {[i.value for i in rule_result.sub_intents]}")
    print(f"    实体: {rule_result.entities}")
    
    # LLM识别
    print("  正在调用LLM...")
    llm_result = intent_recognizer.recognize_with_llm(text)
    print(f"  LLM识别: {llm_result.intent.value} ({llm_result.confidence:.2f})")
    print(f"    次要意图: {[i.value for i in llm_result.sub_intents]}")
    print(f"    实体: {llm_result.entities}")
    print(f"    需要多智能体: {llm_result.requires_multi_agent}")
    
    print()

print("=" * 60)
print("测试完成！")
print("=" * 60)
