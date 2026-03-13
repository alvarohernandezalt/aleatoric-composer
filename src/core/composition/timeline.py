"""Data model for a multitrack composition."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AudioEvent:
    """A single audio event placed on the timeline."""

    source_name: str
    source_start: float          # offset within source (seconds)
    source_end: float            # end offset within source (seconds)
    timeline_start: float        # position on the composition timeline (seconds)
    track_index: int

    amplitude: float = 1.0
    pan: float = 0.0             # -1.0 left … +1.0 right
    fade_in: float = 0.01        # seconds
    fade_out: float = 0.01       # seconds
    effects_config: list[dict] = field(default_factory=list)
    is_reversed: bool = False

    @property
    def duration(self) -> float:
        return self.source_end - self.source_start

    @property
    def timeline_end(self) -> float:
        return self.timeline_start + self.duration


@dataclass
class Track:
    """A single track in the composition."""

    index: int
    name: str = ""
    events: list[AudioEvent] = field(default_factory=list)
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False


@dataclass
class Composition:
    """The complete multitrack composition."""

    tracks: list[Track] = field(default_factory=list)
    sample_rate: int = 44100
    seed: int = 42

    @property
    def duration(self) -> float:
        all_ends = [e.timeline_end for t in self.tracks for e in t.events]
        return max(all_ends) if all_ends else 0.0

    @property
    def num_events(self) -> int:
        return sum(len(t.events) for t in self.tracks)
