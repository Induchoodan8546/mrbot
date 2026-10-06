from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str | None = None
    model: str | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str | None = None
    model: str | None = None