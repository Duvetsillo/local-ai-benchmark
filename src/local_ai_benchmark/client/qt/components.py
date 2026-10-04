"""Reusable native primitives. All drawing uses logical coordinates and vector paths."""

from __future__ import annotations

import math
from functools import lru_cache

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QDialog,
    QFrame,
    QGraphicsBlurEffect,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .tokens import ASSETS, COLORS, MOTION_MS


def motion_enabled() -> bool:
    return not bool(QApplication.instance().property("reduce_motion"))


@lru_cache(maxsize=128)
def svg_data(name: str, color: str) -> bytes:
    return (
        (ASSETS / f"{name}.svg")
        .read_text(encoding="utf-8")
        .replace('stroke="currentColor"', f'stroke="{color}"')
        .encode()
    )


def draw_icon(painter, name, rect, color=COLORS["muted"]):
    QSvgRenderer(svg_data(name, color)).render(painter, rect)


def label(text="", role="", wrap=False):
    widget = QLabel(str(text))
    widget.setProperty("role", role)
    widget.setWordWrap(wrap)
    if wrap:
        policy = widget.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Ignored)
        widget.setSizePolicy(policy)
        widget.setMinimumWidth(0)
    widget.setTextFormat(Qt.PlainText)
    widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return widget


def column(widget, margins=0, gap=12):
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(
        *((margins,) * 4 if isinstance(margins, int) else margins)
    )
    layout.setSpacing(gap)
    return layout


def row(widget=None, gap=12):
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(gap)
    return layout


class Icon(QWidget):
    def __init__(self, name, size=20, color=COLORS["muted"]):
        super().__init__()
        self.name, self.color = name, color
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        draw_icon(painter, self.name, QRectF(self.rect()), self.color)


class Spinner(QWidget):
    """A vector activity indicator; hidden/offscreen indicators do no timer work."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(18, 18)
        self.angle = 0
        self.running = False
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.advance)
        self.setAccessibleName("Operation in progress")
        self.hide()

    def set_running(self, active):
        self.running = active
        self.setVisible(active)
        if active and self.isVisible() and motion_enabled():
            self.timer.start()
        else:
            self.timer.stop()

    def advance(self):
        if not self.isVisible() or not motion_enabled():
            self.timer.stop()
            return
        self.angle = (self.angle + 10) % 360
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.running and motion_enabled():
            self.timer.start()

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(9, 9)
        p.rotate(self.angle)
        p.setPen(QPen(QColor(COLORS["accent"]), 1.8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(-6, -6, 12, 12), 0, 260 * 16)


class Button(QAbstractButton):
    def __init__(
        self, text="", icon=None, kind="secondary", callback=None, parent=None
    ):
        super().__init__(parent)
        self.setText(text)
        self.icon_name, self.kind = icon, kind
        self.hover = 0.0
        self.animation = QVariantAnimation(self)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._animate)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(text or icon or "Button")
        self.setMinimumHeight(40)
        if not text:
            self.setFixedWidth(40)
        if callback:
            self.clicked.connect(callback)
        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def sizeHint(self):
        return QSize(
            self.fontMetrics().horizontalAdvance(self.text())
            + (60 if self.icon_name else 32),
            40,
        )

    def keyPressEvent(self, event):
        if (
            event.key() in (Qt.Key_Return, Qt.Key_Enter)
            and event.modifiers() == Qt.NoModifier
        ):
            self.click()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _animate(self, value):
        self.hover = float(value)
        self.update()

    def enterEvent(self, _event):
        self._target(1.0)

    def leaveEvent(self, _event):
        self._target(0.0)

    def _target(self, value):
        self.animation.stop()
        self.animation.setDuration(MOTION_MS if motion_enabled() else 0)
        self.animation.setStartValue(self.hover)
        self.animation.setEndValue(value)
        self.animation.start()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setOpacity(1 if self.isEnabled() else 0.4)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        primary = self.kind == "primary"
        base = QColor(COLORS["accent"] if primary else "#1A2030")
        if self.kind == "ghost":
            base = QColor(255, 255, 255, round(13 * self.hover))
        else:
            base = base.lighter(round(100 + self.hover * 12))
        if self.isDown():
            base = base.darker(115)
        p.setPen(Qt.NoPen)
        p.setBrush(base)
        p.drawRoundedRect(rect, 9, 9)
        if self.hasFocus():
            p.setPen(QPen(QColor(COLORS["text"]), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 8, 8)
        color = "#0B1020" if primary else COLORS["text"]
        font = QFont(self.font())
        font.setWeight(QFont.DemiBold if primary else QFont.Medium)
        p.setFont(font)
        width = p.fontMetrics().horizontalAdvance(self.text()) + (
            26 if self.icon_name and self.text() else 0
        )
        x = (self.width() - width) / 2
        if self.icon_name:
            draw_icon(
                p,
                self.icon_name,
                QRectF(
                    x if self.text() else (self.width() - 18) / 2,
                    (self.height() - 18) / 2,
                    18,
                    18,
                ),
                color,
            )
            x += 26
        p.setPen(QColor(color))
        p.drawText(
            QRectF(x, 0, max(0, self.width() - x - 8), self.height()),
            Qt.AlignVCenter | Qt.AlignLeft,
            self.text(),
        )


class NavButton(Button):
    def __init__(self, text, icon, callback):
        super().__init__(text, icon, "ghost", callback)
        self.active = False
        self.setMinimumHeight(44)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 2, -1, -2)
        p.setPen(Qt.NoPen)
        p.setBrush(
            QColor(139, 168, 255, 23)
            if self.active
            else QColor(255, 255, 255, round(10 * self.hover))
        )
        p.drawRoundedRect(rect, 9, 9)
        color = COLORS["text"] if self.active else COLORS["muted"]
        draw_icon(
            p,
            self.icon_name,
            QRectF(14, (self.height() - 18) / 2, 18, 18),
            COLORS["accent"] if self.active else color,
        )
        p.setPen(QColor(color))
        p.drawText(
            QRectF(44, 0, self.width() - 48, self.height()),
            Qt.AlignVCenter,
            self.text(),
        )
        if self.active:
            p.setBrush(QColor(COLORS["accent"]))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(self.width() - 15, self.height() / 2), 2, 2)
        if self.hasFocus():
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(COLORS["accent"]), 1.5))
            p.drawRoundedRect(rect, 9, 9)


class Surface(QWidget):
    def __init__(self, parent=None, glass=False, featured=False):
        super().__init__(parent)
        self.glass, self.featured = glass, featured

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        glass = self.glass and QApplication.instance().property("glass") is not False
        gradient.setColorAt(
            0,
            QColor(35, 43, 62, 210 if glass else 255)
            if self.featured
            else QColor(24, 30, 43, 210 if glass else 255),
        )
        gradient.setColorAt(1, QColor(17, 21, 30, 235 if glass else 255))
        p.setBrush(gradient)
        p.setPen(QPen(QColor(255, 255, 255, 14), 1))
        p.drawRoundedRect(rect, 16, 16)
        if glass:
            path = QPainterPath()
            path.addRoundedRect(rect, 16, 16)
            p.setClipPath(path)
            reflection = QLinearGradient(0, 0, self.width(), 0)
            reflection.setColorAt(0, QColor(255, 255, 255, 0))
            reflection.setColorAt(0.4, QColor(255, 255, 255, 28))
            reflection.setColorAt(1, QColor(255, 255, 255, 0))
            p.setPen(QPen(reflection, 1))
            p.drawLine(QPointF(16, 1), QPointF(self.width() - 16, 1))


class Backdrop(QWidget):
    def paintEvent(self, _event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLORS["canvas"]))
        for x, y, radius, color in (
            (0.05, 0.1, 500, QColor(64, 79, 125, 32)),
            (0.85, 0.0, 600, QColor(63, 80, 128, 24)),
        ):
            gradient = QRadialGradient(self.width() * x, self.height() * y, radius)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(8, 10, 15, 0))
            p.fillRect(self.rect(), gradient)


class BrandMark(QWidget):
    def __init__(self, size=40):
        super().__init__()
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.width() / 64, self.height() / 64)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#B8C9E4"), 1.8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(8, 8, 48, 48), 40 * 16, 310 * 16)
        p.save()
        p.translate(32, 32)
        p.rotate(-42)
        p.setPen(QPen(QColor(COLORS["accent"]), 1.4))
        p.drawEllipse(QRectF(-26, -10.5, 52, 21))
        p.restore()
        path = QPainterPath(QPointF(32, 15))
        path.cubicTo(35, 26, 38, 29, 49, 32)
        path.cubicTo(38, 35, 35, 38, 32, 49)
        path.cubicTo(29, 38, 26, 35, 15, 32)
        path.cubicTo(26, 29, 29, 26, 32, 15)
        p.setBrush(QColor(COLORS["surface"]))
        p.setPen(QPen(QColor(COLORS["text"]), 1.8))
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(COLORS["text"]))
        p.drawEllipse(QPointF(32, 32), 3.3, 3.3)
        p.setBrush(QColor(COLORS["accent"]))
        p.drawEllipse(QPointF(52.7, 19.8), 2.4, 2.4)


class ChipArt(QWidget):
    """A static, antialiased silicon diagram, never a simulated performance graph."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(190, 160)
        self.setMaximumWidth(300)
        self.setAccessibleName("Hardware and model illustration")

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(self.width() / 2, self.height() / 2)
        scale = min(self.width() / 300, self.height() / 230)
        p.scale(scale, scale)
        for y, width, height, fill, edge in (
            (36, 124, 56, "#151D2C", "#384662"),
            (23, 124, 56, "#1E2A41", "#60769D"),
            (-36, 124, 56, "#162032", "#435674"),
        ):
            path = QPainterPath(QPointF(0, y - height))
            path.lineTo(width, y)
            path.lineTo(0, y + height)
            path.lineTo(-width, y)
            path.closeSubpath()
            gradient = QLinearGradient(-width, y - height, width, y + height)
            gradient.setColorAt(0, QColor(fill))
            gradient.setColorAt(1, QColor("#111723"))
            p.setBrush(gradient)
            p.setPen(QPen(QColor(edge), 0.8))
            p.drawPath(path)
        for i in range(5):
            offset = (i - 2) * 19
            p.setPen(QPen(QColor("#40577B"), 0.6))
            p.drawLine(
                QPointF(-53 + offset, -36 + offset * 0.45 + 24),
                QPointF(53 + offset, -36 + offset * 0.45 - 24),
            )
        p.setPen(QPen(QColor(COLORS["accent"]), 1.2))
        p.setBrush(QColor("#233354"))
        path = QPainterPath(QPointF(0, -63))
        for point in ((58, -36), (0, -9), (-58, -36)):
            path.lineTo(*point)
        path.closeSubpath()
        p.drawPath(path)
        p.setPen(QPen(QColor("#C9D6FF"), 1))
        p.drawLine(QPointF(-14, -36), QPointF(14, -36))
        p.drawLine(QPointF(0, -43), QPointF(0, -29))
        p.setPen(QPen(QColor("#394963"), 0.8, Qt.DashLine))
        for x in (-124, 124):
            p.drawLine(QPointF(x, -36), QPointF(x, 23))


class Badge(QLabel):
    def __init__(self, text, tone="accent"):
        super().__init__(text)
        color = COLORS.get(tone, COLORS["muted"])
        self.setStyleSheet(
            f"QLabel {{ color: {color}; background: rgba(139,168,255,10); padding: 5px 9px; border-radius: 6px; font-size: 11px; font-weight: 500; }}"
        )
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy()
        )


class Progress(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0.0
        self.setFixedHeight(6)
        self.animation = QVariantAnimation(self)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._value)
        self.setAccessibleName("Benchmark progress")

    def _value(self, value):
        self.value = float(value)
        self.update()

    def set_value(self, value):
        self.setAccessibleDescription(f"{value:.0f} percent")
        self.animation.stop()
        self.animation.setDuration(250 if motion_enabled() else 0)
        self.animation.setStartValue(self.value)
        self.animation.setEndValue(float(value))
        self.animation.start()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#252D40"))
        p.drawRoundedRect(QRectF(self.rect()), 3, 3)
        p.setBrush(QColor(COLORS["accent"]))
        p.drawRoundedRect(
            QRectF(0, 0, self.width() * self.value / 100, self.height()), 3, 3
        )


def divider():
    frame = QFrame()
    frame.setFixedHeight(1)
    frame.setStyleSheet("background: rgba(255,255,255,10);")
    return frame


def scroll_page(content):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setWidget(content)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    return area


def fade_in(widget, finished=None):
    old = getattr(widget, "_fade", None)
    current = widget.graphicsEffect()
    start = current.opacity() if isinstance(current, QGraphicsOpacityEffect) else 0.45
    if old:
        old.stop()
        old.deleteLater()
    widget._fade = None
    if not motion_enabled():
        widget.setGraphicsEffect(None)
        if finished:
            finished()
        return
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QVariantAnimation(widget)
    animation.setDuration(MOTION_MS)
    animation.setStartValue(start)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.valueChanged.connect(effect.setOpacity)

    def complete():
        widget.setGraphicsEffect(None)
        widget._fade = None
        if finished:
            finished()
        animation.deleteLater()

    animation.finished.connect(complete)
    widget._fade = animation
    animation.start()


class Sheet(QDialog):
    """A focus-trapped modal with selective background blur and a readable glass panel."""

    def __init__(self, parent, title, description=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setGeometry(parent.geometry())
        background = QLabel(self)
        background.setPixmap(parent.grab())
        background.setGeometry(self.rect())
        if QApplication.instance().property("glass") is not False:
            blur = QGraphicsBlurEffect(background)
            blur.setBlurRadius(14)
            background.setGraphicsEffect(blur)
        scrim = QWidget(self)
        scrim.setGeometry(self.rect())
        scrim.setStyleSheet("background: rgba(3,5,10,145);")
        outer = column(self, 32, 0)
        outer.addStretch()
        center = row()
        center.addStretch()
        self.surface = Surface(glass=True)
        self.surface.setMaximumWidth(610)
        self.surface.setMinimumWidth(min(560, parent.width() - 64))
        self.body = column(self.surface, 28, 14)
        heading = row()
        heading.addWidget(label(title, "h2"), 1)
        close = Button(icon="x", kind="ghost", callback=self.reject)
        close.setToolTip("Close · Esc")
        close.setAccessibleName("Close dialog")
        heading.addWidget(close)
        self.body.addLayout(heading)
        if description:
            self.body.addWidget(label(description, "muted", True))
        center.addWidget(self.surface)
        center.addStretch()
        outer.addLayout(center)
        outer.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        fade_in(self.surface, self.restore_shadow)

    def restore_shadow(self):
        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.surface.setGraphicsEffect(shadow)


class SpeedChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.setMinimumHeight(205)
        self.setAccessibleName(
            "Measured generation speed; numeric values also available in results table"
        )

    def set_records(self, records):
        measured = {}
        for record in sorted(
            records, key=lambda r: r.get("created_at", ""), reverse=True
        ):
            rate = record.get("result", {}).get("average_tokens_per_second")
            if isinstance(rate, (int, float)) and math.isfinite(rate) and rate >= 0:
                measured.setdefault(record.get("benchmark", "Unknown"), rate)
        self.data = sorted(measured.items(), key=lambda pair: pair[1], reverse=True)[:4]
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.data:
            p.setPen(QColor(COLORS["muted"]))
            p.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Your first run will build this comparison.",
            )
            return
        highest = max(1, self.data[0][1])
        label_width = min(240, self.width() * 0.3)
        bar_width = max(40, self.width() - label_width - 85)
        for index, (name, rate) in enumerate(self.data):
            y = 26 + index * 44
            p.setPen(QColor(COLORS["muted"]))
            title = p.fontMetrics().elidedText(
                name, Qt.ElideRight, int(label_width - 12)
            )
            p.drawText(QRectF(0, y - 12, label_width - 12, 24), Qt.AlignVCenter, title)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#242D41"))
            p.drawRoundedRect(QRectF(label_width, y - 5, bar_width, 10), 5, 5)
            p.setBrush(QColor(COLORS["accent"] if index == 0 else "#52658F"))
            p.drawRoundedRect(
                QRectF(label_width, y - 5, max(1, bar_width * rate / highest), 10), 5, 5
            )
            p.setPen(QColor(COLORS["text"]))
            p.drawText(
                QRectF(self.width() - 70, y - 12, 70, 24),
                Qt.AlignVCenter | Qt.AlignRight,
                f"{rate:.2f}",
            )
