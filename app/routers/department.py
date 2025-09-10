from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import security
from app.database.database import get_session

from app.repository.user import UserRepository, User
from app.repository.school import SchoolRepository
from app.repository.department import DepartmentRepository
from app.service.department import DepartmentService
from app.schemas.department import *

from uuid import UUID
from typing import List

dept_router = APIRouter(
    prefix="/dept",
    tags=["Dept"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)


def get_department_service(session: AsyncSession = Depends(get_session)) -> DepartmentService:
    user_repository = UserRepository(session)
    school_repository = SchoolRepository(session)
    department_repository = DepartmentRepository(session)
    return DepartmentService(department_repository, school_repository, user_repository)

@dept_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=DepartmentResponse)
async def create_department(data: DepartmentCreate,current_user: User = Depends(security.get_current_user)
                            ,department_service: DepartmentService = Depends(get_department_service) ):
    return await department_service.create_department(data, current_user)

@dept_router.get("/departments", status_code=status.HTTP_200_OK, response_model=List[DepartmentResponse])
async def get_departments(school_id: UUID = Query(..., description="UUID of the school"),
                          department_service: DepartmentService = Depends(get_department_service),
                          current_user: User = Depends(security.get_current_user)):
    return await department_service.get_departments(school_id, current_user)

@dept_router.get("/department", status_code=status.HTTP_200_OK, response_model=DepartmentResponse)
async def get_department(department_id: UUID = Query(..., description="UUID of the department"),
                         department_service: DepartmentService = Depends(get_department_service),
                         current_user: User = Depends(security.get_current_user)):
    return await department_service.get_department(department_id, current_user)