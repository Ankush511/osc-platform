from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class IssueStatus(str, enum.Enum):
    AVAILABLE = "available"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    CLOSED = "closed"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    github_issue_id = Column(Integer, nullable=False, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Issue details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    labels = Column(ARRAY(String), default=list, nullable=False)
    programming_language = Column(String(100), nullable=True, index=True)
    difficulty_level = Column(String(50), nullable=True, index=True)
    
    # AI-generated content
    ai_explanation = Column(Text, nullable=True)
    
    # Status and claim tracking
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.AVAILABLE, nullable=False, index=True)
    claimed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    claim_expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # GitHub reference
    github_url = Column(String(500), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    repository = relationship("Repository", back_populates="issues")
    claimer = relationship("User", back_populates="claimed_issues", foreign_keys=[claimed_by])
    contributions = relationship("Contribution", back_populates="issue", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"
