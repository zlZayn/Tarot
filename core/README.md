# core/ — Rich 启动器核心逻辑

## 文件职责
- `config.py`：路径 / 端口 / 文件名常量（唯一权威）
- `integrity.py`：`check()` → `BuildStatus`（need_rebuild + reasons）；src/public/config 三指纹 + 元数据 + 产物存在性
- `builder.py`：`run_build()` 执行 `npm run build`，返回 (成功, 尾部日志)
- `server.py`：`TarotHTTPServer`（127.0.0.1 同进程，start/stop/wait）、`pick_port()`、`open_browser()`

## 被谁依赖
- `launcher.py`（入口）组合各模块；`ui/` 只消费 core 的结果渲染

## 变更影响路由
- 改指纹维度/判定 → 同步测试与 `docs/ARCHITECTURE.md` 防错清单（若涉及判定契约）
- 改端口逻辑 → 同步 `core/README.md` 用法与根 README 入口表

## 参考
- 设计依据 → [2026-09-01-launcher](../.agents/notes/2026-09-01-launcher.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)