"""
知识库服务 - LangChain RAG 实现
================================

使用 LangChain + ChromaDB 实现更强大的 RAG 功能。

特点：
1. 持久化向量存储 (ChromaDB)
2. 更好的文档分块策略
3. 支持多种文档格式
4. 更灵活的检索策略
"""
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# 检查依赖
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    logger.warning("LangChain 依赖未安装，请运行: pip install langchain langchain-community chromadb langchain-text-splitters")


class SiliconFlowEmbeddings:
    """硅基流动嵌入模型封装（兼容LangChain接口）"""
    
    def __init__(self):
        from services.siliconflow_service import siliconflow_service
        self.service = siliconflow_service
        self.model = "BAAI/bge-m3"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        embeddings = []
        for text in texts:
            try:
                emb = self.service.get_embedding(text, model=self.model)
                embeddings.append(emb)
            except Exception as e:
                logger.error(f"嵌入失败: {e}")
                embeddings.append([0.0] * 1024)  # BGE-M3 维度
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询"""
        try:
            return self.service.get_embedding(text, model=self.model)
        except Exception as e:
            logger.error(f"查询嵌入失败: {e}")
            return [0.0] * 1024


class LangChainKnowledgeBase:
    """
    基于 LangChain 的知识库
    
    功能：
    - 文档导入和分块
    - 向量化存储 (ChromaDB)
    - 语义检索
    - 持久化存储
    """
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        初始化知识库
        
        Args:
            persist_dir: ChromaDB 持久化目录
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = None
        
        if HAS_LANGCHAIN:
            self._init_components()
        else:
            logger.warning("LangChain 未安装，知识库将使用模拟模式")
    
    def _init_components(self):
        """初始化 LangChain 组件"""
        try:
            # 1. 初始化嵌入模型（只使用硅基流动API，避免HuggingFace下载问题）
            self.embeddings = None
            
            try:
                from services.siliconflow_service import siliconflow_service
                if siliconflow_service and siliconflow_service.is_available:
                    self.embeddings = SiliconFlowEmbeddings()
                    logger.info("✅ LangChain 使用硅基流动 BGE-M3 嵌入模型")
                else:
                    logger.warning("硅基流动服务不可用，知识库功能将受限")
            except Exception as e:
                logger.warning(f"硅基流动初始化失败: {e}")
            
            # 2. 初始化文本分割器
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
            )
            
            # 3. 初始化或加载向量存储
            self._load_or_create_vectorstore()
            
            logger.info("LangChain 知识库初始化成功")
            
        except Exception as e:
            logger.error(f"LangChain 组件初始化失败: {e}")
            self.embeddings = None
    
    def _load_or_create_vectorstore(self):
        """加载或创建向量存储"""
        try:
            # 尝试加载现有的向量存储
            if (self.persist_dir / "chroma.sqlite3").exists():
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_dir),
                    embedding_function=self.embeddings
                )
                count = self.vectorstore._collection.count()
                logger.info(f"加载现有向量存储，包含 {count} 个文档块")
            else:
                # 创建新的向量存储
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_dir),
                    embedding_function=self.embeddings
                )
                logger.info("创建新的向量存储")
        except Exception as e:
            logger.error(f"向量存储初始化失败: {e}")
            self.vectorstore = None
    
    def add_document(
        self, 
        title: str, 
        content: str, 
        doc_type: str = "text",
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
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
        if not HAS_LANGCHAIN or self.vectorstore is None:
            logger.warning("知识库未初始化")
            return ""
        
        try:
            import hashlib
            from datetime import datetime
            
            # 生成文档ID
            doc_id = hashlib.md5(f"{title}_{content[:100]}".encode()).hexdigest()
            
            # 分割文档
            chunks = self.text_splitter.split_text(content)
            
            if not chunks:
                logger.warning(f"文档 {title} 内容为空")
                return doc_id
            
            # 创建 LangChain Document 对象
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "title": title,
                    "doc_type": doc_type,
                    "source": source or "",
                    "added_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
                documents.append(Document(page_content=chunk, metadata=doc_metadata))
            
            # 添加到向量存储
            self.vectorstore.add_documents(documents)
            
            logger.info(f"文档添加成功: {title} (ID: {doc_id}, {len(chunks)} 个块)")
            return doc_id
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return ""
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_dict: 过滤条件
            score_threshold: 相似度阈值
            
        Returns:
            搜索结果列表
        """
        if not HAS_LANGCHAIN or self.vectorstore is None:
            logger.warning("知识库未初始化")
            return []
        
        try:
            # 使用相似度搜索
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_dict
            )
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                # ChromaDB 返回的是距离，需要转换为相似度
                similarity = 1 - score if score <= 1 else 1 / (1 + score)
                
                if similarity >= score_threshold:
                    formatted_results.append({
                        "content": doc.page_content,
                        "title": doc.metadata.get("title", ""),
                        "doc_id": doc.metadata.get("doc_id", ""),
                        "chunk_index": doc.metadata.get("chunk_index", 0),
                        "doc_type": doc.metadata.get("doc_type", ""),
                        "source": doc.metadata.get("source", ""),
                        "similarity_score": similarity,
                        "metadata": doc.metadata
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def search_with_context(
        self, 
        query: str, 
        top_k: int = 3
    ) -> str:
        """
        搜索并返回格式化的上下文（用于RAG）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            格式化的上下文字符串
        """
        results = self.search(query, top_k=top_k)
        
        if not results:
            return ""
        
        context_parts = ["【相关知识库内容】"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. 【{result['title']}】")
            context_parts.append(result['content'])
        
        return "\n".join(context_parts)
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        if not HAS_LANGCHAIN or self.vectorstore is None:
            return False
        
        try:
            # ChromaDB 支持按条件删除
            self.vectorstore._collection.delete(
                where={"doc_id": doc_id}
            )
            logger.info(f"文档删除成功: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        if not HAS_LANGCHAIN or self.vectorstore is None:
            return []
        
        try:
            # 获取所有文档的元数据
            collection = self.vectorstore._collection
            results = collection.get()
            
            # 按 doc_id 去重
            docs_map = {}
            for metadata in results.get("metadatas", []):
                doc_id = metadata.get("doc_id")
                if doc_id and doc_id not in docs_map:
                    docs_map[doc_id] = {
                        "doc_id": doc_id,
                        "title": metadata.get("title", ""),
                        "doc_type": metadata.get("doc_type", ""),
                        "source": metadata.get("source", ""),
                        "added_at": metadata.get("added_at", "")
                    }
            
            return list(docs_map.values())
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            return []
    
    def import_from_directory(self, source_dir: str) -> int:
        """
        从目录导入文档
        
        Args:
            source_dir: 源目录
            
        Returns:
            导入的文档数量
        """
        if not HAS_LANGCHAIN:
            return 0
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f"目录不存在: {source_dir}")
            return 0
        
        imported = 0
        existing_titles = {doc.get("title") for doc in self.list_documents()}
        
        # 导入 .txt 文件
        for txt_file in source_path.glob("*.txt"):
            title = txt_file.stem
            if title in existing_titles:
                continue
            
            try:
                content = txt_file.read_text(encoding='utf-8')
                if content.strip():
                    self.add_document(
                        title=title,
                        content=content,
                        doc_type="text",
                        source=str(txt_file),
                        metadata={"category": self._guess_category(title)}
                    )
                    imported += 1
            except Exception as e:
                logger.error(f"导入 {txt_file} 失败: {e}")
        
        # 导入 .docx 文件
        for docx_file in source_path.glob("*.docx"):
            title = docx_file.stem
            if title in existing_titles:
                continue
            
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(str(docx_file))
                content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                
                if content.strip():
                    self.add_document(
                        title=title,
                        content=content,
                        doc_type="docx",
                        source=str(docx_file),
                        metadata={"category": self._guess_category(title)}
                    )
                    imported += 1
            except Exception as e:
                logger.error(f"导入 {docx_file} 失败: {e}")
        
        logger.info(f"从 {source_dir} 导入了 {imported} 个文档")
        return imported
    
    def _guess_category(self, title: str) -> str:
        """根据标题猜测分类"""
        title_lower = title.lower()
        if any(k in title_lower for k in ["血压", "高血压"]):
            return "高血压"
        elif any(k in title_lower for k in ["血糖", "糖尿病"]):
            return "糖尿病"
        elif any(k in title_lower for k in ["血脂", "胆固醇"]):
            return "心血管"
        elif any(k in title_lower for k in ["运动", "活动"]):
            return "运动指导"
        elif any(k in title_lower for k in ["膳食", "饮食"]):
            return "饮食营养"
        else:
            return "综合健康"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if not HAS_LANGCHAIN or self.vectorstore is None:
            return {"status": "未初始化", "documents": 0, "chunks": 0}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            docs = self.list_documents()
            
            return {
                "status": "正常",
                "documents": len(docs),
                "chunks": count,
                "persist_dir": str(self.persist_dir),
                "embedding_model": "BGE-M3" if isinstance(self.embeddings, SiliconFlowEmbeddings) else "m3e-base"
            }
        except Exception as e:
            return {"status": f"错误: {e}", "documents": 0, "chunks": 0}


# 创建全局实例
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_chroma_path = os.path.join(_project_root, "chroma_db")
_kb_path = os.path.join(_project_root, "knowledge-base")

langchain_knowledge_base = LangChainKnowledgeBase(persist_dir=_chroma_path)

# 兼容旧接口
knowledge_base = langchain_knowledge_base

# 自动导入知识库文档
if HAS_LANGCHAIN and langchain_knowledge_base.vectorstore:
    _imported = langchain_knowledge_base.import_from_directory(_kb_path)
    if _imported > 0:
        logger.info(f"LangChain 知识库初始化完成，导入 {_imported} 个新文档")
