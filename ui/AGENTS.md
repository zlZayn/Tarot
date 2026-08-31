# ui/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

ui/ 特有约束：
- 只做渲染与交互，不做业务判断（判定在 core/）
- rich 输入统一走 prompts.py，不裸写 Prompt/Confirm 调用
- Windows 控制台 Unicode 输出由 launcher.py 统一 reconfigure