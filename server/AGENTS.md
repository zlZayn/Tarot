# server/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

server/ 特有约束：
- 必须保持纯标准库（零第三方依赖）—— 朋友端没有 pip 环境
- Rich 启动器逻辑在 `core/` + `ui/` + 根 `launcher.py`，不落本目录
- 服务机制（同进程、零残留）与 launcher 保持一致，避免双份行为