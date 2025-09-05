import uuid
from datetime import datetime, timezone

from app.database.database import Base

from sqlalchemy import String,  DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ResearchPaperAuthor(Base):
    __tablename__ = "research_paper_authors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    research_paper_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_papers.id"), nullable=False)
    student_first_name: Mapped[str] = mapped_column(String, nullable=False)
    student_last_name: Mapped[str] = mapped_column(String, nullable=False)
    student_reg_no: Mapped[str] = mapped_column(String, nullable=False)
    student_phone: Mapped[str] = mapped_column(String, nullable=False)
    student_email: Mapped[str] = mapped_column(String, nullable=False)
