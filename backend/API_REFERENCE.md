# API接口参考文档

> **最后更新**: 2024年12月
> 
> 本文档提供完整的API接口参考，确保前后端开发一致。

## 📋 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API版本**: v1
- **认证方式**: JWT Bearer Token

## 🔐 认证

所有需要认证的接口都在请求头中包含：
```
Authorization: Bearer <access_token>
```

### 获取Token

通过登录接口获取：
- **路径**: `POST /api/v1/auth/login`

---

## 📚 API端点索引

### 认证相关 (`/api/v1/auth`)
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/logout` - 退出登录

### 老人相关 (`/api/v1/elderly`)
- `GET /api/v1/elderly` - 获取老人列表
- `GET /api/v1/elderly/{elderly_id}` - 获取老人详情
- `POST /api/v1/elderly` - 创建老人档案
- `PUT /api/v1/elderly/{elderly_id}` - 更新老人档案
- `DELETE /api/v1/elderly/{elderly_id}` - 删除老人档案
- `GET /api/v1/elderly/{elderly_id}/health-summary` - 获取健康摘要
- `GET /api/v1/elderly/{elderly_id}/health-records` - 获取健康记录
- `POST /api/v1/elderly/{elderly_id}/health-records` - 添加健康记录

### 子女相关 (`/api/v1/children`)
- `GET /api/v1/children` - 获取子女列表
- `GET /api/v1/children/{children_id}` - 获取子女详情

### 社区相关 (`/api/v1/communities`)
- `GET /api/v1/communities` - 获取社区列表
- `GET /api/v1/communities/{community_id}` - 获取社区详情

### AI健康助手 (`/api/v1/ai`)
- `POST /api/v1/ai/consult` - AI健康咨询 **[需要认证]**
- `GET /api/v1/ai/health` - AI服务健康检查
- `GET /api/v1/ai/history` - 获取咨询历史 **[需要认证]**

### 知识库管理 (`/api/v1/knowledge-base`)
- `POST /api/v1/knowledge-base/upload` - 上传文档
- `POST /api/v1/knowledge-base/add-text` - 添加文本
- `GET /api/v1/knowledge-base/search` - 搜索知识库
- `GET /api/v1/knowledge-base/documents` - 列出文档
- `GET /api/v1/knowledge-base/documents/{doc_id}` - 获取文档详情
- `DELETE /api/v1/knowledge-base/documents/{doc_id}` - 删除文档
- `GET /api/v1/knowledge-base/stats` - 获取统计信息

---

## 🔍 详细接口说明

### 1. 用户注册

**请求**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone_number": "13800138000",
  "password": "password123",
  "role": "elderly"
}
```

**响应**
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": "uuid",
    "phone_number": "13800138000",
    "role": "elderly"
  }
}
```

**注意：**
- `phone_number`: 11位手机号，必须以1开头
- `role`: 必须是 `elderly`, `children`, 或 `community`

---

### 2. 用户登录

**请求**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=13800138000&password=password123
```

或使用JSON（如果支持）：
```json
{
  "phone_number": "13800138000",
  "password": "password123"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_info": {
      "id": "uuid",
      "phone_number": "13800138000",
      "role": "elderly"
    }
  },
  "message": "登录成功"
}
```

**注意：**
- OAuth2格式：使用 `username` 字段传递手机号
- Token有效期：默认3600秒（1小时）

---

### 3. AI健康咨询

**请求**
```http
POST /api/v1/ai/consult
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_input": "我血压偏高，应该怎么控制？",
  "elderly_id": "uuid (可选)",
  "use_knowledge_base": true,
  "save_history": true
}
```

**响应**
```json
{
  "status": "success",
  "data": {
    "query": "我血压偏高，应该怎么控制？",
    "response": "根据您的健康数据，我建议您...",
    "user_role": "elderly",
    "health_data_used": true,
    "knowledge_base_used": true
  },
  "message": "咨询成功"
}
```

**功能说明：**
- 自动获取用户健康数据（如果用户是老人或指定了elderly_id）
- 自动加载对话历史（用于上下文）
- 支持知识库RAG检索
- 自动保存对话记录

**错误响应：**
```json
{
  "detail": "用户输入不能为空"
}
```
状态码：400

```json
{
  "detail": "无法验证凭据"
}
```
状态码：401

```json
{
  "detail": "AI服务暂时不可用: ..."
}
```
状态码：503

---

### 4. 获取咨询历史

**请求**
```http
GET /api/v1/ai/history?limit=20&elderly_id=uuid
Authorization: Bearer <token>
```

**响应**
```json
{
  "status": "success",
  "data": {
    "queries": [
      {
        "id": "uuid",
        "query_text": "用户问题",
        "response_text": "AI回复",
        "created_at": "2024-12-01T10:00:00Z",
        "elderly_id": "uuid"
      }
    ],
    "count": 10
  }
}
```

---

### 5. 知识库搜索

**请求**
```http
GET /api/v1/knowledge-base/search?query=高血压&top_k=5
```

**响应**
```json
{
  "status": "success",
  "data": {
    "query": "高血压",
    "results": [
      {
        "title": "高血压管理指南",
        "content": "文档内容...",
        "similarity_score": 0.85,
        "metadata": {
          "source": "health/高血压管理指南.md",
          "elderly_id": "uuid (可选)"
        }
      }
    ],
    "count": 3
  }
}
```

---

### 6. 知识库统计

**请求**
```http
GET /api/v1/knowledge-base/stats
```

**响应**
```json
{
  "status": "success",
  "data": {
    "total_documents": 13,
    "total_chunks": 37,
    "index_status": "ready"
  }
}
```

---

### 7. 上传文档到知识库

**请求**
```http
POST /api/v1/knowledge-base/upload
Content-Type: multipart/form-data

file: <文件>
title: 文档标题
source: 来源
doc_type: health (可选)
```

**响应**
```json
{
  "status": "success",
  "data": {
    "doc_id": "uuid",
    "title": "文档标题",
    "message": "文档上传并索引成功"
  }
}
```

**支持格式：**
- `.txt` - 纯文本
- `.md`, `.markdown` - Markdown
- `.pdf` - PDF文档
- `.docx`, `.doc` - Word文档

---

## 🔄 数据格式规范

### UUID格式
所有ID字段使用UUID v4格式：
```
550e8400-e29b-41d4-a716-446655440000
```

### 时间格式
所有时间字段使用ISO 8601格式（UTC时区）：
```
2024-12-01T10:30:00Z
2024-12-01T10:30:00+08:00
```

### 健康数据格式

**血压：**
- 存储：`systolic_pressure` (整数), `diastolic_pressure` (整数)
- API响应：`"118/75"` (字符串格式)

**心率：**
- 单位：次/分钟 (bpm)
- 类型：整数

**血糖：**
- 单位：mmol/L
- 类型：浮点数

**体温：**
- 单位：℃
- 类型：浮点数

**血氧：**
- 单位：%
- 类型：浮点数

---

## ⚠️ 常见错误码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求体格式和必填字段 |
| 401 | 未认证 | 检查Token是否有效或已过期 |
| 403 | 权限不足 | 确认用户角色是否有权限访问 |
| 404 | 资源不存在 | 检查资源ID是否正确 |
| 500 | 服务器错误 | 查看服务器日志 |
| 503 | 服务不可用 | AI服务可能暂时不可用，稍后重试 |

---

## 🔗 前端对接说明

### 1. 认证流程

```typescript
// 登录并保存token
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=13800138000&password=xxx'
});
const data = await response.json();
localStorage.setItem('access_token', data.data.access_token);
```

### 2. API调用示例

```typescript
// 带认证的请求
const token = localStorage.getItem('access_token');
const response = await fetch('/api/v1/ai/consult', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    user_input: '问题内容',
    use_knowledge_base: true
  })
});
```

### 3. 错误处理

```typescript
if (!response.ok) {
  if (response.status === 401) {
    // Token过期，跳转登录
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  } else {
    const error = await response.json();
    console.error('API错误:', error.detail);
  }
}
```

---

## 📝 更新日志

### 2024-12-01
- ✅ 修复API路径不一致（`/api/user/*` → `/api/auth/*`）
- ✅ 统一AI咨询表名（`ai_consultations` → `ai_queries`）
- ✅ 明确健康数据与睡眠数据分离
- ✅ 补充完整的枚举类型定义

---

## 🔍 验证清单

使用以下清单验证API一致性：

- [ ] API路径与文档一致
- [ ] 请求/响应格式与Schema一致
- [ ] 认证机制正常工作
- [ ] 错误处理正确
- [ ] 数据类型匹配（UUID, 时间格式等）
- [ ] 枚举值与代码一致


