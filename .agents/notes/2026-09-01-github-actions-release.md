# 决策：GitHub Actions Release 自动化（2026-09-01）

已实施：是

## 问题
- 手动发布费时且易错：每次都要本地 build、打包、上传，且无法保证发布包经过测试。

## 决策
- `.github/workflows/release.yml`：打 `v*` tag 触发 GitHub Actions。
- 流水线：checkout → setup-node(20) + `npm ci` + `npm run build` → setup-uv + `uv sync` → `playwright install --with-deps chromium` → 起 `serve.py` 跑 `run_checks` + `run_e2e` → 组装发布包（仅 dist + Click Me.bat + server/serve.py）→ zip `Ethereal-Tarot-{tag}.zip` → `softprops/action-gh-release@v2` 上传。
- 发布包零开发文件（node_modules/src/.venv/tests/docs 不打包）；bat 无法在 Ubuntu 实测，仅保证打包正确，运行验证留本地。
- CI 红 = 先修测试，不做 continue-on-error 掩盖（写入 .github/AGENTS.md 规则）。

## 替代方案（强制）
- 手动发布（现状）：易漏测、无审计，被自动化取代。
- 本地上传 zip 脚本：仍无统一 CI 证据，且朋友拿不到 Release 链接。
- PR 触发的独立 test workflow：有价值但本阶段先保证发布链；test 已内嵌发布链中。

## 影响
- 打 tag 即得到"构建 + 测试通过 + 可下载 zip"的完整 Release；朋友下载 Releases 资产即可运行。
- 首次 tag 由实施验证（v0.1.0）。