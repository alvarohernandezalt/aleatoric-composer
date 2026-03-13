"""Granular synthesis engine — breaks audio into grains and reassembles them."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import resample as scipy_resample
from scipy.signal.windows import hann, hamming, blackmanharris, triang

from src.core.audio_buffer import AudioBuffer
from src.core.effects.base import Effect

_WINDOWS = {
    "hann": hann,
    "hamming": hamming,
    "blackman": blackmanharris,
    "triangular": triang,
}


class GranularSynth(Effect):
    """Granular synthesis: chops audio into tiny grains and reconstructs them.

    This creates textures ranging from shimmering clouds to stuttering
    glitch effects depending on the parameters.
    """

    def __init__(
        self,
        grain_size_ms: float = 50.0,
        grain_density: float = 10.0,
        grain_scatter: float = 0.0,
        position_start: float = 0.0,
        position_end: float = 1.0,
        position_random: float = 0.0,
        pitch_shift_semitones: float = 0.0,
        pitch_random: float = 0.0,
        amplitude_random: float = 0.0,
        window_type: str = "hann",
        reverse_probability: float = 0.0,
        output_duration: float | None = None,
        seed: int = 42,
    ):
        self.grain_size_ms = grain_size_ms
        self.grain_density = grain_density
        self.grain_scatter = grain_scatter
        self.position_start = position_start
        self.position_end = position_end
        self.position_random = position_random
        self.pitch_shift_semitones = pitch_shift_semitones
        self.pitch_random = pitch_random
        self.amplitude_random = amplitude_random
        self.window_type = window_type
        self.reverse_probability = reverse_probability
        self.output_duration = output_duration
        self.seed = seed

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        rng = np.random.default_rng(self.seed)
        sr = buffer.sample_rate
        samples = buffer.to_mono().samples

        grain_samples = int(self.grain_size_ms * sr / 1000.0)
        grain_samples = max(4, grain_samples)

        out_duration = self.output_duration if self.output_duration else buffer.duration
        out_length = int(out_duration * sr)
        output = np.zeros(out_length, dtype=np.float32)

        # Grain onset times in the output
        n_grains = max(1, int(self.grain_density * out_duration))
        base_spacing = out_duration / n_grains
        onset_times = np.arange(n_grains) * base_spacing

        # Add scatter to onset times
        if self.grain_scatter > 0:
            jitter = rng.uniform(-0.5, 0.5, n_grains) * base_spacing * self.grain_scatter
            onset_times = onset_times + jitter

        # Source read region in samples
        src_len = len(samples)
        read_start = int(self.position_start * src_len)
        read_end = int(self.position_end * src_len)
        read_range = max(1, read_end - read_start)

        # Window
        window_fn = _WINDOWS.get(self.window_type, hann)
        window = window_fn(grain_samples).astype(np.float32)

        for i in range(n_grains):
            # Read position: linear scan through source region + random offset
            progress = i / max(1, n_grains - 1)
            base_pos = read_start + int(progress * (read_range - grain_samples))

            if self.position_random > 0:
                offset = int(rng.uniform(-0.5, 0.5) * self.position_random * read_range)
                base_pos += offset

            base_pos = np.clip(base_pos, 0, src_len - grain_samples)

            # Extract grain
            grain = samples[base_pos: base_pos + grain_samples].copy()

            # Pad if grain is shorter than expected
            if len(grain) < grain_samples:
                grain = np.pad(grain, (0, grain_samples - len(grain)))

            # Apply window
            grain *= window

            # Reverse grain
            if self.reverse_probability > 0 and rng.random() < self.reverse_probability:
                grain = grain[::-1].copy()

            # Per-grain pitch shift via resampling
            total_shift = self.pitch_shift_semitones
            if self.pitch_random > 0:
                total_shift += rng.uniform(-self.pitch_random, self.pitch_random)

            if abs(total_shift) > 0.01:
                ratio = 2.0 ** (total_shift / 12.0)
                new_len = max(4, int(len(grain) / ratio))
                grain = scipy_resample(grain, new_len).astype(np.float32)

            # Amplitude variation
            if self.amplitude_random > 0:
                amp = 1.0 - rng.random() * self.amplitude_random
                grain *= np.float32(amp)

            # Place grain in output (overlap-add)
            onset_sample = int(onset_times[i] * sr)
            onset_sample = max(0, onset_sample)
            end_sample = onset_sample + len(grain)

            if end_sample > out_length:
                grain = grain[: out_length - onset_sample]
                end_sample = out_length

            if onset_sample < out_length:
                output[onset_sample:end_sample] += grain

        # Normalize to prevent clipping
        peak = np.max(np.abs(output))
        if peak > 0:
            output /= peak
            output *= 0.9  # headroom

        return buffer.with_samples(output)

    def get_parameters(self) -> dict[str, Any]:
        return {
            "grain_size_ms": self.grain_size_ms,
            "grain_density": self.grain_density,
            "grain_scatter": self.grain_scatter,
            "position_start": self.position_start,
            "position_end": self.position_end,
            "position_random": self.position_random,
            "pitch_shift_semitones": self.pitch_shift_semitones,
            "pitch_random": self.pitch_random,
            "amplitude_random": self.amplitude_random,
            "window_type": self.window_type,
            "reverse_probability": self.reverse_probability,
            "output_duration": self.output_duration,
            "seed": self.seed,
        }

    def set_parameters(self, **kwargs: Any) -> None:
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


# ---------------------------------------------------------------------------
# Factory function for the effects registry
# ---------------------------------------------------------------------------

def granular_synth(
    grain_size_ms: float = 50.0,
    grain_density: float = 10.0,
    grain_scatter: float = 0.0,
    position_random: float = 0.0,
    pitch_random: float = 0.0,
    amplitude_random: float = 0.0,
    reverse_probability: float = 0.0,
    seed: int = 42,
    **kwargs,
) -> GranularSynth:
    return GranularSynth(
        grain_size_ms=grain_size_ms,
        grain_density=grain_density,
        grain_scatter=grain_scatter,
        position_random=position_random,
        pitch_random=pitch_random,
        amplitude_random=amplitude_random,
        reverse_probability=reverse_probability,
        seed=seed,
        **kwargs,
    )
