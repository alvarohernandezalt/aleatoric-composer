"""Wrappers around Spotify's pedalboard library adapted to the Effect interface."""

from __future__ import annotations

from typing import Any

import numpy as np
import pedalboard as pb

from src.core.audio_buffer import AudioBuffer
from src.core.effects.base import Effect


# ---------------------------------------------------------------------------
# Generic wrapper
# ---------------------------------------------------------------------------

class PedalboardEffect(Effect):
    """Adapts any pedalboard.Plugin to the unified Effect interface."""

    def __init__(self, plugin: pb.Plugin, param_names: list[str]):
        self._plugin = plugin
        self._param_names = param_names

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        board = pb.Pedalboard([self._plugin])
        samples = buffer.samples
        # pedalboard expects (channels, samples)
        if samples.ndim == 1:
            samples = samples[np.newaxis, :]
        else:
            samples = samples.T
        processed = board(samples, buffer.sample_rate)
        # back to (samples,) or (samples, channels)
        if processed.shape[0] == 1:
            processed = processed[0]
        else:
            processed = processed.T
        return buffer.with_samples(processed)

    def get_parameters(self) -> dict[str, Any]:
        return {name: getattr(self._plugin, name) for name in self._param_names}

    def set_parameters(self, **kwargs: Any) -> None:
        for key, val in kwargs.items():
            if key in self._param_names:
                setattr(self._plugin, key, val)


# ---------------------------------------------------------------------------
# Factory functions — one per effect
# ---------------------------------------------------------------------------

def reverb(
    room_size: float = 0.5,
    damping: float = 0.5,
    wet_level: float = 0.33,
    dry_level: float = 0.4,
    width: float = 1.0,
) -> PedalboardEffect:
    plugin = pb.Reverb(
        room_size=room_size,
        damping=damping,
        wet_level=wet_level,
        dry_level=dry_level,
        width=width,
    )
    return PedalboardEffect(plugin, ["room_size", "damping", "wet_level", "dry_level", "width"])


def delay(
    delay_seconds: float = 0.5,
    feedback: float = 0.3,
    mix: float = 0.5,
) -> PedalboardEffect:
    plugin = pb.Delay(delay_seconds=delay_seconds, feedback=feedback, mix=mix)
    return PedalboardEffect(plugin, ["delay_seconds", "feedback", "mix"])


def pitch_shift(semitones: float = 0.0) -> PedalboardEffect:
    plugin = pb.PitchShift(semitones=semitones)
    return PedalboardEffect(plugin, ["semitones"])


def distortion(drive_db: float = 25.0) -> PedalboardEffect:
    plugin = pb.Distortion(drive_db=drive_db)
    return PedalboardEffect(plugin, ["drive_db"])


def compressor(
    threshold_db: float = -20.0,
    ratio: float = 4.0,
    attack_ms: float = 1.0,
    release_ms: float = 100.0,
) -> PedalboardEffect:
    plugin = pb.Compressor(
        threshold_db=threshold_db,
        ratio=ratio,
        attack_ms=attack_ms,
        release_ms=release_ms,
    )
    return PedalboardEffect(plugin, ["threshold_db", "ratio", "attack_ms", "release_ms"])


def gain(gain_db: float = 0.0) -> PedalboardEffect:
    plugin = pb.Gain(gain_db=gain_db)
    return PedalboardEffect(plugin, ["gain_db"])


def limiter(threshold_db: float = -1.0, release_ms: float = 100.0) -> PedalboardEffect:
    plugin = pb.Limiter(threshold_db=threshold_db, release_ms=release_ms)
    return PedalboardEffect(plugin, ["threshold_db", "release_ms"])


def chorus(
    rate_hz: float = 1.0,
    depth: float = 0.25,
    centre_delay_ms: float = 7.0,
    feedback: float = 0.0,
    mix: float = 0.5,
) -> PedalboardEffect:
    plugin = pb.Chorus(
        rate_hz=rate_hz,
        depth=depth,
        centre_delay_ms=centre_delay_ms,
        feedback=feedback,
        mix=mix,
    )
    return PedalboardEffect(plugin, ["rate_hz", "depth", "centre_delay_ms", "feedback", "mix"])


def phaser(
    rate_hz: float = 1.0,
    depth: float = 0.5,
    centre_frequency_hz: float = 1300.0,
    feedback: float = 0.0,
    mix: float = 0.5,
) -> PedalboardEffect:
    plugin = pb.Phaser(
        rate_hz=rate_hz,
        depth=depth,
        centre_frequency_hz=centre_frequency_hz,
        feedback=feedback,
        mix=mix,
    )
    return PedalboardEffect(
        plugin, ["rate_hz", "depth", "centre_frequency_hz", "feedback", "mix"]
    )


def highpass_filter(cutoff_frequency_hz: float = 200.0) -> PedalboardEffect:
    plugin = pb.HighpassFilter(cutoff_frequency_hz=cutoff_frequency_hz)
    return PedalboardEffect(plugin, ["cutoff_frequency_hz"])


def lowpass_filter(cutoff_frequency_hz: float = 5000.0) -> PedalboardEffect:
    plugin = pb.LowpassFilter(cutoff_frequency_hz=cutoff_frequency_hz)
    return PedalboardEffect(plugin, ["cutoff_frequency_hz"])


def bitcrush(bit_depth: float = 8.0) -> PedalboardEffect:
    plugin = pb.Bitcrush(bit_depth=bit_depth)
    return PedalboardEffect(plugin, ["bit_depth"])


def convolution(impulse_response_path: str, mix: float = 1.0) -> PedalboardEffect:
    plugin = pb.Convolution(impulse_response_filename=impulse_response_path, mix=mix)
    return PedalboardEffect(plugin, ["mix"])


# ---------------------------------------------------------------------------
# Registry: name -> factory function (used by composition engine)
# ---------------------------------------------------------------------------

EFFECTS_REGISTRY: dict[str, callable] = {
    "reverb": reverb,
    "delay": delay,
    "pitch_shift": pitch_shift,
    "distortion": distortion,
    "compressor": compressor,
    "gain": gain,
    "limiter": limiter,
    "chorus": chorus,
    "phaser": phaser,
    "highpass_filter": highpass_filter,
    "lowpass_filter": lowpass_filter,
    "bitcrush": bitcrush,
}


def _register_advanced_effects() -> None:
    """Lazily register granular, spectral, and time_stretch effects."""
    from src.core.effects.granular import granular_synth
    from src.core.effects.spectral import (
        spectral_freeze,
        spectral_gate,
        spectral_shift,
        spectral_smear,
    )
    from src.core.effects.time_stretch import time_stretch

    EFFECTS_REGISTRY.update(
        {
            "granular": granular_synth,
            "spectral_freeze": spectral_freeze,
            "spectral_smear": spectral_smear,
            "spectral_gate": spectral_gate,
            "spectral_shift": spectral_shift,
            "time_stretch": time_stretch,
        }
    )


_register_advanced_effects()
