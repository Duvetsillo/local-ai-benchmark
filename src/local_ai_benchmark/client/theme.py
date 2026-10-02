from __future__ import annotations

from tkinter import ttk
from typing import Final


COLORS: Final[dict[str, str]] = {
    "canvas": "#070C14",
    "shell": "#0B121C",
    "surface": "#111D2A",
    "surface_elevated": "#172637",
    "surface_interactive": "#21384B",
    "line": "#263B4D",
    "line_strong": "#3A566B",
    "text": "#F4F7FA",
    "text_soft": "#C4CFD9",
    "muted": "#94A6B5",
    "quiet": "#728393",
    "accent": "#75E8C8",
    "accent_hover": "#9AF4D9",
    "glow_mint": "#0B5558",
    "glow_blue": "#1B395E",
    "success": "#9BE0B5",
    "error": "#FF9292",
}

FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": ("Segoe UI", 27, "bold"),
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
