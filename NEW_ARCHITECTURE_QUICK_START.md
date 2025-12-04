# 新架构快速上手指南

> **目标读者**: 所有开发者（人类和 AI）  
> **预计阅读时间**: 10分钟  
> **更新日期**: 2024-12-01

---

## 🚀 5分钟快速上手

### 步骤 1: 理解新架构

```
你的代码应该放在哪里？
├── 📄 页面组件 → /src/pages/{role}/{PageName}Page.tsx
├── 🧩 复用组件 → /src/components/{category}/{ComponentName}.tsx
├── 🎣 数据逻辑 → /src/hooks/api/use{FeatureName}.ts
├── 🌐 API调用  → /src/api/{role}/{module}.ts
└── 📘 类型定义 → /src/types/api/{module}.types.ts
```

### 步骤 2: 开发新功能的标准流程

#### 示例：添加"血氧监测"功能

**1. 定义 API 函数** (`/src/api/elderly/health.ts`)

```typescript
export const elderlyHealthApi = {
  // ... 现有函数
  
  /**
   * 获取血氧数据
   */
  getOxygenData: () => 
    api.get<OxygenDataResponse>(API_ENDPOINTS.ELDERLY.OXYGEN_DATA),
};
```

**2. 创建 Hook** (`/src/hooks/api/useOxygenData.ts`)

```typescript
export function useOxygenData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    elderlyHealthApi.getOxygenData()
      .then(res => setData(res.data))
      .finally(() => setLoading(false));
  }, []);
  
  return { data, loading };
}
```

**3. 创建组件** (`/src/components/cards/OxygenCard.tsx`)

```typescript
export function OxygenCard({ data }: { data: OxygenData }) {
  return (
    <Card>
      <CardContent>
        <div className="text-6xl font-bold">{data.value}</div>
        <div className="text-xl">%</div>
        <div>血氧</div>
      </CardContent>
    </Card>
  );
}
```

**4. 在页面中使用** (`/src/pages/elderly/DashboardPage.tsx`)

```typescript
export function DashboardPage() {
  const { data, loading } = useOxygenData(); // 使用 Hook
  
  if (loading) return <Loading />;
  
  return (
    <div>
      <OxygenCard data={data} /> {/* 使用组件 */}
    </div>
  );
}
```

✅ **完成！你已经按照新架构添加了一个功能**

---

## 📖 详细指南

### 1. API 客户端使用

#### ✅ 正确做法：使用 api 客户端

```typescript
import { api } from '@/api/client';
import { API_ENDPOINTS } from '@/api/config';

// 类型安全的 API 调用
const response = await api.get<HealthDataResponse>(
  API_ENDPOINTS.ELDERLY.HEALTH_TODAY
);
```

#### ❌ 错误做法：直接使用 fetch

```typescript
// ❌ 不要这样做
const response = await fetch('/api/health');
const data = await response.json();
```

**为什么？**
- ✅ 自动添加 token
- ✅ 统一错误处理
- ✅ 类型安全
- ✅ 自动 Toast 提示

---

### 2. 创建新的 API 函数

#### 模板文件：`/src/api/{role}/{module}.ts`

```typescript
import { api } from '../client';
import { API_ENDPOINTS } from '../config';

/**
 * {角色}端 - {模块}API
 */
export const {role}{Module}Api = {
  /**
   * 获取列表
   */
  getList: () => 
    api.get<ListResponse>(API_ENDPOINTS.{ROLE}.{MODULE}_LIST),
  
  /**
   * 获取详情
   * @param id - 记录ID
   */
  getDetail: (id: string) => 
    api.get<DetailResponse>(API_ENDPOINTS.{ROLE}.{MODULE}_DETAIL(id)),
  
  /**
   * 创建记录
   * @param data - 创建数据
   */
  create: (data: CreatePayload) => 
    api.post<CreateResponse>(API_ENDPOINTS.{ROLE}.{MODULE}_CREATE, data),
  
  /**
   * 更新记录
   * @param id - 记录ID
   * @param data - 更新数据
   */
  update: (id: string, data: UpdatePayload) => 
    api.put<UpdateResponse>(API_ENDPOINTS.{ROLE}.{MODULE}_UPDATE(id), data),
  
  /**
   * 删除记录
   * @param id - 记录ID
   */
  delete: (id: string) => 
    api.delete(API_ENDPOINTS.{ROLE}.{MODULE}_DELETE(id)),
};
```

**命名规范**:
- 文件名：小写 `health.ts`, `reports.ts`
- 导出对象：驼峰 `elderlyHealthApi`, `childrenRemindersApi`
- 函数名：动词+名词 `getList()`, `createReport()`

---

### 3. 创建新的 Hook

#### 模板文件：`/src/hooks/api/use{FeatureName}.ts`

```typescript
import { useState, useEffect } from 'react';
import { {module}Api } from '@/api/{role}/{module}';
import { toast } from 'sonner@2.0.3';

/**
 * Hook: use{FeatureName}
 * 
 * 功能：获取{功能描述}
 * API: GET /api/v1/{endpoint}
 */
export function use{FeatureName}() {
  const [data, setData] = useState<DataType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await {module}Api.getData();
      setData(response.data);
      
    } catch (err) {
      const error = err as Error;
      setError(error);
      toast.error('获取数据失败');
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
    refetch: fetchData,
  };
}
```

**返回值规范**:
```typescript
return {
  data,      // 数据
  loading,   // 加载状态
  error,     // 错误信息
  refetch,   // 刷新函数
};
```

---

### 4. 创建新的页面组件

#### 模板文件：`/src/pages/{role}/{FeatureName}Page.tsx`

```typescript
import React from 'react';
import { use{Feature}Data } from '@/hooks/api/use{Feature}Data';
import { FeatureCard } from '@/components/cards/FeatureCard';

/**
 * {角色}端 - {功能名称}页面
 * 
 * 职责：
 * 1. 组合所有子组件
 * 2. 管理页面级状态
 * 3. 处理组件间通信
 */
export function {Feature}Page() {
  // 1. 使用 Hooks 获取数据
  const { data, loading, error, refetch } = use{Feature}Data();
  
  // 2. 页面级状态
  const [activeTab, setActiveTab] = useState('overview');
  
  // 3. 事件处理
  const handleAction = () => {
    // 处理逻辑
  };
  
  // 4. 条件渲染
  if (loading) return <LoadingScreen />;
  if (error) return <ErrorMessage error={error} onRetry={refetch} />;
  if (!data) return <EmptyState />;
  
  // 5. 组合子组件
  return (
    <div className="p-6 space-y-6">
      <PageHeader title="{功能名称}" />
      <FeatureCard data={data} onAction={handleAction} />
      {/* 更多组件 */}
    </div>
  );
}
```

**页面组件的职责**:
- ✅ 组合子组件
- ✅ 管理页面级状态
- ✅ 处理路由和导航
- ❌ 不直接调用 API
- ❌ 不包含复杂业务逻辑

---

### 5. 创建新的复用组件

#### 模板文件：`/src/components/{category}/{ComponentName}.tsx`

```typescript
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

/**
 * 组件：{ComponentName}
 * 
 * 功能：{组件功能描述}
 * 
 * Props:
 * - data: {数据类型} - {数据描述}
 * - onAction: () => void - {回调描述}
 */

interface {ComponentName}Props {
  data: DataType;
  onAction?: () => void;
}

export function {ComponentName}({ 
  data, 
  onAction 
}: {ComponentName}Props) {
  // 只包含 UI 逻辑
  const handleClick = () => {
    onAction?.();
  };
  
  return (
    <Card>
      <CardContent>
        <div>{data.value}</div>
        <Button onClick={handleClick}>操作</Button>
      </CardContent>
    </Card>
  );
}
```

**复用组件的职责**:
- ✅ 展示 UI
- ✅ 处理用户交互（通过回调）
- ✅ 通过 Props 接收数据
- ❌ 不直接调用 API
- ❌ 不包含业务逻辑

---

## 🎯 最佳实践

### 1. 数据流向

```
API 端点
  ↓
API 函数 (src/api/)
  ↓
Hook (src/hooks/)
  ↓
页面组件 (src/pages/)
  ↓
复用组件 (src/components/)
```

### 2. 导入路径别名

使用 `@/` 别名导入：

```typescript
// ✅ 正确
import { api } from '@/api/client';
import { useHealthData } from '@/hooks/api/useHealthData';
import { HealthCard } from '@/components/cards/HealthCard';

// ❌ 错误
import { api } from '../../api/client';
import { useHealthData } from '../../../hooks/api/useHealthData';
```

### 3. 类型定义位置

```typescript
// ✅ 共享类型 → /src/types/
export interface HealthData {
  // ...
}

// ✅ 组件 Props → 组件文件内
interface HealthCardProps {
  data: HealthData;
}
```

### 4. 错误处理

```typescript
// ✅ Hook 中处理错误
export function useHealthData() {
  const [error, setError] = useState<Error | null>(null);
  
  try {
    // ...
  } catch (err) {
    setError(err as Error);
    toast.error('获取数据失败'); // 统一提示
  }
  
  return { data, loading, error };
}

// ✅ 组件中显示错误
export function DashboardPage() {
  const { data, loading, error } = useHealthData();
  
  if (error) {
    return <ErrorMessage error={error} onRetry={refetch} />;
  }
  
  // ...
}
```

### 5. Loading 状态

```typescript
// ✅ Hook 中管理 loading
export function useHealthData() {
  const [loading, setLoading] = useState(true);
  
  try {
    setLoading(true);
    // ...
  } finally {
    setLoading(false);
  }
  
  return { data, loading };
}

// ✅ 组件中显示 loading
export function DashboardPage() {
  const { data, loading } = useHealthData();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  // ...
}
```

---

## 🛠️ 常见问题

### Q1: 我应该在哪里调用 API？

**A**: 永远不要在组件中直接调用 API。使用 Hook。

```typescript
// ❌ 错误
export function MyComponent() {
  useEffect(() => {
    fetch('/api/data').then(/* ... */);
  }, []);
}

// ✅ 正确
export function MyComponent() {
  const { data } = useMyData(); // 使用 Hook
}
```

### Q2: 我的组件需要业务逻辑怎么办？

**A**: 业务逻辑放在 Hook 中，组件只负责展示。

```typescript
// ❌ 错误 - 组件中有业务逻辑
export function MyComponent() {
  const processData = (raw: RawData) => {
    // 复杂的处理逻辑...
    return processed;
  };
}

// ✅ 正确 - 业务逻辑在 Hook 中
export function useProcessedData() {
  const { data } = useRawData();
  
  const processed = useMemo(() => {
    // 复杂的处理逻辑...
    return result;
  }, [data]);
  
  return processed;
}
```

### Q3: 什么时候创建新的 Hook？

**A**: 当你需要复用数据获取逻辑时。

**应该创建 Hook**:
- 多个页面需要相同数据
- 需要管理复杂状态
- 需要订阅实时数据

**不需要创建 Hook**:
- 只有一个组件使用
- 简单的状态管理（用 useState）
- 纯 UI 逻辑

### Q4: 组件放在哪个目录？

**A**: 根据功能分类：

```
/src/components/
├── ui/        → 基础UI组件（Button, Card, Input）
├── common/    → 通用业务组件（VoiceButton, AIButton）
├── charts/    → 图表组件（HeartRateChart, SleepChart）
├── cards/     → 卡片组件（HealthCard, MoodCard）
├── layout/    → 布局组件（Header, Navbar）
├── map/       → 地图组件（CommunityMap, Marker）
└── modals/    → 弹窗组件（Dialog, Alert）
```

### Q5: 如何处理表单提交？

**A**: 使用 mutation Hook。

```typescript
// src/hooks/api/useSubmitMood.ts
export function useSubmitMood() {
  const [loading, setLoading] = useState(false);
  
  const submit = async (data: MoodData) => {
    setLoading(true);
    try {
      await psychologyApi.submitMood(data);
      toast.success('提交成功！');
    } catch (err) {
      toast.error('提交失败');
    } finally {
      setLoading(false);
    }
  };
  
  return { submit, loading };
}

// 在组件中使用
export function MoodForm() {
  const { submit, loading } = useSubmitMood();
  
  const handleSubmit = (data: MoodData) => {
    submit(data);
  };
  
  return <Form onSubmit={handleSubmit} loading={loading} />;
}
```

---

## 📚 完整示例

### 示例：添加"用药提醒"功能（完整流程）

#### 1. 添加 API 端点常量

```typescript
// src/api/config.ts
export const API_ENDPOINTS = {
  // ...
  ELDERLY: {
    // ...
    MEDICATION_LIST: '/elderly/medication/list',
    MEDICATION_CREATE: '/elderly/medication/create',
  },
};
```

#### 2. 创建 API 函数

```typescript
// src/api/elderly/medication.ts
import { api } from '../client';
import { API_ENDPOINTS } from '../config';

export const elderlyMedicationApi = {
  getList: () => 
    api.get<MedicationListResponse>(API_ENDPOINTS.ELDERLY.MEDICATION_LIST),
  
  create: (data: CreateMedicationPayload) => 
    api.post<CreateMedicationResponse>(
      API_ENDPOINTS.ELDERLY.MEDICATION_CREATE, 
      data
    ),
};
```

#### 3. 创建类型定义

```typescript
// src/types/api/medication.types.ts
export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  nextTime: string;
}

export interface MedicationListResponse {
  success: boolean;
  data: {
    medications: Medication[];
  };
}

export interface CreateMedicationPayload {
  name: string;
  dosage: string;
  frequency: string;
  startTime: string;
}
```

#### 4. 创建 Hooks

```typescript
// src/hooks/api/useMedicationList.ts
export function useMedicationList() {
  const [data, setData] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    elderlyMedicationApi.getList()
      .then(res => setData(res.data.medications))
      .finally(() => setLoading(false));
  }, []);
  
  return { data, loading };
}

// src/hooks/api/useCreateMedication.ts
export function useCreateMedication() {
  const [loading, setLoading] = useState(false);
  
  const create = async (data: CreateMedicationPayload) => {
    setLoading(true);
    try {
      await elderlyMedicationApi.create(data);
      toast.success('添加成功！');
      return true;
    } catch (err) {
      toast.error('添加失败');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  return { create, loading };
}
```

#### 5. 创建复用组件

```typescript
// src/components/cards/MedicationCard.tsx
export function MedicationCard({ data }: { data: Medication }) {
  return (
    <Card>
      <CardContent>
        <h3>{data.name}</h3>
        <p>剂量：{data.dosage}</p>
        <p>频率：{data.frequency}</p>
        <p>下次：{data.nextTime}</p>
      </CardContent>
    </Card>
  );
}
```

#### 6. 创建页面组件

```typescript
// src/pages/elderly/MedicationPage.tsx
export function MedicationPage() {
  const { data, loading } = useMedicationList();
  const { create, loading: creating } = useCreateMedication();
  
  if (loading) return <Loading />;
  
  return (
    <div className="p-6 space-y-6">
      <h1>用药提醒</h1>
      
      <div className="grid gap-4">
        {data.map(med => (
          <MedicationCard key={med.id} data={med} />
        ))}
      </div>
      
      <Button onClick={() => /* 打开创建弹窗 */}>
        添加用药
      </Button>
    </div>
  );
}
```

✅ **完成！用药提醒功能开发完毕**

---

## 🎓 下一步学习

1. **阅读详细规范**: `/PROJECT_STRUCTURE_STANDARD.md`
2. **查看重构计划**: `/ARCHITECTURE_REFACTOR_PLAN.md`
3. **查看进度报告**: `/REFACTOR_STATUS_REPORT.md`
4. **研究示例代码**:
   - API: `/src/api/elderly/health.ts`
   - Hook: `/src/hooks/api/useHealthData.ts`
   - 语音: `/src/hooks/voice/useSpeechRecognition.ts`

---

## 💡 记住这些原则

### ✅ DO（应该做）

- 在 Hook 中调用 API
- 使用类型定义
- 统一错误处理
- 组件职责单一
- 代码可复用

### ❌ DON'T（不应该做）

- 在组件中直接调用 API
- 使用 any 类型
- 每个组件自己处理错误
- 一个组件做太多事情
- 重复写相同代码

---

**最后更新**: 2024-12-01  
**维护者**: React 架构师  
**状态**: ✅ 正式生效
