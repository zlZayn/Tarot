"""主题定义（统一颜色语义）。"""
from rich.theme import Theme

THEME = Theme(
    {
        "title": "bold gold1",
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "muted": "dim",
        "hotkey": "bold gold1 on grey19",
    }
)