from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.audio_buffer import AudioBuffer


class Effect(ABC):
    """Base class for all audio effects."""

    @abstractmethod
    def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply effect and return a new AudioBuffer."""

    @abstractmethod
    def get_parameters(self) -> dict[str, Any]:
        """Return current parameter values."""

    @abstractmethod
    def set_parameters(self, **kwargs: Any) -> None:
        """Update parameter values."""

    def serialize(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "parameters": self.get_parameters(),
        }

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v}" for k, v in self.get_parameters().items())
        return f"{self.__class__.__name__}({params})"
