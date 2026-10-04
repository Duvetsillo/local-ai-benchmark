"""One set of materials, typography and interaction tokens for the desktop UI."""

from pathlib import Path

COLORS = {
    "canvas": "#080A0F",
    "surface": "#11151E",
    "elevated": "#1A2030",
    "text": "#F5F7FA",
    "muted": "#A0A8B8",
    "quiet": "#929AAA",
    "accent": "#8BA8FF",
    "success": "#9BE0B5",
    "warning": "#F2C879",
    "error": "#FF9292",
    "line": "#272D3A",
}
ASSETS = Path(__file__).parent / "assets"
RADIUS = 16
MOTION_MS = 200

STYLES = """
QWidget { color: #F5F7FA; font-family: Inter; font-size: 13px; }
QMainWindow, QDialog { background: #080A0F; }
QLabel { background: transparent; }
QLabel[role="eyebrow"] { color: #8BA8FF; font-size: 11px; font-weight: 600; }
QLabel[role="muted"] { color: #A0A8B8; }
QLabel[role="quiet"] { color: #929AAA; font-size: 12px; }
QLabel[role="h1"] { font-size: 30px; font-weight: 600; }
QLabel[role="h2"] { font-size: 19px; font-weight: 600; }
QLabel[role="h3"] { font-size: 14px; font-weight: 600; }
QLabel[role="metric"] { font-size: 25px; font-weight: 600; }
QLabel[role="hero"] { font-size: 35px; font-weight: 600; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #161C28; border: 1px solid #343D50; border-radius: 9px;
    padding: 10px 12px; min-height: 18px; selection-background-color: #394E79;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #8BA8FF; }
QLineEdit:disabled, QComboBox:disabled { color: #929AAA; background: #11151E; }
QComboBox::drop-down { width: 28px; border: none; }
QComboBox::down-arrow { image: url(__CHEVRON__); width: 14px; height: 14px; }
QComboBox QAbstractItemView { background: #1A2030; border: 1px solid #343D50; padding: 6px; selection-background-color: #304164; }
QSpinBox::up-button, QDoubleSpinBox::up-button { width: 20px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { width: 20px; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 6px 0; }
QScrollBar::handle:vertical { background: #343D50; border-radius: 4px; min-height: 36px; }
QScrollBar::handle:vertical:hover { background: #526582; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { height: 8px; background: transparent; }
QScrollBar::handle:horizontal { background: #343D50; border-radius: 4px; min-width: 36px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
QPlainTextEdit { background: #0C1018; border: none; border-radius: 12px; padding: 14px; font-family: Consolas; font-size: 12px; selection-background-color: #394E79; }
QTableWidget { background: transparent; alternate-background-color: #151B26; border: none; gridline-color: transparent; selection-background-color: #293A5C; selection-color: #F5F7FA; }
QTableWidget::item { padding: 12px; border: none; }
QHeaderView::section { color: #A0A8B8; background: #121722; padding: 14px; border: none; font-size: 11px; font-weight: 600; }
QTableWidget:focus { border: 1px solid #8BA8FF; border-radius: 8px; }
QCheckBox { spacing: 10px; padding: 7px 0; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #526582; border-radius: 5px; background: #161C28; }
QCheckBox::indicator:checked { background: #8BA8FF; image: url(__CHECK__); }
QCheckBox::indicator:focus { border: 2px solid #F5F7FA; }
QToolTip { color: #F5F7FA; background: #232B3D; border: 1px solid #46526A; border-radius: 6px; padding: 8px; }
""".replace("__CHEVRON__", (ASSETS / "chevron-down-light.svg").as_posix()).replace(
    "__CHECK__", (ASSETS / "check.svg").as_posix()
)
