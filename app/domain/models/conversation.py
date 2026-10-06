from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conversation:
    id: str
    user_id: str | None
    title: str | None
    model: str
    created_at: datetime
    updated_at: datetime