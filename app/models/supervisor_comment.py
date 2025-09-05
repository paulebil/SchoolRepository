import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Enum, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.research_paper import ResearchStatus

class SupervisorComment(Base):
    __tablename__ = "supervisor_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    research_paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_papers.id"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[ResearchStatus] = mapped_column(Enum(ResearchStatus), nullable=False)

    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    research_paper: Mapped["ResearchPaper"] = relationship(
        "ResearchPaper", back_populates="reviews"
    )
    reviewer: Mapped["User"] = relationship("User", backref="supervisor_comments")

    def __repr__(self):
        return f"<SupervisorComment id={self.id} paper_id={self.research_paper_id} reviewer_id={self.reviewer_id} decision={self.decision}>"
