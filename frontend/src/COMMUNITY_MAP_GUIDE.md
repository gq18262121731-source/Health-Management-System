# 🗺️ 社区2D数字孪生地图使用指南

## 🎯 快速定位

**文件位置：** `/components/community/bigscreen/CommunityMap2D.tsx`  
**在大屏中的位置：** 底部完整宽度（700px高度）

---

## 📊 功能概览

### 核心特性
- ✅ 社区航拍图展示
- ✅ 10栋建筑交互热区
- ✅ 悬停/点击显示详情
- ✅ 实时预警标记
- ✅ 健康率统计
- ✅ 百分比响应式布局

---

## 🏢 建筑布局

```
┌─────────────────────────────────────────────┐
│  1号楼   2号楼   3号楼            4号楼      │ ← 顶部一排
│                                             │
│  5号楼           6号楼            7号楼      │ ← 中间一排
│                                             │
│  8号楼   9号楼   10号楼                      │ ← 底部一排
└─────────────────────────────────────────────┘
```

### 建筑数据

| 楼栋 | 位置 | 入住人数 | 预警 | 健康率 |
|------|------|----------|------|--------|
| 1号楼 | 左上 | 87人 | 0 | 100% |
| 2号楼 | 中上 | 92人 | 1 | 99% |
| 3号楼 | 右上 | 105人 | 0 | 100% |
| 4号楼 | 右上角 | 98人 | 2 | 98% |
| 5号楼 | 左中 | 112人 | 0 | 100% |
| 6号楼 | 中中 | 88人 | 0 | 100% |
| 7号楼 | 右中 | 96人 | 0 | 100% |
| 8号楼 | 左下 | 89人 | 0 | 100% |
| 9号楼 | 中下 | 94人 | 0 | 100% |
| 10号楼 | 右下 | 78人 | 0 | 100% |

**总计：** 10栋建筑，939人，3个预警

---

## 🎨 交互状态

### 1️⃣ 正常状态（默认）
- **边框：** 绿色虚线
- **填充：** 透明
- **标签：** 左上角显示楼号
- **预警：** 无标记

### 2️⃣ 预警状态
- **边框：** 黄色虚线
- **标记：** 右上角黄色圆形脉冲标记
- **数字：** 预警数量显示在标记中
- **动画：** 标记脉冲 + 光圈扩散

**示例：**
- 2号楼：1个预警
- 4号楼：2个预警

### 3️⃣ 悬停状态
- **边框：** 发光边框
- **填充：** 半透明绿色/黄色
- **弹窗：** 中心显示详情卡片
  - 建筑名称
  - 入住人数
  - 预警数量（如有）
- **动画：** 脉冲边框效果

### 4️⃣ 选中状态
- **边框：** 实线发光边框
- **填充：** 半透明高亮
- **详情：** 底部展开详细信息卡片
  - 建筑名称
  - 建筑类型
  - 入住人数
  - 健康率

---

## 🛠️ 自定义配置

### 修改建筑数据

**文件位置：** CommunityMap2D.tsx 第23-39行

```typescript
const buildings: Building[] = [
  { 
    id: 1,                    // 建筑ID（唯一）
    name: '1号楼',            // 建筑名称
    x: '8%',                  // 横向位置（百分比）
    y: '13%',                 // 纵向位置（百分比）
    width: '20%',             // 宽度（百分比）
    height: '20%',            // 高度（百分比）
    elderCount: 87,           // 入住老人数量
    alertCount: 0,            // 预警数量（0表示无预警）
    healthyRate: 100,         // 健康率（百分比）
    type: 'residential'       // 建筑类型
  },
  // ... 其他9栋楼
];
```

### 建筑类型说明

```typescript
type: 'residential'  // 住宅楼（绿色）
type: 'activity'     // 活动中心（青绿色）
type: 'medical'      // 医疗楼（青色）
type: 'service'      // 服务中心（默认绿色）
```

### 更换航拍图

**文件位置：** CommunityMap2D.tsx 第2行

```typescript
// 当前路径（Figma Make环境）
import communityImageLabeled from 'figma:asset/a6a8584d81114e37a33568db3546c0c6d4e54027.png';

// 如果在本地环境，改为：
import communityImageLabeled from '/images/community-aerial.png';
```

**步骤：**
1. 准备新的社区航拍图（建议尺寸：1920x1080）
2. 保存到 `/public/images/` 目录
3. 修改导入路径
4. 调整 `buildings` 数组中的坐标以匹配新图片

---

## 📐 坐标定位技巧

### 百分比坐标系统

```
 0%                    50%                    100%
  ├──────────────────────┼──────────────────────┤  0%
  │                      │                      │
  │                      │                      │
  │                      │                      │
  ├──────────────────────┼──────────────────────┤  50%
  │                      │                      │
  │                      │                      │
  │                      │                      │
  ├──────────────────────┼──────────────────────┤  100%
```

### 定位步骤

1. **使用图片编辑软件**（如Photoshop、Figma）打开航拍图
2. **绘制矩形框**在每栋楼的位置
3. **记录坐标**：
   - `x` = 左边距离 ÷ 总宽度 × 100%
   - `y` = 顶边距离 ÷ 总高度 × 100%
   - `width` = 矩形宽度 ÷ 总宽度 × 100%
   - `height` = 矩形高度 ÷ 总高度 × 100%
4. **填入数组**

### 示例计算

假设航拍图宽度 = 1920px，高度 = 1080px

**1号楼矩形框：**
- 左边距：154px → x = 154/1920 × 100% ≈ 8%
- 顶边距：140px → y = 140/1080 × 100% ≈ 13%
- 宽度：384px → width = 384/1920 × 100% = 20%
- 高度：216px → height = 216/1080 × 100% = 20%

---

## 🎨 颜色配置

### 建筑颜色函数

**文件位置：** CommunityMap2D.tsx 第41-55行

```typescript
const getColor = (building: Building) => {
  if (building.alertCount > 2) return 'rgba(245, 158, 11, 0.7)'; // 橙色-紧急
  if (building.alertCount > 0) return 'rgba(251, 191, 36, 0.7)'; // 黄色-预警
  
  switch (building.type) {
    case 'residential':
      return 'rgba(16, 185, 129, 0.6)'; // 绿色-住宅
    case 'activity':
      return 'rgba(20, 184, 166, 0.6)'; // 青绿色-活动
    case 'medical':
      return 'rgba(6, 182, 212, 0.6)'; // 青色-医疗
    default:
      return 'rgba(16, 185, 129, 0.6)';
  }
};
```

### 边框颜色函数

**文件位置：** CommunityMap2D.tsx 第57-70行

```typescript
const getBorderColor = (building: Building) => {
  if (building.alertCount > 0) return '#fbbf24'; // 黄色-有预警
  
  switch (building.type) {
    case 'residential': return '#10b981'; // 绿色
    case 'activity': return '#14b8a6';    // 青绿色
    case 'medical': return '#06b6d4';     // 青色
    default: return '#10b981';
  }
};
```

---

## 🚀 添加新建筑

### 步骤

1. **在 `buildings` 数组末尾添加新对象**

```typescript
{ 
  id: 11,                    // ← 新ID（唯一）
  name: '11号楼',            // ← 新名称
  x: '80%',                  // ← 定位坐标
  y: '75%', 
  width: '15%', 
  height: '20%', 
  elderCount: 95,            // ← 数据
  alertCount: 0, 
  healthyRate: 100, 
  type: 'residential' 
}
```

2. **保存文件，刷新页面**
3. **检查新建筑是否显示**
4. **调整坐标以匹配航拍图**

---

## 📊 统计数据更新

### 自动统计

地图顶部的统计数据会自动计算：

```typescript
// 文件位置：第72-73行
const totalElders = buildings.reduce((sum, b) => sum + b.elderCount, 0);
const totalAlerts = buildings.reduce((sum, b) => sum + b.alertCount, 0);
```

- **总建筑：** `buildings.length`（自动）
- **总人数：** 所有楼栋入住人数之和（自动）
- **预警数：** 所有楼栋预警数量之和（自动）

**无需手动修改！**

---

## 🎯 常见问题

### Q1: 建筑热区位置不准确？
**A:** 
1. 检查 `x, y, width, height` 的百分比是否正确
2. 使用图片编辑软件重新测量坐标
3. 确保航拍图没有被拉伸变形

### Q2: 航拍图显示模糊？
**A:** 
1. 使用更高分辨率的图片（建议≥1920x1080）
2. 确保 `object-cover` 类正常生效
3. 检查容器高度是否固定（当前为700px）

### Q3: 预警标记不显示？
**A:** 
1. 检查 `alertCount` 是否大于0
2. 确保 z-index 层级正确（标记为 z-20）
3. 检查脉冲动画 `animate-pulse` 和 `animate-ping` 是否生效

### Q4: 点击建筑无反应？
**A:** 
1. 检查热区的 `cursor-pointer` 是否生效
2. 确保 `onClick` 事件绑定正常
3. 检查交互层的 z-index 是否在图片层之上

### Q5: 悬停时详情弹窗被遮挡？
**A:** 
1. 调整弹窗的 z-index（当前为 z-10）
2. 确保父容器没有 `overflow: hidden`
3. 检查 `pointer-events-none` 是否正确设置

---

## 🔧 高级自定义

### 添加新的建筑类型

1. **扩展类型定义**（第15行）

```typescript
type: 'residential' | 'activity' | 'medical' | 'service' | 'dining' // ← 添加 'dining'
```

2. **添加颜色配置**（第41行）

```typescript
case 'dining':
  return 'rgba(59, 130, 246, 0.6)'; // 蓝色-餐饮
```

3. **添加边框颜色**（第57行）

```typescript
case 'dining': return '#3b82f6'; // 蓝色
```

4. **更新图例**（第231行）

```typescript
<div className="flex items-center gap-1.5">
  <div className="w-3 h-3 bg-blue-500 rounded"></div>
  <span className="text-gray-300">餐饮中心</span>
</div>
```

### 添加更多预警级别

**当前：**
- 0个预警 → 绿色
- 1-2个预警 → 黄色
- 3个以上 → 橙色

**自定义：**

```typescript
const getColor = (building: Building) => {
  if (building.alertCount > 5) return 'rgba(239, 68, 68, 0.7)'; // 红色-危险
  if (building.alertCount > 2) return 'rgba(245, 158, 11, 0.7)'; // 橙色-紧急
  if (building.alertCount > 0) return 'rgba(251, 191, 36, 0.7)'; // 黄色-预警
  return 'rgba(16, 185, 129, 0.6)'; // 绿色-正常
};
```

---

## 📝 数据对接指南

### 连接真实API

**当前：** 使用硬编码的模拟数据

**改造为动态数据：**

```typescript
import { useState, useEffect } from 'react';

export function CommunityMap2D() {
  const [buildings, setBuildings] = useState<Building[]>([]);
  
  // 组件挂载时获取数据
  useEffect(() => {
    fetchBuildingsData();
    
    // 每30秒刷新一次
    const interval = setInterval(fetchBuildingsData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const fetchBuildingsData = async () => {
    try {
      const response = await fetch('/api/community/buildings');
      const data = await response.json();
      setBuildings(data);
    } catch (error) {
      console.error('获取建筑数据失败:', error);
    }
  };
  
  // ... 其余代码
}
```

**API数据格式：**

```json
[
  {
    "id": 1,
    "name": "1号楼",
    "x": "8%",
    "y": "13%",
    "width": "20%",
    "height": "20%",
    "elderCount": 87,
    "alertCount": 0,
    "healthyRate": 100,
    "type": "residential"
  },
  ...
]
```

---

## 🎨 视觉效果说明

### 边框样式

| 状态 | 边框类型 | 颜色 | 发光效果 |
|------|----------|------|----------|
| 正常 | 虚线 | 绿色 | 无 |
| 预警 | 虚线 | 黄色 | 无 |
| 悬停 | 虚线 | 原色 | 15px发光 |
| 选中 | 实线 | 原色 | 20px发光 + 内部发光 |

### 动画效果

1. **预警标记脉冲**
   - 动画：`animate-pulse`
   - 周期：2秒
   - 效果：不透明度变化

2. **预警光圈扩散**
   - 动画：`animate-ping`
   - 周期：1秒
   - 效果：缩放 + 淡出

3. **边框脉冲**
   - 动画：`animate-pulse`
   - 触发：悬停或选中
   - 效果：边框透明度变化

---

## 📦 完整组件结构

```
CommunityMap2D
├── 容器 (bg-teal-900/40)
│   ├── 装饰角 (4个)
│   ├── 标题栏
│   │   ├── 标题 + 脉冲点
│   │   └── 统计信息 (建筑数、人数、预警数)
│   ├── 主内容区
│   │   ├── 航拍图容器
│   │   │   ├── 航拍图 (<img>)
│   │   │   └── 交互层
│   │   │       └── 建筑热区 (10个 <div>)
│   │   │           ├── 覆盖层（边框+填充）
│   │   │           ├── 信息标签（悬停/选中时）
│   │   │           ├── 预警标记（如有）
│   │   │           └── 楼号标签（默认）
│   │   └── 底部信息栏
│   │       ├── 图例
│   │       └── 选中建筑详情（如有）
```

---

## 🎯 最佳实践

1. **坐标定位**
   - 使用百分比而不是像素
   - 预留边距避免边缘建筑被裁切
   - 使用标注图辅助定位

2. **性能优化**
   - 避免过多建筑（建议≤20栋）
   - 使用 `transform` 代替 `width/height` 动画
   - 优化图片大小（建议≤500KB）

3. **用户体验**
   - 提供清晰的视觉反馈
   - 预警标记要醒目
   - 详情信息要完整

4. **可维护性**
   - 使用常量配置颜色
   - 提取公共函数
   - 添加必要的注释

---

## 📞 需要帮助？

如果您需要：
- 🗺️ 重新定位建筑坐标
- 🖼️ 更换航拍图
- 🎨 自定义颜色方案
- 📊 连接真实API
- ⚡ 性能优化
- 🐛 问题排查

请随时告诉我！😊

---

**文档更新时间：** 2025-11-29  
**组件版本：** v1.0  
**维护状态：** ✅ 活跃维护
