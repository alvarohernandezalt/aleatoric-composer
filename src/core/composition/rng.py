"""Controllable random number generator with multiple distribution types."""

from __future__ import annotations

import time

import numpy as np


class ControlledRandom:
    """Seeded RNG with selectable probability distributions and constraints."""

    def __init__(self, seed: int | None = None):
        self.seed = seed if seed is not None else int(time.time())
        self._rng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # Basic distributions
    # ------------------------------------------------------------------

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        return float(self._rng.uniform(low, high))

    def gaussian(
        self,
        mean: float,
        std: float,
        clip_low: float | None = None,
        clip_high: float | None = None,
    ) -> float:
        val = float(self._rng.normal(mean, std))
        if clip_low is not None:
            val = max(val, clip_low)
        if clip_high is not None:
            val = min(val, clip_high)
        return val

    def integer(self, low: int, high: int) -> int:
        """Inclusive on both ends."""
        return int(self._rng.integers(low, high + 1))

    def boolean(self, probability: float = 0.5) -> bool:
        return self._rng.random() < probability

    # ------------------------------------------------------------------
    # Weighted / discrete choice
    # ------------------------------------------------------------------

    def weighted_choice(self, items: list, weights: list[float]):
        """Choose from *items* using *weights* as probabilities."""
        probs = np.array(weights, dtype=np.float64)
        probs /= probs.sum()
        idx = self._rng.choice(len(items), p=probs)
        return items[idx]

    def choice(self, items: list):
        """Uniform random choice from a list."""
        return items[self._rng.integers(0, len(items))]

    # ------------------------------------------------------------------
    # Quasi-random / low-discrepancy
    # ------------------------------------------------------------------

    def van_der_corput(self, n: int, base: int = 2) -> list[float]:
        """Generate *n* values in a low-discrepancy Van der Corput sequence."""
        sequence: list[float] = []
        for i in range(1, n + 1):
            vdc, denom = 0.0, 1.0
            num = i
            while num > 0:
                denom *= base
                num, remainder = divmod(num, base)
                vdc += remainder / denom
            sequence.append(vdc)
        return sequence

    # ------------------------------------------------------------------
    # Markov chain
    # ------------------------------------------------------------------

    def markov_choice(
        self,
        current_state: str,
        transition_matrix: dict[str, dict[str, float]],
    ) -> str:
        """Choose next state from a Markov transition matrix."""
        transitions = transition_matrix[current_state]
        states = list(transitions.keys())
        weights = list(transitions.values())
        return self.weighted_choice(states, weights)

    # ------------------------------------------------------------------
    # Forking
    # ------------------------------------------------------------------

    def fork(self) -> ControlledRandom:
        """Create a child RNG derived from this one (for independent tracks)."""
        child_seed = int(self._rng.integers(0, 2**31))
        return ControlledRandom(seed=child_seed)
