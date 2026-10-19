
#from app.core.exception_handlers import logger
import json
from collections.abc import Iterator
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.application.query_manager import QueryManager
from app.core.dependencies import get_query_manager
from app.domain.exceptions import ConversationNotFoundError


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    query_manager: QueryManager = Depends(get_query_manager),
) -> ChatResponse:
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


@router.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    query_manager: QueryManager = Depends(get_query_manager),
) -> StreamingResponse:
    conversation_id = (
        str(request.conversation_id)
        if request.conversation_id is not None
        else None
    )

    # Resolve the conversation before returning the stream so that
    # a missing conversation can return a normal HTTP 404 response.
    if conversation_id is not None:
        conversation = query_manager.conversation_repository.get_by_id(
            conversation_id
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "conversation_not_found",
                    "message": f"Conversation not found: {conversation_id}",
                },
            )

    def generate_events() -> Iterator[str]:
        try:
            for chunk in query_manager.execute_stream(
                message=request.message,
                conversation_id=conversation_id,
                model=request.model,
                temperature=request.temperature,
            ):
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

            yield "event: done\ndata: {}\n\n"

        except Exception:
            logger.exception("MRBot streaming response failed")

            yield (
            "event: error\n"
            + "data: "
            + json.dumps({
                "error": "stream_generation_failed",
                "message": "Unable to generate a response. Please try again.",
            })
            + "\n\n"
        )

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
