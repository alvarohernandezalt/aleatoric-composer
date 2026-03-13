"""Effects palette panel — configure default parameters per effect type."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QScrollArea,
    QGroupBox,
)

from src.core.effects.pedalboard_effects import EFFECTS_REGISTRY
from src.gui.widgets.parameter_controls import LabeledSlider


# Parameter definitions for each effect (name, min, max, default, decimals)
EFFECT_PARAMS: dict[str, list[tuple[str, float, float, float, int]]] = {
    "reverb": [
        ("room_size", 0.0, 1.0, 0.5, 2),
        ("damping", 0.0, 1.0, 0.5, 2),
        ("wet_level", 0.0, 1.0, 0.33, 2),
        ("dry_level", 0.0, 1.0, 0.4, 2),
        ("width", 0.0, 1.0, 1.0, 2),
    ],
    "delay": [
        ("delay_seconds", 0.01, 2.0, 0.5, 2),
        ("feedback", 0.0, 1.0, 0.3, 2),
        ("mix", 0.0, 1.0, 0.5, 2),
    ],
    "pitch_shift": [
        ("semitones", -24.0, 24.0, 0.0, 1),
    ],
    "distortion": [
        ("drive_db", 0.0, 100.0, 25.0, 1),
    ],
    "compressor": [
        ("threshold_db", -60.0, 0.0, -20.0, 1),
        ("ratio", 1.0, 20.0, 4.0, 1),
        ("attack_ms", 0.1, 100.0, 1.0, 1),
        ("release_ms", 10.0, 1000.0, 100.0, 0),
    ],
    "gain": [
        ("gain_db", -60.0, 30.0, 0.0, 1),
    ],
    "limiter": [
        ("threshold_db", -60.0, 0.0, -1.0, 1),
        ("release_ms", 10.0, 1000.0, 100.0, 0),
    ],
    "chorus": [
        ("rate_hz", 0.1, 10.0, 1.0, 1),
        ("depth", 0.0, 1.0, 0.25, 2),
        ("mix", 0.0, 1.0, 0.5, 2),
    ],
    "phaser": [
        ("rate_hz", 0.1, 10.0, 1.0, 1),
        ("depth", 0.0, 1.0, 0.5, 2),
        ("mix", 0.0, 1.0, 0.5, 2),
    ],
    "highpass_filter": [
        ("cutoff_frequency_hz", 20.0, 10000.0, 200.0, 0),
    ],
    "lowpass_filter": [
        ("cutoff_frequency_hz", 20.0, 20000.0, 5000.0, 0),
    ],
    "bitcrush": [
        ("bit_depth", 1.0, 24.0, 8.0, 0),
    ],
    "granular": [
        ("grain_size_ms", 5.0, 500.0, 50.0, 0),
        ("grain_density", 1.0, 100.0, 10.0, 0),
        ("grain_scatter", 0.0, 1.0, 0.0, 2),
        ("position_random", 0.0, 1.0, 0.0, 2),
        ("pitch_random", 0.0, 12.0, 0.0, 1),
        ("amplitude_random", 0.0, 1.0, 0.0, 2),
        ("reverse_probability", 0.0, 1.0, 0.0, 2),
    ],
    "spectral_freeze": [
        ("freeze_position", 0.0, 1.0, 0.5, 2),
        ("output_duration", 1.0, 60.0, 10.0, 1),
    ],
    "spectral_smear": [
        ("smear_amount", 0.0, 50.0, 5.0, 1),
        ("time_smear", 0.0, 20.0, 0.0, 1),
    ],
    "spectral_gate": [
        ("threshold", 0.0, 1.0, 0.1, 2),
    ],
    "spectral_shift": [
        ("shift_bins", -200.0, 200.0, 0.0, 0),
    ],
    "time_stretch": [
        ("rate", 0.1, 4.0, 1.0, 2),
    ],
}


class EffectsPalettePanel(QWidget):
    """Tab 2: select an effect and view/adjust its parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header
        header = QLabel("EFFECTS PALETTE")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #7c6ff0;")
        layout.addWidget(header)

        info = QLabel("Browse available effects and their parameters")
        info.setObjectName("secondary")
        layout.addWidget(info)

        # Effect selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Effect:"))
        self._selector = QComboBox()
        self._selector.addItems(sorted(EFFECTS_REGISTRY.keys()))
        self._selector.currentTextChanged.connect(self._on_effect_changed)
        row.addWidget(self._selector, stretch=1)
        layout.addLayout(row)

        # Parameter area
        self._param_scroll = QScrollArea()
        self._param_scroll.setWidgetResizable(True)
        self._param_container = QWidget()
        self._param_layout = QVBoxLayout(self._param_container)
        self._param_layout.setSpacing(4)
        self._param_layout.addStretch()
        self._param_scroll.setWidget(self._param_container)
        layout.addWidget(self._param_scroll, stretch=1)

        self._sliders: dict[str, LabeledSlider] = {}

        # Initial display
        if self._selector.count() > 0:
            self._on_effect_changed(self._selector.currentText())

    def _on_effect_changed(self, name: str):
        # Clear old sliders
        while self._param_layout.count() > 1:
            item = self._param_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._sliders.clear()

        params = EFFECT_PARAMS.get(name, [])
        if not params:
            lbl = QLabel("No configurable parameters")
            lbl.setObjectName("secondary")
            self._param_layout.insertWidget(0, lbl)
            return

        group = QGroupBox(name.replace("_", " ").title())
        group_layout = QVBoxLayout(group)

        for pname, pmin, pmax, pdefault, pdec in params:
            slider = LabeledSlider(
                label=pname.replace("_", " ").title(),
                min_val=pmin,
                max_val=pmax,
                default=pdefault,
                decimals=pdec,
            )
            self._sliders[pname] = slider
            group_layout.addWidget(slider)

        self._param_layout.insertWidget(0, group)
