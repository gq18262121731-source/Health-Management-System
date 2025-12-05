"""
测试知识库功能脚本
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.knowledge_base import knowledge_base

# 设置输出编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_search():
    """测试知识库搜索功能"""
    print("=" * 60)
    print("[测试] 知识库搜索功能")
    print("=" * 60)
    
    test_queries = [
        "高血压应该注意什么",
        "糖尿病患者如何运动",
        "血糖正常范围是多少",
        "如何控制体重",
        "骨质疏松的预防"
    ]
    
    for query in test_queries:
        print(f"\n[查询] {query}")
        print("-" * 60)
        results = knowledge_base.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n结果 {i} (相似度: {result.get('similarity_score', 0):.3f}):")
                print(f"  标题: {result.get('title', '未知')}")
                print(f"  内容预览: {result.get('content', '')[:150]}...")
        else:
            print("  未找到相关结果")
    
    print("\n" + "=" * 60)
    print("[完成] 测试完成")


def show_stats():
    """显示知识库统计信息"""
    print("\n[统计] 知识库信息:")
    print("-" * 60)
    
    docs = knowledge_base.list_documents()
    total_chunks = sum(doc.get("chunks_count", 0) for doc in docs)
    
    print(f"总文档数: {len(docs)}")
    print(f"总文档块: {total_chunks}")
    print(f"索引状态: {'已就绪' if knowledge_base.index is not None else '未初始化'}")
    
    print("\n文档列表:")
    for i, doc in enumerate(docs, 1):
        print(f"  {i}. {doc.get('title', '未知')} (类型: {doc.get('doc_type', '未知')}, 块数: {doc.get('chunks_count', 0)})")


if __name__ == "__main__":
    show_stats()
    print("\n")
    test_search()


