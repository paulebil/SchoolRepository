from fastapi import HTTPException, status
from uuid import UUID

from app.repository.school import SchoolRepository, School
from app.schemas.school import SchoolCreate, SchoolResponse
from app.repository.user import UserRepository
from app.models.user import UserRole

class SchoolService:
    def __init__(self,school_repository: SchoolRepository, user_repository: UserRepository ):
        self.school_repository = school_repository
        self.user_repository = user_repository

    async def create_school(self, data: SchoolCreate) -> SchoolResponse:
        # check if user exists
        user_id_uuid = UUID(data.admin_id)
        user_exists = await self.user_repository.get_user_by_id(user_id_uuid)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if user_exists.role != UserRole.ADMIN.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not user_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not active. Cannot perform this action")
        # check if school already exist
        school_exists = await self.school_repository.get_school_by_name(data.name)
        if school_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="School with this name already exist")
        # proceed to create school
        school_dict = data.model_dump()
        school_to_create = School(**school_dict)
        created_school = await self.school_repository.create_school(school_to_create)
        return SchoolResponse.model_validate(created_school)