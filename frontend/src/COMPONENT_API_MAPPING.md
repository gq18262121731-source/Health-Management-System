# 组件 API 映射文档

> 本文档列出所有前端组件及其对应的API端点  
> 便于前后端开发协作和接口对接

---

## 📋 老人端组件

### 1. 登录页 (`/components/login/ElderlyLoginPage.tsx`)

#### 涉及的API:
- `POST /api/v1/elderly/auth/login` - 用户登录
- `POST /api/v1/elderly/auth/logout` - 用户登出

#### 数据交互点:
```typescript
const handleLogin = () => {
  // TODO: Call POST /api/v1/elderly/auth/login
  // Request: { username: string, password: string }
  // Response: { success: boolean, data: { token, userId, name, avatar } }
  
  if (rememberMe) {
    // 保存到localStorage
    localStorage.setItem('elderly_username', username);
    localStorage.setItem('elderly_password', password);
  }
};
```

---

### 2. 今日健康页 (`/App.tsx` - analysis tab)

#### 涉及的API:
- `GET /api/v1/elderly/health/today` - 今日健康概览
- `GET /api/v1/elderly/health/charts/heartrate?period=today` - 心率趋势
- `GET /api/v1/elderly/health/charts/sleep?period=week` - 睡眠分析
- `GET /api/v1/elderly/health/charts/bloodpressure?period=week` - 血压趋势
- `GET /api/v1/elderly/health/charts/radar` - 健康雷达图

#### 数据交互点:
```typescript
// 组件加载时获取今日健康数据
useEffect(() => {
  // TODO: Call GET /api/v1/elderly/health/today
  // Response: { 
  //   userId, userName, date, greeting,
  //   vitalSigns: { temperature, bloodSugar, bloodPressure, heartRate },
  //   activity: { steps, goal, percentage },
  //   weight: { value, unit, bmi, bmiStatus }
  // }
}, []);
```

#### 关键组件:
- **HealthCardWithAI** (`/components/elderly/HealthCardWithAI.tsx`)
  - 显示生命体征数据（血糖、血压、心率）
  - 带AI分析按钮
  - 数据来源: `GET /api/v1/elderly/health/today`

- **HeartRateChart** (`/components/dashboard/HealthCharts.tsx`)
  - 24小时心率趋势图
  - 数据来源: `GET /api/v1/elderly/health/charts/heartrate?period=today`

- **SleepAnalysisChart** (`/components/dashboard/HealthCharts.tsx`)
  - 7天睡眠质量分析
  - 数据来源: `GET /api/v1/elderly/health/charts/sleep?period=week`

- **BloodPressureChart** (`/components/dashboard/HealthCharts.tsx`)
  - 7天血压趋势
  - 数据来源: `GET /api/v1/elderly/health/charts/bloodpressure?period=week`

- **HealthRadarChart** (`/components/dashboard/HealthCharts.tsx`)
  - 综合健康雷达图
  - 数据来源: `GET /api/v1/elderly/health/charts/radar`

---

### 3. 历史报告页 (`/App.tsx` - reports tab)

#### 涉及的API:
- `GET /api/v1/elderly/reports/current` - 当前健康报告
- `GET /api/v1/elderly/reports/history?page=1&pageSize=10` - 历史报告列表
- `POST /api/v1/elderly/reports/generate` - 生成完整报告
- `GET /api/v1/elderly/reports/{reportId}/download` - 下载PDF

#### 数据交互点:
```typescript
// 获取当前报告
useEffect(() => {
  if (!showHistoricalReports) {
    // TODO: Call GET /api/v1/elderly/reports/current
    // Response: { reportId, generatedAt, metrics, summary, recommendations }
  }
}, [showHistoricalReports]);

// 获取历史报告列表
useEffect(() => {
  if (showHistoricalReports) {
    // TODO: Call GET /api/v1/elderly/reports/history?page=1&pageSize=10
    // Response: { total, page, pageSize, reports: [...] }
  }
}, [showHistoricalReports]);

// 生成报告
const handleGenerateReport = () => {
  // TODO: Call POST /api/v1/elderly/reports/generate
  // Request: { reportType: 'daily|weekly|monthly', startDate, endDate }
};

// 下载PDF
const handleDownloadPDF = () => {
  // TODO: Call GET /api/v1/elderly/reports/{reportId}/download
  // Response: PDF file stream
};
```

---

### 4. AI健康助手 (`/components/elderly/FloatingAIAssistant.tsx`)

#### 涉及的API:
- `POST /api/v1/elderly/ai/chat` - AI对话
- `POST /api/v1/elderly/ai/analyze` - AI数据分析

#### 数据交互点:
```typescript
// 发送消息
const handleSendMessage = async (message: string) => {
  // TODO: Call POST /api/v1/elderly/ai/chat
  // Request: { 
  //   message: string, 
  //   context: { dataType, currentValue } 
  // }
  // Response: { message, suggestions, needsAttention }
};

// AI分析（从HealthCardWithAI触发）
const handleAIAnalyze = async (dataType: string) => {
  // TODO: Call POST /api/v1/elderly/ai/analyze
  // Request: { dataType: '血糖|血压|心率', timeRange: 'today|week|month' }
  // Response: { analysis, trends, recommendations, alerts }
};
```

---

### 5. 心理健康页 (`/components/psychology/PsychologyPage.tsx`)

#### 涉及的API:
- `POST /api/v1/elderly/psychology/mood` - 提交心情记录
- `GET /api/v1/elderly/psychology/mood/history?period=week` - 心情历史
- `GET /api/v1/elderly/psychology/stress?period=week` - 压力指数
- `GET /api/v1/elderly/psychology/sleep-mood` - 睡眠与心情关系

#### 数据交互点:
```typescript
// 提交心情
const handleMoodSubmit = (mood: string) => {
  // TODO: Call POST /api/v1/elderly/psychology/mood
  // Request: { mood: 'happy|calm|tired|anxious', note, timestamp }
};

// 获取心情趋势
useEffect(() => {
  // TODO: Call GET /api/v1/elderly/psychology/mood/history?period=week
  // Response: { dataPoints: [{ date, mood, score }] }
}, []);
```

---

### 6. 心情快速卡片 (`/components/dashboard/MoodQuickCard.tsx`)

#### 涉及的API:
- `POST /api/v1/elderly/psychology/mood` - 快速记录心情

#### 数据交互点:
```typescript
const handleQuickMood = (mood: string) => {
  // TODO: Call POST /api/v1/elderly/psychology/mood
  // Request: { mood, note: '', timestamp: new Date().toISOString() }
};
```

---

## 👨‍👩‍👧 子女端组件

### 7. 子女端仪表板 (`/components/children/ChildrenDashboard.tsx`)

#### 涉及的API:
- `GET /api/v1/children/elders/list` - 绑定老人列表

#### 数据交互点:
```typescript
useEffect(() => {
  // TODO: Call GET /api/v1/children/elders/list
  // Response: { 
  //   elders: [{ 
  //     elderId, name, avatar, age, relationship, 
  //     healthStatus, lastUpdate, location, recentAlerts,
  //     vitalSigns: { heartRate, bloodPressure, temperature }
  //   }] 
  // }
}, []);
```

---

### 8. 老人列表 (`/components/children/ElderlyList.tsx`)

#### 涉及的API:
- `GET /api/v1/children/elders/list` - 老人列表

#### 关键功能:
- 显示所有绑定老人
- 显示健康状态（good/warning/danger）
- 点击查看详情

---

### 9. 老人详情 (`/components/children/ElderlyDetail.tsx`)

#### 涉及的API:
- `GET /api/v1/children/elders/{elderId}/detail` - 老人详细信息
- `GET /api/v1/children/monitor/{elderId}/realtime` - 实时监控数据

#### 数据交互点:
```typescript
useEffect(() => {
  // TODO: Call GET /api/v1/children/elders/{elderId}/detail
  // Response: { 
  //   elderId, personalInfo, healthData, alerts, medications 
  // }
}, [elderId]);

// 实时数据轮询
useEffect(() => {
  const interval = setInterval(() => {
    // TODO: Call GET /api/v1/children/monitor/{elderId}/realtime
  }, 30000); // 每30秒更新
  return () => clearInterval(interval);
}, [elderId]);
```

---

### 10. 智能提醒 (`/components/children/SmartReminders.tsx`)

#### 涉及的API:
- `GET /api/v1/children/reminders/list` - 提醒列表
- `POST /api/v1/children/reminders/create` - 创建提醒
- `PUT /api/v1/children/reminders/{reminderId}/status` - 更新提醒状态

#### 数据交互点:
```typescript
// 获取提醒列表
useEffect(() => {
  // TODO: Call GET /api/v1/children/reminders/list
  // Response: { 
  //   reminders: [{ 
  //     reminderId, elderId, elderName, type, title, 
  //     description, scheduledTime, status, priority 
  //   }] 
  // }
}, []);

// 创建提醒
const handleCreateReminder = (reminderData) => {
  // TODO: Call POST /api/v1/children/reminders/create
  // Request: { elderId, type, title, description, scheduledTime, repeat, priority }
};

// 标记完成
const handleCompleteReminder = (reminderId) => {
  // TODO: Call PUT /api/v1/children/reminders/{reminderId}/status
  // Request: { status: 'completed' }
};
```

---

### 11. 子女端AI助手 (`/components/children/ChildrenAIAssistant.tsx`)

#### 涉及的API:
- `POST /api/v1/children/ai/advice` - 获取AI健康建议

#### 数据交互点:
```typescript
const handleGetAdvice = (elderId: string, concern: string) => {
  // TODO: Call POST /api/v1/children/ai/advice
  // Request: { elderId, concern }
  // Response: { advice, recommendations, urgency }
};
```

---

## 🏥 社区端组件

### 12. 社区端大屏 (`/components/community/BigScreenDashboard.tsx`)

#### 涉及的API:
- `GET /api/v1/community/dashboard/overview` - 社区概览统计
- `GET /api/v1/community/dashboard/age-distribution` - 年龄分布
- `GET /api/v1/community/dashboard/health-trends?period=month` - 健康趋势
- `GET /api/v1/community/dashboard/devices` - 设备状态
- `GET /api/v1/community/dashboard/services` - 服务统计

#### 数据交互点:
```typescript
// 实时数据刷新
useEffect(() => {
  const fetchDashboardData = async () => {
    // TODO: Call GET /api/v1/community/dashboard/overview
    // TODO: Call GET /api/v1/community/dashboard/age-distribution
    // TODO: Call GET /api/v1/community/dashboard/health-trends?period=month
    // TODO: Call GET /api/v1/community/dashboard/devices
    // TODO: Call GET /api/v1/community/dashboard/services
  };
  
  fetchDashboardData();
  const interval = setInterval(fetchDashboardData, 60000); // 每分钟刷新
  return () => clearInterval(interval);
}, []);
```

---

### 13. 2D数字孪生地图 (`/components/community/bigscreen/CommunityMap2D.tsx`)

#### 涉及的API:
- `GET /api/v1/community/map/config` - 地图配置
- `GET /api/v1/community/map/elders/locations` - 老人位置
- `GET /api/v1/community/map/alerts` - 地图告警

#### 数据交互点:
```typescript
// 获取地图配置
useEffect(() => {
  // TODO: Call GET /api/v1/community/map/config
  // Response: { mapImage, bounds, buildings }
}, []);

// 实时位置更新（可以使用WebSocket）
useEffect(() => {
  const interval = setInterval(() => {
    // TODO: Call GET /api/v1/community/map/elders/locations
    // Response: { elders: [{ elderId, name, coordinates, building, status }] }
  }, 5000); // 每5秒更新
  return () => clearInterval(interval);
}, []);

// 告警监听
useEffect(() => {
  // TODO: Call GET /api/v1/community/map/alerts
  // TODO: 或使用 WebSocket ws://api-server/api/v1/community/realtime
}, []);
```

---

### 14. 告警管理 (`/components/community/AlertManagement.tsx`)

#### 涉及的API:
- `GET /api/v1/community/alerts/list?status=all&severity=all` - 告警列表
- `PUT /api/v1/community/alerts/{alertId}/handle` - 处理告警

#### 数据交互点:
```typescript
// 获取告警
useEffect(() => {
  // TODO: Call GET /api/v1/community/alerts/list?status=active&page=1&pageSize=20
  // Response: { 
  //   total, 
  //   alerts: [{ 
  //     alertId, elderId, elderName, type, severity, 
  //     message, location, timestamp, status, assignedTo 
  //   }] 
  // }
}, []);

// 处理告警
const handleAlert = (alertId: string, action: string) => {
  // TODO: Call PUT /api/v1/community/alerts/{alertId}/handle
  // Request: { action: 'acknowledge|resolve|escalate', assignTo, note }
};
```

---

### 15. 群体健康分析 (`/components/community/GroupHealthAnalysis.tsx`)

#### 涉及的API:
- `GET /api/v1/community/analysis/group-health?ageGroup=all&metric=all&period=month`

#### 数据交互点:
```typescript
useEffect(() => {
  // TODO: Call GET /api/v1/community/analysis/group-health
  // Response: { 
  //   summary: { totalElders, healthyCount, warningCount, criticalCount },
  //   metrics: { heartRate, bloodPressure },
  //   trends: [{ date, healthyPercentage, warningPercentage }]
  // }
}, []);
```

---

## 🔄 共享组件

### 16. 个人信息 (`/components/MyInfo.tsx`)

#### 涉及的API:
- `GET /api/v1/{role}/profile` - 获取个人信息
- `PUT /api/v1/{role}/profile` - 更新个人信息

#### 数据交互点:
```typescript
// role 根据登录用户类型确定: elderly | children | community

useEffect(() => {
  // TODO: Call GET /api/v1/{role}/profile
  // Response: { 
  //   userId, name, avatar, phone, email, 
  //   emergencyContacts: [{ name, relationship, phone }] 
  // }
}, []);

const handleUpdateProfile = (profileData) => {
  // TODO: Call PUT /api/v1/{role}/profile
  // Request: { name, phone, email, emergencyContacts }
};
```

---

### 17. AI咨询（通用） (`/components/consultation/AIConsultation.tsx`)

#### 涉及的API:
- `POST /api/v1/elderly/ai/chat` - 老人端AI对话
- `POST /api/v1/children/ai/advice` - 子女端AI建议
- `POST /api/v1/elderly/ai/analyze` - AI分析

---

## 📊 数据刷新策略

### 实时数据 (WebSocket推荐)
- 地图老人位置: 每5秒
- 大屏统计数据: 每60秒
- 告警通知: 实时推送

### 定期刷新 (轮询)
- 今日健康数据: 每30秒
- 子女端老人列表: 每30秒
- 提醒列表: 每60秒

### 按需加载
- 历史报告列表: 用户打开页面时
- 图表数据: 组件挂载时
- 个人信息: 页面加载时

---

## 🔐 认证机制

所有API请求需要在请求头携带token:

```typescript
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  'Content-Type': 'application/json'
};
```

### Token存储
```typescript
// 登录成功后
localStorage.setItem('auth_token', response.data.token);
localStorage.setItem('user_role', 'elderly'); // elderly | children | community
localStorage.setItem('user_id', response.data.userId);

// 登出时清除
localStorage.removeItem('auth_token');
localStorage.removeItem('user_role');
localStorage.removeItem('user_id');
```

---

## 📝 错误处理

所有组件应实现统一的错误处理:

```typescript
const fetchData = async () => {
  try {
    const response = await fetch('/api/v1/elderly/health/today', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    });
    
    const data = await response.json();
    
    if (!data.success) {
      // 处理业务错误
      console.error(data.error.message);
      toast.error(data.error.message);
      return;
    }
    
    // 使用数据
    setHealthData(data.data);
    
  } catch (error) {
    // 处理网络错误
    console.error('Network error:', error);
    toast.error('网络连接失败，请检查您的网络');
  }
};
```

---

## 🚀 下一步行动

### 前端开发任务:
1. ✅ 创建API文档 (`/API_DOCUMENTATION.md`)
2. ✅ 创建组件映射文档 (本文档)
3. ⏳ 为每个组件添加API调用占位符
4. ⏳ 实现统一的API调用工具类
5. ⏳ 实现错误处理中间件
6. ⏳ 实现数据缓存策略

### 后端开发参考:
- 参考 `/API_DOCUMENTATION.md` 实现接口
- 返回数据格式严格遵循文档定义
- 实现token认证机制
- 考虑实现WebSocket用于实时数据推送

---

**文档版本**: 1.0  
**最后更新**: 2024-12-01  
**维护者**: 前端开发团队
