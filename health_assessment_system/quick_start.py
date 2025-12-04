#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 多模型健康评估系统
Quick Start Script - Multi-Model Health Assessment System

本脚本提供了系统的快速启动和测试功能。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """检查依赖是否安装"""
    print("=" * 60)
    print("检查依赖...")
    print("=" * 60)
    
    required = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy',
        'sklearn': 'scikit-learn',
    }
    
    optional = {
        'flask': 'flask',
        'flask_cors': 'flask-cors',
        'skfuzzy': 'scikit-fuzzy',
    }
    
    missing_required = []
    missing_optional = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (必需)")
            missing_required.append(package)
    
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ○ {package} (可选)")
            missing_optional.append(package)
    
    print()
    
    if missing_required:
        print("缺少必需依赖，请运行:")
        print(f"  pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print("缺少可选依赖，如需完整功能请运行:")
        print(f"  pip install {' '.join(missing_optional)}")
    
    print("✓ 依赖检查通过")
    return True


def test_assessment_engine():
    """测试健康评估引擎"""
    print("\n" + "=" * 60)
    print("测试健康评估引擎")
    print("=" * 60)
    
    try:
        from health_assessment_system import HealthAssessmentEngine
        from modules.assessment_config import AssessmentPeriod, TimeWindow
        from modules.report_generation import ReportType, ReportFormat
        
        # 创建引擎
        print("\n1. 创建评估引擎...")
        engine = HealthAssessmentEngine()
        print("   ✓ 引擎创建成功")
        
        # 运行评估
        print("\n2. 运行健康评估...")
        result = engine.run_scheduled_assessment(
            user_id="TEST_USER",
            period=AssessmentPeriod.MONTHLY,
            time_window=TimeWindow.LAST_30_DAYS
        )
        print(f"   ✓ 评估完成")
        print(f"   - 评估ID: {result.assessment_id}")
        print(f"   - 综合评分: {result.overall_score:.1f}/100")
        print(f"   - 健康等级: {result.health_level.value}")
        
        # 生成报告
        print("\n3. 生成评估报告...")
        report = engine.generate_report(
            assessment_id=result.assessment_id,
            user_id=result.user_id,
            report_type=ReportType.ELDERLY,
            report_format=ReportFormat.TEXT
        )
        print("   ✓ 报告生成成功")
        print("\n" + "-" * 40)
        print(report[:500] + "..." if len(report) > 500 else report)
        print("-" * 40)
        
        # 获取可视化数据
        print("\n4. 获取可视化数据...")
        viz_data = engine.get_visualization_data(
            assessment_id=result.assessment_id,
            user_id=result.user_id
        )
        print("   ✓ 可视化数据获取成功")
        print(f"   - 维度评分: {viz_data.get('dimension_scores', {})}")
        
        print("\n✓ 健康评估引擎测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_agent_system():
    """测试多智能体系统"""
    print("\n" + "=" * 60)
    print("测试多智能体系统")
    print("=" * 60)
    
    try:
        from agents import MultiAgentSystem
        
        # 创建系统
        print("\n1. 创建多智能体系统...")
        system = MultiAgentSystem(
            user_id="TEST_USER",
            user_name="测试用户",
            enable_assessment=False  # 禁用评估集成以加快测试
        )
        print("   ✓ 系统创建成功")
        
        # 获取问候语
        print("\n2. 获取问候语...")
        greeting = system.get_greeting()
        print(f"   {greeting}")
        
        # 测试对话
        print("\n3. 测试对话...")
        test_messages = [
            "你好",
            "我最近血压有点高",
            "晚上睡不好觉怎么办？"
        ]
        
        for msg in test_messages:
            print(f"\n   用户: {msg}")
            response = system.chat(msg)
            # 截取响应的前200个字符
            short_response = response[:200] + "..." if len(response) > 200 else response
            print(f"   AI: {short_response}")
        
        # 获取智能体信息
        print("\n4. 获取智能体信息...")
        agents_info = system.get_agents_info()
        print(f"   已注册智能体: {len(agents_info)} 个")
        for info in agents_info:
            print(f"   - {info.get('name', 'Unknown')}: {info.get('role', 'Unknown')}")
        
        print("\n✓ 多智能体系统测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_web_server():
    """启动Web服务器"""
    print("\n" + "=" * 60)
    print("启动Web服务器")
    print("=" * 60)
    
    try:
        from web_digital_human.app import app
        
        print("\n  🌐 Web 3D数字人服务器")
        print("  访问地址: http://localhost:5000")
        print("  按 Ctrl+C 停止服务")
        print()
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"\n✗ 启动失败: 缺少依赖 - {e}")
        print("  请运行: pip install flask flask-cors")
    except Exception as e:
        print(f"\n✗ 启动失败: {e}")


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("交互式演示 - 与AI数字人对话")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'report' 获取健康报告")
    print("-" * 60)
    
    try:
        from agents import MultiAgentSystem
        
        system = MultiAgentSystem(
            user_id="DEMO_USER",
            user_name="演示用户",
            enable_assessment=False
        )
        
        print(f"\n{system.get_greeting()}\n")
        
        while True:
            try:
                user_input = input("您: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n再见！祝您健康！")
                    break
                
                response = system.chat(user_input)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n\n再见！祝您健康！")
                break
                
    except Exception as e:
        print(f"\n✗ 演示失败: {e}")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("  多模型健康评估系统 - 快速启动")
    print("=" * 60)
    print()
    print("  请选择操作:")
    print()
    print("  1. 检查依赖")
    print("  2. 测试健康评估引擎")
    print("  3. 测试多智能体系统")
    print("  4. 启动Web服务器")
    print("  5. 交互式演示")
    print("  6. 运行所有测试")
    print("  0. 退出")
    print()


def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请输入选项 (0-6): ").strip()
            
            if choice == '0':
                print("\n再见！")
                break
            elif choice == '1':
                check_dependencies()
            elif choice == '2':
                test_assessment_engine()
            elif choice == '3':
                test_multi_agent_system()
            elif choice == '4':
                start_web_server()
            elif choice == '5':
                interactive_demo()
            elif choice == '6':
                print("\n运行所有测试...")
                check_dependencies()
                test_assessment_engine()
                test_multi_agent_system()
                print("\n" + "=" * 60)
                print("所有测试完成")
                print("=" * 60)
            else:
                print("\n无效选项，请重新输入")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()
