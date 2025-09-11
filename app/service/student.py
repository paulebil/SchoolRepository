from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from  app.repository.user import UserRepository
from app.models.user import UserRole , User
from app.repository.object_store import upload_file_to_minio
from app.core.settings import get_settings
from app.repository.research_paper import ResearchPaperRepository, ResearchPaper
from app.schemas.research_paper import ResearchStatus, ResearchPaperResponse

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
