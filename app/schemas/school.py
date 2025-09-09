import uuid
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    logo_url: HttpUrl | None = None
    location: str | None = None
    website: HttpUrl | None = None
    email: EmailStr | None = None
    address: str | None = None
    admin_id: uuid.UUID | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Greenwood International School",
                "logo_url": "https://example.com/logo.png",
                "location": "Kampala",
                "website": "https://greenwood.ac.ug",
                "email": "info@greenwood.ac.ug",
                "address": "Plot 12, Ntinda Road, Kampala",
                "admin_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    }


class SchoolResponse(BaseModel):
    id: uuid.UUID
    name: str
    logo_url: HttpUrl | None = None
    location: str | None = None
    website: HttpUrl | None = None
    email: EmailStr | None = None
    address: str | None = None
    admin_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Greenwood International School",
                "logo_url": "https://example.com/logo.png",
                "location": "Kampala",
                "website": "https://greenwood.ac.ug",
                "email": "info@greenwood.ac.ug",
                "address": "Plot 12, Ntinda Road, Kampala",
                "admin_id": "987e6543-e21b-65d3-a456-426614174999",
                "created_at": "2025-09-09T08:00:00Z",
                "updated_at": "2025-09-09T10:30:00Z"
            }
        }
    }
