from __future__ import annotations

from src.core.audio_buffer import AudioBuffer
from src.core.effects.base import Effect


class EffectChain:
    """Ordered sequence of effects applied to an AudioBuffer."""

    def __init__(self, effects: list[Effect] | None = None):
        self.effects: list[Effect] = list(effects) if effects else []

    def add(self, effect: Effect) -> EffectChain:
        self.effects.append(effect)
        return self

    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        result = buffer
        for effect in self.effects:
            result = effect.process(result)
        return result

    def serialize(self) -> list[dict]:
        return [e.serialize() for e in self.effects]

    def __len__(self) -> int:
        return len(self.effects)

    def __repr__(self) -> str:
        names = " -> ".join(e.__class__.__name__ for e in self.effects)
        return f"EffectChain([{names}])"
