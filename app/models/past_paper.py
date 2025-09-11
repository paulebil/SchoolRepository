import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class PastPaper(Base):
    __tablename__ = "past_papers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g., "Final Exam"
    course_code: Mapped[str] = mapped_column(String, nullable=False)
    course_name: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "Semester 1"

    object_name: Mapped[str] = mapped_column(String, nullable=False)
    etag: Mapped[str] = mapped_column(String, nullable=False)

    lecturer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    lecturer: Mapped["User"] = relationship("User", backref="past_papers")
    department: Mapped["Department"] = relationship("Department", backref="past_papers")

    def __repr__(self):
        return f"<PastPaper id={self.id} course={self.course_code} year={self.year} semester={self.semester}>"
