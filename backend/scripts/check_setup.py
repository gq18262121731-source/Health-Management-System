"""
AI问诊功能配置检查脚本
检查所有必需的配置是否正确
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def check_environment():
    """检查环境配置"""
    print("=" * 60)
    print("[检查1] 环境变量配置")
    print("=" * 60)
    
    from config.settings import settings
    
    checks = []
    
    # 检查AI配置
    print(f"\nAI服务提供商: {settings.AI_PROVIDER}")
    if settings.AI_PROVIDER == 'deepseek':
        api_key = settings.DEEPSEEK_API_KEY
        if api_key and api_key != 'None':
            print(f"[通过] DeepSeek API Key已配置: {api_key[:10]}...")
            checks.append(True)
        else:
            print("[失败] DeepSeek API Key未配置")
            checks.append(False)
    
    # 检查数据库配置
    db_url = settings.DATABASE_URL
    if db_url:
        print(f"[通过] 数据库配置: {db_url}")
        checks.append(True)
    else:
        print("[失败] 数据库配置缺失")
        checks.append(False)
    
    return all(checks)


def check_dependencies():
    """检查依赖安装"""
    print("\n" + "=" * 60)
    print("[检查2] Python依赖")
    print("=" * 60)
    
    required_packages = {
        'httpx': 'HTTP客户端',
        'fastapi': 'Web框架',
        'uvicorn': 'ASGI服务器',
    }
    
    optional_packages = {
        'faiss': '向量数据库',
        'sentence_transformers': '嵌入模型',
        'PyPDF2': 'PDF处理',
        'docx': 'Word文档处理',
    }
    
    checks = []
    
    print("\n必需依赖:")
    for package, desc in required_packages.items():
        try:
            __import__(package)
            print(f"  [通过] {package} - {desc}")
            checks.append(True)
        except ImportError:
            print(f"  [失败] {package} - {desc} (未安装)")
            checks.append(False)
    
    print("\n可选依赖 (知识库功能):")
    for package, desc in optional_packages.items():
        try:
            __import__(package)
            print(f"  [通过] {package} - {desc}")
        except ImportError:
            print(f"  [警告] {package} - {desc} (未安装，知识库功能将受限)")
    
    return all(checks)


def check_knowledge_base():
    """检查知识库"""
    print("\n" + "=" * 60)
    print("[检查3] 知识库配置")
    print("=" * 60)
    
    try:
        from services.knowledge_base import knowledge_base
        
        docs = knowledge_base.list_documents()
        total_chunks = sum(doc.get("chunks_count", 0) for doc in docs)
        
        print(f"\n知识库状态:")
        print(f"  文档数量: {len(docs)}")
        print(f"  文档块数: {total_chunks}")
        print(f"  索引状态: {'已就绪' if knowledge_base.index is not None else '未初始化'}")
        
        if len(docs) > 0:
            print(f"\n[通过] 知识库已初始化，包含 {len(docs)} 个文档")
            return True
        else:
            print(f"\n[警告] 知识库为空，建议导入文档")
            return False
            
    except Exception as e:
        print(f"\n[失败] 知识库检查失败: {str(e)}")
        return False


def check_ai_service():
    """检查AI服务"""
    print("\n" + "=" * 60)
    print("[检查4] AI服务配置")
    print("=" * 60)
    
    try:
        from services.ai_service import ai_service
        
        print(f"\nAI服务状态:")
        print(f"  提供商: {ai_service.provider or '未配置'}")
        print(f"  API Key: {'已配置' if ai_service.api_key else '未配置'}")
        print(f"  模式: {'真实API' if ai_service.provider and ai_service.api_key else '模拟模式'}")
        
        if ai_service.provider and ai_service.api_key:
            print(f"\n[通过] AI服务配置正常 ({ai_service.provider})")
            return True
        else:
            print(f"\n[警告] AI服务将使用模拟模式")
            return False
            
    except Exception as e:
        print(f"\n[失败] AI服务检查失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("AI问诊功能配置检查")
    print("=" * 60)
    
    results = []
    
    results.append(("环境变量", check_environment()))
    results.append(("Python依赖", check_dependencies()))
    results.append(("知识库", check_knowledge_base()))
    results.append(("AI服务", check_ai_service()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("[检查结果汇总]")
    print("=" * 60)
    
    for name, result in results:
        status = "[通过]" if result else "[警告/失败]"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n[成功] 所有配置正常，可以启动服务！")
    else:
        print("\n[提示] 请根据上述检查结果完善配置")
    
    print("\n启动服务:")
    print("  cd backend")
    print("  python main.py")


if __name__ == "__main__":
    main()


