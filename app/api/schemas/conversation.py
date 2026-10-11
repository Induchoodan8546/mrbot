
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import MessageRole


class ConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, min_length=1, max_length=100)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    token_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    title: str | None = None
    model: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = Field(default_factory=list)


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class ConversationDeleteResponse(BaseModel):
    message: str
    conversation_id: UUID
