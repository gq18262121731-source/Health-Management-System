# 项目启动指南

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

**验证后端启动成功：**
- 访问：http://localhost:8000/health
- 访问API文档：http://localhost:8000/docs

### 2. 启动前端服务

在新的终端窗口：

```bash
cd health-monitoring-system
npm run dev
```

前端服务将在 `http://localhost:3000` 启动（或自动选择可用端口）

## ✅ 启动前检查

运行配置检查：

```bash
cd backend
python scripts/check_setup.py
```

应该看到所有检查项都通过。

## 🔍 验证服务

### 后端API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 测试后端API

```bash
# 健康检查
curl http://localhost:8000/health

# AI服务状态
curl http://localhost:8000/api/ai/health

# 知识库统计
curl http://localhost:8000/api/knowledge-base/stats
```

### 运行完整测试

```bash
cd backend
python test_api.py
```

## 📝 端口说明

- **后端**: 8000
- **前端**: 3000（默认，如果被占用会自动选择其他端口）

## ⚠️ 常见问题

### 1. 端口被占用
如果8000端口被占用，修改 `backend/.env` 中的 `PORT` 配置

### 2. 前端依赖未安装
```bash
cd health-monitoring-system
npm install
```

### 3. Python依赖未安装
```bash
cd backend
pip install -r requirements.txt
```

## 🎯 下一步

1. 访问前端：http://localhost:3000
2. 选择角色登录（老人/子女/社区）
3. 测试AI健康助手功能
4. 测试知识库功能
5. 测试朗读功能（老人端）


