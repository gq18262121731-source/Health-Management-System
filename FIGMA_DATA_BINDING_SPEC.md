# Figma 数据绑定规范文档

> **文档版本**: v1.0  
> **更新时间**: 2024-12-01  
> **适用范围**: 智慧健康管理系统（老人端、子女端、社区端）

---

## 📋 目录

1. [Figma 注释规范](#figma-注释规范)
2. [老人端组件数据绑定](#老人端组件数据绑定)
3. [子女端组件数据绑定](#子女端组件数据绑定)
4. [社区端组件数据绑定](#社区端组件数据绑定)
5. [共享组件数据绑定](#共享组件数据绑定)
6. [数据模型定义](#数据模型定义)
7. [Figma 实操指南](#figma-实操指南)

---

## 📌 Figma 注释规范

### 在 Figma 中添加数据绑定注释的方法

#### 方法 1: 使用注释层 (Comment Layer)
```
1. 选中需要标注的组件
2. 在右侧属性面板找到 "Layer" 名称
3. 在组件名称后添加 [DATA] 标记
4. 在 Description 中添加数据绑定说明

示例：
Layer 名称: HealthCard [DATA]
Description: 
  数据源: GET /api/v1/elderly/health/today
  字段: { systolic, diastolic, heartRate }
  刷新: 页面加载时
```

#### 方法 2: 使用 Figma Comments (推荐)
```
1. 按 C 键进入评论模式
2. 点击组件添加评论
3. 使用统一的注释格式（见下方模板）
```

#### 方法 3: 创建 Dev Mode 注释
```
1. 进入 Dev Mode (Shift + D)
2. 选中组件
3. 在 "Add description" 中添加数据绑定说明
```

### 统一注释模板

```markdown
📊 数据绑定
API: [METHOD] [API_PATH]
数据模型: [ModelName]
必需字段: field1, field2, field3
可选字段: field4, field5

🔄 交互动作
- 点击: [触发动作]
- 加载: [加载时机]
- 刷新: [刷新策略]

💡 备注
[其他说明]
```

---

## 🏥 老人端组件数据绑定

### 1. 今日健康数据卡片组

#### 1.1 综合指标卡片 (Comprehensive Indicators)

**Figma 组件路径**: `老人端 / 今日健康 / 综合指标卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/today
数据模型: HealthTodayModel
必需字段: 
  - temperature: number (体温, °C)
  - steps: number (步数)
  - stepsGoal: number (步数目标)
  - weight: number (体重, kg)
  - bmi: number (BMI)
  - bmiStatus: string (BMI状态: "正常" | "偏瘦" | "偏胖")
  - temperatureChange: number (体温变化)

🔄 交互动作
- 加载: 页面加载时自动获取
- 刷新: 下拉刷新 / 每5分钟自动刷新
- 点击: 无

💡 备注
- 温度变化用箭头表示：↑ 升高 / ↓ 降低
- 步数进度条显示百分比：steps / stepsGoal * 100
- BMI 状态颜色：正常=蓝色，偏瘦=橙色，偏胖=红色
```

**TypeScript 接口**:
```typescript
interface ComprehensiveIndicators {
  temperature: number;
  temperatureChange: number;
  temperatureUnit: string;
  steps: number;
  stepsGoal: number;
  stepsPercentage: number;
  weight: number;
  weightUnit: string;
  bmi: number;
  bmiStatus: 'normal' | 'underweight' | 'overweight';
}
```

---

#### 1.2 血糖卡片 (Blood Sugar Card)

**Figma 组件路径**: `老人端 / 今日健康 / 血糖卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/today
数据模型: HealthTodayModel.vitalSigns.bloodSugar
必需字段:
  - value: number (血糖值)
  - unit: string (单位: "mmol/L")
  - status: string (状态: "正常" | "偏低" | "偏高")
  - testType: string (测试类型: "空腹" | "餐后")

🔄 交互动作
- 加载: 页面加载时自动获取
- 点击AI分析按钮: 
  → 打开悬浮AI助手
  → 自动发送分析prompt: "请分析我的血糖数据：{value} {unit}，测试类型：{testType}"
- 点击卡片: 跳转到详细趋势图

💡 备注
- 状态颜色：正常=绿色，偏低=橙色，偏高=红色
- AI分析按钮位于右上角
- 适老化：字体超大，数值 text-6xl
```

**TypeScript 接口**:
```typescript
interface BloodSugarCard {
  value: number;
  unit: string;
  status: 'normal' | 'low' | 'high';
  statusText: string;
  testType: 'fasting' | 'postprandial';
  testTypeText: string;
}
```

---

#### 1.3 血压卡片 (Blood Pressure Card)

**Figma 组件路径**: `老人端 / 今日健康 / 血压卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/today
数据模型: HealthTodayModel.vitalSigns.bloodPressure
必需字段:
  - systolic: number (收缩压)
  - diastolic: number (舒张压)
  - unit: string (单位: "mmHg")
  - status: string (状态: "正常" | "偏低" | "偏高")

🔄 交互动作
- 加载: 页面加载时自动获取
- 点击AI分析按钮: 
  → 打开悬浮AI助手
  → 自动发送分析prompt: "请分析我的血压数据：{systolic}/{diastolic} {unit}"
- 点击卡片: 跳转到血压趋势图

💡 备注
- 显示格式：{systolic}/{diastolic}
- 状态判断：正常范围 90-140 / 60-90
- 卡片背景：蓝色渐变 from-blue-100 to-blue-50
```

**TypeScript 接口**:
```typescript
interface BloodPressureCard {
  systolic: number;
  diastolic: number;
  unit: string;
  status: 'normal' | 'low' | 'high';
  statusText: string;
  displayValue: string; // "118/75"
}
```

---

#### 1.4 心率卡片 (Heart Rate Card)

**Figma 组件路径**: `老人端 / 今日健康 / 心率卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/today
数据模型: HealthTodayModel.vitalSigns.heartRate
必需字段:
  - value: number (心率值)
  - unit: string (单位: "bpm")
  - change: number (较昨日变化)
  - status: string (状态: "正常" | "偏低" | "偏高")
  - variability: string (心率变异性: "good" | "fair" | "poor")

🔄 交互动作
- 加载: 页面加载时自动获取
- 点击AI分析按钮: 
  → 打开悬浮AI助手
  → 自动发送分析prompt: "请分析我的心率数据：{value} {unit}，较昨日变化 {change}"
- 点击卡片: 跳转到心率趋势图

💡 备注
- 变化显示：+2bpm (绿色) / -2bpm (橙色)
- 卡片背景：玫瑰色渐变 from-rose-100 to-rose-50
- Icon: Heart (lucide-react)
```

**TypeScript 接口**:
```typescript
interface HeartRateCard {
  value: number;
  unit: string;
  change: number;
  changeText: string; // "+2bpm"
  status: 'normal' | 'low' | 'high';
  statusText: string;
  variability: 'good' | 'fair' | 'poor';
}
```

---

### 2. 快速心情记录卡片 (Mood Quick Card)

**Figma 组件路径**: `老人端 / 今日健康 / 快速心情记录`

**数据绑定注释**:
```markdown
📊 数据绑定
API: POST /api/v1/elderly/psychology/mood (提交时)
数据模型: MoodQuickRecord
必需字段:
  - mood: string (心情: "excellent" | "good" | "normal" | "bad")
  - timestamp: string (记录时间, ISO 8601)
可选字段:
  - note: string (简短备注)

🔄 交互动作
- 点击心情图标: 
  → 切换选中状态
  → 更新显示的心情文案和图标
- 点击"详细记录"按钮:
  → 跳转到心理健康页面 (activeTab = 'psychology')
  → 传递当前选中的心情值
  → 语音播报："正在跳转到心理健康页面"

💡 备注
- 默认选中：good (愉快)
- 心情选项：很好❤️、愉快😊、一般😐、低落😔
- 适老化：图标超大 h-12 w-12，可点击区域大
```

**TypeScript 接口**:
```typescript
interface MoodQuickCard {
  selectedMood: 'excellent' | 'good' | 'normal' | 'bad';
  moodOptions: Array<{
    value: string;
    label: string;
    icon: LucideIcon;
    color: string;
    bg: string;
  }>;
}

interface MoodSubmitPayload {
  mood: 'excellent' | 'good' | 'normal' | 'bad';
  note?: string;
  timestamp: string;
}
```

---

### 3. 健康趋势图表

#### 3.1 心率趋势图 (Heart Rate Chart)

**Figma 组件路径**: `老人端 / 今日健康 / 图表区 / 心率趋势图`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/charts/heartrate?period=week
数据模型: HeartRateChartModel
必需字段:
  - period: string (时间段: "week" | "month")
  - dataPoints: Array<{
      time: string (时间: "周一" | "11-20")
      value: number (心率值)
      timestamp: string (完整时间戳)
    }>
  - average: number (平均心率)
  - min: number (最低心率)
  - max: number (最高心率)

🔄 交互动作
- 加载: 页面加载时自动获取
- 切换时间段: 
  → 点击"周" / "月"切换按钮
  → 调用 API 重新获取数据
  → URL参数变化: ?period=week 或 ?period=month
- Hover数据点: 显示Tooltip (时间 + 心率值)
- 点击AI分析按钮:
  → 打开AI助手
  → prompt: "请分析我最近{period}的心率趋势"

💡 备注
- 使用 recharts 的 LineChart
- Y轴范围：60-100 bpm
- 数据点颜色：玫瑰色 #f43f5e
- 正常范围参考线：60-100 (浅灰色虚线)
```

**TypeScript 接口**:
```typescript
interface HeartRateChartData {
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
```

---

#### 3.2 睡眠分析图 (Sleep Analysis Chart)

**Figma 组件路径**: `老人端 / 今日健康 / 图表区 / 睡眠分析图`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/health/charts/sleep?period=week
数据模型: SleepAnalysisChartModel
必需字段:
  - period: string (时间段: "week" | "month")
  - dataPoints: Array<{
      day: string (日期: "周一")
      deepSleep: number (深睡时长, 小时)
      lightSleep: number (浅睡时长, 小时)
      total: number (总睡眠时长)
    }>
  - averageDeepSleep: number (平均深睡)
  - averageTotalSleep: number (平均总睡眠)

🔄 交互动作
- 加载: 页面加载时自动获取
- 切换时间段: 点击"周" / "月"
- Hover数据柱: 显示Tooltip (日期 + 深睡 + 浅睡)
- 点击AI分析按钮:
  → prompt: "请分析我最近{period}的睡眠质量"

💡 备注
- 使用 recharts 的 BarChart (堆叠柱状图)
- 深睡颜色：靛蓝色 #6366f1
- 浅睡颜色：天蓝色 #38bdf8
- 推荐睡眠参考线：7-9小时 (虚线)
```

**TypeScript 接口**:
```typescript
interface SleepAnalysisChartData {
  period: 'week' | 'month';
  dataPoints: Array<{
    day: string;
    deepSleep: number;
    lightSleep: number;
    total: number;
  }>;
  statistics: {
    averageDeepSleep: number;
    averageTotalSleep: number;
    sleepQuality: 'good' | 'fair' | 'poor';
  };
}
```

---

### 4. 历史报告列表 (Historical Reports)

**Figma 组件路径**: `老人端 / 历史报告 / 报告列表`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/reports/history?page=1&pageSize=10
数据模型: ReportsListModel
必需字段:
  - total: number (总数)
  - page: number (当前页码)
  - pageSize: number (每页数量)
  - reports: Array<{
      reportId: string (报告ID)
      date: string (报告日期)
      type: string (类型: "每日报告" | "每周报告" | "月度报告")
      healthScore: number (健康评分 0-100)
      riskLevel: string (风险等级: "low" | "medium" | "high")
      summary: string (摘要)
    }>

🔄 交互动作
- 加载: 进入"历史报告"页面时加载
- 点击"查看详情"按钮:
  → 跳转到报告详情页面
  → URL: /report/:reportId
  → 传递报告ID
- 点击"下载PDF"按钮:
  → 调用 GET /api/v1/elderly/reports/{reportId}/pdf
  → 下载PDF文件
  → 语音播报："正在下载报告"
- 翻页:
  → 点击页码
  → 调用API，参数 page 变化
- 筛选:
  → 选择报告类型
  → 调用API，添加 type 参数

💡 备注
- 每行显示1个报告卡片
- 健康评分颜色：>80绿色，60-80黄色，<60红色
- 风险等级图标：low=✓，medium=!，high=⚠
- 适老化：卡片高度充足 py-6，字体大
```

**TypeScript 接口**:
```typescript
interface ReportsList {
  total: number;
  page: number;
  pageSize: number;
  reports: Array<{
    reportId: string;
    date: string;
    type: 'daily' | 'weekly' | 'monthly';
    typeText: string;
    healthScore: number;
    riskLevel: 'low' | 'medium' | 'high';
    riskLevelText: string;
    summary: string;
  }>;
}
```

---

### 5. 心理健康页面 (Psychology Page)

#### 5.1 心情记录表单 (Mood Record Form)

**Figma 组件路径**: `老人端 / 心理健康 / 心情记录`

**数据绑定注释**:
```markdown
📊 数据绑定
API: POST /api/v1/elderly/psychology/mood
数据模型: MoodRecordModel
必需字段:
  - mood: string ("excellent" | "good" | "normal" | "bad")
  - timestamp: string (记录时间, ISO 8601)
可选字段:
  - note: string (详细备注, 最多200字)
  - activities: Array<string> (今日活动)
  - sleepQuality: number (昨晚睡眠质量 1-5)

🔄 交互动作
- 选择心情:
  → 点击四个心情图标之一
  → 更新选中状态和颜色
- 输入备注:
  → 文本框输入
  → 旁边有"语音输入"按钮 (Mic图标)
  → 点击语音按钮启动语音识别
- 点击"提交"按钮:
  → 验证必填字段
  → 调用 POST API
  → 成功后显示 Toast："心情记录成功！"
  → 语音播报："您的心情已记录"
  → 清空表单

💡 备注
- 语音输入按钮：h-14 w-14，右侧浮动
- 备注框：min-h-32，支持多行
- 提交按钮：超大 h-16，全宽
```

**TypeScript 接口**:
```typescript
interface MoodRecordForm {
  mood: 'excellent' | 'good' | 'normal' | 'bad';
  note?: string;
  activities?: string[];
  sleepQuality?: number;
  timestamp: string;
}

interface MoodRecordResponse {
  success: boolean;
  data: {
    moodId: string;
    message: string;
  };
}
```

---

#### 5.2 心情趋势图 (Mood Trend Chart)

**Figma 组件路径**: `老人端 / 心理健康 / 心情趋势图`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/elderly/psychology/mood/history?period=month
数据模型: MoodTrendChartModel
必需字段:
  - period: string ("week" | "month")
  - dataPoints: Array<{
      date: string (日期)
      moodScore: number (心情分数 1-4)
      moodType: string (心情类型)
    }>
  - positivePercentage: number (积极情绪占比)
  - negativePercentage: number (消极情绪占比)

🔄 交互动作
- 加载: 进入心理健康页面时加载
- 切换时间段: 点击"周" / "月"
- Hover数据点: 显示当天心情和备注
- 点击数据点: 展开当天的详细记录

💡 备注
- Y轴映射：1=低落，2=一般，3=愉快，4=很好
- 颜色渐变：低落=灰色，一般=黄色，愉快=绿色，很好=粉色
```

**TypeScript 接口**:
```typescript
interface MoodTrendChartData {
  period: 'week' | 'month';
  dataPoints: Array<{
    date: string;
    moodScore: number;
    moodType: 'excellent' | 'good' | 'normal' | 'bad';
    note?: string;
  }>;
  statistics: {
    positivePercentage: number;
    neutralPercentage: number;
    negativePercentage: number;
  };
}
```

---

### 6. AI咨询组件 (AI Consultation)

**Figma 组件路径**: `老人端 / AI健康助手 / 对话界面`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - POST /api/v1/elderly/ai/chat (发送消息)
  - POST /api/v1/elderly/ai/analyze (触发分析)
  - GET /api/v1/elderly/ai/history (获取历史)

数据模型: AIChatModel
必需字段:
  - messages: Array<{
      id: string
      type: "user" | "ai"
      content: string
      timestamp: string
    }>
  - healthSummary: string (健康状态摘要)

🔄 交互动作
- 发送消息:
  → 输入框输入文本
  → 点击"发送"按钮 或 按Enter键
  → 调用 POST /api/v1/elderly/ai/chat
  → 将用户消息添加到对话列表
  → 等待AI响应并添加到列表
  → 自动滚动到底部
  → 语音播报AI回复

- 语音输入:
  → 点击麦克风按钮
  → 启动语音识别
  → 识别文本自动填入输入框
  → 按钮变为红色闪烁状态
  → 识别完成后自动停止

- 快速问题:
  → 点击预设问题按钮
  → 自动填入问题并发送
  → 预设问题："为什么会这样？"、"我可以做什么？"、"需要去医院吗？"

- 播报健康摘要:
  → 点击"听你念一遍"按钮
  → 语音播报健康状态摘要
  → 播报时按钮文字变为"停止播报"

💡 备注
- 消息气泡：用户=蓝色右对齐，AI=灰色左对齐
- 输入框高度：h-14，带语音按钮 w-14
- 快速问题：3个按钮横排，hover有颜色变化
- 自动语音播报：AI回复后自动播放
- 对话历史：无限滚动，最多显示50条
```

**TypeScript 接口**:
```typescript
interface AIChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: string;
}

interface AIChatRequest {
  message: string;
  context?: {
    healthData?: object;
    recentReports?: object[];
  };
}

interface AIChatResponse {
  success: boolean;
  data: {
    messageId: string;
    aiResponse: string;
    suggestions?: string[];
    timestamp: string;
  };
}
```

---

## 👨‍👩‍👧 子女端组件数据绑定

### 1. 老人列表 (Elderly List)

**Figma 组件路径**: `子女端 / 老人列表 / 列表卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/children/elders/list
数据模型: ElderlyListModel
必需字段:
  - total: number (关联老人总数)
  - elders: Array<{
      elderId: string
      elderName: string
      age: number
      relationship: string (关系: "父亲" | "母亲" | "爷爷" | "奶奶")
      avatar: string (头像URL)
      healthStatus: string ("normal" | "warning" | "danger")
      latestVitalSigns: {
        temperature: number
        bloodPressure: { systolic: number, diastolic: number }
        heartRate: number
        bloodSugar: number
      }
      alerts: Array<string> (告警信息)
      lastUpdate: string (最后更新时间)
    }>

🔄 交互动作
- 加载: 进入子女端首页时加载
- 自动刷新: 每30秒刷新一次列表
- 点击卡片:
  → 跳转到老人详情页面
  → 传递 elderId
  → URL: /elderly/:elderId/detail

- 状态颜色映射:
  → normal: 绿色边框 + 绿色✓图标
  → warning: 黄色边框 + 黄色!图标
  → danger: 红色边框 + 红色⚠图标

💡 备注
- 卡片布局：grid grid-cols-1 md:grid-cols-2 gap-6
- 健康指标：4个小卡片横排展示
- 告警区域：红色背景，最多显示3条
- hover效果：阴影加深 + 轻微上移
```

**TypeScript 接口**:
```typescript
interface ElderlyListItem {
  elderId: string;
  elderName: string;
  age: number;
  relationship: string;
  avatar?: string;
  healthStatus: 'normal' | 'warning' | 'danger';
  latestVitalSigns: {
    temperature: number;
    bloodPressure: {
      systolic: number;
      diastolic: number;
    };
    heartRate: number;
    bloodSugar: number;
  };
  alerts: string[];
  lastUpdate: string;
}

interface ElderlyList {
  total: number;
  elders: ElderlyListItem[];
}
```

---

### 2. 老人详情页面 (Elderly Detail)

**Figma 组件路径**: `子女端 / 老人详情 / 详情页面`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/children/elders/{elderId}/detail (基础信息)
  - GET /api/v1/children/monitor/{elderId}/realtime (实时监测)

数据模型: ElderlyDetailModel
必需字段:
  - elderId: string
  - elderName: string
  - age: number
  - relationship: string
  - contact: string (紧急联系人)
  - address: string (居住地址)
  - healthStatus: string
  - vitalSigns: {
      temperature: number
      bloodPressure: { systolic, diastolic }
      heartRate: number
      bloodSugar: number
      spo2: number (血氧)
    }
  - todayActivity: {
      steps: number
      distance: number (km)
      calories: number
    }
  - recentReports: Array<Report> (最近3份报告)
  - medications: Array<{
      name: string
      dosage: string
      frequency: string
      nextTime: string
    }>

🔄 交互动作
- 加载: 
  → 获取基础信息 (一次性)
  → 启动实时监测 (每10秒轮询)

- 点击"返回列表":
  → 返回老人列表页面
  → 停止实时监测轮询

- 点击报告卡片:
  → 查看该老人的报告详情
  → URL: /elderly/:elderId/report/:reportId

- 点击"设置提醒":
  → 打开提醒设置弹窗
  → 选择提醒类型（吃药、运动、测量等）
  → 调用 POST /api/v1/children/reminders/create

💡 备注
- 顶部：老人基本信息 + 头像
- 中部：实时生命体征（4个大卡片）
- 底部：今日活动 + 用药提醒 + 最近报告
- 实时数据标记：右上角有"实时"闪烁图标
```

**TypeScript 接口**:
```typescript
interface ElderlyDetail {
  elderId: string;
  elderName: string;
  age: number;
  relationship: string;
  contact: string;
  address: string;
  healthStatus: 'normal' | 'warning' | 'danger';
  vitalSigns: {
    temperature: number;
    bloodPressure: {
      systolic: number;
      diastolic: number;
    };
    heartRate: number;
    bloodSugar: number;
    spo2: number;
  };
  todayActivity: {
    steps: number;
    distance: number;
    calories: number;
  };
  recentReports: Array<{
    reportId: string;
    date: string;
    type: string;
    healthScore: number;
  }>;
  medications: Array<{
    medicationId: string;
    name: string;
    dosage: string;
    frequency: string;
    nextTime: string;
  }>;
}
```

---

### 3. 智能提醒 (Smart Reminders)

**Figma 组件路径**: `子女端 / 智能提醒 / 提醒列表`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/children/reminders/list (获取列表)
  - POST /api/v1/children/reminders/create (创建提醒)
  - PUT /api/v1/children/reminders/{reminderId}/status (标记状态)
  - DELETE /api/v1/children/reminders/{reminderId} (删除提醒)

数据模型: RemindersListModel
必需字段:
  - total: number
  - unread: number (未读数量)
  - reminders: Array<{
      reminderId: string
      elderlyId: string
      elderlyName: string
      type: string ("health_alert" | "medication" | "appointment" | "exercise")
      priority: string ("high" | "medium" | "low")
      title: string
      description: string
      timestamp: string
      status: string ("unread" | "read" | "handled")
    }>

🔄 交互动作
- 加载: 进入提醒页面时加载
- 筛选:
  → 按类型筛选（全部、健康告警、用药、复诊、运动）
  → 按优先级筛选（全部、高、中、低）
  → 按状态筛选（全部、未读、已读、已处理）

- 点击"标记已读":
  → 调用 PUT API，status = "read"
  → 卡片颜色变淡
  → 未读数量 -1

- 点击"标记已处理":
  → 调用 PUT API，status = "handled"
  → 卡片添加 ✓ 标记
  → 可选：移动到"已处理"列表

- 点击"删除":
  → 弹出确认对话框
  → 调用 DELETE API
  → 从列表中移除

- 点击"新建提醒":
  → 打开创建提醒弹窗
  → 选择老人、类型、时间等
  → 调用 POST API

💡 备注
- 优先级颜色：high=红色，medium=黄色，low=蓝色
- 类型图标：health_alert=Activity，medication=Pill，appointment=Clock，exercise=TrendingUp
- 列表排序：优先级高 > 时间新
- 未读提醒：左侧有红点标记
```

**TypeScript 接口**:
```typescript
interface Reminder {
  reminderId: string;
  elderlyId: string;
  elderlyName: string;
  type: 'health_alert' | 'medication' | 'appointment' | 'exercise';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  timestamp: string;
  status: 'unread' | 'read' | 'handled';
}

interface RemindersList {
  total: number;
  unread: number;
  reminders: Reminder[];
}

interface CreateReminderPayload {
  elderlyId: string;
  type: string;
  title: string;
  description?: string;
  scheduledTime: string;
  repeatPattern?: 'daily' | 'weekly' | 'monthly' | 'once';
}
```

---

## 🏘️ 社区端组件数据绑定

### 1. 大屏统计卡片 (Dashboard Stats Cards)

**Figma 组件路径**: `社区端 / 大屏 / 顶部统计卡片`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/community/dashboard/overview
数据模型: CommunityOverviewModel
必需字段:
  - totalElderly: number (社区老人总数)
  - elderlyChange: number (较上月变化)
  - monitoringCount: number (健康监测人数)
  - monitoringRate: number (监测覆盖率 %)
  - alertsCount: number (当前告警数)
  - urgentAlerts: number (紧急告警数)
  - devicesCount: number (设备总数)
  - devicesOnline: number (在线设备数)
  - devicesOnlineRate: number (设备在线率 %)

🔄 交互动作
- 加载: 页面加载时获取
- 自动刷新: 每30秒刷新一次
- 数字动画: 
  → 使用 AnimatedNumber 组件
  → 从0到目标值缓动动画 (2秒)
  → easeOutQuart 缓动函数

- 点击卡片:
  → 跳转到对应的详细页面
  → 总人数 → 人员管理
  → 监测人数 → 设备管理
  → 告警数 → 告警管理
  → 设备数 → 设备状态

💡 备注
- 卡片布局：grid grid-cols-4 gap-6
- 渐变背景：每个卡片不同颜色
- Icon尺寸：h-12 w-12
- 数值字体：text-5xl font-bold
- 变化值：绿色上升箭头，红色下降箭头
```

**TypeScript 接口**:
```typescript
interface CommunityOverview {
  totalElderly: number;
  elderlyChange: number;
  monitoringCount: number;
  monitoringRate: number;
  alertsCount: number;
  urgentAlerts: number;
  devicesCount: number;
  devicesOnline: number;
  devicesOnlineRate: number;
}

interface StatCard {
  icon: LucideIcon;
  label: string;
  value: number;
  unit: string;
  change?: string;
  changeLabel?: string;
  color: string; // gradient class
}
```

---

### 2. 年龄分布饼图 (Age Distribution Chart)

**Figma 组件路径**: `社区端 / 大屏 / 左侧图表 / 年龄分布`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/community/dashboard/age-distribution
数据模型: AgeDistributionModel
必需字段:
  - ageGroups: Array<{
      name: string (年龄段: "60-70岁" | "70-80岁" | "80-90岁" | "90岁以上")
      value: number (人数)
      percentage: number (占比 %)
    }>
  - totalCount: number (总人数)

🔄 交互动作
- 加载: 页面加载时获取
- Hover扇区: 
  → 显示 Tooltip
  → 内容：{name}: {value}人 ({percentage}%)
  → 扇区放大效果

- 点击扇区:
  → 跳转到该年龄段的人员列表
  → URL: /community/elderly?ageGroup={name}

💡 备注
- 使用 recharts 的 PieChart
- 颜色方案：
  → 60-70岁: #10b981 (绿色)
  → 70-80岁: #3b82f6 (蓝色)
  → 80-90岁: #f59e0b (橙色)
  → 90岁以上: #ef4444 (红色)
- 图例位置：右侧
- 饼图尺寸：响应式，最小 200px
```

**TypeScript 接口**:
```typescript
interface AgeDistribution {
  ageGroups: Array<{
    name: string;
    value: number;
    percentage: number;
    color: string;
  }>;
  totalCount: number;
}
```

---

### 3. 健康趋势折线图 (Health Trends Chart)

**Figma 组件路径**: `社区端 / 大屏 / 右侧图表 / 健康趋势`

**数据绑定注释**:
```markdown
📊 数据绑定
API: GET /api/v1/community/dashboard/health-trends?period=week
数据模型: HealthTrendsModel
必需字段:
  - period: string ("week" | "month")
  - dataPoints: Array<{
      date: string (日期: "周一" | "11-20")
      normalCount: number (正常人数)
      warningCount: number (预警人数)
      dangerCount: number (高危人数)
    }>
  - totalPopulation: number (总人口基数)

🔄 交互动作
- 加载: 页面加载时获取
- 切换周期: 
  → 点击"周" / "月"切换按钮
  → 调用 API，period 参数变化
  → 图表数据平滑过渡

- Hover数据点:
  → 显示 Tooltip
  → 内容：日期 + 各状态人数
  → 数据点高亮

💡 备注
- 使用 recharts 的 LineChart，3条线
- 颜色：
  → normalCount: #10b981 (绿色)
  → warningCount: #f59e0b (橙色)
  → dangerCount: #ef4444 (红色)
- Y轴：人数
- X轴：日期
- 网格线：浅灰色虚线
```

**TypeScript 接口**:
```typescript
interface HealthTrends {
  period: 'week' | 'month';
  dataPoints: Array<{
    date: string;
    normalCount: number;
    warningCount: number;
    dangerCount: number;
  }>;
  totalPopulation: number;
}
```

---

### 4. 2D数字孪生地图 (Community Map 2D)

**Figma 组件路径**: `社区端 / 大屏 / 中央地图`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/community/map/config (地图配置)
  - GET /api/v1/community/map/elders/locations (老人位置)
  - GET /api/v1/community/map/alerts (实时告警)

数据模型: CommunityMapModel
必需字段:
  - mapConfig: {
      buildings: Array<{
        id: number
        name: string (楼栋名: "1号楼")
        x: number (SVG坐标)
        y: number (SVG坐标)
        width: number
        height: number
        floors: number (楼层数)
      }>
    }
  - elderLocations: Array<{
      elderId: string
      elderName: string
      buildingId: number
      floor: number
      room: string
      healthStatus: string ("normal" | "warning" | "danger")
      hasAlert: boolean
    }>
  - alerts: Array<{
      alertId: string
      elderId: string
      buildingId: number
      type: string
      severity: string ("low" | "medium" | "high")
      timestamp: string
    }>

🔄 交互动作
- 加载:
  → 获取地图配置 (一次性)
  → 获取老人位置 (每10秒刷新)
  → 获取告警信息 (每5秒刷新)

- Hover楼栋:
  → 显示楼栋信息面板
  → 内容：楼栋名、总人数、告警数
  → 楼栋高亮（描边加粗）

- 点击楼栋:
  → 展开楼栋详情弹窗
  → 显示该楼所有居民列表
  → 显示健康状态分布
  → 可点击居民查看详情

- 告警闪烁:
  → 有告警的楼栋：红色脉冲动画
  → 告警标记：楼顶显示 ⚠ 图标
  → 点击告警图标：跳转到告警详情

💡 备注
- SVG 地图尺寸：1200x800
- 楼栋颜色：
  → normal: 绿色 #10b981
  → warning: 黄色 #f59e0b
  → danger: 红色 #ef4444
- 动画：CSS animation pulse
- 缩放：支持鼠标滚轮缩放
```

**TypeScript 接口**:
```typescript
interface Building {
  id: number;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  floors: number;
  elderCount?: number;
  alertCount?: number;
}

interface ElderLocation {
  elderId: string;
  elderName: string;
  buildingId: number;
  floor: number;
  room: string;
  healthStatus: 'normal' | 'warning' | 'danger';
  hasAlert: boolean;
}

interface MapAlert {
  alertId: string;
  elderId: string;
  elderName: string;
  buildingId: number;
  type: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

interface CommunityMapData {
  mapConfig: {
    buildings: Building[];
  };
  elderLocations: ElderLocation[];
  alerts: MapAlert[];
}
```

---

### 5. 告警管理列表 (Alert Management)

**Figma 组件路径**: `社区端 / 告警管理 / 告警列表`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/community/alerts/list (获取告警列表)
  - PUT /api/v1/community/alerts/{alertId}/handle (处理告警)
  - GET /api/v1/community/alerts/statistics (告警统计)

数据模型: AlertsListModel
必需字段:
  - total: number
  - unhandled: number (未处理数量)
  - alerts: Array<{
      alertId: string
      elderId: string
      elderName: string
      buildingName: string
      room: string
      type: string ("heart_rate" | "blood_pressure" | "fall" | "sos")
      severity: string ("low" | "medium" | "high")
      message: string
      timestamp: string
      status: string ("pending" | "handling" | "resolved")
      handler: string (处理人)
      handleTime: string (处理时间)
    }>

🔄 交互动作
- 加载: 进入告警管理页面时加载
- 实时推送: 
  → WebSocket 连接
  → 新告警自动添加到列表顶部
  → 播放告警音效
  → 浏览器通知

- 筛选:
  → 按状态：全部、待处理、处理中、已解决
  → 按严重程度：全部、高、中、低
  → 按类型：全部、心率、血压、跌倒、SOS

- 点击"处理":
  → 打开处理弹窗
  → 填写处理说明
  → 调用 PUT API，status = "handling"
  → 记录处理人和时间

- 点击"查看详情":
  → 跳转到该老人的详细页面
  → URL: /community/elderly/:elderId/detail

💡 备注
- 列表排序：高危 > 中危 > 低危 > 时间倒序
- 严重程度颜色：high=红色背景，medium=黄色背景，low=蓝色背景
- 未处理告警：左侧红色竖条
- 告警类型图标：heart_rate=Heart，blood_pressure=Activity，fall=AlertTriangle，sos=Bell
```

**TypeScript 接口**:
```typescript
interface Alert {
  alertId: string;
  elderId: string;
  elderName: string;
  buildingName: string;
  room: string;
  type: 'heart_rate' | 'blood_pressure' | 'fall' | 'sos';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: string;
  status: 'pending' | 'handling' | 'resolved';
  handler?: string;
  handleTime?: string;
  handleNote?: string;
}

interface AlertsList {
  total: number;
  unhandled: number;
  alerts: Alert[];
}

interface HandleAlertPayload {
  alertId: string;
  handler: string;
  handleNote: string;
  status: 'handling' | 'resolved';
}
```

---

## 🔧 共享组件数据绑定

### 1. 统一导航栏 (Unified Navbar)

**Figma 组件路径**: `共享组件 / UnifiedNavbar`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/{role}/profile (获取用户信息)
  - GET /api/v1/{role}/notifications/unread (未读通知数)

数据模型: NavbarModel
必需字段:
  - userName: string (用户名)
  - userRole: string ("elderly" | "children" | "community")
  - avatar: string (头像URL)
  - unreadCount: number (未读通知数)

🔄 交互动作
- 加载: 登录后自动获取用户信息
- 轮询: 每30秒获取未读通知数
- 点击菜单项:
  → 切换 activeTab 状态
  → 更新面包屑导航
  → 语音播报菜单名称（仅老人端）

- 点击"退出登录":
  → 弹出确认对话框
  → 清除 localStorage
  → 停止所有轮询
  → 跳转到登录页面

💡 备注
- 老人端：超大按钮 h-16，大图标
- 子女端/社区端：标准尺寸 h-12
- Logo: 左侧固定
- 菜单：中间
- 退出：右侧
```

**TypeScript 接口**:
```typescript
interface NavbarData {
  userName: string;
  userRole: 'elderly' | 'children' | 'community';
  avatar?: string;
  unreadCount: number;
}
```

---

### 2. 个人信息页面 (My Info)

**Figma 组件路径**: `共享组件 / MyInfo`

**数据绑定注释**:
```markdown
📊 数据绑定
API: 
  - GET /api/v1/{role}/profile (获取个人信息)
  - PUT /api/v1/{role}/profile (更新个人信息)
  - POST /api/v1/{role}/avatar/upload (上传头像)

数据模型: UserProfileModel
必需字段:
  - userId: string
  - userName: string
  - role: string
  - phone: string
  - email: string
  - address: string
可选字段:
  - avatar: string
  - birthday: string
  - gender: string
  - emergencyContact: string

🔄 交互动作
- 加载: 进入个人信息页面时获取
- 编辑模式:
  → 点击"编辑"按钮
  → 输入框变为可编辑状态
  → 显示"保存" / "取消"按钮

- 保存:
  → 验证必填字段
  → 调用 PUT API
  → 成功后显示 Toast："保存成功！"
  → 退出编辑模式

- 上传头像:
  → 点击头像区域
  → 打开文件选择器
  → 选择图片后预览
  → 调用 POST API 上传
  → 更新头像显示

💡 备注
- 表单布局：2列 grid
- 输入框：老人端超大 h-14，其他端标准 h-10
- 头像尺寸：老人端 128px，其他端 96px
```

**TypeScript 接口**:
```typescript
interface UserProfile {
  userId: string;
  userName: string;
  role: 'elderly' | 'children' | 'community';
  phone: string;
  email?: string;
  address?: string;
  avatar?: string;
  birthday?: string;
  gender?: 'male' | 'female';
  emergencyContact?: string;
}

interface UpdateProfilePayload {
  userName?: string;
  phone?: string;
  email?: string;
  address?: string;
  birthday?: string;
  gender?: 'male' | 'female';
  emergencyContact?: string;
}
```

---

## 📖 数据模型定义

### 通用数据类型

```typescript
// 健康状态
type HealthStatus = 'normal' | 'warning' | 'danger';

// 用户角色
type UserRole = 'elderly' | 'children' | 'community';

// 告警级别
type AlertSeverity = 'low' | 'medium' | 'high';

// 时间段
type TimePeriod = 'day' | 'week' | 'month' | 'year';

// 心情类型
type MoodType = 'excellent' | 'good' | 'normal' | 'bad';

// 报告类型
type ReportType = 'daily' | 'weekly' | 'monthly';

// API 响应格式
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  timestamp: string;
}
```

---

## 🎨 Figma 实操指南

### Step 1: 创建数据绑定注释层

1. **打开 Figma 文件**
2. **选择页面**：例如 `老人端 / 今日健康`
3. **创建注释 Frame**：
   ```
   - 按 F 创建 Frame
   - 命名：📊 数据绑定说明
   - 设置为固定位置（右上角）
   - 背景色：浅黄色 #fef3c7
   - 宽度：400px
   ```

4. **添加文本内容**：
   ```
   使用上面提供的注释模板
   复制粘贴对应组件的数据绑定说明
   ```

### Step 2: 为组件添加 Dev Mode 注释

1. **进入 Dev Mode**：`Shift + D`
2. **选择组件**：例如 `血糖卡片`
3. **添加描述**：
   ```
   点击右侧 "Add description"
   粘贴数据绑定注释
   ```

4. **添加链接**：
   ```
   点击 "Add link"
   链接到 API 文档对应章节
   ```

### Step 3: 使用 Figma Comments

1. **按 C 键**进入评论模式
2. **点击组件**位置
3. **添加评论**：
   ```
   @开发团队
   
   📊 数据绑定
   API: GET /api/v1/elderly/health/today
   字段: bloodSugar { value, unit, status }
   
   详见文档：FIGMA_DATA_BINDING_SPEC.md
   ```

4. **@提及相关人员**确保通知到位

### Step 4: 创建变量和样式

1. **创建颜色变量**：
   ```
   - Colors / Status / Normal: #10b981
   - Colors / Status / Warning: #f59e0b
   - Colors / Status / Danger: #ef4444
   ```

2. **创建文本样式**：
   ```
   - Elderly / Value / Large: 60px, Bold
   - Elderly / Label / Medium: 32px, Regular
   - Children / Value / Medium: 36px, Bold
   ```

3. **绑定到组件**：
   ```
   选择文本 → 右侧面板 → Text properties → 选择样式
   ```

### Step 5: 组织图层命名

使用统一的命名规范：
```
✅ 好的命名：
- HealthCard-BloodSugar [DATA]
- Chart-HeartRate [DATA]
- Button-AIAnalysis [ACTION]

❌ 不好的命名：
- Rectangle 1
- Group 23
- Frame 456
```

### Step 6: 创建组件变体

为不同状态创建变体：
```
组件: HealthStatusCard
变体:
  - Status: Normal | Warning | Danger
  - Size: Large (老人端) | Medium (子女端) | Small (社区端)
```

### Step 7: 使用 Auto Layout

确保所有卡片都使用 Auto Layout：
```
1. 选择 Frame
2. 按 Shift + A 启用 Auto Layout
3. 设置间距、padding、对齐方式
4. 设置 Resizing：
   - 水平：Fill container
   - 垂直：Hug contents
```

### Step 8: 导出标注

1. **使用 Figma Inspect**：
   ```
   - 进入 Dev Mode
   - 选择组件
   - 查看右侧 Inspect 面板
   - 复制 CSS / React 代码
   ```

2. **导出切图**：
   ```
   - 选择需要导出的元素
   - 右下角 Export
   - 选择格式：SVG (图标) / PNG (图片)
   - 导出到 /figma_exports 文件夹
   ```

---

## 📋 检查清单

使用此清单确保所有组件都已正确标注：

### 老人端
- [ ] 综合指标卡片 - 数据绑定 ✓
- [ ] 血糖卡片 - 数据绑定 + 交互动作 ✓
- [ ] 血压卡片 - 数据绑定 + 交互动作 ✓
- [ ] 心率卡片 - 数据绑定 + 交互动作 ✓
- [ ] 快速心情记录 - 数据绑定 + 交互动作 ✓
- [ ] 心率趋势图 - 数据绑定 + 图表配置 ✓
- [ ] 睡眠分析图 - 数据绑定 + 图表配置 ✓
- [ ] 历史报告列表 - 数据绑定 + 分页逻辑 ✓
- [ ] 心理健康表单 - 数据绑定 + 表单验证 ✓
- [ ] AI咨询界面 - 数据绑定 + 实时交互 ✓

### 子女端
- [ ] 老人列表 - 数据绑定 + 状态映射 ✓
- [ ] 老人详情 - 数据绑定 + 实时监测 ✓
- [ ] 智能提醒 - 数据绑定 + CRUD操作 ✓

### 社区端
- [ ] 统计卡片 - 数据绑定 + 动画效果 ✓
- [ ] 年龄分布图 - 数据绑定 + 图表配置 ✓
- [ ] 健康趋势图 - 数据绑定 + 图表配置 ✓
- [ ] 2D地图 - 数据绑定 + 实时刷新 ✓
- [ ] 告警列表 - 数据绑定 + 实时推送 ✓

### 共享组件
- [ ] 导航栏 - 数据绑定 + 状态管理 ✓
- [ ] 个人信息 - 数据绑定 + 表单验证 ✓

---

## 🚀 快速参考

### 常用 API 路径模板

```typescript
// 老人端
GET /api/v1/elderly/health/today
GET /api/v1/elderly/health/charts/{type}?period={period}
GET /api/v1/elderly/reports/history
POST /api/v1/elderly/psychology/mood
POST /api/v1/elderly/ai/chat

// 子女端
GET /api/v1/children/elders/list
GET /api/v1/children/elders/{elderId}/detail
GET /api/v1/children/reminders/list
POST /api/v1/children/reminders/create

// 社区端
GET /api/v1/community/dashboard/overview
GET /api/v1/community/map/elders/locations
GET /api/v1/community/alerts/list
PUT /api/v1/community/alerts/{alertId}/handle
```

### 常用颜色变量

```css
/* 健康状态 */
--status-normal: #10b981;
--status-warning: #f59e0b;
--status-danger: #ef4444;

/* 主题色 */
--primary: #0d9488;
--secondary: #06b6d4;
--background: #f0fdf4;

/* 文本 */
--text-primary: #0f172a;
--text-secondary: #64748b;
--text-muted: #94a3b8;
```

### 常用字体大小（适老化）

```css
/* 老人端 */
--elderly-title: 40px;
--elderly-value: 60px;
--elderly-label: 32px;
--elderly-body: 24px;
--elderly-button: 24px;

/* 子女端/社区端 */
--standard-title: 24px;
--standard-value: 36px;
--standard-label: 18px;
--standard-body: 16px;
--standard-button: 16px;
```

---

## 📞 支持与反馈

### 遇到问题？

1. **查看 API 文档**：`/API_DOCUMENTATION.md`
2. **查看组件映射**：`/COMPONENT_API_MAPPING.md`
3. **查看代码示例**：对应的 `.tsx` 文件中的 TODO 注释

### 文档更新

- **维护者**：前端开发团队
- **最后更新**：2024-12-01
- **版本**：v1.0

---

**恭喜！🎉 现在您可以在 Figma 中为所有组件添加完整的数据绑定说明了！**
