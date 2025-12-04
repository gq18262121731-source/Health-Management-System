# Figma 设计重构检查清单

> **项目**: 智慧健康管理系统  
> **目标**: 消除 `position: absolute`，实现纯 Flexbox/Grid 布局  
> **优先级**: ⭐⭐⭐⭐⭐

---

## 📊 当前问题分析

### 可能存在的布局问题

根据代码分析，以下组件可能在 Figma 中没有正确使用 Auto Layout：

#### ⚠️ 高风险组件（需要重点检查）

1. **健康卡片** (`HealthCardWithAI.tsx`)
   - 图标 + 标题 + 数值 + AI按钮
   - 如果元素是手动拖拽放置的，会生成 absolute 定位

2. **导航栏** (`UnifiedNavbar.tsx`)
   - Logo + 菜单项 + 用户信息
   - 需要使用 space-between 布局

3. **大屏统计卡片** (`BigScreenDashboard.tsx`)
   - 4个主要统计数据
   - 可能使用了 Grid，但 Figma 中可能是手动排列

4. **2D地图组件** (`CommunityMap2D.tsx`)
   - 地图背景 + 标记点
   - 标记点位置可能是绝对定位

5. **悬浮AI助手** (`FloatingAIAssistant.tsx`)
   - 这个应该使用 fixed 定位，属于合理的绝对定位

---

## ✅ 重构检查清单

### 第一步：识别问题

打开 Figma 设计文件，检查以下问题：

#### 问题 1: 元素是否使用了绝对坐标？

**如何检查**:
1. 选中任意元素
2. 查看右侧属性面板
3. 如果看到固定的 X/Y 数值（如 X: 120, Y: 45），且父级不是 Auto Layout
   - ❌ **问题确认**：这会生成 `position: absolute`

**解决方案**:
```
选中父容器 → Shift + A → 设置 Auto Layout
- Direction: 根据布局选择 Horizontal 或 Vertical
- Gap: 设置元素间距
- Padding: 设置容器内边距
```

#### 问题 2: 卡片网格是否手动排列？

**如何检查**:
1. 查看多个卡片是否等距排列
2. 拖动其中一个卡片
3. 如果其他卡片不跟随移动
   - ❌ **问题确认**：卡片是独立放置的

**解决方案**:
```
1. 选中所有卡片
2. Cmd/Ctrl + Option/Alt + G (创建 Frame)
3. Shift + A (添加 Auto Layout)
4. 设置:
   - Direction: Horizontal
   - Wrap: ✓ (允许换行)
   - Gap: 24px
```

#### 问题 3: 图标和文字是否对齐？

**如何检查**:
1. 选中图标和相邻的文字
2. 查看它们是否在同一个 Auto Layout 容器中
3. 如果图标 Y 坐标需要手动调整才能对齐
   - ❌ **问题确认**：没有使用 Auto Layout 对齐

**解决方案**:
```
1. 选中图标和文字
2. Cmd/Ctrl + Option/Alt + G
3. Shift + A
4. 设置:
   - Direction: Horizontal
   - Align items: Center (垂直居中)
   - Gap: 12px
```

---

## 🔧 分组件重构指南

### 1. 健康卡片 (HealthCard)

#### ❌ 当前可能的错误结构
```
Frame: HealthCard (1440 x 200) - 无 Auto Layout
  ├─ Icon: Droplets (X: 24, Y: 24, 24x24)
  ├─ Text: "血糖" (X: 60, Y: 28, W: 100)
  ├─ Text: "5.2" (X: 24, Y: 80, W: 150, Size: 80px)
  ├─ Text: "mmol/L" (X: 180, Y: 95, Size: 32px)
  ├─ Text: "正常 空腹血糖" (X: 24, Y: 160)
  └─ Button: "AI 分析" (X: 280, Y: 155, W: 120)
```

#### ✅ 正确的 Auto Layout 结构
```
Frame: HealthCard - Auto Layout ✓
  Direction: Vertical ↓
  Padding: 24px
  Gap: 16px
  Width: Fill container
  Height: Hug contents
  │
  ├─ Frame: Header - Auto Layout ✓
  │   Direction: Horizontal →
  │   Gap: 12px
  │   Align: Center
  │   │
  │   ├─ Icon: Droplets (24x24, Fixed)
  │   └─ Text: "血糖" (Fill container, 36px)
  │
  ├─ Frame: Value - Auto Layout ✓
  │   Direction: Horizontal →
  │   Gap: 8px
  │   Align: Baseline
  │   │
  │   ├─ Text: "5.2" (Hug, 80px, Bold)
  │   └─ Text: "mmol/L" (Hug, 32px)
  │
  ├─ Frame: Status - Auto Layout ✓
  │   Direction: Horizontal →
  │   │
  │   └─ Text: "正常 空腹血糖" (Fill, 28px)
  │
  └─ Frame: Button - Auto Layout ✓
      Direction: Horizontal →
      Padding: 12px 16px
      Gap: 8px
      Width: Fill container
      │
      ├─ Icon: Sparkles (20x20, Fixed)
      └─ Text: "AI 分析" (Fill, 24px)
```

#### 重构步骤（Figma 操作）
1. **备份原设计**
   - 复制当前 Frame 到新页面
   - 命名为 "HealthCard - Backup"

2. **清理图层**
   - 删除所有辅助线和注释
   - 解组不必要的分组

3. **重建 Header**
   ```
   - 创建新 Frame "Header"
   - Shift + A (Auto Layout)
   - 拖入图标和标题文字
   - Gap: 12px, Align: Center
   ```

4. **重建 Value**
   ```
   - 创建 Frame "Value"
   - Shift + A
   - 拖入数值和单位
   - Gap: 8px, Align: Baseline
   ```

5. **组装卡片**
   ```
   - 创建外层 Frame "HealthCard"
   - Shift + A
   - 依次拖入: Header, Value, Status, Button
   - Direction: Vertical
   - Gap: 16px
   - Padding: 24px
   ```

6. **测试响应式**
   ```
   - 拖动卡片宽度从 300px 到 600px
   - 检查元素是否正确缩放
   - 文字不应被截断
   - 间距保持一致
   ```

---

### 2. 导航栏 (Navbar)

#### ❌ 错误结构
```
Frame: Navbar (1440 x 80)
  ├─ Logo (X: 48, Y: 16)
  ├─ MenuItem 1 (X: 600, Y: 26)
  ├─ MenuItem 2 (X: 750, Y: 26)
  ├─ MenuItem 3 (X: 900, Y: 26)
  └─ User Avatar (X: 1344, Y: 16)
```

#### ✅ 正确结构
```
Frame: Navbar - Auto Layout ✓
  Direction: Horizontal →
  Padding: 16px 48px
  Gap: 32px
  Align: Center
  Width: Fill container (1440px)
  Height: 80px (Fixed)
  Constraints: Left & Right, Top
  │
  ├─ Frame: Logo - Auto Layout ✓
  │   Direction: Horizontal →
  │   Gap: 12px
  │   Width: Hug
  │   │
  │   ├─ Icon (48x48)
  │   └─ Text (Hug, 32px)
  │
  ├─ Frame: Spacer
  │   Width: Fill container ← 关键！推开左右
  │   Height: 1px
  │
  ├─ Frame: Menu - Auto Layout ✓
  │   Direction: Horizontal →
  │   Gap: 16px
  │   Width: Hug
  │   │
  │   ├─ MenuItem (Component)
  │   ├─ MenuItem
  │   └─ MenuItem
  │
  └─ Frame: UserSection - Auto Layout ✓
      Direction: Horizontal →
      Gap: 12px
      Width: Hug
      │
      ├─ Avatar (48x48)
      └─ Name (Hug, 28px)
```

#### 关键点
- ✅ Spacer 元素用于实现 `justify-content: space-between`
- ✅ 整个导航栏设置 Constraints: Left & Right, Top
- ✅ MenuItem 创建为 Component，方便复用

---

### 3. 统计卡片网格

#### ❌ 错误结构（4个卡片手动排列）
```
Frame: StatsSection (1440 x 200)
  ├─ StatCard 1 (X: 48,  Y: 0, W: 300, H: 180)
  ├─ StatCard 2 (X: 372, Y: 0, W: 300, H: 180)
  ├─ StatCard 3 (X: 696, Y: 0, W: 300, H: 180)
  └─ StatCard 4 (X: 1020, Y: 0, W: 300, H: 180)
```

#### ✅ 正确结构
```
Frame: StatsSection - Auto Layout ✓
  Direction: Horizontal →
  Gap: 24px
  Padding: 48px
  Width: Fill container
  │
  ├─ StatCard (Component Instance)
  │   Width: Fill container (会自动计算 25% - gap)
  │   Height: Hug
  │
  ├─ StatCard (Instance)
  ├─ StatCard (Instance)
  └─ StatCard (Instance)
```

#### StatCard 组件设计
```
Component: StatCard - Auto Layout ✓
  Direction: Vertical ↓
  Padding: 24px
  Gap: 12px
  Width: 280px (Base), 可变体调整
  Height: Hug
  │
  ├─ Icon (48x48, Fixed)
  ├─ Label (Hug, 24px)
  ├─ Value (Hug, 64px, Bold)
  └─ Change (Hug, 20px, Color variant)
```

---

### 4. 表单输入框 (老人端适老化)

#### ❌ 错误结构
```
Frame: FormField (600 x 120)
  ├─ Label (X: 0, Y: 0, W: 200)
  ├─ Icon: User (X: 0, Y: 60, 48x48)
  ├─ Input (X: 64, Y: 60, W: 500, H: 60)
  └─ VoiceButton (X: 580, Y: 60, 48x48)
```

#### ✅ 正确结构
```
Frame: FormField - Auto Layout ✓
  Direction: Vertical ↓
  Gap: 16px
  Width: Fill container
  │
  ├─ Frame: LabelRow - Auto Layout ✓
  │   Direction: Horizontal →
  │   Gap: 12px
  │   Align: Center
  │   │
  │   ├─ Icon: User (48x48, Fixed)
  │   └─ Text: "账号" (Hug, 40px)
  │
  └─ Frame: InputRow - Auto Layout ✓
      Direction: Horizontal →
      Gap: 12px
      Width: Fill container
      │
      ├─ Input
      │   Width: Fill container
      │   Height: 80px (Fixed)
      │   Padding: 20px
      │   Border: 4px
      │
      └─ Button: VoiceInput
          Width: 80px (Fixed)
          Height: 80px (Fixed)
```

---

## 📝 快速检查命令

在 Figma 中使用以下快捷方式快速检查：

### 1. 查找所有未使用 Auto Layout 的 Frame
```
Figma 插件: "Find All Absolute Positioned"
或者手动:
1. Cmd/Ctrl + F (搜索)
2. 输入 "Frame"
3. 逐个检查是否有 Auto Layout 图标 ⚡
```

### 2. 批量添加 Auto Layout
```
1. 选中多个 Frame
2. Shift + A
3. 在右侧面板统一设置 Direction、Gap、Padding
```

### 3. 检查约束设置
```
选中元素 → 右侧面板 → Constraints
应该看到:
- Left & Right (填充宽度)
- Top (顶部对齐)
而不是:
- Left, Top (绝对定位)
```

---

## 🎯 优先级排序

### P0 (立即修复)
- [ ] 登录页表单
- [ ] 主导航栏
- [ ] 健康卡片组件

### P1 (本周完成)
- [ ] 统计卡片网格
- [ ] 图表容器
- [ ] 按钮组件

### P2 (下周完成)
- [ ] 大屏数据面板
- [ ] 心理健康页面
- [ ] 个人信息页面

---

## 📊 验收标准

### 设计文件验收
- [ ] 所有 Frame 都有 Auto Layout
- [ ] 没有元素使用绝对 X/Y 坐标
- [ ] 拖动容器宽度，布局不崩溃
- [ ] 所有文本使用 Hug 或 Fill
- [ ] 图片使用约束 Left & Right, Top & Bottom

### 代码生成验收
- [ ] 生成的代码无 `position: absolute`（悬浮元素除外）
- [ ] 使用 Flexbox 或 Grid 布局
- [ ] 元素间距使用 gap 而非 margin
- [ ] 响应式断点正确

### 视觉还原验收
- [ ] Desktop (1440px) 完美还原
- [ ] Tablet (768px) 正确自适应
- [ ] Mobile (375px) 布局合理
- [ ] 字体大小和间距一致

---

## 🛠️ 推荐工作流

### Day 1: 审计和分类
1. 打开 Figma 文件
2. 创建检查清单 (Notion/Excel)
3. 逐页检查，标记问题组件
4. 按优先级排序

### Day 2-3: 核心组件重构
1. 从 P0 开始
2. 每个组件重构后立即测试
3. 导出代码验证布局
4. 更新组件库

### Day 4: 页面级重构
1. 使用新组件重建页面
2. 测试响应式
3. 对比原设计和新设计

### Day 5: 验收和文档
1. 完整走查
2. 生成代码测试
3. 更新设计系统文档
4. 交付给开发团队

---

## ✅ 检查清单总结

复制到 Figma 设计文件中：

```markdown
## Figma 布局自查清单

### 设计开始前
- [ ] 定义了间距系统（4/8/16/24/32px）
- [ ] 创建了组件库
- [ ] 确定了断点（375/768/1440px）

### 每个组件设计完成后
- [ ] 所有 Frame 都启用了 Auto Layout
- [ ] 没有固定 X/Y 坐标
- [ ] 测试了响应式（拖动宽度）
- [ ] 文字不会被截断
- [ ] 图层命名清晰（Header/Content/Footer）

### 设计交付前
- [ ] 运行 "Find Absolute Positioned" 插件
- [ ] 导出测试代码查看
- [ ] 检查约束设置
- [ ] 清理无用图层
- [ ] 标注交互状态
```

---

## 📞 需要帮助？

如果在重构过程中遇到问题：

### 常见问题
1. **"我的 Auto Layout 方向设置对了，为什么还是挤在一起？"**
   - 检查 Gap 是否设置
   - 检查子元素的 Width 是否都是 Fixed（应该至少有一个 Fill）

2. **"怎么实现 space-between 布局？"**
   - 在需要推开的两侧元素之间插入一个空 Frame
   - 设置这个 Frame 的 Width: Fill container

3. **"图片总是变形怎么办？"**
   - 设置图片 Constraints: Left & Right, Top & Bottom
   - 设置 Object Fit: Cover 或 Contain

### 联系方式
- Figma 社区论坛
- 内部设计团队 Slack 频道
- 本文档 GitHub Issues

---

**文档维护**: 设计团队  
**最后更新**: 2024-12-01  
**版本**: v1.0
