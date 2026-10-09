from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.application.query_manager import QueryManager
from app.core.dependencies import get_query_manager
from app.domain.exceptions import ConversationNotFoundError


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    query_manager: QueryManager = Depends(get_query_manager),
) -> ChatResponse:
    # Convert UUID to str because the domain and repositories use string IDs.
    conversation_id = (
        str(request.conversation_id)
        if request.conversation_id is not None
        else None
    )

    try:
        result = query_manager.execute(
            message=request.message,
            conversation_id=conversation_id,
            model=request.model,
            temperature=request.temperature,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "conversation_not_found",
                "message": str(exc),
            },
        ) from exc

    return ChatResponse(
        conversation_id=result.conversation_id,
        message=result.response,
    )