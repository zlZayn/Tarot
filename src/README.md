# src/ — 前端源码与变更路由

## 文件职责（关键导出 / 被谁依赖）
- `index.html`：HTML 结构 + MediaPipe CDN 脚本 + 入口；不承载样式与业务逻辑
- `main.ts`：入口，导入 `styles/app.css` 与 `legacy/app`
- `legacy/app.ts`：原逻辑整体搬运区（已类型化），与原文差异见文件头注释
- `config/assets.ts`：`IMG_URL` / `BACK_URL`，资源路径唯一权威，被 legacy 依赖
- `data/cards.ts`：`TAROT_EN` / `TAROT_CN`（22 张牌数据），被 legacy 依赖
- `i18n/`：`UI_TEXT`（en/zh 聚合），被 legacy 依赖
- `services/records.ts`：`saveDrawSession` / `getDrawSessions`（localStorage），被 legacy 的 dismiss 调用
- `types/tarot.ts`：`TarotCardData` / `Language` 类型
- `types/globals.d.ts`：MediaPipe 全局（`Hands`/`Camera`）声明 + `Element.userData` 遗留约定
- `styles/app.css`：从原 index.html 原样搬运的全部样式

## 变更影响路由
- 改 `config/assets.ts` → 必须 `npm run build` 重建 dist
- 改 `data/cards.ts` / `i18n/` → 检查 legacy 引用是否同步（文案一一对应）
- 改 `legacy/` → 先读 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) 防错清单；改后必跑 [tests/](../tests/README.md)
- 改 `services/records.ts` → schemaVersion 变更需迁移逻辑，先看决策记录

## 参考
- 架构 → [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)