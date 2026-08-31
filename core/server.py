"""本地 HTTP 服务（同进程 ThreadingHTTPServer：退出即零残留）。"""
from __future__ import annotations

import socket
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import config as C


def pick_port(start: int = C.DEFAULT_PORT) -> int:
    for port in range(start, start + C.MAX_PORT_TRY):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"端口 {start}~{start + C.MAX_PORT_TRY - 1} 均被占用")


class TarotHTTPServer(ThreadingHTTPServer):
    """在守护线程中运行的可停止服务器。绑定 127.0.0.1，不暴露局域网。"""

    def __init__(self, dist: Path, port: int):
        handler = partial(SimpleHTTPRequestHandler, directory=str(dist))
        super().__init__(("127.0.0.1", port), handler)
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.shutdown()
        self.server_close()

    def wait(self, timeout: float | None = None) -> None:
        if self._thread is not None:
            self._thread.join(timeout)


def open_browser(url: str, delay: float = 0.6) -> None:
    threading.Timer(delay, lambda: webbrowser.open(url)).start()