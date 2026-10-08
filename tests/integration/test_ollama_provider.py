from datetime import datetime

from app.domain.models import Message, MessageRole, ModelSettings
from app.infrastructure.llm.ollama_provider import OllamaProvider


def test_ollama_generate():
    provider = OllamaProvider()

    messages = [
        Message(
            id="msg-1",
            conversation_id="conv-1",
            role=MessageRole.USER,
            content="Say hello in one sentence.",
            created_at=datetime.now(),
        )
    ]

    settings = ModelSettings(
        model="llama3.2",
        temperature=0.2,
    )

    response = provider.generate(
        messages,
        settings,
    )

    assert isinstance(response, str)
    assert response.strip()