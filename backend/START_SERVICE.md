# 启动服务指南

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

### 2. 启动前端服务

在另一个终端窗口：

```bash
cd health-monitoring-system
npm run dev
```

前端将在 `http://localhost:3000` 启动

## ✅ 配置检查

启动前，运行配置检查：

```bash
cd backend
python scripts/check_setup.py
```

应该看到：
- ✅ 环境变量
- ✅ Python依赖
- ✅ 知识库
- ✅ AI服务

## 🔍 验证服务

### 后端API文档
访问：http://localhost:8000/docs

### 测试AI服务
```bash
# 健康检查
curl http://localhost:8000/health

# AI服务状态
curl http://localhost:8000/api/ai/health

# 测试AI咨询
curl -X POST "http://localhost:8000/api/ai/consult" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我血压偏高，应该怎么控制？",
    "use_knowledge_base": true
  }'
```

## 📝 前端环境变量（可选）

如果需要修改后端API地址，创建 `health-monitoring-system/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```


