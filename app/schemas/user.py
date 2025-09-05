import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole  # adjust import to your project


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    role: UserRole
    school_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    supervisor_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole
    is_active: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    school_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    supervisor_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}
