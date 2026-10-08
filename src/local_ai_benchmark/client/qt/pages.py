"""Task-focused native desktop pages, backed exclusively by actual local data."""

from __future__ import annotations

import datetime as dt
import importlib.util
import shutil

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHeaderView,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from ..auth import get_service_url, machine_fingerprint
from .catalog import MODEL_DOWNLOAD_CATALOG, TASK_SUITE_DESCRIPTIONS
from .components import (
    Badge,
    BrandMark,
    Button,
    ChipArt,
    Icon,
    Progress,
    Sheet,
    SpeedChart,
    Surface,
    column,
    divider,
    label,
    row,
)
from .tokens import COLORS


def gb(value):
    return f"{value:.1f} GB" if isinstance(value, (int, float)) else "Unavailable"


def local_date(value):
    try:
        return dt.datetime.fromisoformat(value).astimezone().strftime("%d %b · %H:%M")
    except (ValueError, AttributeError, TypeError):
        return "Date unavailable"


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())


def field(layout, title, widget, helper=None):
    title_label = label(title, "h3")
    title_label.setBuddy(widget)
    widget.setAccessibleName(title)
    layout.addWidget(title_label)
    layout.addWidget(widget)
    if helper:
        layout.addWidget(label(helper, "quiet", True))


class Page(QWidget):
    def __init__(self, window, title, description):
        super().__init__()
        self.window, self.controller = window, window.controller
        self.body = column(self, (0, 0, 4, 12), 24)
        self.heading = row()
        copy = column(None, 0, 7)
        copy.addWidget(label(title, "h1"))
        copy.addWidget(label(description, "muted", True))
        self.heading.addLayout(copy, 1)
        self.body.addLayout(self.heading)

    def actions(self, *widgets):
        for widget in widgets:
            self.heading.addWidget(widget, 0, Qt.AlignTop)


class HardwareStrip(Surface):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = row(self, 0)
        layout.setContentsMargins(20, 20, 20, 20)
        self.values, self.notes = {}, {}
        for index, (key, name, icon) in enumerate(
            (
                ("cpu", "PROCESSOR", "cpu"),
                ("gpu", "GRAPHICS", "layers"),
                ("ram", "MEMORY", "memory-stick"),
                ("vram", "AVAILABLE VRAM", "zap"),
            )
        ):
            cell = QWidget()
            cell.setMinimumWidth(110)
            body = column(cell, (14, 0, 14, 0), 9)
            caption = row(gap=8)
            caption.addWidget(Icon(icon, 16))
            caption.addWidget(label(name, "quiet"), 1)
            body.addLayout(caption)
            self.values[key] = label("Detecting…", "h3", True)
            self.notes[key] = label("Reading this device", "quiet", True)
            body.addWidget(self.values[key])
            body.addWidget(self.notes[key])
            layout.addWidget(cell, 1)
            if index < 3:
                line = QWidget()
                line.setFixedWidth(1)
                line.setStyleSheet("background: rgba(255,255,255,10);")
                layout.addWidget(line)

    def refresh(self):
        hardware = self.controller.session.hardware
        if not hardware:
            return
        cpu, ram = hardware.get("cpu", {}), hardware.get("memory", {})
        gpu = next(
            (g for g in hardware.get("gpu", []) if g.get("name") != "UNKNOWN"), {}
        )
        self.values["cpu"].setText(cpu.get("model", "Unavailable"))
        self.notes["cpu"].setText(
            f"{cpu.get('cores') or '—'} cores · {cpu.get('threads') or '—'} threads"
        )
        self.values["gpu"].setText(gpu.get("name", "Not detected"))
        self.notes["gpu"].setText(f"{gb(gpu.get('vram_gb'))} total VRAM")
        self.values["ram"].setText(gb(ram.get("total_gb")))
        self.notes["ram"].setText(f"{gb(ram.get('available_gb'))} available")
        self.values["vram"].setText(gb(gpu.get("free_vram_gb")))
        self.notes["vram"].setText(
            "Latest NVIDIA reading"
            if isinstance(gpu.get("free_vram_gb"), (int, float))
            else "Telemetry unavailable"
        )


class ModelRow(Surface):
    def __init__(self, controller, model, callback, recommended=False):
        super().__init__()
        self.model_name = model.name
        self.setAccessibleName(model.name)
        layout = row(self, 16)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.addWidget(
            Icon("box", 22, COLORS["accent"] if recommended else COLORS["muted"])
        )
        info = column(None, 0, 6)
        info.addWidget(label(model.name, "h3", True))
        size = (
            gb(model.size_bytes / 1024**3) if model.size_bytes else "Size unavailable"
        )
        quant = (
            model.details.get("quantization_level")
            or model.details.get("format")
            or "Precision unknown"
        )
        info.addWidget(
            label(f"{model.provider.upper()}   ·   {quant}   ·   {size}", "quiet", True)
        )
        fit = controller.model_fit_summary(controller.assess_model(model)).replace(
            "LIKELY TO RUN · ", "Estimated fit · "
        )
        self.fit_label = label(fit, "muted", True)
        info.addWidget(self.fit_label)
        layout.addLayout(info, 1)
        self.action = Button("Configure", "arrow-right", "ghost", callback)
        self.action.setEnabled(not controller.busy)
        self.action.setAccessibleName(f"Configure benchmark for {model.name}")
        layout.addWidget(self.action)

    def refresh_fit(self, controller):
        model = controller.models.get(self.model_name)
        if model:
            fit = controller.model_fit_summary(controller.assess_model(model))
            self.fit_label.setText(fit.replace("LIKELY TO RUN · ", "Estimated fit · "))
        self.action.setEnabled(not controller.busy)


class Workspace(Page):
    def __init__(self, window):
        super().__init__(
            window,
            "Your local intelligence.",
            "A clear view of your machine, your models, and what to measure next.",
        )
        self.start = Button(
            "New benchmark", "plus", "primary", lambda: window.navigate("benchmarks")
        )
        self.actions(self.start)
        self.hardware = HardwareStrip(self.controller)
        self.body.addWidget(self.hardware)
        feature = Surface(glass=True, featured=True)
        content = row(feature, 20)
        content.setContentsMargins(28, 26, 28, 26)
        details = column(None, 0, 13)
        badge_row = row()
        badge_row.addWidget(Badge("YOUR NEXT EXPERIMENT"))
        badge_row.addStretch()
        details.addLayout(badge_row)
        self.featured_name = label("Find your starting point.", "hero", True)
        self.featured_details = label(
            "Discover an installed model, then measure its performance on this machine.",
            "muted",
            True,
        )
        details.addWidget(self.featured_name)
        details.addWidget(self.featured_details)
        self.featured_note = label(
            "Hardware fit is an estimate. A benchmark provides the evidence.",
            "quiet",
            True,
        )
        details.addWidget(self.featured_note)
        actions = row()
        self.featured_action = Button(
            "Explore models", "arrow-right", "primary", self.use_recommendation
        )
        actions.addWidget(self.featured_action)
        actions.addStretch()
        details.addLayout(actions)
        content.addLayout(details, 3)
        content.addWidget(ChipArt(), 1)
        self.body.addWidget(feature)
        lower = row(gap=24)
        collection = column(None, 0, 12)
        header = row()
        self.model_count = label("Local collection", "h2")
        header.addWidget(self.model_count, 1)
        header.addWidget(
            Button(
                "View all", "arrow-up-right", "ghost", lambda: window.navigate("models")
            )
        )
        collection.addLayout(header)
        self.model_rows = column(None, 0, 8)
        collection.addLayout(self.model_rows)
        collection.addStretch()
        lower.addLayout(collection, 3)
        activity = Surface()
        recent = column(activity, 22, 14)
        recent.addWidget(label("Recent experiments", "h2"))
        self.recent_rows = column(None, 0, 14)
        recent.addLayout(self.recent_rows)
        recent.addStretch()
        recent.addWidget(
            Button(
                "Open history", "history", "ghost", lambda: window.navigate("history")
            )
        )
        lower.addWidget(activity, 2)
        self.body.addLayout(lower)
        self.body.addStretch()
        self.refresh()

    def use_recommendation(self):
        if self.controller.recommended_model_name:
            self.window.prepare_model(self.controller.recommended_model_name)
        else:
            self.window.navigate("models")

    def refresh(self, key="all"):
        self.hardware.refresh()
        c = self.controller
        self.featured_action.setEnabled(not c.busy)
        self.start.setEnabled(not c.busy)
        if key in {"all", "models", "hardware"}:
            model = c.models.get(c.recommended_model_name)
            if model:
                self.featured_name.setText(model.name)
                self.featured_details.setText(
                    f"{c.model_fit_summary(c.assess_model(model))}\n{model.provider.upper()} · {gb(model.size_bytes / 1024**3) if model.size_bytes else 'Size unavailable'} · Ready to configure"
                )
                self.featured_action.setText("Benchmark this model")
            else:
                self.featured_name.setText(
                    "Find your starting point."
                    if not c.models
                    else "Find the right fit."
                )
                self.featured_details.setText(
                    "Add a model or refresh Ollama to discover your local collection."
                    if not c.models
                    else "Your available models need a runtime or more memory, or their fit cannot yet be confirmed."
                )
                self.featured_action.setText("Explore models")
        if key in {"all", "models"}:
            clear_layout(self.model_rows)
            self.model_count.setText(f"Local collection   {len(c.models):02d}")
            for model in list(c.models.values())[:3]:
                self.model_rows.addWidget(
                    ModelRow(
                        c,
                        model,
                        lambda _checked=False, name=model.name: (
                            self.window.prepare_model(name)
                        ),
                        model.name == c.recommended_model_name,
                    )
                )
            if not c.models:
                empty = Surface()
                content = column(empty, 22, 12)
                content.addWidget(Icon("box", 28))
                content.addWidget(label("Make room for your first model.", "h3"))
                content.addWidget(
                    label(
                        "Connect Ollama or add a GGUF file. Your collection stays on this device.",
                        "muted",
                        True,
                    )
                )
                content.addWidget(
                    Button(
                        "Add a model", "plus", "secondary", self.window.open_downloader
                    )
                )
                self.model_rows.addWidget(empty)
        for i in range(self.model_rows.count()):
            widget = self.model_rows.itemAt(i).widget()
            if isinstance(widget, ModelRow):
                widget.refresh_fit(c)
        if key in {"all", "run"}:
            clear_layout(self.recent_rows)
            records = sorted(
                c.records, key=lambda r: r.get("created_at", ""), reverse=True
            )[:3]
            if not records:
                self.recent_rows.addWidget(label("No experiments yet.", "h3"))
                self.recent_rows.addWidget(
                    label(
                        "Your first benchmark will appear here with measured speed and validation results.",
                        "muted",
                        True,
                    )
                )
            for record in records:
                self.recent_rows.addWidget(
                    label(record.get("benchmark", "Unknown model"), "h3", True)
                )
                self.recent_rows.addWidget(
                    label(
                        f"{local_date(record.get('created_at'))} · {record.get('status', 'unknown')}",
                        "quiet",
                        True,
                    )
                )
                self.recent_rows.addWidget(divider())


class Models(Page):
    def __init__(self, window):
        super().__init__(
            window,
            "Model library",
            "Local models, with their size, runtime and estimated fit in one place.",
        )
        self.refresh_button = Button(
            "Refresh", "refresh-cw", callback=self.controller.refresh_models
        )
        self.add_button = Button("Add model", "plus", "primary", window.open_downloader)
        self.actions(self.refresh_button, self.add_button)
        tools = row()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by model name or runtime…")
        self.search.setAccessibleName("Search model library")
        self.search.addAction(self.window.qt_icon("search"), QLineEdit.LeadingPosition)
        self.search.textChanged.connect(self.refresh_rows)
        self.filter = QComboBox()
        self.filter.setAccessibleName("Filter models by runtime")
        self.filter.addItems(["All runtimes", "Ollama", "GGUF"])
        self.filter.currentTextChanged.connect(self.refresh_rows)
        tools.addWidget(self.search, 1)
        tools.addWidget(self.filter)
        self.body.addLayout(tools)
        self.summary = label("", "quiet")
        self.body.addWidget(self.summary)
        self.rows = column(None, 0, 10)
        self.body.addLayout(self.rows)
        self.body.addStretch()
        self.refresh_rows()

    def refresh_rows(self):
        clear_layout(self.rows)
        query, runtime = (
            self.search.text().casefold().strip(),
            self.filter.currentText().lower(),
        )
        models = [
            m
            for m in self.controller.models.values()
            if (query in m.name.casefold() or query in m.provider.casefold())
            and (runtime == "all runtimes" or runtime == m.provider)
        ]
        self.summary.setText(
            f"{len(models)} models shown · Hardware fit is estimated, not a measured ranking"
        )
        for model in models:
            self.rows.addWidget(
                ModelRow(
                    self.controller,
                    model,
                    lambda _checked=False, name=model.name: self.window.prepare_model(
                        name
                    ),
                    model.name == self.controller.recommended_model_name,
                )
            )
        if not models:
            surface = Surface()
            content = column(surface, 32, 16)
            content.addWidget(Icon("box", 32))
            content.addWidget(
                label(
                    "Discovering local models…"
                    if "models" in self.controller.pending
                    else "No matching models"
                    if self.controller.models
                    else "Your library starts here.",
                    "h2",
                )
            )
            content.addWidget(
                label(
                    "Try a different search or runtime filter."
                    if self.controller.models
                    else "Refresh installed Ollama models, download a GGUF, or choose a folder containing your model files.",
                    "muted",
                    True,
                )
            )
            buttons = row()
            buttons.addWidget(
                Button("Add model", "download", "primary", self.window.open_downloader)
            )
            buttons.addWidget(
                Button(
                    "Choose GGUF folder", "folder", callback=self.window.choose_folder
                )
            )
            buttons.addStretch()
            content.addLayout(buttons)
            self.rows.addWidget(surface)

    def refresh(self, key):
        self.refresh_button.setEnabled(not self.controller.busy)
        self.add_button.setEnabled(not self.controller.busy)
        if key == "models" or "models" in self.controller.pending:
            self.refresh_rows()
        else:
            for i in range(self.rows.count()):
                widget = self.rows.itemAt(i).widget()
                if isinstance(widget, ModelRow):
                    widget.refresh_fit(self.controller)


class Benchmark(Page):
    def __init__(self, window):
        super().__init__(
            window,
            "Benchmark lab",
            "Same machine. Deliberate tasks. Reproducible evidence.",
        )
        self.run_button = Button("Run benchmark", "play", "primary", self.run)
        self.stop_button = Button("Stop", "square", callback=self.controller.stop)
        self.actions(self.stop_button, self.run_button)
        split = row(gap=20)
        self.split = split
        config = Surface()
        self.config_panel = config
        config.setMinimumWidth(280)
        config.setMaximumWidth(380)
        body = column(config, 24, 14)
        body.addWidget(label("Run configuration", "h2"))
        self.model = QComboBox()
        self.model.setMinimumContentsLength(12)
        self.model.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        field(body, "Model", self.model)
        self.model_fit = label("Discover local models to begin.", "quiet", True)
        body.addWidget(self.model_fit)
        self.model.currentTextChanged.connect(self.update_fit)
        body.addWidget(divider())
        self.suite = QComboBox()
        self.suite.addItems(list(TASK_SUITE_DESCRIPTIONS))
        field(body, "Task suite", self.suite)
        self.suite_hint = label(TASK_SUITE_DESCRIPTIONS["All tasks"], "quiet", True)
        body.addWidget(self.suite_hint)
        self.suite.currentTextChanged.connect(
            lambda text: self.suite_hint.setText(TASK_SUITE_DESCRIPTIONS[text])
        )
        self.advanced = QWidget()
        advanced_body = column(self.advanced, 0, 10)
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0, 2)
        self.temperature.setSingleStep(0.1)
        self.temperature.setDecimals(1)
        field(
            advanced_body,
            "Temperature",
            self.temperature,
            "0.0 keeps the validation run deterministic.",
        )
        self.context = QSpinBox()
        self.context.setRange(512, 131072)
        self.context.setSingleStep(512)
        self.context.setValue(4096)
        field(advanced_body, "Context tokens", self.context)
        self.advanced.hide()
        self.advanced_toggle = Button(
            "Advanced settings", "sliders-horizontal", "ghost", self.toggle_advanced
        )
        body.addWidget(self.advanced_toggle)
        body.addWidget(self.advanced)
        body.addStretch()
        body.addWidget(divider())
        body.addWidget(label("PRIVATE BY DESIGN", "eyebrow"))
        body.addWidget(
            label(
                "Inference and reports stay on your device. Account access is checked with the license service.",
                "quiet",
                True,
            )
        )
        split.addWidget(config, 2)
        run_panel = Surface()
        run_body = column(run_panel, 24, 16)
        top = row()
        top.addWidget(label("Execution", "h2"), 1)
        self.state = Badge("READY")
        top.addWidget(self.state)
        run_body.addLayout(top)
        self.run_description = label(
            "Configure a model and press Run benchmark.", "muted", True
        )
        run_body.addWidget(self.run_description)
        self.progress_bar = Progress()
        run_body.addWidget(self.progress_bar)
        self.progress_text = label("No active run", "quiet")
        run_body.addWidget(self.progress_text)
        metrics = row(gap=24)
        self.metric_labels = {}
        for key, caption in (
            ("speed", "TOKENS / SECOND"),
            ("checks", "CHECKS PASSED"),
            ("latency", "FIRST TOKEN"),
        ):
            metric = column(None, 0, 8)
            metric.addWidget(label(caption, "quiet"))
            value = label("—", "metric")
            self.metric_labels[key] = value
            metric.addWidget(value)
            metrics.addLayout(metric, 1)
        run_body.addLayout(metrics)
        run_body.addWidget(divider())
        run_body.addWidget(label("Run trace", "h3"))
        self.trace = QPlainTextEdit()
        self.trace.setReadOnly(True)
        self.trace.setAccessibleName("Benchmark task responses and errors")
        self.trace.setPlaceholderText(
            "Task responses, validation and runtime errors will appear here."
        )
        self.trace.setMinimumHeight(230)
        run_body.addWidget(self.trace, 1)
        run_body.addWidget(
            Button("Open reports folder", "folder", "ghost", window.open_results),
            0,
            Qt.AlignRight,
        )
        split.addWidget(run_panel, 4)
        self.body.addLayout(split, 1)
        self.refresh("models")
        self.controller.progress.connect(self.on_progress)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "split"):
            narrow = self.width() < 730
            self.split.setDirection(
                QBoxLayout.TopToBottom if narrow else QBoxLayout.LeftToRight
            )
            self.config_panel.setMinimumWidth(0 if narrow else 280)
            self.config_panel.setMaximumWidth(16777215 if narrow else 380)

    def toggle_advanced(self):
        self.advanced.setVisible(not self.advanced.isVisible())
        self.advanced_toggle.setText(
            "Hide advanced settings"
            if self.advanced.isVisible()
            else "Advanced settings"
        )

    def update_fit(self):
        model = self.controller.models.get(self.model.currentText())
        self.model_fit.setText(
            self.controller.assess_model(model).replace("DIRECT RUN:", "Estimated fit:")
            if model
            else "Discover local models to begin."
        )

    def run(self):
        suite = self.suite.currentText()
        self.controller.run(
            self.model.currentText(),
            None if suite == "All tasks" else suite,
            self.temperature.value(),
            self.context.value(),
        )

    def refresh(self, key):
        c = self.controller
        if key == "models":
            selected = self.model.currentText()
            self.model.blockSignals(True)
            self.model.clear()
            self.model.addItems(list(c.models))
            self.model.setCurrentText(
                selected
                if selected in c.models
                else c.recommended_model_name or next(iter(c.models), "")
            )
            self.model.blockSignals(False)
        self.update_fit()
        self.run_button.setEnabled(not c.busy and bool(c.models))
        self.stop_button.setVisible(c.run_status == "running")
        self.stop_button.setEnabled(
            c.busy and c.run_status == "running" and not c.stop_event.is_set()
        )
        for widget in (self.model, self.suite, self.temperature, self.context):
            widget.setEnabled(not c.busy)
        if key == "run":
            self.state.setText(c.run_status.upper())
            self.trace.setPlainText("\n".join(c.trace))
            self.run_description.setText(c.status)
            if c.run_status == "running":
                self.progress_bar.set_value(0)
                self.progress_text.setText("Preparing tasks…")
                for value in self.metric_labels.values():
                    value.setText("—")
            else:
                summary = c.run_summary
                rate = summary.get("average_tokens_per_second")
                self.metric_labels["speed"].setText(
                    f"{rate:.2f}" if isinstance(rate, (int, float)) else "—"
                )
                self.metric_labels["checks"].setText(
                    f"{summary.get('passed_checks', 0)} / {summary.get('task_count', 0)}"
                )
                self.progress_text.setText(
                    f"{c.run_status.capitalize()} · {summary.get('task_count', 0)} tasks saved"
                )

    def on_progress(self, index, total, result):
        self.progress_bar.set_value(index / total * 100)
        self.progress_text.setText(f"Task {index} of {total} · {result.task}")
        speed = result.metrics.get("tokens_per_second")
        latency = result.metrics.get("time_to_first_token_seconds")
        self.metric_labels["speed"].setText(
            f"{speed:.2f}" if isinstance(speed, (int, float)) else "—"
        )
        self.metric_labels["latency"].setText(
            f"{latency:.2f} s" if isinstance(latency, (int, float)) else "—"
        )
        self.trace.setPlainText("\n".join(self.controller.trace))
        self.trace.verticalScrollBar().setValue(
            self.trace.verticalScrollBar().maximum()
        )


class Records(Page):
    def __init__(self, window, history=False):
        super().__init__(
            window,
            "Experiment history" if history else "Results & insights",
            "Every saved run, with its configuration and evidence."
            if history
            else "Measured performance. Compare the latest run per model, then inspect the full record.",
        )
        self.history = history
        self.actions(Button("Reports folder", "folder", callback=window.open_results))
        if not history:
            panel = Surface()
            chart_body = column(panel, 24, 8)
            header = row()
            header.addWidget(label("Generation speed", "h2"), 1)
            header.addWidget(Badge("TOKENS / SECOND"))
            chart_body.addLayout(header)
            chart_body.addWidget(
                label(
                    "Latest measured run per model. Task suites may differ; speed does not establish quality.",
                    "quiet",
                    True,
                )
            )
            self.chart = SpeedChart()
            chart_body.addWidget(self.chart)
            self.body.addWidget(panel)
        tools = row()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search saved experiments…")
        self.search.setAccessibleName("Search experiment records")
        self.search.textChanged.connect(self.refresh)
        tools.addWidget(self.search, 1)
        self.order = QComboBox()
        self.order.setAccessibleName("Sort experiment records")
        self.order.addItems(
            ["Newest first", "Fastest first", "Most checks passed", "Model A–Z"]
        )
        self.order.currentTextChanged.connect(self.refresh)
        tools.addWidget(self.order)
        self.body.addLayout(tools)
        self.empty = label(
            "No experiments yet. Run a benchmark to create your first record.",
            "muted",
            True,
        )
        self.body.addWidget(self.empty)
        panel = Surface()
        table_body = column(panel, (8, 8, 8, 12), 8)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["MODEL", "STATUS", "VALIDATION", "TOKENS / S", "SAVED"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for index, width in ((1, 110), (2, 120), (3, 110), (4, 155)):
            self.table.horizontalHeader().setSectionResizeMode(index, QHeaderView.Fixed)
            self.table.setColumnWidth(index, width)
        self.table.setMinimumHeight(180)
        self.table.setAccessibleName("Saved benchmark records")
        self.table.cellDoubleClicked.connect(lambda _row, _col: self.open_selected())
        table_body.addWidget(self.table, 1)
        bottom = row()
        bottom.addWidget(label("Select a row to inspect its report.", "quiet"), 1)
        self.open_button = Button(
            "Inspect record", "arrow-up-right", callback=self.open_selected
        )
        bottom.addWidget(self.open_button)
        table_body.addLayout(bottom)
        self.table.itemSelectionChanged.connect(
            lambda: self.open_button.setEnabled(bool(self.table.selectedItems()))
        )
        self.body.addWidget(panel, 1)
        self.refresh()

    def refresh(self, *_args):
        query = self.search.text().casefold().strip()
        records = [
            r
            for r in self.controller.records
            if query in str(r.get("benchmark", "")).casefold()
            or query in str(r.get("status", "")).casefold()
        ]
        mode = self.order.currentText()

        def key(record):
            result = record.get("result", {})
            if mode == "Model A–Z":
                return str(record.get("benchmark", "")).casefold()
            if mode == "Fastest first":
                value = result.get("average_tokens_per_second")
                return value if isinstance(value, (int, float)) else -1
            if mode == "Most checks passed":
                return result.get("passed_checks", 0)
            return record.get("created_at", "")

        self.shown_records = sorted(records, key=key, reverse=mode != "Model A–Z")
        self.table.setRowCount(len(records))
        for i, record in enumerate(self.shown_records):
            result = record.get("result", {})
            speed = result.get("average_tokens_per_second")
            values = [
                record.get("benchmark", "Unknown"),
                record.get("status", "Unknown").capitalize(),
                f"{result.get('passed_checks', 0)} / {result.get('task_count', 0)}",
                f"{speed:.2f}" if isinstance(speed, (int, float)) else "—",
                local_date(record.get("created_at")),
            ]
            for j, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                if j == 1:
                    item.setForeground(
                        QColor(
                            COLORS["success"]
                            if record.get("status") == "complete"
                            else COLORS["warning"]
                            if record.get("status") in {"partial", "stopped"}
                            else COLORS["error"]
                        )
                    )
                self.table.setItem(i, j, item)
        self.empty.setVisible(not records)
        self.open_button.setEnabled(bool(self.table.selectedItems()))
        if not self.history:
            self.chart.set_records(self.controller.records)

    def open_selected(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.shown_records):
            return
        self.window.inspect_record(self.shown_records[selected])


class Hardware(Page):
    def __init__(self, window):
        super().__init__(
            window,
            "System profile",
            "The machine behind every measurement. Readings update every 15 seconds.",
        )
        self.actions(
            Button(
                "Refresh readings",
                "refresh-cw",
                callback=self.controller.refresh_hardware,
            )
        )
        self.strip = HardwareStrip(self.controller)
        self.body.addWidget(self.strip)
        monitor = Surface(glass=True)
        content = column(monitor, 24, 18)
        header = row()
        header.addWidget(label("Current utilization", "h2"), 1)
        self.timestamp = label("Waiting for telemetry", "quiet")
        header.addWidget(self.timestamp)
        content.addLayout(header)
        self.monitors = {}
        for key, title in (
            ("cpu", "CPU utilization"),
            ("ram", "RAM usage"),
            ("gpu", "GPU utilization"),
        ):
            line = row()
            line.addWidget(label(title, "muted"), 1)
            value = label("Unavailable", "h3")
            line.addWidget(value)
            content.addLayout(line)
            progress = Progress()
            content.addWidget(progress)
            self.monitors[key] = (value, progress)
        self.body.addWidget(monitor)
        info = Surface()
        details = column(info, 24, 14)
        details.addWidget(label("Device details", "h2"))
        self.detail = label(
            "Detecting operating system and acceleration…", "muted", True
        )
        details.addWidget(self.detail)
        self.body.addWidget(info)
        self.body.addStretch()

    def refresh(self, *_args):
        self.strip.refresh()
        h = self.controller.session.hardware
        gpu = next((g for g in h.get("gpu", []) if g.get("name") != "UNKNOWN"), {})
        for key, value in (
            ("cpu", h.get("cpu", {}).get("usage_percent")),
            ("ram", h.get("memory", {}).get("used_percent")),
            ("gpu", gpu.get("usage_percent")),
        ):
            caption, bar = self.monitors[key]
            caption.setText(
                f"{value:.0f}%" if isinstance(value, (int, float)) else "Unavailable"
            )
            bar.set_value(value if isinstance(value, (int, float)) else 0)
        self.timestamp.setText(
            f"Updated {local_date(h.get('updated_at'))}"
            if h
            else "Waiting for telemetry"
        )
        os_info = h.get("os", {})
        acceleration = [
            name.upper()
            for name, enabled in h.get("ai_acceleration", {}).items()
            if enabled is True
        ]
        self.detail.setText(
            f"{os_info.get('name', 'Unknown')} {os_info.get('version', '')} · {os_info.get('architecture', 'Unknown architecture')}\n\nDetected acceleration: {', '.join(acceleration) or 'Unavailable'}\nGPU driver: {gpu.get('driver', 'Unavailable')}\n\nAcceleration detection does not guarantee that an installed runtime uses that backend."
        )


class Settings(Page):
    def __init__(self, window):
        super().__init__(
            window, "Settings", "A focused workspace, configured for your machine."
        )
        storage = Surface()
        body = column(storage, 24, 14)
        body.addWidget(label("Local storage", "h2"))
        self.folder = label(
            str(self.controller.session.gguf_provider.models_dir), "muted", True
        )
        body.addWidget(label("GGUF model folder", "h3"))
        body.addWidget(self.folder)
        actions = row()
        self.choose_button = Button(
            "Change folder", "folder", callback=window.choose_folder
        )
        actions.addWidget(self.choose_button)
        actions.addWidget(
            Button("Open reports", "external-link", callback=window.open_results)
        )
        actions.addStretch()
        body.addLayout(actions)
        self.body.addWidget(storage)
        appearance = Surface()
        body = column(appearance, 24, 10)
        body.addWidget(label("Appearance & interaction", "h2"))
        self.reduced = QCheckBox("Reduce motion")
        self.reduced.setChecked(window.reduced_motion)
        self.reduced.toggled.connect(
            lambda value: window.set_preference("reduce_motion", value)
        )
        self.glass = QCheckBox("Use translucent materials")
        self.glass.setChecked(self.controller.preferences.get("glass", True))
        self.glass.toggled.connect(lambda value: window.set_preference("glass", value))
        body.addWidget(self.reduced)
        body.addWidget(self.glass)
        body.addWidget(
            label(
                "Typography and icons follow Windows display scaling automatically.\nKeyboard: Ctrl+1–7 to navigate · Ctrl+K for quick actions · Ctrl+Enter to run.",
                "quiet",
                True,
            )
        )
        self.body.addWidget(appearance)
        runtimes = Surface()
        body = column(runtimes, 24, 14)
        body.addWidget(label("Model runtimes", "h2"))
        self.runtime_info = label("", "muted", True)
        body.addWidget(self.runtime_info)
        actions = row()
        actions.addWidget(
            Button(
                "Install Ollama",
                "download",
                callback=lambda: self.controller.install_runtime("Ollama"),
            )
        )
        actions.addWidget(
            Button(
                "Install GGUF runtime",
                "download",
                callback=lambda: self.controller.install_runtime("GGUF"),
            )
        )
        actions.addStretch()
        body.addLayout(actions)
        self.body.addWidget(runtimes)
        account = Surface()
        body = column(account, 24, 14)
        body.addWidget(label("Account & access", "h2"))
        self.account = label("Not signed in", "muted", True)
        body.addWidget(self.account)
        self.sign_out = Button("Sign out", "log-out", callback=self.controller.sign_out)
        body.addWidget(self.sign_out, 0, Qt.AlignLeft)
        self.body.addWidget(account)
        self.body.addWidget(
            label(
                "AETHERION STUDIO · Beyond the known.\nQt 6 · Inter · Lucide · Inference and benchmark reports remain local.",
                "quiet",
                True,
            )
        )
        self.body.addStretch()
        self.refresh()

    def refresh(self, *_args):
        self.folder.setText(str(self.controller.session.gguf_provider.models_dir))
        self.choose_button.setEnabled(
            not self.controller.busy and "download" not in self.controller.pending
        )
        self.sign_out.setEnabled(not self.controller.busy)
        self.runtime_info.setText(
            f"Ollama executable: {'Detected' if shutil.which('ollama') else 'Not detected'}\nGGUF inference: {'Available' if importlib.util.find_spec('llama_cpp') else 'Runtime not installed'}\nA running Ollama server can be discovered even when its executable is not on PATH."
        )
        session = self.controller.auth_session
        self.account.setText(
            f"{session.username} · {session.plan}\n{'Offline access' if session.offline else 'Signed in'} · Offline pass valid until {local_date(session.offline_until.isoformat())}"
            if session
            else "Not signed in"
        )


class DownloadSheet(Sheet):
    def __init__(self, window):
        super().__init__(
            window,
            "Add a local model",
            "Download a GGUF file directly into your library. Ollama models can be added with ollama pull <model>.",
        )
        self.controller = window.controller
        self.catalog = QComboBox()
        self.catalog.addItems(
            ["Choose a catalog model…"] + list(MODEL_DOWNLOAD_CATALOG)
        )
        field(self.body, "Model catalog", self.catalog)
        self.url = QLineEdit()
        self.url.setPlaceholderText("https://…/model.gguf")
        field(self.body, "Direct HTTPS model URL", self.url)
        self.catalog.currentTextChanged.connect(
            lambda name: self.url.setText(MODEL_DOWNLOAD_CATALOG.get(name, ""))
        )
        self.body.addWidget(
            label(
                f"Saved to {self.controller.session.gguf_provider.models_dir}",
                "quiet",
                True,
            )
        )
        self.status = label(
            "Check the estimated fit before downloading.", "muted", True
        )
        self.body.addWidget(self.status)
        self.progress = Progress()
        self.body.addWidget(self.progress)
        actions = row()
        self.check = Button("Check hardware fit", "cpu", callback=self.preflight)
        self.download = Button(
            "Download",
            "download",
            "primary",
            lambda: self.controller.download(self.url.text().strip()),
        )
        self.cancel = Button(
            "Cancel download", "x", callback=lambda: self.controller.download_stop.set()
        )
        self.cancel.hide()
        actions.addWidget(self.check)
        actions.addWidget(self.download)
        self.body.addLayout(actions)
        self.body.addWidget(self.cancel)
        self.controller.download_event.connect(self.on_event)
        self.finished.connect(self.disconnect_events)
        if "download" in self.controller.pending:
            self.on_event("started", "Current model")

    def preflight(self):
        self.check.setEnabled(False)
        self.status.setText("Reading file size and checking your hardware…")
        self.controller.preflight(self.url.text().strip())

    def on_event(self, kind, payload):
        if kind == "started":
            self.status.setText(
                f"Downloading {payload}… You may close this dialog; transfer continues."
            )
            self.download.setEnabled(False)
            self.check.setEnabled(False)
            self.url.setEnabled(False)
            self.catalog.setEnabled(False)
            self.cancel.show()
        elif kind == "preflight":
            self.status.setText(
                payload[0] + "\nThese are estimates; runtime support also matters."
            )
            self.check.setEnabled(True)
        elif kind == "download_progress":
            downloaded, total, _name = payload
            self.progress.set_value(downloaded / total * 100 if total else 0)
            self.status.setText(
                f"{downloaded / 1024**2:.1f} MB downloaded"
                + (f" of {total / 1024**2:.1f} MB" if total else " · Size unavailable")
            )
        elif kind in {"download", "error"}:
            self.status.setText(
                f"Saved: {payload}" if kind == "download" else str(payload)
            )
            self.download.setEnabled("download" not in self.controller.pending)
            self.check.setEnabled(True)
            self.url.setEnabled(True)
            self.catalog.setEnabled(True)
            self.cancel.hide()
            if kind == "download":
                self.progress.set_value(100)

    def disconnect_events(self):
        self.controller.download_event.disconnect(self.on_event)


class AuthPage(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window, self.controller = window, window.controller
        self.mode = "login"
        outer = column(self, 44, 24)
        brand = row()
        brand.addWidget(BrandMark(44))
        branding = column(None, 0, 4)
        branding.addWidget(label("AETHERION", "h2"))
        branding.addWidget(label("BEYOND THE KNOWN.", "quiet"))
        brand.addLayout(branding)
        brand.addStretch()
        outer.addLayout(brand)
        outer.addStretch()
        center = row(gap=64)
        story = column(None, 0, 18)
        story.addStretch()
        story.addWidget(label("LOCAL INTELLIGENCE, MEASURED.", "eyebrow"))
        title = label("Your machine.\nYour models.\nYour evidence.", "hero")
        title.setStyleSheet("font-size: 46px; font-weight: 600;")
        story.addWidget(title)
        story.addWidget(
            label(
                "A focused studio for finding what your hardware can really do.",
                "muted",
                True,
            )
        )
        story.addWidget(ChipArt(), 0, Qt.AlignLeft)
        story.addStretch()
        center.addLayout(story, 1)
        card = Surface(glass=True)
        card.setMinimumWidth(350)
        card.setMaximumWidth(460)
        content = column(card, 30, 14)
        content.addWidget(label("YOUR PRIVATE WORKSPACE", "eyebrow"))
        self.title = label("Welcome back.", "h1")
        content.addWidget(self.title)
        content.addWidget(
            label(
                "Sign in to your studio. Models and reports stay on this device.",
                "muted",
                True,
            )
        )
        tabs = row()
        self.mode_buttons = [
            Button("Sign in", callback=lambda: self.set_mode("login")),
            Button("Create account", callback=lambda: self.set_mode("register")),
        ]
        for mode_button in self.mode_buttons:
            tabs.addWidget(mode_button)
        content.addLayout(tabs)
        self.form = column(None, 0, 10)
        content.addLayout(self.form)
        self.entries = {}
        for key, caption in (
            ("username", "Username"),
            ("password", "Password"),
            ("new_password", "New password"),
            ("confirm", "Confirm password"),
            ("license_key", "License key"),
        ):
            entry = QLineEdit()
            if key in {"password", "new_password", "confirm"}:
                entry.setEchoMode(QLineEdit.Password)
            entry.returnPressed.connect(self.submit)
            entry.setAccessibleName(caption)
            caption_widget = label(caption, "h3")
            caption_widget.setBuddy(entry)
            self.form.addWidget(caption_widget)
            self.form.addWidget(entry)
            self.entries[key] = (caption_widget, entry)
        self.feedback = label("Checking saved account access…", "quiet", True)
        content.addWidget(self.feedback)
        self.submit_button = Button("Sign in", "arrow-right", "primary", self.submit)
        content.addWidget(self.submit_button)
        self.offline_button = Button(
            "Use saved offline access", "shield-check", "ghost", self.restore
        )
        content.addWidget(self.offline_button)
        self.password_change_sign_in = Button(
            "Back to sign in", "arrow-left", "ghost", self.use_new_password_for_sign_in
        )
        content.addWidget(self.password_change_sign_in)
        content.addWidget(
            Button(
                "Connection settings", "settings-2", "ghost", self.connection_settings
            )
        )
        center.addWidget(card, 1, Qt.AlignVCenter)
        outer.addLayout(center)
        outer.addStretch()
        outer.addWidget(
            label(
                "Private inference. Ollama & GGUF.\nSaved access allows up to seven days offline on this device and Windows account.",
                "quiet",
                True,
            )
        )
        self.set_mode("login")
        self.controller.auth_feedback.connect(self.on_feedback)

    def set_mode(self, mode):
        self.mode = mode
        registering = mode == "register"
        changing_password = mode == "password_change"
        visible_entries = {"username", "password"}
        if registering:
            visible_entries.update({"confirm", "license_key"})
        elif changing_password:
            visible_entries.update({"new_password", "confirm"})
        for key, widgets in self.entries.items():
            for widget in widgets:
                widget.setVisible(key in visible_entries)
        self.entries["password"][0].setText(
            "Temporary password" if changing_password else "Password"
        )
        self.entries["confirm"][0].setText(
            "Confirm new password" if changing_password else "Confirm password"
        )
        for mode_button in self.mode_buttons:
            mode_button.setVisible(not changing_password)
        self.offline_button.setEnabled(not changing_password)
        self.password_change_sign_in.setVisible(changing_password)
        self.title.setText(
            "Create your account."
            if registering
            else "Set a new password."
            if changing_password
            else "Welcome back."
        )
        self.submit_button.setText(
            "Update password"
            if changing_password
            else "Create account"
            if registering
            else "Sign in"
        )

    def use_new_password_for_sign_in(self):
        self.entries["password"][1].setText(self.entries["new_password"][1].text())
        self.set_mode("login")
        self.feedback.setText("Sign in with the new password.")
        self.feedback.setStyleSheet(f"color: {COLORS['muted']};")

    def require_password_change(self):
        self.set_mode("password_change")
        self.feedback.setText(
            "Your administrator issued a temporary password. Change it to continue."
        )
        self.feedback.setStyleSheet(f"color: {COLORS['muted']};")

    def submit(self):
        values = {key: widgets[1].text() for key, widgets in self.entries.items()}
        self.controller.authenticate(self.mode, values, get_service_url())
        self.submit_button.setEnabled("auth" not in self.controller.pending)

    def restore(self):
        self.controller.restore()
        self.submit_button.setEnabled(False)
        self.offline_button.setEnabled(False)
        self.feedback.setText("Checking saved access…")

    def on_feedback(self, message, error):
        self.feedback.setText(message)
        self.feedback.setStyleSheet(
            f"color: {COLORS['error'] if error else COLORS['muted']};"
        )
        self.submit_button.setEnabled("auth" not in self.controller.pending)
        self.offline_button.setEnabled("auth" not in self.controller.pending)
        if error:
            self.feedback.setAccessibleDescription(f"Authentication error: {message}")
            self.entries["username"][1].setFocus()

    def connection_settings(self):
        sheet = Sheet(
            self.window,
            "Account connection",
            "The account service manages access. Your benchmark reports remain local.",
        )
        service = QLineEdit(get_service_url())
        field(sheet.body, "License service URL", service)
        device = machine_fingerprint()
        sheet.body.addWidget(label(f"Device ID\n{device}", "quiet", True))
        sheet.body.addWidget(
            Button(
                "Copy device ID",
                "copy",
                callback=lambda: QApplication.clipboard().setText(device),
            )
        )
        feedback = label("", "quiet", True)
        sheet.body.addWidget(feedback)

        def save():
            from ..auth import AuthError, save_service_url

            try:
                save_service_url(service.text())
                sheet.accept()
            except AuthError as exc:
                feedback.setText(str(exc))

        sheet.body.addWidget(Button("Save connection", kind="primary", callback=save))
        sheet.exec()
