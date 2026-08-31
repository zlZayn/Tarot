# public/ — 静态资源（textures）

- `textures/cards/0.jpg ~ 21.jpg`：22 张牌面（文件名即牌 id，勿改）
- `textures/backs/bm.jpg、bm2.png、bm3.png、bm4.png`：牌背（默认 bm4.png）
- 构建时 textures 原样拷入 dist/；本目录的维护双件（README.md/AGENTS.md）被 `scripts/clean-dist.mjs` 排除，不进发布包

## 变更影响路由
- 换牌背：文件放 `backs/`，改 `src/config/assets.ts` 的 `BACK_URL`，重建 dist
- 新增/删除/改名图片 → 必须同步更新引用方，并跑 `uv run python tests/run_checks.py` 校验清单

## 参考
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)