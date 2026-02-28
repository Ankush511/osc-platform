from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class ContributionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    MERGED = "merged"
    CLOSED = "closed"


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Pull request details
    pr_url = Column(String(500), nullable=False)
    pr_number = Column(Integer, nullable=False)
    
    # Status tracking
    status = Column(SQLEnum(ContributionStatus), default=ContributionStatus.SUBMITTED, nullable=False, index=True)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    merged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Gamification
    points_earned = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="contributions")
    issue = relationship("Issue", back_populates="contributions")

    def __repr__(self):
        return f"<Contribution(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
