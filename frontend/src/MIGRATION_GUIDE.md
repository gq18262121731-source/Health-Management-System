# 🚀 健康监测系统迁移指南

## 📦 第一步：安装依赖

在您的本地项目中，运行以下命令安装所有必需的依赖：

```bash
# 初始化项目（如果还没有）
npm create vite@latest my-health-app -- --template react-ts
cd my-health-app

# 安装核心依赖
npm install lucide-react recharts

# 安装 Radix UI 组件（用于 shadcn/ui）
npm install @radix-ui/react-avatar
npm install @radix-ui/react-slot
npm install @radix-ui/react-tooltip
npm install @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select
npm install @radix-ui/react-switch
npm install @radix-ui/react-tabs
npm install @radix-ui/react-accordion
npm install @radix-ui/react-alert-dialog
npm install @radix-ui/react-popover
npm install @radix-ui/react-separator
npm install @radix-ui/react-label

# 安装工具库
npm install class-variance-authority clsx tailwind-merge
npm install date-fns

# 安装 Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# TypeScript 类型定义
npm install -D @types/react @types/react-dom
```

---

## 📁 第二步：配置 Tailwind CSS

### `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}
```

---

## 📂 第三步：复制文件

从 Figma Make 复制以下文件到您的项目：

### 核心文件结构

```
src/
├── App.tsx                                    ✅ 主应用入口
├── styles/
│   └── globals.css                           ✅ 全局样式（包含 Tailwind）
├── components/
│   ├── ui/                                   ✅ 基础 UI 组件（30+ 个文件）
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── avatar.tsx
│   │   ├── tooltip.tsx
│   │   └── ... （所有 ui 组件）
│   │
│   ├── dashboard/                            ✅ 仪表盘组件
│   │   ├── HealthCharts.tsx                 （核心图表组件）
│   │   ├── MoodQuickCard.tsx                （心情记录）
│   │   └── StatCard.tsx                     （统计卡片）
│   │
│   ├── layout/                               ✅ 布局组件
│   │   └── LayoutComponents.tsx             （导航栏、头部）
│   │
│   ├── login/                                ✅ 登录页面
│   │   └── LoginPage.tsx                    （三端选择）
│   │
│   ├── children/                             ✅ 子女端
│   │   ├── ChildrenDashboard.tsx
│   │   ├── ElderlyList.tsx
│   │   └── ... （5个文件）
│   │
│   ├── community/                            ✅ 社区端
│   │   ├── CommunityDashboard.tsx
│   │   ├── DataVisualization.tsx
│   │   └── ... （4个文件）
│   │
│   ├── consultation/                         ✅ AI 咨询
│   │   └── AIConsultation.tsx
│   │
│   ├── psychology/                           ✅ 心理健康
│   │   ├── PsychologyPage.tsx
│   │   └── PsychologyCharts.tsx
│   │
│   ├── figma/                                ✅ 工具组件
│   │   └── ImageWithFallback.tsx            （图片回退组件）
│   │
│   └── MyInfo.tsx                            ✅ 个人信息
```

---

## 🖼️ 第四步：处理图片资源

### 替换 Figma 资源路径

在代码中搜索 `figma:asset/` 并替换为本地路径：

```typescript
// 原来的代码（Figma Make）
import logoImage from 'figma:asset/5c227ba3fcc87ef2343e011cf298867b85205e30.png';

// 改为本地路径
import logoImage from '../assets/logo.png';
```

### 创建 assets 目录

```bash
mkdir src/assets
# 将您的图片文件放到这里
```

---

## 🎨 第五步：导入全局样式

在 `src/main.tsx` 或 `src/index.tsx` 中导入样式：

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

## 🔧 第六步：处理路径别名（可选但推荐）

### `tsconfig.json` 添加路径别名

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### `vite.config.ts` 配置别名

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

然后在代码中将 `'./components/ui/button'` 改为 `'@/components/ui/button'`

---

## 🚀 第七步：运行项目

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

---

## ⚠️ 常见问题解决

### 1. 如果遇到 `Cell` 组件错误

recharts 的 `Cell` 组件需要从 recharts 导入：

```typescript
import { BarChart, Bar, Cell } from 'recharts';
```

### 2. 如果遇到类型错误

安装缺失的类型定义：

```bash
npm install -D @types/node
```

### 3. 如果图表不显示

确保父容器有明确的高度：

```tsx
<div style={{ height: '300px' }}>
  <ResponsiveContainer width="100%" height="100%">
    {/* 图表 */}
  </ResponsiveContainer>
</div>
```

### 4. 如果语音播报不工作

检查浏览器支持：

```typescript
if ('speechSynthesis' in window) {
  // 浏览器支持语音合成
} else {
  console.warn('浏览器不支持语音合成');
}
```

---

## 📱 第八步：部署到生产环境

### 部署到 Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录并部署
vercel
```

### 部署到 Netlify

```bash
# 构建
npm run build

# 上传 dist/ 目录到 Netlify
```

### 部署到自己的服务器

```bash
# 构建
npm run build

# 将 dist/ 目录上传到服务器
# 使用 Nginx 或 Apache 托管
```

---

## 📊 项目依赖清单

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.294.0",
    "recharts": "^2.10.3",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-tooltip": "^1.0.7",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "date-fns": "^2.30.0",
    "tailwind-merge": "^2.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

---

## ✅ 检查清单

完成迁移后，确认以下项目：

- [ ] 所有依赖已安装
- [ ] Tailwind CSS 配置正确
- [ ] 全局样式已导入
- [ ] 所有组件文件已复制
- [ ] 图片资源路径已更新
- [ ] 项目可以正常运行 (`npm run dev`)
- [ ] 登录页面可以显示
- [ ] 三端（老人端/子女端/社区端）都能正常切换
- [ ] 图表组件正常显示
- [ ] 语音播报功能正常（Chrome/Edge）

---

## 🎯 下一步优化建议

1. **添加后端 API 集成**
   - 连接真实的健康数据
   - 实现用户认证

2. **数据持久化**
   - 使用 localStorage 或 IndexedDB
   - 或连接到 Supabase/Firebase

3. **移动端适配**
   - 添加响应式断点
   - 优化触摸交互

4. **性能优化**
   - 代码分割 (React.lazy)
   - 图片懒加载

---

## 📞 需要帮助？

如果遇到任何问题，请检查：
1. 控制台错误信息
2. 是否所有依赖都已安装
3. 文件路径是否正确
4. Tailwind CSS 是否正确配置

祝您迁移顺利！🎉
