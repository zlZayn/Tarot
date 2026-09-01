# workflows/ — CI/Release 配置

## 文件职责
- `release.yml`：v* tag 触发，构建 → 测试 → 打包 zip → 上传 Releases（softprops/action-gh-release@v2）

## 变更影响路由
- 改发布包内容（新增/移除文件）→ 同步 root `README.md` 的"给朋友发布"段与 `release.yml` 的 assemble 步骤
- 改测试流程 → 步骤 "Start server and run checks + E2E"，与 `tests/README.md` 一致

## 参考
- 规则 → [../AGENTS.md](../AGENTS.md)、根 [AGENTS.md](../../AGENTS.md)
- 决策 → [2026-09-01-github-actions-release](../../.agents/notes/2026-09-01-github-actions-release.md)