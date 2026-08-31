# Ethereal Tarot

基于 WebGL (Three.js) 的 3D 塔罗牌应用，支持鼠标交互与摄像头手势控制。

预览图：[docs/assets/preview.png](docs/assets/preview.png)

## 普通用户运行（Windows）

1. 安装 Python（https://www.python.org/downloads/ ，无需 Node.js）
2. 双击 `Click Me.bat`
3. 浏览器自动打开 `http://localhost:8000`（端口被占用时自动顺延）

> 注意：必须通过本地 HTTP 服务运行。直接用 `file://` 打开时，图片纹理受浏览器跨域限制无法加载。
> 摄像头手势依赖联网加载 MediaPipe 资源，加载慢时请科学上网。

## 开发者运行

前置：Node.js（≥18）

```bash
npm install        # 安装依赖（three 固定 0.160.0）
npm run dev        # 开发服务器 http://localhost:5173（改代码自动刷新）
npm run build      # 构建发布版到 dist/
npm run typecheck  # TypeScript 类型检查
```

也可以双击 `Start Dev.bat`（开发）或 `Build.bat`（构建）。

## 操作指南

- **鼠标模式**：拖拽浏览牌堆，点击抽牌
- **手势模式**（点击右下角 "Camera Off" 切换）：张掌移动光标，握拳选中/确认

## 抽牌记录

每完成一次 3 张抽牌，浏览器 `localStorage` 写入一条记录（key: `ethereal-tarot:records`，含 `schemaVersion: 1`）。纯本地保存，无后端依赖。

## 测试

```bash
uv sync                             # 安装测试环境（playwright）
uv run playwright install chromium  # 首次需下载浏览器
uv run python tests/run_checks.py http://localhost:8000   # 资源完整性
uv run python tests/run_e2e.py http://localhost:8000      # 交互 E2E
```

详细说明见 [tests/README.md](tests/README.md)。

## 目录结构

```text
├─ Click Me.bat         # 普通用户启动（dist）
├─ Build.bat            # 本地构建
├─ Start Dev.bat        # 本地开发
├─ src/                 # 源码（index.html / main.ts / legacy / config / data / i18n / services / styles / types）
├─ public/textures/     # 运行时图片（cards/ 牌面 0-21，backs/ 牌背）
├─ server/serve.py      # 本地启动器（纯标准库，端口顺延、退出零残留）
├─ tests/               # 资源校验与 E2E 脚本
├─ pyproject.toml       # Python 测试环境（uv 管理，零运行时依赖）
├─ docs/                # 架构文档与预览图
└─ dist/                # 构建产物（发给朋友的就是它 + Click Me.bat + server/serve.py）
```

## 自定义：更换牌背

1. 把新图片放入 `public/textures/backs/`
2. 修改 `src/config/assets.ts` 中的 `BACK_URL`
3. 运行 `npm run build` 重建 `dist/`

牌面/牌背路径只需改这一个文件。

## 给朋友发布包

朋友包 = `dist/` + `Click Me.bat` + `server/serve.py` + `README`（不含 `src/`、`node_modules/`、`.venv/`、`package.json` 等开发文件）。

维护者文档：架构见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，维护索引见 [AGENTS.md](AGENTS.md)。