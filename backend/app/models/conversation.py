from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


def utc_now():
    return datetime.now(timezone.utc)


class ConversationBase(BaseModel):
    title: str = Field(default="New Conversation", max_length=150)


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)


class ConversationInDB(ConversationBase):
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(populate_by_name=True)


class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(populate_by_name=True)
