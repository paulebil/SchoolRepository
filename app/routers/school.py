from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.user import security
from app.database.database import get_session

from app.service.school import SchoolService
from app.repository.school import SchoolRepository
from app.repository.user import UserRepository
from app.schemas.school import *


sch_router = APIRouter(
    prefix="/sch",
    tags=["SCH"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)


def get_school_service(session: AsyncSession = Depends(get_session)) -> SchoolService:
    user_repository = UserRepository(session)
    school_repository = SchoolRepository(session)
    return SchoolService(school_repository, user_repository)

@sch_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_school(data: SchoolCreate, school_service: SchoolService = Depends(get_school_service)):
    return await school_service.create_school(data)