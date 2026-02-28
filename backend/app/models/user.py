from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_username = Column(String(255), unique=True, nullable=False, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=False)
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # User preferences stored as arrays
    preferred_languages = Column(ARRAY(String), default=list, nullable=False)
    preferred_labels = Column(ARRAY(String), default=list, nullable=False)
    
    # Statistics
    total_contributions = Column(Integer, default=0, nullable=False)
    merged_prs = Column(Integer, default=0, nullable=False)
    
    # Admin role
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    contributions = relationship("Contribution", back_populates="user", cascade="all, delete-orphan")
    claimed_issues = relationship("Issue", back_populates="claimer", foreign_keys="Issue.claimed_by")

    def __repr__(self):
        return f"<User(id={self.id}, github_username='{self.github_username}')>"
