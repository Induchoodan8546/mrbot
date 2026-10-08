from datetime import datetime, timezone

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
        yield "This is a test response."


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