# tests/ — 测试与校验

## 测试对应关系
| 脚本 | 覆盖 | 运行条件 |
|------|------|----------|
| `run_checks.py` | 资源完整性：public↔dist 清单对比 + HTTP 全 200 | 有服务器更佳；无服务器也跑清单部分 |
| `run_e2e.py` | 交互 E2E：加载、UI 文案、连抽 3 张、展开/回顾视图、localStorage 断言、截图 | 服务器运行中 + uv 环境（见下方用法） |

## 用法（uv 管理测试环境）

```bash
uv sync                             # 安装环境（playwright，见根 pyproject.toml）
uv run playwright install chromium  # 首次需下载浏览器
npm run build
python server/serve.py --dir dist   # 或 python -m http.server 8000 --directory dist
uv run python tests/run_checks.py http://localhost:8000
uv run python tests/run_e2e.py http://localhost:8000     # 对 dev 用 http://localhost:5173
```

## 说明
- 截图产物在 `tests/artifacts/`（gitignore），供人眼抽查；删除可随时重生成
- E2E 采用结构+交互断言（3D 场景初始随机，像素比对会误报）
- 失败即故障：先读输出定位，不要盲目重跑

## 参考
- 为何这样设计（被否决方案）→ [2026-09-01-testing-as-gate](../.agents/notes/2026-09-01-testing-as-gate.md)
- 规则 → [AGENTS.md](AGENTS.md)、根 [AGENTS.md](../AGENTS.md)