from fastapi import APIRouter, status, Depends

from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import UserService
from app.repository.user import UserRepository
from app.schemas.user import *


admin_user_router = APIRouter(
    tags=["User"]
)

def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(user_repository)

@admin_user_router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_admin_user(data: CreateAdminUser, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_admin_user(data)