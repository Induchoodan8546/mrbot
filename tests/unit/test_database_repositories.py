from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.models import (
    Conversation,
    Message,
    MessageRole,
)
from app.infrastructure.database.connection import Base
from app.infrastructure.database.models import (
    ConversationORM,
    MessageORM,
)
from app.infrastructure.database.repositories import (
    SQLAlchemyConversationRepository,
    SQLAlchemyMessageRepository,
)


def create_test_repositories(tmp_path):
    database_path = tmp_path / "test_mrbot.db"

    test_engine = create_engine(
        f"sqlite:///{database_path}",
    )

    Base.metadata.create_all(bind=test_engine)

    test_session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    conversations = SQLAlchemyConversationRepository(
        session_factory=test_session_factory,
    )

    messages = SQLAlchemyMessageRepository(
        session_factory=test_session_factory,
    )

    return test_engine, conversations, messages


def test_conversation_persists_between_repository_instances(tmp_path):
    engine, repository, _ = create_test_repositories(tmp_path)

    try:
        now = datetime.now(timezone.utc)

        conversation = Conversation(
            id="conversation-1",
            user_id=None,
            title="Persistence test",
            model="llama3.2",
            created_at=now,
            updated_at=now,
        )

        repository.create(conversation)

        # A new repository instance reads from the same database.
        another_repository = SQLAlchemyConversationRepository(
            session_factory=repository.session_factory,
        )

        loaded = another_repository.get_by_id("conversation-1")

        assert loaded is not None
        assert loaded.id == "conversation-1"
        assert loaded.title == "Persistence test"

    finally:
        engine.dispose()


def test_messages_persist_in_insertion_order(tmp_path):
    engine, conversations, messages = create_test_repositories(
        tmp_path
    )

    try:
        now = datetime.now(timezone.utc)

        conversations.create(
            Conversation(
                id="conversation-2",
                user_id=None,
                title="Order test",
                model="llama3.2",
                created_at=now,
                updated_at=now,
            )
        )

        messages.add(
            Message(
                id="message-1",
                conversation_id="conversation-2",
                role=MessageRole.USER,
                content="Hello",
                created_at=now,
            )
        )

        messages.add(
            Message(
                id="message-2",
                conversation_id="conversation-2",
                role=MessageRole.ASSISTANT,
                content="Hi there!",
                created_at=now,
            )
        )

        history = messages.get_by_conversation_id(
            "conversation-2"
        )

        assert [message.content for message in history] == [
            "Hello",
            "Hi there!",
        ]

        assert [message.role for message in history] == [
            MessageRole.USER,
            MessageRole.ASSISTANT,
        ]

    finally:
        engine.dispose()