# ui/ — Rich 渲染层

## 文件职责
- `theme.py`：`THEME` 主题（颜色语义统一：success/warning/error/info/title/hotkey）
- `spinners.py`：`Spinner`（Status 上下文管理器，统一加载态文案）
- `prompts.py`：`choose()` 数字菜单、`confirm()` 确认
- `dashboard.py`：`checks_panel()` 完整性表、`running_panel()` 运行态面板、`banner()`

## 被谁依赖
- `launcher.py` 唯一调用方；本层只消费 core 结果，不做业务判断

## 变更影响路由
- 改主题/面板样式 → 不影响逻辑，但保持与根 README 入口表描述一致
- 新增交互 → 优先复用 prompts/spinners，不散写 rich 调用

## 参考
- 设计依据 → [2026-09-01-launcher](../.agents/notes/2026-09-01-launcher.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)