import pytest
from datetime import datetime, timezone
from app.domain.exceptions import ConversationNotFoundError
from app.application.query_manager import QueryManager
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


class FakeLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self.received_messages: list[Message] = []
        self.received_settings: ModelSettings | None = None

    def generate(
        self,
        messages: list[Message],
        settings: ModelSettings,
    ) -> str:
        self.received_messages = messages
        self.received_settings = settings

        return "This is a test response."

    def stream(
    self,
    messages: list[Message],
    settings: ModelSettings,
):
        self.received_messages = messages
        self.received_settings = settings

        yield "This is a test "
        yield "response."


class FakeConversationRepository(ConversationRepository):
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


class FakeMessageRepository(MessageRepository):
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


def create_manager():
    llm_provider = FakeLLMProvider()
    conversation_repository = FakeConversationRepository()
    message_repository = FakeMessageRepository()

    manager = QueryManager(
        llm_provider=llm_provider,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        default_model="llama3.2",
        system_prompt="You are MRBot.",
    )

    return (
        manager,
        llm_provider,
        conversation_repository,
        message_repository,
    )


def test_query_manager_creates_conversation():
    (
        manager,
        llm_provider,
        conversation_repository,
        message_repository,
    ) = create_manager()

    result = manager.execute(
        message="  Hello  ",
        temperature=0.2,
    )

    assert result.response == "This is a test response."
    assert result.model == "llama3.2"

    assert result.conversation_id in conversation_repository.conversations

    assert len(message_repository.messages) == 2

    assert message_repository.messages[0].role == MessageRole.USER
    assert message_repository.messages[0].content == "Hello"

    assert message_repository.messages[1].role == MessageRole.ASSISTANT


def test_query_manager_builds_conversation_context():
    (
        manager,
        llm_provider,
        conversation_repository,
        message_repository,
    ) = create_manager()

    now = datetime.now(timezone.utc)

    conversation = Conversation(
        id="conversation-1",
        user_id=None,
        title="Test",
        model="llama3.2",
        created_at=now,
        updated_at=now,
    )

    conversation_repository.create(conversation)

    message_repository.add(
        Message(
            id="message-1",
            conversation_id="conversation-1",
            role=MessageRole.USER,
            content="What is Python?",
            created_at=now,
        )
    )

    message_repository.add(
        Message(
            id="message-2",
            conversation_id="conversation-1",
            role=MessageRole.ASSISTANT,
            content="Python is a programming language.",
            created_at=now,
        )
    )

    result = manager.execute(
        message="What can Python be used for?",
        conversation_id="conversation-1",
    )

    assert result.conversation_id == "conversation-1"

    roles = [
        message.role
        for message in llm_provider.received_messages
    ]

    contents = [
        message.content
        for message in llm_provider.received_messages
    ]

    assert roles == [
        MessageRole.SYSTEM,
        MessageRole.USER,
        MessageRole.ASSISTANT,
        MessageRole.USER,
    ]

    assert contents[-1] == "What can Python be used for?"

    assert llm_provider.received_settings is not None
    assert llm_provider.received_settings.model == "llama3.2"


def test_query_manager_rejects_blank_message():
    (
        manager,
        _,
        _,
        _,
    ) = create_manager()

    try:
        manager.execute("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Message cannot be empty."
def test_query_manager_rejects_unknown_conversation():
    manager, _, _, _ = create_manager()

    with pytest.raises(ConversationNotFoundError):
        manager.execute(
            message="What is a computer?",
            conversation_id="00000000-0000-4000-8000-000000000001",)

def test_query_manager_isolates_conversation_history():
    (
        manager,
        llm_provider,
        conversation_repository,
        message_repository,
    ) = create_manager()

    now = datetime.now(timezone.utc)

    # Create two independent conversations.
    conversation_a = Conversation(
        id="conversation-A",
        user_id=None,
        title="Conversation A",
        model="llama3.2",
        created_at=now,
        updated_at=now,
    )

    conversation_b = Conversation(
        id="conversation-B",
        user_id=None,
        title="Conversation B",
        model="llama3.2",
        created_at=now,
        updated_at=now,
    )

    conversation_repository.create(conversation_a)
    conversation_repository.create(conversation_b)

    # Add a unique message to Conversation A.
    message_repository.add(
        Message(
            id="message-A",
            conversation_id="conversation-A",
            role=MessageRole.USER,
            content="My secret test word is BLUEBIRD.",
            created_at=now,
        )
    )

    # Add separate history to Conversation B.
    message_repository.add(
        Message(
            id="message-B",
            conversation_id="conversation-B",
            role=MessageRole.USER,
            content="I am learning about computers.",
            created_at=now,
        )
    )

    # Execute a query only in Conversation B.
    result = manager.execute(
        message="What topic am I learning about?",
        conversation_id="conversation-B",
    )

    # Confirm the request stayed in Conversation B.
    assert result.conversation_id == "conversation-B"

    received_contents = [
        message.content
        for message in llm_provider.received_messages
    ]

    # Conversation B's context includes its own history and query.
    assert "I am learning about computers." in received_contents
    assert "What topic am I learning about?" in received_contents

    # Conversation A's private test message must not leak.
    assert "My secret test word is BLUEBIRD." not in received_contents

    # System prompt remains in the context.
    assert "You are MRBot." in received_contents


def test_query_manager_streams_and_persists_response():
    (
        manager,
        llm_provider,
        conversation_repository,
        message_repository,
    ) = create_manager()

    chunks = list(
        manager.execute_stream(
            message="What is a computer?",
        )
    )

    assert chunks == ["This is a test ", "response."]

    assert len(message_repository.messages) == 2
    assert message_repository.messages[0].role == MessageRole.USER
    assert message_repository.messages[0].content == "What is a computer?"
    assert message_repository.messages[1].role == MessageRole.ASSISTANT
    assert message_repository.messages[1].content == "This is a test response."

    assert llm_provider.received_messages

def test_query_manager_does_not_persist_failed_stream():
    (
        manager,
        llm_provider,
        _,
        message_repository,
    ) = create_manager()

    def failing_stream(messages, settings):
        yield "Partial answer"
        raise RuntimeError("Simulated Ollama failure")

    llm_provider.stream = failing_stream

    with pytest.raises(RuntimeError, match="Simulated Ollama failure"):
        list(manager.execute_stream(message="Test failure"))

    assert message_repository.messages == []


def test_query_manager_does_not_persist_closed_stream():
    (
        manager,
        llm_provider,
        _,
        message_repository,
    ) = create_manager()

    def long_stream(messages, settings):
        yield "First chunk"
        yield "Second chunk"

    llm_provider.stream = long_stream

    stream = manager.execute_stream(message="Test disconnect")

    assert next(stream) == "First chunk"

    stream.close()

    assert message_repository.messages == []
