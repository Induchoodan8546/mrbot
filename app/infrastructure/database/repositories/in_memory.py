from app.domain.models import Conversation, Message
from app.domain.interfaces import (
    ConversationRepository,
    MessageRepository,
)


class InMemoryConversationRepository(ConversationRepository):
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}

    def create(self, conversation: Conversation) -> Conversation:
        self.conversations[conversation.id] = conversation
        return conversation

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        return self.conversations.get(conversation_id)

    def list(self) -> list[Conversation]:
        return list(self.conversations.values())

    def delete(self, conversation_id: str) -> None:
        self.conversations.pop(conversation_id, None)


class InMemoryMessageRepository(MessageRepository):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add(self, message: Message) -> Message:
        self.messages.append(message)
        return message

    def get_by_conversation_id(
        self,
        conversation_id: str,
    ) -> list[Message]:
        return [
            message
            for message in self.messages
            if message.conversation_id == conversation_id
        ]