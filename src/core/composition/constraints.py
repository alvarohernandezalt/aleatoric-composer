"""User-controllable parameters that bound the randomness of composition."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CompositionConstraints:
    # -- Global --
    total_duration: float = 120.0       # seconds
    num_tracks: int = 4
    master_seed: int = 42

    # -- Timing --
    min_event_duration: float = 0.5     # seconds
    max_event_duration: float = 30.0
    min_silence: float = 0.0            # gap between events
    max_silence: float = 5.0
    overlap_allowed: bool = True

    # -- Source selection --
    source_weights: dict[str, float] = field(default_factory=dict)
    source_repeat_allowed: bool = True

    # -- Effects --
    effects_probability: float = 0.7
    max_effects_per_event: int = 3
    effect_weights: dict[str, float] = field(default_factory=dict)

    # -- Dynamics --
    amplitude_min: float = 0.3
    amplitude_max: float = 1.0
    fade_in_min: float = 0.01
    fade_in_max: float = 0.5
    fade_out_min: float = 0.01
    fade_out_max: float = 1.0
    pan_min: float = -1.0
    pan_max: float = 1.0

    # -- Structure --
    density_curve: str = "constant"
    # options: constant, crescendo, decrescendo, arc, wave
