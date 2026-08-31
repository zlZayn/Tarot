"""npm 构建执行（纯逻辑）。"""
from __future__ import annotations

import subprocess
import sys


def run_build(log_lines: list[str] | None = None) -> tuple[bool, str]:
    """执行 npm run build；返回 (成功与否, 尾部日志)。"""
    cmd = ["npm.cmd", "run", "build"] if sys.platform == "win32" else ["npm", "run", "build"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return False, "[Error] npm 未找到，请安装 Node.js"
    text = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(text.splitlines()[-12:])
    if log_lines is not None:
        log_lines.extend(text.splitlines())
    return proc.returncode == 0, tail