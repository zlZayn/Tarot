"""Ethereal Tarot Rich 启动器（开发者入口）。

流程：完整性检查 → 决策（重建/跳过/详情/退出）→ 构建 → 运行面板（热键 O/R/Q）。
服务与 serve.py 同机制：127.0.0.1 同进程 ThreadingHTTPServer，退出零残留。

用法:
    uv run python launcher.py                # 标准流程
    uv run python launcher.py --check-only   # 只做完整性检查（CI/冒烟）
    uv run python launcher.py --force        # 跳过比对强制重建
    uv run python launcher.py --no-open      # 不自动打开浏览器

退出码: 0 = 正常; 1 = 需重建(--check-only) / 构建失败 / 端口不可用
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from core import builder, config as C, integrity, server
from ui.dashboard import banner, checks_panel, running_panel
from ui.prompts import choose
from ui.spinners import Spinner
from ui.theme import THEME

# Windows 控制台 GBK 无法打印 • 等 Unicode，统一 UTF-8 输出
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def do_build(console: Console) -> tuple[bool, str]:
    with Spinner(console, "正在执行 npm run build ..."):
        ok, tail = builder.run_build()
    if ok:
        integrity.write_meta(
            {
                "src_hash": integrity.src_hash(),
                "res_hash": integrity.res_hash(),
                "config_hash": integrity.config_hash(),
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        )
    return ok, tail


def run_server(console: Console, start_port: int, no_open: bool) -> int:
    try:
        port = server.pick_port(start_port)
    except RuntimeError as e:
        console.print(f"[error]{e}[/error]")
        return 1

    runnable = server.TarotHTTPServer(C.DIST, port)
    runnable.start()
    url = f"http://localhost:{port}"
    if not no_open:
        server.open_browser(url)
    console.print(f"[success]服务已启动: {url}[/success]  (Ctrl+C 退出，Q 关闭)")

    state = {"stop": False, "rebuild": False, "open": False}

    def hotkeys() -> None:
        while not state["stop"]:
            try:
                key = input().strip().upper()
            except EOFError:
                break
            if key in ("Q", "QUIT", "EXIT"):
                state["stop"] = True
            elif key in ("O", "OPEN"):
                state["open"] = True
            elif key in ("R", "REBUILD"):
                state["rebuild"] = True

    threading.Thread(target=hotkeys, daemon=True).start()

    started = time.monotonic()
    try:
        with Live(console=console, refresh_per_second=4) as live:
            while not state["stop"]:
                if state["open"]:
                    state["open"] = False
                    server.open_browser(url, delay=0)
                    live.update(running_panel(console, url, port, str(C.DIST), started, note="已打开浏览器"))
                elif state["rebuild"]:
                    state["rebuild"] = False
                    live.stop()
                    console.print("[warning]正在重建（服务暂停）...[/warning]")
                    runnable.stop()
                    ok, tail = do_build(console)
                    if ok:
                        runnable = server.TarotHTTPServer(C.DIST, port)
                        runnable.start()
                        console.print("[success]重建完成，服务已恢复[/success]")
                        started = time.monotonic()
                    else:
                        console.print(Panel(tail, title="构建失败", border_style="red"))
                        console.print("[warning]继续运行旧版本服务，输入 R 可重试[/warning]")
                        runnable = server.TarotHTTPServer(C.DIST, port)
                        runnable.start()
                    live.start()
                live.update(running_panel(console, url, port, str(C.DIST), started))
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        runnable.stop()
        console.print("[muted]服务已停止（无残留进程）[/muted]")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ethereal Tarot 本地启动器（开发者版）")
    ap.add_argument("--check-only", action="store_true", help="只做完整性检查并退出")
    ap.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    ap.add_argument("--force", action="store_true", help="跳过比对，强制重建")
    ap.add_argument("--port", type=int, default=C.DEFAULT_PORT, help=f"起始端口（默认 {C.DEFAULT_PORT}，被占用自动顺延）")
    args = ap.parse_args(argv)

    console = Console(theme=THEME)
    banner(console, C.APP_NAME, C.APP_VERSION)

    with Spinner(console, "正在检查项目完整性..."):
        status = integrity.check(force=args.force)
    meta = integrity.read_meta()
    console.print(checks_panel(console, status, meta))

    if args.check_only:
        return 0 if not status.need_rebuild else 1

    if status.need_rebuild:
        choice = choose(
            console,
            "构建产物需要更新",
            {
                "1": "立即重新构建（推荐）",
                "2": "跳过构建，使用旧版本运行",
                "3": "查看变更详情",
                "4": "退出",
            },
        )
        if choice == "4":
            return 0
        if choice == "3":
            if status.reasons:
                for r in status.reasons:
                    console.print(f"[warning]原因: {r}[/warning]")
            else:
                console.print("[info]无具体原因（首次/强制模式）[/info]")
            choice = choose(console, "如何处理", {"1": "立即重新构建", "2": "跳过构建，使用旧版本运行", "4": "退出"})
            if choice == "4":
                return 0
        if choice in ("1", "3"):
            ok, tail = do_build(console)
            if not ok:
                console.print(Panel(tail, title="构建失败", border_style="red"))
                return 1
            console.print("[success]构建完成[/success]")

    return run_server(console, args.port, args.no_open)


if __name__ == "__main__":
    sys.exit(main())