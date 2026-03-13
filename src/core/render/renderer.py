"""Full render pipeline with progress reporting."""

from __future__ import annotations

from typing import Callable

import numpy as np

from src.core.audio_buffer import AudioBuffer
from src.core.composition.timeline import Composition
from src.core.render.mixer import Mixer


class Renderer:
    """Orchestrates the complete render pipeline."""

    def __init__(
        self,
        composition: Composition,
        sources: dict[str, AudioBuffer],
    ):
        self.composition = composition
        self.sources = sources
        self.progress_callback: Callable[[float], None] | None = None

    def render(self) -> np.ndarray:
        """Render the full composition to a stereo numpy array."""
        mixer = Mixer(self.composition.sample_rate)
        return mixer.mix(
            self.composition,
            self.sources,
            progress_callback=self.progress_callback,
        )

    def render_to_buffer(self) -> AudioBuffer:
        """Render and wrap in an AudioBuffer."""
        samples = self.render()
        return AudioBuffer(
            samples=samples,
            sample_rate=self.composition.sample_rate,
            name="composition_render",
        )
