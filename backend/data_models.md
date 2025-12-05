# 智慧健康管理系统 - 数据模型规范

## 1. 用户表 (users)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 用户唯一标识符 |
| `username` | `VARCHAR(100)` | `UNIQUE NOT NULL` | 用户名/账号 |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | 密码哈希值 |
| `role` | `ENUM('elderly', 'children', 'community')` | `NOT NULL` | 用户角色 |
| `phone_number` | `VARCHAR(20)` | `UNIQUE` | 手机号码 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |
| `status` | `ENUM('active', 'inactive')` | `DEFAULT 'active'` | 账户状态 |

## 2. 老人基础信息表 (elderly_profiles)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 老人档案ID |
| `user_id` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 关联的用户ID |
| `name` | `VARCHAR(50)` | `NOT NULL` | 老人姓名 |
| `gender` | `ENUM('male', 'female', 'other')` | `NOT NULL` | 性别 |
| `birth_date` | `DATE` | `NOT NULL` | 出生日期 |
| `age` | `INTEGER` | `GENERATED ALWAYS AS (TIMESTAMPDIFF(YEAR, birth_date, CURRENT_DATE))` | 年龄（计算字段） |
| `id_card` | `VARCHAR(18)` | `UNIQUE` | 身份证号 |
| `address` | `VARCHAR(255)` | | 居住地址 |
| `emergency_contact` | `VARCHAR(50)` | | 紧急联系人 |
| `emergency_phone` | `VARCHAR(20)` | | 紧急联系电话 |
| `medical_history` | `TEXT` | | 病史 |
| `medications` | `TEXT` | | 用药情况 |
| `avatar` | `VARCHAR(255)` | | 头像URL |
| `blood_type` | `ENUM('A', 'B', 'AB', 'O', 'unknown')` | `DEFAULT 'unknown'` | 血型 |
| `height` | `DECIMAL(5,2)` | | 身高(cm) |
| `weight` | `DECIMAL(5,2)` | | 体重(kg) |
| `bmi` | `DECIMAL(4,2)` | `GENERATED ALWAYS AS (weight / POWER(height/100, 2))` | BMI指数（计算字段） |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

## 3. 子女表 (children_profiles)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 子女档案ID |
| `user_id` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 关联的用户ID |
| `name` | `VARCHAR(50)` | `NOT NULL` | 子女姓名 |
| `gender` | `ENUM('male', 'female', 'other')` | | 性别 |
| `phone_number` | `VARCHAR(20)` | `UNIQUE` | 手机号码 |
| `address` | `VARCHAR(255)` | | 居住地址 |
| `avatar` | `VARCHAR(255)` | | 头像URL |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

## 4. 社区表 (communities)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 社区ID |
| `user_id` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 关联的用户ID |
| `community_name` | `VARCHAR(100)` | `NOT NULL` | 社区名称 |
| `contact_person` | `VARCHAR(50)` | `NOT NULL` | 联系人 |
| `contact_phone` | `VARCHAR(20)` | `NOT NULL` | 联系电话 |
| `address` | `VARCHAR(255)` | `NOT NULL` | 社区地址 |
| `description` | `TEXT` | | 社区描述 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

## 5. 健康数据表 (health_records)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 记录ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `recorded_at` | `TIMESTAMP` | `NOT NULL` | 记录时间 |
| `heart_rate` | `INTEGER` | | 心率(次/分) |
| `systolic_pressure` | `INTEGER` | | 收缩压(mmHg) |
| `diastolic_pressure` | `INTEGER` | | 舒张压(mmHg) |
| `blood_sugar` | `DECIMAL(4,2)` | | 血糖(mmol/L) |
| `temperature` | `DECIMAL(3,1)` | | 体温(°C) |
| `steps` | `INTEGER` | | 步数 |
| `sleep_hours` | `DECIMAL(3,1)` | | 睡眠时间(小时) |
| `deep_sleep_hours` | `DECIMAL(3,1)` | | 深度睡眠时间(小时) |
| `light_sleep_hours` | `DECIMAL(3,1)` | | 浅度睡眠时间(小时) |
| `sleep_quality` | `INTEGER` | | 睡眠质量评分(0-100) |
| `blood_oxygen` | `DECIMAL(4,1)` | | 血氧饱和度(%) |
| `weight` | `DECIMAL(5,2)` | | 体重(kg) |
| `notes` | `TEXT` | | 备注 |
| `status` | `ENUM('normal', 'warning', 'danger')` | `DEFAULT 'normal'` | 健康状态 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

## 6. 健康指标预警表 (health_alerts)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 预警ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `health_record_id` | `UUID` | `FOREIGN KEY REFERENCES health_records(id)` | 关联的健康记录ID |
| `alert_type` | `VARCHAR(50)` | `NOT NULL` | 预警类型 |
| `alert_message` | `TEXT` | `NOT NULL` | 预警信息 |
| `severity` | `ENUM('low', 'medium', 'high')` | `DEFAULT 'medium'` | 严重程度 |
| `status` | `ENUM('active', 'resolved', 'dismissed')` | `DEFAULT 'active'` | 预警状态 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `resolved_at` | `TIMESTAMP` | | 解决时间 |

## 7. 提醒表 (reminders)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 提醒ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `created_by` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 创建者ID |
| `title` | `VARCHAR(100)` | `NOT NULL` | 提醒标题 |
| `description` | `TEXT` | | 提醒描述 |
| `reminder_type` | `VARCHAR(50)` | `NOT NULL` | 提醒类型 |
| `frequency` | `VARCHAR(50)` | | 频率 |
| `next_reminder_time` | `TIMESTAMP` | `NOT NULL` | 下次提醒时间 |
| `status` | `ENUM('active', 'inactive', 'completed')` | `DEFAULT 'active'` | 提醒状态 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

## 8. 子女-老人关系表 (child_elderly_relations)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 关系ID |
| `child_id` | `UUID` | `FOREIGN KEY REFERENCES children_profiles(id)` | 子女ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `relationship_type` | `VARCHAR(50)` | `NOT NULL` | 关系类型 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

## 9. 社区-老人关系表 (community_elderly_relations)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 关系ID |
| `community_id` | `UUID` | `FOREIGN KEY REFERENCES communities(id)` | 社区ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `registered_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 注册时间 |
| `status` | `ENUM('active', 'inactive')` | `DEFAULT 'active'` | 状态 |

## 10. 健康报告表 (health_reports)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 报告ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `report_type` | `VARCHAR(50)` | `NOT NULL` | 报告类型 |
| `report_period` | `VARCHAR(50)` | `NOT NULL` | 报告周期 |
| `start_date` | `DATE` | `NOT NULL` | 开始日期 |
| `end_date` | `DATE` | `NOT NULL` | 结束日期 |
| `content` | `TEXT` | `NOT NULL` | 报告内容 |
| `summary` | `TEXT` | | 报告摘要 |
| `recommendations` | `TEXT` | | 健康建议 |
| `generated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 生成时间 |
| `generated_by` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 生成者ID |

## 11. 健康评估表 (health_assessments)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 评估ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 老人ID |
| `assessment_date` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 评估日期 |
| `cardiovascular_score` | `INTEGER` | | 心血管评分(0-100) |
| `sleep_quality_score` | `INTEGER` | | 睡眠质量评分(0-100) |
| `exercise_score` | `INTEGER` | | 运动评分(0-100) |
| `nutrition_score` | `INTEGER` | | 营养评分(0-100) |
| `mental_health_score` | `INTEGER` | | 心理健康评分(0-100) |
| `weight_management_score` | `INTEGER` | | 体重管理评分(0-100) |
| `overall_score` | `INTEGER` | | 总体评分(0-100) |
| `notes` | `TEXT` | | 评估备注 |
| `assessed_by` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 评估者ID |

## 12. AI咨询记录表 (ai_consultations)

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY` | 咨询记录ID |
| `user_id` | `UUID` | `FOREIGN KEY REFERENCES users(id)` | 用户ID |
| `elderly_id` | `UUID` | `FOREIGN KEY REFERENCES elderly_profiles(id)` | 相关老人ID |
| `query_text` | `TEXT` | `NOT NULL` | 用户提问 |
| `response_text` | `TEXT` | `NOT NULL` | AI回答 |
| `query_type` | `VARCHAR(50)` | | 咨询类型 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

## 字段命名规范

1. **主键**: 统一使用 `id` 作为主键字段名
2. **关联字段**: 使用 `{表名}_id` 格式，如 `elderly_id`
3. **布尔状态**: 使用 `is_` 前缀，如 `is_active`
4. **时间字段**:
   - 创建时间: `created_at`
   - 更新时间: `updated_at`
   - 删除时间: `deleted_at` (用于软删除)
5. **复合词**: 使用下划线分隔，如 `blood_pressure`
6. **状态字段**: 使用明确的状态枚举，如 `status` 或特定状态字段如 `alert_status`
7. **外键索引**: 所有外键必须建立索引以提高查询性能

## 数据校验规则

1. **必填字段**: 明确标记 `NOT NULL` 约束
2. **唯一性约束**: 使用 `UNIQUE` 约束确保唯一值
3. **数据范围**: 对数值类型设置合理的范围约束
4. **长度限制**: 对字符串类型设置适当的长度限制
5. **日期时间**: 使用 `TIMESTAMP` 或 `DATE` 类型存储日期时间信息
6. **枚举值**: 使用 `ENUM` 限制字段只能使用预定义的值
7. **正则验证**: 对特殊格式字段如电话号码、身份证号等使用正则表达式验证

## 数据安全规范

1. **密码存储**: 使用bcrypt等安全算法对密码进行哈希存储
2. **敏感信息加密**: 对身份证号等敏感信息进行加密存储
3. **数据脱敏**: 在API响应中对敏感字段进行脱敏处理
4. **访问控制**: 根据用户角色严格控制数据访问权限
5. **数据审计**: 记录关键操作的审计日志
6. **软删除**: 对重要数据使用软删除而非物理删除

## 数据同步规范

1. **实时性要求**: 健康监测数据需要保证准实时同步
2. **批处理优化**: 非实时数据可以采用批处理方式同步
3. **数据一致性**: 确保跨系统数据的最终一致性
4. **错误处理**: 数据同步失败时的重试和错误处理机制