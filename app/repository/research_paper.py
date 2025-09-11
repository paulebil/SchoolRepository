from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from uuid import UUID

from app.models.research_paper import ResearchPaper

class ResearchPaperRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_research_paper(self, research_paper: ResearchPaper):
        try:
            self.session.add(research_paper)
            await self.session.commit()
            await self.session.refresh(research_paper)
            return research_paper
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_all_my_research_paper(self, student_id: UUID):
        stmt = select(ResearchPaper).where(ResearchPaper.student_id == student_id)
        result = await self.session.execute(stmt)
        return result.scalars()

    async def get_research_paper(self, research_paper_id: UUID) -> ResearchPaper:
        stmt = select(ResearchPaper).where(ResearchPaper.id == research_paper_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()