# .github/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

.github/ 特有约束：
- workflow 必须保持"发布包零开发文件"约束（dist + bat + serve.py）
- 测试步骤不豁免已知失败：CI 红 = 先修测试，不许加 continue-on-error 掩盖
- 本目录不设 README.md：GitHub 的默认 README 优先级会展示 `.github/README.md` 而非根 README；文档层在 [workflows/README.md](workflows/README.md)