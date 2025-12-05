# 🏥 养生之道 - 智慧健康管理系统

> 基于人工智能与物联网技术的社区老年健康监测与服务平台

## 📋 项目概述

**养生之道**是一款面向社区老年群体的智慧健康管理系统，通过**物联网数据采集**、**AI智能分析**、**语音交互**等技术，实现健康数据的实时监测、智能预警和个性化健康建议。

### 核心价值

| 用户群体 | 核心价值 |
|---------|---------|
| 👴 老年人 | 适老化交互、语音对话、健康预警、AI健康咨询 |
| 👨‍👩‍👧 子女 | 远程监护、实时告警、健康报告、安心陪伴 |
| 🏘️ 社区 | 群体健康统计、大屏监控、风险预警、精准服务 |

## 🔗 GitHub 仓库

**仓库地址**: https://github.com/gq18262121731-source/Health-Management-System.git

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React + TypeScript + Vite + TailwindCSS + shadcn/ui |
| **后端** | FastAPI + SQLAlchemy + PostgreSQL/SQLite |
| **AI** | DeepSeek API + RAG知识库 |
| **语音** | Edge-TTS（语音合成）+ Web Speech API（语音识别）|
| **可视化** | Recharts + ECharts |

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/gq18262121731-source/Health-Management-System.git
cd Health-Management-System
```

### 2. 后端启动
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问地址
| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

## ✨ 主要功能

### 健康监测
- 📊 **实时数据采集** - 血压、血糖、心率、体温、血氧
- 😴 **睡眠监测** - 睡眠时长、质量分析
- 🚶 **运动数据** - 步数统计、运动建议

### AI 智能助手
- 🤖 **智能问诊** - 基于症状的健康咨询
- 📝 **健康报告** - AI生成个性化健康分析报告
- 💡 **健康建议** - 基于RAG知识库的专业建议

### 适老化交互
- 🔊 **语音播报** - 健康数据语音朗读
- 🎤 **语音输入** - 语音对话交互
- 📱 **大字体UI** - 适老化界面设计

### 多端支持
- 👴 **老人端** - 健康监测、AI问诊、语音交互
- 👨‍👩‍👧 **子女端** - 远程监护、健康报告查看
- 🏘️ **社区端** - 群体健康管理、数据大屏

## 📁 项目结构

```
养生之道/
├── frontend/          # React 前端
├── backend/           # FastAPI 后端
│   ├── api/           # API 路由
│   ├── services/      # 业务逻辑
│   ├── database/      # 数据库模型
│   └── knowledge_base/# RAG 知识库
├── data-creation/     # 测试数据生成
└── knowledge-base/    # 健康知识文档
```

## 🔑 测试账号

| 类型 | 账号 | 说明 |
|------|------|------|
| 老人端 | `18262121731` / `demo` | 含模拟健康数据 |

## 📄 相关文档

- [API 文档](backend/API_DOCUMENTATION.md)
- [数据库设计](backend/DATABASE_SCHEMA.md)
- [知识库指南](backend/KNOWLEDGE_BASE_GUIDE.md)
