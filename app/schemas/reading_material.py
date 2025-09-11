import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from typing import List



class ReadingMaterialResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    file_url: str
    object_name: str
    etag: str

    lecturer_id: uuid.UUID
    department_id: uuid.UUID

    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReadingMaterialListResponse(BaseModel):
    items: List[ReadingMaterialResponse]
    total: int
    page: int
    size: int
