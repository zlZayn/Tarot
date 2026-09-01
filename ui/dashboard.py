"""面板渲染（校验结果表 / 运行态面板）。"""
from __future__ import annotations

import time

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from core.integrity import BuildStatus


def checks_panel(console: Console, status: BuildStatus, meta: dict | None) -> Panel:
    style_map = {"ok": "success", "warn": "warning", "bad": "error"}
    state_ok = "ok" if meta else "warn"
    table = Table(show_header=False, box=None, expand=False)
    rows = [
        ("源码指纹", status.details.get("src_hash", "-"), state_ok),
        ("资源指纹", status.details.get("res_hash", "-"), state_ok),
        ("配置指纹", status.details.get("config_hash", "-"), state_ok),
        ("构建元数据", "有" if meta else "缺失", state_ok),
    ]
    for label, value, state in rows:
        style = style_map[state]
        table.add_row(f"[muted]{label}[/muted]", value[:16], style=style)
    if status.reasons:
        table.add_row("[error]需重建:[/error]", ", ".join(status.reasons), "error")
    else:
        table.add_row("[success]状态[/success]", "与上次构建一致", "success")
    return Panel(table, title="项目完整性", border_style="cyan")


def running_panel(
    console: Console,
    url: str,
    port: int,
    dist: str,
    started_at: float,
    note: str = "",
) -> Panel:
    uptime = max(0, int(time.monotonic() - started_at))
    table = Table(show_header=False, box=None, expand=False)
    table.add_row("[muted]访问地址[/muted]", f"[success]{url}[/success]")
    table.add_row("[muted]端口[/muted]", str(port))
    table.add_row("[muted]服务目录[/muted]", dist)
    table.add_row("[muted]已运行[/muted]", f"{uptime // 60}分 {uptime % 60}秒")
    if note:
        table.add_row("[warning]提示[/warning]", note)
    hotkeys = "[hotkey] O [/hotkey]开浏览器  [hotkey] R [/hotkey]重建  [hotkey] Q [/hotkey]退出"
    return Panel(Group(table, Panel(hotkeys, border_style="grey19")), title="运行中", border_style="green")


def banner(console: Console, app: str, version: str) -> None:
    console.print(Panel(f"[title]{app}[/title]  v{version}", border_style="gold1"))