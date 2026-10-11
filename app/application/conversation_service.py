from datetime import datetime, timezone
from uuid import uuid4

from app.domain.exceptions import ConversationNotFoundError
from app.domain.models import Conversation


class ConversationService:
    def __init__(
        self,
        conversation_repository,
        message_repository,
        default_model: str,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.default_model = default_model

    def create(
        self,
        title: str | None = None,
        model: str | None = None,
    ) -> Conversation:
        now = datetime.now(timezone.utc)

        conversation = Conversation(
            id=str(uuid4()),
            user_id=None,
            title=title.strip() if title and title.strip() else None,
            model=model or self.default_model,
            created_at=now,
            updated_at=now,
        )

        return self.conversation_repository.create(conversation)

    def list_all(self) -> list[Conversation]:
        return self.conversation_repository.list()

    def get(self, conversation_id: str):
        conversation = self.conversation_repository.get_by_id(
            conversation_id
        )

        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        messages = self.message_repository.get_by_conversation_id(
            conversation_id
        )

        return conversation, messages

    def delete(self, conversation_id: str) -> None:
        conversation = self.conversation_repository.get_by_id(
            conversation_id
        )

        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        self.conversation_repository.delete(conversation_id)