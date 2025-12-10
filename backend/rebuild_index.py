"""重建知识库 FAISS 索引"""
import json
from pathlib import Path
import numpy as np

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 先加载知识库模块
from services.knowledge_base import knowledge_base, faiss, HAS_DEPS

if not HAS_DEPS:
    print("错误: 依赖未安装")
    exit(1)

print("=" * 50)
print("重建知识库索引")
print("=" * 50)

# 读取所有文档
documents_dir = knowledge_base.documents_dir
all_chunks = []
all_embeddings = []

for doc_file in documents_dir.glob("*.json"):
    with open(doc_file, 'r', encoding='utf-8') as f:
        doc = json.load(f)
    
    title = doc.get("title", "")
    content = doc.get("content", "")
    doc_type = doc.get("doc_type", "text")
    source = doc.get("source", "")
    doc_id = doc.get("doc_id", "")
    metadata = doc.get("metadata", {})
    
    print(f"处理: {title}")
    
    # 分块
    chunks = knowledge_base._chunk_text(content)
    
    for i, chunk in enumerate(chunks):
        # 生成嵌入
        embedding = knowledge_base._get_embedding(chunk)
        all_embeddings.append(embedding)
        
        chunk_metadata = {
            "doc_id": doc_id,
            "chunk_index": i,
            "title": title,
            "content": chunk,
            "doc_type": doc_type,
            "source": source,
            "category": metadata.get("category", "综合健康"),
        }
        all_chunks.append(chunk_metadata)

print(f"\n共处理 {len(all_chunks)} 个文本块")

# 创建 FAISS 索引
if all_embeddings:
    embeddings_array = np.vstack(all_embeddings).astype('float32')
    
    # 创建索引 (使用内积，适合归一化向量)
    index = faiss.IndexFlatIP(knowledge_base.embedding_dim)
    index.add(embeddings_array)
    
    # 保存索引 (使用临时目录避免中文路径问题)
    import os
    import tempfile
    index_dir = os.path.join(tempfile.gettempdir(), "health_kb_index")
    os.makedirs(index_dir, exist_ok=True)
    index_file = os.path.join(index_dir, "faiss.index")
    metadata_file = os.path.join(index_dir, "metadata.json")
    
    faiss.write_index(index, index_file)
    
    # 保存元数据
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"索引已保存: {index_file}")
    print(f"元数据已保存: {metadata_file}")
    
    # 更新内存中的索引
    knowledge_base.index = index
    knowledge_base.metadata = all_chunks
    
    # 测试搜索
    print("\n" + "=" * 50)
    print("测试搜索: '血压高怎么办'")
    print("=" * 50)
    results = knowledge_base.search("血压高怎么办", top_k=3)
    for i, r in enumerate(results):
        print(f"\n{i+1}. 【{r.get('category', '未分类')}】{r.get('title', '无标题')}")
        print(f"   相关度: {r.get('similarity_score', 0):.3f}")
        print(f"   内容: {r.get('content', '')[:80]}...")
else:
    print("没有文档需要索引")
