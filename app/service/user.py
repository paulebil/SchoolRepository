import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from app.repository.user import UserRepository
from app.repository.user_jwt_token import UserJwtToken
from app.schemas.user import *
from app.models.user import User, UserRole
from app.service.email_service import UserAuthEmailService

from app.service.password_reset import PasswordResetService
from app.repository.password_reset import PasswordResetRepository
from app.repository.school import SchoolRepository
from app.repository.signup_token import SignupTokenRepository
from app.models.signup_token import SignupToken
from app.repository.department import DepartmentRepository

from app.core.security import Security
from app.utils.email_context import USER_VERIFY_ACCOUNT

security = Security()

class UserService:
    def __init__(self, user_repository: UserRepository, user_jwt_token_repository: UserJwtToken,
                 password_reset_repository: PasswordResetRepository, school_repository: SchoolRepository,
                 signup_token_repository: SignupTokenRepository, department_repository: DepartmentRepository):
        self.department_repository = department_repository
        self.signup_token_repository = signup_token_repository
        self.school_repository = school_repository
        self.user_repository = user_repository
        self.user_jwt_token_repository = user_jwt_token_repository
        self.password_reset_service = PasswordResetService(password_reset_repository, user_repository)

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

    async def get_login_tokens(self, data:UserLoginSchema):
        user_to_login = await self.user_repository.get_user_by_email(data.username)
        if not user_to_login:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exits")
        if not security.verify_password(data.password, user_to_login.password_hash):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")
        if not user_to_login.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not activated")
        return await security.generate_token_pair(user_to_login, self.user_jwt_token_repository)

    async def get_user_detail(self, user_id: str):
        user_uuid = UUID(user_id)
        user = await self.user_repository.get_user_by_id(user_uuid)
        return UserResponse.model_validate(user)

    async def get_refresh_token(self, refresh_token: str):
        token_payload = security.get_token_payload(refresh_token)
        if not token_payload:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Request 1")

        refresh_key = token_payload.get('t')
        access_key = token_payload.get('a')
        user_id = security.str_decode(token_payload.get('sub'))
        user_id_uuid = UUID(user_id)

        # Call the tuple-returning repository function
        result = await self.user_jwt_token_repository.get_valid_user_token_with_user(
            user_id=user_id_uuid,
            access_key=access_key,
            refresh_key=refresh_key
        )

        # Unpack the tuple
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Request 2")
        user_token, user = result
        # Update expiration
        user_token.expires_at = datetime.now(timezone.utc)
        await self.user_jwt_token_repository.create_jwt_token(user_token)

        return await security.generate_token_pair(user, self.user_jwt_token_repository)

    async def email_forgot_password_link(self, data: UserForgotPasswordSchema, background_tasks: BackgroundTasks):
        user = await security.load_user(data.email, self.user_repository)
        if not user.verified_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your account is not verified.")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your account has been deactivated.")
        await self.password_reset_service.send_password_reset_email(user, background_tasks)
        return JSONResponse({"message": "A email with password reset link has been sent to you."})

    async def reset_password(self, data: UserRestPasswordSchema):
        user = await security.load_user(data.email, self.user_repository)
        if not user or not user.verified_at or not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
        user_email = str(user.email)
        token_valid = await self.password_reset_service.reset_password(user_email, data.token, data.password)
        if not token_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request window.")
        user.password = security.hash_password(data.password)
        user.updated_at = datetime.now(timezone.utc)
        await self.user_repository.update_user(user)
        return JSONResponse({"message": "Password updated successfully"})


    async def create_lecturer_login_token(self, school_id: UUID, department_id: UUID, current_user: User) -> SignupLinkResponse:
        # check if user exists
        user_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if user_exists.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not user_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")
        # check if user is the creator of the school

        # check if school  exist
        school_exists = await self.school_repository.get_school_by_id(school_id)
        if not school_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="School with this id does not exist")

        # check if department exist and is under the school
        department_exists = await self.department_repository.get_department_by_school_id_and_department_id(school_id, department_id)
        if not department_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="department with this id doesn't exist or belong to this school" )
        # proceed to create the token
        lecturer_signup_token = SignupToken(
            school_id=school_id,
            department_id=department_id,
            role=UserRole.LECTURER,
            generated_by=current_user.id,
            used=False
        )

        lecturer_signup_token.generate_signup_token()

        created_token = await self.signup_token_repository.create_signup_token(lecturer_signup_token)
        link = f"https://localhost:3000/signup?token={created_token.token}"
        return SignupLinkResponse(link=link)