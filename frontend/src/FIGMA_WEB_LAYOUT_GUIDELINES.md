# Figma Web 布局设计规范

> **目标**: 从设计阶段就使用Web布局思维，避免生成 `position: absolute` 代码  
> **适用项目**: 智慧健康管理系统（老人端、子女端、社区端）  
> **版本**: v1.0

---

## 📋 目录

1. [核心原则](#核心原则)
2. [Auto Layout 使用规范](#auto-layout-使用规范)
3. [约束系统最佳实践](#约束系统最佳实践)
4. [响应式设计策略](#响应式设计策略)
5. [图片和资源处理](#图片和资源处理)
6. [常见错误和解决方案](#常见错误和解决方案)
7. [设计检查清单](#设计检查清单)
8. [实战示例](#实战示例)

---

## 🎯 核心原则

### ✅ 应该做的
- ✅ **始终使用 Auto Layout** 构建所有容器
- ✅ **使用相对单位** 而非绝对像素
- ✅ **从上到下、从外到内** 嵌套 Auto Layout
- ✅ **使用 Fill Container** 让元素自适应
- ✅ **命名规范清晰**，让开发者一眼看懂

### ❌ 不应该做的
- ❌ **手动拖拽** 元素到任意位置
- ❌ **使用固定 X/Y 坐标** 定位元素
- ❌ **直接设置固定宽度** 给内容元素
- ❌ **混合使用** Auto Layout 和手动定位
- ❌ **忽略约束设置**

---

## 🔧 Auto Layout 使用规范

### 1. 基础容器结构

#### ✅ 正确示例：Card 组件
```
Frame: HealthCard (Auto Layout ✓)
  ├─ Direction: Vertical
  ├─ Padding: 24px (all sides)
  ├─ Gap: 16px
  ├─ Fill: Hug contents (高度)
  ├─ Fill: Fill container (宽度)
  │
  ├─ Frame: CardHeader (Auto Layout ✓)
  │   ├─ Direction: Horizontal
  │   ├─ Gap: 12px
  │   ├─ Align: Center
  │   │
  │   ├─ Icon (Fixed: 24x24)
  │   └─ Text: Title (Fill container)
  │
  ├─ Frame: CardContent (Auto Layout ✓)
  │   ├─ Direction: Vertical
  │   ├─ Gap: 8px
  │   │
  │   ├─ Text: Value
  │   └─ Text: Unit
  │
  └─ Frame: CardFooter (Auto Layout ✓)
      └─ Text: Status
```

**对应的 React 代码**:
```tsx
<Card className="p-6 flex flex-col gap-4">
  <div className="flex items-center gap-3">
    <Icon className="w-6 h-6" />
    <h3 className="flex-1">Title</h3>
  </div>
  <div className="flex flex-col gap-2">
    <span>Value</span>
    <span>Unit</span>
  </div>
  <div>
    <p>Status</p>
  </div>
</Card>
```

#### ❌ 错误示例：不使用 Auto Layout
```
Frame: HealthCard (No Auto Layout ✗)
  ├─ Icon (X: 24, Y: 24) ← 绝对定位！
  ├─ Text: Title (X: 60, Y: 26) ← 绝对定位！
  ├─ Text: Value (X: 24, Y: 80) ← 绝对定位！
  └─ Text: Unit (X: 120, Y: 85) ← 绝对定位！
```

**会生成的糟糕代码**:
```tsx
<div style={{ position: 'relative' }}>
  <Icon style={{ position: 'absolute', left: '24px', top: '24px' }} />
  <h3 style={{ position: 'absolute', left: '60px', top: '26px' }}>Title</h3>
  <span style={{ position: 'absolute', left: '24px', top: '80px' }}>Value</span>
  <span style={{ position: 'absolute', left: '120px', top: '85px' }}>Unit</span>
</div>
```

---

### 2. Auto Layout 属性设置指南

#### Direction (方向)
- **Horizontal**: 用于导航栏、按钮组、统计卡片组
- **Vertical**: 用于表单、列表、文章内容

```
导航栏 → Horizontal
├─ Logo
├─ Menu Items (Horizontal)
└─ User Info
```

#### Gap (间距)
- **统一间距系统**: 使用 4px 的倍数
  - 4px: 紧密元素（图标和文字）
  - 8px: 相关元素
  - 16px: 卡片内部分段
  - 24px: 不同区块
  - 32px: 主要区域

#### Padding (内边距)
- **卡片**: 16px - 24px
- **按钮**: 12px 16px (vertical horizontal)
- **输入框**: 12px 16px
- **容器**: 24px - 48px

#### Resizing (尺寸调整)
- **Hug contents**: 内容决定大小（按钮、标签）
- **Fill container**: 填充父容器（主要内容区域）
- **Fixed**: 固定大小（图标、头像）

```
Button (Auto Layout)
  ├─ Horizontal resizing: Hug ✓
  ├─ Vertical resizing: Hug ✓
  ├─ Padding: 12px 24px
  └─ Text (Fill container)
```

---

### 3. 嵌套 Auto Layout 的最佳实践

#### ✅ 三层嵌套结构
```
Page Container (Auto Layout - Vertical)
  └─ Section Container (Auto Layout - Vertical, Gap: 24px)
      └─ Card Grid (Auto Layout - Horizontal, Wrap)
          ├─ Card 1 (Auto Layout - Vertical)
          ├─ Card 2 (Auto Layout - Vertical)
          └─ Card 3 (Auto Layout - Vertical)
```

**Figma 操作步骤**:
1. 选中最外层 Frame → `Shift + A` (添加 Auto Layout)
2. 设置 Direction: Vertical, Padding: 48px
3. 选中内部 Section → `Shift + A`
4. 设置 Direction: Vertical, Gap: 24px
5. 选中 Card 容器 → `Shift + A`
6. 设置 Direction: Horizontal, Wrap

---

## 🎨 约束系统最佳实践

### 1. 约束类型说明

| 约束类型 | 使用场景 | CSS 等价 |
|---------|---------|---------|
| **Left & Right** | 需要填充宽度的元素 | `width: 100%` |
| **Top & Bottom** | 需要填充高度的元素 | `height: 100%` |
| **Center** | 居中元素 | `margin: 0 auto` |
| **Scale** | 等比例缩放 | `width: 50%` |
| **Left** | 左对齐固定宽度 | `position: static` |

### 2. 常见布局的约束设置

#### 📱 顶部导航栏
```
Navbar Frame
  ├─ Constraints: Left & Right, Top
  ├─ Width: Fill container
  ├─ Height: Fixed (64px)
  │
  ├─ Logo (Constraints: Left, Center Vertically)
  ├─ Menu (Constraints: Left & Right, Center)
  └─ User Avatar (Constraints: Right, Center)
```

#### 🖼️ 图片容器
```
Image Container
  ├─ Constraints: Left & Right
  ├─ Width: Fill container
  ├─ Height: Fixed (或 Scale)
  │
  └─ Image
      ├─ Constraints: Left & Right, Top & Bottom
      └─ Object Fit: Cover (或 Contain)
```

#### 📊 卡片网格
```
Grid Container
  ├─ Auto Layout: Horizontal, Wrap
  ├─ Gap: 24px
  │
  └─ Card
      ├─ Width: Fixed (360px) 或 Fill (33.33%)
      ├─ Height: Hug
      └─ Constraints: Top, Left
```

---

## 📐 响应式设计策略

### 1. 断点系统

在 Figma 中创建不同尺寸的 Frame 模拟响应式：

```
Desktop (1440px)
├─ Container: Max-width 1200px, Center
└─ 3 列卡片网格

Tablet (768px)
├─ Container: Padding 24px
└─ 2 列卡片网格

Mobile (375px)
├─ Container: Padding 16px
└─ 1 列卡片堆叠
```

### 2. 使用 Figma Components 变体

创建响应式组件：

```
Component: HealthCard
  Variant: Desktop (width: 360px)
  Variant: Tablet (width: 280px)
  Variant: Mobile (width: 100%)
```

### 3. 固定宽度 vs 自适应宽度

#### ✅ 推荐：自适应宽度
```
Container (Auto Layout)
  ├─ Width: Fill container
  ├─ Max-width: 1200px (使用插件设置)
  └─ Margin: Auto (左右居中)
```

#### ❌ 避免：所有元素都固定宽度
```
Container
  ├─ Width: 1440px ← 不要这样！
  └─ Card
      └─ Width: 360px ← 在小屏幕会溢出！
```

---

## 🖼️ 图片和资源处理

### 1. 图片容器设计

#### ✅ 正确方式：使用 Fill
```
Image Frame (Auto Layout)
  ├─ Width: Fill container
  ├─ Height: 240px (Fixed)
  ├─ Clip content: ✓
  │
  └─ Image
      ├─ Constraints: Left & Right, Top & Bottom
      ├─ Object fit: Cover
      └─ Alignment: Center
```

**生成的代码**:
```tsx
<div className="w-full h-60 overflow-hidden">
  <img 
    src="..." 
    alt="..." 
    className="w-full h-full object-cover"
  />
</div>
```

#### ❌ 错误方式：固定尺寸图片
```
Image
  ├─ Width: 360px (Fixed) ← 不要这样！
  ├─ Height: 240px (Fixed)
  └─ Constraints: Left, Top ← 会生成 position: absolute!
```

### 2. 图标处理

#### ✅ 使用 SVG 组件
```
Icon Frame
  ├��� Width: 24px (Fixed)
  ├─ Height: 24px (Fixed)
  ├─ Constraints: Left, Center
  └─ SVG Path (不要使用栅格图片！)
```

#### 导出设置
- **Format**: SVG
- **Include "id" attribute**: OFF
- **Outline text**: ON
- **Simplify stroke**: ON

---

## ⚠️ 常见错误和解决方案

### 错误 1: 元素自由浮动

**问题**:
```
Container (无 Auto Layout)
  ├─ Card 1 (X: 100, Y: 50)
  ├─ Card 2 (X: 500, Y: 50)
  └─ Card 3 (X: 900, Y: 50)
```

**解决**:
```
Container (Auto Layout - Horizontal)
  ├─ Gap: 24px
  ├─ Padding: 48px
  ├─ Card 1
  ├─ Card 2
  └─ Card 3
```

---

### 错误 2: 文本宽度固定

**问题**:
```
Text: "下午好，张三"
  └─ Width: 200px (Fixed) ← 名字长了会被截断！
```

**解决**:
```
Text: "下午好，张三"
  └─ Width: Hug contents (或 Fill container)
```

---

### 错误 3: 使用负边距对齐

**问题**:
```
Element
  ├─ X: -10px ← 使用负坐标"调整"位置
  └─ Y: -5px
```

**解决**:
```
使用 Auto Layout 的 Padding 和 Gap 控制间距
不要手动调整坐标！
```

---

### 错误 4: 混合使用定位方式

**问题**:
```
Container (Auto Layout)
  ├─ Card 1 (在 Auto Layout 流中)
  ├─ Card 2 (Absolute position) ← 不要混用！
  └─ Card 3 (在 Auto Layout 流中)
```

**解决**:
```
Container (Auto Layout)
  ├─ Card 1
  ├─ Card 2 (也在 Auto Layout 流中)
  └─ Card 3

如果确实需要浮动元素（如悬浮按钮），
将它单独放在一个图层，使用 position: fixed
```

---

## ✅ 设计检查清单

### 开始设计前
- [ ] 确定目标设备（Desktop / Tablet / Mobile）
- [ ] 定义间距系统（4px / 8px / 16px / 24px）
- [ ] 定义断点（375px / 768px / 1440px）
- [ ] 准备组件库（按钮、卡片、表单）

### 设计过程中
- [ ] 每个 Frame 都启用了 Auto Layout
- [ ] 使用 Gap 而不是手动调整间距
- [ ] 使用 Padding 设置容器内边距
- [ ] 文本使用 Hug 或 Fill，不固定宽度
- [ ] 图片使用 Fill container + 约束

### 设计完成后
- [ ] 检查所有元素，无 X/Y 绝对坐标
- [ ] 检查图层命名，使用语义化名称
- [ ] 测试响应式（拖动 Frame 宽度）
- [ ] 导出前清理无用图层
- [ ] 确认所有图片为 SVG 或正确比例

### 交付给开发前
- [ ] 创建组件库文档
- [ ] 标注特殊交互（hover / active）
- [ ] 提供设计 token（颜色 / 字体 / 间距）
- [ ] 确认 Auto Layout 方向和对齐
- [ ] 验证约束设置正确

---

## 💡 实战示例

### 示例 1: 老人端健康卡片

#### 设计结构
```
HealthCard (Auto Layout - Vertical)
  ├─ Width: Fill container
  ├─ Height: Hug contents
  ├─ Padding: 24px
  ├─ Gap: 16px
  ├─ Background: gradient(amber-100 to amber-50)
  ├─ Border: 2px, amber-200
  ├─ Border radius: 16px
  │
  ├─ Header (Auto Layout - Horizontal)
  │   ├─ Gap: 12px
  │   ├─ Align: Center
  │   │
  │   ├─ Icon: Droplets (24x24, Fixed)
  │   └─ Title: "血糖" (Fill container, Text size: 36px)
  │
  ├─ Value Container (Auto Layout - Horizontal)
  │   ├─ Gap: 8px
  │   ├─ Align: Baseline
  │   │
  │   ├─ Value: "5.2" (Hug, Text size: 80px, Bold)
  │   └─ Unit: "mmol/L" (Hug, Text size: 32px)
  │
  ├─ Status (Auto Layout - Horizontal)
  │   ├─ Gap: 8px
  │   │
  │   └─ Text: "正常 空腹血糖" (Fill, Text size: 28px)
  │
  └─ AI Button (Auto Layout - Horizontal)
      ├─ Width: Fill container
      ├─ Height: Hug
      ├─ Padding: 12px 16px
      ├─ Gap: 8px
      ├─ Background: gradient(purple-600 to purple-500)
      │
      ├─ Icon: Sparkles (20x20, Fixed)
      └─ Text: "AI 分析" (Fill, Text size: 24px)
```

#### Figma 操作步骤

1. **创建容器**
   - 按 `F` 创建 Frame
   - 命名为 "HealthCard"
   - 宽度: 400px (临时)
   - 按 `Shift + A` 启用 Auto Layout

2. **设置容器属性**
   - Direction: Vertical ↓
   - Gap: 16px
   - Padding: 24px (all sides)
   - Horizontal resizing: Fill container
   - Vertical resizing: Hug contents

3. **添加 Header**
   - 在容器内按 `F` 创建 Frame
   - 命名为 "Header"
   - `Shift + A` 启用 Auto Layout
   - Direction: Horizontal →
   - Gap: 12px
   - Align items: Center

4. **添加图标**
   - 使用插件 "Iconify" 搜索 "Droplets"
   - 拖入 Header
   - 设置大小: 24x24
   - Constraints: Left, Center

5. **添加标题**
   - 按 `T` 创建文本
   - 输入 "血糖"
   - 字号: 36px
   - Width: Fill container

6. **添加数值**
   - 创建新 Frame "ValueContainer"
   - Auto Layout - Horizontal
   - Gap: 8px
   - Align: Baseline
   - 添加两个文本: "5.2" (80px) 和 "mmol/L" (32px)

7. **测试响应式**
   - 拖动 HealthCard 的宽度
   - 观察元素是否正确缩放
   - 文字不应该被截断
   - 间距保持一致

---

### 示例 2: 导航栏 (老人端)

#### 设计结构
```
Navbar (Auto Layout - Horizontal)
  ├─ Width: Fill container (100%)
  ├─ Height: Fixed (80px)
  ├─ Padding: 16px 48px
  ├─ Gap: 32px
  ├─ Align: Center
  ├─ Background: white
  ├─ Border bottom: 2px, teal-200
  ├─ Constraints: Left & Right, Top
  │
  ├─ Logo (Auto Layout - Horizontal)
  │   ├─ Gap: 12px
  │   ├─ Width: Hug
  │   │
  │   ├─ Icon: Heart (48x48, Fixed)
  │   └─ Text: "智慧健康管理" (Hug, 32px)
  │
  ├─ Spacer (Fill container) ← 用于推开左右两侧
  │
  ├─ Menu Items (Auto Layout - Horizontal)
  │   ├─ Gap: 16px
  │   ├─ Width: Hug
  │   │
  │   ├─ MenuItem: "今日健康" (Active state)
  │   ├─ MenuItem: "历史报告"
  │   ├─ MenuItem: "AI 助手"
  │   └─ MenuItem: "心理健康"
  │
  └─ User Section (Auto Layout - Horizontal)
      ├─ Gap: 12px
      ├─ Width: Hug
      ├─ Padding: 8px 16px
      │
      ├─ Avatar (48x48, Fixed)
      └─ Name: "张三" (Hug, 28px)
```

**关键点**:
- ✅ Spacer 元素（空 Frame）设置为 Fill container，实现 `justify-content: space-between` 效果
- ✅ 菜单项使用 Component Variants 管理 Active/Inactive 状态
- ✅ 整个导航栏使用 Constraints: Left & Right, Top

---

### 示例 3: 响应式卡片网格

#### Desktop (1440px)
```
Container (Auto Layout - Vertical)
  ├─ Width: 1200px, Center in parent
  ├─ Padding: 48px
  ├─ Gap: 32px
  │
  └─ Card Grid (Auto Layout - Horizontal)
      ├─ Gap: 24px
      ├─ Wrap: ✓
      │
      ├─ Card (360px, Hug) x 3 per row
      ├─ Card
      └─ Card
```

#### Tablet (768px)
```
Container (Auto Layout - Vertical)
  ├─ Width: Fill container
  ├─ Padding: 24px
  ├─ Gap: 24px
  │
  └─ Card Grid (Auto Layout - Horizontal)
      ├─ Gap: 16px
      ├─ Wrap: ✓
      │
      ├─ Card (calc(50% - 8px), Hug) x 2 per row
      └─ Card
```

#### Mobile (375px)
```
Container (Auto Layout - Vertical)
  ├─ Width: Fill container
  ├─ Padding: 16px
  ├─ Gap: 16px
  │
  └─ Card Grid (Auto Layout - Vertical) ← 注意改为 Vertical
      ├─ Gap: 16px
      │
      ├─ Card (Fill container, Hug)
      ├─ Card
      └─ Card
```

---

## 🔗 有用的 Figma 插件

### 布局辅助
- **Auto Layout Manager**: 批量设置 Auto Layout
- **Find and Replace**: 批量修改间距值
- **Responsify**: 快速创建响应式变体
- **Rename It**: 批量重命名图层

### 图标和资源
- **Iconify**: 搜索和使用 SVG 图标
- **Unsplash**: 高质量图片
- **Remove BG**: 去除图片背景

### 代码生成
- **Anima**: 预览响应式效果
- **Figma to Code**: ��查生成的代码质量
- **Inspect**: 查看 CSS 属性

---

## 📊 设计 Token 系统

### 间距系统 (Spacing Scale)
```
xs:  4px   → gap-1, p-1
sm:  8px   → gap-2, p-2
md:  16px  → gap-4, p-4
lg:  24px  → gap-6, p-6
xl:  32px  → gap-8, p-8
2xl: 48px  → gap-12, p-12
```

在 Figma 中创建 Local Variables:
- `spacing/xs` = 4
- `spacing/sm` = 8
- `spacing/md` = 16
- `spacing/lg` = 24

### 颜色系统
```
医疗主色调 (Teal):
  - teal-50:  #f0fdf4
  - teal-100: #dcfce7
  - teal-500: #0d9488 (主色)
  - teal-600: #0c8074

功能色:
  - success: green-500
  - warning: amber-500
  - danger:  red-500
  - info:    blue-500
```

### 字体系统（老人端）
```
Display:  80px (数值显示)
Heading:  48px (大标题)
Title:    36px (卡片标题)
Body:     28px (正文)
Caption:  24px (辅助说明)
```

---

## 🎓 学习资源

### Figma 官方教程
- [Auto Layout 完整指南](https://www.figma.com/best-practices/everything-you-need-to-know-about-layout-grids/)
- [Constraints 深度解析](https://help.figma.com/hc/en-us/articles/360039957734)
- [响应式设计](https://www.figma.com/best-practices/responsive-design-in-figma/)

### 推荐视频
- Figma Auto Layout 完全指南 - YouTube
- 从 Figma 到 React 的正确姿势 - Bilibili

---

## 📝 总结

### 三个黄金法则

1. **永远使用 Auto Layout**
   - 每个容器都应该是 Auto Layout
   - 从最外层到最内层，层层嵌套
   - 不要让任何元素"自由浮动"

2. **使用 Fill Container 而非固定宽度**
   - 让元素自适应父容器
   - 使用 Max-width 而非 Width
   - 图片、文本都应该是流式布局

3. **避免绝对定位**
   - 不要手动设置 X/Y 坐标
   - 使用 Gap 和 Padding 控制间距
   - 使用 Constraints 只用于确定对齐方式

### 检查标准

✅ **合格的设计**:
- 没有任何 X/Y 绝对坐标
- 所有容器都是 Auto Layout
- 拖动 Frame 宽度，布局不会崩溃
- 文字不会被截断
- 元素间距保持一致

❌ **不合格的设计**:
- 大量元素有固定 X/Y 坐标
- 混用 Auto Layout 和手动定位
- 固定宽度导致小屏幕溢出
- 文字宽度固定导致截断

---

**文档维护**: 设计团队  
**最后更新**: 2024-12-01  
**版本**: v1.0
