import uuid
from datetime import datetime
from typing import List, Optional
import enum

from sqlalchemy import String, ForeignKey, Enum, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ResearchStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    revision = "revision"
    rejected = "rejected"
    published = "published"

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    object_name: Mapped[str] = mapped_column(String, nullable=False)
    etag: Mapped[str] = mapped_column(String, nullable=False)

    supervisor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[ResearchStatus] = mapped_column(Enum(ResearchStatus), default=ResearchStatus.pending, nullable=False)

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    supervisor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[supervisor_id])
    department: Mapped["Department"] = relationship("Department", backref="research_papers")
    paper_authors: Mapped[List["ResearchPaperAuthor"]] = relationship(
        "ResearchPaperAuthor", back_populates="research_paper", cascade="all, delete-orphan"
    )
    comments: Mapped[List["SupervisorComment"]] = relationship(
        "SupervisorComment", back_populates="research_paper", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ResearchPaper id={self.id} title={self.title} status={self.status}>"
