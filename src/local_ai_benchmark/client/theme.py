from __future__ import annotations

from tkinter import ttk
from typing import Final


COLORS: Final[dict[str, str]] = {
    "canvas": "#050505",
    "shell": "#0B0B0B",
    "surface": "#111111",
    "surface_elevated": "#171717",
    "surface_interactive": "#242424",
    "line": "#303030",
    "line_strong": "#424242",
    "text": "#EEEEEE",
    "text_soft": "#C8C8C8",
    "muted": "#8C8C8C",
    "quiet": "#666666",
    "accent": "#D8D8D8",
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
