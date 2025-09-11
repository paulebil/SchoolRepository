import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class ResearchStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    revision = "revision"
    rejected = "rejected"
    published = "published"


class ResearchPaperResponse(BaseModel):
    id: uuid.UUID
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    object_name: str
    etag: str

    supervisor_id: Optional[uuid.UUID] = None
    department_id: uuid.UUID
    student_id: uuid.UUID

    status: ResearchStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ResearchPaperListResponse(BaseModel):
    items: List[ResearchPaperResponse]
    total: int
    page: int
    size: int
