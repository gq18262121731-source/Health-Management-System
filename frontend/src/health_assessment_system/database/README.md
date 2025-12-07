# 数据库设计说明

## 表结构概览

```
┌─────────────────┐     ┌──────────────────┐
│   elder_info    │     │   user_account   │
│   (老人信息)     │     │   (用户账号)      │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         │    ┌──────────────────┤
         │    │                  │
         ▼    ▼                  │
┌─────────────────────┐          │
│ elder_user_relation │          │
│   (老人-用户关系)    │◄─────────┘
└─────────────────────┘
         │
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  health_record  │────►│assessment_result │
│  (健康检测明细)  │     │   (评估结果)      │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  ai_consult_log  │
                        │  (AI问诊记录)     │
                        └──────────────────┘
```

## 表说明

| 序号 | 表名 | 用途 | 核心字段 |
|-----|------|------|---------|
| 1 | `elder_info` | 老人基础信息 | 姓名、性别、年龄、慢病标签 |
| 2 | `user_account` | 统一登录账号 | 用户名、密码、角色 |
| 3 | `elder_user_relation` | 老人与用户关系 | 关系类型、是否主要联系人 |
| 4 | `health_record` | 每次检测明细 | 20项体征数据 |
| 5 | `assessment_result` | 综合评估结果 | 风险评分、AHP/TOPSIS结果 |
| 6 | `ai_consult_log` | AI问诊记录 | 问答内容、模型版本 |

## 快速开始

### 1. 创建数据库

```bash
mysql -u root -p < schema.sql
```

### 2. 连接配置

```python
# config/database.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'health_assessment_db',
    'charset': 'utf8mb4'
}
```

## 索引说明

| 表 | 索引 | 用途 |
|---|------|------|
| `health_record` | `idx_record_elder_time` | 按老人+时间查询检测记录 |
| `assessment_result` | `idx_assessment_window` | 按时间窗口查询评估 |
| `ai_consult_log` | `idx_consult_elder` | 查询老人的问诊历史 |

## 视图

| 视图名 | 用途 |
|-------|------|
| `v_elder_latest_record` | 查询每位老人最新一条检测记录 |
| `v_elder_latest_assessment` | 查询每位老人最新一次评估结果 |

## 字段约定

### 状态字段
- `status = 1` 表示有效/在管
- `status = 0` 表示禁用/已离开

### 性别字段
- `gender = 0` 女
- `gender = 1` 男
- `gender = 2` 其他或未知

### 角色字段
- `ELDER` - 老人端
- `FAMILY` - 家属端
- `COMMUNITY` - 社区端
- `ADMIN` - 管理员

### 风险等级
- `LOW` - 低风险
- `MEDIUM` - 中风险
- `HIGH` - 高风险
- `CRITICAL` - 危急

### 建议等级
- `OBSERVE` - 观察
- `OUTPATIENT` - 建议门诊
- `EMERGENCY` - 紧急就医
