from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

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

    async def get_reading_material(self):
        stmt = select(ReadingMaterial)
        pass