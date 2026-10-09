from collections.abc import Iterator

from ollama import Client

from app.core.config import settings as app_settings
from app.domain.interfaces import LLMProvider
from app.domain.models import Message, ModelSettings


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = Client(host=app_settings.ollama_base_url)

    @staticmethod
    def _convert_messages(messages: list[Message]) -> list[dict[str, str]]:
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in messages
        ]

    def generate(
        self,
        messages: list[Message],
        settings: ModelSettings,
    ) -> str:
        response = self.client.chat(
            model=settings.model,
            messages=self._convert_messages(messages),
            options={"temperature": settings.temperature},
            stream=False,
        )
        return response.message.content

    def stream(
        self,
        messages: list[Message],
        settings: ModelSettings,
    ) -> Iterator[str]:
        response = self.client.chat(
            model=settings.model,
            messages=self._convert_messages(messages),
            options={"temperature": settings.temperature},
            stream=True,
        )

        for chunk in response:
            content = chunk.message.content
            if content:
                yield content