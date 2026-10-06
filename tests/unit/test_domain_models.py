from datetime import datetime

from app.domain.models import (
    Conversation,
    Message,
    MessageRole,
    ModelSettings,
)


def test_message_model():
    message = Message(
        id="msg-1",
        conversation_id="conv-1",
        role=MessageRole.USER,
        content="Hello",
        created_at=datetime.now(),
    )

    assert message.id == "msg-1"
    assert message.role == MessageRole.USER
    assert message.content == "Hello"


def test_conversation_model():
    now = datetime.now()

    conversation = Conversation(
        id="conv-1",
        user_id=None,
        title="Test conversation",
        model="llama3.2",
        created_at=now,
        updated_at=now,
    )

    assert conversation.id == "conv-1"
    assert conversation.model == "llama3.2"


def test_model_settings():
    settings = ModelSettings(
        model="llama3.2",
        temperature=0.7,
    )

    assert settings.model == "llama3.2"
    assert settings.temperature == 0.7