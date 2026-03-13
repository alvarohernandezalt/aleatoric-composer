from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from src.core.audio_buffer import AudioBuffer
from src.utils.constants import DEFAULT_SAMPLE_RATE, SUPPORTED_FORMATS


def load(filepath: str | Path, sr: int = DEFAULT_SAMPLE_RATE, mono: bool = False) -> AudioBuffer:
    """Load an audio file and return an AudioBuffer.

    Resamples to *sr* if the file has a different sample rate.
    """
    filepath = Path(filepath)
    if filepath.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {filepath.suffix}")

    audio, file_sr = sf.read(str(filepath), dtype="float32")

    if file_sr != sr:
        # librosa.resample expects (channels, samples) for multi-channel
        if audio.ndim > 1:
            audio = librosa.resample(audio.T, orig_sr=file_sr, target_sr=sr).T
        else:
            audio = librosa.resample(audio, orig_sr=file_sr, target_sr=sr)

    if mono and audio.ndim > 1:
        audio = np.mean(audio, axis=1).astype(np.float32)

    return AudioBuffer(samples=audio, sample_rate=sr, name=filepath.stem)


def save_wav(
    filepath: str | Path,
    buffer: AudioBuffer,
    bit_depth: int = 24,
) -> None:
    """Save an AudioBuffer to a WAV file."""
    subtype = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}[bit_depth]
    sf.write(str(filepath), buffer.samples, buffer.sample_rate, subtype=subtype)


def save_flac(filepath: str | Path, buffer: AudioBuffer) -> None:
    """Save an AudioBuffer to a FLAC file."""
    sf.write(str(filepath), buffer.samples, buffer.sample_rate, format="FLAC")


def save_mp3(
    filepath: str | Path,
    buffer: AudioBuffer,
    bitrate: str = "320k",
) -> None:
    """Save an AudioBuffer to an MP3 file (requires ffmpeg)."""
    from pydub import AudioSegment

    # pydub expects int16
    samples_int16 = (buffer.samples * 32767).clip(-32768, 32767).astype(np.int16)

    if buffer.samples.ndim == 1:
        channels = 1
    else:
        channels = buffer.samples.shape[1]

    seg = AudioSegment(
        data=samples_int16.tobytes(),
        sample_width=2,
        frame_rate=buffer.sample_rate,
        channels=channels,
    )
    seg.export(str(filepath), format="mp3", bitrate=bitrate)
