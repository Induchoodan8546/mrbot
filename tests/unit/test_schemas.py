import pytest
from pydantic import ValidationError

from app.api.schemas.chat import ChatRequest


def test_valid_chat_request():
    request = ChatRequest(
        message="Explain gradient descent"
    )

    assert request.message == "Explain gradient descent"
    assert request.temperature == 0.7
    assert request.stream is False


def test_empty_message_is_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_invalid_temperature_is_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(
            message="Hello",
            temperature=3.0
        )