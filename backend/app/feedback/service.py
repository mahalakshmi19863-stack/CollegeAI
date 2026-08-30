import uuid
from datetime import datetime, timezone
from typing import List

from ..auth.service import _memory_users
from ..chat.service import _memory_messages
from ..database.mongodb import db_manager
from ..models.feedback import FeedbackCreate, FeedbackResponse
from ..models.user import UserResponse
from ..utils.errors import MessageNotFoundException

_memory_feedback: List[dict] = []


def utc_now():
    return datetime.now(timezone.utc)


class FeedbackService:
    @staticmethod
    async def _validate_message(message_id: str, user_id: str) -> None:
        if db_manager.is_connected and db_manager.messages is not None:
            message = await db_manager.messages.find_one(
                {"_id": message_id, "user_id": user_id, "role": "ASSISTANT"}
            )
        else:
            message = next(
                (
                    item
                    for item in _memory_messages
                    if item.get("_id") == message_id
                    and item.get("user_id") == user_id
                    and item.get("role") == "ASSISTANT"
                ),
                None,
            )
        if not message:
            raise MessageNotFoundException()

    @classmethod
    async def submit(
        cls, feedback_in: FeedbackCreate, current_user: UserResponse
    ) -> FeedbackResponse:
        await cls._validate_message(feedback_in.message_id, current_user.id)
        feedback_id = str(uuid.uuid4())
        now = utc_now()
        feedback_doc = {
            "_id": feedback_id,
            "message_id": feedback_in.message_id,
            "user_id": current_user.id,
            "rating": feedback_in.rating.value,
            "comment": feedback_in.comment,
            "created_at": now,
        }

        if db_manager.is_connected and db_manager.feedback is not None:
            await db_manager.feedback.insert_one(feedback_doc)
        else:
            _memory_feedback.append(feedback_doc)

        return FeedbackResponse(
            id=feedback_id,
            message_id=feedback_in.message_id,
            user_id=current_user.id,
            rating=feedback_in.rating,
            comment=feedback_in.comment,
            created_at=now,
        )


feedback_service = FeedbackService()