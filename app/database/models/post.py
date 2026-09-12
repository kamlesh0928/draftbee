from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.approval import Approval
    from app.database.models.publication import Publication
    from app.database.models.source import Source
    from app.database.models.topic import Topic


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="posts", uselist=False)
    approvals = relationship("Approval", back_populates="post", uselist=True)
    publications = relationship("Publication", back_populates="post", uselist=True)
    sources = relationship("Source", back_populates="post", uselist=True)