# server/ — 本地启动器（零依赖）

## 文件职责
- `serve.py`：Ethereal Tarot 本地启动器（纯标准库，零依赖）
  - 功能：dist 缺失报错 / 源比 dist 新警告 / 端口 8000 被占用自动顺延 / 同进程服务（退出零残留）/ 自动开浏览器
  - 用法：`python server/serve.py --dir dist [--port 8000] [--open] [--no-check]`
  - 被 `Click Me.bat` 调用（朋友端与开发端共用）

> 开发者的 Rich 版启动器（完整性校验 + 交互面板）在项目根 `launcher.py`，逻辑分 `core/` 与 `ui/`，见 [core/README.md](../core/README.md)。两者同机制（127.0.0.1 同进程服务、零残留），serve.py 保持零依赖供朋友端。

## 变更影响路由
- 改 serve.py 的行为 → 同步更新本 README 与根 README 的"快速开始"节
- Rich 版改行为 → 在 core/、ui/、launcher.py 侧处理，同步其双件与根 README 入口描述

## 参考
- 决策 → [2026-09-01-launcher](../.agents/notes/2026-09-01-launcher.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)