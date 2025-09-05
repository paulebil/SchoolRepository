import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class ReadingMaterial(Base):
    __tablename__ = "reading_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[str] = mapped_column(String, nullable=False)

    object_name: Mapped[str] = mapped_column(String, nullable=False)
    etag: Mapped[str] = mapped_column(String, nullable=False)

    lecturer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    lecturer: Mapped["User"] = relationship("User", backref="reading_materials")
    department: Mapped["Department"] = relationship("Department", backref="reading_materials")

    def __repr__(self):
        return f"<ReadingMaterial id={self.id} title={self.title} department_id={self.department_id}>"
