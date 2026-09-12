from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rank = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=STATUS_PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="topic", uselist=True)  # type: ignore