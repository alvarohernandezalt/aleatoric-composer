"""Composition configuration panel — strategy, constraints, density curve."""

from __future__ import annotations

import random

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
)

from src.core.composition.constraints import CompositionConstraints
from src.gui.widgets.parameter_controls import LabeledSlider, RangeSlider, DensityCurvePreview


class CompositionPanel(QScrollArea):
    """Tab 1: all composition configuration controls."""

    compose_requested = Signal()
    reroll_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)

        # ── General ──
        gen_group = QGroupBox("General")
        gen_layout = QVBoxLayout(gen_group)

        # Strategy
        row = QHBoxLayout()
        row.addWidget(QLabel("Strategy:"))
        self._strategy = QComboBox()
        self._strategy.addItems(["scatter", "structured", "layer", "canon"])
        row.addWidget(self._strategy, stretch=1)
        gen_layout.addLayout(row)

        # Seed
        row = QHBoxLayout()
        row.addWidget(QLabel("Seed:"))
        self._seed = QSpinBox()
        self._seed.setRange(0, 2_147_483_647)
        self._seed.setValue(42)
        row.addWidget(self._seed, stretch=1)
        btn_rand = QPushButton("Random")
        btn_rand.setFixedWidth(70)
        btn_rand.clicked.connect(lambda: self._seed.setValue(random.randint(0, 2_147_483_647)))
        row.addWidget(btn_rand)
        gen_layout.addLayout(row)

        # Duration
        row = QHBoxLayout()
        row.addWidget(QLabel("Duration (s):"))
        self._duration = QDoubleSpinBox()
        self._duration.setRange(1.0, 3600.0)
        self._duration.setValue(120.0)
        self._duration.setDecimals(1)
        row.addWidget(self._duration, stretch=1)
        gen_layout.addLayout(row)

        # Tracks
        row = QHBoxLayout()
        row.addWidget(QLabel("Tracks:"))
        self._num_tracks = QSpinBox()
        self._num_tracks.setRange(1, 16)
        self._num_tracks.setValue(4)
        row.addWidget(self._num_tracks, stretch=1)
        gen_layout.addLayout(row)

        layout.addWidget(gen_group)

        # ── Timing ──
        time_group = QGroupBox("Timing")
        time_layout = QVBoxLayout(time_group)

        self._event_dur = RangeSlider("Event duration", 0.01, 60.0, 0.5, 30.0, decimals=1)
        time_layout.addWidget(self._event_dur)

        self._silence = RangeSlider("Silence gap", 0.0, 30.0, 0.0, 5.0, decimals=1)
        time_layout.addWidget(self._silence)

        self._overlap = QCheckBox("Allow overlap")
        self._overlap.setChecked(True)
        time_layout.addWidget(self._overlap)

        layout.addWidget(time_group)

        # ── Dynamics ──
        dyn_group = QGroupBox("Dynamics")
        dyn_layout = QVBoxLayout(dyn_group)

        self._amplitude = RangeSlider("Amplitude", 0.0, 1.0, 0.3, 1.0)
        dyn_layout.addWidget(self._amplitude)

        self._pan = RangeSlider("Pan", -1.0, 1.0, -1.0, 1.0)
        dyn_layout.addWidget(self._pan)

        self._fade_in = RangeSlider("Fade in", 0.001, 2.0, 0.01, 0.5, decimals=3)
        dyn_layout.addWidget(self._fade_in)

        self._fade_out = RangeSlider("Fade out", 0.001, 2.0, 0.01, 1.0, decimals=3)
        dyn_layout.addWidget(self._fade_out)

        layout.addWidget(dyn_group)

        # ── Effects ──
        fx_group = QGroupBox("Effects")
        fx_layout = QVBoxLayout(fx_group)

        self._fx_prob = LabeledSlider("Probability", 0.0, 1.0, 0.7, suffix="")
        fx_layout.addWidget(self._fx_prob)

        row = QHBoxLayout()
        row.addWidget(QLabel("Max per event:"))
        self._max_fx = QSpinBox()
        self._max_fx.setRange(1, 10)
        self._max_fx.setValue(3)
        row.addWidget(self._max_fx, stretch=1)
        fx_layout.addLayout(row)

        layout.addWidget(fx_group)

        # ── Structure ──
        struct_group = QGroupBox("Structure")
        struct_layout = QVBoxLayout(struct_group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Density curve:"))
        self._density_curve = QComboBox()
        self._density_curve.addItems(["constant", "crescendo", "decrescendo", "arc", "wave"])
        row.addWidget(self._density_curve, stretch=1)
        struct_layout.addLayout(row)

        self._curve_preview = DensityCurvePreview()
        self._density_curve.currentTextChanged.connect(self._curve_preview.set_curve)
        struct_layout.addWidget(self._curve_preview)

        layout.addWidget(struct_group)

        # ── Action buttons ──
        btn_layout = QHBoxLayout()
        self._btn_compose = QPushButton("Compose")
        self._btn_compose.setObjectName("accent")
        self._btn_compose.setMinimumHeight(36)
        self._btn_compose.clicked.connect(self.compose_requested.emit)
        btn_layout.addWidget(self._btn_compose)

        self._btn_reroll = QPushButton("Re-roll")
        self._btn_reroll.setMinimumHeight(36)
        self._btn_reroll.clicked.connect(self.reroll_requested.emit)
        btn_layout.addWidget(self._btn_reroll)

        layout.addLayout(btn_layout)
        layout.addStretch()

        self.setWidget(container)

    # ── Build constraints from current UI state ──

    def build_constraints(self, source_weights: dict[str, float] | None = None) -> CompositionConstraints:
        return CompositionConstraints(
            total_duration=self._duration.value(),
            num_tracks=self._num_tracks.value(),
            master_seed=self._seed.value(),
            min_event_duration=self._event_dur.low(),
            max_event_duration=self._event_dur.high(),
            min_silence=self._silence.low(),
            max_silence=self._silence.high(),
            overlap_allowed=self._overlap.isChecked(),
            source_weights=source_weights or {},
            effects_probability=self._fx_prob.value(),
            max_effects_per_event=self._max_fx.value(),
            amplitude_min=self._amplitude.low(),
            amplitude_max=self._amplitude.high(),
            pan_min=self._pan.low(),
            pan_max=self._pan.high(),
            fade_in_min=self._fade_in.low(),
            fade_in_max=self._fade_in.high(),
            fade_out_min=self._fade_out.low(),
            fade_out_max=self._fade_out.high(),
            density_curve=self._density_curve.currentText(),
        )

    def strategy_name(self) -> str:
        return self._strategy.currentText()
