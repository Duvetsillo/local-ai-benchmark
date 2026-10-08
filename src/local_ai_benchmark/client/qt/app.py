"""Aetherion Studio's native Qt shell, keyboard commands and desktop entrypoint."""

from __future__ import annotations

import ctypes
import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QIcon,
    QKeySequence,
    QPainter,
    QPixmap,
    QShortcut,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from .components import (
    Backdrop,
    Badge,
    BrandMark,
    Button,
    NavButton,
    Sheet,
    Spinner,
    Surface,
    column,
    divider,
    fade_in,
    label,
    row,
    scroll_page,
    svg_data,
)
from .controller import StudioController
from .pages import (
    AuthPage,
    Benchmark,
    DownloadSheet,
    Hardware,
    Models,
    Records,
    Settings,
    Workspace,
    field,
)
from .tokens import ASSETS, COLORS, STYLES

NAVIGATION = [
    ("workspace", "Workspace", "layout-dashboard"),
    ("models", "Models", "box"),
    ("benchmarks", "Benchmark", "flask-conical"),
    ("results", "Results", "chart-no-axes-column"),
    ("history", "History", "history"),
    ("hardware", "Hardware", "cpu"),
    ("settings", "Settings", "settings-2"),
]


def system_reduced_motion():
    if os.name != "nt":
        return False
    enabled = ctypes.c_int(1)
    # SPI_GETCLIENTAREAANIMATION follows the Windows accessibility preference.
    ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0)
    return not bool(enabled.value)


def initialize_application():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Aetherion Studio")
    app.setWindowIcon(QIcon(str(ASSETS / "brand-symbol.svg")))
    app.setOrganizationName("Aetherion")
    app.setStyle("Fusion")
    font_id = QFontDatabase.addApplicationFont(str(ASSETS / "Inter.ttf"))
    families = QFontDatabase.applicationFontFamilies(font_id)
    font = QFont(families[0] if families else "Segoe UI")
    font.setPixelSize(13)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)
    app.setStyleSheet(STYLES)
    palette = app.palette()
    from PySide6.QtGui import QPalette

    for role, color in (
        (QPalette.Window, COLORS["canvas"]),
        (QPalette.Base, COLORS["surface"]),
        (QPalette.Text, COLORS["text"]),
        (QPalette.WindowText, COLORS["text"]),
        (QPalette.Button, COLORS["elevated"]),
        (QPalette.ButtonText, COLORS["text"]),
        (QPalette.Highlight, "#304164"),
        (QPalette.HighlightedText, COLORS["text"]),
    ):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    return app


class StudioWindow(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self.setWindowTitle("AETHERION STUDIO — Beyond the known.")
        self.controller = controller or StudioController(parent=self)
        self.reduced_motion = self.controller.preferences.get(
            "reduce_motion", system_reduced_motion()
        )
        QApplication.instance().setProperty("reduce_motion", self.reduced_motion)
        QApplication.instance().setProperty(
            "glass", self.controller.preferences.get("glass", True)
        )
        available = QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(
            min(1040, available.width() - 40), min(700, available.height() - 60)
        )
        self.resize(
            min(1440, available.width() - 100), min(940, available.height() - 100)
        )
        self.active_view = "workspace"
        self._allow_close = False
        self.root = Backdrop()
        self.setCentralWidget(self.root)
        root_layout = column(self.root, 0, 0)
        self.gate_stack = QStackedWidget()
        root_layout.addWidget(self.gate_stack)
        self.auth_page = AuthPage(self)
        self.gate_stack.addWidget(scroll_page(self.auth_page))
        self.shell = QWidget()
        self.gate_stack.addWidget(self.shell)
        self.build_shell()
        self.controller.changed.connect(self.refresh)
        self.controller.auth_changed.connect(self.on_auth)
        self.controller.notification.connect(self.notify)
        self.controller.password_change_required.connect(
            self.auth_page.require_password_change
        )
        self.controller.download_event.connect(self.on_download)
        self.on_auth()
        for i, (key, _name, _icon) in enumerate(NAVIGATION, 1):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda key=key: self.navigate(key))
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.command_shortcut.activated.connect(self.command_palette)
        self.run_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.run_shortcut.activated.connect(self.run_from_shortcut)
        self.find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.find_shortcut.activated.connect(self.focus_search)
        QTimer.singleShot(0, self.apply_native_chrome)

    def build_shell(self):
        shell = row(self.shell, 0)
        self.sidebar = Surface(glass=True)
        self.sidebar.setFixedWidth(212)
        sidebar = column(self.sidebar, (14, 24, 14, 20), 6)
        brand = row(gap=10)
        brand.addWidget(BrandMark(36))
        branding = column(None, 0, 5)
        name = label("AETHERION", "h3")
        name.setStyleSheet("font-size: 14px; font-weight: 600; letter-spacing: 1px;")
        branding.addWidget(name)
        branding.addWidget(label("BEYOND THE KNOWN.", "quiet"))
        brand.addLayout(branding, 1)
        sidebar.addLayout(brand)
        sidebar.addSpacing(26)
        self.nav_buttons = {}
        for i, (key, name, icon) in enumerate(NAVIGATION):
            if i == 4:
                sidebar.addSpacing(16)
                sidebar.addWidget(divider())
                sidebar.addSpacing(16)
            button = NavButton(
                name, icon, lambda _checked=False, key=key: self.navigate(key)
            )
            button.setToolTip(f"{name} · Ctrl+{i + 1}")
            sidebar.addWidget(button)
            self.nav_buttons[key] = button
        sidebar.addStretch()
        local = Surface()
        local_body = column(local, 14, 7)
        local_body.addWidget(label("LOCAL INFERENCE", "eyebrow"))
        self.runtime_status = label(self.controller.status, "quiet", True)
        local_body.addWidget(self.runtime_status)
        sidebar.addWidget(local)
        sidebar.addSpacing(12)
        self.account_label = label("", "quiet", True)
        sidebar.addWidget(self.account_label)
        shell.addWidget(self.sidebar)
        main = QWidget()
        body = column(main, (30, 8, 30, 0), 20)
        toolbar = row()
        self.breadcrumb = label("Studio   /   Workspace", "quiet")
        toolbar.addWidget(self.breadcrumb, 1)
        self.spinner = Spinner()
        toolbar.addWidget(self.spinner)
        self.connection_badge = Badge("LOCAL WORKSPACE", "muted")
        toolbar.addWidget(self.connection_badge)
        quick = Button("Quick actions", "command", "ghost", self.command_palette)
        quick.setToolTip("Search commands · Ctrl+K")
        toolbar.addWidget(quick)
        body.addLayout(toolbar)
        self.notice = Surface(glass=True)
        notice_body = row(self.notice, 14)
        notice_body.setContentsMargins(16, 12, 10, 12)
        self.notice_title = label("", "eyebrow")
        self.notice_text = label("", "muted", True)
        notice_body.addWidget(self.notice_title)
        notice_body.addWidget(self.notice_text, 1)
        dismiss = Button(icon="x", kind="ghost", callback=self.notice.hide)
        dismiss.setAccessibleName("Dismiss notification")
        notice_body.addWidget(dismiss)
        self.notice.hide()
        body.addWidget(self.notice)
        self.notice_timer = QTimer(self)
        self.notice_timer.setSingleShot(True)
        self.notice_timer.timeout.connect(self.notice.hide)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: transparent; }")
        self.pages = {
            "workspace": Workspace(self),
            "models": Models(self),
            "benchmarks": Benchmark(self),
            "results": Records(self),
            "history": Records(self, history=True),
            "hardware": Hardware(self),
            "settings": Settings(self),
        }
        self.page_areas = {}
        for key, page in self.pages.items():
            area = scroll_page(page)
            self.page_areas[key] = area
            self.stack.addWidget(area)
        for key in ("results", "history"):
            shortcut = QShortcut(QKeySequence("Return"), self.pages[key].table)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(self.pages[key].open_selected)
        body.addWidget(self.stack, 1)
        shell.addWidget(main, 1)
        self.navigate("workspace")

    def qt_icon(self, name, color=COLORS["muted"]):
        ratio = self.devicePixelRatioF()
        pixmap = QPixmap(round(20 * ratio), round(20 * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        from PySide6.QtCore import QRectF

        QSvgRenderer(svg_data(name, color)).render(painter, QRectF(0, 0, 20, 20))
        painter.end()
        return QIcon(pixmap)

    def navigate(self, key):
        if key not in self.pages:
            return
        if (
            self.gate_stack.currentIndex() == 0
            and self.controller.auth_session is None
            and self.isVisible()
        ):
            return
        previous = self.active_view
        self.active_view = key
        self.stack.setCurrentWidget(self.page_areas[key])
        for name, button in self.nav_buttons.items():
            button.active = name == key
            button.setAccessibleDescription("Selected" if button.active else "")
            button.update()
        title = next(name for name, text, _icon in NAVIGATION if name == key)
        display = next(text for name, text, _icon in NAVIGATION if name == title)
        self.breadcrumb.setText(f"Studio   /   {display}")
        if key != previous:
            fade_in(self.page_areas[key])

    def on_auth(self):
        session = self.controller.auth_session
        self.gate_stack.setCurrentIndex(1 if session else 0)
        if session:
            self.account_label.setText(
                f"{session.username}\n{session.plan.capitalize()} · {'Offline access' if session.offline else 'Signed in'}"
            )
            self.controller.refresh_hardware()
            self.controller.monitor_timer.start()
            if not self.controller.models:
                self.controller.refresh_models()
            self.pages["settings"].refresh()
        else:
            for key in ("password", "new_password", "confirm", "license_key"):
                self.auth_page.entries[key][1].clear()
            self.auth_page.set_mode("login")

    def refresh(self, key):
        self.runtime_status.setText(self.controller.status)
        self.spinner.set_running(self.controller.busy)
        self.connection_badge.setText(
            "RUNNING"
            if self.controller.run_status == "running"
            else "DISCOVERING"
            if self.controller.busy
            else f"{len(self.controller.models)} LOCAL MODELS"
        )
        self.pages["workspace"].refresh(key)
        self.pages["models"].refresh(key)
        self.pages["benchmarks"].refresh(key)
        if key in {"run", "models"}:
            self.pages["results"].refresh()
            self.pages["history"].refresh()
        if key == "hardware":
            self.pages["hardware"].refresh()
        self.pages["settings"].refresh()

    def prepare_model(self, name):
        if self.controller.busy:
            return
        self.pages["benchmarks"].model.setCurrentText(name)
        self.navigate("benchmarks")

    def choose_folder(self):
        if self.controller.busy or "download" in self.controller.pending:
            self.notify(
                "Finish the active operation before changing the model folder.",
                "warning",
            )
            return
        selected = QFileDialog.getExistingDirectory(
            self,
            "Choose GGUF model folder",
            str(self.controller.session.gguf_provider.models_dir),
        )
        if selected:
            self.controller.set_model_folder(selected)

    def open_results(self):
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(self.controller.session.results_dir.resolve()))
        )

    def open_downloader(self):
        DownloadSheet(self).exec()

    def on_download(self, kind, payload):
        if kind == "download":
            self.notify(f"Model saved: {Path(payload).name}", "success")
        elif kind == "error":
            self.notify(str(payload), "error")

    def notify(self, message, tone="info"):
        self.notice_timer.stop()
        self.notice_title.setText(tone.upper())
        self.notice_title.setStyleSheet(f"color: {COLORS.get(tone, COLORS['accent'])};")
        self.notice_text.setText(str(message))
        self.notice.show()
        fade_in(self.notice)
        # Errors persist until dismissed so long explanations stay readable.
        if tone not in {"error", "warning"}:
            self.notice_timer.start(10000)

    def set_preference(self, key, value):
        self.controller.save_preference(key, value)
        QApplication.instance().setProperty(key, value)
        if key == "reduce_motion":
            self.reduced_motion = value
        self.root.update()
        for surface in self.findChildren(Surface):
            surface.update()
        self.apply_native_chrome()

    def command_palette(self):
        if self.controller.auth_session is None:
            return
        sheet = Sheet(self, "Quick actions", "Navigate without leaving the keyboard.")
        search = QLineEdit()
        search.setPlaceholderText("Search commands…")
        field(sheet.body, "Command", search)
        commands = [
            (f"Open {name}", icon, lambda key=key: self.navigate(key))
            for key, name, icon in NAVIGATION
        ]
        commands += [
            ("Refresh local models", "refresh-cw", self.controller.refresh_models),
            ("Add a model", "download", self.open_downloader),
            ("Open reports folder", "folder", self.open_results),
        ]
        buttons = []

        def activate(callback):
            sheet.accept()
            QTimer.singleShot(0, callback)

        for name, icon, callback in commands:
            button = Button(
                name,
                icon,
                "ghost",
                lambda _checked=False, callback=callback: activate(callback),
            )
            sheet.body.addWidget(button)
            buttons.append(button)

        def filter_commands(text):
            for button in buttons:
                button.setVisible(text.casefold() in button.text().casefold())

        search.textChanged.connect(filter_commands)
        search.returnPressed.connect(
            lambda: next((b for b in buttons if b.isVisible()), buttons[0]).click()
        )
        search.setFocus()
        sheet.exec()

    def inspect_record(self, record):
        sheet = Sheet(
            self,
            record.get("benchmark", "Experiment record"),
            f"{record.get('run_id', '')} · {record.get('status', 'unknown')}",
        )
        from PySide6.QtWidgets import QPlainTextEdit

        report = QPlainTextEdit(json.dumps(record, indent=2, ensure_ascii=False))
        report.setReadOnly(True)
        report.setAccessibleName("Saved benchmark JSON record")
        report.setMinimumHeight(280)
        report.setMaximumHeight(max(280, self.height() - 300))
        sheet.body.addWidget(report)
        actions = row()
        actions.addWidget(
            Button(
                "Export JSON", "download", callback=lambda: self.export_record(record)
            )
        )
        full = record.get("notes", {}).get("benchmark_results_file")
        if full and Path(full).is_file():
            actions.addWidget(
                Button(
                    "Full task report",
                    "external-link",
                    callback=lambda: QDesktopServices.openUrl(
                        QUrl.fromLocalFile(str(Path(full).resolve()))
                    ),
                )
            )
        sheet.body.addLayout(actions)
        sheet.exec()

    def export_record(self, record):
        name = f"{record.get('run_id', 'aetherion-record')}.json"
        target, _filter = QFileDialog.getSaveFileName(
            self, "Export benchmark record", name, "JSON reports (*.json)"
        )
        if target:
            try:
                Path(target).write_text(
                    json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                self.notify("Report exported.", "success")
            except OSError as exc:
                self.notify(str(exc), "error")

    def run_from_shortcut(self):
        if self.active_view == "benchmarks" and self.controller.auth_session:
            self.pages["benchmarks"].run()

    def focus_search(self):
        if self.controller.auth_session and self.active_view in {
            "models",
            "results",
            "history",
        }:
            self.pages[self.active_view].search.setFocus()

    def apply_native_chrome(self):
        if os.name != "nt":
            return
        try:
            dwm = ctypes.windll.dwmapi
            handle = int(self.winId())
            dwm.DwmSetWindowAttribute.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.c_uint,
            ]
            for attribute, value in (
                (20, 1),
                (33, 2),
                (38, 2 if self.controller.preferences.get("glass", True) else 1),
                (35, 0x00120E0B),
                (36, 0x00FAF7F5),
            ):
                number = ctypes.c_int(value)
                dwm.DwmSetWindowAttribute(
                    handle, attribute, ctypes.byref(number), ctypes.sizeof(number)
                )
        except (AttributeError, OSError):
            pass  # Windows 10 / non-DWM environments retain the solid material.

    def closeEvent(self, event):
        if not self._allow_close and (
            self.controller.busy or "download" in self.controller.pending
        ):
            sheet = Sheet(
                self,
                "An operation is in progress",
                "Closing requests cancellation. Completed task reports remain saved locally.",
            )
            actions = row()
            actions.addWidget(Button("Keep working", callback=sheet.reject))
            actions.addWidget(
                Button("Stop and close", kind="primary", callback=sheet.accept)
            )
            sheet.body.addLayout(actions)
            if sheet.exec() != Sheet.Accepted:
                event.ignore()
                return
        self.controller.close()
        event.accept()


def launch_desktop_app():
    app = initialize_application()
    window = StudioWindow()
    window.show()
    QTimer.singleShot(100, window.controller.restore)
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_desktop_app()
