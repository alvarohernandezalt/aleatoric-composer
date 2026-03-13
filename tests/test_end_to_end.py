"""End-to-end test: generate synthetic audio, compose, render to WAV."""

import sys
import os
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import soundfile as sf

from src.core.audio_buffer import AudioBuffer
from src.core.audio_io import load, save_wav
from src.core.effects.pedalboard_effects import reverb, delay, pitch_shift
from src.core.effects.chain import EffectChain
from src.core.composition.constraints import CompositionConstraints
from src.core.composition.arranger import Arranger
from src.core.render.renderer import Renderer
from src.core.render.exporter import export


def generate_test_wavs(output_dir: Path) -> list[Path]:
    """Create synthetic WAV files for testing."""
    sr = 44100
    files = []

    # 1. Sine wave (5 seconds, 440 Hz)
    t = np.linspace(0, 5, sr * 5, dtype=np.float32)
    sine = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    path1 = output_dir / "sine_440.wav"
    sf.write(str(path1), sine, sr)
    files.append(path1)

    # 2. Chord (5 seconds)
    chord = np.zeros(sr * 5, dtype=np.float32)
    for freq in [261.63, 329.63, 392.0]:  # C major
        chord += (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    path2 = output_dir / "chord_c.wav"
    sf.write(str(path2), chord, sr)
    files.append(path2)

    # 3. Noise burst (3 seconds)
    t3 = np.linspace(0, 3, sr * 3, dtype=np.float32)
    noise = (0.3 * np.random.default_rng(42).standard_normal(sr * 3)).astype(np.float32)
    # Apply envelope
    env = np.exp(-t3 * 2)
    noise *= env
    path3 = output_dir / "noise_burst.wav"
    sf.write(str(path3), noise, sr)
    files.append(path3)

    return files


def test_audio_buffer():
    """Test AudioBuffer basic operations."""
    sr = 44100
    samples = np.zeros(sr * 2, dtype=np.float32)
    buf = AudioBuffer(samples=samples, sample_rate=sr, name="test")
    assert buf.duration == 2.0
    assert buf.channels == 1
    assert buf.num_samples == sr * 2

    # slice
    sliced = buf.slice(0.5, 1.5)
    assert abs(sliced.duration - 1.0) < 0.001

    # to_stereo
    stereo = buf.to_stereo()
    assert stereo.channels == 2

    # reversed
    rev = buf.reversed()
    assert rev.num_samples == buf.num_samples

    print("  [OK] AudioBuffer tests passed")


def test_effects_chain():
    """Test that effects chain processes audio without errors."""
    sr = 44100
    t = np.linspace(0, 1, sr, dtype=np.float32)
    samples = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    buf = AudioBuffer(samples=samples, sample_rate=sr, name="test")

    chain = EffectChain()
    chain.add(reverb(room_size=0.3))
    chain.add(delay(delay_seconds=0.2, feedback=0.2, mix=0.3))

    result = chain.process(buf)
    assert result.sample_rate == sr
    assert result.num_samples > 0

    print("  [OK] Effects chain test passed")


def test_composition_and_render(test_dir: Path):
    """Full pipeline: load sources, compose, render, export."""
    # Generate test files
    wav_files = generate_test_wavs(test_dir)

    # Load sources
    sources = {}
    for f in wav_files:
        buf = load(f)
        sources[buf.name] = buf
        print(f"  Loaded: {buf.name} ({buf.duration:.1f}s, {buf.channels}ch)")

    # Define constraints
    constraints = CompositionConstraints(
        total_duration=15.0,   # short for testing
        num_tracks=3,
        master_seed=42,
        min_event_duration=0.5,
        max_event_duration=3.0,
        min_silence=0.1,
        max_silence=1.0,
        effects_probability=0.5,
        max_effects_per_event=2,
        density_curve="arc",
    )

    # Test each strategy
    for strategy_name in ["scatter", "structured", "layer", "canon"]:
        print(f"\n  Testing strategy: {strategy_name}")
        arranger = Arranger(strategy=strategy_name, constraints=constraints)
        composition = arranger.compose(sources)

        print(f"    Events: {composition.num_events}")
        print(f"    Duration: {composition.duration:.1f}s")
        print(f"    Tracks: {len(composition.tracks)}")

        # Render
        renderer = Renderer(composition, sources)
        result = renderer.render()
        print(f"    Rendered: {result.shape} samples")

        # Export
        out_path = test_dir / f"test_{strategy_name}.wav"
        export(result, out_path, sample_rate=44100)
        print(f"    Exported: {out_path}")

        # Verify file exists and has content
        assert out_path.exists()
        info = sf.info(str(out_path))
        assert info.duration > 0
        print(f"    Verified: {info.duration:.1f}s, {info.channels}ch, {info.samplerate}Hz")

    print("\n  [OK] Composition and render tests passed")


def test_reroll(test_dir: Path):
    """Test that reroll produces a different composition."""
    wav_files = generate_test_wavs(test_dir)
    sources = {load(f).name: load(f) for f in wav_files}

    constraints = CompositionConstraints(
        total_duration=10.0,
        num_tracks=2,
        master_seed=42,
    )

    arranger = Arranger(strategy="scatter", constraints=constraints)
    comp1 = arranger.compose(sources)
    comp2 = arranger.reroll()

    # They should be different (different seeds after fork)
    events1 = [(e.timeline_start, e.source_name) for t in comp1.tracks for e in t.events]
    events2 = [(e.timeline_start, e.source_name) for t in comp2.tracks for e in t.events]
    assert events1 != events2, "Reroll should produce different compositions"

    print("  [OK] Reroll test passed")


if __name__ == "__main__":
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)

    print("Running end-to-end tests...\n")

    print("1. AudioBuffer")
    test_audio_buffer()

    print("\n2. Effects Chain")
    test_effects_chain()

    print("\n3. Composition & Render")
    test_composition_and_render(test_dir)

    print("\n4. Reroll")
    test_reroll(test_dir)

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED")
    print(f"Output files in: {test_dir}")
