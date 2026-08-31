# Ethereal Tarot

基于 WebGL (Three.js) 的 3D 塔罗牌应用：鼠标与摄像头手势双模式，每次 3 张牌，完成后自动存入浏览器本地（localStorage）。

预览图：[docs/assets/preview.png](docs/assets/preview.png)

## 快速开始

**普通用户 / 朋友（只需要 Python，不需要 Node）**

1. 安装 Python 3（https://www.python.org/downloads/ ）
2. 双击 `Click Me.bat`
3. 浏览器自动打开 `http://localhost:8000`（端口被占用时自动顺延）

**开发者（需要 Node.js ≥ 18 + Python）**

```bash
npm install
npm run dev        # 开发服务器 http://localhost:5173（改代码自动刷新）
npm run build      # 构建发布版到 dist/
```

## 入口文件一览

| 入口 | 用途 | 适用 |
|---|---|---|
| `Click Me.bat` | 启动构建产物 dist（检测 Python / dist，端口顺延，自动开浏览器） | 用户 |
| `Start Dev.bat` | 启动 Vite 开发服务器 | 开发者 |
| `Build.bat` | 类型检查 + 构建 dist | 开发者 |
| `server/serve.py` | 本地静态服务（纯标准库，退出零残留），被 Click Me.bat 调用 | 双方 |

## 操作

- **鼠标**：拖拽浏览牌堆，点击抽牌
- **手势**（右下角 `Camera Off` 切换）：张掌移动光标，握拳选中/确认

## 自定义牌背

1. 新图片放入 `public/textures/backs/`
2. 修改 `src/config/assets.ts` 的 `BACK_URL`
3. `npm run build` 重建

## 测试（可选）

```bash
uv sync                             # 安装测试环境（playwright）
uv run playwright install chromium  # 首次需下载浏览器
uv run python tests/run_checks.py http://localhost:8000   # 资源完整性
uv run python tests/run_e2e.py      http://localhost:8000 # 交互 E2E
```

详细见 [tests/README.md](tests/README.md)。

## 目录结构

```text
├─ Click Me.bat / Start Dev.bat / Build.bat   # 三个入口
├─ src/              # 源码：页面结构、样式、逻辑（legacy/ 为原逻辑搬运区）
├─ public/textures/  # 运行时图片：cards/ 22 张牌面，backs/ 4 张牌背
├─ server/serve.py   # 本地启动器
├─ tests/            # 资源校验与 E2E
├─ docs/             # 架构文档 + 预览图
└─ dist/             # 构建产物（发布包 = dist + Click Me.bat + server/serve.py）
```

## 文档

- 维护索引（规则/命令/待办）→ [AGENTS.md](AGENTS.md)
- 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 决策记录 → [.agents/notes/](.agents/notes/)