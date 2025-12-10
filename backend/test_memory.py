"""测试对话记忆功能"""
from services.conversation_memory import conversation_memory

print("=" * 50)
print("对话记忆测试")
print("=" * 50)

# 模拟会话ID
session_id = "test_user_001"

# 模拟用户对话
test_messages = [
    ("user", "我今年65岁，有高血压"),
    ("assistant", "了解了，您65岁有高血压。请问您目前血压是多少？"),
    ("user", "血压150/95"),
    ("assistant", "您的血压150/95偏高，建议控制饮食，减少盐分摄入。"),
    ("user", "那我能吃什么"),
]

print("\n1. 添加对话消息...")
for role, content in test_messages:
    conversation_memory.add_message(session_id, role, content)
    print(f"  [{role}]: {content[:30]}...")

print("\n2. 查看用户档案（自动提取）...")
profile = conversation_memory.get_user_profile(session_id)
print(f"  用户档案: {profile}")

print("\n3. 获取上下文摘要...")
summary = conversation_memory.get_context_summary(session_id)
print(f"  摘要:\n{summary}")

print("\n4. 获取LLM格式的对话历史...")
history = conversation_memory.get_chat_history_for_llm(session_id, limit=3)
for msg in history:
    print(f"  [{msg['role']}]: {msg['content'][:40]}...")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
