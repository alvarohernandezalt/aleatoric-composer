"""Tests for advanced effects: granular, spectral, time_stretch."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import soundfile as sf

from src.core.audio_buffer import AudioBuffer
from src.core.effects.granular import GranularSynth
from src.core.effects.spectral import SpectralFreeze, SpectralSmear, SpectralGate, SpectralShift
from src.core.effects.time_stretch import TimeStretch
from src.core.effects.chain import EffectChain
from src.core.effects.pedalboard_effects import EFFECTS_REGISTRY, reverb


def _make_test_buffer(duration: float = 2.0, freq: float = 440.0, sr: int = 44100) -> AudioBuffer:
    """Create a sine wave test buffer."""
    t = np.linspace(0, duration, int(sr * duration), dtype=np.float32)
    samples = (0.5 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    return AudioBuffer(samples=samples, sample_rate=sr, name="test_sine")


def _make_chord_buffer(duration: float = 3.0, sr: int = 44100) -> AudioBuffer:
    """Create a chord for richer spectral content."""
    t = np.linspace(0, duration, int(sr * duration), dtype=np.float32)
    chord = np.zeros_like(t)
    for freq in [261.63, 329.63, 392.0, 523.25]:  # C major + octave
        chord += 0.2 * np.sin(2 * np.pi * freq * t)
    return AudioBuffer(samples=chord.astype(np.float32), sample_rate=sr, name="test_chord")


# ---------------------------------------------------------------------------
# Granular Synthesis Tests
# ---------------------------------------------------------------------------

def test_granular_basic():
    """Granular synth produces valid output."""
    buf = _make_test_buffer()
    gs = GranularSynth(grain_size_ms=50, grain_density=20, seed=42)
    result = gs.process(buf)

    assert result.num_samples > 0
    assert result.sample_rate == buf.sample_rate
    assert np.max(np.abs(result.samples)) <= 1.0
    print("  [OK] Granular basic")


def test_granular_output_duration():
    """Output duration parameter works."""
    buf = _make_test_buffer(duration=2.0)
    gs = GranularSynth(grain_density=15, output_duration=5.0, seed=42)
    result = gs.process(buf)

    assert abs(result.duration - 5.0) < 0.1
    print("  [OK] Granular output duration")


def test_granular_reproducible():
    """Same seed produces identical results."""
    buf = _make_test_buffer()
    gs1 = GranularSynth(seed=123, grain_density=20)
    gs2 = GranularSynth(seed=123, grain_density=20)

    r1 = gs1.process(buf)
    r2 = gs2.process(buf)

    assert np.array_equal(r1.samples, r2.samples)
    print("  [OK] Granular reproducibility")


def test_granular_different_seeds():
    """Different seeds produce different results when randomness is enabled."""
    buf = _make_test_buffer()
    r1 = GranularSynth(seed=1, grain_density=20, position_random=0.5, amplitude_random=0.3).process(buf)
    r2 = GranularSynth(seed=2, grain_density=20, position_random=0.5, amplitude_random=0.3).process(buf)

    assert not np.array_equal(r1.samples, r2.samples)
    print("  [OK] Granular different seeds")


def test_granular_parameters():
    """get_parameters and set_parameters work."""
    gs = GranularSynth(grain_size_ms=100, grain_density=5)
    params = gs.get_parameters()
    assert params["grain_size_ms"] == 100
    assert params["grain_density"] == 5

    gs.set_parameters(grain_size_ms=200)
    assert gs.grain_size_ms == 200
    print("  [OK] Granular parameters")


def test_granular_pitch_and_reverse():
    """Pitch shift and reverse options don't crash."""
    buf = _make_test_buffer()
    gs = GranularSynth(
        pitch_shift_semitones=5,
        pitch_random=3,
        reverse_probability=0.5,
        grain_density=15,
        seed=42,
    )
    result = gs.process(buf)
    assert result.num_samples > 0
    print("  [OK] Granular pitch + reverse")


# ---------------------------------------------------------------------------
# Spectral Effects Tests
# ---------------------------------------------------------------------------

def test_spectral_freeze():
    """SpectralFreeze produces a longer drone."""
    buf = _make_test_buffer(duration=1.0)
    sf_eff = SpectralFreeze(freeze_position=0.5, output_duration=5.0)
    result = sf_eff.process(buf)

    assert result.duration > buf.duration
    assert abs(result.duration - 5.0) < 0.5  # approximate
    assert np.max(np.abs(result.samples)) <= 1.0
    print("  [OK] SpectralFreeze")


def test_spectral_smear():
    """SpectralSmear processes without error and changes the signal."""
    buf = _make_chord_buffer()
    sm = SpectralSmear(smear_amount=10.0)
    result = sm.process(buf)

    assert result.num_samples == buf.num_samples
    assert not np.array_equal(result.samples, buf.samples)
    print("  [OK] SpectralSmear")


def test_spectral_gate():
    """SpectralGate reduces energy (zeroes weak bins)."""
    buf = _make_chord_buffer()
    sg = SpectralGate(threshold=0.3)
    result = sg.process(buf)

    # Energy should be less or equal (we removed bins)
    original_energy = np.sum(buf.samples ** 2)
    gated_energy = np.sum(result.samples ** 2)
    assert gated_energy <= original_energy * 1.01  # tiny float tolerance
    print("  [OK] SpectralGate")


def test_spectral_shift():
    """SpectralShift shifts frequencies up/down."""
    buf = _make_test_buffer()

    # Shift up
    up = SpectralShift(shift_bins=10)
    r_up = up.process(buf)
    assert r_up.num_samples == buf.num_samples

    # Shift down
    down = SpectralShift(shift_bins=-10)
    r_down = down.process(buf)
    assert r_down.num_samples == buf.num_samples

    # They should differ from original
    assert not np.array_equal(r_up.samples, buf.samples)
    assert not np.array_equal(r_down.samples, buf.samples)
    print("  [OK] SpectralShift")


# ---------------------------------------------------------------------------
# Time Stretch Tests
# ---------------------------------------------------------------------------

def test_time_stretch_slower():
    """Slowing down produces longer audio."""
    buf = _make_test_buffer(duration=2.0)
    ts = TimeStretch(rate=0.5)
    result = ts.process(buf)

    assert result.duration > buf.duration * 1.5  # should be ~4s
    print(f"  [OK] TimeStretch slower: {buf.duration:.1f}s -> {result.duration:.1f}s")


def test_time_stretch_faster():
    """Speeding up produces shorter audio."""
    buf = _make_test_buffer(duration=2.0)
    ts = TimeStretch(rate=2.0)
    result = ts.process(buf)

    assert result.duration < buf.duration * 0.75  # should be ~1s
    print(f"  [OK] TimeStretch faster: {buf.duration:.1f}s -> {result.duration:.1f}s")


def test_time_stretch_identity():
    """Rate 1.0 returns same length."""
    buf = _make_test_buffer(duration=1.0)
    ts = TimeStretch(rate=1.0)
    result = ts.process(buf)

    assert abs(result.duration - buf.duration) < 0.01
    print("  [OK] TimeStretch identity")


# ---------------------------------------------------------------------------
# Registry Tests
# ---------------------------------------------------------------------------

def test_registry_has_advanced_effects():
    """All advanced effects are registered in EFFECTS_REGISTRY."""
    expected = ["granular", "spectral_freeze", "spectral_smear",
                "spectral_gate", "spectral_shift", "time_stretch"]
    for name in expected:
        assert name in EFFECTS_REGISTRY, f"Missing from registry: {name}"
    print(f"  [OK] Registry has all {len(expected)} advanced effects")


def test_registry_factory_functions():
    """Factory functions from registry produce working effects."""
    buf = _make_test_buffer(duration=1.0)

    for name in ["granular", "spectral_smear", "spectral_gate", "spectral_shift", "time_stretch"]:
        factory = EFFECTS_REGISTRY[name]
        effect = factory()
        result = effect.process(buf)
        assert result.num_samples > 0, f"{name} produced empty output"

    print("  [OK] Registry factory functions all work")


# ---------------------------------------------------------------------------
# Chain Integration Test
# ---------------------------------------------------------------------------

def test_chain_with_advanced_effects():
    """Chain combining pedalboard + advanced effects."""
    buf = _make_chord_buffer(duration=2.0)

    chain = EffectChain()
    chain.add(SpectralSmear(smear_amount=3.0))
    chain.add(reverb(room_size=0.5))
    chain.add(GranularSynth(grain_density=30, grain_size_ms=30, seed=42))

    result = chain.process(buf)
    assert result.num_samples > 0
    print("  [OK] Chain with mixed effects")


# ---------------------------------------------------------------------------
# Export Test WAVs
# ---------------------------------------------------------------------------

def export_test_wavs(output_dir: Path):
    """Generate WAVs for each advanced effect to listen to."""
    output_dir.mkdir(exist_ok=True)
    buf = _make_chord_buffer(duration=3.0)
    sr = buf.sample_rate

    effects = {
        "granular_cloud": GranularSynth(
            grain_size_ms=40, grain_density=30, grain_scatter=0.3,
            position_random=0.3, pitch_random=2.0, amplitude_random=0.3,
            output_duration=5.0, seed=42,
        ),
        "granular_stutter": GranularSynth(
            grain_size_ms=100, grain_density=8, grain_scatter=0.0,
            pitch_shift_semitones=0, reverse_probability=0.3, seed=42,
        ),
        "spectral_freeze": SpectralFreeze(freeze_position=0.3, output_duration=5.0),
        "spectral_smear": SpectralSmear(smear_amount=15.0, time_smear=3.0),
        "spectral_gate": SpectralGate(threshold=0.2),
        "spectral_shift_up": SpectralShift(shift_bins=20),
        "spectral_shift_down": SpectralShift(shift_bins=-20),
        "time_stretch_slow": TimeStretch(rate=0.5),
        "time_stretch_fast": TimeStretch(rate=1.5),
    }

    for name, effect in effects.items():
        result = effect.process(buf)
        path = output_dir / f"fx_{name}.wav"
        sf.write(str(path), result.samples, sr)
        print(f"  Exported: {path.name} ({result.duration:.1f}s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing Advanced Effects...\n")

    print("1. Granular Synthesis")
    test_granular_basic()
    test_granular_output_duration()
    test_granular_reproducible()
    test_granular_different_seeds()
    test_granular_parameters()
    test_granular_pitch_and_reverse()

    print("\n2. Spectral Effects")
    test_spectral_freeze()
    test_spectral_smear()
    test_spectral_gate()
    test_spectral_shift()

    print("\n3. Time Stretch")
    test_time_stretch_slower()
    test_time_stretch_faster()
    test_time_stretch_identity()

    print("\n4. Registry")
    test_registry_has_advanced_effects()
    test_registry_factory_functions()

    print("\n5. Chain Integration")
    test_chain_with_advanced_effects()

    print("\n6. Exporting test WAVs...")
    out = Path(__file__).parent / "test_output" / "advanced_effects"
    export_test_wavs(out)

    print("\n" + "=" * 50)
    print("ALL ADVANCED EFFECTS TESTS PASSED")
    print(f"Audio samples in: {out}")
