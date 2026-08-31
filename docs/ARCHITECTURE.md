# Ethereal Tarot 架构说明

## 项目一句话
- 原生 HTML/CSS/JS + Three.js 的 3D 塔罗牌应用，Vite + TypeScript 工程化整理，不引入前端框架。

## 设计决策（不变，改动需先推翻决策记录）
- 构建：Vite 5，`root=src`、`base="./"`、`publicDir=../public`、`outDir=../dist`；构建后 `scripts/clean-dist.mjs` 剔除 public 维护双件
- 依赖：three 固定 `0.160.0`（npm 本地化，与原 CDN import map 同版本、同模块文件）
- 手部识别：MediaPipe CDN 经典脚本保留（全局 `Hands` / `Camera`），`three/addons` 经 npm 解析
- 资源：全部在 `public/textures/`，路径唯一权威 `src/config/assets.ts`（`IMG_URL` / `BACK_URL`）
- 记录：`localStorage`（key `ethereal-tarot:records`，`schemaVersion: 1`），无后端
- 启动：`server/serve.py` 纯标准库（端口顺延、同进程服务零残留、dist 过期提示）
- Python 工具链：uv 管理（`pyproject.toml` + `uv.lock` + `.python-version` 3.12.10）；运行时零依赖，测试用 dev 组 playwright

## 分层
- `src/index.html`：HTML 结构 + CDN 脚本 + 入口（不再含样式与业务脚本）
- `src/main.ts`：入口，导入样式与 legacy
- `src/legacy/app.ts`：原内联脚本整体搬运区（`@ts-nocheck`），与原文差异只有三处（见文件头注释）
- `src/config/` `src/data/` `src/i18n/` `src/services/` `src/types/` `src/styles/`：配置 / 数据 / 文案 / 服务 / 类型 / 样式
- `public/textures/`：运行时图片（cards/ 0-21.jpg，backs/ bm*.jpg|png）
- `server/serve.py`：本地启动器
- `tests/`：资源校验 + 交互 E2E
- `docs/assets/`：README 预览图（原 42MB 大图，不进入 dist）

## 数据流（不变契约）
- 页面加载 → `main.ts` → `legacy/app.ts`：加载 22 张牌面纹理 + 牌背 → loader 移除 → 洗牌入场
- 交互（鼠标/手势）→ 选牌 → 翻牌 SHOW → 连抽 3 张 → SPREAD_VIEW → 历史组回顾 REVIEW_VIEW
- 第 3 张收起时写入一条抽牌记录（新功能，不影响任何原流程）

## 防错清单（改代码前必读）
- legacy 区禁止重构、禁止"顺手修 bug"；只允许新增无副作用调用点
- `IMG_URL` / `BACK_URL` 只在 `assets.ts` 改；改后必须 `npm run build` 重建 dist
- 文案只在 `data/cards.ts`（牌数据）与 `i18n/`（UI 文案）改，与 legacy 内引用一一对应
- dist 只由 `npm run build` 生成，手工改动一律会被覆盖（build 含 clean-dist 后置清理）
- public 双件不改名放（AGENTS.md 需精确文件名才能被注入）；dist 洁净由 tests/run_checks.py 防回归
- 换牌背/换牌面图片：文件放 `public/textures/` 对应子目录，不要动 `src/` 里的引用写法
- 任何改动后跑 `tests/`（P0：run_checks + run_e2e）