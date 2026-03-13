"""Spectral processing effects operating in the frequency domain via STFT."""

from __future__ import annotations

from typing import Any

import librosa
import numpy as np
from scipy.ndimage import gaussian_filter

from src.core.audio_buffer import AudioBuffer
from src.core.effects.base import Effect


# ---------------------------------------------------------------------------
# SpectralFreeze
# ---------------------------------------------------------------------------

class SpectralFreeze(Effect):
    """Freezes the spectrum at a single time point, creating a sustained drone.

    Captures the magnitude of one STFT frame and repeats it for the
    requested duration, using smoothly advancing phase to avoid clicks.
    """

    def __init__(
        self,
        freeze_position: float = 0.5,
        output_duration: float = 10.0,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        self.freeze_position = freeze_position
        self.output_duration = output_duration
        self.n_fft = n_fft
        self.hop_length = hop_length

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        samples = buffer.to_mono().samples
        sr = buffer.sample_rate

        S = librosa.stft(samples, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(S)
        phase = np.angle(S)

        # Pick the frame closest to freeze_position
        n_frames = magnitude.shape[1]
        frame_idx = int(self.freeze_position * (n_frames - 1))
        frame_idx = np.clip(frame_idx, 0, n_frames - 1)

        frozen_mag = magnitude[:, frame_idx]
        frozen_phase = phase[:, frame_idx]

        # Number of output frames
        out_frames = int(self.output_duration * sr / self.hop_length)

        # Build output spectrogram: frozen magnitude with advancing phase
        out_mag = np.tile(frozen_mag[:, np.newaxis], (1, out_frames))

        # Phase advances linearly per frame (based on frequency bin centers)
        freq_bins = np.arange(self.n_fft // 2 + 1)
        phase_advance = 2.0 * np.pi * freq_bins * self.hop_length / self.n_fft
        out_phase = np.zeros_like(out_mag)
        out_phase[:, 0] = frozen_phase
        for f in range(1, out_frames):
            out_phase[:, f] = out_phase[:, f - 1] + phase_advance

        S_out = out_mag * np.exp(1j * out_phase)
        result = librosa.istft(S_out, hop_length=self.hop_length).astype(np.float32)

        # Normalize
        peak = np.max(np.abs(result))
        if peak > 0:
            result = result / peak * 0.9

        return buffer.with_samples(result)

    def get_parameters(self) -> dict[str, Any]:
        return {
            "freeze_position": self.freeze_position,
            "output_duration": self.output_duration,
        }

    def set_parameters(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


# ---------------------------------------------------------------------------
# SpectralSmear
# ---------------------------------------------------------------------------

class SpectralSmear(Effect):
    """Blurs spectral content by applying Gaussian smoothing to the magnitude.

    Creates a washed-out, dreamy quality as distinct frequencies bleed
    into their neighbours.
    """

    def __init__(
        self,
        smear_amount: float = 5.0,
        time_smear: float = 0.0,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        self.smear_amount = smear_amount
        self.time_smear = time_smear
        self.n_fft = n_fft
        self.hop_length = hop_length

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        samples = buffer.to_mono().samples
        sr = buffer.sample_rate

        S = librosa.stft(samples, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(S)
        phase = np.angle(S)

        # Gaussian blur on magnitude spectrogram
        sigma = (self.smear_amount, self.time_smear) if self.time_smear > 0 else (self.smear_amount, 0)
        blurred_mag = gaussian_filter(magnitude, sigma=sigma)

        S_out = blurred_mag * np.exp(1j * phase)
        result = librosa.istft(S_out, hop_length=self.hop_length, length=len(samples)).astype(
            np.float32
        )

        return buffer.with_samples(result)

    def get_parameters(self) -> dict[str, Any]:
        return {"smear_amount": self.smear_amount, "time_smear": self.time_smear}

    def set_parameters(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


# ---------------------------------------------------------------------------
# SpectralGate
# ---------------------------------------------------------------------------

class SpectralGate(Effect):
    """Zeroes spectral bins below a threshold — keeps only the strongest frequencies.

    Low threshold = subtle noise reduction.
    High threshold = only the loudest partials survive, ghostly effect.
    """

    def __init__(
        self,
        threshold: float = 0.1,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        self.threshold = threshold
        self.n_fft = n_fft
        self.hop_length = hop_length

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        samples = buffer.to_mono().samples
        sr = buffer.sample_rate

        S = librosa.stft(samples, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(S)
        phase = np.angle(S)

        # Gate: zero out bins below threshold * max
        gate_level = self.threshold * np.max(magnitude)
        mask = magnitude >= gate_level
        gated_mag = magnitude * mask

        S_out = gated_mag * np.exp(1j * phase)
        result = librosa.istft(S_out, hop_length=self.hop_length, length=len(samples)).astype(
            np.float32
        )

        return buffer.with_samples(result)

    def get_parameters(self) -> dict[str, Any]:
        return {"threshold": self.threshold}

    def set_parameters(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


# ---------------------------------------------------------------------------
# SpectralShift
# ---------------------------------------------------------------------------

class SpectralShift(Effect):
    """Shifts all frequency bins up or down by a fixed number of bins.

    Positive shift_bins = shift frequencies up (higher pitch, inharmonic).
    Negative shift_bins = shift frequencies down (lower pitch, inharmonic).
    Unlike pitch shifting, this does NOT preserve harmonic relationships.
    """

    def __init__(
        self,
        shift_bins: int = 0,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        self.shift_bins = shift_bins
        self.n_fft = n_fft
        self.hop_length = hop_length

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        samples = buffer.to_mono().samples
        sr = buffer.sample_rate

        S = librosa.stft(samples, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(S)
        phase = np.angle(S)

        # Roll along frequency axis
        shifted_mag = np.roll(magnitude, self.shift_bins, axis=0)
        shifted_phase = np.roll(phase, self.shift_bins, axis=0)

        # Zero out bins that wrapped around
        if self.shift_bins > 0:
            shifted_mag[: self.shift_bins, :] = 0
            shifted_phase[: self.shift_bins, :] = 0
        elif self.shift_bins < 0:
            shifted_mag[self.shift_bins:, :] = 0
            shifted_phase[self.shift_bins:, :] = 0

        S_out = shifted_mag * np.exp(1j * shifted_phase)
        result = librosa.istft(S_out, hop_length=self.hop_length, length=len(samples)).astype(
            np.float32
        )

        return buffer.with_samples(result)

    def get_parameters(self) -> dict[str, Any]:
        return {"shift_bins": self.shift_bins}

    def set_parameters(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


# ---------------------------------------------------------------------------
# Factory functions for the effects registry
# ---------------------------------------------------------------------------

def spectral_freeze(freeze_position: float = 0.5, output_duration: float = 10.0, **kw) -> SpectralFreeze:
    return SpectralFreeze(freeze_position=freeze_position, output_duration=output_duration, **kw)


def spectral_smear(smear_amount: float = 5.0, time_smear: float = 0.0, **kw) -> SpectralSmear:
    return SpectralSmear(smear_amount=smear_amount, time_smear=time_smear, **kw)


def spectral_gate(threshold: float = 0.1, **kw) -> SpectralGate:
    return SpectralGate(threshold=threshold, **kw)


def spectral_shift(shift_bins: int = 0, **kw) -> SpectralShift:
    return SpectralShift(shift_bins=shift_bins, **kw)
