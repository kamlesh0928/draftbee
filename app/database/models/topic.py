from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

STATUS_PENDING = "pending"
STATUS_USED = "used"
STATUS_REJECTED = "rejected"


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'used', 'rejected')",
            name="ck_topics_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="topic", uselist=True)  # type: ignore
    