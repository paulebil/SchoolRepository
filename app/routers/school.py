from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import security
from app.database.database import get_session

from app.service.school import SchoolService
from app.repository.school import SchoolRepository
from app.repository.user import UserRepository, User
from app.schemas.school import *

from uuid import UUID

sch_router = APIRouter(
    prefix="/sch",
    tags=["Sch"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)


def get_school_service(session: AsyncSession = Depends(get_session)) -> SchoolService:
    user_repository = UserRepository(session)
    school_repository = SchoolRepository(session)
    return SchoolService(school_repository, user_repository)

@sch_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=SchoolResponse)
async def create_school(data: SchoolCreate, school_service: SchoolService = Depends(get_school_service)):
    return await school_service.create_school(data)

@sch_router.get("/school", status_code=status.HTTP_200_OK, response_model=SchoolResponse)
async def get_school(  school_id: UUID = Query(..., description="UUID of the school"), current_user: User = Depends(security.get_current_user),
                     school_service: SchoolService = Depends(get_school_service)):
    return await school_service.get_my_school(school_id, current_user)