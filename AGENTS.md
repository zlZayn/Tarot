# Ethereal Tarot — 维护索引

## 文档地图
- 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 模块手册 → [src/README.md](src/README.md)
- 启动器（Rich）→ [core/README.md](core/README.md) · [ui/README.md](ui/README.md)
- 启动器（零依赖）→ [server/README.md](server/README.md)
- CI/Release → [.github/workflows/README.md](.github/workflows/README.md)
- 测试说明 → [tests/README.md](tests/README.md)
- 决策记录 → [.agents/notes/](.agents/notes/)

## 全局规则
- legacy/ 只搬不重写；改它必须先读 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 的防错清单
- 资源路径唯一权威：`src/config/assets.ts`，改后必须 `npm run build`
- **类型严格面（现值，改配置要同批改这里）**：`tsconfig.json` 为 `strict: false` + `allowJs: true` + `checkJs: false`，`noUncheckedIndexedAccess` 与 `exactOptionalPropertyTypes` **均未开**；`npm run typecheck` 的判据因此只是「TS 在宽松档下不报错」。兄弟仓（AIA / ATC / imagora）三开关全开，本仓要不要对齐**未决** —— 成本集中在 `src/legacy/app.ts`（受保护的搬运区，占 `src` 八成行）
- 文案唯一权威：`src/data/cards.ts` + `src/i18n/`，不留在 legacy
- three 固定 0.160.0，不升级不换加载方式（理由见决策记录）

## 常用命令
- 前端：`npm run dev` · `npm run build` · `npm run typecheck`
- Python 测试环境：`uv sync`（变更 py 依赖后 `uv lock && uv sync`）
- 开发者启动器：双击 `Rich Launcher.bat`，或 `uv run python launcher.py`（`--check-only` 只做完整性检查；`--force` 强制重建）
- 运行（轻量）：`python server/serve.py --dir dist --open`
- 测试：`uv run python tests/run_checks.py http://localhost:8000` · `uv run python tests/run_e2e.py http://localhost:8000`（首次 `uv run playwright install chromium`）
- 发布：打 `v*` tag 推送 → GitHub Actions 自动构建/测试/打包/上传 Releases（见 [.github/workflows/README.md](.github/workflows/README.md)）；手动包则用 `Build.bat` + `Rich Launcher.bat` 校验后复制 dist + bat + serve.py

## 验证快照（2026-09-24 复核；产物与资源类结论沿用 2026-09-01 实跑）
- typecheck: 0 error —— **口径要说清：本仓 `strict: false`，这是最弱配置下的「0 error」，不等于类型安全**（见全局规则那条）
- build: Vite 5.4.21 通过；dist = 26 textures + index.html + 2 assets，无文档文件（clean-dist 生效）
- run_checks: 不带 URL 时只比清单（打印 `public=26 dist=26`，含 dist 根禁止文件防回归）；带 URL 时另外发 **27** 次 GET（入口页 + 26 张纹理）全 200
- run_e2e: dist + dev 双端通过（抽 3 张 + localStorage 断言 + 截图）；uv 环境（.venv + playwright 1.62.0）复跑通过
- launcher: 冒烟通过（首次判定重建 / build 后免重建 / 源码变更触发 / 8000 占用顺延 8001 / Q 退出零残留）

## 待办
- [ ] 前端单测要不要开：**曾是「legacy 无纯函数可测」而暂缓**（见 [.agents/notes/2026-09-01-testing-as-gate.md](.agents/notes/2026-09-01-testing-as-gate.md)），但前提已变 —— `services/records.ts`、`i18n/`、`data/cards.ts` 现在都是可测纯模块。要动就先裁范围（只测非 legacy 那三个），别顺手引 vitest 全家桶
- 其余无当前待办（决策/否决历史见 [.agents/notes/](.agents/notes/)；迁移、类型化、Rich 启动器均已完成）

## 活跃坑
- 编辑器原子保存会在 src/ 生成 `*.tmpdir` 临时目录，chokidar Windows 上 EBUSY 崩溃；vite.config.ts 已忽略，勿扩监视范围
- Windows 控制台 GBK 打印 `•` 等 Unicode 会崩；三个 Python 入口（`launcher.py` / `tests/run_e2e.py` / `tests/run_checks.py`）都 reconfigure UTF-8，加第四个时照抄那段
- Vite publicDir 会把 public/ 里的维护双件拷进 dist，且 closeBundle 钩子早于拷贝执行（删了会被拷回）；必须用构建后置脚本 scripts/clean-dist.mjs
- `uv.lock` 的 URL 曾经是**机器全局**配置的结果，不是仓库选择：`AppData\Roaming\uv\uv.toml` 里的 `index-url` 指向 tuna 镜像，任何配了镜像的机器跑 plain `uv lock` 都会把 90 条 URL 写回镜像。项目群约定「锁文件 `resolved` 必须官方源」，Python 侧**已按 pin 官方 index 落定**：`pyproject.toml` 里 `[[tool.uv.index]]` = `https://pypi.org/simple` + `default = true`，安装源由仓自决、与本机配置无关；`uv lock --check` 就是这条的执行体（红了即有人改了源或锁漂了）。**代价要知道**：这条改变所有协作者与 CI 的 `uv` 安装源（要镜像加速得显式改，别指望偷偷用本机全局配置 —— 那正是这次修掉的东西）。当初另一条路（手工洗 URL 不动配置）已实测为假修：`uv lock --check` 当场红，下次 `uv lock` 就回退
- 本仓 4 个 `.bat` 是纯 ASCII + **LF**，实测 cmd 能容忍；兄弟仓约定 `.cmd` 必须 CRLF + GBK —— 别拿那条来「顺手改行尾」，要改先在这行留下结论
- .bat 文件禁止中文/非 ASCII：cmd 按 GBK 解析 UTF-8 中文注释会把括号块拆碎（if/exit 失效、乱码命令）；bat 一律纯 ASCII，中文说明写 README