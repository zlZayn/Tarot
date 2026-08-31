# tests/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

tests/ 特有约束：
- 新增校验必须能在 Windows 无额外服务下运行（纯标准库优先）
- E2E 脚本 stdout/stderr 必须 reconfigure UTF-8（控制台 GBK 会炸 Unicode）
- 测试是验收门槛：业务改动后必须跑通对应脚本再提交
- Python 依赖变更走 uv（`uv lock && uv sync`），禁止 pip 直改全局环境；serve.py 保持零依赖（见 [server/AGENTS.md](../server/AGENTS.md)）