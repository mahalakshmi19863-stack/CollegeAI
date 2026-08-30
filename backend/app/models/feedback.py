from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


def utc_now():
    return datetime.now(timezone.utc)


class FeedbackRating(str, Enum):
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class FeedbackCreate(BaseModel):
    message_id: str
    rating: FeedbackRating
    comment: Optional[str] = Field(default=None, max_length=1000)


class FeedbackInDB(FeedbackCreate):
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(populate_by_name=True)


class FeedbackResponse(FeedbackCreate):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)
