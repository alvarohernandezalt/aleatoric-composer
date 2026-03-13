"""Multitrack mixdown engine."""

from __future__ import annotations

from typing import Callable

import numpy as np

from src.core.audio_buffer import AudioBuffer
from src.core.composition.timeline import AudioEvent, Composition
from src.core.effects.chain import EffectChain
from src.core.effects.pedalboard_effects import EFFECTS_REGISTRY


def _build_effect_chain(effects_config: list[dict]) -> EffectChain:
    """Instantiate effects from serialized configs."""
    chain = EffectChain()
    for cfg in effects_config:
        factory = EFFECTS_REGISTRY.get(cfg["type"])
        if factory is None:
            continue
        params = cfg.get("parameters", {})
        chain.add(factory(**params))
    return chain


def _apply_fade(samples: np.ndarray, fade_in_samples: int, fade_out_samples: int) -> np.ndarray:
    """Apply linear fade-in and fade-out to samples (in-place)."""
    n = len(samples)
    if fade_in_samples > 0:
        fade_in_samples = min(fade_in_samples, n)
        ramp = np.linspace(0.0, 1.0, fade_in_samples, dtype=np.float32)
        if samples.ndim == 2:
            ramp = ramp[:, np.newaxis]
        samples[:fade_in_samples] *= ramp
    if fade_out_samples > 0:
        fade_out_samples = min(fade_out_samples, n)
        ramp = np.linspace(1.0, 0.0, fade_out_samples, dtype=np.float32)
        if samples.ndim == 2:
            ramp = ramp[:, np.newaxis]
        samples[-fade_out_samples:] *= ramp
    return samples


def _pan_stereo(samples: np.ndarray, pan: float) -> np.ndarray:
    """Apply constant-power panning to mono or stereo signal.

    *pan*: -1.0 = full left, 0.0 = center, 1.0 = full right.
    Returns stereo (n, 2) array.
    """
    # Convert to stereo if needed
    if samples.ndim == 1:
        samples = np.column_stack([samples, samples])

    angle = (pan + 1.0) * 0.25 * np.pi  # 0..pi/2
    left_gain = np.float32(np.cos(angle))
    right_gain = np.float32(np.sin(angle))

    out = np.empty_like(samples)
    out[:, 0] = samples[:, 0] * left_gain
    out[:, 1] = samples[:, 1] * right_gain
    return out


class Mixer:
    """Mixes a Composition into a stereo output buffer."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def mix(
        self,
        composition: Composition,
        sources: dict[str, AudioBuffer],
        progress_callback: Callable[[float], None] | None = None,
    ) -> np.ndarray:
        """Render all tracks to a stereo numpy array."""
        total_samples = int(composition.duration * self.sample_rate) + self.sample_rate
        output = np.zeros((total_samples, 2), dtype=np.float32)

        # Determine which tracks to render (solo logic)
        has_solo = any(t.solo for t in composition.tracks)
        total_events = composition.num_events
        processed = 0

        for track in composition.tracks:
            if track.muted:
                continue
            if has_solo and not track.solo:
                continue

            for event in track.events:
                self._render_event(event, track, sources, output)

                processed += 1
                if progress_callback and total_events > 0:
                    progress_callback(processed / total_events)

        # Master limiter: soft clip
        peak = np.max(np.abs(output))
        if peak > 1.0:
            output = np.tanh(output * (1.0 / peak))

        return output

    def _render_event(
        self,
        event: AudioEvent,
        track,
        sources: dict[str, AudioBuffer],
        output: np.ndarray,
    ) -> None:
        src = sources.get(event.source_name)
        if src is None:
            return

        # Extract segment
        buf = src.slice(event.source_start, event.source_end)

        # Reverse if needed
        if event.is_reversed:
            buf = buf.reversed()

        # Apply effects
        if event.effects_config:
            chain = _build_effect_chain(event.effects_config)
            buf = chain.process(buf)

        samples = buf.samples.copy()

        # Apply fades
        fade_in_s = int(event.fade_in * self.sample_rate)
        fade_out_s = int(event.fade_out * self.sample_rate)
        samples = _apply_fade(samples, fade_in_s, fade_out_s)

        # Apply amplitude
        samples *= np.float32(event.amplitude * track.volume)

        # Apply panning
        combined_pan = np.clip(event.pan + track.pan, -1.0, 1.0)
        stereo = _pan_stereo(samples, combined_pan)

        # Add to output at the correct position
        start_idx = int(event.timeline_start * self.sample_rate)
        end_idx = start_idx + len(stereo)

        # Ensure we don't write past the output buffer
        if end_idx > len(output):
            end_idx = len(output)
            stereo = stereo[: end_idx - start_idx]
        if start_idx < 0:
            stereo = stereo[-start_idx:]
            start_idx = 0

        output[start_idx:end_idx] += stereo
