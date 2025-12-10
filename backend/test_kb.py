"""测试知识库"""
from services.knowledge_base import knowledge_base

print("=" * 50)
print("知识库状态")
print("=" * 50)
print(f"嵌入模型: {'已加载' if knowledge_base.embedding_model else '未加载'}")
print(f"文档数量: {len(knowledge_base.list_documents())}")

print("\n文档列表:")
for doc in knowledge_base.list_documents():
    print(f"  - [{doc.get('doc_type')}] {doc.get('title')} ({doc.get('chunks_count')} 块)")

print("\n" + "=" * 50)
print("搜索测试: '血压高怎么办'")
print("=" * 50)
results = knowledge_base.search("血压高怎么办", top_k=3)
for i, r in enumerate(results):
    print(f"\n{i+1}. 【{r.get('category', '未分类')}】{r.get('title', '无标题')}")
    print(f"   相关度: {r.get('score', 0):.3f}")
    print(f"   内容: {r.get('content', '')[:100]}...")
