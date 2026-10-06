from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime
    token_count: int | None = None