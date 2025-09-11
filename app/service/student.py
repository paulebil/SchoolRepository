from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from  app.repository.user import UserRepository
from app.models.user import UserRole , User
from app.repository.object_store import upload_file_to_minio, generate_presigned_url
from app.core.settings import get_settings
from app.repository.research_paper import ResearchPaperRepository, ResearchPaper
from app.schemas.research_paper import ResearchStatus, ResearchPaperResponse

from typing import List

from uuid import UUID, uuid4
settings = get_settings()

class StudentService:
    def __init__(self, user_repository: UserRepository, research_paper_repository: ResearchPaperRepository):
        self.user_repository = user_repository
        self.research_paper_repository = research_paper_repository

    async def upload_research_paper(self, title: str, abstract: str, keywords: str,
                                    research_paper: UploadFile, current_user: User):
        # check if user exists
        student_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not student_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if student_exists.role != UserRole.STUDENT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a student to create a research paper")
        # check if user is active
        if not student_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        if not research_paper:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

        bucket_name = settings.MINIO_RESEARCH_PAPER_BUCKET_NAME

        research_paper_object_name = f"{uuid4().hex}_{research_paper.filename}"
        # proceed to upload the reading material
        meta_data = await upload_file_to_minio(bucket_name, research_paper_object_name, research_paper)
        research_paper_to_create = ResearchPaper(
            title=title,
            abstract=abstract,
            keywords=keywords,
            status=ResearchStatus.pending,
            student_id=student_exists.id,
            department_id=student_exists.department_id,
            supervisor_id=student_exists.supervisor_id,
            etag=meta_data["etag"],
            object_name=meta_data["object_name"]
        )

        await self.research_paper_repository.create_research_paper(research_paper_to_create)

        return JSONResponse(content= {"message": "Upload successful"},status_code=status.HTTP_200_OK)

    async def get_all_my_research_paper(self, current_user: User) -> List[ResearchPaperResponse]:
        # check if user exists
        student_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not student_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a student
        if student_exists.role != UserRole.STUDENT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a student. Action not allowed")
        # check if user is active
        if not student_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        content = []
        research_papers = await self.research_paper_repository.get_all_my_research_paper(student_exists.id)
        bucket_name = settings.MINIO_RESEARCH_PAPER_BUCKET_NAME

        for research_paper in research_papers:
            # get presigned urls
            file_url = await generate_presigned_url(bucket_name, research_paper.object_name)
            research_paper.file_url = file_url
            research_paper_response = ResearchPaperResponse.model_validate(research_paper)
            content.append(research_paper_response)

        return content

    async def get_research_paper_detail(self, research_paper_id: UUID, current_user: User) -> ResearchPaperResponse:
        # check if user exists
        student_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not student_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if student_exists.role != UserRole.STUDENT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a Student. Action not allowed.")
        # check if user is active
        if not student_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        bucket_name = settings.MINIO_RESEARCH_PAPER_BUCKET_NAME
        research_paper_response = await self.research_paper_repository.get_research_paper(research_paper_id)
        file_url = await generate_presigned_url(bucket_name, research_paper_response.object_name)
        research_paper_response.file_url = file_url
        return ResearchPaperResponse.model_validate(research_paper_response)


