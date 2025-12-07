"""测试意图识别 + 多智能体 + 讯飞星火"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("测试意图识别 + 多智能体 + 讯飞星火")
print("=" * 60)

# 测试讯飞星火服务
print("\n[1] 测试讯飞星火服务连接...")
from services.spark_service import spark_service

response = spark_service.chat(
    user_input="你好",
    system_prompt="你是一个友好的助手，用一句话回复"
)
print(f"星火回复: {response[:100]}...")
print("✅ 讯飞星火服务正常")

# 测试意图识别
print("\n[2] 测试意图识别...")
from services.agents.intent_recognizer import intent_recognizer

intent_tests = [
    ("血压150/95高吗", "blood_pressure"),
    ("血糖6.8正常吗", "blood_sugar"),
    ("老年人怎么运动", "exercise"),
    ("我最近很焦虑", "anxiety"),
    ("血压高还很担心睡不好", "blood_pressure"),  # 多意图
]

for query, expected_intent in intent_tests:
    result = intent_recognizer.recognize(query)
    status = "✅" if result.intent.value == expected_intent else "❌"
    print(f"{status} '{query}' → {result.intent.value} (置信度:{result.confidence:.2f})")
    if result.entities:
        print(f"   实体: {result.entities}")
    if result.requires_multi_agent:
        print(f"   需要多Agent: {[i.value for i in result.sub_intents]}")

# 测试完整流程（意图识别 + 智能体 + LLM）
print("\n[3] 测试完整流程（意图识别 + 智能体 + 讯飞星火）...")
from services.agents.multi_agent_service import multi_agent_service

test_cases = [
    ("血压150/95高吗", "慢病专家", "blood_pressure"),
    ("老年人怎么运动", "生活教练", "exercise"),
    ("我最近很焦虑", "心理关怀师", "anxiety"),
    ("你好", "健康管家", "greeting"),
]

for query, expected_agent, expected_intent in test_cases:
    print(f"\n问: {query}")
    
    result = multi_agent_service.process(query, user_id="test", mode="auto")
    agent = result.get("agent", "")
    intent = result.get("intent", {}).get("intent", "")
    mode = result.get("mode", "")
    response = result.get("response", "")[:100]
    
    print(f"  意图: {intent}")
    print(f"  模式: {mode}")
    print(f"  智能体: {agent}")
    print(f"  回复: {response}...")
    
    agent_ok = expected_agent in agent
    intent_ok = intent == expected_intent
    print(f"  {'✅' if agent_ok and intent_ok else '❌'} 路由{'正确' if agent_ok else '错误'}, 意图{'正确' if intent_ok else '错误'}")

# 测试多智能体协作
print("\n[4] 测试多智能体协作...")
multi_query = "血压高还很担心睡不好怎么办"
print(f"问: {multi_query}")
result = multi_agent_service.process(multi_query, user_id="test", mode="auto")
print(f"  意图: {result.get('intent', {}).get('intent', '')}")
print(f"  模式: {result.get('mode', '')}")
print(f"  智能体: {result.get('agent', '')}")
print(f"  回复长度: {len(result.get('response', ''))}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
