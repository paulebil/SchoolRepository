from fastapi import HTTPException, status

from app.repository.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

from app.core.security import Security

security = Security()

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, data: UserCreate) -> UserResponse:
        user_exists = await self.user_repository.get_user_by_email(str(data.email))
        if user_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exists.")
        hashed_password = security.hash_password(data.password)
        data.password = hashed_password
        user_dict = data.model_dump()
        user_to_create = User(**user_dict)
        user = await self.user_repository.create_user(user_to_create)
        return UserResponse.model_validate(user)