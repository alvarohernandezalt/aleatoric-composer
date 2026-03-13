"""Mini waveform display widget using QPainter."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Draws a waveform from a numpy array of audio samples."""

    def __init__(
        self,
        parent: QWidget | None = None,
        color: QColor | None = None,
        bg_color: QColor | None = None,
        num_points: int = 200,
    ):
        super().__init__(parent)
        self._peaks: np.ndarray | None = None
        self._color = color or QColor("#4ecdc4")
        self._bg_color = bg_color or QColor("#1e1e2e")
        self._num_points = num_points
        self.setMinimumHeight(30)
        self.setMaximumHeight(60)

    def set_audio(self, samples: np.ndarray) -> None:
        """Set audio data and compute peaks for display."""
        if samples.ndim > 1:
            samples = np.mean(samples, axis=1)

        # Downsample to num_points by computing max amplitude per chunk
        n = len(samples)
        chunk_size = max(1, n // self._num_points)
        n_chunks = n // chunk_size
        if n_chunks == 0:
            self._peaks = np.abs(samples[:1])
        else:
            trimmed = samples[: n_chunks * chunk_size].reshape(n_chunks, chunk_size)
            self._peaks = np.max(np.abs(trimmed), axis=1)

        self.update()

    def clear(self) -> None:
        self._peaks = None
        self.update()

    def set_color(self, color: QColor) -> None:
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, self._bg_color)

        if self._peaks is None or len(self._peaks) == 0:
            painter.end()
            return

        w = rect.width()
        h = rect.height()
        mid_y = h / 2.0
        n = len(self._peaks)

        # Normalize peaks
        peak_max = np.max(self._peaks)
        if peak_max < 1e-6:
            painter.end()
            return

        normalized = self._peaks / peak_max

        # Draw filled waveform (mirrored top/bottom)
        pen = QPen(self._color, 1.0)
        painter.setPen(pen)

        fill_color = QColor(self._color)
        fill_color.setAlpha(80)

        path_top = QPainterPath()
        path_bottom = QPainterPath()

        x_scale = w / max(1, n - 1)

        path_top.moveTo(0, mid_y)
        path_bottom.moveTo(0, mid_y)

        for i in range(n):
            x = i * x_scale
            amp = normalized[i] * (mid_y - 2)
            path_top.lineTo(x, mid_y - amp)
            path_bottom.lineTo(x, mid_y + amp)

        path_top.lineTo(w, mid_y)
        path_bottom.lineTo(w, mid_y)

        painter.fillPath(path_top, fill_color)
        painter.fillPath(path_bottom, fill_color)
        painter.drawPath(path_top)
        painter.drawPath(path_bottom)

        painter.end()
