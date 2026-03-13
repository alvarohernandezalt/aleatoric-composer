from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class AudioBuffer:
    """Immutable audio data container passed between processing stages.

    samples: float32 numpy array.
        mono  -> shape (num_samples,)
        stereo -> shape (num_samples, 2)
    """

    samples: np.ndarray
    sample_rate: int
    name: str = ""

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def channels(self) -> int:
        return 1 if self.samples.ndim == 1 else self.samples.shape[1]

    @property
    def num_samples(self) -> int:
        return self.samples.shape[0]

    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return self.num_samples / self.sample_rate

    # ------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------

    def to_mono(self) -> AudioBuffer:
        if self.channels == 1:
            return self
        mono = np.mean(self.samples, axis=1).astype(np.float32)
        return AudioBuffer(samples=mono, sample_rate=self.sample_rate, name=self.name)

    def to_stereo(self) -> AudioBuffer:
        if self.channels == 2:
            return self
        stereo = np.column_stack([self.samples, self.samples]).astype(np.float32)
        return AudioBuffer(samples=stereo, sample_rate=self.sample_rate, name=self.name)

    def slice(self, start_sec: float, end_sec: float) -> AudioBuffer:
        """Return a sub-segment between *start_sec* and *end_sec*."""
        s = int(start_sec * self.sample_rate)
        e = int(end_sec * self.sample_rate)
        s = max(0, s)
        e = min(self.num_samples, e)
        return AudioBuffer(
            samples=self.samples[s:e].copy(),
            sample_rate=self.sample_rate,
            name=self.name,
        )

    def with_samples(self, new_samples: np.ndarray) -> AudioBuffer:
        """Return a new buffer with different sample data but same metadata."""
        return AudioBuffer(
            samples=new_samples.astype(np.float32),
            sample_rate=self.sample_rate,
            name=self.name,
        )

    def reversed(self) -> AudioBuffer:
        """Return a time-reversed copy."""
        return self.with_samples(self.samples[::-1].copy())
