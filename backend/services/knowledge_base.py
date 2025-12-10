"""知识库服务 - RAG（检索增强生成）"""
import logging
import os
import json
import ssl
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

# 解决 SSL 证书验证问题
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

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
        self.documents_dir = self.kb_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        
        # FAISS 索引使用临时目录（避免中文路径问题）
        import tempfile
        self.vectors_dir = Path(tempfile.gettempdir()) / "health_kb_index"
        self.vectors_dir.mkdir(exist_ok=True)
        
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
            import os
            import torch
            from transformers import AutoTokenizer, AutoModel
            
            # 本地模型路径（从 ModelScope 下载）
            local_model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "models", "damo", "nlp_corom_sentence-embedding_chinese-base"
            )
            
            if os.path.exists(local_model_path):
                logger.info(f"加载本地嵌入模型: {local_model_path}")
                self._tokenizer = AutoTokenizer.from_pretrained(local_model_path)
                self._transformer_model = AutoModel.from_pretrained(local_model_path)
                self._transformer_model.eval()
                self._use_transformers = True
                self.embedding_dim = 768
                self.embedding_model = True  # 标记为已加载
                logger.info(f"本地嵌入模型加载成功，维度: {self.embedding_dim}")
                return
            
            # 回退：尝试 SentenceTransformer
            logger.info("本地模型不存在，尝试 SentenceTransformer")
            self._use_transformers = False
            try:
                import socket
                socket.setdefaulttimeout(10)
                self.embedding_model = SentenceTransformer("moka-ai/m3e-base")
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                logger.info(f"SentenceTransformer 加载成功，维度: {self.embedding_dim}")
            except Exception as e:
                logger.warning(f"SentenceTransformer 加载失败: {str(e)[:100]}")
                self.embedding_model = None
                
        except Exception as e:
            logger.warning(f"嵌入模型加载失败: {str(e)[:100]}")
            self.embedding_model = None
            self._use_transformers = False
    
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
            # 使用 transformers 本地模型
            if getattr(self, '_use_transformers', False):
                import torch
                inputs = self._tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = self._transformer_model(**inputs)
                # 使用 [CLS] token 的输出作为句子嵌入
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
                # 归一化
                embedding = embedding / np.linalg.norm(embedding)
                return embedding.astype('float32')
            
            # 使用 SentenceTransformer
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


    def import_from_directory(self, source_dir: str = None) -> int:
        """
        从目录导入所有文档（支持 .txt 和 .docx）
        
        Args:
            source_dir: 源文档目录，默认为知识库根目录
            
        Returns:
            成功导入的文档数量
        """
        if source_dir is None:
            source_dir = self.kb_dir
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f"目录不存在: {source_dir}")
            return 0
        
        imported = 0
        
        # 获取已导入的文档标题
        existing_titles = {doc.get("title") for doc in self.list_documents()}
        
        # 导入 .txt 文件
        for txt_file in source_path.glob("*.txt"):
            title = txt_file.stem
            if title in existing_titles:
                logger.debug(f"文档已存在，跳过: {title}")
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
                logger.debug(f"文档已存在，跳过: {title}")
                continue
            
            try:
                # 尝试读取 docx
                try:
                    from docx import Document
                    doc = Document(str(docx_file))
                    content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                except ImportError:
                    logger.warning(f"python-docx 未安装，跳过 {docx_file}")
                    continue
                
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
        """根据标题猜测文档分类"""
        title_lower = title.lower()
        if any(k in title_lower for k in ["血压", "高血压"]):
            return "高血压"
        elif any(k in title_lower for k in ["血糖", "糖尿病"]):
            return "糖尿病"
        elif any(k in title_lower for k in ["血脂", "胆固醇", "心肌梗死", "脑血栓"]):
            return "心血管"
        elif any(k in title_lower for k in ["运动", "活动"]):
            return "运动指导"
        elif any(k in title_lower for k in ["膳食", "饮食", "营养"]):
            return "饮食营养"
        elif any(k in title_lower for k in ["骨质", "骨骼"]):
            return "骨骼健康"
        elif any(k in title_lower for k in ["体重", "肥胖"]):
            return "体重管理"
        else:
            return "综合健康"


# 创建全局知识库实例（使用项目根目录的 knowledge-base 文件夹）
import os
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_kb_path = os.path.join(_project_root, "knowledge-base")
knowledge_base = KnowledgeBase(kb_dir=_kb_path)

# 自动导入知识库目录下的文档
if HAS_DEPS and knowledge_base.embedding_model:
    _imported = knowledge_base.import_from_directory()
    if _imported > 0:
        logger.info(f"知识库初始化完成，共导入 {_imported} 个新文档")

