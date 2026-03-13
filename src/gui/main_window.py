"""Main application window — integrates all panels and the core engine."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QRunnable, QThreadPool, QObject, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QFileDialog,
    QMessageBox,
)

from src.core.audio_buffer import AudioBuffer
from src.core.composition.arranger import Arranger
from src.core.composition.timeline import Composition
from src.core.render.renderer import Renderer
from src.core.render.exporter import export

from src.gui.styles.theme import DARK_QSS
from src.gui.widgets.source_panel import SourcePanel
from src.gui.widgets.composition_panel import CompositionPanel
from src.gui.widgets.effects_panel import EffectsPalettePanel
from src.gui.widgets.timeline_view import TimelineView


# ---------------------------------------------------------------------------
# Background render worker
# ---------------------------------------------------------------------------

class _RenderSignals(QObject):
    progress = Signal(float)
    finished = Signal(np.ndarray)
    error = Signal(str)


class RenderWorker(QRunnable):
    def __init__(self, renderer: Renderer):
        super().__init__()
        self.renderer = renderer
        self.signals = _RenderSignals()

    @Slot()
    def run(self):
        try:
            self.renderer.progress_callback = lambda p: self.signals.progress.emit(p)
            result = self.renderer.render()
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


# ---------------------------------------------------------------------------
# MainWindow
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aleatoric Composer para la Escuela SUR (beta)")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet(DARK_QSS)

        # State
        self._composition: Composition | None = None
        self._arranger: Arranger | None = None
        self._rendered_audio: np.ndarray | None = None
        self._thread_pool = QThreadPool()

        self._build_menu()
        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        act_open = QAction("Add audio files…", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(lambda: self._source_panel._on_add())
        file_menu.addAction(act_open)

        act_export = QAction("Export render…", self)
        act_export.setShortcut("Ctrl+E")
        act_export.triggered.connect(self._on_export)
        file_menu.addAction(act_export)

        file_menu.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        comp_menu = menu.addMenu("Composition")
        act_compose = QAction("Compose", self)
        act_compose.setShortcut("Ctrl+G")
        act_compose.triggered.connect(self._on_compose)
        comp_menu.addAction(act_compose)

        act_reroll = QAction("Re-roll", self)
        act_reroll.setShortcut("Ctrl+R")
        act_reroll.triggered.connect(self._on_reroll)
        comp_menu.addAction(act_reroll)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Vertical splitter: top panels | bottom timeline
        v_splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Top: horizontal splitter (sources | tabs) ──
        h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Source panel
        self._source_panel = SourcePanel()
        self._source_panel.setMinimumWidth(280)
        self._source_panel.setMaximumWidth(400)
        h_splitter.addWidget(self._source_panel)

        # Right: Tabs
        self._tabs = QTabWidget()
        self._comp_panel = CompositionPanel()
        self._tabs.addTab(self._comp_panel, "Composition")

        self._effects_panel = EffectsPalettePanel()
        self._tabs.addTab(self._effects_panel, "Effects Palette")

        h_splitter.addWidget(self._tabs)
        h_splitter.setSizes([300, 700])

        v_splitter.addWidget(h_splitter)

        # ── Bottom: Timeline ──
        self._timeline = TimelineView()
        v_splitter.addWidget(self._timeline)

        v_splitter.setSizes([450, 350])
        main_layout.addWidget(v_splitter, stretch=1)

        # ── Transport bar ──
        transport = QHBoxLayout()
        transport.setContentsMargins(8, 4, 8, 4)

        self._btn_render = QPushButton("Render")
        self._btn_render.setObjectName("accent")
        self._btn_render.setMinimumHeight(32)
        self._btn_render.clicked.connect(self._on_render)
        transport.addWidget(self._btn_render)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(22)
        transport.addWidget(self._progress, stretch=1)

        self._btn_export_wav = QPushButton("Export WAV")
        self._btn_export_wav.clicked.connect(lambda: self._on_export("wav"))
        transport.addWidget(self._btn_export_wav)

        self._btn_export_mp3 = QPushButton("Export MP3")
        self._btn_export_mp3.clicked.connect(lambda: self._on_export("mp3"))
        transport.addWidget(self._btn_export_mp3)

        transport_widget = QWidget()
        transport_widget.setLayout(transport)
        transport_widget.setStyleSheet(f"background-color: #252536; border-top: 1px solid #3a3a55;")
        main_layout.addWidget(transport_widget)

        copyright_label = QLabel("\u00a9 Alvaro Hernandez Altozano 2026")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #8888aa; font-size: 11px; padding: 4px;")
        main_layout.addWidget(copyright_label)

    def _connect_signals(self):
        self._comp_panel.compose_requested.connect(self._on_compose)
        self._comp_panel.reroll_requested.connect(self._on_reroll)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_compose(self):
        sources = self._source_panel.sources
        if not sources:
            QMessageBox.warning(self, "No sources", "Add at least one audio file first.")
            return

        weights = self._source_panel.get_source_weights()
        constraints = self._comp_panel.build_constraints(source_weights=weights)
        strategy = self._comp_panel.strategy_name()

        self._arranger = Arranger(strategy=strategy, constraints=constraints)
        self._composition = self._arranger.compose(sources)
        self._rendered_audio = None

        # Get source colors
        colors = {name: self._source_panel.get_source_color(name) for name in sources}
        self._timeline.set_composition(self._composition, colors)
        self._progress.setValue(0)

    def _on_reroll(self):
        if self._arranger is None:
            QMessageBox.warning(self, "No composition", "Compose first before re-rolling.")
            return

        self._composition = self._arranger.reroll()
        self._rendered_audio = None

        sources = self._source_panel.sources
        colors = {name: self._source_panel.get_source_color(name) for name in sources}
        self._timeline.set_composition(self._composition, colors)
        self._progress.setValue(0)

    def _on_render(self):
        if self._composition is None:
            QMessageBox.warning(self, "Nothing to render", "Compose first.")
            return

        sources = self._source_panel.sources
        renderer = Renderer(self._composition, sources)

        worker = RenderWorker(renderer)
        worker.signals.progress.connect(self._on_render_progress)
        worker.signals.finished.connect(self._on_render_finished)
        worker.signals.error.connect(self._on_render_error)

        self._btn_render.setEnabled(False)
        self._btn_render.setText("Rendering…")
        self._progress.setValue(0)

        self._thread_pool.start(worker)

    def _on_render_progress(self, value: float):
        self._progress.setValue(int(value * 100))

    def _on_render_finished(self, audio: np.ndarray):
        self._rendered_audio = audio
        self._btn_render.setEnabled(True)
        self._btn_render.setText("Render")
        self._progress.setValue(100)
        duration = len(audio) / 44100
        QMessageBox.information(
            self, "Render complete",
            f"Rendered {duration:.1f}s of audio.\nUse Export to save to file."
        )

    def _on_render_error(self, msg: str):
        self._btn_render.setEnabled(True)
        self._btn_render.setText("Render")
        QMessageBox.critical(self, "Render error", msg)

    def _on_export(self, fmt: str = ""):
        if self._rendered_audio is None:
            QMessageBox.warning(self, "Nothing to export", "Render first.")
            return

        if fmt == "wav":
            path, _ = QFileDialog.getSaveFileName(self, "Export WAV", "composition.wav", "WAV (*.wav)")
        elif fmt == "mp3":
            path, _ = QFileDialog.getSaveFileName(self, "Export MP3", "composition.mp3", "MP3 (*.mp3)")
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Export audio", "composition.wav",
                "WAV (*.wav);;FLAC (*.flac);;MP3 (*.mp3)"
            )

        if not path:
            return

        try:
            export(self._rendered_audio, path, sample_rate=44100)
            QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export error", str(e))
