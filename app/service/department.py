from fastapi import HTTPException, status

from app.repository.department import DepartmentRepository, Department
from app.schemas.department import *
from app.models.user import User, UserRole
from app.repository.school import SchoolRepository
from app.repository.user import UserRepository

from uuid import UUID
from typing import List

class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository, school_repository: SchoolRepository,
                 user_repository: UserRepository):
        self.department_repository = department_repository
        self.school_repository = school_repository
        self.user_repository = user_repository

    async def create_department(self, data: DepartmentCreate, current_user: User) -> DepartmentResponse:
        # check if user exists
        user_exists = await self.user_repository.get_user_by_id(user_id=current_user.id)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if user_exists.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not user_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")
        school_exists = await self.school_repository.get_school_by_id(data.school_id)
        if not school_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School with this id does not exists.")
        department_to_create_dict = data.model_dump(mode="json")
        if department_to_create_dict.get("school_id"):
            department_to_create_dict["school_id"] = UUID(department_to_create_dict["school_id"])
        department_to_create = Department(**department_to_create_dict)
        created_department = await self.department_repository.create_department(department_to_create)
        return DepartmentResponse.model_validate(created_department)

    async def get_departments(self, school_id: UUID, current_user: User) -> List[DepartmentResponse]:
        # check if user exists
        user_exists = await self.user_repository.get_user_by_id(user_id=current_user.id)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if user_exists.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not user_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")
        departments = await self.department_repository.get_departments_by_school_id(school_id)
        # if not departments:
        #     return []
        return [DepartmentResponse.model_validate(department) for department in departments]

    async def get_department(self, department_id: UUID, current_user: User) -> DepartmentResponse:
        # check if user exists
        user_exists = await self.user_repository.get_user_by_id(user_id=current_user.id)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if user_exists.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not user_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")
        department = await self.department_repository.get_departments_by_department_id(department_id)
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department with this id does not exits")
        return DepartmentResponse.model_validate(department)
