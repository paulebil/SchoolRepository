import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

class ResearchPaperAuthor(Base):
    __tablename__ = "research_paper_authors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    research_paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_papers.id"), nullable=False
    )
    student_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_reg_no: Mapped[str] = mapped_column(String(50), nullable=False)
    student_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    student_email: Mapped[str] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the research paper using string forward reference
    research_paper: Mapped["ResearchPaper"] = relationship(
        "ResearchPaper", back_populates="paper_authors"
    )

    def __repr__(self) -> str:
        return f"<ResearchPaperAuthor id={self.id} name={self.student_first_name} {self.student_last_name}>"
