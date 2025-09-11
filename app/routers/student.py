from fastapi import APIRouter, status, Depends, Query, Form, UploadFile, File

from uuid import UUID
from typing import List

from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.student import StudentService
from app.repository.user import UserRepository, User
from app.repository.research_paper import ResearchPaperRepository
from app.schemas.user import *
from app.core.security import Security

security = Security()

stud_router = APIRouter(
    prefix="/stud",
    tags=["Auth Stud"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)

def get_student_service(session: AsyncSession = Depends(get_session)) -> StudentService:
    user_repository = UserRepository(session)
    research_paper_repository = ResearchPaperRepository(session)
    return StudentService(user_repository, research_paper_repository)

@stud_router.post("/past-paper", status_code=status.HTTP_201_CREATED)
async def upload_past_paper(title: str = Form(), keywords: str = Form(), abstract: str = Form(),
                            research_paper: UploadFile = File(...),
                            current_user: User = Depends(security.get_current_user),
                            student_service: StudentService = Depends(get_student_service)):
    return await student_service.upload_research_paper(title, abstract, keywords, research_paper, current_user)
