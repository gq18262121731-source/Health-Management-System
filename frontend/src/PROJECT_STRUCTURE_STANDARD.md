# 项目文件结构规范

> **版本**: v2.0  
> **生效日期**: 2024-12-01  
> **适用范围**: 智慧健康管理系统  
> **状态**: ✅ 正式标准

---

## 🎯 设计原则

### 1. 关注点分离 (Separation of Concerns)
- **页面组件** 只负责组合和布局
- **复用组件** 只负责 UI 展示
- **Hooks** 负责业务逻辑和数据获取
- **API** 负责与后端通信

### 2. 单一职责 (Single Responsibility)
- 每个文件只做一件事
- 每个组件只有一个改变的理由
- 每个 Hook 只处理一个业务逻辑

### 3. 高内聚低耦合 (High Cohesion, Low Coupling)
- 相关功能放在一起
- 减少组件间依赖
- 通过 Props 和 Context 通信

### 4. 可测试性 (Testability)
- 业务逻辑独立可测
- 组件纯粹易测
- Mock 数据容易

---

## 📁 标准目录结构

```
src/
├── pages/              # 📄 页面级组件（对应路由）
├── components/         # 🧩 可复用UI组件
├── hooks/             # 🎣 自定义Hooks
├── api/               # 🌐 API客户端
├── types/             # 📘 TypeScript类型
├── utils/             # 🛠️ 工具函数
├── constants/         # 📌 常量定义
├── styles/            # 🎨 样式文件
└── assets/            # 🖼️ 静态资源
```

---

## 📄 Pages (页面组件)

### 定义
- 对应路由的顶层组件
- 负责组合多个子组件
- 管理页面级状态
- 处理组件间通信

### 目录结构

```
src/pages/
├── elderly/                    # 老人端页面
│   ├── DashboardPage.tsx      # 今日健康
│   ├── ReportsPage.tsx        # 历史报告
│   ├── PsychologyPage.tsx     # 心理健康
│   ├── AIConsultationPage.tsx # AI助手
│   └── ProfilePage.tsx        # 个人信息
├── children/                   # 子女端页面
│   ├── DashboardPage.tsx      # 仪表板
│   ├── ElderlyDetailPage.tsx  # 老人详情
│   └── RemindersPage.tsx      # 提醒管理
├── community/                  # 社区端页面
│   ├── BigScreenPage.tsx      # 大屏展示
│   ├── AlertManagementPage.tsx # 告警管理
│   └── AnalyticsPage.tsx      # 数据分析
└── auth/                       # 认证页面
    ├── RoleSelectionPage.tsx  # 角色选择
    ├── ElderlyLoginPage.tsx   # 老人端登录
    ├── ChildrenLoginPage.tsx  # 子女端登录
    └── CommunityLoginPage.tsx # 社区端登录
```

### 代码规范

```typescript
/**
 * ✅ 好的页面组件示例
 */
export function DashboardPage() {
  // 1. 使用 Hooks 获取数据（不直接调用 API）
  const { data, loading, error } = useHealthData();
  const { charts } = useHealthCharts('week');
  
  // 2. 页面级状态管理
  const [activeTab, setActiveTab] = useState('overview');
  
  // 3. 事件处理
  const handleNavigate = (mood: string) => {
    setActiveTab('psychology');
  };
  
  // 4. 条件渲染
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  // 5. 组合子组件
  return (
    <div className="p-6 space-y-6">
      <WelcomeSection user={data.userName} />
      <HealthCardsGrid vitalSigns={data.vitalSigns} />
      <MoodQuickCard onNavigate={handleNavigate} />
      <ChartsSection data={charts} />
    </div>
  );
}

/**
 * ❌ 不好的页面组件示例
 */
export function BadDashboardPage() {
  const [data, setData] = useState(null);
  
  // ❌ 直接在组件中调用 API
  useEffect(() => {
    fetch('/api/v1/elderly/health/today')
      .then(res => res.json())
      .then(data => setData(data));
  }, []);
  
  // ❌ 包含太多业务逻辑
  const processHealthData = (data: any) => {
    // 复杂的数据处理逻辑...
  };
  
  // ❌ 直接写大量 JSX，不拆分组件
  return (
    <div>
      {/* 100行重复的 JSX... */}
    </div>
  );
}
```

### 命名规范
- **文件名**: `DashboardPage.tsx` (大驼峰 + Page后缀)
- **组件名**: `export function DashboardPage()` (与文件名一致)
- **路径**: `/elderly/dashboard` → `src/pages/elderly/DashboardPage.tsx`

---

## 🧩 Components (复用组件)

### 定义
- 可在多个页面复用的UI组件
- **不包含**任何数据获取逻辑
- **不包含**复杂业务逻辑
- 通过 Props 接收数据

### 目录结构

```
src/components/
├── ui/                        # 基础UI组件（shadcn/ui）
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── ...
├── common/                    # 通用业务组件
│   ├── VoiceInputButton.tsx  # 语音输入按钮
│   ├── AIAnalysisButton.tsx  # AI分析按钮
│   ├── StatCard.tsx          # 统计卡片
│   └── ImageWithFallback.tsx # 图片组件
├── charts/                    # 图表组件
│   ├── HeartRateChart.tsx
│   ├── SleepAnalysisChart.tsx
│   ├── BloodPressureChart.tsx
│   ├── MoodTrendChart.tsx
│   └── HealthRadarChart.tsx
├── cards/                     # 卡片组件
│   ├── HealthCardWithAI.tsx  # 健康卡片（带AI）
│   ├── MoodQuickCard.tsx     # 快速心情记录
│   ├── ElderlyListItem.tsx   # 老人列表项
│   └── ReminderCard.tsx      # 提醒卡片
├── layout/                    # 布局组件
│   ├── Header.tsx
│   ├── Navbar.tsx
│   ├── Breadcrumb.tsx
│   └── Footer.tsx
├── map/                       # 地图组件
│   ├── CommunityMap2D.tsx
│   ├── BuildingMarker.tsx
│   └── AlertMarker.tsx
└── modals/                    # 弹窗组件
    ├── FloatingAIAssistant.tsx
    ├── ReminderDialog.tsx
    └── ConfirmDialog.tsx
```

### 代码规范

```typescript
/**
 * ✅ 好的复用组件示例
 */
interface HealthCardProps {
  icon: LucideIcon;
  value: number | string;
  unit: string;
  title: string;
  status: string;
  onAnalyze?: (prompt: string) => void;
}

export function HealthCard({ 
  icon: Icon, 
  value, 
  unit, 
  title, 
  status,
  onAnalyze 
}: HealthCardProps) {
  // ✅ 只包含UI逻辑
  const handleClick = () => {
    onAnalyze?.(`请分析我的${title}数据：${value} ${unit}`);
  };
  
  return (
    <Card>
      <CardContent>
        <Icon className="h-8 w-8" />
        <div className="text-6xl font-bold">{value}</div>
        <div className="text-xl">{unit}</div>
        <div>{title}</div>
        <Button onClick={handleClick}>AI分析</Button>
      </CardContent>
    </Card>
  );
}

/**
 * ❌ 不好的复用组件示例
 */
export function BadHealthCard() {
  const [data, setData] = useState(null);
  
  // ❌ 组件内部获取数据
  useEffect(() => {
    fetch('/api/health').then(res => setData(res.json()));
  }, []);
  
  // ❌ 包含复杂业务逻辑
  const analyzeHealth = (data: any) => {
    // 复杂的健康分析逻辑...
  };
  
  return <div>{/* ... */}</div>;
}
```

### 命名规范
- **文件名**: `HealthCard.tsx` (大驼峰)
- **组件名**: `export function HealthCard()` (与文件名一致)
- **Props 接口**: `interface HealthCardProps` (组件名 + Props)

---

## 🎣 Hooks (自定义Hooks)

### 定义
- 封装可复用的业务逻辑
- 负责数据获取和状态管理
- 返回数据和操作方法

### 目录结构

```
src/hooks/
├── api/                       # API相关Hooks
│   ├── useHealthData.ts      # 获取健康数据
│   ├── useElderlyList.ts     # 获取老人列表
│   ├── useReports.ts         # 获取报告
│   ├── useMoodHistory.ts     # 获取心情历史
│   ├── useReminders.ts       # 获取提醒
│   ├── useCommunityStats.ts  # 获取社区统计
│   └── useAIChat.ts          # AI对话
├── auth/                      # 认证相关Hooks
│   ├── useAuth.ts            # 认证状态
│   ├── useLogin.ts           # 登录
│   └── useLogout.ts          # 登出
├── voice/                     # 语音相关Hooks
│   ├── useSpeechRecognition.ts # 语音识别
│   ├── useSpeechSynthesis.ts   # 语音播报
│   └── useVoiceInput.ts        # 语音输入
└── utils/                     # 工具Hooks
    ├── useLocalStorage.ts    # LocalStorage
    ├── useDebounce.ts        # 防抖
    ├── useInterval.ts        # 定时器
    └── useWebSocket.ts       # WebSocket
```

### 代码规范

```typescript
/**
 * ✅ 好的 Hook 示例
 */
export function useHealthData() {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      // 调用 API 客户端，不直接 fetch
      const response = await elderlyHealthApi.getTodayHealth();
      setData(response.data);
    } catch (err) {
      setError(err as Error);
      toast.error('获取健康数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * ❌ 不好的 Hook 示例
 */
export function useBadHealthData() {
  const [data, setData] = useState(null);
  
  // ❌ 直接使用 fetch
  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.log(err)); // ❌ 错误处理不统一
  }, []);
  
  // ❌ 没有 loading 和 error 状态
  return data;
}
```

### 命名规范
- **文件名**: `useHealthData.ts` (小驼峰 + use前缀)
- **Hook名**: `export function useHealthData()` (与文件名一致)
- **返回值**: 对象形式 `{ data, loading, error, refetch }`

---

## 🌐 API (API客户端)

### 定义
- 统一管理所有 API 调用
- 封装 Axios 实例和拦截器
- 提供类型安全的API函数

### 目录结构

```
src/api/
├── client.ts              # Axios客户端实例
├── config.ts              # API配置
├── interceptors.ts        # 拦截器
├── elderly/               # 老人端API
│   ├── health.ts         # 健康数据API
│   ├── reports.ts        # 报告API
│   ├── psychology.ts     # 心理健康API
│   └── ai.ts             # AI API
├── children/              # 子女端API
│   ├── elders.ts         # 老人管理API
│   ├── reminders.ts      # 提醒API
│   └── monitoring.ts     # 监测API
├── community/             # 社区端API
│   ├── dashboard.ts      # 仪表板API
│   ├── map.ts            # 地图API
│   └── alerts.ts         # 告警API
└── auth/                  # 认证API
    ├── login.ts          # 登录
    └── profile.ts        # 个人信息
```

### 代码规范

```typescript
/**
 * ✅ 好的 API 函数示例
 */
// src/api/elderly/health.ts
import { api } from '../client';
import { API_ENDPOINTS } from '../config';
import { HealthTodayResponse } from '@/types/api/health.types';

export const elderlyHealthApi = {
  /**
   * 获取今日健康数据
   */
  getTodayHealth: () => 
    api.get<HealthTodayResponse>(API_ENDPOINTS.ELDERLY.HEALTH_TODAY),

  /**
   * 获取心率趋势图数据
   * @param period 时间段 ('week' | 'month')
   */
  getHeartRateChart: (period: 'week' | 'month' = 'week') => 
    api.get<HeartRateChartResponse>(
      `${API_ENDPOINTS.ELDERLY.CHARTS_HEARTRATE}?period=${period}`
    ),
};

/**
 * ❌ 不好的 API 函数示例
 */
// ❌ 直接导出 fetch 函数
export function fetchHealthData() {
  return fetch('/api/health').then(res => res.json());
}

// ❌ 没有类型定义
export function getHealth() {
  return axios.get('/api/health');
}
```

### 命名规范
- **文件名**: `health.ts` (小写)
- **导出对象**: `elderlyHealthApi`, `childrenEldersApi` (角色 + 模块 + Api)
- **函数名**: `getTodayHealth()`, `getHeartRateChart()` (动词 + 名词)

---

## 📘 Types (类型定义)

### 定义
- 集中管理所有 TypeScript 类型
- 提高类型复用性
- 确保类型安全

### 目录结构

```
src/types/
├── api/                   # API响应类型
│   ├── health.types.ts   # 健康数据类型
│   ├── reports.types.ts  # 报告类型
│   ├── elders.types.ts   # 老人数据类型
│   └── common.types.ts   # 通用类型
├── models/                # 数据模型
│   ├── User.ts
│   ├── HealthData.ts
│   ├── Report.ts
│   └── Reminder.ts
└── index.ts               # 类型统一导出
```

### 代码规范

```typescript
/**
 * ✅ 好的类型定义示例
 */
// src/types/api/health.types.ts

/** 通用 API 响应 */
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  timestamp: string;
}

/** 健康状态 */
export type HealthStatus = 'normal' | 'warning' | 'danger';

/** 今日健康数据 */
export interface HealthTodayData {
  userId: string;
  userName: string;
  vitalSigns: {
    temperature: {
      value: number;
      unit: string;
      change: number;
      status: HealthStatus;
    };
    // ...
  };
}

/** API 响应 */
export type HealthTodayResponse = APIResponse<HealthTodayData>;
```

### 命名规范
- **文件名**: `health.types.ts` (小写 + .types后缀)
- **接口名**: `HealthTodayData`, `HealthCardProps` (大驼峰)
- **类型别名**: `HealthStatus`, `UserRole` (大驼峰)

---

## 🛠️ Utils (工具函数)

### 定义
- 纯函数工具集
- 不依赖组件状态
- 可独立测试

### 目录结构

```
src/utils/
├── format.ts          # 格式化函数
├── validators.ts      # 验证函数
├── storage.ts         # 存储工具
├── speech.ts          # 语音工具
└── date.ts            # 日期工具
```

### 代码规范

```typescript
/**
 * ✅ 好的工具函数示例
 */
// src/utils/format.ts

/** 格式化血压值 */
export function formatBloodPressure(
  systolic: number, 
  diastolic: number
): string {
  return `${systolic}/${diastolic}`;
}

/** 格式化日期 */
export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}
```

---

## 📌 Constants (常量定义)

### 目录结构

```
src/constants/
├── routes.ts          # 路由常量
├── api.ts             # API端点常量
├── colors.ts          # 颜色常量
└── messages.ts        # 消息常量
```

### 代码规范

```typescript
/**
 * ✅ 好的常量定义示例
 */
// src/constants/routes.ts

export const ROUTES = {
  ELDERLY: {
    DASHBOARD: '/elderly/dashboard',
    REPORTS: '/elderly/reports',
    PSYCHOLOGY: '/elderly/psychology',
    AI: '/elderly/ai',
    PROFILE: '/elderly/profile',
  },
  CHILDREN: {
    DASHBOARD: '/children/dashboard',
    ELDERLY_DETAIL: (id: string) => `/children/elderly/${id}`,
    REMINDERS: '/children/reminders',
  },
  COMMUNITY: {
    BIGSCREEN: '/community/bigscreen',
    ALERTS: '/community/alerts',
    ANALYTICS: '/community/analytics',
  },
  AUTH: {
    SELECT_ROLE: '/',
    ELDERLY_LOGIN: '/auth/elderly',
    CHILDREN_LOGIN: '/auth/children',
    COMMUNITY_LOGIN: '/auth/community',
  },
} as const;
```

---

## 🎨 Styles (样式文件)

### 目录结��

```
src/styles/
├── globals.css        # 全局样式
└── tailwind.css       # Tailwind配置
```

---

## 🖼️ Assets (静态资源)

### 目录结构

```
src/assets/
├── images/            # 图片文件
├── icons/             # 图标文件
└── fonts/             # 字体文件
```

---

## 🚀 工作流程

### 开发新功能的标准流程

#### 1. 定义类型 (Types First)
```typescript
// src/types/api/newFeature.types.ts
export interface NewFeatureData {
  id: string;
  name: string;
}
export type NewFeatureResponse = APIResponse<NewFeatureData>;
```

#### 2. 创建 API 函数
```typescript
// src/api/newModule/newFeature.ts
export const newFeatureApi = {
  getList: () => api.get<NewFeatureResponse>('/new-feature/list'),
};
```

#### 3. 创建 Hook
```typescript
// src/hooks/api/useNewFeature.ts
export function useNewFeature() {
  const [data, setData] = useState<NewFeatureData | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    newFeatureApi.getList().then(res => setData(res.data));
  }, []);
  
  return { data, loading };
}
```

#### 4. 创建复用组件
```typescript
// src/components/cards/NewFeatureCard.tsx
export function NewFeatureCard({ data }: { data: NewFeatureData }) {
  return <Card>{data.name}</Card>;
}
```

#### 5. 创建页面组件
```typescript
// src/pages/newModule/NewFeaturePage.tsx
export function NewFeaturePage() {
  const { data, loading } = useNewFeature();
  
  if (loading) return <Loading />;
  
  return (
    <div>
      <NewFeatureCard data={data} />
    </div>
  );
}
```

---

## ✅ 代码审查检查清单

### 组件审查
- [ ] 页面组件在 `/src/pages/`
- [ ] 复用组件在 `/src/components/`
- [ ] 组件不直接调用 API
- [ ] 组件通过 Props 接收数据
- [ ] 组件职责单一

### Hooks 审查
- [ ] Hooks 在 `/src/hooks/`
- [ ] Hook 名称以 `use` 开头
- [ ] 返回 `{ data, loading, error }` 格式
- [ ] 使用 API 客户端，不直接 fetch
- [ ] 错误处理统一

### API 审查
- [ ] API 函数在 `/src/api/`
- [ ] 使用 `api.get/post/put/delete` 方法
- [ ] 有完整的类型定义
- [ ] 函数有注释说明

### 类型审查
- [ ] 类型定义在 `/src/types/`
- [ ] 接口和类型命名规范
- [ ] 复用性高
- [ ] 导出统一

---

## 📚 相关文档

1. **重构计划**: `/ARCHITECTURE_REFACTOR_PLAN.md`
2. **API 文档**: `/docs/api/API_DOCUMENTATION.md`
3. **迁移指南**: `/docs/guides/MIGRATION_GUIDE.md`

---

**维护者**: React 架构师  
**最后更新**: 2024-12-01  
**版本**: v2.0  
**状态**: ✅ 正式标准
