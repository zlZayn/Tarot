"""core/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

core/ 特有约束：
- 零 Rich 依赖（纯逻辑层，可独立测试）：任何 rich 导入进 core/ 即违规，放 ui/
- 路径一律经 config.py，不写死本机路径
- 判定函数（integrity.check）保持纯函数风格，便于冒烟验证