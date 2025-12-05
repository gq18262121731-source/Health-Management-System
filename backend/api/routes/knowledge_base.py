"""知识库管理路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
import logging
import os
import tempfile

from services.knowledge_base import knowledge_base
from services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None)
):
    """
    上传文档到知识库
    
    支持格式: txt, md, pdf, docx
    """
    try:
        # 保存临时文件
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.txt', '.md', '.markdown', '.pdf', '.docx', '.doc']
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持格式: {', '.join(allowed_extensions)}"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 处理文档
            doc_info = DocumentProcessor.process_file(tmp_file_path, file_ext)
            
            # 添加到知识库
            doc_id = knowledge_base.add_document(
                title=title or doc_info["title"],
                content=doc_info["content"],
                doc_type=doc_type or file_ext[1:],  # 移除点号
                source=source or file.filename
            )
            
            if not doc_id:
                raise HTTPException(status_code=500, detail="文档添加失败")
            
            return {
                "status": "success",
                "data": {
                    "doc_id": doc_id,
                    "title": title or doc_info["title"],
                    "message": "文档上传并索引成功"
                }
            }
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/add-text")
async def add_text_document(
    title: str,
    content: str,
    source: Optional[str] = None,
    doc_type: str = "text"
):
    """
    直接添加文本内容到知识库
    """
    try:
        doc_id = knowledge_base.add_document(
            title=title,
            content=content,
            doc_type=doc_type,
            source=source
        )
        
        if not doc_id:
            raise HTTPException(status_code=500, detail="文档添加失败")
        
        return {
            "status": "success",
            "data": {
                "doc_id": doc_id,
                "title": title,
                "message": "文本内容添加成功"
            }
        }
        
    except Exception as e:
        logger.error(f"添加文本失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.get("/search")
async def search_knowledge_base(query: str, top_k: int = 5):
    """
    搜索知识库
    """
    try:
        results = knowledge_base.search(query, top_k=top_k)
        
        return {
            "status": "success",
            "data": {
                "query": query,
                "results": results,
                "count": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/documents")
async def list_documents():
    """
    列出所有文档
    """
    try:
        documents = knowledge_base.list_documents()
        
        return {
            "status": "success",
            "data": {
                "documents": documents,
                "count": len(documents)
            }
        }
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    获取文档详情
    """
    try:
        doc_info = knowledge_base.get_document_info(doc_id)
        
        if not doc_info:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        return {
            "status": "success",
            "data": doc_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    删除文档
    """
    try:
        success = knowledge_base.delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在或删除失败")
        
        return {
            "status": "success",
            "message": "文档删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/stats")
async def get_knowledge_base_stats():
    """
    获取知识库统计信息
    """
    try:
        documents = knowledge_base.list_documents()
        total_chunks = sum(doc.get("chunks_count", 0) for doc in documents)
        
        return {
            "status": "success",
            "data": {
                "total_documents": len(documents),
                "total_chunks": total_chunks,
                "index_status": "ready" if knowledge_base.index is not None else "empty"
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


