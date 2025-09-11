import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from typing import List


class PastPaperResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    course_code: str
    course_name: str
    year: str
    semester: str
    file_url: str
    object_name: str
    etag: str

    lecturer_id: uuid.UUID
    department_id: uuid.UUID

    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)



class PastPaperListResponse(BaseModel):
    items: List[PastPaperResponse]
    total: int
    page: int
    size: int
