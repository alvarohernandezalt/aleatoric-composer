"""Time stretching via phase vocoder — change duration without altering pitch."""

from __future__ import annotations

from typing import Any

import librosa
import numpy as np

from src.core.audio_buffer import AudioBuffer
from src.core.effects.base import Effect


class TimeStretch(Effect):
    """Stretch or compress audio in time without changing pitch.

    rate > 1.0 → faster / shorter
    rate < 1.0 → slower / longer
    rate = 1.0 → no change
    """

    def __init__(self, rate: float = 1.0):
        self.rate = rate

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        if abs(self.rate - 1.0) < 0.001:
            return buffer

        samples = buffer.to_mono().samples

        stretched = librosa.effects.time_stretch(samples, rate=self.rate)
        return buffer.with_samples(stretched.astype(np.float32))

    def get_parameters(self) -> dict[str, Any]:
        return {"rate": self.rate}

    def set_parameters(self, **kwargs: Any) -> None:
        if "rate" in kwargs:
            self.rate = kwargs["rate"]


# ---------------------------------------------------------------------------
# Factory function for the effects registry
# ---------------------------------------------------------------------------

def time_stretch(rate: float = 1.0, **kw) -> TimeStretch:
    return TimeStretch(rate=rate)
