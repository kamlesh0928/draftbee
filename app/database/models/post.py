from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="posts", uselist=False)  # type: ignore
    approvals = relationship("Approval", back_populates="post", uselist=True)  # type: ignore
    publications = relationship("Publication", back_populates="post", uselist=True)  # type: ignore
    sources = relationship("Source", back_populates="post", uselist=True)  # type: ignore
    