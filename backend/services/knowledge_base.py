"""知识库服务 - RAG（检索增强生成）"""
import logging
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库类，实现文档向量化和检索功能"""
    
    def __init__(self, kb_dir: str = "./knowledge_base"):
        """
        初始化知识库
        
        Args:
            kb_dir: 知识库存储目录
        """
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(exist_ok=True)
        
        # 存储目录
        self.vectors_dir = self.kb_dir / "vectors"
        self.vectors_dir.mkdir(exist_ok=True)
        
        self.documents_dir = self.kb_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        
        self.index_file = self.vectors_dir / "faiss.index"
        self.metadata_file = self.vectors_dir / "metadata.json"
        
        # 嵌入模型（使用中文优化的模型）
        self.embedding_model = None
        self.embedding_dim = 768  # m3e-base的维度
        
        # FAISS索引
        self.index = None
        self.metadata = []
        
        # 初始化
        if HAS_DEPS:
            self._init_model()
            self._load_index()
        else:
            logger.warning("知识库依赖未安装，将使用模拟模式。请运行: pip install faiss-cpu sentence-transformers numpy")
    
    def _init_model(self):
        """初始化嵌入模型"""
        try:
            # 使用m3e-base模型（中文优化）
            # 如果下载失败，可以手动下载或使用其他模型
            model_name = "moka-ai/m3e-base"
            logger.info(f"正在加载嵌入模型: {model_name}")
            
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"嵌入模型加载成功，维度: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {str(e)}")
            logger.info("将使用模拟嵌入模式")
            self.embedding_model = None
    
    def _load_index(self):
        """加载FAISS索引"""
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                # 加载索引
                self.index = faiss.read_index(str(self.index_file))
                
                # 加载元数据
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                logger.info(f"知识库索引加载成功，包含 {len(self.metadata)} 个文档块")
            else:
                # 创建新索引
                self.index = None
                self.metadata = []
                logger.info("创建新的知识库索引")
        except Exception as e:
            logger.error(f"加载索引失败: {str(e)}")
            self.index = None
            self.metadata = []
    
    def _save_index(self):
        """保存FAISS索引"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            logger.info("知识库索引保存成功")
        except Exception as e:
            logger.error(f"保存索引失败: {str(e)}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的向量嵌入
        
        Args:
            text: 输入文本
        
        Returns:
            向量嵌入
        """
        if self.embedding_model is None:
            # 模拟嵌入（返回随机向量）
            return np.random.rand(self.embedding_dim).astype('float32')
        
        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.astype('float32')
        except Exception as e:
            logger.error(f"生成嵌入失败: {str(e)}")
            return np.random.rand(self.embedding_dim).astype('float32')
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        将文本分块
        
        Args:
            text: 输入文本
            chunk_size: 每块字符数
            overlap: 重叠字符数
        
        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # 尝试在句号、问号、感叹号处分割
            if end < len(text):
                last_punct = max(
                    chunk.rfind('。'),
                    chunk.rfind('！'),
                    chunk.rfind('？'),
                    chunk.rfind('\n')
                )
                if last_punct > chunk_size // 2:
                    chunk = chunk[:last_punct + 1]
                    end = start + last_punct + 1
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
        
        return chunks
    
    def add_document(self, title: str, content: str, doc_type: str = "text", 
                    source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加文档到知识库
        
        Args:
            title: 文档标题
            content: 文档内容
            doc_type: 文档类型
            source: 文档来源
            metadata: 额外元数据
        
        Returns:
            文档ID
        """
        if not HAS_DEPS:
            logger.warning("知识库依赖未安装，无法添加文档")
            return ""
        
        try:
            # 生成文档ID
            doc_id = hashlib.md5(f"{title}_{content[:100]}".encode()).hexdigest()
            
            # 文本分块
            chunks = self._chunk_text(content)
            
            if not chunks:
                logger.warning(f"文档 {title} 内容为空，跳过")
                return doc_id
            
            # 生成向量
            embeddings = []
            new_metadata = []
            
            for i, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk)
                embeddings.append(embedding)
                
                chunk_metadata = {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "title": title,
                    "content": chunk,
                    "doc_type": doc_type,
                    "source": source or "",
                    "added_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
                new_metadata.append(chunk_metadata)
            
            # 转换为numpy数组
            embeddings_array = np.vstack(embeddings).astype('float32')
            
            # 创建或更新FAISS索引
            if self.index is None:
                # 创建新索引
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # 使用内积（余弦相似度）
            
            # 添加到索引
            self.index.add(embeddings_array)
            
            # 添加元数据
            self.metadata.extend(new_metadata)
            
            # 保存索引
            self._save_index()
            
            # 保存原始文档
            doc_file = self.documents_dir / f"{doc_id}.json"
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "doc_id": doc_id,
                    "title": title,
                    "content": content,
                    "doc_type": doc_type,
                    "source": source,
                    "chunks_count": len(chunks),
                    "added_at": datetime.now().isoformat(),
                    "metadata": metadata or {}
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"文档添加成功: {title} (ID: {doc_id}, {len(chunks)} 个块)")
            return doc_id
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            return ""
    
    def search(self, query: str, top_k: int = 5, elderly_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回最相关的K个结果
            elderly_id: 老人ID（可选，用于过滤文档）
        
        Returns:
            搜索结果列表
        """
        if not HAS_DEPS or self.index is None or len(self.metadata) == 0:
            logger.warning("知识库未初始化或为空")
            return []
        
        try:
            # 生成查询向量
            query_embedding = self._get_embedding(query).reshape(1, -1)
            
            # 搜索（获取更多结果以进行过滤）
            search_k = top_k * 3 if elderly_id else top_k
            scores, indices = self.index.search(query_embedding, min(search_k, len(self.metadata)))
            
            # 组装结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    
                    # 如果指定了elderly_id，进行过滤
                    if elderly_id and result.get("metadata", {}).get("elderly_id"):
                        if str(result["metadata"]["elderly_id"]) != str(elderly_id):
                            continue
                    
                    result["similarity_score"] = float(score)
                    results.append(result)
                    
                    # 如果已经获取足够的 filtered 结果，停止
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            是否删除成功
        """
        try:
            # 找到所有相关块
            indices_to_remove = [
                i for i, meta in enumerate(self.metadata)
                if meta.get("doc_id") == doc_id
            ]
            
            if not indices_to_remove:
                logger.warning(f"未找到文档: {doc_id}")
                return False
            
            # 重建索引（移除相关块）
            # 注意：FAISS不支持直接删除，需要重建
            remaining_metadata = [
                meta for i, meta in enumerate(self.metadata)
                if i not in indices_to_remove
            ]
            
            if remaining_metadata:
                # 重新生成向量并重建索引
                embeddings = []
                for meta in remaining_metadata:
                    embedding = self._get_embedding(meta["content"])
                    embeddings.append(embedding)
                
                embeddings_array = np.vstack(embeddings).astype('float32')
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(embeddings_array)
            else:
                self.index = None
            
            self.metadata = remaining_metadata
            self._save_index()
            
            # 删除文档文件
            doc_file = self.documents_dir / f"{doc_id}.json"
            if doc_file.exists():
                doc_file.unlink()
            
            logger.info(f"文档删除成功: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False
    
    def get_document_info(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取文档信息"""
        doc_file = self.documents_dir / f"{doc_id}.json"
        if doc_file.exists():
            with open(doc_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        docs = []
        for doc_file in self.documents_dir.glob("*.json"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    docs.append({
                        "doc_id": doc.get("doc_id"),
                        "title": doc.get("title"),
                        "doc_type": doc.get("doc_type"),
                        "source": doc.get("source"),
                        "chunks_count": doc.get("chunks_count", 0),
                        "added_at": doc.get("added_at")
                    })
            except Exception as e:
                logger.error(f"读取文档失败 {doc_file}: {str(e)}")
        
        return docs


# 创建全局知识库实例
knowledge_base = KnowledgeBase()

