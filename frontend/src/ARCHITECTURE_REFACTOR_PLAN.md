# React 架构重构计划

> **重构负责人**: React 架构师  
> **开始时间**: 2024-12-01  
> **预计完成**: 2024-12-03  
> **状态**: 🚧 进行中

---

## 📋 目录

1. [当前问题分析](#当前问题分析)
2. [新架构设计](#新架构设计)
3. [重构步骤](#重构步骤)
4. [迁移指南](#迁移指南)
5. [验收标准](#验收标准)

---

## 🔍 当前问题分析

### 问题 1: 文件结构混乱

```
❌ 当前结构（混乱）:
/
├── App.tsx                    # 重复！根目录有一个
├── /src/App.tsx               # 重复！src 也有一个
├── /components/               # 重复！根目录有一个
├── /src/components/           # 重复！src 也有一个
├── /styles/globals.css        # 重复！
├── /src/styles/globals.css    # 重复！
├── API_DOCUMENTATION.md       # 文档散落在根目录
├── FIGMA_*.md                 # 大量文档在根目录
└── ...太多文档在根目录

问题：
- 重复文件导致混淆
- 不清楚哪个是主文件
- AI 生成代码时不知道放在哪里
- 维护成本高
```

### 问题 2: 业务逻辑与 UI 耦合

```tsx
❌ 当前代码（耦合）:
// App.tsx
export default function App() {
  const [data, setData] = useState(null);
  
  // 业务逻辑混在组件中 ❌
  useEffect(() => {
    fetch('/api/v1/elderly/health/today')
      .then(res => res.json())
      .then(data => setData(data));
  }, []);
  
  return <HealthCard data={data} />;
}

问题：
- 组件负责太多职责
- 难以测试
- 难以复用
- 数据获取逻辑无法共享
```

### 问题 3: 缺少统一的 API 客户端

```tsx
❌ 当前代码（分散）:
// 每个组件都自己写 fetch
fetch('/api/v1/elderly/health/today')
fetch('/api/v1/children/elders/list')
fetch('/api/v1/community/dashboard/overview')

问题：
- 错误处理不统一
- Loading 状态不统一
- 无法统一配置（baseURL, headers, 拦截器）
- 代码重复
```

### 问题 4: 页面组件和复用组件混在一起

```
❌ 当前结构:
/components/
├── children/ChildrenDashboard.tsx   # 页面级组件 ❌
├── elderly/HealthCardWithAI.tsx     # 复用组件 ✓
├── dashboard/MoodQuickCard.tsx      # 复用组件 ✓
├── login/ElderlyLoginPage.tsx       # 页面级组件 ❌

问题：
- 无法区分页面和组件
- 不知道哪些可以复用
- 难以理解项目结构
```

---

## 🏗️ 新架构设计

### 标准目录结构

```
smart-health-system/
│
├── /docs/                          # 📚 所有文档（新建）
│   ├── api/
│   │   ├── API_DOCUMENTATION.md
│   │   ├── COMPONENT_API_MAPPING.md
│   │   └── API_INTEGRATION_README.md
│   ├── architecture/
│   │   ├── ARCHITECTURE_REFACTOR_PLAN.md
│   │   └── PROJECT_STRUCTURE.md
│   ├── figma/
│   │   ├── FIGMA_DATA_BINDING_SPEC.md
│   │   ├── FIGMA_WEB_LAYOUT_GUIDELINES.md
│   │   └── FIGMA_REFACTOR_CHECKLIST.md
│   └── guides/
│       ├── QUICK_START.md
│       ├── MIGRATION_GUIDE.md
│       └── CODE_REFACTOR_STATUS.md
│
├── /src/                           # 🎯 源代码根目录
│   │
│   ├── /pages/                     # 📄 页面级组件（新建）
│   │   ├── /elderly/               # 老人端页面
│   │   │   ├── DashboardPage.tsx          # 今日健康
│   │   │   ├── ReportsPage.tsx            # 历史报告
│   │   │   ├── PsychologyPage.tsx         # 心理健康
│   │   │   ├── AIConsultationPage.tsx     # AI助手
│   │   │   └── ProfilePage.tsx            # 个人信息
│   │   ├── /children/              # 子女端页面
│   │   │   ├── DashboardPage.tsx          # 仪表板
│   │   │   ├── ElderlyDetailPage.tsx      # 老人详情
│   │   │   └── RemindersPage.tsx          # 提醒管理
│   │   ├── /community/             # 社区端页面
│   │   │   ├── BigScreenPage.tsx          # 大屏展示
│   │   │   ├── AlertManagementPage.tsx    # 告警管理
│   │   │   └── AnalyticsPage.tsx          # 数据分析
│   │   └── /auth/                  # 认证页面
│   │       ├── RoleSelectionPage.tsx      # 角色选择
│   │       ├── ElderlyLoginPage.tsx       # 老人端登录
│   │       ├── ChildrenLoginPage.tsx      # 子女端登录
│   │       └── CommunityLoginPage.tsx     # 社区端登录
│   │
│   ├── /components/                # 🧩 可复用组件（重组）
│   │   ├── /ui/                    # 基础 UI 组件（shadcn/ui）
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── /common/                # 通用业务组件（新建）
│   │   │   ├── VoiceInputButton.tsx       # 语音输入按钮
│   │   │   ├── AIAnalysisButton.tsx       # AI分析按钮
│   │   │   ├── StatCard.tsx               # 统计卡片
│   │   │   └── ImageWithFallback.tsx      # 图片组件
│   │   ├── /charts/                # 图表组件（新建）
│   │   │   ├── HeartRateChart.tsx
│   │   │   ├── SleepAnalysisChart.tsx
│   │   │   ├── BloodPressureChart.tsx
│   │   │   ├── MoodTrendChart.tsx
│   │   │   └── HealthRadarChart.tsx
│   │   ├── /cards/                 # 卡片组件（新建）
│   │   │   ├── HealthCardWithAI.tsx       # 健康卡片（带AI）
│   │   │   ├── MoodQuickCard.tsx          # 快速心情记录
│   │   │   ├── ElderlyListItem.tsx        # 老人列表项
│   │   │   └── ReminderCard.tsx           # 提醒卡片
│   │   ├── /layout/                # 布局组件
│   │   │   ├── Header.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── Breadcrumb.tsx
│   │   │   └── Footer.tsx
│   │   ├── /map/                   # 地图组件（新建）
│   │   │   ├── CommunityMap2D.tsx
│   │   │   ├── BuildingMarker.tsx
│   │   │   └── AlertMarker.tsx
│   │   └── /modals/                # 弹窗组件（新建）
│   │       ├── FloatingAIAssistant.tsx    # 悬浮AI助手
│   │       ├── ReminderDialog.tsx         # 提醒弹窗
│   │       └── ConfirmDialog.tsx          # 确认弹窗
│   │
│   ├── /hooks/                     # 🎣 自定义 Hooks（新建）
│   │   ├── /api/                   # API 相关 Hooks
│   │   │   ├── useHealthData.ts           # 获取健康数据
│   │   │   ├── useElderlyList.ts          # 获取老人列表
│   │   │   ├── useReports.ts              # 获取报告
│   │   │   ├── useMoodHistory.ts          # 获取心情历史
│   │   │   ├── useReminders.ts            # 获取提醒
│   │   │   ├── useCommunityStats.ts       # 获取社区统计
│   │   │   └── useAIChat.ts               # AI对话
│   │   ├── /auth/                  # 认证相关 Hooks
│   │   │   ├── useAuth.ts                 # 认证状态
│   │   │   ├── useLogin.ts                # 登录
│   │   │   └── useLogout.ts               # 登出
│   │   ├── /voice/                 # 语音相关 Hooks
│   │   │   ├── useSpeechRecognition.ts    # 语音识别
│   │   │   ├── useSpeechSynthesis.ts      # 语音播报
│   │   │   └── useVoiceInput.ts           # 语音输入
│   │   └── /utils/                 # 工具 Hooks
│   │       ├── useLocalStorage.ts         # LocalStorage
│   │       ├── useDebounce.ts             # 防抖
│   │       ├── useInterval.ts             # 定时器
│   │       └── useWebSocket.ts            # WebSocket
│   │
│   ├── /api/                       # 🌐 API 客户端（新建）
│   │   ├── client.ts               # Axios 客户端实例
│   │   ├── config.ts               # API 配置
│   │   ├── interceptors.ts         # 拦截器
│   │   ├── /elderly/               # 老人端 API
│   │   │   ├── health.ts                  # 健康数据 API
│   │   │   ├── reports.ts                 # 报告 API
│   │   │   ├── psychology.ts              # 心理健康 API
│   │   │   └── ai.ts                      # AI API
│   │   ├── /children/              # 子女端 API
│   │   │   ├── elders.ts                  # 老人管理 API
│   │   │   ├── reminders.ts               # 提醒 API
│   │   │   └── monitoring.ts              # 监测 API
│   │   ├── /community/             # 社区端 API
│   │   │   ├── dashboard.ts               # 仪表板 API
│   │   │   ├── map.ts                     # 地图 API
│   │   │   └── alerts.ts                  # 告警 API
│   │   └── /auth/                  # 认证 API
│   │       ├── login.ts                   # 登录
│   │       └── profile.ts                 # 个人信息
│   │
│   ├── /types/                     # 📘 TypeScript 类型（新建）
│   │   ├── /api/                   # API 响应类型
│   │   │   ├── health.types.ts
│   │   │   ├── reports.types.ts
│   │   │   ├── elders.types.ts
│   │   │   └── common.types.ts
│   │   ├── /models/                # 数据模型
│   │   │   ├── User.ts
│   │   │   ├── HealthData.ts
│   │   │   ├── Report.ts
│   │   │   └── Reminder.ts
│   │   └── index.ts                # 类型统一导出
│   │
│   ├── /utils/                     # 🛠️ 工具函数（新建）
│   │   ├── format.ts               # 格式化函数
│   │   ├── validators.ts           # 验证函数
│   │   ├── storage.ts              # 存储工具
│   │   ├── speech.ts               # 语音工具
│   │   └── date.ts                 # 日期工具
│   │
│   ├── /constants/                 # 📌 常量（新建）
│   │   ├── routes.ts               # 路由常量
│   │   ├── api.ts                  # API 端点常量
│   │   ├── colors.ts               # 颜色常量
│   │   └── messages.ts             # 消息常量
│   │
│   ├── /styles/                    # 🎨 样式文件
│   │   ├── globals.css             # 全局样式
│   │   └── tailwind.css            # Tailwind 配置
│   │
│   ├── /assets/                    # 🖼️ 静态资源
│   │   ├── /images/
│   │   ├── /icons/
│   │   └── /fonts/
│   │
│   ├── App.tsx                     # 应用根组件
│   ├── main.tsx                    # 入口文件
│   └── vite-env.d.ts               # Vite 类型声明
│
├── /public/                        # 公共静态文件
│   └── favicon.ico
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

---

## 🔄 重构步骤

### Phase 1: 创建新的目录结构（第1天上午）

**优先级**: P0  
**预计时间**: 2小时

```bash
# 1. 创建新目录
mkdir -p src/pages/{elderly,children,community,auth}
mkdir -p src/components/{common,charts,cards,layout,map,modals}
mkdir -p src/hooks/{api,auth,voice,utils}
mkdir -p src/api/{elderly,children,community,auth}
mkdir -p src/types/{api,models}
mkdir -p src/utils
mkdir -p src/constants
mkdir -p docs/{api,architecture,figma,guides}

# 2. 创建索引文件
touch src/types/index.ts
touch src/constants/index.ts
touch src/utils/index.ts
```

**验收标准**:
- ✅ 所有目录已创建
- ✅ 索引文件已创建
- ✅ 符合标准结构

---

### Phase 2: 创建 API 客户端系统（第1天下午）

**优先级**: P0  
**预计时间**: 3小时

#### 2.1 创建 Axios 客户端实例

**文件**: `src/api/client.ts`

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { setupInterceptors } from './interceptors';
import { API_CONFIG } from './config';

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 设置拦截器
setupInterceptors(apiClient);

// 封装请求方法
export const api = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.get(url, config).then(res => res.data),
  
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.post(url, data, config).then(res => res.data),
  
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.put(url, data, config).then(res => res.data),
  
  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.delete(url, config).then(res => res.data),
  
  patch: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.patch(url, data, config).then(res => res.data),
};

export default apiClient;
```

#### 2.2 创建 API 配置

**文件**: `src/api/config.ts`

```typescript
export const API_CONFIG = {
  // 开发环境
  development: {
    baseURL: 'http://localhost:3000/api/v1',
    timeout: 10000,
  },
  // 生产环境
  production: {
    baseURL: 'https://api.smart-health.com/api/v1',
    timeout: 15000,
  },
  // 当前环境
  get baseURL() {
    return import.meta.env.PROD 
      ? this.production.baseURL 
      : this.development.baseURL;
  },
  get timeout() {
    return import.meta.env.PROD 
      ? this.production.timeout 
      : this.development.timeout;
  },
};

// API 端点常量
export const API_ENDPOINTS = {
  // 老人端
  ELDERLY: {
    HEALTH_TODAY: '/elderly/health/today',
    REPORTS_HISTORY: '/elderly/reports/history',
    REPORTS_CURRENT: '/elderly/reports/current',
    CHARTS_HEARTRATE: '/elderly/health/charts/heartrate',
    CHARTS_SLEEP: '/elderly/health/charts/sleep',
    CHARTS_BLOODPRESSURE: '/elderly/health/charts/bloodpressure',
    CHARTS_RADAR: '/elderly/health/charts/radar',
    PSYCHOLOGY_MOOD: '/elderly/psychology/mood',
    PSYCHOLOGY_MOOD_HISTORY: '/elderly/psychology/mood/history',
    AI_CHAT: '/elderly/ai/chat',
    AI_ANALYZE: '/elderly/ai/analyze',
  },
  // 子女端
  CHILDREN: {
    ELDERS_LIST: '/children/elders/list',
    ELDER_DETAIL: (id: string) => `/children/elders/${id}/detail`,
    REMINDERS_LIST: '/children/reminders/list',
    REMINDERS_CREATE: '/children/reminders/create',
    MONITOR_REALTIME: (id: string) => `/children/monitor/${id}/realtime`,
  },
  // 社区端
  COMMUNITY: {
    DASHBOARD_OVERVIEW: '/community/dashboard/overview',
    DASHBOARD_AGE_DISTRIBUTION: '/community/dashboard/age-distribution',
    DASHBOARD_HEALTH_TRENDS: '/community/dashboard/health-trends',
    MAP_CONFIG: '/community/map/config',
    MAP_LOCATIONS: '/community/map/elders/locations',
    MAP_ALERTS: '/community/map/alerts',
    ALERTS_LIST: '/community/alerts/list',
  },
  // 认证
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    PROFILE: (role: string) => `/${role}/profile`,
  },
};
```

#### 2.3 创建拦截器

**文件**: `src/api/interceptors.ts`

```typescript
import { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { toast } from 'sonner@2.0.3';

export function setupInterceptors(instance: AxiosInstance) {
  // 请求拦截器
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // 添加 token
      const token = localStorage.getItem('authToken');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // 添加用户角色
      const role = localStorage.getItem('userRole');
      if (role && config.headers) {
        config.headers['X-User-Role'] = role;
      }
      
      console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
      return config;
    },
    (error: AxiosError) => {
      console.error('❌ Request Error:', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response) => {
      console.log('✅ API Response:', response.config.url, response.data);
      return response;
    },
    (error: AxiosError) => {
      console.error('❌ Response Error:', error);
      
      // 统一错误处理
      if (error.response) {
        const status = error.response.status;
        const message = (error.response.data as any)?.message || '请求失败';
        
        switch (status) {
          case 401:
            toast.error('未授权，请重新登录');
            // 清除 token 并跳转到登录页
            localStorage.removeItem('authToken');
            window.location.href = '/';
            break;
          case 403:
            toast.error('无权限访问');
            break;
          case 404:
            toast.error('请求的资源不存在');
            break;
          case 500:
            toast.error('服务器错误，请稍后重试');
            break;
          default:
            toast.error(message);
        }
      } else if (error.request) {
        toast.error('网络错误，请检查网络连接');
      } else {
        toast.error('请求配置错误');
      }
      
      return Promise.reject(error);
    }
  );
}
```

#### 2.4 创建具体 API 函数

**文件**: `src/api/elderly/health.ts`

```typescript
import { api } from '../client';
import { API_ENDPOINTS } from '../config';
import { 
  HealthTodayResponse, 
  HeartRateChartResponse,
  SleepAnalysisResponse 
} from '@/types/api/health.types';

/**
 * 老人端 - 健康数据 API
 */
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

  /**
   * 获取睡眠分析数据
   * @param period 时间段 ('week' | 'month')
   */
  getSleepAnalysis: (period: 'week' | 'month' = 'week') => 
    api.get<SleepAnalysisResponse>(
      `${API_ENDPOINTS.ELDERLY.CHARTS_SLEEP}?period=${period}`
    ),
};
```

**验收标准**:
- ✅ API 客户端已创建
- ✅ 拦截器已配置
- ✅ 错误处理已统一
- ✅ 所有 API 函数已封装

---

### Phase 3: 创建自定义 Hooks（第2天上午）

**优先级**: P0  
**预计时间**: 4小时

#### 3.1 创建通用数据获取 Hook

**文件**: `src/hooks/api/useHealthData.ts`

```typescript
import { useState, useEffect } from 'react';
import { elderlyHealthApi } from '@/api/elderly/health';
import { HealthTodayResponse } from '@/types/api/health.types';
import { toast } from 'sonner@2.0.3';

export function useHealthData() {
  const [data, setData] = useState<HealthTodayResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await elderlyHealthApi.getTodayHealth();
      setData(response);
    } catch (err) {
      const error = err as Error;
      setError(error);
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
```

#### 3.2 创建图表数据 Hook

**文件**: `src/hooks/api/useHeartRateChart.ts`

```typescript
import { useState, useEffect } from 'react';
import { elderlyHealthApi } from '@/api/elderly/health';
import { HeartRateChartResponse } from '@/types/api/health.types';

export function useHeartRateChart(period: 'week' | 'month' = 'week') {
  const [data, setData] = useState<HeartRateChartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await elderlyHealthApi.getHeartRateChart(period);
        setData(response);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period]);

  return { data, loading, error };
}
```

#### 3.3 创建语音识别 Hook

**文件**: `src/hooks/voice/useSpeechRecognition.ts`

```typescript
import { useState, useRef, useCallback } from 'react';

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  const startListening = useCallback(() => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('您的浏览器不支持语音识别');
      return;
    }

    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'zh-CN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setTranscript(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, []);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript: () => setTranscript(''),
  };
}
```

**验收标准**:
- ✅ 所有数据获取 Hooks 已创建
- ✅ Loading/Error 状态已处理
- ✅ 语音相关 Hooks 已创建
- ✅ Hooks 可复用

---

### Phase 4: 重构页面组件（第2天下午）

**优先级**: P1  
**预计时间**: 4小时

#### 4.1 重构老人端仪表板

**文件**: `src/pages/elderly/DashboardPage.tsx`

```typescript
import React from 'react';
import { useHealthData } from '@/hooks/api/useHealthData';
import { HealthCardWithAI } from '@/components/cards/HealthCardWithAI';
import { MoodQuickCard } from '@/components/cards/MoodQuickCard';
import { HeartRateChart } from '@/components/charts/HeartRateChart';
import { Activity, Heart, Droplets, Thermometer } from 'lucide-react';

/**
 * 老人端 - 今日健康页面
 * 
 * 职责：
 * 1. 组合所有子组件
 * 2. 管理页面级状态
 * 3. 处理组件间通信
 * 
 * 数据获取：通过 useHealthData Hook
 */
export function DashboardPage() {
  const { data, loading, error, refetch } = useHealthData();

  if (loading) {
    return <div className="p-6">加载中...</div>;
  }

  if (error || !data) {
    return <div className="p-6">加载失败</div>;
  }

  const { vitalSigns, activity, weight } = data.data;

  return (
    <div className="p-6 space-y-6">
      {/* 欢迎区域 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[40px]">
            下午好, {data.data.userName}
          </h2>
          <p className="text-muted-foreground text-[24px]">
            这是你今天的健康监测概览。
          </p>
        </div>
      </div>

      {/* 健康卡片 */}
      <div className="grid gap-4 grid-cols-10">
        {/* 综合指标 */}
        <div className="col-span-4">
          {/* ... */}
        </div>

        {/* 血糖、血压、心率 */}
        <div className="col-span-6 space-y-4">
          <HealthCardWithAI
            icon={Droplets}
            iconColor="text-amber-500"
            value={vitalSigns.bloodSugar.value}
            unit={vitalSigns.bloodSugar.unit}
            title="血糖"
            status={vitalSigns.bloodSugar.status}
            bgGradient="bg-gradient-to-br from-amber-100 to-amber-50"
            borderColor="border-amber-200"
            dataType="血糖"
          />
          {/* ... 其他卡片 */}
        </div>
      </div>

      {/* 心情快速记录 */}
      <MoodQuickCard />

      {/* 图表区域 */}
      <div className="grid gap-4 md:grid-cols-2">
        <HeartRateChart />
        {/* ... 其他图表 */}
      </div>
    </div>
  );
}
```

**验收标准**:
- ✅ 页面组件只负责组合
- ✅ 数据获取使用 Hooks
- ✅ 业务逻辑已抽离
- ✅ 组件可读性高

---

### Phase 5: 移动和整理文件（第3天上午）

**优先级**: P1  
**预计时间**: 3小时

#### 移动计划

```bash
# 1. 移动页面组件
根目录/components/login/* → src/pages/auth/
根目录/components/children/ChildrenDashboard.tsx → src/pages/children/DashboardPage.tsx
根目录/components/community/BigScreenDashboard.tsx → src/pages/community/BigScreenPage.tsx

# 2. 移动复用组件
根目录/components/elderly/HealthCardWithAI.tsx → src/components/cards/
根目录/components/dashboard/MoodQuickCard.tsx → src/components/cards/
根目录/components/dashboard/HealthCharts.tsx → src/components/charts/

# 3. 移动文档
根目录/*.md → docs/对应目录/

# 4. 删除重复文件
删除 根目录/App.tsx (保留 src/App.tsx)
删除 根目录/components/ (保留 src/components/)
删除 根目录/styles/ (保留 src/styles/)
```

**验收标准**:
- ✅ 所有文件已移动到正确位置
- ✅ 导入路径已更新
- ✅ 重复文件已删除
- ✅ 项目可正常运行

---

### Phase 6: 创建类型定义（第3天下午）

**优先级**: P1  
**预计时间**: 2小时

#### 6.1 创建 API 响应类型

**文件**: `src/types/api/health.types.ts`

```typescript
/**
 * 健康数据相关类型定义
 */

// 通用 API 响应
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  timestamp: string;
}

// 今日健康数据
export interface HealthTodayData {
  userId: string;
  userName: string;
  vitalSigns: {
    temperature: {
      value: number;
      unit: string;
      change: number;
      status: 'normal' | 'low' | 'high';
    };
    bloodSugar: {
      value: number;
      unit: string;
      status: string;
      testType: 'fasting' | 'postprandial';
    };
    bloodPressure: {
      systolic: number;
      diastolic: number;
      unit: string;
      status: string;
    };
    heartRate: {
      value: number;
      unit: string;
      change: number;
      status: string;
      variability: string;
    };
  };
  activity: {
    steps: number;
    goal: number;
    percentage: number;
    distance: number;
    calories: number;
  };
  weight: {
    value: number;
    unit: string;
    bmi: number;
    bmiStatus: string;
  };
}

export type HealthTodayResponse = APIResponse<HealthTodayData>;

// 心率图表数据
export interface HeartRateChartData {
  period: 'week' | 'month';
  dataPoints: Array<{
    time: string;
    value: number;
    timestamp: string;
  }>;
  statistics: {
    average: number;
    min: number;
    max: number;
  };
}

export type HeartRateChartResponse = APIResponse<HeartRateChartData>;

// ... 其他类型定义
```

**验收标准**:
- ✅ 所有 API 响应类型已定义
- ✅ 数据模型类型已定义
- ✅ 类型可复用
- ✅ 类型安全

---

## 📊 迁移检查清单

### 文件移动

- [ ] 页面组件移动到 `/src/pages/`
- [ ] 复用组件移动到 `/src/components/`
- [ ] API 函数创建在 `/src/api/`
- [ ] Hooks 创建在 `/src/hooks/`
- [ ] 类型定义在 `/src/types/`
- [ ] 文档移动到 `/docs/`

### 代码重构

- [ ] 所有页面使用 Hooks 获取数据
- [ ] 组件不再直接调用 API
- [ ] 业务逻辑已抽离
- [ ] 类型定义完整
- [ ] 错误处理统一

### 清理工作

- [ ] 删除重复的 App.tsx
- [ ] 删除重复的 components/
- [ ] 删除重复的 styles/
- [ ] 更新所有导入路径
- [ ] 删除未使用的代码

### 测试验证

- [ ] 老人端页面正常运行
- [ ] 子女端页面正常运行
- [ ] 社区端页面正常运行
- [ ] API 调用正常
- [ ] Hooks 工作正常
- [ ] 语音功能正常
- [ ] 无 TypeScript 错误
- [ ] 无控制台错误

---

## ✅ 验收标准

### 目录结构

```bash
✅ 符合标准 React 项目结构
✅ 页面和组件清晰分离
✅ 业务逻辑在 Hooks 中
✅ API 调用统一管理
✅ 类型定义完整
✅ 文档组织清晰
```

### 代码质量

```bash
✅ 组件职责单一
✅ 数据获取与 UI 分离
✅ 可测试性高
✅ 可维护性好
✅ 类型安全
✅ 错误处理统一
```

### 开发体验

```bash
✅ AI 生成代码知道放在哪里
✅ 新功能开发流程清晰
✅ 代码复用率高
✅ 调试容易
✅ 文档完善
```

---

## 📚 参考资料

1. **React 官方文档**: https://react.dev/
2. **Hooks 最佳实践**: https://react.dev/reference/react
3. **TypeScript 指南**: https://www.typescriptlang.org/docs/
4. **Axios 文档**: https://axios-http.com/docs/intro

---

**重构负责人**: React 架构师  
**最后更新**: 2024-12-01  
**状态**: 🚧 进行中
