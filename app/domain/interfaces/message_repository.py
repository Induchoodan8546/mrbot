from abc import ABC, abstractmethod

from app.domain.models import Message


class MessageRepository(ABC):

    @abstractmethod
    def add(self, message: Message) -> Message:
        raise NotImplementedError

    @abstractmethod
    def get_by_conversation_id(
        self,
        conversation_id: str,
    ) -> list[Message]:
        raise NotImplementedError