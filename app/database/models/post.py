from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="posts")
    approvals = relationship("Approval", back_populates="post")
    publications = relationship("Publication", back_populates="post")
    sources = relationship("Source", back_populates="post")
