from fastapi import HTTPException, status, UploadFile
from uuid import UUID, uuid4
from typing import List

from starlette.responses import JSONResponse

from app.repository.user import UserRepository
from app.models.user import User
from app.repository.signup_token import SignupTokenRepository, SignupToken
from app.schemas.user import *
from app.repository.reading_material import ReadingMaterialRepository
from app.models.reading_material import ReadingMaterial
from app.repository.past_paper import PastPaperRepository
from app.models.past_paper import PastPaper
from app.schemas.past_paper import PastPaperResponse
from app.schemas.reading_material import *
from app.repository.object_store import upload_file_to_minio, generate_presigned_url

from app.core.security import Security
from app.core.settings import get_settings

security = Security()
settings = get_settings()

class LecturerService:
    def __init__(self, user_repository: UserRepository, signup_token_repository: SignupTokenRepository,
                 reading_material_repository: ReadingMaterialRepository, past_paper_repository: PastPaperRepository):
        self.user_repository = user_repository
        self.signup_token_repository = signup_token_repository
        self.reading_material_repository = reading_material_repository
        self.past_paper_repository = past_paper_repository

    async def create_student_login_token(self, current_user: User) -> SignupLinkResponse:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is an admin
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        # proceed to create the token
        lecturer_signup_token = SignupToken(
            school_id=lecturer_exists.school_id,
            department_id=lecturer_exists.department_id,
            role=UserRole.STUDENT,
            generated_by=current_user.id,
            used=False
        )
        lecturer_signup_token.generate_signup_token()

        created_token = await self.signup_token_repository.create_signup_token(lecturer_signup_token)

        link = f"https://localhost:3000/signup?token={created_token.token}"
        return SignupLinkResponse(link=link)

    async def upload_reading_material(self, title: str, description: str, reading_material: UploadFile, current_user: User):
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        if not reading_material:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

        bucket_name = settings.MINIO_READING_MATERIAL_BUCKET_NAME

        reading_material_object_name = f"{uuid4().hex}_{reading_material.filename}"
        # proceed to upload the reading material
        meta_data = await upload_file_to_minio(bucket_name, reading_material_object_name, reading_material)
        reading_material_to_create = ReadingMaterial(
            title=title,
            description=description,
            object_name=meta_data["object_name"],
            etag=meta_data["etag"],
            lecturer_id=current_user.id,
            department_id=lecturer_exists.department_id
        )
        await self.reading_material_repository.create_reading_material(reading_material_to_create)

        return JSONResponse(content= {"message": "Upload successful"},status_code=status.HTTP_200_OK)

    async def get_all_my_reading_materials(self, current_user: User) -> List[ReadingMaterialResponse]:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        content = []
        reading_materials = await self.reading_material_repository.get_all_my_reading_material(current_user.id)
        bucket_name = settings.MINIO_READING_MATERIAL_BUCKET_NAME

        for reading_material in reading_materials:
            # get presigned urls
            file_url = await generate_presigned_url(bucket_name, reading_material.object_name)
            reading_material.file_url = file_url
            reading_material_response = ReadingMaterialResponse.model_validate(reading_material)
            content.append(reading_material_response)

        return content

    async def get_reading_material_detail(self, reading_material_id: UUID, current_user: User) -> ReadingMaterialResponse:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        bucket_name = settings.MINIO_READING_MATERIAL_BUCKET_NAME
        reading_material = await self.reading_material_repository.get_reading_material(reading_material_id)
        file_url = await generate_presigned_url(bucket_name, reading_material.object_name)
        reading_material.file_url = file_url
        return ReadingMaterialResponse.model_validate(reading_material)
    
    async def upload_past_paper(self, title: str, course_code: str, course_name: str, year: str, semester: str, 
                                past_paper: UploadFile, current_user: User):
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        if not past_paper:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

        bucket_name = settings.MINIO_PAST_PAPER_BUCKET_NAME

        past_paper_object_name = f"{uuid4().hex}_{past_paper.filename}"
        # proceed to upload the reading material
        meta_data = await upload_file_to_minio(bucket_name, past_paper_object_name, past_paper)
        past_paper_to_create = PastPaper(
            title=title,
            course_code=course_code,
            course_name=course_name,
            year=year,
            semester=semester,
            department_id=lecturer_exists.department_id,
            lecturer_id=lecturer_exists.id,
            etag=meta_data["etag"],
            object_name=meta_data["object_name"]
        )
    
        await self.past_paper_repository.create_past_paper(past_paper_to_create)

        return JSONResponse(content= {"message": "Upload successful"},status_code=status.HTTP_200_OK)

    async def get_all_my_past_paper(self, current_user: User) -> List[PastPaperResponse]:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        content = []
        past_papers = await self.past_paper_repository.get_all_my_past_paper(lecturer_exists.id)
        bucket_name = settings.MINIO_PAST_PAPER_BUCKET_NAME

        for past_paper in past_papers:
            # get presigned urls
            file_url = await generate_presigned_url(bucket_name, past_paper.object_name)
            past_paper.file_url = file_url
            past_paper_response = PastPaperResponse.model_validate(past_paper)
            content.append(past_paper_response)

        return content

    async def get_past_paper_detail(self, past_paper_id: UUID, current_user: User) -> PastPaperResponse:
        # check if user exists
        lecturer_exists = await self.user_repository.get_user_by_id(current_user.id)
        if not lecturer_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exists.")
        # check if user is a lecturer
        if lecturer_exists.role != UserRole.LECTURER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin to create a school")
        # check if user is active
        if not lecturer_exists.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is not active. Cannot perform this action")

        bucket_name = settings.MINIO_PAST_PAPER_BUCKET_NAME
        past_paper_response = await self.past_paper_repository.get_past_paper(past_paper_id)
        file_url = await generate_presigned_url(bucket_name, past_paper_response.object_name)
        past_paper_response.file_url = file_url
        return PastPaperResponse.model_validate(past_paper_response)

