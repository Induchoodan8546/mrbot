from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. Omit or use null to start a new conversation.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="The message to send to MRBot.",
    )

    model: str | None = Field(
        default=None,
        description="Optional Ollama model name. Uses the configured default when omitted.",
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    stream: bool = False

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty or whitespace.")

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "conversation_id": None,
                    "message": "What is a computer?",
                    "model": None,
                    "temperature": 0.7,
                    "stream": False,
                }
            ]
        }
    )


class ChatResponse(BaseModel):
    conversation_id: str
    message: str