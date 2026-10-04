from __future__ import annotations

from tkinter import ttk
from typing import Final


COLORS: Final[dict[str, str]] = {
    "canvas": "#080C12",
    "shell": "#080C12",
    "surface": "#101823",
    "surface_elevated": "#172130",
    "surface_interactive": "#26364D",
    "line": "#26313F",
    "line_strong": "#526582",
    "text": "#EDF2F7",
    "text_soft": "#CAD9F4",
    "muted": "#A4B0C0",
    "quiet": "#A4B0C0",
    "accent": "#8EAFFF",
    "accent_hover": "#CAD9F4",
    "primary": "#EDF2F7",
    "primary_hover": "#CAD9F4",
    "warning": "#F2C879",
    "hero": "#101823",
    "glow_mint": "#172130",
    "glow_blue": "#293C68",
    "success": "#9BE0B5",
    "error": "#FF9292",
}

FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": ("Segoe UI", 32, "bold"),
    "title": ("Segoe UI", 30, "bold"),
    "metric": ("Segoe UI", 17, "bold"),
    "button": ("Segoe UI", 9, "bold"),
    "section": ("Segoe UI", 9, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "small": ("Segoe UI", 9, "normal"),
    "mono": ("Consolas", 9, "normal"),
}


def configure_ttk(style: ttk.Style) -> None:
    style.theme_use("clam")
    style.configure("Studio.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                    foreground=COLORS["text_soft"], borderwidth=0, rowheight=42, font=FONTS["body"])
    style.configure("Studio.Treeview.Heading", background=COLORS["surface_elevated"],
                    foreground=COLORS["text"], relief="flat", padding=(12, 12), font=FONTS["section"])
    style.map("Studio.Treeview", background=[("selected", COLORS["surface_interactive"])],
              foreground=[("selected", COLORS["text"])])
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
        bordercolor=[("focus", COLORS["accent"]), ("disabled", COLORS["line"])],
        arrowcolor=[("disabled", COLORS["quiet"]), ("active", COLORS["accent_hover"])],
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
        thickness=6,
    )
