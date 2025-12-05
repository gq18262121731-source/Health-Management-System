# AI问诊功能完整设置清单

## ✅ 已完成配置

1. **后端AI服务**
   - ✅ DeepSeek API Key已配置
   - ✅ AI服务模块已创建 (`services/ai_service.py`)
   - ✅ AI路由接口已创建 (`api/routes/ai.py`)

2. **知识库系统**
   - ✅ 知识库服务已创建 (`services/knowledge_base.py`)
   - ✅ 13个健康文档已导入
   - ✅ RAG检索功能已集成

3. **文档格式支持**
   - ✅ 支持 txt, md, pdf, docx 格式

## 📋 待完成设置

### 1. 后端服务配置

#### 1.1 环境变量检查
确保 `.env` 文件中包含：
```env
# AI服务配置
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-49b06f2468d747368ad9f70fe218e73f

# 数据库配置
DATABASE_URL=sqlite:///./sql_app.db

# 服务器配置
PORT=8000
HOST=0.0.0.0
```

#### 1.2 依赖安装
```bash
cd backend
pip install -r requirements.txt
```

主要依赖包括：
- `httpx` - HTTP客户端
- `faiss-cpu` - 向量数据库
- `sentence-transformers` - 嵌入模型
- `PyPDF2` - PDF处理
- `python-docx` - Word文档处理
- `email-validator` - 邮箱验证

#### 1.3 启动后端服务
```bash
cd backend
python main.py
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- AI服务检查：http://localhost:8000/api/ai/health

### 2. 前端配置

#### 2.1 创建API配置文件
需要创建 `src/config/api.ts` 或 `src/utils/api.ts` 配置后端API地址

#### 2.2 创建API调用函数
需要创建 `src/services/aiConsultation.ts` 调用后端AI接口

#### 2.3 修改前端组件
将 `AIConsultation.tsx` 等组件中的模拟回复替换为真实API调用

#### 2.4 配置CORS
确保后端 `BACKEND_CORS_ORIGINS` 包含前端地址（如 `http://localhost:3000`）

### 3. 可选功能配置

#### 3.1 健康数据集成
- 从数据库获取用户实时健康数据
- 将健康数据传递给AI作为上下文

#### 3.2 对话历史记录
- 保存用户的咨询历史
- 支持查看历史对话记录

#### 3.3 用户认证
- 集成JWT认证（如果需要）
- 关联用户ID和咨询记录

## 🔧 快速检查清单

- [ ] 后端服务能正常启动
- [ ] AI服务健康检查返回正常
- [ ] 知识库统计信息正确
- [ ] 前端能连接到后端API
- [ ] 前端组件调用AI接口成功
- [ ] AI回答使用了知识库内容
- [ ] 对话历史功能正常（如启用）

## 🚀 测试步骤

1. **测试后端AI服务**
   ```bash
   curl -X POST "http://localhost:8000/api/ai/consult" \
     -H "Content-Type: application/json" \
     -d '{
       "user_input": "我血压偏高，应该怎么控制？",
       "use_knowledge_base": true
     }'
   ```

2. **测试知识库检索**
   ```bash
   curl "http://localhost:8000/api/knowledge-base/search?query=高血压&top_k=3"
   ```

3. **测试前端连接**
   - 启动前端服务
   - 打开AI咨询页面
   - 发送测试消息

## ⚠️ 常见问题

1. **AI服务返回模拟回复**
   - 检查 `.env` 中的 `DEEPSEEK_API_KEY` 是否正确
   - 检查网络是否能访问 DeepSeek API

2. **知识库检索不到内容**
   - 确认文档已成功导入（检查 `knowledge_base/documents/` 目录）
   - 检查搜索关键词是否匹配

3. **前端无法连接后端**
   - 检查后端服务是否启动
   - 检查CORS配置
   - 检查API地址是否正确


