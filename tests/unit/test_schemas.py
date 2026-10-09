import pytest
from pydantic import ValidationError

from app.api.schemas.chat import ChatRequest


def test_omitted_conversation_id_starts_new_conversation():
    request = ChatRequest(
        message="What is a computer?"
    )

    assert request.conversation_id is None


def test_null_conversation_id_is_allowed():
    request = ChatRequest(
        conversation_id=None,
        message="What is a computer?",
    )

    assert request.conversation_id is None


def test_placeholder_conversation_id_is_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(
            conversation_id="string",
            message="What is a computer?",
        )


def test_whitespace_message_is_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")