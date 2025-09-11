from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from uuid import UUID

from app.models.past_paper import PastPaper

class PastPaperRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_past_paper(self, past_paper: PastPaper):
        try:
            self.session.add(past_paper)
            await self.session.commit()
            await self.session.refresh(past_paper)
            return past_paper
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_all_my_past_paper(self, lecturer_id: UUID):
        stmt = select(PastPaper).where(PastPaper.lecturer_id == lecturer_id)
        result = await self.session.execute(stmt)
        return result.scalars()

    async def get_past_paper(self, past_paper_id: UUID) -> PastPaper:
        stmt = select(PastPaper).where(PastPaper.id == past_paper_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()