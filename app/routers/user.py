from fastapi import APIRouter, status, Depends, BackgroundTasks, Header, Query
from fastapi.security import OAuth2PasswordRequestForm

from uuid import UUID

from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import UserService, security
from app.repository.user import UserRepository, User
from app.repository.user_jwt_token import UserJwtToken
from app.repository.password_reset import PasswordResetRepository
from app.schemas.user import *

from app.repository.school import SchoolRepository
from app.repository.signup_token import SignupTokenRepository
from app.repository.department import DepartmentRepository


user_router = APIRouter(
    prefix="/users",
    tags=["Admin User"]
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth Admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)

def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    user_jwt_repository = UserJwtToken(session)
    password_reset_repository = PasswordResetRepository(session)
    school_repository = SchoolRepository(session)
    signup_token_repository = SignupTokenRepository(session)
    department_repository = DepartmentRepository(session)
    return UserService(user_repository, user_jwt_repository, password_reset_repository, school_repository, signup_token_repository, department_repository)

@user_router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_admin_user(data: CreateAdminUser, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_admin_user(data, background_tasks)

@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(data: ActivateUserSchema, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.activate_user_account(data, background_tasks)

@user_router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),user_service: UserService = Depends(get_user_service)):
    # Convert OAuth2 form data to your schema
    data = UserLoginSchema(username=form_data.username, password=form_data.password)
    return await user_service.get_login_tokens(data)

@user_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def refresh_token(token = Header(), user_service: UserService = Depends(get_user_service)):
    return await user_service.get_refresh_token(token)

@user_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: UserForgotPasswordSchema, background_tasks: BackgroundTasks,user_service: UserService = Depends(get_user_service)):
    return await user_service.email_forgot_password_link(data, background_tasks)

@user_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: UserRestPasswordSchema, user_service: UserService = Depends(get_user_service)):
    return await user_service.reset_password(data)

@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_signup_user(data: SignupCreate, background_tasks: BackgroundTasks,
                             user_service: UserService = Depends(get_user_service)):
    return await user_service.user_signup(data, background_tasks)

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_detail(current_user: User = Depends(security.get_current_user) ):
    return current_user

@auth_router.get("/signup-link", status_code=status.HTTP_200_OK, response_model=SignupLinkResponse)
async def generate_lecturer_signup_link(school_id: UUID = Query(..., description="UUID of school"),
                                        department_id: UUID = Query(..., description="UUID of department"),
                                        current_user: User = Depends(security.get_current_user),
                                        user_service: UserService = Depends(get_user_service)):
    return await user_service.create_lecturer_login_token(school_id, department_id, current_user)