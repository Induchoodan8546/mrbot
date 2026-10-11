from app.infrastructure.database.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyMessageRepository,
)


def get_conversation_repository() -> SQLAlchemyConversationRepository:
    return SQLAlchemyConversationRepository()


def get_message_repository() -> SQLAlchemyMessageRepository:
    return SQLAlchemyMessageRepository()