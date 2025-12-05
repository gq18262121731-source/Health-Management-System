# 数据库模型规范文档

> **最后更新**: 2024年12月
> 
> 本文档描述智慧健康管理系统的完整数据库模型结构，确保前后端和文档的一致性。

## 📋 目录

1. [用户相关表](#用户相关表)
2. [健康数据表](#健康数据表)
3. [AI和知识库表](#ai和知识库表)
4. [关系表](#关系表)
5. [枚举类型](#枚举类型)
6. [字段命名规范](#字段命名规范)

---

## 用户相关表

### 1. users (用户表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 用户唯一标识符 | 自动生成 |
| `username` | `VARCHAR(100)` | UNIQUE, NOT NULL, INDEX | 用户名/账号 | |
| `password` | `VARCHAR(255)` | NOT NULL | 密码哈希值 | 使用bcrypt加密 |
| `role` | `ENUM` | NOT NULL | 用户角色 | 见枚举类型 |
| `status` | `ENUM` | DEFAULT 'active' | 账户状态 | 见枚举类型 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | 时区感知 |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | 自动更新 |
| `last_login_at` | `TIMESTAMP` | NULLABLE | 最后登录时间 | |

**关系：**
- 一对一：`elderly_profile`, `children_profile`, `community_profile`
- 一对多：`ai_queries`

**索引：**
- `username` (UNIQUE INDEX)

---

### 2. elderly_profiles (老人基本信息表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 老人档案ID | 自动生成 |
| `user_id` | `UUID` | FOREIGN KEY, UNIQUE, NOT NULL | 关联的用户ID | 引用 users.id |
| `name` | `VARCHAR(50)` | NOT NULL | 老人姓名 | |
| `gender` | `ENUM` | NOT NULL | 性别 | 见枚举类型 |
| `birth_date` | `TIMESTAMP` | NOT NULL | 出生日期 | 时区感知 |
| `age` | `INTEGER` | NOT NULL | 年龄 | 根据birth_date计算 |
| `address` | `VARCHAR(255)` | NOT NULL | 居住地址 | |
| `phone_number` | `VARCHAR(20)` | NULLABLE | 手机号码 | |
| `emergency_contact` | `VARCHAR(50)` | NULLABLE | 紧急联系人 | |
| `emergency_phone` | `VARCHAR(20)` | NULLABLE | 紧急联系电话 | |
| `medical_history` | `TEXT` | NULLABLE | 病史 | |
| `medications` | `TEXT` | NULLABLE | 用药情况 | |
| `avatar` | `VARCHAR(255)` | NULLABLE | 头像URL | |
| `blood_type` | `VARCHAR(5)` | NULLABLE | 血型 | A, B, AB, O |
| `height` | `FLOAT` | NULLABLE | 身高(cm) | |
| `weight` | `FLOAT` | NULLABLE | 体重(kg) | |
| `bmi` | `FLOAT` | NULLABLE | 体重指数 | 计算字段 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | |

**关系：**
- 多对一：`user`
- 一对多：`health_records`, `sleep_data`, `alerts`, `reminders`, `health_assessments`, `children_relations`, `ai_queries`

**注意：** 
- 文档中提到的 `health_status` 字段**不存在**于此表，健康状态应根据 `health_records` 中的最新数据动态计算。

---

### 3. children_profiles (子女信息表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 子女档案ID | 自动生成 |
| `user_id` | `UUID` | FOREIGN KEY, UNIQUE, NOT NULL | 关联的用户ID | 引用 users.id |
| `name` | `VARCHAR(50)` | NOT NULL | 子女姓名 | |
| `phone_number` | `VARCHAR(20)` | NULLABLE | 手机号码 | |
| `avatar` | `VARCHAR(255)` | NULLABLE | 头像URL | |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | |

**关系：**
- 多对一：`user`
- 一对多：`elderly_relations`

---

### 4. community_profiles (社区信息表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 社区档案ID | 自动生成 |
| `user_id` | `UUID` | FOREIGN KEY, UNIQUE, NOT NULL | 关联的用户ID | 引用 users.id |
| `community_name` | `VARCHAR(100)` | NOT NULL | 社区名称 | |
| `address` | `VARCHAR(255)` | NOT NULL | 社区地址 | |
| `contact_person` | `VARCHAR(50)` | NOT NULL | 联系人 | |
| `contact_phone` | `VARCHAR(20)` | NOT NULL | 联系电话 | |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | |

**关系：**
- 多对一：`user`
- 一对多：`reports`

---

## 健康数据表

### 5. health_records (健康记录表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 记录ID | 自动生成 |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `heart_rate` | `INTEGER` | NULLABLE | 心率(bpm) | 单位：次/分钟 |
| `systolic_pressure` | `INTEGER` | NULLABLE | 收缩压(mmHg) | |
| `diastolic_pressure` | `INTEGER` | NULLABLE | 舒张压(mmHg) | |
| `blood_sugar` | `FLOAT` | NULLABLE | 血糖(mmol/L) | |
| `temperature` | `FLOAT` | NULLABLE | 体温(℃) | |
| `blood_oxygen` | `FLOAT` | NULLABLE | 血氧饱和度(%) | |
| `weight` | `FLOAT` | NULLABLE | 体重(kg) | |
| `steps` | `INTEGER` | NULLABLE | 步数 | |
| `notes` | `TEXT` | NULLABLE | 备注 | |
| `status` | `ENUM` | DEFAULT 'normal' | 健康状态 | 见枚举类型 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `recorded_at` | `TIMESTAMP` | DEFAULT NOW() | 记录时间 | 数据采集时间 |

**关系：**
- 多对一：`elderly`
- 一对多：`alerts` (通过health_record_id)

**注意：**
- **睡眠数据不在本表中**，睡眠相关数据存储在 `sleep_data` 表中
- 血压存储为两个独立字段：`systolic_pressure` 和 `diastolic_pressure`
- API响应中应组合为字符串格式：`"{systolic_pressure}/{diastolic_pressure}"`

---

### 6. sleep_data (睡眠数据表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 睡眠记录ID | 自动生成 |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `date` | `TIMESTAMP` | NOT NULL | 睡眠日期 | 时区感知 |
| `sleep_start_time` | `TIMESTAMP` | NULLABLE | 睡眠开始时间 | |
| `sleep_end_time` | `TIMESTAMP` | NULLABLE | 睡眠结束时间 | |
| `total_hours` | `FLOAT` | NOT NULL | 总睡眠时间(小时) | |
| `deep_sleep_hours` | `FLOAT` | NOT NULL | 深度睡眠(小时) | |
| `light_sleep_hours` | `FLOAT` | NOT NULL | 浅睡眠(小时) | |
| `quality` | `INTEGER` | NOT NULL | 睡眠质量评分 | 0-100 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |

**关系：**
- 多对一：`elderly`

**注意：**
- 睡眠数据与健康记录分开存储，不在 `health_records` 表中

---

### 7. alerts (预警信息表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 预警ID | 自动生成 |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `alert_type` | `ENUM` | NOT NULL | 预警类型 | 见枚举类型 |
| `alert_message` | `VARCHAR(255)` | NOT NULL | 预警信息 | |
| `severity` | `ENUM` | NOT NULL | 严重程度 | 见枚举类型 |
| `status` | `ENUM` | DEFAULT 'active' | 预警状态 | 见枚举类型 |
| `health_record_id` | `UUID` | FOREIGN KEY, NULLABLE | 关联健康记录ID | 引用 health_records.id |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | |

**关系：**
- 多对一：`elderly`, `health_record`
- 一对一：`resolution`

---

### 8. alert_resolutions (预警解决方案表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 解决方案ID | 自动生成 |
| `alert_id` | `UUID` | FOREIGN KEY, UNIQUE, NOT NULL | 预警ID | 引用 alerts.id |
| `resolved_by` | `UUID` | FOREIGN KEY, NULLABLE | 处理人ID | 引用 users.id |
| `resolution_time` | `TIMESTAMP` | DEFAULT NOW() | 处理时间 | |
| `resolution_method` | `VARCHAR(255)` | NOT NULL | 处理方法 | |
| `notes` | `TEXT` | NULLABLE | 备注 | |

**关系：**
- 多对一：`alert`, `resolver`

---

### 9. reminders (提醒表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 提醒ID | 自动生成 |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `created_by` | `UUID` | FOREIGN KEY, NOT NULL | 创建者ID | 引用 users.id |
| `title` | `VARCHAR(100)` | NOT NULL | 提醒标题 | |
| `description` | `TEXT` | NULLABLE | 提醒描述 | |
| `reminder_type` | `ENUM` | NOT NULL | 提醒类型 | 见枚举类型 |
| `frequency` | `ENUM` | DEFAULT 'once' | 提醒频率 | 见枚举类型 |
| `next_reminder_time` | `TIMESTAMP` | NOT NULL | 下次提醒时间 | |
| `status` | `ENUM` | DEFAULT 'active' | 提醒状态 | 见枚举类型 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |
| `updated_at` | `TIMESTAMP` | DEFAULT NOW() | 更新时间 | |

**关系：**
- 多对一：`elderly`, `creator`

---

### 10. health_assessments (健康评估表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 评估ID | 自动生成 |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `cardiovascular` | `INTEGER` | NOT NULL | 心血管健康评分 | 0-100 |
| `sleep_quality` | `INTEGER` | NOT NULL | 睡眠质量评分 | 0-100 |
| `exercise` | `INTEGER` | NOT NULL | 运动情况评分 | 0-100 |
| `nutrition` | `INTEGER` | NOT NULL | 营养状况评分 | 0-100 |
| `mental_health` | `INTEGER` | NOT NULL | 心理健康评分 | 0-100 |
| `weight_management` | `INTEGER` | NOT NULL | 体重管理评分 | 0-100 |
| `overall` | `INTEGER` | NOT NULL | 整体健康评分 | 0-100 |
| `assessment_date` | `TIMESTAMP` | DEFAULT NOW() | 评估日期 | |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |

**关系：**
- 多对一：`elderly`

---

## AI和知识库表

### 11. ai_queries (AI咨询记录表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 咨询记录ID | 自动生成 |
| `user_id` | `UUID` | FOREIGN KEY, NOT NULL | 用户ID | 引用 users.id |
| `elderly_id` | `UUID` | FOREIGN KEY, NULLABLE | 关联的老人ID | 引用 elderly_profiles.id |
| `query_text` | `TEXT` | NOT NULL | 用户提问 | |
| `query_type` | `ENUM` | NOT NULL | 咨询类型 | 见枚举类型 |
| `response_text` | `TEXT` | NOT NULL | AI回答 | |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |

**关系：**
- 多对一：`user`, `elderly`

**注意：**
- 表名为 `ai_queries`，不是 `ai_consultations`

---

### 12. 知识库（非数据库表）

知识库使用文件系统存储：
- 向量索引：`knowledge_base_index.faiss`
- 文档数据：`knowledge_base_docs.json`
- 嵌入模型：`m3e-base` (中文优化)

**文档结构：**
```json
{
  "doc_id": {
    "content": "文档内容",
    "metadata": {
      "title": "文档标题",
      "source": "来源",
      "elderly_id": "关联的老人ID（可选）"
    }
  }
}
```

---

## 关系表

### 13. children_elderly_relations (子女老人关系表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 关系ID | 自动生成 |
| `children_id` | `UUID` | FOREIGN KEY, NOT NULL | 子女ID | 引用 children_profiles.id |
| `elderly_id` | `UUID` | FOREIGN KEY, NOT NULL | 老人ID | 引用 elderly_profiles.id |
| `relationship_type` | `ENUM` | NOT NULL | 关系类型 | 见枚举类型 |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | 创建时间 | |

**关系：**
- 多对一：`children`, `elderly`

---

### 14. community_reports (社区报告表)

| 字段名 | 数据类型 | 约束 | 描述 | 备注 |
|--------|----------|------|------|------|
| `id` | `UUID` | PRIMARY KEY | 报告ID | 自动生成 |
| `community_id` | `UUID` | FOREIGN KEY, NOT NULL | 社区ID | 引用 community_profiles.id |
| `report_type` | `ENUM` | NOT NULL | 报告类型 | 见枚举类型 |
| `start_date` | `TIMESTAMP` | NOT NULL | 开始日期 | |
| `end_date` | `TIMESTAMP` | NOT NULL | 结束日期 | |
| `summary` | `TEXT` | NOT NULL | 报告摘要 | |
| `report_data` | `TEXT` | NOT NULL | 报告数据 | JSON格式 |
| `generated_at` | `TIMESTAMP` | DEFAULT NOW() | 生成时间 | |

**关系：**
- 多对一：`community`

---

## 枚举类型

### UserRole (用户角色)
```python
ELDERLY = "elderly"      # 老人
CHILDREN = "children"    # 子女
COMMUNITY = "community"  # 社区
```

### UserStatus (用户状态)
```python
ACTIVE = "active"        # 活跃
INACTIVE = "inactive"    # 未激活
LOCKED = "locked"        # 已锁定
```

### Gender (性别)
```python
MALE = "male"            # 男性
FEMALE = "female"        # 女性
OTHER = "other"          # 其他
```

### RelationshipType (关系类型)
```python
FATHER = "父亲"
MOTHER = "母亲"
SON = "儿子"
DAUGHTER = "女儿"
HUSBAND = "丈夫"
WIFE = "妻子"
OTHER = "其他"
```

### HealthRecordStatus (健康记录状态)
```python
NORMAL = "normal"        # 正常
WARNING = "warning"      # 警告
DANGER = "danger"        # 危险
```

### AlertType (预警类型)
```python
HEART_RATE_HIGH = "heart_rate_high"
HEART_RATE_LOW = "heart_rate_low"
BLOOD_PRESSURE_HIGH = "blood_pressure_high"
BLOOD_PRESSURE_LOW = "blood_pressure_low"
BLOOD_SUGAR_HIGH = "blood_sugar_high"
BLOOD_SUGAR_LOW = "blood_sugar_low"
TEMPERATURE_HIGH = "temperature_high"
TEMPERATURE_LOW = "temperature_low"
BLOOD_OXYGEN_LOW = "blood_oxygen_low"
FALL_DETECTED = "fall_detected"
NO_ACTIVITY = "no_activity"
MEDICATION_MISSED = "medication_missed"
OTHER = "other"
```

### AlertSeverity (预警严重程度)
```python
LOW = "low"              # 低
MEDIUM = "medium"        # 中
HIGH = "high"            # 高
```

### AlertStatus (预警状态)
```python
ACTIVE = "active"        # 活跃
RESOLVED = "resolved"    # 已解决
DISMISSED = "dismissed"  # 已忽略
```

### ReminderType (提醒类型)
```python
MEDICATION = "medication"    # 用药
EXERCISE = "exercise"        # 运动
MEAL = "meal"                # 用餐
MEASUREMENT = "measurement"  # 测量
OTHER = "other"              # 其他
```

### ReminderFrequency (提醒频率)
```python
ONCE = "once"            # 一次
DAILY = "daily"          # 每天
WEEKLY = "weekly"        # 每周
MONTHLY = "monthly"      # 每月
CUSTOM = "custom"        # 自定义
```

### ReminderStatus (提醒状态)
```python
ACTIVE = "active"        # 活跃
INACTIVE = "inactive"    # 未激活
COMPLETED = "completed"  # 已完成
EXPIRED = "expired"      # 已过期
```

### QueryType (AI查询类型)
```python
HEALTH_ADVICE = "health_advice"                  # 健康建议
DISEASE_INFORMATION = "disease_information"      # 疾病信息
MEDICATION_INFORMATION = "medication_information" # 用药信息
LIFE_SUGGESTION = "life_suggestion"              # 生活建议
OTHER = "other"                                  # 其他
```

### ReportType (报告类型)
```python
DAILY = "daily"          # 日报
WEEKLY = "weekly"        # 周报
MONTHLY = "monthly"      # 月报
CUSTOM = "custom"        # 自定义
```

---

## 字段命名规范

### 1. 主键和ID
- 所有表的主键统一使用 `id` (UUID类型)
- 外键使用 `{表名}_id` 格式，如 `elderly_id`, `user_id`

### 2. 时间字段
- 创建时间：`created_at` (TIMESTAMP with timezone)
- 更新时间：`updated_at` (TIMESTAMP with timezone)
- 特定时间：使用描述性名称，如 `birth_date`, `recorded_at`, `assessment_date`

### 3. 布尔和状态字段
- 状态字段：使用 `status` (ENUM类型)
- 布尔字段：建议使用明确的枚举值而非布尔类型

### 4. 字符串字段长度限制
- 姓名：`VARCHAR(50)`
- 地址：`VARCHAR(255)`
- 手机号：`VARCHAR(20)`
- 标题：`VARCHAR(100)`
- 描述性文本：`TEXT`

### 5. 数值字段
- 整数：`INTEGER`
- 浮点数：`FLOAT`
- 精确小数：`DECIMAL(precision, scale)`

---

## 重要说明

### 不一致修复记录

1. **User表密码字段**
   - ❌ 文档中写的是 `password_hash`
   - ✅ **实际数据库字段为** `password`
   - ✅ **但存储的是哈希值**，代码中通过 `get_password_hash()` 函数处理

2. **API端点路径**
   - ❌ 文档中：`/api/user/login`
   - ✅ **实际路径为** `/api/auth/login`
   - ✅ **实际路径为** `/api/auth/register`

3. **健康状态字段**
   - ❌ 文档中提到 `elderly_profiles.health_status`
   - ✅ **该字段不存在**，健康状态应从 `health_records` 动态计算

4. **睡眠数据存储**
   - ❌ 文档中误将睡眠字段放在 `health_records` 表
   - ✅ **睡眠数据存储在独立的** `sleep_data` 表

5. **AI咨询表名**
   - ❌ 文档中：`ai_consultations`
   - ✅ **实际表名为** `ai_queries`

6. **ElderlyProfile字段**
   - ✅ 数据库模型中**没有** `health_status` 字段
   - ✅ 但API响应可能需要计算并返回健康状态（从health_records计算）

---

## 数据完整性约束

### 外键约束
- 所有外键都建立了适当的索引
- 删除策略：CASCADE 用于级联删除（如删除用户时删除关联档案）

### 唯一性约束
- `users.username`: UNIQUE
- `users.phone_number`: 可能为UNIQUE（需验证）
- `elderly_profiles.user_id`: UNIQUE
- `children_profiles.user_id`: UNIQUE
- `community_profiles.user_id`: UNIQUE

### 必填字段
- 所有主键和必要关联字段都标记为 NOT NULL
- 可选字段标记为 NULLABLE

---

## 数据迁移注意事项

1. 如果现有数据库使用了不同的字段名，需要创建迁移脚本
2. UUID类型确保全局唯一性
3. 时区感知的时间戳确保跨时区一致性
4. 枚举类型确保数据有效性

---

## 参考

- 数据库模型定义：`backend/database/models.py`
- Schema定义：`backend/schemas/models.py`
- API路由：`backend/api/routes/`


