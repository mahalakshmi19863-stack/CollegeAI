from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


def utc_now():
    return datetime.now(timezone.utc)


class ChunkBase(BaseModel):
    document_id: str
    document_name: str
    document_version: int = 1
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    category: str = "General"
    department: Optional[str] = "General"
    is_active: bool = True


class ChunkCreate(ChunkBase):
    embedding: List[float]


class ChunkInDB(ChunkBase):
    id: str = Field(..., alias="_id")
    embedding: List[float]
    created_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(populate_by_name=True)


class ChunkSearchCandidate(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    document_version: int
    page_number: Optional[int] = None
    category: str
    department: Optional[str] = None
    content: str
    score: float
