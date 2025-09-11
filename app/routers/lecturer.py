from fastapi import APIRouter, status, Depends, Query, Form, UploadFile, File

from uuid import UUID
from typing import List

from app.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.lecturer import LecturerService, security
from app.repository.user import UserRepository, User
from app.schemas.user import *
from app.repository.signup_token import SignupTokenRepository
from app.repository.reading_material import ReadingMaterialRepository
from app.schemas.reading_material import ReadingMaterialResponse
from app.schemas.past_paper import PastPaperResponse
from app.repository.past_paper import PastPaperRepository


lect_router = APIRouter(
    prefix="/lect",
    tags=["Auth Lect"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)

def get_lecturer_service(session: AsyncSession = Depends(get_session)) -> LecturerService:
    user_repository = UserRepository(session)
    signup_token_repository = SignupTokenRepository(session)
    reading_material_repository = ReadingMaterialRepository(session)
    past_paper_repository = PastPaperRepository(session)
    return LecturerService(user_repository, signup_token_repository, reading_material_repository, past_paper_repository)


@lect_router.get("/create-signup-link", status_code=status.HTTP_200_OK, response_model=SignupLinkResponse)
async def generate_student_signup_link(current_user: User = Depends(security.get_current_user),
                                        lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.create_student_login_token(current_user)

# @lect_router.get("/generate-link", status_code=status.HTTP_200_OK, response_model=SignupLinkResponse)
# async def create_student_signup_link(school_id: UUID = Query(..., description="UUID of school"),
#                                         department_id: UUID = Query(..., description="UUID of department"),
#         current_user: User = Depends(security.get_current_user), lecturer_service: LecturerService = Depends(get_lecturer_service)):
#     return await lecturer_service.create_student_login_token(school_id, department_id, current_user)


@lect_router.post("/reading-material", status_code=status.HTTP_201_CREATED)
async def upload_reading_material(title: str = Form(), description: str = Form(), reading_material: UploadFile = File(...),
                                  current_user: User = Depends(security.get_current_user),
                                  lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.upload_reading_material(title, description, reading_material, current_user)

@lect_router.get("/reading-material", status_code=status.HTTP_200_OK, response_model=List[ReadingMaterialResponse])
async def get_all_my_reading_materials(current_user: User = Depends(security.get_current_user),
                                        lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.get_all_my_reading_materials(current_user)

@lect_router.get("/reading-material-detail", status_code=status.HTTP_200_OK, response_model=ReadingMaterialResponse)
async def get_reading_material_detail(reading_material_id: UUID = Query(..., description="UUID of the reading material"),
                                      current_user: User = Depends(security.get_current_user),
                                        lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.get_reading_material_detail(reading_material_id, current_user)


@lect_router.post("/past-paper", status_code=status.HTTP_201_CREATED)
async def upload_past_paper(title: str = Form(), course_code: str = Form(), course_name: str = Form(),
                                  year: str = Form(), semester: str = Form(), past_paper: UploadFile = File(...),
                                  current_user: User = Depends(security.get_current_user),
                                  lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.upload_past_paper(title, course_code, course_name, year, semester, past_paper, current_user)

@lect_router.get("/past-paper", status_code=status.HTTP_200_OK, response_model=List[PastPaperResponse])
async def get_all_my_past_papers(current_user: User = Depends(security.get_current_user),
                                        lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.get_all_my_past_paper(current_user)

@lect_router.get("/past-paper-detail", status_code=status.HTTP_200_OK, response_model=PastPaperResponse)
async def get_past_paper_detail(past_paper_id: UUID = Query(..., description="UUID of the past_paper"),
                                      current_user: User = Depends(security.get_current_user),
                                        lecturer_service: LecturerService = Depends(get_lecturer_service)):
    return await lecturer_service.get_past_paper_detail(past_paper_id, current_user)
