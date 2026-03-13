"""High-level composition generator."""

from __future__ import annotations

from src.core.audio_buffer import AudioBuffer
from src.core.composition.constraints import CompositionConstraints
from src.core.composition.rng import ControlledRandom
from src.core.composition.strategies import CompositionStrategy, STRATEGIES
from src.core.composition.timeline import Composition


class Arranger:
    """Combines a strategy, constraints, and source audio to produce compositions."""

    def __init__(
        self,
        strategy: CompositionStrategy | str,
        constraints: CompositionConstraints,
    ):
        if isinstance(strategy, str):
            cls = STRATEGIES[strategy]
            self.strategy = cls()
        else:
            self.strategy = strategy

        self.constraints = constraints
        self.rng = ControlledRandom(seed=constraints.master_seed)
        self._last_sources: dict[str, AudioBuffer] | None = None

    def compose(self, sources: dict[str, AudioBuffer]) -> Composition:
        """Generate a composition from the given source audio files."""
        self._last_sources = sources
        return self.strategy.generate(sources, self.constraints, self.rng)

    def reroll(self) -> Composition:
        """Generate a new variation by advancing the RNG state."""
        if self._last_sources is None:
            raise RuntimeError("Call compose() first before reroll()")
        self.rng = self.rng.fork()
        return self.strategy.generate(self._last_sources, self.constraints, self.rng)
