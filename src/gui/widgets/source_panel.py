"""Source audio file manager panel with waveform thumbnails and weight sliders."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QSlider,
    QScrollArea,
)

from src.core.audio_buffer import AudioBuffer
from src.core import audio_io
from src.gui.styles.theme import TRACK_COLORS
from src.gui.widgets.waveform_view import WaveformWidget
from src.utils.constants import SUPPORTED_FORMATS


class SourceItemWidget(QWidget):
    """Custom widget displayed inside each list item."""

    def __init__(self, buf: AudioBuffer, color: QColor, parent=None):
        super().__init__(parent)
        self.buffer = buf
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Name
        name_label = QLabel(f"  {buf.name}")
        name_label.setStyleSheet(f"color: {color.name()}; font-weight: bold; font-size: 12px;")
        layout.addWidget(name_label)

        # Info
        ch = "mono" if buf.channels == 1 else "stereo"
        info = QLabel(f"  {buf.duration:.1f}s  |  {ch}  |  {buf.sample_rate}Hz")
        info.setObjectName("secondary")
        layout.addWidget(info)

        # Waveform
        self.waveform = WaveformWidget(color=color)
        self.waveform.set_audio(buf.samples)
        self.waveform.setFixedHeight(35)
        layout.addWidget(self.waveform)


class SourcePanel(QWidget):
    """Left panel: load audio files, show waveforms, adjust weights."""

    sources_changed = Signal()  # emitted when files are added/removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sources: dict[str, AudioBuffer] = {}
        self._source_colors: dict[str, QColor] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Header
        header = QLabel("SOURCES")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #7c6ff0;")
        layout.addWidget(header)

        # Buttons
        btn_row = QHBoxLayout()
        self._btn_add = QPushButton("+ Add files")
        self._btn_add.clicked.connect(self._on_add)
        btn_row.addWidget(self._btn_add)

        self._btn_remove = QPushButton("- Remove")
        self._btn_remove.clicked.connect(self._on_remove)
        btn_row.addWidget(self._btn_remove)
        layout.addLayout(btn_row)

        # File list
        self._list = QListWidget()
        self._list.setMinimumHeight(100)
        layout.addWidget(self._list, stretch=1)

        # Weights section
        weights_label = QLabel("SOURCE WEIGHTS")
        weights_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #8888aa; margin-top: 8px;")
        layout.addWidget(weights_label)

        self._weights_area = QScrollArea()
        self._weights_area.setWidgetResizable(True)
        self._weights_area.setMaximumHeight(150)
        self._weights_container = QWidget()
        self._weights_layout = QVBoxLayout(self._weights_container)
        self._weights_layout.setContentsMargins(0, 0, 0, 0)
        self._weights_layout.setSpacing(2)
        self._weights_area.setWidget(self._weights_container)
        layout.addWidget(self._weights_area)

        self._weight_sliders: dict[str, QSlider] = {}

        # Enable drag & drop
        self.setAcceptDrops(True)

    def _get_color(self, index: int) -> QColor:
        return QColor(TRACK_COLORS[index % len(TRACK_COLORS)])

    def _on_add(self):
        exts = " ".join(f"*{e}" for e in SUPPORTED_FORMATS)
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add audio files", "", f"Audio Files ({exts})"
        )
        for f in files:
            self._load_file(f)

    def _load_file(self, filepath: str):
        try:
            buf = audio_io.load(filepath)
            if buf.name in self.sources:
                return  # already loaded
            self.sources[buf.name] = buf
            color = self._get_color(len(self.sources) - 1)
            self._source_colors[buf.name] = color

            # Add to list
            item_widget = SourceItemWidget(buf, color)
            item = QListWidgetItem(self._list)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, buf.name)
            self._list.addItem(item)
            self._list.setItemWidget(item, item_widget)

            # Add weight slider
            self._add_weight_slider(buf.name, color)

            self.sources_changed.emit()
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

    def _on_remove(self):
        item = self._list.currentItem()
        if item is None:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        if name in self.sources:
            del self.sources[name]
            del self._source_colors[name]
        row = self._list.row(item)
        self._list.takeItem(row)
        self._remove_weight_slider(name)
        self.sources_changed.emit()

    def _add_weight_slider(self, name: str, color: QColor):
        row = QHBoxLayout()
        label = QLabel(name)
        label.setFixedWidth(90)
        label.setStyleSheet(f"color: {color.name()}; font-size: 11px;")
        row.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        row.addWidget(slider, stretch=1)

        val_label = QLabel("1.00")
        val_label.setFixedWidth(35)
        val_label.setStyleSheet("font-size: 11px;")
        slider.valueChanged.connect(lambda v, lbl=val_label: lbl.setText(f"{v / 100:.2f}"))
        row.addWidget(val_label)

        container = QWidget()
        container.setLayout(row)
        container.setObjectName(f"weight_{name}")
        self._weights_layout.addWidget(container)
        self._weight_sliders[name] = slider

    def _remove_weight_slider(self, name: str):
        if name in self._weight_sliders:
            del self._weight_sliders[name]
        for i in range(self._weights_layout.count()):
            w = self._weights_layout.itemAt(i).widget()
            if w and w.objectName() == f"weight_{name}":
                self._weights_layout.removeWidget(w)
                w.deleteLater()
                break

    def get_source_weights(self) -> dict[str, float]:
        return {name: s.value() / 100.0 for name, s in self._weight_sliders.items()}

    def get_source_color(self, name: str) -> QColor:
        return self._source_colors.get(name, QColor("#888888"))

    # Drag & drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).suffix.lower() in SUPPORTED_FORMATS:
                self._load_file(path)
