"""加载态封装（Status 上下文管理器，统一文案）。"""
from __future__ import annotations

from rich.console import Console
from rich.status import Status


class Spinner:
    """用法：with Spinner(console, "正在检查...") as s: ..."""

    def __init__(self, console: Console, message: str):
        self._status: Status | None = None
        self._console = console
        self._message = message

    def __enter__(self) -> "Spinner":
        self._status = self._console.status(self._message)
        self._status.start()
        return self

    def update(self, message: str) -> None:
        if self._status:
            self._status.update(message)

    def __exit__(self, *exc) -> None:
        if self._status:
            self._status.stop()