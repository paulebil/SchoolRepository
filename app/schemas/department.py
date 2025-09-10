import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    school_id: uuid.UUID = Field(..., description="UUID of the school this department belongs to")
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, description="Department description")
    office_location: str | None = Field(None, description="Office location of the department")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Computer Science Department",
                "description": "Handles all CS-related programs and research.",
                "office_location": "Block B, Room 101"
            }
        }
    }


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    name: str
    description: str | None = None
    office_location: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "321e6547-e89b-12d3-a456-426614174999",
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Computer Science Department",
                "description": "Handles all CS-related programs and research.",
                "office_location": "Block B, Room 101",
                "created_at": "2025-09-09T08:00:00Z",
                "updated_at": "2025-09-09T10:30:00Z"
            }
        }
    }
