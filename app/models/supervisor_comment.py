import uuid
from datetime import datetime, timezone

from app.database.database import Base
from app.models.research_paper import ResearchStatus

from sqlalchemy import String,  DateTime, Enum, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SupervisorComment(Base):
    __tablename__ = "supervisor_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    research_paper_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_papers.id"), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[ResearchStatus] = mapped_column(Enum(ResearchStatus), nullable=False)

    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
