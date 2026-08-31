# 决策：three 依赖 npm 本地化（2026-09-01）

已实施：是

## 问题
- 原 index.html 用 import map 从 unpkg CDN 加载 three@0.160.0。
- Vite 会把源码中的裸导入 `import * as THREE from 'three'` 交给 bundler 解析，不读浏览器 import map；不装 npm 包则 dev/build 直接失败。

## 决策
- `npm install three@0.160.0`（精确锁版本，与 CDN 完全同版本、同模块文件 `build/three.module.js`）。
- `three/addons/*` 由 npm 包 exports 映射解析，与原 `examples/jsm/` 路径同文件。
- MediaPipe 四个 CDN 经典脚本原样保留（全局 `Hands`/`Camera`，无 npm 等价替代且不改代码签名）。

## 替代方案（强制）
- 保留 import map：Vite bundler 不认，失败。
- 下载 CDN 文件进 `public/vendor/`：可行但等于手动 vendoring，无收益还失去 npm 版本管理。
- 升级 three：违反"不换 CDN 依赖版本"约束，fixed 0.160.0。

## 影响
- 运行时行为与原来逐字节一致（同版本），加载方式从网络 CDN 变为本地打包（反而更快、更稳）。
- 未来升级 three 必须单独测试并更新本记录。