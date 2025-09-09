from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from uuid import UUID

from app.models.school import School

class SchoolRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_school(self, school: School):
        try:
            self.session.add(school)
            await self.session.commit()
            await self.session.refresh(school)
            return school
        except IntegrityError:
            await self.session.rollback()
            raise

    async def update_school(self, school: School):
        try:
            await self.session.merge(school)
            await self.session.commit()
            await self.session.refresh(school)
        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete_school(self, school_id: UUID ):
        stmt = select(School).where(School.id == school_id)
        result = await self.session.execute(stmt)
        school = result.scalar_one_or_none()
        await self.session.delete(school)
        await self.session.commit()

    async def get_school_by_id(self, school_id: UUID):
        stmt = select(School).where(School.id == school_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_school_by_name(self, school_name: str):
        stmt = select(School).where(School.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()