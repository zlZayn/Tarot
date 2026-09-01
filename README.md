# Ethereal Tarot 🔮

<div style="width: 260px; margin: 15px 0; border-radius: 8px; overflow: hidden; box-shadow: 0 3px 8px rgba(139, 69, 19, 0.15);">
  <a href="https://github.com/zlZayn/Tarot" target="_blank">
    <img src="docs/assets/preview.jpg" alt="虚幻塔罗牌" style="width: 100%; height: auto; display: block; cursor: pointer;">
  </a>
</div>

这是一个基于 WebGL (Three.js) 的 3D 塔罗牌应用程序，支持鼠标交互与摄像头手势控制。
每次抽牌完成会自动保存到浏览器本地（3 张牌与正逆位），下次打开随时回顾。

## 🪄 快速开始

**朋友 / 普通用户**：装好 Python，两步打开。

1. 安装 [Python](https://www.python.org/downloads/)（不需要 Node.js）
2. 双击 `Click Me.bat`，浏览器自动打开（端口被占用时自动顺延）

打不开图？塔罗牌纹理依赖本地 HTTP 服务：不用脚本时，可以用 [VS Code Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) 打开 `dist/` 目录。
摄像头手势模式需要联网加载 MediaPipe 资源，加载慢时可尝试科学上网。

## 🖐️ 操作指南

* **鼠标模式**：
    * **拖拽**：左右滑动浏览牌堆。
    * **点击**：抽取选中的牌。


* **手势模式**（需开启摄像头，点击右下角 "Camera Off" 切换模式）：
    * **张掌**：移动光标浏览。
    * **握拳**：选中/确认。

## 🛠️ 自定义设置

### 更换牌背图案

默认牌背是 `bm4.png`，可自由替换：

1. 把新图片（`.png` 或 `.jpg`）放入 `public/textures/backs/`。
2. 打开 `src/config/assets.ts`，修改 `BACK_URL`：

```javascript
const BACK_URL = "./textures/backs/bm4.png";
// 改成你的文件，例如：
const BACK_URL = "./textures/backs/my_back.jpg";
```

3. 运行 `npm run build` 重新构建，刷新网页生效。

## 🧑‍💻 开发者

**前置**：Node.js ≥ 18 与 Python（经 uv 管理）。

**常用命令**

```bash
npm install        # 安装依赖
npm run dev        # 开发服务器 http://localhost:5173（改代码自动刷新）
npm run build      # 构建发布版到 dist/
npm run typecheck  # 类型检查
```

**四个启动入口**

| 入口 | 用途 | 适用 | 依赖 |
|---|---|---|---|
| `Click Me.bat` | 启动构建产物 `dist/`，端口顺延，自动开浏览器 | 朋友 / 普通用户 | 仅 Python |
| `Start Dev.bat` | 启动 Vite 开发服务器（改代码自动刷新，热更新） | 开发者 | Node.js |
| `Build.bat` | 类型检查 + 构建 `dist/`（发布前必跑） | 开发者 | Node.js |
| `Rich Launcher.bat` | Rich 面板：构建过期检测、确认重建、运行（O 开浏览器 / R 重建 / Q 退出） | 开发者 | Node.js + uv |

**测试**

资源校验与交互 E2E 见 [tests/README.md](tests/README.md)，命令速查见 [AGENTS.md](AGENTS.md)。

**发布与分享**

- **发布新版本**：打 `v*` 标签，GitHub Actions 自动完成构建、测试、打包并上传 Releases：

```bash
git tag v1.0.0
git push --tags
```

- **给朋友**：分享 [Releases 页面](https://github.com/zlZayn/Tarot/releases) 的最新 zip——解压后双击 `Click Me.bat` 即可运行。
zip 只含 `dist/` + `Click Me.bat` + `server/serve.py`，无任何开发文件，朋友不需要 Node / uv / pip。

### 📂 项目结构

为了确保程序正常运行，请保持文件结构完整，**不要移动、删除或重命名文件与素材**。

```text
Ethereal Tarot/
├── Click Me.bat           # 🟢 启动脚本（朋友用，仅需 Python）
├── Start Dev.bat          # 📝 开发服务器（Vite 热更新）
├── Build.bat              # 🔨 构建 dist（类型检查 + 构建）
├── Rich Launcher.bat      # 🧙 开发者 Rich 面板（需 uv）
├── server/serve.py        # 本地服务器（被 Click Me.bat 调用，端口占用自动顺延）
├── launcher.py            # 开发者启动器（Rich 面板 + 构建过期检测）
├── core/ ui/              # 启动器核心逻辑层 / 渲染层（被 launcher.py 使用）
├── dist/                  # 网页程序本体 (npm run build 生成)
│   ├── index.html         # 主程序入口
│   └── textures/          # 素材文件夹
│       ├── backs/         # 牌背图片 (bm.jpg, bm2.png, bm3.png, bm4.png)
│       └── cards/         # 牌面图片 (0.jpg 愚者 ~ 21.jpg 世界，共 22 张)
└── src/                   # 源码文件夹
    ├── index.html         # 页面结构
    ├── config/assets.ts   # 图片路径配置（改图片路径改这里）
    └── ...                # 样式 / 逻辑 / 牌数据 / 多语言模块
```

## 📖 文档

* 维护索引（规则 / 命令 / 待办）→ [AGENTS.md](AGENTS.md)
* 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
* 决策记录 → [.agents/notes/](.agents/notes/)