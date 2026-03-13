"""Reusable parameter control widgets: RangeSlider, LabeledSlider, DensityCurvePreview."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSlider,
    QDoubleSpinBox,
    QSpinBox,
)


# ---------------------------------------------------------------------------
# LabeledSlider: slider + label + value display
# ---------------------------------------------------------------------------


class LabeledSlider(QWidget):
    """A horizontal slider with a label and numeric value display."""

    valueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        min_val: float = 0.0,
        max_val: float = 1.0,
        default: float = 0.5,
        decimals: int = 2,
        suffix: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._decimals = decimals
        self._suffix = suffix
        self._steps = 1000

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(label)
        self._label.setFixedWidth(120)
        self._label.setStyleSheet("color: #bbbbcc;")
        layout.addWidget(self._label)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, self._steps)
        self._slider.setValue(self._val_to_pos(default))
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider, stretch=1)

        self._value_label = QLabel(self._format(default))
        self._value_label.setFixedWidth(70)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._value_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self._value_label)

    def _val_to_pos(self, val: float) -> int:
        ratio = (val - self._min) / max(1e-9, self._max - self._min)
        return int(ratio * self._steps)

    def _pos_to_val(self, pos: int) -> float:
        ratio = pos / self._steps
        return self._min + ratio * (self._max - self._min)

    def _format(self, val: float) -> str:
        return f"{val:.{self._decimals}f}{self._suffix}"

    def _on_slider_changed(self, pos: int):
        val = self._pos_to_val(pos)
        self._value_label.setText(self._format(val))
        self.valueChanged.emit(val)

    def value(self) -> float:
        return self._pos_to_val(self._slider.value())

    def setValue(self, val: float):
        self._slider.blockSignals(True)
        self._slider.setValue(self._val_to_pos(val))
        self._value_label.setText(self._format(val))
        self._slider.blockSignals(False)


# ---------------------------------------------------------------------------
# RangeSlider: double-handled slider for min/max ranges
# ---------------------------------------------------------------------------


class RangeSlider(QWidget):
    """A slider with two handles for defining a min/max range."""

    rangeChanged = Signal(float, float)

    def __init__(
        self,
        label: str,
        min_val: float = 0.0,
        max_val: float = 1.0,
        low: float = 0.0,
        high: float = 1.0,
        decimals: int = 2,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._low = low
        self._high = high
        self._decimals = decimals
        self._dragging: str | None = None  # "low" or "high"
        self._handle_radius = 7

        self.setMinimumHeight(36)
        self.setMaximumHeight(36)

        self._label_text = label
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def low(self) -> float:
        return self._low

    def high(self) -> float:
        return self._high

    def setRange(self, low: float, high: float):
        self._low = max(self._min, min(low, self._max))
        self._high = max(self._min, min(high, self._max))
        self.update()

    def _val_to_x(self, val: float) -> float:
        track_left = 130.0
        track_right = self.width() - 60.0
        ratio = (val - self._min) / max(1e-9, self._max - self._min)
        return track_left + ratio * (track_right - track_left)

    def _x_to_val(self, x: float) -> float:
        track_left = 130.0
        track_right = self.width() - 60.0
        ratio = (x - track_left) / max(1, track_right - track_left)
        ratio = max(0.0, min(1.0, ratio))
        return self._min + ratio * (self._max - self._min)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        h = self.height()
        mid_y = h / 2.0

        # Label
        painter.setPen(QColor("#bbbbcc"))
        painter.drawText(QRectF(0, 0, 125, h), Qt.AlignmentFlag.AlignVCenter, self._label_text)

        # Track background
        track_left = 130.0
        track_right = self.width() - 60.0
        painter.setPen(QPen(QColor("#444466"), 2))
        painter.drawLine(QPointF(track_left, mid_y), QPointF(track_right, mid_y))

        # Active range
        x_low = self._val_to_x(self._low)
        x_high = self._val_to_x(self._high)
        painter.setPen(QPen(QColor("#7c6ff0"), 3))
        painter.drawLine(QPointF(x_low, mid_y), QPointF(x_high, mid_y))

        # Handles
        for x in (x_low, x_high):
            painter.setBrush(QColor("#7c6ff0"))
            painter.setPen(QPen(QColor("#e0e0e0"), 1))
            painter.drawEllipse(QPointF(x, mid_y), self._handle_radius, self._handle_radius)

        # Value labels
        painter.setPen(QColor("#e0e0e0"))
        text = f"{self._low:.{self._decimals}f} – {self._high:.{self._decimals}f}"
        painter.drawText(
            QRectF(track_right + 5, 0, 55, h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            text,
        )

        painter.end()

    def mousePressEvent(self, event):
        x = event.position().x()
        x_low = self._val_to_x(self._low)
        x_high = self._val_to_x(self._high)

        if abs(x - x_low) < abs(x - x_high):
            self._dragging = "low"
        else:
            self._dragging = "high"

    def mouseMoveEvent(self, event):
        if self._dragging is None:
            return
        val = self._x_to_val(event.position().x())

        if self._dragging == "low":
            self._low = max(self._min, min(val, self._high))
        else:
            self._high = max(self._low, min(val, self._max))

        self.rangeChanged.emit(self._low, self._high)
        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = None


# ---------------------------------------------------------------------------
# DensityCurvePreview: draws the density curve shape
# ---------------------------------------------------------------------------


class DensityCurvePreview(QWidget):
    """Small widget that visualizes the selected density curve."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._curve = "constant"
        self.setFixedHeight(70)
        self.setMinimumWidth(180)

    def set_curve(self, curve: str):
        self._curve = curve
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e2e"))

        w = self.width()
        h = self.height()
        margin = 8
        plot_w = w - 2 * margin
        plot_h = h - 2 * margin

        # Draw grid
        painter.setPen(QPen(QColor("#333355"), 1, Qt.PenStyle.DotLine))
        painter.drawLine(margin, margin, margin, h - margin)
        painter.drawLine(margin, h - margin, w - margin, h - margin)

        # Compute curve points
        n = 100
        points: list[QPointF] = []
        for i in range(n):
            t = i / (n - 1)
            density = self._eval(t)
            x = margin + t * plot_w
            y = (h - margin) - density * plot_h * 0.45
            points.append(QPointF(x, y))

        # Draw curve
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)

        painter.setPen(QPen(QColor("#7c6ff0"), 2))
        painter.drawPath(path)

        # Label
        painter.setPen(QColor("#8888aa"))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(QRectF(margin, 2, plot_w, 14), Qt.AlignmentFlag.AlignCenter, self._curve)

        painter.end()

    def _eval(self, t: float) -> float:
        if self._curve == "crescendo":
            return 0.3 + 1.7 * t
        if self._curve == "decrescendo":
            return 2.0 - 1.7 * t
        if self._curve == "arc":
            return 0.3 + 1.7 * math.sin(t * math.pi)
        if self._curve == "wave":
            return 1.0 + 0.8 * math.sin(t * math.pi * 4)
        return 1.0  # constant
