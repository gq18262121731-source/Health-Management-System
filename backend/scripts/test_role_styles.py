"""测试三种用户角色的不同回复风格"""
import sys
sys.path.insert(0, '.')

from services.agents.multi_agent_service import multi_agent_service

print("=" * 70)
print("测试角色适配回复风格")
print("=" * 70)

query = "血压150/95高吗"
roles = ["elderly", "children", "community"]
role_names = {"elderly": "👴 老年人", "children": "👨‍👩‍👧 子女", "community": "🏥 社区"}

for role in roles:
    print(f"\n{'='*70}")
    print(f"【{role_names[role]}】模式")
    print(f"{'='*70}")
    print(f"问: {query}\n")
    
    result = multi_agent_service.process(
        user_input=query,
        user_id="test",
        user_role=role,
        mode="single"
    )
    
    print(f"智能体: {result.get('agent')}")
    print(f"回复:\n{result.get('response')}")
    print(f"\n字数: {len(result.get('response', ''))}")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
