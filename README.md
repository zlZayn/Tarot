# Ethereal Tarot 🔮

<div style="width: 260px; margin: 15px 0; border-radius: 8px; overflow: hidden; box-shadow: 0 3px 8px rgba(139, 69, 19, 0.15);">
  <a href="https://github.com/zlZayn/Tarot" target="_blank">
    <img src="docs/assets/preview.png" alt="虚幻塔罗牌" style="width: 100%; height: auto; display: block; cursor: pointer;">
  </a>
</div>

这是一个基于 WebGL (Three.js) 的 3D 塔罗牌应用程序，支持鼠标交互与摄像头手势控制。
每次抽牌完成会自动保存到浏览器本地（3 张牌与正逆位），下次打开随时回顾。

## 📂 目录结构 (Directory Structure)

为了确保程序正常运行，请保持文件结构完整，**不要移动、删除或重命名文件与素材**。

```text
Ethereal Tarot/
├── Click Me.bat           # 🟢 启动脚本 (Windows)
├── server/serve.py        # 本地服务器（被 Click Me.bat 调用，端口占用自动顺延）
├── dist/                  # 网页程序本体 (npm run build 生成)
│   ├── index.html         # 主程序入口
│   └── textures/          # 素材文件夹
│       ├── backs/         # 牌背图片 (bm.jpg, bm2.png, bm3.png, bm4.png)
│       └── cards/         # 牌面图片 (0.jpg 愚者 ~ 21.jpg 世界，共 22 张)
└── src/                   # 源码文件夹（开发者用）
    ├── index.html         # 页面结构
    ├── config/assets.ts   # 图片路径配置（改图片路径改这里）
    └── ...                # 样式 / 逻辑 / 牌数据 / 多语言模块
```

> 分享给朋友只需这三部分：`dist/` + `Click Me.bat` + `server/serve.py`。

## 🪄 如何使用 (How to Use)

本项目专为 Windows 环境设计，利用 Python 快速启动本地服务。

### 前置要求

* 电脑上必须安装 **Python** (用于运行本地服务器)。

> 或者：VS Code + Live Server（核心目的都是启动本地 HTTP 服务，规避图片跨域限制）

### 启动步骤

1. 下载本项目全部文件（源码包不含 `dist/`，需先运行 `Build.bat` 或 `npm run build` 生成）。
2. 直接双击根目录下的 **`Click Me.bat`** 文件。
3. 脚本会自动启动服务器，并调用默认浏览器打开应用 (端口被占用时会自动顺延)。

> **注意**：如果不使用脚本，你需要手动在 `dist` 目录下开启一个 HTTP 服务器（如 Live Server），否则图片纹理将无法加载（CORS 跨域限制）。外部资源加载可能较慢，有必要时科学上网。

## 🖐️ 操作指南

* **鼠标模式**：
    * **拖拽**：左右滑动浏览牌堆。
    * **点击**：抽取选中的牌。


* **手势模式 (需开启摄像头，点击右下角 "Camera Off" 切换模式)**：
    * **张掌**：移动光标浏览。
    * **握拳**：选中/确认。

## 🛠️ 自定义设置 (Customization)

### 更换牌背图案

你可以更改塔罗牌背面的图案（默认为 `bm4.png`）。

1. 将你想要的图片（推荐 .png 或 .jpg）放入 `public/textures/backs/` 文件夹中。
2. 使用记事本或代码编辑器打开 `src/config/assets.ts`。
3. 搜索关键词 `BACK_URL` 并修改文件名：

```javascript
// 修改前
const BACK_URL = "./textures/backs/bm4.png";

// 修改后 (假设你的新图片叫 my_back.jpg)
const BACK_URL = "./textures/backs/my_back.jpg";
```

4. 运行 `npm run build` 构建。
5. 刷新网页即可生效新牌背。

## 🧑‍💻 开发者 (Developer)

* 前置：Node.js ≥ 18 与 Python。
* `npm install` 安装依赖，`npm run dev` 启动开发服务器 (`http://localhost:5173`，改代码自动刷新)。
* `npm run build` 构建发布版到 `dist/`；`npm run typecheck` 做类型检查。
* 测试与维护文档见 [tests/README.md](tests/README.md) 与 [AGENTS.md](AGENTS.md)。

## 📖 文档

* 维护索引（规则 / 命令 / 待办）→ [AGENTS.md](AGENTS.md)
* 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
* 决策记录 → [.agents/notes/](.agents/notes/)