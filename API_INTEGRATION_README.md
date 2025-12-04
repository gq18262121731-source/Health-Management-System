# 智慧健康管理系统 - API集成指南

> **状态**: ✅ 代码整理完成，已添加API占位符和注释  
> **版本**: v1.0  
> **日期**: 2024-12-01

---

## 📦 项目概述

本项目是一个现代化的**三端健康监测系统**，采用医疗风格的蓝绿白配色，包含：
- 🧓 **老人端**: 个人健康监测，特大字体适老化设计，语音播报功能
- 👨‍👩‍👧 **子女端**: 远程监控多位老人的健康状况
- 🏥 **社区端**: 群体健康分析与管理，2D数字孪生地图

---

## 📚 文档目录

### 1. **API接口文档** ([`/API_DOCUMENTATION.md`](./API_DOCUMENTATION.md))
完整的后端API接口规范，包含42个API端点：
- 老人端API（17个）
- 子女端API（9个）
- 社区端API（13个）
- 共享API（3个）

每个API都包含：
- 请求路径和方法
- 请求参数格式
- 响应数据结构
- 示例代码

### 2. **组件API映射文档** ([`/COMPONENT_API_MAPPING.md`](./COMPONENT_API_MAPPING.md))
前端组件与API端点的映射关系，包含17个主要组件：
- 每个组件需要调用哪些API
- 在哪里添加API调用代码
- 数据刷新策略
- 错误处理建议

### 3. **本指南** ([`/API_INTEGRATION_README.md`](./API_INTEGRATION_README.md))
集成指南和快速开始

---

## 🎯 API设计规范

### 路径结构
```
/api/v1/{role}/{resource}/{action}
```

- **role**: `elderly` | `children` | `community`
- **resource**: `health` | `reports` | `ai` | `psychology` | `elders` | `reminders` | `dashboard` | `map` | `alerts`
- **action**: 具体操作，如 `today` | `history` | `chat` | `analyze`

### 示例
```bash
# 老人端 - 获取今日健康数据
GET /api/v1/elderly/health/today

# 子女端 - 获取绑定老人列表
GET /api/v1/children/elders/list

# 社区端 - 获取大屏概览数据
GET /api/v1/community/dashboard/overview
```

---

## 🔑 关键API端点速查

### 老人端核心API
| 端点 | 方法 | 用途 | 组件 |
|------|------|------|------|
| `/api/v1/elderly/auth/login` | POST | 登录 | ElderlyLoginPage |
| `/api/v1/elderly/health/today` | GET | 今日健康概览 | App (analysis tab) |
| `/api/v1/elderly/health/charts/heartrate` | GET | 心率趋势 | HeartRateChart |
| `/api/v1/elderly/reports/current` | GET | 当前报告 | App (reports tab) |
| `/api/v1/elderly/ai/chat` | POST | AI对话 | FloatingAIAssistant |
| `/api/v1/elderly/psychology/mood` | POST | 记录心情 | PsychologyPage |

### 子女端核心API
| 端点 | 方法 | 用途 | 组件 |
|------|------|------|------|
| `/api/v1/children/auth/login` | POST | 登录 | ChildrenLoginPage |
| `/api/v1/children/elders/list` | GET | 老人列表 | ChildrenDashboard |
| `/api/v1/children/elders/{elderId}/detail` | GET | 老人详情 | ElderlyDetail |
| `/api/v1/children/reminders/list` | GET | 提醒列表 | SmartReminders |
| `/api/v1/children/monitor/{elderId}/realtime` | GET | 实时监控 | ElderlyDetail |

### 社区端核心API
| 端点 | 方法 | 用途 | 组件 |
|------|------|------|------|
| `/api/v1/community/auth/login` | POST | 登录 | CommunityLoginPage |
| `/api/v1/community/dashboard/overview` | GET | 概览统计 | BigScreenDashboard |
| `/api/v1/community/map/elders/locations` | GET | 老人位置 | CommunityMap2D |
| `/api/v1/community/alerts/list` | GET | 告警列表 | AlertManagement |
| `/api/v1/community/analysis/group-health` | GET | 群体健康 | GroupHealthAnalysis |

---

## 📂 项目结构

```
/
├── API_DOCUMENTATION.md          # 完整API接口文档
├── COMPONENT_API_MAPPING.md      # 组件与API映射关系
├── API_INTEGRATION_README.md     # 本文件
│
├── App.tsx                        # 主应用入口（老人端）
│
├── components/
│   ├── login/                     # 登录组件
│   │   ├── ElderlyLoginPage.tsx   # ✅ 已添加API占位符
│   │   ├── ChildrenLoginPage.tsx
│   │   └── CommunityLoginPage.tsx
│   │
│   ├── elderly/                   # 老人端组件
│   │   ├── FloatingAIAssistant.tsx  # AI助手
│   │   ├── HealthCardWithAI.tsx     # 健康卡片
│   │   └── AIAnalysisButton.tsx     # AI分析按钮
│   │
│   ├── children/                  # 子女端组件
│   │   ├── ChildrenDashboard.tsx
│   │   ├── ElderlyList.tsx
│   │   ├── ElderlyDetail.tsx
│   │   └── SmartReminders.tsx
│   │
│   ├── community/                 # 社区端组件
│   │   ├── BigScreenDashboard.tsx
│   │   ├── CommunityMap2D.tsx
│   │   ├── AlertManagement.tsx
│   │   └── GroupHealthAnalysis.tsx
│   │
│   ├── dashboard/                 # 仪表板组件
│   │   ├── HealthCharts.tsx        # ✅ 已添加API占位符
│   │   ├── MoodQuickCard.tsx
│   │   └── StatCard.tsx
│   │
│   └── psychology/                # 心理健康组件
│       └── PsychologyPage.tsx
│
└── styles/
    └── globals.css                # 全局样式（医疗风格配色）
```

---

## 🚀 快速开始

### 步骤1: 查看API文档
```bash
# 阅读完整API文档
open API_DOCUMENTATION.md
```

### 步骤2: 了解组件映射
```bash
# 查看哪个组件需要哪些API
open COMPONENT_API_MAPPING.md
```

### 步骤3: 在代码中查找TODO标记
所有需要API集成的地方都已标记为 `TODO: Call [API_ENDPOINT]`

```typescript
// 示例：在 App.tsx 中
useEffect(() => {
  // TODO: Call GET /api/v1/elderly/health/today
  // Response: { success: true, data: { userId, userName, vitalSigns, ... } }
  
  // 临时使用mock数据
  const mockData = {
    userName: "张三",
    vitalSigns: { ... }
  };
}, []);
```

### 步骤4: 替换mock数据为真实API调用
```typescript
useEffect(() => {
  const fetchHealthData = async () => {
    try {
      const response = await fetch('/api/v1/elderly/health/today', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setHealthData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    }
  };
  
  fetchHealthData();
}, []);
```

---

## 💡 代码集成示例

### 示例1: 老人端登录
```typescript
// File: /components/login/ElderlyLoginPage.tsx

const handleLogin = async () => {
  if (!username || !password) {
    speak('请输入账号和密码');
    return;
  }
  
  try {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/elderly/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // 保存token
      localStorage.setItem('auth_token', data.data.token);
      localStorage.setItem('user_id', data.data.userId);
      localStorage.setItem('user_role', 'elderly');
      
      // 记住密码
      if (rememberMe) {
        localStorage.setItem('elderly_username', username);
        localStorage.setItem('elderly_password', password);
        localStorage.setItem('elderly_rememberMe', 'true');
      }
      
      speak('登录成功，正在进入系统');
      setTimeout(onLogin, 1000);
    } else {
      speak(`登录失败：${data.error.message}`);
    }
  } catch (error) {
    speak('网络错误，请稍后重试');
    console.error('Login error:', error);
  }
};
```

### 示例2: 获取今日健康数据
```typescript
// File: /App.tsx

const [healthData, setHealthData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchTodayHealth = async () => {
    try {
      const response = await fetch('/api/v1/elderly/health/today', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setHealthData(data.data);
      } else {
        toast.error(data.error.message);
      }
    } catch (error) {
      toast.error('获取健康数据失败');
    } finally {
      setLoading(false);
    }
  };
  
  if (activeTab === 'analysis') {
    fetchTodayHealth();
  }
}, [activeTab]);

// 在JSX中使用数据
{healthData && (
  <>
    <h2>下午好, {healthData.userName}</h2>
    <HealthCardWithAI
      value={healthData.vitalSigns.bloodSugar.value}
      status={healthData.vitalSigns.bloodSugar.status}
      // ...
    />
  </>
)}
```

### 示例3: 图表数据加载
```typescript
// File: /components/dashboard/HealthCharts.tsx

export function HeartRateChart() {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchHeartRateData = async () => {
      try {
        const response = await fetch(
          '/api/v1/elderly/health/charts/heartrate?period=today',
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
          }
        );
        
        const data = await response.json();
        
        if (data.success) {
          setChartData(data.data.dataPoints);
        }
      } catch (error) {
        console.error('Failed to fetch heart rate data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHeartRateData();
    
    // 每30秒刷新一次
    const interval = setInterval(fetchHeartRateData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  if (loading) {
    return <div>加载中...</div>;
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>心率趋势 (24h)</CardTitle>
      </CardHeader>
      <CardContent>
        <AreaChart data={chartData}>
          {/* ... chart configuration */}
        </AreaChart>
      </CardContent>
    </Card>
  );
}
```

### 示例4: AI对话
```typescript
// File: /components/elderly/FloatingAIAssistant.tsx

const handleSendMessage = async (message: string) => {
  try {
    const response = await fetch('/api/v1/elderly/ai/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        context: {
          dataType: currentDataType,
          currentValue: currentValue
        }
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // 添加AI回复到消息列表
      setMessages(prev => [...prev, {
        type: 'ai',
        content: data.data.message,
        timestamp: new Date()
      }]);
      
      // 如果有需要注意的事项，显示警告
      if (data.data.needsAttention) {
        toast.warning('请注意：您的健康数据需要关注');
      }
    }
  } catch (error) {
    toast.error('AI助手暂时无法回复');
  }
};
```

---

## 🛠️ 建议的工具类

### API Client封装
创建一个统一的API调用工具类：

```typescript
// File: /utils/apiClient.ts

export class ApiClient {
  private baseURL = '/api/v1';
  
  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    };
  }
  
  async get(endpoint: string) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  async post(endpoint: string, data: any) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data)
      });
      
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  async put(endpoint: string, data: any) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data)
      });
      
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  private async handleResponse(response: Response) {
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error.message);
    }
    
    return data.data;
  }
  
  private handleError(error: any) {
    console.error('API Error:', error);
    throw error;
  }
}

export const apiClient = new ApiClient();
```

### 使用示例
```typescript
import { apiClient } from './utils/apiClient';

// GET请求
const healthData = await apiClient.get('/elderly/health/today');

// POST请求
const loginResult = await apiClient.post('/elderly/auth/login', {
  username: 'demo',
  password: '123456'
});

// PUT请求
await apiClient.put('/elderly/profile', {
  name: '张三',
  phone: '13800138000'
});
```

---

## 📊 数据模型TypeScript定义

### 生命体征数据
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

### 今日健康数据
```typescript
interface TodayHealthData {
  userId: string;
  userName: string;
  date: string;
  greeting: string;
  vitalSigns: VitalSigns;
  activity: {
    steps: number;
    goal: number;
    percentage: number;
  };
  weight: {
    value: number;
    unit: 'kg';
    bmi: number;
    bmiStatus: 'underweight' | 'normal' | 'overweight' | 'obese';
  };
}
```

---

## 🔐 认证流程

### 1. 登录获取Token
```typescript
const response = await fetch('/api/v1/elderly/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});

const { token, userId } = response.data;

localStorage.setItem('auth_token', token);
localStorage.setItem('user_id', userId);
localStorage.setItem('user_role', 'elderly');
```

### 2. 所有后续请求携带Token
```typescript
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
};
```

### 3. Token过期处理
```typescript
if (response.error.code === 'AUTH_INVALID') {
  // 清除本地token
  localStorage.clear();
  // 跳转到登录页
  window.location.href = '/login';
}
```

---

## ⚠️ 注意事项

### 1. CORS配置
后端需要配置CORS允许前端域名访问：
```javascript
// 后端示例（Express.js）
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
```

### 2. 环境变量
建议使用环境变量配置API基础URL：
```typescript
// .env
VITE_API_BASE_URL=http://localhost:8080/api/v1

// 使用
const BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

### 3. 错误处理
所有API调用都应包含错误处理：
```typescript
try {
  const data = await apiClient.get('/elderly/health/today');
} catch (error) {
  toast.error('获取数据失败，请稍后重试');
  console.error(error);
}
```

### 4. 加载状态
显示加载状态提升用户体验：
```typescript
const [loading, setLoading] = useState(true);

useEffect(() => {
  setLoading(true);
  fetchData().finally(() => setLoading(false));
}, []);

if (loading) return <Spinner />;
```

---

## 📈 性能优化建议

### 1. 数据缓存
对不常变化的数据进行缓存：
```typescript
const CACHE_DURATION = 5 * 60 * 1000; // 5分钟

const getCachedData = (key: string) => {
  const cached = localStorage.getItem(key);
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < CACHE_DURATION) {
      return data;
    }
  }
  return null;
};
```

### 2. 请求合并
将多个相关请求合并：
```typescript
const fetchDashboardData = async () => {
  const [health, charts, reports] = await Promise.all([
    apiClient.get('/elderly/health/today'),
    apiClient.get('/elderly/health/charts/heartrate'),
    apiClient.get('/elderly/reports/current')
  ]);
  
  return { health, charts, reports };
};
```

### 3. 防抖和节流
对频繁触发的操作进行防抖：
```typescript
import { debounce } from 'lodash';

const debouncedSearch = debounce(async (query) => {
  const results = await apiClient.get(`/search?q=${query}`);
  setSearchResults(results);
}, 300);
```

---

## ✅ 已完成工作

- ✅ 创建完整API文档 (42个端点)
- ✅ 创建组件API映射文档 (17个组件)
- ✅ 为登录组件添加API占位符和注释
- ✅ 为图表组件添加API占位符和注释
- ✅ 定义统一的数据模型和接口
- ✅ 提供详细的代码集成示例
- ✅ 编写API客户端工具类建议

---

## 🎯 下一步任务

### 前端开发:
1. ⏳ 为所有组件添加完整的API调用代码
2. ⏳ 实现统一的错误处理中间件
3. ⏳ 添加加载状态和骨架屏
4. ⏳ 实现数据缓存策略
5. ⏳ 添加WebSocket支持（实时数据）
6. ⏳ 单元测试和集成测试

### 后端开发:
1. ⏳ 根据API文档实现所有端点
2. ⏳ 实现JWT认证机制
3. ⏳ 实现WebSocket服务
4. ⏳ 数据库设计和ORM配置
5. ⏳ API性能优化和缓存
6. ⏳ 接口文档自动生成（Swagger）

---

## 📞 联系与支持

如有任何问题，请参考：
- **API文档**: `/API_DOCUMENTATION.md`
- **组件映射**: `/COMPONENT_API_MAPPING.md`
- **Git提交**: 查看历史记录了解代码变更

---

**文档维护**: 前端开发团队  
**最后更新**: 2024-12-01  
**版本**: v1.0
