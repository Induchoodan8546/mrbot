from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.conversation import (
    ConversationCreateRequest,
    ConversationDeleteResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)
from app.application.conversation_service import ConversationService
from app.core.dependencies import get_conversation_service
from app.domain.exceptions import ConversationNotFoundError


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    request: ConversationCreateRequest,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    conversation = service.create(
        title=request.title,
        model=request.model,
    )
    return ConversationResponse.model_validate(conversation)


@router.get(
    "",
    response_model=ConversationListResponse,
)
def list_conversations(
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationListResponse:
    conversations = service.list_all()

    return ConversationListResponse(
        conversations=[
            ConversationResponse.model_validate(item)
            for item in conversations
        ],
        total=len(conversations),
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationDetailResponse:
    try:
        conversation, messages = service.get(str(conversation_id))
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "conversation_not_found",
                "message": str(exc),
            },
        ) from exc

    return ConversationDetailResponse(
        **ConversationResponse.model_validate(conversation).model_dump(),
        messages=[
            MessageResponse.model_validate(message)
            for message in messages
        ],
    )


@router.delete(
    "/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
def delete_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationDeleteResponse:
    try:
        service.delete(str(conversation_id))
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "conversation_not_found",
                "message": str(exc),
            },
        ) from exc

    return ConversationDeleteResponse(
        message="Conversation deleted successfully.",
        conversation_id=conversation_id,
    )