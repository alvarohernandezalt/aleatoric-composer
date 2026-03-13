"""Export rendered audio to various file formats."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from src.core.audio_buffer import AudioBuffer
from src.core import audio_io


def export(
    audio: np.ndarray | AudioBuffer,
    filepath: str | Path,
    sample_rate: int = 44100,
    bit_depth: int = 24,
    mp3_bitrate: str = "320k",
) -> None:
    """Export audio to file. Format is inferred from file extension."""
    filepath = Path(filepath)

    if isinstance(audio, np.ndarray):
        buf = AudioBuffer(samples=audio, sample_rate=sample_rate, name="export")
    else:
        buf = audio

    ext = filepath.suffix.lower()
    if ext == ".wav":
        audio_io.save_wav(filepath, buf, bit_depth=bit_depth)
    elif ext == ".flac":
        audio_io.save_flac(filepath, buf)
    elif ext == ".mp3":
        audio_io.save_mp3(filepath, buf, bitrate=mp3_bitrate)
    else:
        raise ValueError(f"Unsupported export format: {ext}")
