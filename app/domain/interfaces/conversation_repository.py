from abc import ABC, abstractmethod

from app.domain.models import Conversation


class ConversationRepository(ABC):

    @abstractmethod
    def create(self, conversation: Conversation) -> Conversation:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Conversation | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Conversation]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        raise NotImplementedError