from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    approvals = relationship("Approval", back_populates="post")
    publications = relationship("Publication", back_populates="post")
    sources = relationship("Source", back_populates="post")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
