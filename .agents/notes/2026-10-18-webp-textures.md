# 决策：纹理统一转 WebP（2026-10-18）

状态：生效

## 问题
- `dist/` 首屏 46MB，其中纹理占 45.6MB：4 张牌背 5.8–8.4MB（其中 3 张是无压缩 RGBA PNG），22 张牌面各约 1MB 的 JPG。
- 部署到 2 核 1.7G 小带宽云主机后，纯 IP 分享给他人时首屏加载慢；`caddy` 的 gzip 对已经压缩过的 JPG/PNG 几乎无效。

## 决策
- `public/textures/` 下 26 张纹理**全量转 WebP**（Pillow，`quality=85`、`method=6`、`alpha_quality=100`，保持原分辨率与原透明通道），原 PNG/JPG 删除（git 历史可找回）。
- 转换工具落在 `scripts/optimize_images.py`（默认删原图，`--dry-run` 只比体积；Pillow 进 `pyproject.toml` dev 组）。
- 路径收口在 `src/config/assets.ts`：文件内私有 `CARDS_DIR` / `BACKS_DIR` / `EXT`，对外只暴露 `BACK_URL` 与 `cardUrl(id)`；`legacy/app.ts` 两处硬编码 `.jpg` 改为调用 `cardUrl()`（文件头 changelog 第 8 条）。
- 顺带把静态站点部署到 `110.41.40.11`（Caddy 静态服务，`/www/wwwroot/tarot`，属主 `caddy:caddy`，755/644）。

## 替代方案（强制）
- 保留 JPG/PNG 只开 `encode gzip`：对已压缩格式几乎零收益，实测达不到体积目标。
- 转 AVIF：压缩率更好，但 Pillow 12 的 AVIF 编码支持依赖外部插件、且老浏览器/老设备兼容面更窄，收益不足以换兼容风险。
- 降分辨率（如牌面 1086×1810 → 720×1200）：会损失 Three.js 贴图清晰度（牌面在翻牌/特写视角下可辨识），且属视觉降级，越过了「不改视觉表现」的既有约束。
- 只在构建期用 Vite 插件压缩：能把转换排除出仓，但需要新增构建依赖并处理 `public/` 不进 bundle 的现实，收益低于一个 26 行脚本。

## 影响
- 纹理 45.6MB → 11.2MB（-75%），`dist/` 46.1MB → 11.7MB；实测线上单张牌背 660KB、牌面约 386KB。
- 新增 dev 依赖 `pillow`（仅素材维护时用，运行时零影响）。
- 换牌背/换牌面的流程变化：放新图后建议先跑一次 `uv run python scripts/optimize_images.py`，再改 `assets.ts` 里的 `BACK_URL`（或牌面 id），最后 `npm run build`。
- 格式迁移有测试兜底但不等于格式锁死：`tests/run_checks.py` 对 `public/textures` 与 `dist/textures` 做集合比对，漏拷/新增未同步会直接红；但它不校验后缀与 `assets.ts` 是否一致 —— 若将来把某张图换回 `.jpg` 而忘记改 `EXT`，只有 E2E 的贴图加载能发现。
- 未来若换 AVIF 或改质量档，必须单独测视觉并更新本记录。
