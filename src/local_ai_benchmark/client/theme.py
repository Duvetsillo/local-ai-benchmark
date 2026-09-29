from __future__ import annotations

from tkinter import ttk
from typing import Final


COLORS: Final[dict[str, str]] = {
    "canvas": "#080B10",
    "shell": "#0D1117",
    "surface": "#131A22",
    "surface_elevated": "#1C2733",
    "surface_interactive": "#253444",
    "line": "#283747",
    "line_strong": "#35485B",
    "text": "#F1F5F9",
    "text_soft": "#C5D0DC",
    "muted": "#91A0B2",
    "quiet": "#708196",
    "accent": "#67E8C5",
    "success": "#91E2B2",
    "error": "#FF9D9D",
}

FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": ("Segoe UI", 24, "bold"),
    "section": ("Segoe UI", 9, "bold"),
    "body": ("Segoe UI", 9, "normal"),
    "small": ("Segoe UI", 8, "normal"),
    "mono": ("Consolas", 8, "normal"),
}


def configure_ttk(style: ttk.Style) -> None:
    style.theme_use("clam")
    style.configure(
        "Aetherion.TCombobox",
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["accent"],
        bordercolor=COLORS["line_strong"],
        lightcolor=COLORS["line_strong"],
        darkcolor=COLORS["line_strong"],
        padding=(10, 9),
    )
    style.map(
        "Aetherion.TCombobox",
        fieldbackground=[("readonly", COLORS["surface"]), ("disabled", COLORS["canvas"])],
        foreground=[("readonly", COLORS["text"]), ("disabled", COLORS["quiet"])],
        selectbackground=[("readonly", COLORS["surface_interactive"])],
    )
    style.configure(
        "Aetherion.Vertical.TScrollbar",
        background="#252525",
        troughcolor=COLORS["canvas"],
        bordercolor=COLORS["canvas"],
        arrowcolor="#999999",
    )
    style.configure(
        "Aetherion.Horizontal.TProgressbar",
        troughcolor="#242424",
        background=COLORS["accent"],
        bordercolor="#242424",
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
    )
