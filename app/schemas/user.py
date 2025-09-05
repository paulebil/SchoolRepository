import uuid
from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, constr

from app.models.user import UserRole  # adjust import to your project


# Regex explanation:
# - ^07\d{8}$ → local format, e.g., 0701234567
# - ^\+2567\d{8}$ → international format, e.g., +256701234567

UgandanPhoneNumber = Annotated[
    str,
    constr(pattern=r"^(07\d{8}|\+2567\d{8})$")
]

class CreateAdminUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[UgandanPhoneNumber] = None
    password_hash: str

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[UgandanPhoneNumber] = None
    password_hash: str
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

class ActivateUserSchema(BaseModel):
    email: str
    token: str

