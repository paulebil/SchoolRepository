from fastapi import HTTPException, status
from uuid import UUID

from app.repository.user import UserRepository
from app.models.user import User
from app.repository.signup_token import SignupTokenRepository, SignupToken
from app.schemas.user import *

from app.core.security import Security

security = Security()

class LecturerService:
    def __init__(self, user_repository: UserRepository, signup_token_repository: SignupTokenRepository):
        self.user_repository = user_repository
        self.signup_token_repository = signup_token_repository

    async def create_student_login_token(self, current_user: User) -> SignupLinkResponse:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        # proceed to create the token
        lecturer_signup_token = SignupToken(
            school_id=lecturer_exists.school_id,
            department_id=lecturer_exists.department_id,
            role=UserRole.STUDENT,
            generated_by=current_user.id,
            used=False
        )
        lecturer_signup_token.generate_signup_token()

        created_token = await self.signup_token_repository.create_signup_token(lecturer_signup_token)

        link = f"https://localhost:3000/signup?token={created_token.token}"
        return SignupLinkResponse(link=link)

    async def upload_reading_material(self, current_user: User):
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        # proceed to upload the reading material
        pass
