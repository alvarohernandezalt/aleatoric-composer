"""Timeline view: multitrack arrangement display with mixer strips."""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QWheelEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QScrollArea,
    QSplitter,
    QCheckBox,
)

from src.core.composition.timeline import Composition, Track, AudioEvent
from src.gui.styles.theme import TRACK_COLORS, BG_WINDOW, BG_PANEL, BORDER, TEXT_SECONDARY


# ---------------------------------------------------------------------------
# MixerStrip: per-track controls
# ---------------------------------------------------------------------------

class MixerStrip(QWidget):
    """Vertical mixer strip for one track: name, mute, solo, volume, pan."""

    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track
        self.setFixedWidth(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(3)

        # Track name
        self._name = QLabel(track.name)
        self._name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(self._name)

        # Mute / Solo
        btn_row = QHBoxLayout()
        self._mute = QPushButton("M")
        self._mute.setCheckable(True)
        self._mute.setFixedSize(30, 22)
        self._mute.setStyleSheet("font-size: 10px;")
        self._mute.toggled.connect(self._on_mute)
        btn_row.addWidget(self._mute)

        self._solo = QPushButton("S")
        self._solo.setCheckable(True)
        self._solo.setFixedSize(30, 22)
        self._solo.setStyleSheet("font-size: 10px;")
        self._solo.toggled.connect(self._on_solo)
        btn_row.addWidget(self._solo)
        layout.addLayout(btn_row)

        # Volume
        layout.addWidget(QLabel("Vol"))
        self._volume = QSlider(Qt.Orientation.Vertical)
        self._volume.setRange(0, 100)
        self._volume.setValue(int(track.volume * 100))
        self._volume.setFixedHeight(60)
        self._volume.valueChanged.connect(lambda v: setattr(track, 'volume', v / 100.0))
        layout.addWidget(self._volume, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Pan
        layout.addWidget(QLabel("Pan"))
        self._pan = QSlider(Qt.Orientation.Horizontal)
        self._pan.setRange(-100, 100)
        self._pan.setValue(int(track.pan * 100))
        self._pan.valueChanged.connect(lambda v: setattr(track, 'pan', v / 100.0))
        layout.addWidget(self._pan)

        layout.addStretch()

    def _on_mute(self, checked):
        self.track.muted = checked
        self._mute.setStyleSheet(
            "background-color: #ff6b6b; font-size: 10px;" if checked else "font-size: 10px;"
        )

    def _on_solo(self, checked):
        self.track.solo = checked
        self._solo.setStyleSheet(
            "background-color: #ffd93d; color: black; font-size: 10px;" if checked else "font-size: 10px;"
        )


# ---------------------------------------------------------------------------
# TimelineCanvas: draws the events
# ---------------------------------------------------------------------------

class TimelineCanvas(QWidget):
    """Custom painted canvas showing audio events across tracks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._composition: Composition | None = None
        self._source_colors: dict[str, QColor] = {}
        self._zoom = 8.0  # pixels per second
        self._track_height = 55
        self._scroll_x = 0.0

        self.setMinimumHeight(100)
        self.setMouseTracking(True)
        self._hovered_event: AudioEvent | None = None

    def set_composition(self, comp: Composition, source_colors: dict[str, QColor]):
        self._composition = comp
        self._source_colors = source_colors
        # Auto-zoom to fit
        if comp.duration > 0:
            self._zoom = max(2.0, (self.width() - 20) / comp.duration)
        min_h = max(200, len(comp.tracks) * self._track_height + 40)
        self.setMinimumHeight(min_h)
        self.update()

    def clear(self):
        self._composition = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BG_WINDOW))

        if self._composition is None or not self._composition.tracks:
            painter.setPen(QColor(TEXT_SECONDARY))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No composition yet — click Compose")
            painter.end()
            return

        w = self.width()
        comp = self._composition

        # Time ruler
        painter.setPen(QColor(TEXT_SECONDARY))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        ruler_h = 20
        step = max(1, int(10 / max(0.1, self._zoom)))  # adapt step to zoom
        for t in range(0, int(comp.duration) + step + 1, step):
            x = t * self._zoom - self._scroll_x
            if 0 <= x <= w:
                painter.drawLine(int(x), ruler_h - 4, int(x), ruler_h)
                painter.drawText(int(x) - 15, ruler_h - 5, f"{t}s")

        # Track lanes
        for i, track in enumerate(comp.tracks):
            y_top = ruler_h + i * self._track_height
            y_bottom = y_top + self._track_height

            # Lane background
            bg = QColor(BG_PANEL) if i % 2 == 0 else QColor("#2a2a3e")
            painter.fillRect(QRectF(0, y_top, w, self._track_height), bg)

            # Lane separator
            painter.setPen(QPen(QColor(BORDER), 1))
            painter.drawLine(0, int(y_bottom), w, int(y_bottom))

            # Events
            for ev in track.events:
                self._draw_event(painter, ev, y_top)

        painter.end()

    def _draw_event(self, painter: QPainter, ev: AudioEvent, y_top: float):
        x = ev.timeline_start * self._zoom - self._scroll_x
        width = ev.duration * self._zoom
        height = self._track_height - 6
        y = y_top + 3

        if x + width < 0 or x > self.width():
            return  # off-screen

        color = self._source_colors.get(ev.source_name, QColor("#888888"))

        # Event rectangle
        fill = QColor(color)
        fill.setAlpha(160)
        painter.fillRect(QRectF(x, y, width, height), fill)

        # Border
        border = QColor(color)
        border.setAlpha(220)
        painter.setPen(QPen(border, 1))
        painter.drawRect(QRectF(x, y, width, height))

        # Label (source name if wide enough)
        if width > 40:
            painter.setPen(QColor("#ffffff"))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            label = ev.source_name
            if ev.is_reversed:
                label = f"↺ {label}"
            if ev.effects_config:
                label += f" [{len(ev.effects_config)}fx]"
            painter.drawText(
                QRectF(x + 3, y + 2, width - 6, height - 4),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                label,
            )

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 0.87
            self._zoom = max(1.0, min(200.0, self._zoom * factor))
        else:
            # Scroll
            delta = event.angleDelta().y()
            self._scroll_x -= delta * 0.5
            self._scroll_x = max(0, self._scroll_x)
        self.update()


# ---------------------------------------------------------------------------
# TimelineView: combines mixer strips + canvas
# ---------------------------------------------------------------------------

class TimelineView(QWidget):
    """Full timeline view with mixer strip column + canvas + stats bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._composition: Composition | None = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Mixer + Canvas row
        content = QHBoxLayout()
        content.setSpacing(0)

        # Mixer column
        self._mixer_area = QScrollArea()
        self._mixer_area.setFixedWidth(85)
        self._mixer_area.setWidgetResizable(True)
        self._mixer_widget = QWidget()
        self._mixer_layout = QVBoxLayout(self._mixer_widget)
        self._mixer_layout.setContentsMargins(0, 20, 0, 0)  # offset for ruler
        self._mixer_layout.setSpacing(0)
        self._mixer_layout.addStretch()
        self._mixer_area.setWidget(self._mixer_widget)
        content.addWidget(self._mixer_area)

        # Canvas
        self._canvas = TimelineCanvas()
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidget(self._canvas)
        canvas_scroll.setWidgetResizable(True)
        content.addWidget(canvas_scroll, stretch=1)

        main_layout.addLayout(content, stretch=1)

        # Stats bar
        self._stats = QLabel("No composition")
        self._stats.setObjectName("secondary")
        self._stats.setStyleSheet("padding: 4px 8px; background-color: #252536; border-top: 1px solid #3a3a55;")
        main_layout.addWidget(self._stats)

    def set_composition(self, comp: Composition, source_colors: dict[str, QColor]):
        self._composition = comp

        # Clear old mixer strips
        while self._mixer_layout.count() > 1:
            item = self._mixer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new mixer strips
        for track in comp.tracks:
            strip = MixerStrip(track)
            self._mixer_layout.insertWidget(self._mixer_layout.count() - 1, strip)

        # Update canvas
        self._canvas.set_composition(comp, source_colors)

        # Stats
        self._stats.setText(
            f"  {comp.num_events} events  |  {comp.duration:.1f}s  |  "
            f"{len(comp.tracks)} tracks  |  Seed: {comp.seed}"
        )

    def clear(self):
        self._canvas.clear()
        self._stats.setText("No composition")
