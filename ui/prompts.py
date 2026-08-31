"""交互封装（菜单选择 / 确认，统一默认值与样式）。"""
from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm, Prompt


def choose(console: Console, title: str, options: dict[str, str], default: str | None = None) -> str:
    """数字菜单：返回选中的键（options 的键即显示序号字符串）。"""
    console.print(f"\n[title]{title}[/title]")
    for key, label in options.items():
        console.print(f"  [info][{key}][/info] {label}")
    prompt = f"选择 [{default or '1'}]: " if default else "选择: "
    return Prompt.ask(prompt, choices=list(options), default=default or "1")


def confirm(console: Console, message: str, default: bool = True) -> bool:
    return Confirm.ask(message, default=default)