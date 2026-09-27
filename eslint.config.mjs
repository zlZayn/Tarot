import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  {
    // .venv/ 是 Python 虚拟环境（内含 Playwright 打包的 JS），dist/ 与 tests/artifacts/
    // 是构建与测试产物：都不是本仓源码，必须排除（ESLint 默认只忽略 node_modules 与 .git）。
    // src/legacy/ 是受保护的搬运区（只搬不重写，见 AGENTS.md 全局规则），
    // 不纳入 lint —— 让它变红就等于要求重写它。
    ignores: ["dist/**", "node_modules/**", ".venv/**", "tests/artifacts/**", "src/legacy/**"],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    // 前端源码跑在浏览器里。
    languageOptions: {
      globals: { ...globals.browser },
    },
  },
  {
    // 构建脚本与 vite 配置跑在 Node 里。
    files: ["vite.config.ts", "*.config.ts", "scripts/**/*.mjs"],
    languageOptions: {
      globals: { ...globals.node },
    },
  },
  eslintConfigPrettier,
];
