# 🏥 养生之道 - 智慧健康管理系统

> 基于人工智能与物联网技术的社区老年健康监测与服务平台

## 📋 项目概述

**养生之道**是一款面向社区老年群体的智慧健康管理系统，通过**物联网数据采集**、**AI智能分析**、**多智能体协作**、**专业评估算法**、**语音交互**等技术，实现健康数据的实时监测、智能预警和个性化健康建议。

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
| **AI服务** | DeepSeek/智谱GLM/通义千问 + RAG知识库 |
| **多智能体** | 健康管家、慢病专家、生活教练、心理关怀师 |
| **评估算法** | 模糊逻辑、AHP层次分析、TOPSIS、Isolation Forest |
| **语音** | Edge-TTS（语音合成）+ FunASR（语音识别）|
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

### 🤖 多智能体系统
- 🏠 **健康管家** - 日常健康问答、数据解读、健康提醒
- 🩺 **慢病专家** - 高血压/糖尿病/血脂风险评估与管理建议
- 🏃 **生活教练** - 运动处方、饮食营养、睡眠改善指导
- 💚 **心理关怀师** - 情绪识别、心理疏导、陪伴关怀

### 📈 专业评估算法
- 🔬 **模糊逻辑** - 处理阈值边界的疾病风险评估
- ⚖️ **AHP层次分析** - 多维度健康权重确定
- 📊 **TOPSIS排序** - 风险因素优先级排序
- 🔍 **Isolation Forest** - 异常行为检测
- 📉 **趋势分析** - 线性回归、波动检测、连续异常预警

### AI 智能助手
- 🤖 **智能问诊** - 基于症状的健康咨询
- 📝 **健康报告** - AI生成个性化健康分析报告
- 💡 **健康建议** - 基于RAG知识库的专业建议
- 🎯 **意图识别** - 规则+LLM混合意图识别

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
Health-Management-System/
├── frontend/                    # React 前端
├── backend/                     # FastAPI 后端
│   ├── api/routes/              # API 路由
│   │   ├── health_assessment.py # 健康评估API
│   │   ├── ai.py                # AI对话API
│   │   └── ...
│   ├── services/
│   │   ├── agents/              # 多智能体系统
│   │   │   ├── base_agent.py    # 智能体基类
│   │   │   ├── health_butler.py # 健康管家
│   │   │   ├── chronic_disease_expert.py  # 慢病专家
│   │   │   ├── lifestyle_coach.py         # 生活教练
│   │   │   ├── emotional_care.py          # 心理关怀师
│   │   │   ├── intent_recognizer.py       # 意图识别
│   │   │   └── multi_agent_service.py     # 多智能体服务
│   │   ├── health_assessment/   # 健康评估算法
│   │   │   ├── disease_assessment.py      # 疾病风险评估
│   │   │   ├── lifestyle_assessment.py    # 生活方式评估
│   │   │   ├── comprehensive_assessment.py # 综合评估(AHP+TOPSIS)
│   │   │   ├── trend_alert.py             # 趋势预警
│   │   │   └── assessment_service.py      # 评估服务适配层
│   │   ├── ai_service.py        # AI服务
│   │   └── knowledge_base.py    # RAG知识库
│   ├── database/                # 数据库模型
│   └── knowledge_base/          # 知识库文档
├── data-creation/               # 测试数据生成
└── knowledge-base/              # 健康知识文档
```

## 🔑 测试账号

| 类型 | 账号 | 说明 |
|------|------|------|
| 老人端 | `18262121731` / `demo` | 含模拟健康数据 |

## 🔌 API 接口

### 健康评估 API (`/api/assessment`)
| 接口 | 方法 | 说明 |
|------|------|------|
| `/blood-pressure` | POST | 血压风险评估（模糊逻辑） |
| `/blood-sugar` | POST | 血糖风险评估 |
| `/lifestyle` | POST | 生活方式评估 |
| `/trend` | POST | 趋势分析预警 |
| `/comprehensive` | POST | 综合健康评估（AHP+TOPSIS） |
| `/elderly/{id}` | GET | 获取老人综合评估 |

### AI 对话 API (`/api/ai`)
| 接口 | 方法 | 说明 |
|------|------|------|
| `/consult` | POST | AI健康咨询（多智能体） |
| `/agents` | GET | 获取智能体列表 |

## 📄 相关文档

- [API 文档](backend/API_DOCUMENTATION.md)
- [数据库设计](backend/DATABASE_SCHEMA.md)
- [知识库指南](backend/KNOWLEDGE_BASE_GUIDE.md)

## 📜 License

MIT License
