from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(Integer, unique=True, nullable=False, index=True)
    full_name = Column(String(255), unique=True, nullable=False, index=True)  # owner/repo format
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Repository metadata
    primary_language = Column(String(100), nullable=True, index=True)
    topics = Column(ARRAY(String), default=list, nullable=False)
    stars = Column(Integer, default=0, nullable=False)
    forks = Column(Integer, default=0, nullable=False)
    
    # AI-generated content
    ai_summary = Column(Text, nullable=True)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_synced = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Repository(id={self.id}, full_name='{self.full_name}')>"
