from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import UserService
from app.repository.user import UserRepository
from app.repository.user_jwt_token import UserJwtToken
from app.schemas.user import *


admin_user_router = APIRouter(
    prefix="/users",
    tags=["User"]
)

guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    user_jwt_repository = UserJwtToken(session)
    return UserService(user_repository, user_jwt_repository)

@admin_user_router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_admin_user(data: CreateAdminUser, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_admin_user(data, background_tasks)

@admin_user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(data: ActivateUserSchema, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.activate_user_account(data, background_tasks)

@admin_user_router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def admin_user_login(data: UserLoginSchema , user_service: UserService = Depends(get_user_service)):
    user =  await user_service.get_login_tokens(data)
    return user


