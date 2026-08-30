from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


def utc_now():
    return datetime.now(timezone.utc)


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class SourceItem(BaseModel):
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    relevance_score: float
    category: Optional[str] = None
    department: Optional[str] = None
    snippet: Optional[str] = None


class RetrievalStats(BaseModel):
    chunks_retrieved: int = 0
    chunks_used: int = 0
    processing_time_ms: Optional[float] = None


class MessageBase(BaseModel):
    conversation_id: str
    role: MessageRole
    content: str


class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    question: str = Field(..., min_length=1, max_length=2000)


class MessageInDB(MessageBase):
    id: str = Field(..., alias="_id")
    user_id: str
    sources: Optional[List[SourceItem]] = None
    retrieval_metadata: Optional[RetrievalStats] = None
    created_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(populate_by_name=True)


class MessageResponse(MessageBase):
    id: str
    user_id: str
    sources: Optional[List[SourceItem]] = None
    retrieval_metadata: Optional[RetrievalStats] = None
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)


class ChatResponseData(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    sources: List[SourceItem]
    retrieval: RetrievalStats
