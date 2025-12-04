# ⚡ 快速开始指南

## 🎯 三步完成迁移

### 第 1 步：在 Figma Make 中下载项目

1. **点击右上角的导出按钮**
2. **选择 "Download Code" 或 "Export Project"**
3. **下载 ZIP 文件到本地**
4. **解压缩文件**

---

### 第 2 步：设置本地项目

打开终端，运行以下命令：

```bash
# 创建新项目
npm create vite@latest my-health-app -- --template react-ts
cd my-health-app

# 一键安装所有依赖
npm install lucide-react recharts \
  @radix-ui/react-avatar \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-label \
  @radix-ui/react-popover \
  @radix-ui/react-select \
  @radix-ui/react-separator \
  @radix-ui/react-slot \
  @radix-ui/react-switch \
  @radix-ui/react-tabs \
  @radix-ui/react-tooltip \
  @radix-ui/react-accordion \
  @radix-ui/react-alert-dialog \
  class-variance-authority \
  clsx \
  date-fns \
  tailwind-merge

# 安装开发依赖
npm install -D tailwindcss postcss autoprefixer @types/node

# 初始化 Tailwind
npx tailwindcss init -p
```

---

### 第 3 步：复制文件

将从 Figma Make 下载的文件复制到项目中：

```bash
# 从下载的 ZIP 中复制以下内容：

解压的文件夹/App.tsx          → my-health-app/src/App.tsx
解压的文件夹/components/      → my-health-app/src/components/
解压的文件夹/styles/          → my-health-app/src/styles/
```

---

## 📝 配置文件

### 1. 编辑 `tailwind.config.js`

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
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
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

### 2. 编辑 `src/main.tsx`

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

### 3. 编辑 `vite.config.ts`

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

---

## 🖼️ 处理图片资源

### 如果代码中有 `figma:asset/` 导入：

**原代码：**
```typescript
import logoImage from 'figma:asset/xxxxx.png';
```

**修改为：**
```typescript
import logoImage from './assets/logo.png';
```

然后将图片文件放到 `src/assets/` 目录。

---

## 🚀 启动项目

```bash
npm run dev
```

浏览器访问：`http://localhost:5173`

---

## ✅ 验证清单

启动后检查：

- [ ] 登录页面显示正常
- [ ] 可以选择三个角色（老人端/子女端/社区端）
- [ ] 老人端：生命体征卡片显示
- [ ] 老人端：图表正常渲染
- [ ] 导航栏可以切换
- [ ] 语音播报按钮存在（Chrome/Edge 浏览器）
- [ ] 无控制台错误

---

## 🐛 常见问题

### 问题 1：图表不显示

**解决方案：**
```bash
npm install recharts
```

### 问题 2：图标不显示

**解决方案：**
```bash
npm install lucide-react
```

### 问题 3：样式不生效

**解决方案：**
- 确认 `src/main.tsx` 中导入了 `./styles/globals.css`
- 确认 Tailwind 配置正确

### 问题 4：TypeScript 错误

**解决方案：**
```bash
npm install -D @types/node @types/react @types/react-dom
```

### 问题 5：组件导入错误

**检查路径：**
```typescript
// 使用相对路径
import { Button } from './components/ui/button'

// 或使用别名（需要配置 vite.config.ts）
import { Button } from '@/components/ui/button'
```

---

## 📦 完整的 package.json 示例

```json
{
  "name": "health-monitoring-system",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
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
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
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

## 🎉 成功运行后

### 构建生产版本

```bash
npm run build
```

构建文件会在 `dist/` 目录中。

### 部署到 Vercel

```bash
npm i -g vercel
vercel
```

### 部署到 Netlify

上传 `dist/` 目录到 Netlify。

---

## 📞 需要帮助？

如果遇到问题：

1. **查看控制台错误**
2. **确认所有依赖已安装**
3. **检查文件路径是否正确**
4. **参考 MIGRATION_GUIDE.md 详细指南**

---

## 🎯 下一步

项目成功运行后，您可以：

1. ✅ **集成真实数据** - 连接您的后端 API
2. ✅ **添加用户认证** - 实现真实的登录系统
3. ✅ **数据持久化** - 使用数据库存储健康数据
4. ✅ **移动端优化** - 添加响应式设计
5. ✅ **性能优化** - 代码分割和懒加载

祝您开发顺利！🚀
