from functools import lru_cache

from app.application.query_manager import QueryManager
from app.core.config import settings
from app.infrastructure.database.repositories.in_memory import (
    InMemoryConversationRepository,
    InMemoryMessageRepository,
)
from app.infrastructure.llm.ollama_provider import OllamaProvider


@lru_cache
def get_query_manager() -> QueryManager:
    llm_provider = OllamaProvider()

    conversation_repository = InMemoryConversationRepository()
    message_repository = InMemoryMessageRepository()

    return QueryManager(
        llm_provider=llm_provider,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        default_model=settings.ollama_model,
        system_prompt="You are MRBot, a helpful local AI assistant.",
    )