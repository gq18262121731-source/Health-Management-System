
  import { createRoot } from "react-dom/client";
  // 大屏展示界面
// import App from "./App.tsx";

// 用户端界面（角色选择 → 登录 → 老人/子女/社区端）
import App from "./App.tsx";
  import "./index.css";

  createRoot(document.getElementById("root")!).render(<App />);
  