from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from uuid import UUID

from app.models.reading_material import ReadingMaterial

class ReadingMaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reading_material(self, reading_material: ReadingMaterial):
        try:
            self.session.add(reading_material)
            await self.session.commit()
            await self.session.refresh(reading_material)
            return reading_material
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_all_my_reading_material(self, lecturer_id: UUID):
        stmt = select(ReadingMaterial).where(ReadingMaterial.lecturer_id == lecturer_id)
        result = await self.session.execute(stmt)
        return result.scalars()