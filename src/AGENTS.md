# src/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

src/ 特有约束：
- legacy/ 只搬不重写，改前必读 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) 防错清单
- 数据/文案/配置不许留在 legacy 里新增，一律进 data/、i18n/、config/
- 文案加键只改 `i18n/en.ts`（唯一真源）；`zh.ts` 靠 `satisfies UiText` 编译期逼你补齐，别给 zh 放宽类型来「绕过」报错
- 数据表（`data/cards.ts`）保持 `as const satisfies`，不退回宽注解
- 新模块放 services/、utils/ 等新区，保持与 legacy 的调用点最小化
- 文件职责与导出见 [README.md](README.md)，本文件不写"有什么"