from abc import ABC, abstractmethod
from collections.abc import Iterator

from app.domain.models import Message, ModelSettings


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        settings: ModelSettings,
    ) -> str:
        """Generate a complete response."""
        raise NotImplementedError

    @abstractmethod
    def stream(
        self,
        messages: list[Message],
        settings: ModelSettings,
    ) -> Iterator[str]:
        """Generate a response incrementally."""
        raise NotImplementedError