
from functools import lru_cache

from app.application.query_manager import QueryManager
from app.application.conversation_service import ConversationService
from app.core.config import settings
from app.core.prompts import MRBOT_SYSTEM_PROMPT
from app.infrastructure.database.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyMessageRepository,
)
from app.infrastructure.llm.ollama_provider import OllamaProvider


@lru_cache
def get_query_manager() -> QueryManager:
    llm_provider = OllamaProvider()

    conversation_repository = SQLAlchemyConversationRepository()
    message_repository = SQLAlchemyMessageRepository()

    return QueryManager(
        llm_provider=llm_provider,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        default_model=settings.ollama_model,
        system_prompt=MRBOT_SYSTEM_PROMPT,
    )


@lru_cache
def get_conversation_service() -> ConversationService:
    return ConversationService(
        conversation_repository=SQLAlchemyConversationRepository(),
        message_repository=SQLAlchemyMessageRepository(),
        default_model=settings.ollama_model,
    )
