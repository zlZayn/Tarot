# Ethereal Tarot — 维护索引

## 文档地图
- 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 模块手册 → [src/README.md](src/README.md)
- 测试说明 → [tests/README.md](tests/README.md)
- 启动器说明 → [server/README.md](server/README.md)
- 决策记录 → [.agents/notes/](.agents/notes/)

## 全局规则
- legacy/ 只搬不重写；改它必须先读 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 的防错清单
- 资源路径唯一权威：`src/config/assets.ts`，改后必须 `npm run build`
- 文案唯一权威：`src/data/cards.ts` + `src/i18n/`，不留在 legacy
- three 固定 0.160.0，不升级不换加载方式（理由见决策记录）

## 常用命令
- 前端：`npm run dev` · `npm run build` · `npm run typecheck`
- Python 测试环境：`uv sync`（变更 py 依赖后 `uv lock && uv sync`）
- 运行：`python server/serve.py --dir dist --open`
- 测试：`uv run python tests/run_checks.py http://localhost:8000` · `uv run python tests/run_e2e.py http://localhost:8000`（首次 `uv run playwright install chromium`）

## 验证快照（2026-09-01）
- typecheck: 0 error
- build: Vite 5.4.21 通过；dist = 26 textures + index.html + 2 assets，无文档文件（clean-dist 生效）
- run_checks: 26/26 OK（含 dist 根禁止文件防回归），HTTP 全 200
- run_e2e: dist + dev 双端通过（抽 3 张 + localStorage 断言 + 截图）；uv 环境（.venv + playwright 1.62.0）复跑通过

## 待办
- [ ] 完整 Rich 启动器（core/ui 分层 + 哈希校验 + 面板交互），见 [2026-09-01-launcher](.agents/notes/2026-09-01-launcher.md)
- [ ] 渐进去除 `src/legacy/app.ts` 的 `@ts-nocheck`
- [ ] 可选：Python 记录后端（先 localStorage，需求出现再上）

## 活跃坑
- 编辑器原子保存会在 src/ 生成 `*.tmpdir` 临时目录，chokidar Windows 上 EBUSY 崩溃；vite.config.ts 已忽略，勿扩监视范围
- Windows 控制台 GBK 打印 `•` 等 Unicode 会崩；Python 脚本统一 reconfigure UTF-8
- Vite publicDir 会把 public/ 里的维护双件拷进 dist，且 closeBundle 钩子早于拷贝执行（删了会被拷回）；必须用构建后置脚本 scripts/clean-dist.mjs
- .bat 文件禁止中文/非 ASCII：cmd 按 GBK 解析 UTF-8 中文注释会把括号块拆碎（if/exit 失效、乱码命令）；bat 一律纯 ASCII，中文说明写 README