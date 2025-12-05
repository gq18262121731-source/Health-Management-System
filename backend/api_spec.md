# 智慧健康管理系统 - API接口规范

## 1. 认证接口

### 1.1 角色选择

```
GET /api/auth/roles
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "roles": [
      { "value": "elderly", "label": "老人端" },
      { "value": "children", "label": "子女端" },
      { "value": "community", "label": "社区端" }
    ]
  }
}
```

### 1.2 用户登录

```
POST /api/auth/login
```

**请求参数**:
```json
{
  "role": "elderly|children|community",
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "string",
      "role": "string",
      "profile": {}
    }
  }
}
```

### 1.3 用户登出

```
POST /api/auth/logout
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "message": "登出成功"
}
```

## 2. 老人相关接口

### 2.1 获取老人基础信息

```
GET /api/elderly/profile/{id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "张三",
    "gender": "male",
    "age": 68,
    "birth_date": "1956-05-15",
    "address": "广东省广州市天河区XX街道XX社区",
    "phone_number": "13800138000",
    "emergency_contact": "李四",
    "emergency_phone": "13900139000",
    "medical_history": "高血压、糖尿病",
    "medications": "二甲双胍 0.5g 每日三次",
    "avatar": "url",
    "blood_type": "A",
    "height": 170.0,
    "weight": 68.5,
    "bmi": 23.6
  }
}
```

### 2.2 更新老人基础信息

```
PUT /api/elderly/profile/{id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "address": "string",
  "phone_number": "string",
  "emergency_contact": "string",
  "emergency_phone": "string",
  "medical_history": "string",
  "medications": "string",
  "height": 170.0,
  "weight": 68.5
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "张三",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

### 2.3 获取老人实时健康数据

```
GET /api/elderly/{id}/health/realtime
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "heart_rate": 72,
    "blood_pressure": {
      "systolic": 120,
      "diastolic": 80
    },
    "blood_sugar": 5.2,
    "temperature": 36.5,
    "steps": 8542,
    "blood_oxygen": 98.5,
    "weight": 68.5,
    "recorded_at": "2024-01-01T15:30:00Z",
    "status": "normal"
  }
}
```

### 2.4 获取老人健康数据历史

```
GET /api/elderly/{id}/health/history
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `type`: 数据类型 (heart_rate, blood_pressure, blood_sugar, temperature, all)
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "records": [
      {
        "id": "uuid",
        "heart_rate": 72,
        "systolic_pressure": 120,
        "diastolic_pressure": 80,
        "blood_sugar": 5.2,
        "temperature": 36.5,
        "recorded_at": "2024-01-01T15:30:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  }
}
```

### 2.5 获取老人睡眠数据

```
GET /api/elderly/{id}/sleep/data
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应**:
```json
{
  "status": "success",
  "data": {
    "records": [
      {
        "date": "2024-01-01",
        "total_hours": 7.2,
        "deep_sleep_hours": 2.8,
        "light_sleep_hours": 4.4,
        "quality": 85
      }
    ]
  }
}
```

### 2.6 获取老人健康评分

```
GET /api/elderly/{id}/health/assessment
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "cardiovascular": 85,
    "sleep_quality": 78,
    "exercise": 72,
    "nutrition": 88,
    "mental_health": 90,
    "weight_management": 82,
    "overall": 83,
    "assessment_date": "2024-01-01T10:00:00Z"
  }
}
```

### 2.7 获取老人预警信息

```
GET /api/elderly/{id}/alerts
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `status`: 预警状态 (active, resolved, dismissed)
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "id": "uuid",
        "type": "blood_pressure_high",
        "message": "血压偏高，收缩压150mmHg，舒张压95mmHg",
        "severity": "high",
        "status": "active",
        "created_at": "2024-01-01T14:30:00Z"
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### 2.8 创建健康记录

```
POST /api/elderly/{id}/health/records
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "heart_rate": 72,
  "systolic_pressure": 120,
  "diastolic_pressure": 80,
  "blood_sugar": 5.2,
  "temperature": 36.5,
  "blood_oxygen": 98.5,
  "weight": 68.5,
  "notes": "string"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "elderly_id": "uuid",
    "status": "normal",
    "created_at": "2024-01-01T15:30:00Z"
  }
}
```

## 3. 子女相关接口

### 3.1 获取子女管理的老人列表

```
GET /api/children/elderlies
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "elderlies": [
      {
        "id": "uuid",
        "name": "张三",
        "age": 68,
        "relationship": "父亲",
        "avatar": "👴",
        "health": {
          "heart_rate": 72,
          "blood_pressure": "118/75",
          "blood_sugar": 5.2,
          "temperature": 36.5
        },
        "status": "good",
        "alerts": [],
        "last_update": "2分钟前"
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### 3.2 添加老人到子女管理

```
POST /api/children/elderlies
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "elderly_id": "uuid",
  "relationship_type": "父亲"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "elderly_id": "uuid",
    "relationship_type": "父亲",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### 3.3 创建提醒

```
POST /api/children/reminders
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "elderly_id": "uuid",
  "title": "服药提醒",
  "description": "记得服用降压药",
  "reminder_type": "medication",
  "frequency": "daily",
  "next_reminder_time": "2024-01-02T08:00:00Z"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "服药提醒",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### 3.4 获取提醒列表

```
GET /api/children/reminders
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `elderly_id`: 老人ID (可选)
- `status`: 提醒状态 (active, inactive, completed)
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "reminders": [
      {
        "id": "uuid",
        "elderly_id": "uuid",
        "elderly_name": "张三",
        "title": "服药提醒",
        "description": "记得服用降压药",
        "reminder_type": "medication",
        "next_reminder_time": "2024-01-02T08:00:00Z",
        "status": "active"
      }
    ],
    "pagination": {
      "total": 5,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### 3.5 更新提醒

```
PUT /api/children/reminders/{id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "title": "服药提醒",
  "description": "记得服用降压药",
  "frequency": "daily",
  "next_reminder_time": "2024-01-02T09:00:00Z",
  "status": "active"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "服药提醒",
    "updated_at": "2024-01-01T12:30:00Z"
  }
}
```

### 3.6 删除提醒

```
DELETE /api/children/reminders/{id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "message": "提醒删除成功"
}
```

### 3.7 AI健康咨询

```
POST /api/children/ai/consult
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "elderly_id": "uuid",
  "query_text": "老人高血压应该注意什么？",
  "query_type": "health_advice"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "query_text": "老人高血压应该注意什么？",
    "response_text": "老年人高血压患者应注意以下几点：1. 定期监测血压...",
    "created_at": "2024-01-01T15:00:00Z"
  }
}
```

## 4. 社区相关接口

### 4.1 获取社区管理的老人列表

```
GET /api/community/elderlies
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `status`: 健康状态 (good, warning, danger)
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "elderlies": [
      {
        "id": "uuid",
        "name": "张三",
        "age": 68,
        "address": "广东省广州市天河区XX街道XX社区",
        "health_status": "good",
        "alerts_count": 0,
        "registered_at": "2024-01-01T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  }
}
```

### 4.2 获取社区健康数据统计

```
GET /api/community/statistics
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应**:
```json
{
  "status": "success",
  "data": {
    "total_elderlies": 100,
    "active_alerts": 15,
    "health_status_distribution": {
      "good": 75,
      "warning": 15,
      "danger": 10
    },
    "daily_health_checks": [
      { "date": "2024-01-01", "count": 85 },
      { "date": "2024-01-02", "count": 90 }
    ],
    "average_health_scores": {
      "cardiovascular": 82,
      "sleep_quality": 75,
      "exercise": 68,
      "nutrition": 80,
      "mental_health": 85
    }
  }
}
```

### 4.3 获取预警管理列表

```
GET /api/community/alerts
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
- `severity`: 严重程度 (low, medium, high)
- `status`: 预警状态 (active, resolved, dismissed)
- `page`: 页码
- `page_size`: 每页条数

**响应**:
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "id": "uuid",
        "elderly_id": "uuid",
        "elderly_name": "张三",
        "elderly_age": 68,
        "elderly_address": "广东省广州市天河区XX街道XX社区",
        "alert_type": "blood_pressure_high",
        "alert_message": "血压偏高，收缩压150mmHg，舒张压95mmHg",
        "severity": "high",
        "status": "active",
        "created_at": "2024-01-01T14:30:00Z"
      }
    ],
    "pagination": {
      "total": 15,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### 4.4 更新预警状态

```
PUT /api/community/alerts/{id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "status": "resolved",
  "notes": "已联系老人，建议就医检查"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "status": "resolved",
    "resolved_at": "2024-01-01T15:00:00Z"
  }
}
```

### 4.5 生成群体健康分析报告

```
POST /api/community/reports/group
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "report_type": "weekly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "report_id": "uuid",
    "report_type": "weekly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
    "generated_at": "2024-01-08T10:00:00Z",
    "summary": "本周共有100位老人完成健康监测...",
    "url": "/api/reports/export/uuid.pdf"
  }
}
```

## 5. 公共接口

### 5.1 上传头像

```
POST /api/upload/avatar
```

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求参数**:
- `avatar`: 文件 (JPG, PNG, GIF)

**响应**:
```json
{
  "status": "success",
  "data": {
    "file_url": "https://example.com/avatars/uuid.jpg",
    "file_name": "avatar.jpg",
    "file_size": 102400
  }
}
```

### 5.2 获取系统配置

```
GET /api/config
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "system_name": "智慧健康管理系统",
    "version": "1.0.0",
    "health_thresholds": {
      "heart_rate": { "min": 60, "max": 100 },
      "blood_pressure": {
        "systolic": { "min": 90, "max": 140 },
        "diastolic": { "min": 60, "max": 90 }
      },
      "blood_sugar": { "min": 3.9, "max": 6.1 },
      "temperature": { "min": 36.0, "max": 37.3 }
    }
  }
}
```

## 6. 错误响应规范

所有API接口在发生错误时，返回统一的错误响应格式：

```json
{
  "status": "error",
  "code": "错误代码",
  "message": "错误描述",
  "details": {}
}
```

### 6.1 常见错误代码

| 错误代码 | 描述 | HTTP状态码 |
| :--- | :--- | :--- |
| `INVALID_REQUEST` | 请求参数无效 | 400 |
| `AUTH_FAILED` | 认证失败 | 401 |
| `ACCESS_DENIED` | 权限不足 | 403 |
| `NOT_FOUND` | 资源不存在 | 404 |
| `CONFLICT` | 资源冲突 | 409 |
| `SERVER_ERROR` | 服务器内部错误 | 500 |
| `SERVICE_UNAVAILABLE` | 服务不可用 | 503 |

## 7. API安全规范

1. **认证授权**:
   - 所有API接口必须使用JWT进行身份认证
   - 接口访问权限根据用户角色严格控制

2. **数据传输安全**:
   - 使用HTTPS协议传输数据
   - 敏感数据进行加密传输

3. **请求频率限制**:
   - 对API请求实施频率限制，防止恶意请求
   - 单个IP和用户账号设置独立的限制规则

4. **输入验证**:
   - 所有用户输入必须进行严格验证
   - 使用参数绑定和数据类型检查
   - 防止SQL注入、XSS等常见攻击

5. **日志记录**:
   - 记录所有API访问日志
   - 记录关键操作的审计日志
   - 记录异常和错误日志

## 8. API版本管理

1. **版本标识**:
   - API版本通过URL路径前缀指定，如 `/api/v1/`
   - 当API发生不兼容变更时，升级版本号

2. **兼容性保证**:
   - 旧版本API在新版本发布后至少保留3个月
   - 提供API版本迁移指南