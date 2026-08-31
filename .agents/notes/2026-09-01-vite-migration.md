# 决策：Vite + TypeScript 工程化迁移（2026-09-01）

已实施：是

## 问题
- 巨型单文件 HTML（内联 CSS + 内联脚本 + 图片平铺 + 启动 bat）不可维护、不可继续开发。
- 硬约束：不重写 Three.js 逻辑、不改交互、不改视觉表现、不换 CDN 依赖版本。

## 决策
- 主方案：Vite 5 + TypeScript + 原生 HTML/CSS/JS/Three.js，不引入任何前端框架。
- 原内联脚本整体搬运到 `src/legacy/app.ts` 并以 `@ts-nocheck` 起步，与原文差异仅三处（文件头注释声明）：three 改为 npm 解析、数据/文案/配置改为 import、新增记录保存调用点。
- CSS 原样搬入 `src/styles/app.css`；HTML 只留结构与 CDN 脚本。
- 图片移入 `public/textures/`（cards/ + backs/），路径唯一权威 `src/config/assets.ts`。
- 开发 `npm run dev`，发布 `npm run build` → `dist/`，朋友仍双击 `Click Me.bat` 经 Python 静态服务运行。

## 替代方案（强制）
- 逐步手拆原 HTML 的脚本为多个小文件：第一阶段边界不清，先整体搬运更稳，稳定后再拆（见待办）。
- React/Vue 包装：框架收益低于破坏 Three.js 原有代码的风险，不引入。
- 保留 import map + CDN three：Vite 会重写裸导入，import map 不生效，必须让 'three' 可被 bundler 解析（见 three 本地化决策）。
- Electron/Tauri：朋友需装运行时或依赖变重，超出"零新增依赖"约束。

## 影响
- 收益：模块化、可构建、可测试、可继续开发。
- 代价：新增 node_modules 与构建步骤（开发侧），朋友侧体验不变。