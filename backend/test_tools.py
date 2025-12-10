"""测试工具调用功能"""
from services.agents.agent_tools import agent_tools

print("=" * 50)
print("工具调用测试")
print("=" * 50)

# 测试1: 查询健康记录
print("\n1. 查询健康记录...")
result = agent_tools.call("query_health_records", user_id="test_user", record_type="all", days=7)
print(f"  成功: {result.success}")
print(f"  数据: {result.to_context()[:200]}...")

# 测试2: 查询健康趋势
print("\n2. 查询血压趋势...")
result = agent_tools.call("query_health_trend", user_id="test_user", metric="blood_pressure", period="7d")
print(f"  成功: {result.success}")
if result.success:
    print(f"  分析: {result.data.get('analysis', '')}")

# 测试3: 查询预警
print("\n3. 查询最近预警...")
result = agent_tools.call("query_recent_alerts", user_id="test_user")
print(f"  成功: {result.success}")
if result.success:
    print(f"  预警数: {result.data.get('total', 0)}")

# 测试4: 查询用药
print("\n4. 查询用药记录...")
result = agent_tools.call("query_medications", user_id="test_user")
print(f"  成功: {result.success}")
if result.success:
    print(f"  下次提醒: {result.data.get('next_reminder', '')}")

# 测试5: 获取工具描述
print("\n5. 工具列表...")
print(agent_tools.get_tools_description())

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
