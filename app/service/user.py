import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from app.repository.user import UserRepository
from app.schemas.user import *
from app.models.user import User, UserRole
from app.service.email_service import UserAuthEmailService

from app.core.security import Security
from app.utils.email_context import USER_VERIFY_ACCOUNT

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

    async def activate_user_account(self, data: ActivateUserSchema, background_tasks: BackgroundTasks):
        user_to_activate = await self.user_repository.get_user_by_email(data.email)
        if not user_to_activate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exits. Link is either corrupt or not valid")
        user_token = user_to_activate.get_context_string(context=USER_VERIFY_ACCOUNT)
        try:
            token_valid = security.verify_password(user_token, data.token)
        except Exception as verify_exec:
            logging.exception(verify_exec)
            token_valid = False

        if not token_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This link is either expired or not valid.")

        user_to_activate.is_active = True
        user_to_activate.verified_at = datetime.now(timezone.utc)
        user_to_activate.updated_at = datetime.now(timezone.utc)

        updated_user = await self.user_repository.update_user(user_to_activate)
        await UserAuthEmailService.send_account_activation_confirmation_email(updated_user, background_tasks)
        return JSONResponse({"message": "Account is activated successfully. Check your email for confirmation."})