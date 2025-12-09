# 知识库使用指南

## 📚 知识库功能概述

AI健康助手已集成RAG（检索增强生成）知识库系统，可以为AI提供专业知识支持，提升回答的准确性和专业性。

## 🎯 核心功能

1. **文档上传** - 支持多种格式（txt, md, pdf, docx）
2. **智能索引** - 自动分块、向量化、存储
3. **语义检索** - 基于向量相似度的智能搜索
4. **RAG集成** - 自动将相关知识注入AI提示词

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

主要依赖：
- `faiss-cpu` - 向量数据库
- `sentence-transformers` - 嵌入模型
- `PyPDF2` - PDF处理
- `python-docx` - Word文档处理

### 2. 首次运行

首次运行时，系统会自动下载中文嵌入模型 `m3e-base`（约400MB），需要一些时间。

### 3. 上传文档

#### 方式1：API上传文件

```bash
curl -X POST "http://localhost:8000/api/knowledge-base/upload" \
  -F "file=@健康知识.txt" \
  -F "title=健康知识大全" \
  -F "source=权威医学文献"
```

#### 方式2：API直接添加文本

```bash
curl -X POST "http://localhost:8000/api/knowledge-base/add-text" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "高血压管理指南",
    "content": "高血压患者应该...",
    "source": "医疗指南"
  }'
```

### 4. 搜索知识库

```bash
curl "http://localhost:8000/api/knowledge-base/search?query=高血压注意事项&top_k=5"
```

### 5. AI自动使用知识库

当调用AI咨询接口时，系统会自动从知识库检索相关内容：

```bash
curl -X POST "http://localhost:8000/api/ai/consult" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我最近血压偏高，应该注意什么？",
    "use_knowledge_base": true
  }'
```

## 📖 API接口说明

### 文档管理

- `POST /api/knowledge-base/upload` - 上传文件
- `POST /api/knowledge-base/add-text` - 添加文本
- `GET /api/knowledge-base/documents` - 列出所有文档
- `GET /api/knowledge-base/documents/{doc_id}` - 获取文档详情
- `DELETE /api/knowledge-base/documents/{doc_id}` - 删除文档

### 搜索功能

- `GET /api/knowledge-base/search?query=关键词&top_k=5` - 搜索知识库

### 统计信息

- `GET /api/knowledge-base/stats` - 获取统计信息

## 💡 使用建议

### 1. 文档准备

- **格式**：建议使用Markdown或纯文本格式，结构清晰
- **长度**：单个文档建议不超过10万字符
- **内容**：专注于健康医疗知识，避免无关内容

### 2. 文档组织

- 按主题分类上传（如：心血管、糖尿病、营养等）
- 使用清晰的标题和章节结构
- 添加来源信息，便于追溯

### 3. 知识库维护

- 定期更新过时信息
- 删除错误或重复内容
- 监控知识库统计信息

## 🔧 技术架构

### 向量数据库
- 使用 **FAISS**（Facebook AI Similarity Search）
- 索引类型：IndexFlatIP（内积相似度，等同于余弦相似度）

### 嵌入模型
- 模型：**m3e-base**（中文优化）
- 维度：768
- 特点：对中文理解优秀，适合医疗健康领域

### 文档处理
- 自动分块（每块500字符，重叠50字符）
- 智能段落分割（优先在句号、问号处分割）
- 支持多种格式解析

### RAG流程
1. 用户提问 → 2. 向量化查询 → 3. 检索相关知识 → 4. 注入提示词 → 5. AI生成回答

## 📊 性能优化

1. **批量上传**：可以一次性上传多个文档
2. **索引优化**：大文档会自动分块，提升检索效率
3. **缓存机制**：嵌入模型加载后常驻内存

## ⚠️ 注意事项

1. **首次下载**：m3e-base模型首次运行需要下载（约400MB）
2. **内存占用**：知识库索引会占用一定内存（取决于文档数量）
3. **存储位置**：知识库文件存储在 `backend/knowledge_base/` 目录
4. **备份建议**：定期备份 `knowledge_base/` 目录

## 🎓 示例场景

### 场景1：上传医疗指南

```bash
# 上传PDF格式的医疗指南
curl -X POST "http://localhost:8000/api/knowledge-base/upload" \
  -F "file=@中国高血压防治指南2023.pdf" \
  -F "title=中国高血压防治指南2023" \
  -F "source=国家卫健委"
```

### 场景2：添加常见问题

```bash
curl -X POST "http://localhost:8000/api/knowledge-base/add-text" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "老年人常见健康问题FAQ",
    "content": "Q: 老年人每天应该走多少步？\nA: 建议每天6000-8000步...",
    "doc_type": "faq"
  }'
```

### 场景3：测试知识库检索

```bash
# 搜索"高血压"
curl "http://localhost:8000/api/knowledge-base/search?query=高血压&top_k=3"
```

## 🐛 常见问题

**Q: 模型下载失败怎么办？**
A: 可以手动下载模型或使用代理，或使用其他嵌入模型。

**Q: 知识库检索不到相关内容？**
A: 检查文档是否成功上传，尝试使用不同的关键词搜索。

**Q: 如何查看知识库中有哪些文档？**
A: 调用 `GET /api/knowledge-base/documents` 接口。

**Q: 知识库会影响AI回答速度吗？**
A: 会有轻微影响（检索+生成），通常在1-2秒内完成。

## 📝 下一步

- [ ] 实现文档分类和标签系统
- [ ] 支持文档版本管理
- [ ] 添加知识库使用统计
- [ ] 支持多语言文档
- [ ] 实现增量更新机制


