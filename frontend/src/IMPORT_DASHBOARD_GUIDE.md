# 🎯 导入数据大屏并替换社区可视化组件指南

## 📝 背景说明

您要从另一个 Figma Make 项目导入"智慧健康养老系统大屏"，并替换当前社区端的数据可视化组件。

---

## 🚀 方法一：在 Figma Make 中导入（最简单）

### 步骤 1：导入 Figma 设计

1. **在当前 Figma Make 项目中**，点击左侧或顶部的 **"Import from Figma"** 按钮
2. **粘贴您的 Figma 链接**：
   ```
   https://www.figma.com/make/03EJRBuzHCf4VTW7EGcOsF/智慧健康养老系统大屏
   ```
3. **选择要导入的 Frame**（通常是整个大屏页面）
4. **点击 "Import"** 按钮

### 步骤 2：查看生成的代码

导入后，Figma Make 会在 `/imports` 目录下生成文件，例如：

```
/imports/DashboardScreen.tsx
/imports/HealthDataScreen.tsx
/imports/svg-xxxxx
```

### 步骤 3：复制代码给我

**请执行以下操作：**

1. 找到生成的主组件文件（通常在 `/imports` 目录）
2. 打开该文件，复制代码
3. 粘贴给我，告诉我：
   - 文件名是什么
   - 代码内容
4. 我会帮您整合到社区端

---

## 🔧 方法二：手动替换（如果无法导入）

### 步骤 1：创建新的数据大屏组件

我已经为您准备了一个模板，您可以根据大屏设计调整：

```typescript
// /components/community/DataVisualizationNew.tsx

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function DataVisualizationNew() {
  // 这里放您从 Figma 大屏导入的数据结构
  
  return (
    <div className="min-h-screen bg-[#0a0e27] text-white p-8">
      {/* 大屏标题 */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold mb-2">智慧健康养老系统大屏</h1>
        <p className="text-2xl text-gray-400">实时数据监控中心</p>
      </div>

      {/* 您的大屏内容将在这里 */}
      <div className="grid grid-cols-3 gap-6">
        {/* 左侧区域 */}
        <div className="col-span-1 space-y-6">
          {/* 放置左侧的图表组件 */}
        </div>

        {/* 中间区域 */}
        <div className="col-span-1 space-y-6">
          {/* 放置中间的主要数据展示 */}
        </div>

        {/* 右侧区域 */}
        <div className="col-span-1 space-y-6">
          {/* 放置右侧的图表组件 */}
        </div>
      </div>
    </div>
  );
}
```

### 步骤 2：在社区端中替换

打开 `/components/community/CommunityDashboard.tsx`，找到导入语句：

```typescript
// 原来的导入
import { DataVisualization } from './DataVisualization';

// 改为新的导入
import { DataVisualizationNew } from './DataVisualizationNew';
```

然后在渲染部分替换：

```typescript
// 原来的代码
{activeTab === 'visualization' && <DataVisualization />}

// 改为
{activeTab === 'visualization' && <DataVisualizationNew />}
```

---

## 🎨 典型大屏布局结构

根据常见的数据大屏设计，我为您准备了一个更完整的模板：

```typescript
// /components/community/BigScreenDashboard.tsx

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

export function BigScreenDashboard() {
  const [currentTime, setCurrentTime] = useState(new Date());

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 模拟数据（您需要根据大屏设计调整）
  const summaryData = [
    { label: '总人数', value: '5,280', unit: '人', color: 'from-blue-500 to-blue-700' },
    { label: '健康人数', value: '4,856', unit: '人', color: 'from-green-500 to-green-700' },
    { label: '预警人数', value: '358', unit: '人', color: 'from-yellow-500 to-yellow-700' },
    { label: '异常人数', value: '66', unit: '人', color: 'from-red-500 to-red-700' },
  ];

  const healthTrendData = [
    { month: '1月', value: 4520 },
    { month: '2月', value: 4680 },
    { month: '3月', value: 4820 },
    { month: '4月', value: 4950 },
    { month: '5月', value: 5100 },
    { month: '6月', value: 5280 },
  ];

  const ageDistributionData = [
    { age: '60-65', value: 1580, percent: 30 },
    { age: '66-70', value: 1850, percent: 35 },
    { age: '71-75', value: 1108, percent: 21 },
    { age: '76-80', value: 528, percent: 10 },
    { age: '80+', value: 214, percent: 4 },
  ];

  const deviceStatusData = [
    { name: '在线', value: 4856, color: '#22c55e' },
    { name: '离线', value: 358, color: '#94a3b8' },
    { name: '故障', value: 66, color: '#ef4444' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e27] via-[#1a1f3a] to-[#0a0e27] text-white">
      {/* 大屏头部 */}
      <div className="relative h-32 bg-gradient-to-r from-blue-900/50 via-purple-900/50 to-blue-900/50 backdrop-blur-sm border-b border-blue-500/30">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDU5LDEzMCwyNDYsMC4xKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20"></div>
        
        <div className="relative h-full flex items-center justify-between px-12">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-3xl">🏥</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                智慧健康养老系统大屏
              </h1>
              <p className="text-lg text-blue-300 mt-1">Real-time Health Monitoring Dashboard</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-300">
              {currentTime.toLocaleTimeString('zh-CN')}
            </div>
            <div className="text-lg text-gray-400 mt-1">
              {currentTime.toLocaleDateString('zh-CN', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="p-8">
        {/* 顶部数据卡片 */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {summaryData.map((item, index) => (
            <div 
              key={index}
              className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${item.color} p-6 shadow-2xl transform hover:scale-105 transition-all duration-300`}
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
              <div className="relative">
                <div className="text-lg text-white/80 mb-2">{item.label}</div>
                <div className="text-5xl font-bold mb-1">{item.value}</div>
                <div className="text-base text-white/70">{item.unit}</div>
              </div>
            </div>
          ))}
        </div>

        {/* 主要图表区域 - 三列布局 */}
        <div className="grid grid-cols-3 gap-6">
          {/* 左侧列 */}
          <div className="space-y-6">
            {/* 健康趋势图 */}
            <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 backdrop-blur-sm rounded-2xl p-6 border border-blue-500/30 shadow-xl">
              <h3 className="text-2xl font-bold mb-4 text-blue-300">📈 健康人数趋势</h3>
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={healthTrendData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="month" stroke="#94a3b8" style={{ fontSize: '14px' }} />
                  <YAxis stroke="#94a3b8" style={{ fontSize: '14px' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                      border: '1px solid rgba(59, 130, 246, 0.5)',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }} 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fill="url(#colorValue)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* 年龄分布图 */}
            <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/20 backdrop-blur-sm rounded-2xl p-6 border border-purple-500/30 shadow-xl">
              <h3 className="text-2xl font-bold mb-4 text-purple-300">👥 年龄分布</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={ageDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="age" stroke="#94a3b8" style={{ fontSize: '14px' }} />
                  <YAxis stroke="#94a3b8" style={{ fontSize: '14px' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                      border: '1px solid rgba(168, 85, 247, 0.5)',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }} 
                  />
                  <Bar dataKey="value" fill="#a855f7" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 中间列 */}
          <div className="space-y-6">
            {/* 设备状态分布 */}
            <div className="bg-gradient-to-br from-green-900/40 to-green-800/20 backdrop-blur-sm rounded-2xl p-6 border border-green-500/30 shadow-xl">
              <h3 className="text-2xl font-bold mb-4 text-green-300">🖥️ 设备状态分布</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={deviceStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {deviceStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                      border: '1px solid rgba(34, 197, 94, 0.5)',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
              
              {/* 设备状态列表 */}
              <div className="mt-6 space-y-3">
                {deviceStatusData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: item.color }}></div>
                      <span className="text-lg">{item.name}</span>
                    </div>
                    <span className="text-xl font-bold">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 右侧列 */}
          <div className="space-y-6">
            {/* 实时告警列表 */}
            <div className="bg-gradient-to-br from-red-900/40 to-red-800/20 backdrop-blur-sm rounded-2xl p-6 border border-red-500/30 shadow-xl">
              <h3 className="text-2xl font-bold mb-4 text-red-300">⚠️ 实时告警</h3>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {[
                  { time: '14:25', name: '张三', type: '血压异常', level: 'high' },
                  { time: '14:18', name: '李四', type: '心率过快', level: 'medium' },
                  { time: '14:05', name: '王五', type: '血糖偏高', level: 'medium' },
                  { time: '13:52', name: '赵六', type: '体温异常', level: 'high' },
                  { time: '13:30', name: '孙七', type: '血氧偏低', level: 'low' },
                ].map((alert, index) => (
                  <div 
                    key={index}
                    className={`p-4 rounded-lg border-l-4 ${
                      alert.level === 'high' 
                        ? 'bg-red-900/30 border-red-500' 
                        : alert.level === 'medium'
                        ? 'bg-yellow-900/30 border-yellow-500'
                        : 'bg-blue-900/30 border-blue-500'
                    } animate-pulse`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-lg">{alert.name}</span>
                      <span className="text-sm text-gray-400">{alert.time}</span>
                    </div>
                    <div className="text-base text-gray-300">{alert.type}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## 🔄 完整替换步骤

### 1. 创建新组件文件

将上面的 `BigScreenDashboard.tsx` 保存为：
```
/components/community/BigScreenDashboard.tsx
```

### 2. 修改 CommunityDashboard.tsx

```typescript
// 在文件顶部添加导入
import { BigScreenDashboard } from './BigScreenDashboard';

// 在渲染部分替换
{activeTab === 'visualization' && <BigScreenDashboard />}
```

### 3. 测试效果

保存文件后，切换到社区端，点击"数据可视化"标签，查看新的大屏效果。

---

## 🎨 自定义大屏样式

如果您从 Figma 导入了特定的设计，可以调整以下部分：

### 1. 配色方案
```typescript
// 深色背景
bg-[#0a0e27]  // 主背景色
bg-[#1a1f3a]  // 次要背景色

// 渐变色
from-blue-500 to-blue-700   // 蓝色卡片
from-green-500 to-green-700 // 绿色卡片
```

### 2. 布局结构
```typescript
// 三列布局
grid grid-cols-3 gap-6

// 四列布局（顶部卡片）
grid grid-cols-4 gap-6
```

### 3. 图表颜色
```typescript
// 修改图表的颜色以匹配您的设计
fill="#3b82f6"  // 蓝色
fill="#a855f7"  // 紫色
fill="#22c55e"  // 绿色
```

---

## 📞 需要我帮助的地方

完成 Figma 导入后，请告诉我：

1. ✅ **生成的文件名** - 例如 `/imports/HealthScreen.tsx`
2. ✅ **代码片段** - 复制导入的组件代码
3. ✅ **设计截图** - 如果可以，提供大屏的截图
4. ✅ **特殊需求** - 需要保留哪些元素，修改哪些部分

我会帮您：
- 整合导入的代码
- 调整样式以匹配现有系统
- 确保数据流和交互正常
- 优化性能和响应式布局

---

## 🚀 快速测试命令

创建新组件后，运行：

```bash
npm run dev
```

然后：
1. 登录选择"社区端"
2. 点击"数据可视化"标签
3. 查看新的大屏效果

---

准备好后，请分享导入的代码，我会立即帮您整合！🎉
