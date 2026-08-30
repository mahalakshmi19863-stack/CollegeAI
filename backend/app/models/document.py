from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


def utc_now():
    return datetime.now(timezone.utc)


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class DocumentCategory(str, Enum):
    ADMISSIONS = "Admissions"
    ACADEMICS = "Academics"
    EXAMINATIONS = "Examinations"
    FEES = "Fees"
    HOSTEL = "Hostel"
    LIBRARY = "Library"
    SCHOLARSHIPS = "Scholarships"
    PLACEMENTS = "Placements"
    CLUBS = "Clubs"
    EVENTS = "Events"
    POLICIES = "Policies"
    GENERAL = "General"


class DocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="General")
    department: Optional[str] = Field(default="General")
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DocumentInDB(DocumentBase):
    id: str = Field(..., alias="_id")
    original_filename: str
    file_type: str
    file_size: int
    version: int = 1
    status: DocumentStatus = DocumentStatus.UPLOADED
    storage_reference: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_active: bool = True
    processing_error: Optional[str] = None
    chunk_count: int = 0
    total_pages: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)


class DocumentResponse(DocumentBase):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    storage_reference: str
    version: int
    status: DocumentStatus
    uploaded_by: str
    uploaded_at: datetime
    updated_at: datetime
    is_active: bool
    processing_error: Optional[str] = None
    chunk_count: int = 0
    total_pages: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)
