# 养生之道 - 智慧养老服务平台 API 文档

## 1. 项目概述

养生之道是一个专注于老年人健康管理的智慧养老服务平台，提供健康数据记录、分析、智能提醒、社区管理等功能。本API文档详细描述了平台后端提供的所有接口，帮助开发者理解和使用这些接口进行前端开发或第三方集成。

## 2. 认证方式

### 2.1 JWT认证

平台使用JWT (JSON Web Token) 进行身份认证。所有需要认证的接口都需要在请求头中包含有效的JWT令牌。

#### 请求头格式
```
Authorization: Bearer <access_token>
```

#### 获取令牌
通过登录接口获取访问令牌：
- POST `/api/v1/auth/login` ✅ **注意：实际路径为 `/api/v1/auth/login`，不是 `/api/user/login`**

#### 刷新令牌
当令牌即将过期时，可以使用刷新接口获取新令牌：
- POST `/api/user/refresh` ⚠️ **注意：此接口可能存在，请验证实际路由**

## 3. API 端点说明

### 3.1 用户管理接口

#### 3.1.1 用户注册
- **路径**: `/api/v1/auth/register` ✅ **实际路径为 `/api/v1/auth/register`**
- **方法**: `POST`
- **描述**: 创建新用户账号
- **请求体**: 
```json
{
  "username": "string",  // 用户名，必填
  "password": "string",  // 密码，必填，至少8位，包含大小写字母、数字和特殊字符
  "phone": "string",     // 手机号，必填，11位
  "name": "string",      // 姓名，必填
  "role": "string"       // 角色，必填，可选值：admin, community_admin, children
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "string",
    "phone": "string",
    "name": "string",
    "role": "string",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "注册成功"
}
```

#### 3.1.2 用户登录
- **路径**: `/api/v1/auth/login` ✅ **实际路径为 `/api/v1/auth/login`**
- **方法**: `POST`
- **描述**: 用户登录获取访问令牌
- **请求体**: 
```json
{
  "username": "string",  // 用户名，必填
  "password": "string"   // 密码，必填
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_info": {
      "id": 1,
      "username": "string",
      "name": "string",
      "role": "string"
    }
  },
  "message": "登录成功"
}
```

#### 3.1.3 获取当前用户信息
- **路径**: `/api/v1/auth/me` ✅ **实际路径为 `/api/v1/auth/me`**
- **方法**: `GET`
- **描述**: 获取当前登录用户的详细信息
- **认证**: 需要JWT令牌
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "string",
    "phone": "string",
    "name": "string",
    "role": "string",
    "avatar": "string",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "获取成功"
}
```

#### 3.1.4 更新用户信息
- **路径**: `/api/user/profile`
- **方法**: `PUT`
- **描述**: 更新当前用户的个人信息
- **认证**: 需要JWT令牌
- **请求体**: 
```json
{
  "phone": "string",   // 手机号
  "name": "string",    // 姓名
  "avatar": "string"   // 头像URL
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "string",
    "phone": "string",
    "name": "string",
    "avatar": "string"
  },
  "message": "更新成功"
}
```

#### 3.1.5 修改密码
- **路径**: `/api/user/change-password`
- **方法**: `POST`
- **描述**: 修改用户密码
- **认证**: 需要JWT令牌
- **请求体**: 
```json
{
  "current_password": "string",  // 当前密码，必填
  "new_password": "string"       // 新密码，必填，至少8位，包含大小写字母、数字和特殊字符
}
```
- **响应**: 
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

### 3.2 老人信息管理接口

#### 3.2.1 创建老人信息
- **路径**: `/api/v1/elderly`
- **方法**: `POST`
- **描述**: 创建新的老人信息记录
- **认证**: 需要JWT令牌，角色为community_admin或admin
- **请求体**: 
```json
{
  "name": "string",               // 姓名，必填
  "gender": "string",             // 性别，必填，male或female
  "birth_date": "string",         // 出生日期，必填，格式：YYYY-MM-DD
  "id_card": "string",            // 身份证号，必填
  "phone": "string",              // 手机号，必填
  "address": "string",            // 地址，必填
  "health_status": "string",      // 健康状况，必填
  "emergency_contact": "string",  // 紧急联系人，必填
  "emergency_phone": "string"     // 紧急联系电话，必填
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "string",
    "gender": "string",
    "birth_date": "string",
    "id_card": "string",
    "phone": "string",
    "address": "string",
    "health_status": "string",
    "emergency_contact": "string",
    "emergency_phone": "string",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "创建成功"
}
```

#### 3.2.2 获取老人列表
- **路径**: `/api/v1/elderly`
- **方法**: `GET`
- **描述**: 获取老人信息列表，支持分页
- **认证**: 需要JWT令牌
- **查询参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认10
  - `name`: 姓名搜索关键词（可选）
- **响应**: 
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "string",
        "gender": "string",
        "birth_date": "string",
        "phone": "string",
        "health_status": "string"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "pages": 10
  },
  "message": "获取成功"
}
```

#### 3.2.3 获取老人详情
- **路径**: `/api/v1/elderly/{id}`
- **方法**: `GET`
- **描述**: 获取指定老人的详细信息
- **认证**: 需要JWT令牌
- **路径参数**:
  - `id`: 老人ID
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "string",
    "gender": "string",
    "birth_date": "string",
    "id_card": "string",
    "phone": "string",
    "address": "string",
    "health_status": "string",
    "emergency_contact": "string",
    "emergency_phone": "string",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "获取成功"
}
```

#### 3.2.4 更新老人信息
- **路径**: `/api/v1/elderly/{id}`
- **方法**: `PUT`
- **描述**: 更新指定老人的信息
- **认证**: 需要JWT令牌，角色为community_admin或admin
- **路径参数**:
  - `id`: 老人ID
- **请求体**: 
```json
{
  "name": "string",
  "gender": "string",
  "birth_date": "string",
  "phone": "string",
  "address": "string",
  "health_status": "string",
  "emergency_contact": "string",
  "emergency_phone": "string"
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "string",
    "gender": "string",
    "birth_date": "string",
    "id_card": "string",
    "phone": "string",
    "address": "string",
    "health_status": "string",
    "emergency_contact": "string",
    "emergency_phone": "string"
  },
  "message": "更新成功"
}
```

### 3.3 健康数据管理接口

#### 3.3.1 添加健康记录
- **路径**: `/api/v1/health/records`
- **方法**: `POST`
- **描述**: 添加新的健康数据记录
- **认证**: 需要JWT令牌
- **请求体**: 
```json
{
  "elderly_id": 1,                // 老人ID，必填
  "blood_pressure_systolic": 120, // 收缩压
  "blood_pressure_diastolic": 80, // 舒张压
  "heart_rate": 72,               // 心率
  "blood_sugar": 5.6,             // 血糖
  "body_temperature": 36.5,       // 体温
  "oxygen": 98,                   // 血氧
  "weight": 65.5,                 // 体重
  "steps": 5000,                  // 步数
  "record_date": "2024-01-01"    // 记录日期，必填
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "elderly_id": 1,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "heart_rate": 72,
    "blood_sugar": 5.6,
    "body_temperature": 36.5,
    "oxygen": 98,
    "weight": 65.5,
    "steps": 5000,
    "record_date": "2024-01-01",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "记录添加成功"
}
```

#### 3.3.2 获取健康记录列表
- **路径**: `/api/v1/health/records/{elderly_id}`
- **方法**: `GET`
- **描述**: 获取指定老人的健康记录列表
- **认证**: 需要JWT令牌
- **路径参数**:
  - `elderly_id`: 老人ID
- **查询参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认10
  - `start_date`: 开始日期（可选）
  - `end_date`: 结束日期（可选）
- **响应**: 
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "record_date": "2024-01-01",
        "blood_pressure": "120/80",
        "heart_rate": 72,
        "blood_sugar": 5.6,
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 10
  },
  "message": "获取成功"
}
```

#### 3.3.3 获取最新健康记录
- **路径**: `/api/v1/health/latest/{elderly_id}`
- **方法**: `GET`
- **描述**: 获取指定老人的最新健康记录
- **认证**: 需要JWT令牌
- **路径参数**:
  - `elderly_id`: 老人ID
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "elderly_id": 1,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "heart_rate": 72,
    "blood_sugar": 5.6,
    "body_temperature": 36.5,
    "oxygen": 98,
    "weight": 65.5,
    "steps": 5000,
    "record_date": "2024-01-01",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "获取成功"
}
```

#### 3.3.4 获取每日健康摘要
- **路径**: `/api/v1/health/daily-summary/{elderly_id}/{date}`
- **方法**: `GET`
- **描述**: 获取指定老人某一天的健康数据摘要
- **认证**: 需要JWT令牌
- **路径参数**:
  - `elderly_id`: 老人ID
  - `date`: 日期，格式：YYYY-MM-DD
- **响应**: 
```json
{
  "success": true,
  "data": {
    "elderly_id": 1,
    "elderly_name": "张三",
    "date": "2024-01-01",
    "health_metrics": {
      "blood_pressure": {"avg": "120/80", "count": 2},
      "heart_rate": {"avg": 72, "min": 68, "max": 76, "count": 3},
      "blood_sugar": {"avg": 5.6, "min": 5.2, "max": 6.0, "count": 2},
      "steps": {"total": 5000}
    },
    "health_evaluation": "良好",
    "abnormal_count": 0
  },
  "message": "获取成功"
}
```

#### 3.3.5 获取健康预警
- **路径**: `/api/v1/health/alerts/{elderly_id}`
- **方法**: `GET`
- **描述**: 获取指定老人的健康预警信息
- **认证**: 需要JWT令牌
- **路径参数**:
  - `elderly_id`: 老人ID
- **查询参数**:
  - `status`: 预警状态（pending/completed，可选）
- **响应**: 
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "elderly_id": 1,
      "elderly_name": "张三",
      "alert_type": "high_blood_pressure",
      "alert_message": "血压偏高，请及时关注",
      "severity": "warning",
      "related_record_id": 1,
      "status": "pending",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "message": "获取成功"
}
```

### 3.4 提醒管理接口

#### 3.4.1 创建提醒
- **路径**: `/api/v1/reminder`
- **方法**: `POST`
- **描述**: 创建新的提醒任务
- **认证**: 需要JWT令牌
- **请求体**: 
```json
{
  "elderly_id": 1,           // 老人ID，必填
  "title": "string",        // 标题，必填
  "content": "string",      // 内容，必填
  "reminder_type": "string", // 类型，必填：medication/exercise/other
  "remind_time": "08:00",   // 提醒时间，必填
  "start_date": "2024-01-01", // 开始日期，必填
  "end_date": "2024-12-31",  // 结束日期（可选，不填则长期有效）
  "frequency": "string",    // 频率，必填：once/daily/weekly/monthly/custom
  "custom_days": [1,3,5],    // 自定义频率的日期（当frequency为custom时必填）
  "status": "pending"       // 状态，必填
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "elderly_id": 1,
    "title": "string",
    "content": "string",
    "reminder_type": "string",
    "remind_time": "08:00",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "frequency": "string",
    "custom_days": [1,3,5],
    "status": "pending",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "创建成功"
}
```

#### 3.4.2 获取今日提醒
- **路径**: `/api/v1/reminder/today`
- **方法**: `GET`
- **描述**: 获取今日需要执行的提醒
- **认证**: 需要JWT令牌
- **响应**: 
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "elderly_id": 1,
      "elderly_name": "张三",
      "title": "吃药提醒",
      "content": "请按时服用降压药",
      "reminder_type": "medication",
      "remind_time": "08:00",
      "status": "pending",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "message": "获取成功"
}
```

#### 3.4.3 更新提醒状态
- **路径**: `/api/v1/reminder/{id}/status`
- **方法**: `PATCH`
- **描述**: 更新提醒的状态
- **认证**: 需要JWT令牌
- **路径参数**:
  - `id`: 提醒ID
- **请求体**: 
```json
{
  "status": "completed"  // 新状态，必填：pending/completed/cancelled
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "completed",
    "updated_at": "2024-01-01T10:00:00"
  },
  "message": "状态更新成功"
}
```

### 3.5 社区管理接口

#### 3.5.1 创建社区
- **路径**: `/api/v1/communities`
- **方法**: `POST`
- **描述**: 创建新的社区信息
- **认证**: 需要JWT令牌，角色为admin
- **请求体**: 
```json
{
  "name": "string",        // 社区名称，必填
  "address": "string",     // 社区地址，必填
  "description": "string"  // 社区描述
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "string",
    "address": "string",
    "description": "string",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "创建成功"
}
```

#### 3.5.2 获取社区列表
- **路径**: `/api/v1/communities`
- **方法**: `GET`
- **描述**: 获取社区列表
- **认证**: 需要JWT令牌
- **响应**: 
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "string",
      "address": "string",
      "elderly_count": 50,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "message": "获取成功"
}
```

### 3.6 子女相关接口

#### 3.6.1 创建子女信息
- **路径**: `/api/v1/children`
- **方法**: `POST`
- **描述**: 创建子女用户的详细信息
- **认证**: 需要JWT令牌，角色为children
- **请求体**: 
```json
{
  "relationship": "string"  // 与老人的关系，必填
}
```
- **响应**: 
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "relationship": "string",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "创建成功"
}
```

#### 3.6.2 获取关联老人列表
- **路径**: `/api/v1/children/elderly`
- **方法**: `GET`
- **描述**: 获取当前子女用户关联的老人列表
- **认证**: 需要JWT令牌，角色为children
- **响应**: 
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "张三",
      "gender": "male",
      "birth_date": "1945-01-15",
      "phone": "13800138002",
      "health_status": "良好",
      "last_check_time": "2024-01-01T10:00:00"
    }
  ],
  "message": "获取成功"
}
```

## 4. 错误码说明

| 错误码 | 描述 | HTTP状态码 |
|-------|------|----------|
| 40001 | 请求参数错误 | 400 |
| 40101 | 认证失败 | 401 |
| 40102 | 令牌过期 | 401 |
| 40301 | 权限不足 | 403 |
| 40401 | 资源不存在 | 404 |
| 50001 | 服务器内部错误 | 500 |
| 50002 | 数据库操作失败 | 500 |

## 5. 数据验证规则

### 5.1 健康数据验证标准

| 指标 | 正常范围 | 警告范围 | 异常范围 |
|-----|---------|---------|--------|
| 收缩压 | 90-130 mmHg | 131-140 mmHg | <90 或 >140 mmHg |
| 舒张压 | 60-85 mmHg | 86-90 mmHg | <60 或 >90 mmHg |
| 心率 | 60-100 次/分 | 50-59 或 101-110 次/分 | <50 或 >110 次/分 |
| 血糖 | 3.9-6.1 mmol/L | 6.2-7.0 或 3.3-3.8 mmol/L | <3.3 或 >7.0 mmol/L |
| 体温 | 36.0-37.2°C | 37.3-38.0 或 35.0-35.9°C | <35.0 或 >38.0°C |
| 血氧 | 95-100% | 90-94% | <90% |

## 6. 使用示例

### 6.1 Python示例代码

```python
import requests
import json

# 登录获取令牌
def login():
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "username": "admin_test",
        "password": "Admin@123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    return None

# 获取老人列表
def get_elderly_list(token):
    url = "http://localhost:8000/api/v1/elderly"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# 主函数
if __name__ == "__main__":
    # 登录
    token = login()
    if token:
        print("登录成功")
        # 获取老人列表
        elderly_list = get_elderly_list(token)
        print("老人列表:", json.dumps(elderly_list, ensure_ascii=False, indent=2))
    else:
        print("登录失败")
```

## 7. 部署说明

### 7.1 环境要求
- Python 3.8+
- FastAPI
- SQLAlchemy
- MySQL 8.0+ 或 SQLite
- Redis（用于缓存和会话管理）

### 7.2 配置文件

主要配置项：
- 数据库连接信息
- JWT密钥和过期时间
- 文件上传路径
- CORS配置

## 8. 注意事项

1. 所有API接口返回统一的JSON格式，包含success、data、message三个字段
2. 敏感数据（如身份证号）在传输和存储时进行加密处理
3. 定期清理过期的认证令牌和日志数据
4. 生产环境建议开启HTTPS加密传输
5. 定期备份数据库，确保数据安全

## 9. 版本更新记录

### v1.0.0（初始版本）
- 实现用户管理功能
- 实现老人信息管理
- 实现健康数据记录和分析
- 实现智能提醒功能
- 实现社区管理功能

### v1.1.0（计划中）
- 添加智能健康评估算法
- 增加异常行为检测
- 支持更多健康设备接入
- 实现数据可视化报表功能