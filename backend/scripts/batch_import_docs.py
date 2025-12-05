"""
批量导入知识库文档脚本

用法：
    python scripts/batch_import_docs.py [文档目录路径]

示例：
    python scripts/batch_import_docs.py knowledge_base/docs
"""
import sys
import os
from pathlib import Path

# 设置输出编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.knowledge_base import knowledge_base
from services.document_processor import DocumentProcessor


def batch_import_docs(docs_dir: str = None):
    """
    批量导入文档到知识库
    
    Args:
        docs_dir: 文档目录路径，默认使用 knowledge_base/docs
    """
    if docs_dir is None:
        docs_dir = project_root / "knowledge_base" / "docs"
    else:
        docs_dir = Path(docs_dir)
    
    if not docs_dir.exists():
        print(f"❌ 目录不存在: {docs_dir}")
        return
    
    # 支持的文件扩展名
    allowed_extensions = {'.txt', '.md', '.markdown', '.pdf', '.docx', '.doc'}
    
    # 查找所有文档文件
    doc_files = []
    for ext in allowed_extensions:
        doc_files.extend(docs_dir.rglob(f"*{ext}"))
    
    if not doc_files:
        print(f"⚠️ 在 {docs_dir} 中未找到任何文档文件")
        return
    
    print(f"[知识库] 找到 {len(doc_files)} 个文档文件")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    
    for doc_file in doc_files:
        try:
            print(f"[处理] {doc_file.name}...", end=" ")
            
            # 处理文档
            doc_info = DocumentProcessor.process_file(str(doc_file))
            
            # 确定文档类型（根据目录名或文件扩展名）
            relative_path = doc_file.relative_to(docs_dir)
            doc_type = relative_path.parts[0] if len(relative_path.parts) > 1 else doc_file.suffix[1:]
            
            # 添加到知识库
            doc_id = knowledge_base.add_document(
                title=doc_info["title"],
                content=doc_info["content"],
                doc_type=doc_type,
                source=str(relative_path)
            )
            
            if doc_id:
                print(f"[成功] ID: {doc_id[:8]}...")
                success_count += 1
            else:
                print("[失败]")
                error_count += 1
                
        except Exception as e:
            print(f"[错误] {str(e)}")
            error_count += 1
    
    print("-" * 50)
    print(f"[完成] 成功导入: {success_count} 个文档")
    if error_count > 0:
        print(f"[失败] {error_count} 个文档")
    
    # 显示知识库统计
    docs = knowledge_base.list_documents()
    total_chunks = sum(doc.get("chunks_count", 0) for doc in docs)
    print(f"\n[统计] 知识库状态:")
    print(f"   - 总文档数: {len(docs)}")
    print(f"   - 总文档块: {total_chunks}")


if __name__ == "__main__":
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else None
    batch_import_docs(docs_dir)

