from app.domain.exceptions import ConversationNotFoundError
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.interfaces import (
    ConversationRepository,
    LLMProvider,
    MessageRepository,
)
from app.domain.models import (
    Conversation,
    Message,
    MessageRole,
    ModelSettings,
)


@dataclass(frozen=True)
class QueryResult:
    conversation_id: str
    response: str
    model: str


class QueryManager:
    def __init__(
        self,
        llm_provider: LLMProvider,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        default_model: str,
        system_prompt: str = "",
    ) -> None:
        self.llm_provider = llm_provider
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.default_model = default_model
        self.system_prompt = system_prompt.strip()

    def execute(
        self,
        message: str,
        conversation_id: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
    ) -> QueryResult:

        query = self._normalize_query(message)

        conversation = self._resolve_conversation(
            conversation_id=conversation_id,
            requested_model=model,
        )

        selected_model = model or conversation.model

        history = self.message_repository.get_by_conversation_id(
            conversation.id
        )

        context = self._build_context(
            conversation_id=conversation.id,
            history=history,
            user_query=query,
        )

        model_settings = ModelSettings(
            model=selected_model,
            temperature=temperature,
        )

        response = self.llm_provider.generate(
            messages=context,
            settings=model_settings,
        )

        response_text = self._normalize_response(response)

        self._persist_messages(
            conversation_id=conversation.id,
            user_query=query,
            assistant_response=response_text,
        )

        return QueryResult(
            conversation_id=conversation.id,
            response=response_text,
            model=selected_model,
        )

    @staticmethod
    def _normalize_query(message: str) -> str:
        query = message.strip()

        if not query:
            raise ValueError("Message cannot be empty.")

        return query

    def _resolve_conversation(
        self,
        conversation_id: str | None,
        requested_model: str | None,
    ) -> Conversation:

        if conversation_id is not None:
            conversation = self.conversation_repository.get_by_id(
                conversation_id
            )

            if conversation is None:
                raise ConversationNotFoundError(conversation_id)
            return conversation

        now = datetime.now(timezone.utc)

        conversation = Conversation(
            id=str(uuid4()),
            user_id=None,
            title=None,
            model=requested_model or self.default_model,
            created_at=now,
            updated_at=now,
        )

        return self.conversation_repository.create(conversation)

    def _build_context(
        self,
        conversation_id: str,
        history: list[Message],
        user_query: str,
    ) -> list[Message]:

        context: list[Message] = []

        if self.system_prompt:
            context.append(
                Message(
                    id=str(uuid4()),
                    conversation_id=conversation_id,
                    role=MessageRole.SYSTEM,
                    content=self.system_prompt,
                    created_at=datetime.now(timezone.utc),
                )
            )

        context.extend(history)

        context.append(
            Message(
                id=str(uuid4()),
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=user_query,
                created_at=datetime.now(timezone.utc),
            )
        )

        return context

    @staticmethod
    def _normalize_response(response: str) -> str:
        return response.strip()

    def _persist_messages(
        self,
        conversation_id: str,
        user_query: str,
        assistant_response: str,
    ) -> None:

        now = datetime.now(timezone.utc)

        user_message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_query,
            created_at=now,
        )

        assistant_message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_response,
            created_at=datetime.now(timezone.utc),
        )

        self.message_repository.add(user_message)
        self.message_repository.add(assistant_message)