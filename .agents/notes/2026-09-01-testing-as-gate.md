# 决策：测试即验收，不引入运行时守护（2026-09-01）

已实施：是

## 问题
- "不改变逻辑"的重构无法靠肉眼证明；补充审查建议运行时 AssetValidator / 错误降级 / .env 环境分层。

## 决策
- 质量保障落在 `tests/`：`run_checks.py`（public↔dist 清单对比 + HTTP 全 200）+ `run_e2e.py`（Playwright：加载、UI 文案、连抽 3 张、展开/回顾视图、localStorage 断言、截图存档）。
- 任何改动后跑 tests 作为验收门槛；typecheck 并入 Build.bat 流程。
- 不实施运行时改动：AssetValidator（阻塞式预检改变启动行为，原代码已有 fallback 纹理）、错误分级降级（改变原版行为）、`.env`（`base:"./"` 已统一 dev/dist 相对路径，无子目录部署需求）。

## 替代方案（强制）
- 运行时 AssetValidator：启动变慢 + 失败提示行为与原件不一致，被 tests 的 HTTP 全量校验替代。
- 像素级视觉对比：3D 场景初始位置随机（洗牌/offset 随机），必误报；改用结构断言 + 交互断言 + 截图存档供人眼抽查。
- vitest/jest 单元测试：legacy 无纯函数可测（依赖全局 DOM/THREE），引入框架成本大于收益，P3 暂缓。

## 影响
- 验收可自动复现；被否决方案记录在案，避免未来重提。