from typing import List
from fastapi import APIRouter, Depends, status
from ..auth.dependencies import get_current_user
from ..models.conversation import ConversationResponse, ConversationUpdate
from ..models.message import ChatResponseData, MessageCreate
from ..models.user import UserResponse
from ..utils.responses import ApiResponse, success_response
from .service import chat_service

router = APIRouter(tags=["Chat & Conversations"])


@router.post("/chat", response_model=ApiResponse[ChatResponseData])
async def send_chat_message(
    message_in: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Ask a question to CollegeAI and receive a grounded RAG response."""
    response_data = await chat_service.process_chat(
        user_id=current_user.id,
        message_in=message_in,
    )
    return success_response(response_data)


@router.get("/conversations", response_model=ApiResponse[List[ConversationResponse]])
async def list_conversations(
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve all conversations for the authenticated student."""
    conversations = await chat_service.list_conversations(user_id=current_user.id)
    return success_response(conversations)


@router.get("/conversations/{conversation_id}", response_model=ApiResponse[dict])
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Get full conversation with its message history."""
    data = await chat_service.get_conversation_with_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    return success_response(data)


@router.patch(
    "/conversations/{conversation_id}", response_model=ApiResponse[ConversationResponse]
)
async def update_conversation(
    conversation_id: str,
    updates: ConversationUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Update conversation title."""
    conv = await chat_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        updates=updates,
    )
    return success_response(conv)


@router.delete("/conversations/{conversation_id}", response_model=ApiResponse[dict])
async def delete_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Delete a conversation and all its messages."""
    await chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    return success_response({"message": "Conversation successfully deleted."})
