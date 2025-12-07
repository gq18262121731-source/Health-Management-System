"""测试多智能体系统"""
import sys
sys.path.insert(0, '.')

from services.agents.multi_agent_service import multi_agent_service

print("=" * 50)
print("多智能体系统检查")
print("=" * 50)

# 检查注册的智能体
print(f"\n注册智能体数量: {len(multi_agent_service.coordinator.agents)}")
for agent in multi_agent_service.coordinator.agents.values():
    print(f"  {agent.avatar} {agent.name}: {agent.role.value}")
    print(f"     能力: {', '.join(agent.capabilities)}")

# 测试路由
print("\n" + "=" * 50)
print("路由测试")
print("=" * 50)

test_cases = [
    ("血压150高吗", "慢病专家"),
    ("老年人怎么锻炼", "生活教练"),
    ("我最近很焦虑", "心理关怀师"),
    ("你好", "健康管家"),
]

all_passed = True
for query, expected_agent in test_cases:
    result = multi_agent_service.process(query, user_id="test")
    actual_agent = result.get("agent", "")
    confidence = result.get("confidence", 0)
    passed = expected_agent in actual_agent
    status = "✅" if passed else "❌"
    print(f"\n{status} 问: {query}")
    print(f"   期望: {expected_agent}")
    print(f"   实际: {actual_agent} (置信度: {confidence:.2f})")
    if not passed:
        all_passed = False

# 测试多智能体协作
print("\n" + "=" * 50)
print("多智能体协作测试")
print("=" * 50)

result = multi_agent_service.process(
    "血压高还很担心怎么办", 
    user_id="test", 
    mode="multi"
)
print(f"\n问: 血压高还很担心怎么办")
print(f"模式: {result.get('mode')}")
print(f"参与智能体: {result.get('agent')}")
print(f"智能体数量: {result.get('agent_count', 1)}")

print("\n" + "=" * 50)
if all_passed:
    print("✅ 所有测试通过!")
else:
    print("❌ 部分测试失败")
print("=" * 50)
