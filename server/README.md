# server/ — 本地启动器

## 文件职责
- `serve.py`：Ethereal Tarot 本地启动器（纯标准库，零依赖）
  - 功能：dist 缺失报错 / 源比 dist 新警告 / 端口 8000 被占用自动顺延 / 同进程服务（退出零残留）/ 自动开浏览器
  - 用法：`python server/serve.py --dir dist [--port 8000] [--open] [--no-check]`
  - 被 `Click Me.bat` 调用（朋友端与开发端共用）

## 变更影响路由
- 改 serve.py 的行为 → 同步更新本 README 与根 README 的"普通用户运行"段
- 完整 Rich 版启动器实施时替换本文件所在模块，见根 AGENTS.md 待办

## 参考
- 决策 → [2026-09-01-launcher](../.agents/notes/2026-09-01-launcher.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)