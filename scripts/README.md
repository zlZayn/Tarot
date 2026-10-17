# scripts/ — 构建与素材辅助脚本

- 职责：承接不进入运行时的辅助脚本（构建后清理、静态素材优化）
- 文件：
    - `clean-dist.mjs`：构建后从 `dist/` 剔除 public 维护双件（`README.md` / `AGENTS.md`），由 `npm run build` 调用
    - `optimize_images.py`：把 `public/textures/` 下 PNG/JPG 批量转 WebP（同分辨率、保留透明通道）。默认删原图，`--dry-run` 只比体积；依赖 dev 组的 `pillow`，跑前 `uv sync`
- 命名：JS 侧 kebab-case（`*.mjs`，随 npm scripts），Python 侧 snake_case（与 `tests/run_checks.py` / `server/serve.py` 一致）
- 变更影响路由：改这里 → 回查根 [AGENTS.md](../AGENTS.md) 的验证快照与相关模块双件
- 使用约束与工作偏好 → 见 [AGENTS.md](AGENTS.md)
