"""
多智能体数字人系统演示
=====================

本脚本演示多智能体数字人系统的核心功能。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import MultiAgentSystem


def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def print_response(response: str):
    """格式化打印响应"""
    print("-" * 40)
    print(response)
    print("-" * 40)


def demo_basic_chat():
    """演示基础对话"""
    print_separator("🗣️ 基础对话演示")
    
    # 创建系统
    system = MultiAgentSystem(
        user_id="DEMO001",
        user_name="张大爷",
        enable_assessment=False  # 演示时禁用评估引擎
    )
    
    # 显示问候
    print("\n📢 系统问候:")
    print_response(system.get_greeting())
    
    # 测试对话
    test_messages = [
        "你好",
        "我最近血压有点高，该怎么办？",
        "晚上睡不好觉怎么办？",
        "我有点担心自己的身体"
    ]
    
    for msg in test_messages:
        print(f"\n👤 用户: {msg}")
        response = system.chat(msg)
        print(f"\n🤖 数字人:")
        print_response(response)
        input("按回车继续...")


def demo_multi_agent():
    """演示多智能体协作"""
    print_separator("🤝 多智能体协作演示")
    
    system = MultiAgentSystem(
        user_id="DEMO002",
        user_name="李阿姨",
        enable_assessment=False
    )
    
    # 展示智能体团队
    print("\n📋 智能体团队:")
    for agent in system.get_agents_info():
        print(f"  {agent['avatar']} {agent['name']}")
        print(f"     角色: {agent['role']}")
        print(f"     简介: {agent['description']}")
        print()
    
    # 专家会诊演示
    print("\n🏥 专家会诊模式:")
    complex_query = "我血压高、血糖也高，还睡不好，请给我全面的建议"
    print(f"\n👤 用户: {complex_query}")
    
    response = system.chat(complex_query)
    print(f"\n🤖 专家团队响应:")
    print_response(response)


def demo_health_butler():
    """演示健康管家功能"""
    print_separator("👨‍⚕️ 健康管家演示")
    
    system = MultiAgentSystem(
        user_id="DEMO003",
        enable_assessment=False
    )
    
    queries = [
        "给我一些运动建议",
        "饮食上需要注意什么",
        "帮我做个健康评估"
    ]
    
    for query in queries:
        print(f"\n👤 用户: {query}")
        response = system.chat(query)
        print(f"\n🤖 健康管家:")
        print_response(response)
        input("按回车继续...")


def demo_emotional_support():
    """演示心理关怀功能"""
    print_separator("🤗 心理关怀演示")
    
    system = MultiAgentSystem(
        user_id="DEMO004",
        user_name="王奶奶",
        enable_assessment=False
    )
    
    emotional_queries = [
        "我最近总是睡不着，心里很烦",
        "孩子们都忙，我一个人有点孤单",
        "我担心自己的病会越来越严重"
    ]
    
    for query in emotional_queries:
        print(f"\n👤 用户: {query}")
        response = system.chat(query)
        print(f"\n🤗 心理关怀师:")
        print_response(response)
        input("按回车继续...")


def demo_chronic_disease():
    """演示慢病管理功能"""
    print_separator("🩺 慢病管理演示")
    
    system = MultiAgentSystem(
        user_id="DEMO005",
        enable_assessment=False
    )
    
    # 更新健康数据
    system.update_health_data("blood_pressure", {
        "systolic": 145,
        "diastolic": 92
    })
    
    chronic_queries = [
        "我的血压情况怎么样",
        "高血压需要注意什么",
        "血糖高怎么控制",
        "吃药需要注意什么"
    ]
    
    for query in chronic_queries:
        print(f"\n👤 用户: {query}")
        response = system.chat(query)
        print(f"\n🩺 慢病专家:")
        print_response(response)
        input("按回车继续...")


def interactive_mode():
    """交互模式"""
    print_separator("💬 交互对话模式")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清空对话历史")
    print("输入 'info' 查看会话信息")
    
    system = MultiAgentSystem(
        user_id="INTERACTIVE",
        enable_assessment=False
    )
    
    print(f"\n🤖 {system.get_greeting()}\n")
    
    while True:
        try:
            user_input = input("👤 您: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！祝您身体健康！")
                break
            
            if user_input.lower() == 'clear':
                system.clear_conversation()
                print("✓ 对话已清空\n")
                continue
            
            if user_input.lower() == 'info':
                info = system.get_session_info()
                print(f"\n📊 会话信息:")
                print(f"   用户ID: {info['user_id']}")
                print(f"   会话时长: {info['duration_seconds']}秒")
                print(f"   消息数: {info['conversation']['total_messages']}\n")
                continue
            
            response = system.chat(user_input)
            print(f"\n🤖 数字人:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！祝您身体健康！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}\n")


def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║          🏥  多智能体数字人系统 - 演示程序  🏥            ║
    ║                                                            ║
    ║     智能体团队：                                           ║
    ║       👨‍⚕️ 健康管家 - 主要交互入口                         ║
    ║       🩺 慢病专家 - 慢性病管理指导                        ║
    ║       🏃 生活教练 - 运动睡眠饮食                          ║
    ║       🤗 心理关怀 - 情感支持陪伴                          ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n请选择演示内容：")
        print("  1. 基础对话演示")
        print("  2. 多智能体协作演示")
        print("  3. 健康管家演示")
        print("  4. 心理关怀演示")
        print("  5. 慢病管理演示")
        print("  6. 交互对话模式")
        print("  0. 退出")
        
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == '1':
            demo_basic_chat()
        elif choice == '2':
            demo_multi_agent()
        elif choice == '3':
            demo_health_butler()
        elif choice == '4':
            demo_emotional_support()
        elif choice == '5':
            demo_chronic_disease()
        elif choice == '6':
            interactive_mode()
        elif choice == '0':
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("❌ 无效选项，请重新输入")


if __name__ == "__main__":
    main()
