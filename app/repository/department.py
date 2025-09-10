from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.department import Department

from uuid import UUID


class DepartmentRepository:
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create_department(self, department: Department):
        try:
            self.session.add(department)
            await self.session.commit()
            await self.session.refresh(department)
            return department
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_departments_by_school_id(self, school_id: UUID):
        stmt = select(Department).where(Department.school_id == school_id)
        result = await self.session.execute(stmt)
        return result.scalars()

