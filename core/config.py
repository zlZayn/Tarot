"""全局常量（路径 / 端口 / 文件名）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

# 构建元数据：放项目根而非 dist/（Vite emptyOutDir 会清空 dist）
BUILD_META = ROOT / ".ethereal-meta.json"
META_VERSION = 1

# 参与过期的文件后缀（src）
SRC_EXTS = {".ts", ".css", ".html"}
# 参与过期的直接散列文件
CONFIG_FILES = ("vite.config.ts", "tsconfig.json", "package.json", "package-lock.json", "pyproject.toml")

DEFAULT_PORT = 8000
MAX_PORT_TRY = 10
APP_NAME = "Ethereal Tarot"
APP_VERSION = "0.1.0"