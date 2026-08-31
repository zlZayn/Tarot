# 决策：抽牌记录用 localStorage（2026-09-01）

已实施：是

## 问题
- 需要"简单保存抽牌记录"，且不改变任何前端表现与交互。

## 决策
- 第一阶段用浏览器 `localStorage`（key `ethereal-tarot:records`），`src/services/records.ts` 提供 `saveDrawSession` / `getDrawSessions`。
- 每次完整 3 张抽牌在 `dismiss()` 触发点时写入一条记录：`{id, time, schemaVersion: 1, language, mode, cards:[{id,isRev}]}`。
- 仅新增调用点，不触碰任何 UI；存储失败静默降级（try/catch）。

## 替代方案（强制）
- Python 记录后端（`server/record_server.py` 静态托管 + POST /api/records）：朋友端要升级启动脚本、引入 CORS 与数据文件；需求未出现，第二阶段再评估。
- 引入 StorageAdapter 兼容旧 key：原项目无任何 localStorage 数据，无旧数据可兼容，属过度设计；以 `schemaVersion: 1` 留迁移口子。

## 影响
- 零依赖、零 CORS、朋友双击流程完全不变。
- 数据在浏览器本机，换浏览器/清缓存即丢失（可接受，需求是"简单保存"）。