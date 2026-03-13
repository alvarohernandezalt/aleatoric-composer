"""Composition strategies — different algorithms for generating arrangements."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from src.core.audio_buffer import AudioBuffer
from src.core.composition.constraints import CompositionConstraints
from src.core.composition.rng import ControlledRandom
from src.core.composition.timeline import AudioEvent, Composition, Track
from src.core.effects.pedalboard_effects import EFFECTS_REGISTRY


# ---------------------------------------------------------------------------
# Density curve helper
# ---------------------------------------------------------------------------

def _density_at(curve: str, position: float) -> float:
    """Return density multiplier at a normalized position (0..1)."""
    if curve == "crescendo":
        return 0.3 + 1.7 * position
    if curve == "decrescendo":
        return 2.0 - 1.7 * position
    if curve == "arc":
        return 0.3 + 1.7 * math.sin(position * math.pi)
    if curve == "wave":
        return 1.0 + 0.8 * math.sin(position * math.pi * 4)
    return 1.0  # constant


# ---------------------------------------------------------------------------
# Helper: choose random effects config
# ---------------------------------------------------------------------------

def _random_effects_config(
    rng: ControlledRandom,
    constraints: CompositionConstraints,
) -> list[dict]:
    """Pick random effects and return their serialized configs."""
    if not rng.boolean(constraints.effects_probability):
        return []

    available = list(EFFECTS_REGISTRY.keys())
    if constraints.effect_weights:
        available = [e for e in available if e in constraints.effect_weights]
        weights = [constraints.effect_weights[e] for e in available]
    else:
        weights = [1.0] * len(available)

    if not available:
        return []

    n_effects = rng.integer(1, constraints.max_effects_per_event)
    configs: list[dict] = []
    for _ in range(n_effects):
        name = rng.weighted_choice(available, weights)
        configs.append({"type": name, "parameters": {}})
    return configs


# ---------------------------------------------------------------------------
# Base strategy
# ---------------------------------------------------------------------------

class CompositionStrategy(ABC):
    @abstractmethod
    def generate(
        self,
        sources: dict[str, AudioBuffer],
        constraints: CompositionConstraints,
        rng: ControlledRandom,
    ) -> Composition:
        ...


# ---------------------------------------------------------------------------
# ScatterStrategy
# ---------------------------------------------------------------------------

class ScatterStrategy(CompositionStrategy):
    """Randomly scatters audio fragments across the timeline.

    Each event's timing, source, duration, and effects are independently
    random. Produces the most chaotic / aleatory results.
    """

    def generate(
        self,
        sources: dict[str, AudioBuffer],
        constraints: CompositionConstraints,
        rng: ControlledRandom,
    ) -> Composition:
        source_names = list(sources.keys())
        if constraints.source_weights:
            s_weights = [constraints.source_weights.get(n, 1.0) for n in source_names]
        else:
            s_weights = [1.0] * len(source_names)

        tracks: list[Track] = []

        for ti in range(constraints.num_tracks):
            track_rng = rng.fork()
            events: list[AudioEvent] = []
            current_time = 0.0

            while current_time < constraints.total_duration:
                # choose source
                name = track_rng.weighted_choice(source_names, s_weights)
                src = sources[name]

                # event duration
                dur = track_rng.gaussian(
                    mean=(constraints.min_event_duration + constraints.max_event_duration) / 2,
                    std=(constraints.max_event_duration - constraints.min_event_duration) / 4,
                    clip_low=constraints.min_event_duration,
                    clip_high=min(constraints.max_event_duration, src.duration),
                )

                # segment start within source
                max_start = max(0.0, src.duration - dur)
                seg_start = track_rng.uniform(0.0, max_start)
                seg_end = seg_start + dur

                # density-adjusted gap
                pos = current_time / constraints.total_duration
                density = _density_at(constraints.density_curve, pos)
                gap = track_rng.uniform(constraints.min_silence, constraints.max_silence)
                gap /= max(density, 0.1)

                event = AudioEvent(
                    source_name=name,
                    source_start=seg_start,
                    source_end=seg_end,
                    timeline_start=current_time,
                    track_index=ti,
                    amplitude=track_rng.uniform(constraints.amplitude_min, constraints.amplitude_max),
                    pan=track_rng.uniform(constraints.pan_min, constraints.pan_max),
                    fade_in=track_rng.uniform(constraints.fade_in_min, constraints.fade_in_max),
                    fade_out=track_rng.uniform(constraints.fade_out_min, constraints.fade_out_max),
                    effects_config=_random_effects_config(track_rng, constraints),
                    is_reversed=track_rng.boolean(0.15),
                )
                events.append(event)
                current_time += dur + gap

            tracks.append(Track(index=ti, name=f"Track {ti + 1}", events=events))

        return Composition(tracks=tracks, sample_rate=44100, seed=rng.seed)


# ---------------------------------------------------------------------------
# StructuredStrategy
# ---------------------------------------------------------------------------

class StructuredStrategy(CompositionStrategy):
    """Divides the timeline into sections with Markov-chain transitions.

    Section types: sparse, medium, dense, climax, silence.
    """

    TRANSITIONS = {
        "sparse":  {"sparse": 0.2, "medium": 0.5, "dense": 0.1, "climax": 0.0, "silence": 0.2},
        "medium":  {"sparse": 0.2, "medium": 0.3, "dense": 0.3, "climax": 0.1, "silence": 0.1},
        "dense":   {"sparse": 0.1, "medium": 0.2, "dense": 0.3, "climax": 0.3, "silence": 0.1},
        "climax":  {"sparse": 0.3, "medium": 0.2, "dense": 0.1, "climax": 0.1, "silence": 0.3},
        "silence": {"sparse": 0.5, "medium": 0.3, "dense": 0.1, "climax": 0.0, "silence": 0.1},
    }

    SECTION_DENSITY = {
        "silence": 0.0,
        "sparse": 0.3,
        "medium": 0.7,
        "dense": 1.0,
        "climax": 1.5,
    }

    def generate(
        self,
        sources: dict[str, AudioBuffer],
        constraints: CompositionConstraints,
        rng: ControlledRandom,
    ) -> Composition:
        # 1. Generate section sequence
        sections = self._generate_sections(constraints.total_duration, rng)

        # 2. For each track, fill sections with events
        source_names = list(sources.keys())
        s_weights = (
            [constraints.source_weights.get(n, 1.0) for n in source_names]
            if constraints.source_weights
            else [1.0] * len(source_names)
        )

        tracks: list[Track] = []
        for ti in range(constraints.num_tracks):
            track_rng = rng.fork()
            events: list[AudioEvent] = []

            for section_type, sec_start, sec_dur in sections:
                density = self.SECTION_DENSITY[section_type]
                if density <= 0:
                    continue

                # number of events proportional to density
                avg_event_dur = (constraints.min_event_duration + constraints.max_event_duration) / 2
                n_events = max(1, int(density * sec_dur / avg_event_dur))
                current = sec_start

                for _ in range(n_events):
                    if current >= sec_start + sec_dur:
                        break

                    name = track_rng.weighted_choice(source_names, s_weights)
                    src = sources[name]

                    dur = track_rng.gaussian(
                        mean=avg_event_dur * (0.5 + density * 0.5),
                        std=avg_event_dur * 0.3,
                        clip_low=constraints.min_event_duration,
                        clip_high=min(constraints.max_event_duration, src.duration),
                    )

                    max_start = max(0.0, src.duration - dur)
                    seg_start = track_rng.uniform(0.0, max_start)

                    gap = track_rng.uniform(
                        constraints.min_silence,
                        constraints.max_silence,
                    ) / max(density, 0.3)

                    event = AudioEvent(
                        source_name=name,
                        source_start=seg_start,
                        source_end=seg_start + dur,
                        timeline_start=current,
                        track_index=ti,
                        amplitude=track_rng.uniform(
                            constraints.amplitude_min,
                            constraints.amplitude_max * density,
                        ),
                        pan=track_rng.uniform(constraints.pan_min, constraints.pan_max),
                        fade_in=track_rng.uniform(constraints.fade_in_min, constraints.fade_in_max),
                        fade_out=track_rng.uniform(constraints.fade_out_min, constraints.fade_out_max),
                        effects_config=_random_effects_config(track_rng, constraints),
                        is_reversed=track_rng.boolean(0.1),
                    )
                    events.append(event)
                    current += dur + gap

            tracks.append(Track(index=ti, name=f"Track {ti + 1}", events=events))

        return Composition(tracks=tracks, sample_rate=44100, seed=rng.seed)

    def _generate_sections(
        self, total_duration: float, rng: ControlledRandom
    ) -> list[tuple[str, float, float]]:
        sections: list[tuple[str, float, float]] = []
        current = 0.0
        state = rng.choice(list(self.TRANSITIONS.keys()))

        while current < total_duration:
            dur = rng.gaussian(
                mean=total_duration / 8,
                std=total_duration / 16,
                clip_low=5.0,
                clip_high=total_duration / 3,
            )
            dur = min(dur, total_duration - current)
            sections.append((state, current, dur))
            state = rng.markov_choice(state, self.TRANSITIONS)
            current += dur

        return sections


# ---------------------------------------------------------------------------
# LayerStrategy
# ---------------------------------------------------------------------------

class LayerStrategy(CompositionStrategy):
    """Each track is a continuous textural layer derived from one source.

    Sources are time-stretched to fill the duration, with evolving effects.
    """

    def generate(
        self,
        sources: dict[str, AudioBuffer],
        constraints: CompositionConstraints,
        rng: ControlledRandom,
    ) -> Composition:
        source_names = list(sources.keys())
        s_weights = (
            [constraints.source_weights.get(n, 1.0) for n in source_names]
            if constraints.source_weights
            else [1.0] * len(source_names)
        )

        tracks: list[Track] = []
        for ti in range(constraints.num_tracks):
            track_rng = rng.fork()
            name = track_rng.weighted_choice(source_names, s_weights)
            src = sources[name]

            # Create overlapping segments that tile the full duration
            events: list[AudioEvent] = []
            current = 0.0
            while current < constraints.total_duration:
                remaining = constraints.total_duration - current
                dur = min(src.duration, remaining + 2.0)  # slight overlap
                seg_start = track_rng.uniform(0.0, max(0.0, src.duration - dur))

                event = AudioEvent(
                    source_name=name,
                    source_start=seg_start,
                    source_end=seg_start + min(dur, src.duration - seg_start),
                    timeline_start=current,
                    track_index=ti,
                    amplitude=track_rng.uniform(0.4, 0.8),
                    pan=track_rng.uniform(constraints.pan_min, constraints.pan_max),
                    fade_in=min(2.0, dur * 0.3),
                    fade_out=min(2.0, dur * 0.3),
                    effects_config=_random_effects_config(track_rng, constraints),
                )
                events.append(event)
                current += dur - 2.0  # crossfade overlap of 2 seconds
                if dur <= 2.0:
                    current += dur

            tracks.append(Track(index=ti, name=f"Layer {ti + 1}", events=events))

        return Composition(tracks=tracks, sample_rate=44100, seed=rng.seed)


# ---------------------------------------------------------------------------
# CanonStrategy
# ---------------------------------------------------------------------------

class CanonStrategy(CompositionStrategy):
    """Creates canon-like structures where material appears offset across tracks."""

    def generate(
        self,
        sources: dict[str, AudioBuffer],
        constraints: CompositionConstraints,
        rng: ControlledRandom,
    ) -> Composition:
        source_names = list(sources.keys())
        s_weights = (
            [constraints.source_weights.get(n, 1.0) for n in source_names]
            if constraints.source_weights
            else [1.0] * len(source_names)
        )

        # Generate a base sequence of events for track 0
        base_rng = rng.fork()
        base_events: list[AudioEvent] = []
        current = 0.0

        while current < constraints.total_duration:
            name = base_rng.weighted_choice(source_names, s_weights)
            src = sources[name]

            dur = base_rng.gaussian(
                mean=(constraints.min_event_duration + constraints.max_event_duration) / 2,
                std=(constraints.max_event_duration - constraints.min_event_duration) / 4,
                clip_low=constraints.min_event_duration,
                clip_high=min(constraints.max_event_duration, src.duration),
            )

            max_start = max(0.0, src.duration - dur)
            seg_start = base_rng.uniform(0.0, max_start)

            gap = base_rng.uniform(constraints.min_silence, constraints.max_silence)

            event = AudioEvent(
                source_name=name,
                source_start=seg_start,
                source_end=seg_start + dur,
                timeline_start=current,
                track_index=0,
                amplitude=base_rng.uniform(constraints.amplitude_min, constraints.amplitude_max),
                pan=0.0,
                fade_in=base_rng.uniform(constraints.fade_in_min, constraints.fade_in_max),
                fade_out=base_rng.uniform(constraints.fade_out_min, constraints.fade_out_max),
            )
            base_events.append(event)
            current += dur + gap

        tracks = [Track(index=0, name="Canon 1", events=base_events)]

        # Create offset copies for other tracks
        for ti in range(1, constraints.num_tracks):
            track_rng = rng.fork()
            offset = track_rng.uniform(2.0, constraints.total_duration * 0.2)
            copied_events: list[AudioEvent] = []

            for be in base_events:
                new_start = be.timeline_start + offset
                if new_start + be.duration > constraints.total_duration:
                    break

                event = AudioEvent(
                    source_name=be.source_name,
                    source_start=be.source_start,
                    source_end=be.source_end,
                    timeline_start=new_start,
                    track_index=ti,
                    amplitude=be.amplitude * track_rng.uniform(0.6, 1.0),
                    pan=track_rng.uniform(constraints.pan_min, constraints.pan_max),
                    fade_in=be.fade_in,
                    fade_out=be.fade_out,
                    effects_config=_random_effects_config(track_rng, constraints),
                    is_reversed=track_rng.boolean(0.2),
                )
                copied_events.append(event)

            tracks.append(Track(index=ti, name=f"Canon {ti + 1}", events=copied_events))

        return Composition(tracks=tracks, sample_rate=44100, seed=rng.seed)


# ---------------------------------------------------------------------------
# Strategy registry
# ---------------------------------------------------------------------------

STRATEGIES: dict[str, type[CompositionStrategy]] = {
    "scatter": ScatterStrategy,
    "structured": StructuredStrategy,
    "layer": LayerStrategy,
    "canon": CanonStrategy,
}
