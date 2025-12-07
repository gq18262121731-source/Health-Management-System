# 智慧健康管理系统 - API 接口文档

> 本文档定义了前端组件与后端API的交互规范  
> **版本**: v1.0  
> **基础路径**: `/api/v1/`

---

## 📋 目录

1. [老人端 API](#老人端-api)
2. [子女端 API](#子女端-api)
3. [社区端 API](#社区端-api)
4. [共享 API](#共享-api)
5. [数据模型](#数据模型)

---

## 🧓 老人端 API

### 认证与授权

#### 1. 用户登录
```
POST /api/v1/elderly/auth/login
```
**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```
**响应**:
```json
{
  "success": true,
  "data": {
    "token": "string",
    "userId": "string",
    "name": "string",
    "avatar": "string"
  }
}
```

#### 2. 用户登出
```
POST /api/v1/elderly/auth/logout
```

---

### 今日健康数据

#### 3. 获取今日健康概览
```
GET /api/v1/elderly/health/today
```
**响应**:
```json
{
  "success": true,
  "data": {
    "userId": "string",
    "userName": "string",
    "date": "2024-11-26",
    "greeting": "下午好",
    "vitalSigns": {
      "temperature": {
        "value": 36.5,
        "unit": "°C",
        "status": "normal",
        "change": -0.2,
        "updatedAt": "2024-11-26T14:30:00Z"
      },
      "bloodSugar": {
        "value": 5.2,
        "unit": "mmol/L",
        "status": "normal",
        "type": "fasting",
        "updatedAt": "2024-11-26T08:00:00Z"
      },
      "bloodPressure": {
        "systolic": 118,
        "diastolic": 75,
        "unit": "mmHg",
        "status": "normal",
        "updatedAt": "2024-11-26T09:00:00Z"
      },
      "heartRate": {
        "value": 72,
        "unit": "bpm",
        "status": "normal",
        "change": 2,
        "updatedAt": "2024-11-26T14:30:00Z"
      }
    },
    "activity": {
      "steps": 8542,
      "goal": 10000,
      "percentage": 85.42
    },
    "weight": {
      "value": 68.5,
      "unit": "kg",
      "bmi": 22.4,
      "bmiStatus": "normal"
    }
  }
}
```

#### 4. 获取心率趋势数据
```
GET /api/v1/elderly/health/charts/heartrate
Query Parameters: 
  - period: string (today|week|month)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "period": "today",
    "dataPoints": [
      {
        "time": "00:00",
        "value": 68,
        "status": "normal"
      },
      {
        "time": "04:00",
        "value": 65,
        "status": "normal"
      }
    ],
    "average": 72,
    "max": 85,
    "min": 62
  }
}
```

#### 5. 获取睡眠分析数据
```
GET /api/v1/elderly/health/charts/sleep
Query Parameters:
  - period: string (today|week|month)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "period": "week",
    "dataPoints": [
      {
        "date": "周一",
        "deep": 3.2,
        "light": 4.5,
        "awake": 0.3
      }
    ],
    "average": {
      "total": 7.5,
      "deep": 3.0,
      "light": 4.2,
      "awake": 0.3
    },
    "quality": "良好"
  }
}
```

#### 6. 获取血压趋势数据
```
GET /api/v1/elderly/health/charts/bloodpressure
Query Parameters:
  - period: string (week|month|year)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "period": "week",
    "dataPoints": [
      {
        "date": "周一",
        "systolic": 120,
        "diastolic": 80
      }
    ]
  }
}
```

#### 7. 获取健康雷达图数据
```
GET /api/v1/elderly/health/charts/radar
```
**响应**:
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "心血管",
        "score": 85,
        "fullMark": 100
      },
      {
        "name": "睡眠质量",
        "score": 78,
        "fullMark": 100
      },
      {
        "name": "运动量",
        "score": 82,
        "fullMark": 100
      },
      {
        "name": "营养",
        "score": 90,
        "fullMark": 100
      },
      {
        "name": "心理状态",
        "score": 88,
        "fullMark": 100
      }
    ]
  }
}
```

---

### 历史报告

#### 8. 获取当前健康报告
```
GET /api/v1/elderly/reports/current
```
**响应**:
```json
{
  "success": true,
  "data": {
    "reportId": "string",
    "generatedAt": "2024-11-26T14:30:00Z",
    "metrics": {
      "heartRate": { "value": 72, "unit": "bpm", "status": "normal" },
      "bloodPressure": { "systolic": 118, "diastolic": 75, "unit": "mmHg", "status": "normal" },
      "bloodSugar": { "value": 5.2, "unit": "mmol/L", "status": "normal" },
      "temperature": { "value": 36.5, "unit": "°C", "status": "normal" }
    },
    "summary": "您的健康状况总体良好。各项生理指标均在正常范围内，建议继续保持良好的生活习惯。",
    "recommendations": [
      "保持规律的作息时间，每天睡眠7-8小时",
      "继续保持每天8000步以上的运动量",
      "注意饮食均衡，适量摄入蔬菜水果",
      "定期监测血压血糖，保持健康记录"
    ]
  }
}
```

#### 9. 获取历史报告列表
```
GET /api/v1/elderly/reports/history
Query Parameters:
  - page: number (default: 1)
  - pageSize: number (default: 10)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "total": 50,
    "page": 1,
    "pageSize": 10,
    "reports": [
      {
        "reportId": "string",
        "title": "2024年10月健康月报",
        "date": "2024-11-01",
        "summary": "本月健康状况总体良好。平均心率保持稳定，睡眠质量较上月提升15%。",
        "type": "monthly"
      }
    ]
  }
}
```

#### 10. 生成完整报告
```
POST /api/v1/elderly/reports/generate
```
**请求体**:
```json
{
  "reportType": "daily|weekly|monthly",
  "startDate": "2024-11-01",
  "endDate": "2024-11-30"
}
```

#### 11. 下载报告PDF
```
GET /api/v1/elderly/reports/{reportId}/download
```
**响应**: PDF文件流

---

### 心情与心理健康

#### 12. 提交心情记录
```
POST /api/v1/elderly/psychology/mood
```
**请求体**:
```json
{
  "mood": "happy|calm|tired|anxious",
  "note": "string (optional)",
  "timestamp": "2024-11-26T14:30:00Z"
}
```

#### 13. 获取心情历史数据
```
GET /api/v1/elderly/psychology/mood/history
Query Parameters:
  - period: string (week|month|year)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "dataPoints": [
      {
        "date": "2024-11-20",
        "mood": "happy",
        "score": 85
      }
    ]
  }
}
```

#### 14. 获取压力指数数据
```
GET /api/v1/elderly/psychology/stress
Query Parameters:
  - period: string (week|month)
```

#### 15. 获取睡眠质量与心理关系数据
```
GET /api/v1/elderly/psychology/sleep-mood
```

---

### AI 健康助手

#### 16. AI对话
```
POST /api/v1/elderly/ai/chat
```
**请求体**:
```json
{
  "message": "string",
  "context": {
    "dataType": "血糖|血压|心率",
    "currentValue": "string"
  }
}
```
**响应**:
```json
{
  "success": true,
  "data": {
    "message": "string",
    "suggestions": ["string"],
    "needsAttention": boolean
  }
}
```

#### 17. AI数据分析
```
POST /api/v1/elderly/ai/analyze
```
**请求体**:
```json
{
  "dataType": "血糖|血压|心率|综合",
  "timeRange": "today|week|month",
  "customPrompt": "string (optional)"
}
```
**响应**:
```json
{
  "success": true,
  "data": {
    "analysis": "string",
    "trends": ["string"],
    "recommendations": ["string"],
    "alerts": ["string"]
  }
}
```

---

## 👨‍👩‍👧 子女端 API

### 认证

#### 18. 子女端登录
```
POST /api/v1/children/auth/login
```

---

### 老人管理

#### 19. 获取绑定老人列表
```
GET /api/v1/children/elders/list
```
**响应**:
```json
{
  "success": true,
  "data": {
    "elders": [
      {
        "elderId": "string",
        "name": "张三",
        "avatar": "string",
        "age": 68,
        "relationship": "父亲",
        "healthStatus": "good|warning|danger",
        "lastUpdate": "2024-11-26T14:30:00Z",
        "location": "北京市朝阳区",
        "recentAlerts": 0,
        "vitalSigns": {
          "heartRate": 72,
          "bloodPressure": "118/75",
          "temperature": 36.5
        }
      }
    ]
  }
}
```

#### 20. 获取单个老人详细信息
```
GET /api/v1/children/elders/{elderId}/detail
```
**响应**:
```json
{
  "success": true,
  "data": {
    "elderId": "string",
    "personalInfo": {
      "name": "string",
      "age": 68,
      "gender": "male|female",
      "avatar": "string",
      "relationship": "string"
    },
    "healthData": {
      "vitalSigns": { /* same as elderly/health/today */ },
      "recentTrends": { /* chart data */ }
    },
    "alerts": [
      {
        "alertId": "string",
        "type": "blood_pressure|heart_rate|medication",
        "severity": "high|medium|low",
        "message": "string",
        "timestamp": "2024-11-26T14:30:00Z",
        "isRead": false
      }
    ],
    "medications": [
      {
        "name": "string",
        "dosage": "string",
        "frequency": "string",
        "nextDose": "2024-11-26T18:00:00Z"
      }
    ]
  }
}
```

---

### 远程监控

#### 21. 获取实时监控数据
```
GET /api/v1/children/monitor/{elderId}/realtime
```
**响应**: 实时生命体征数据（类似今日健康数据）

#### 22. 获取监控历史数据
```
GET /api/v1/children/monitor/{elderId}/history
Query Parameters:
  - metric: string (heartrate|bloodpressure|temperature)
  - period: string (day|week|month)
```

---

### 智能提醒

#### 23. 获取提醒列表
```
GET /api/v1/children/reminders/list
```
**响应**:
```json
{
  "success": true,
  "data": {
    "reminders": [
      {
        "reminderId": "string",
        "elderId": "string",
        "elderName": "张三",
        "type": "medication|checkup|exercise",
        "title": "服药提醒",
        "description": "降压药",
        "scheduledTime": "2024-11-26T18:00:00Z",
        "status": "pending|completed|missed",
        "priority": "high|medium|low"
      }
    ]
  }
}
```

#### 24. 创建提醒
```
POST /api/v1/children/reminders/create
```
**请求体**:
```json
{
  "elderId": "string",
  "type": "medication|checkup|exercise",
  "title": "string",
  "description": "string",
  "scheduledTime": "2024-11-26T18:00:00Z",
  "repeat": "once|daily|weekly",
  "priority": "high|medium|low"
}
```

#### 25. 更新提醒状态
```
PUT /api/v1/children/reminders/{reminderId}/status
```
**请求体**:
```json
{
  "status": "completed|cancelled"
}
```

---

### AI 助手（子女端）

#### 26. 获取AI健康建议
```
POST /api/v1/children/ai/advice
```
**请求体**:
```json
{
  "elderId": "string",
  "concern": "string"
}
```

---

## 🏥 社区端 API

### 认证

#### 27. 社区端登录
```
POST /api/v1/community/auth/login
```

---

### 大屏数据展示

#### 28. 获取社区概览统计
```
GET /api/v1/community/dashboard/overview
```
**响应**:
```json
{
  "success": true,
  "data": {
    "totalElders": 1234,
    "activeToday": 1156,
    "alertsToday": 23,
    "servicesProvided": 456,
    "healthScore": 87.5,
    "timestamp": "2024-11-26T14:30:00Z"
  }
}
```

#### 29. 获取年龄分布数据
```
GET /api/v1/community/dashboard/age-distribution
```
**响应**:
```json
{
  "success": true,
  "data": {
    "ageGroups": [
      { "range": "60-65", "count": 245, "percentage": 19.9 },
      { "range": "66-70", "count": 312, "percentage": 25.3 },
      { "range": "71-75", "count": 298, "percentage": 24.2 },
      { "range": "76-80", "count": 234, "percentage": 19.0 },
      { "range": "80+", "count": 145, "percentage": 11.8 }
    ]
  }
}
```

#### 30. 获取健康监测趋势
```
GET /api/v1/community/dashboard/health-trends
Query Parameters:
  - period: string (week|month|year)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "metrics": [
      {
        "date": "11-01",
        "heartRate": 72.5,
        "bloodPressure": 125.3,
        "bloodSugar": 5.4,
        "activity": 7850
      }
    ]
  }
}
```

#### 31. 获取设备状态
```
GET /api/v1/community/dashboard/devices
```
**响应**:
```json
{
  "success": true,
  "data": {
    "total": 1234,
    "online": 1156,
    "offline": 78,
    "devices": [
      {
        "deviceId": "string",
        "type": "blood_pressure|heart_rate|glucose",
        "status": "online|offline",
        "lastSync": "2024-11-26T14:30:00Z",
        "batteryLevel": 85
      }
    ]
  }
}
```

#### 32. 获取服务统计
```
GET /api/v1/community/dashboard/services
```
**响应**:
```json
{
  "success": true,
  "data": {
    "services": [
      { "name": "健康咨询", "count": 145 },
      { "name": "体检服务", "count": 89 },
      { "name": "康复训练", "count": 67 },
      { "name": "心理疏导", "count": 45 },
      { "name": "营养指导", "count": 110 }
    ]
  }
}
```

---

### 2D 数字孪生地图

#### 33. 获取地图配置
```
GET /api/v1/community/map/config
```
**响应**:
```json
{
  "success": true,
  "data": {
    "mapImage": "string (URL)",
    "bounds": {
      "north": 40.00,
      "south": 39.90,
      "east": 116.50,
      "west": 116.40
    },
    "buildings": [
      {
        "id": "building-1",
        "name": "A栋养老公寓",
        "coordinates": [116.45, 39.95],
        "type": "residential",
        "floors": 6,
        "residents": 120
      }
    ]
  }
}
```

#### 34. 获取实时老人位置
```
GET /api/v1/community/map/elders/locations
```
**响应**:
```json
{
  "success": true,
  "data": {
    "elders": [
      {
        "elderId": "string",
        "name": "张三",
        "coordinates": [116.45, 39.95],
        "building": "A栋",
        "floor": 3,
        "room": "301",
        "status": "normal|warning|emergency",
        "lastUpdate": "2024-11-26T14:30:00Z"
      }
    ]
  }
}
```

#### 35. 获取地图告警信息
```
GET /api/v1/community/map/alerts
```
**响应**:
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alertId": "string",
        "elderId": "string",
        "elderName": "张三",
        "type": "fall|sos|health",
        "severity": "high|medium|low",
        "coordinates": [116.45, 39.95],
        "building": "A栋",
        "timestamp": "2024-11-26T14:30:00Z",
        "isResolved": false
      }
    ]
  }
}
```

---

### 告警管理

#### 36. 获取告警列表
```
GET /api/v1/community/alerts/list
Query Parameters:
  - status: string (all|active|resolved)
  - severity: string (all|high|medium|low)
  - page: number
  - pageSize: number
```
**响应**:
```json
{
  "success": true,
  "data": {
    "total": 150,
    "alerts": [
      {
        "alertId": "string",
        "elderId": "string",
        "elderName": "张三",
        "type": "fall|sos|health|medication",
        "severity": "high|medium|low",
        "message": "string",
        "location": "A栋301室",
        "timestamp": "2024-11-26T14:30:00Z",
        "status": "active|acknowledged|resolved",
        "assignedTo": "string (工作人员ID)",
        "resolvedAt": "2024-11-26T15:00:00Z"
      }
    ]
  }
}
```

#### 37. 处理告警
```
PUT /api/v1/community/alerts/{alertId}/handle
```
**请求体**:
```json
{
  "action": "acknowledge|resolve|escalate",
  "assignTo": "string (optional)",
  "note": "string (optional)"
}
```

---

### 群体健康分析

#### 38. 获取群体健康分析数据
```
GET /api/v1/community/analysis/group-health
Query Parameters:
  - ageGroup: string (60-65|66-70|71-75|76-80|80+)
  - metric: string (all|heartrate|bloodpressure|bloodsugar)
  - period: string (week|month|year)
```
**响应**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "totalElders": 1234,
      "healthyCount": 1050,
      "warningCount": 150,
      "criticalCount": 34,
      "averageAge": 72.5
    },
    "metrics": {
      "heartRate": {
        "average": 72.5,
        "normal": 85.2,
        "abnormal": 14.8
      },
      "bloodPressure": {
        "average": "125/78",
        "normal": 78.5,
        "abnormal": 21.5
      }
    },
    "trends": [
      {
        "date": "2024-11-20",
        "healthyPercentage": 85.2,
        "warningPercentage": 12.5,
        "criticalPercentage": 2.3
      }
    ]
  }
}
```

---

## 🔄 共享 API

### 用户个人信息

#### 39. 获取个人信息
```
GET /api/v1/{role}/profile
```
**响应**:
```json
{
  "success": true,
  "data": {
    "userId": "string",
    "name": "string",
    "avatar": "string",
    "phone": "string",
    "email": "string",
    "emergencyContacts": [
      {
        "name": "string",
        "relationship": "string",
        "phone": "string"
      }
    ]
  }
}
```

#### 40. 更新个人信息
```
PUT /api/v1/{role}/profile
```

---

### 通知系统

#### 41. 获取通知列表
```
GET /api/v1/{role}/notifications
Query Parameters:
  - isRead: boolean (optional)
  - page: number
  - pageSize: number
```

#### 42. 标记通知已读
```
PUT /api/v1/{role}/notifications/{notificationId}/read
```

---

## 📊 数据模型

### VitalSigns (生命体征)
```typescript
interface VitalSigns {
  temperature?: {
    value: number;
    unit: '°C';
    status: 'normal' | 'warning' | 'danger';
    change?: number;
    updatedAt: string;
  };
  bloodSugar?: {
    value: number;
    unit: 'mmol/L';
    status: 'normal' | 'warning' | 'danger';
    type: 'fasting' | 'postprandial';
    updatedAt: string;
  };
  bloodPressure?: {
    systolic: number;
    diastolic: number;
    unit: 'mmHg';
    status: 'normal' | 'warning' | 'danger';
    updatedAt: string;
  };
  heartRate?: {
    value: number;
    unit: 'bpm';
    status: 'normal' | 'warning' | 'danger';
    change?: number;
    updatedAt: string;
  };
}
```

### HealthStatus (健康状态)
```typescript
type HealthStatus = 'good' | 'warning' | 'danger';
```

### AlertType (告警类型)
```typescript
type AlertType = 'fall' | 'sos' | 'health' | 'medication' | 'blood_pressure' | 'heart_rate';
```

### Severity (严重程度)
```typescript
type Severity = 'high' | 'medium' | 'low';
```

---

## 🔐 认证机制

所有API请求（除登录接口外）都需要在请求头中携带认证token：

```
Authorization: Bearer {token}
```

---

## 📝 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息"
  }
}
```

### 常见错误码

- `AUTH_REQUIRED`: 需要认证
- `AUTH_INVALID`: 认证信息无效
- `NOT_FOUND`: 资源不存在
- `VALIDATION_ERROR`: 参数验证失败
- `SERVER_ERROR`: 服务器内部错误

---

## 🔄 实时通信

对于需要实时更新的数据（如地图位置、告警），建议使用WebSocket：

```
ws://api-server/api/v1/{role}/realtime
```

**消息格式**:
```json
{
  "type": "alert|location|health_update",
  "data": { /* 具体数据 */ }
}
```

---

## 📌 注意事项

1. **时间格式**: 所有时间戳使用 ISO 8601 格式 (YYYY-MM-DDTHH:mm:ssZ)
2. **分页**: 默认 page=1, pageSize=10
3. **权限**: 不同角色只能访问对应的API端点
4. **数据隐私**: 子女端只能查看已绑定老人的数据
5. **缓存策略**: 建议对不频繁变化的数据进行缓存（如个人信息）

---

**文档最后更新**: 2024-11-26  
**维护者**: 前端开发团队
