# public/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

public/ 特有约束：
- 只放运行时必需资源（textures）；预览大图放 docs/assets/
- 图片文件不做压缩/改名/换格式，除非单独决策
- 文件名即契约（cards/ 的 0-21.jpg 对应牌 id），改前先看 [README.md](README.md)