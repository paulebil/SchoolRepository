from fastapi import HTTPException, status, BackgroundTasks

from app.repository.user import UserRepository
from app.schemas.user import *
from app.models.user import User, UserRole
from app.service.email_service import UserAuthEmailService

from app.core.security import Security

security = Security()

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_admin_user(self, data: CreateAdminUser, background_tasks: BackgroundTasks) -> UserResponse:
        user_exists = await self.user_repository.get_user_by_email(str(data.email))
        if user_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exists.")
        hashed_password = security.hash_password(data.password_hash)
        data.password_hash = hashed_password
        user_dict = data.model_dump()
        user_to_create = User(**user_dict)
        user_to_create.role = UserRole.ADMIN
        user = await self.user_repository.create_user(user_to_create)
        await UserAuthEmailService.send_account_verification_email(user, background_tasks)
        return UserResponse.model_validate(user)