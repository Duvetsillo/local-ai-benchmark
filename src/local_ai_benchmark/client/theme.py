from __future__ import annotations

from tkinter import ttk
from typing import Final


COLORS: Final[dict[str, str]] = {
    "canvas": "#080D14",
    "shell": "#0B121B",
    "surface": "#101A26",
    "surface_elevated": "#172536",
    "surface_interactive": "#20364A",
    "line": "#25394B",
    "line_strong": "#3B566C",
    "text": "#F5F8FB",
    "text_soft": "#CDD7E1",
    "muted": "#9AABBA",
    "quiet": "#788B9C",
    "accent": "#70E6C1",
    "accent_hover": "#9AF2D6",
    "glow_mint": "#0B5558",
    "glow_blue": "#1B395E",
    "success": "#91E5B1",
    "error": "#FF8E8E",
}

FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": ("Segoe UI", 29, "bold"),
    "section": ("Segoe UI", 9, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "small": ("Segoe UI", 9, "normal"),
    "mono": ("Consolas", 9, "normal"),
}


def configure_ttk(style: ttk.Style) -> None:
    style.theme_use("clam")
    style.configure(
        "Aetherion.TCombobox",
        fieldbackground=COLORS["surface_elevated"],
        background=COLORS["surface_elevated"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["accent"],
        bordercolor=COLORS["line_strong"],
        lightcolor=COLORS["line_strong"],
        darkcolor=COLORS["line_strong"],
        padding=(10, 9),
        font=("Segoe UI", 10),
    )
    style.map(
        "Aetherion.TCombobox",
        fieldbackground=[("readonly", COLORS["surface_elevated"]), ("disabled", COLORS["canvas"])],
        foreground=[("readonly", COLORS["text"]), ("disabled", COLORS["quiet"])],
        selectbackground=[("readonly", COLORS["surface_interactive"])],
        selectforeground=[("readonly", COLORS["text"])],
    )
    style.configure(
        "Aetherion.Vertical.TScrollbar",
        background=COLORS["surface_interactive"],
        troughcolor=COLORS["surface"],
        bordercolor=COLORS["surface"],
        arrowcolor=COLORS["muted"],
        width=10,
    )
    style.configure(
        "Aetherion.Horizontal.TProgressbar",
        troughcolor=COLORS["surface_elevated"],
        background=COLORS["accent"],
        bordercolor=COLORS["surface_elevated"],
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
    )
