"""
GDPR compliance service for data privacy controls.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.contribution import Contribution
from app.models.issue import Issue
from app.core.logging import logger
from app.core.audit_log import AuditLogger, AuditEventType


class GDPRService:
    """
    Service for GDPR compliance operations.
    """
    
    @staticmethod
    def export_user_data(db: Session, user_id: int, ip_address: str) -> Dict[str, Any]:
        """
        Export all user data (GDPR Article 15 - Right of Access).
        
        Args:
            db: Database session
            user_id: User ID
            ip_address: IP address of request
            
        Returns:
            Dictionary containing all user data
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Collect user profile data
        user_data = {
            "profile": {
                "id": user.id,
                "github_username": user.github_username,
                "github_id": user.github_id,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "bio": user.bio,
                "location": user.location,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            },
            "preferences": {
                "preferred_languages": user.preferred_languages,
                "preferred_labels": user.preferred_labels,
            },
            "statistics": {
                "total_contributions": user.total_contributions,
                "merged_prs": user.merged_prs,
            },
        }
        
        # Collect contributions
        contributions = db.query(Contribution).filter(
            Contribution.user_id == user_id
        ).all()
        
        user_data["contributions"] = [
            {
                "id": contrib.id,
                "issue_id": contrib.issue_id,
                "pr_url": contrib.pr_url,
                "pr_number": contrib.pr_number,
                "status": contrib.status,
                "submitted_at": contrib.submitted_at.isoformat() if contrib.submitted_at else None,
                "merged_at": contrib.merged_at.isoformat() if contrib.merged_at else None,
                "points_earned": contrib.points_earned,
            }
            for contrib in contributions
        ]
        
        # Collect claimed issues
        claimed_issues = db.query(Issue).filter(
            Issue.claimed_by == user_id
        ).all()
        
        user_data["claimed_issues"] = [
            {
                "id": issue.id,
                "title": issue.title,
                "github_url": issue.github_url,
                "status": issue.status,
                "claimed_at": issue.claimed_at.isoformat() if issue.claimed_at else None,
                "claim_expires_at": issue.claim_expires_at.isoformat() if issue.claim_expires_at else None,
            }
            for issue in claimed_issues
        ]
        
        # Add metadata
        user_data["export_metadata"] = {
            "exported_at": datetime.utcnow().isoformat(),
            "export_format": "JSON",
            "gdpr_article": "Article 15 - Right of Access",
        }
        
        # Log the export
        AuditLogger.log_data_privacy(
            event_type=AuditEventType.DATA_EXPORT,
            user_id=user_id,
            user_name=user.github_username,
            ip_address=ip_address,
            details=f"User data exported for user {user.github_username}",
        )
        
        logger.info(
            f"User data exported for user {user_id}",
            extra={"user_id": user_id, "ip_address": ip_address}
        )
        
        return user_data
    
    @staticmethod
    def delete_user_data(
        db: Session,
        user_id: int,
        ip_address: str,
        keep_anonymized: bool = True
    ) -> Dict[str, Any]:
        """
        Delete user data (GDPR Article 17 - Right to Erasure).
        
        Args:
            db: Database session
            user_id: User ID
            ip_address: IP address of request
            keep_anonymized: Whether to keep anonymized contribution records
            
        Returns:
            Dictionary with deletion results
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        username = user.github_username
        
        results = {
            "user_deleted": False,
            "contributions_deleted": 0,
            "contributions_anonymized": 0,
            "issues_released": 0,
        }
        
        # Release any claimed issues
        claimed_issues = db.query(Issue).filter(
            Issue.claimed_by == user_id
        ).all()
        
        for issue in claimed_issues:
            issue.claimed_by = None
            issue.claimed_at = None
            issue.claim_expires_at = None
            issue.status = "available"
            results["issues_released"] += 1
        
        # Handle contributions
        contributions = db.query(Contribution).filter(
            Contribution.user_id == user_id
        ).all()
        
        if keep_anonymized:
            # Anonymize contributions (keep for platform statistics)
            for contrib in contributions:
                # Keep the contribution record but remove user link
                contrib.user_id = None
                results["contributions_anonymized"] += 1
        else:
            # Delete contributions entirely
            for contrib in contributions:
                db.delete(contrib)
                results["contributions_deleted"] += 1
        
        # Delete user account
        db.delete(user)
        results["user_deleted"] = True
        
        # Commit changes
        db.commit()
        
        # Log the deletion
        AuditLogger.log_data_privacy(
            event_type=AuditEventType.DATA_DELETE,
            user_id=user_id,
            user_name=username,
            ip_address=ip_address,
            details=f"User data deleted for user {username} (anonymized: {keep_anonymized})",
        )
        
        logger.info(
            f"User data deleted for user {user_id}",
            extra={
                "user_id": user_id,
                "username": username,
                "ip_address": ip_address,
                "keep_anonymized": keep_anonymized,
                "results": results,
            }
        )
        
        return results
    
    @staticmethod
    def update_consent(
        db: Session,
        user_id: int,
        ip_address: str,
        consent_type: str,
        consent_given: bool
    ) -> Dict[str, Any]:
        """
        Update user consent preferences.
        
        Args:
            db: Database session
            user_id: User ID
            ip_address: IP address of request
            consent_type: Type of consent (e.g., 'data_processing', 'marketing')
            consent_given: Whether consent is given
            
        Returns:
            Dictionary with consent update results
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Note: This assumes a consent field exists on the User model
        # You may need to add a JSON field or separate consent table
        
        # Log the consent update
        AuditLogger.log_data_privacy(
            event_type=AuditEventType.CONSENT_UPDATE,
            user_id=user_id,
            user_name=user.github_username,
            ip_address=ip_address,
            details=f"Consent updated: {consent_type} = {consent_given}",
        )
        
        logger.info(
            f"Consent updated for user {user_id}",
            extra={
                "user_id": user_id,
                "consent_type": consent_type,
                "consent_given": consent_given,
                "ip_address": ip_address,
            }
        )
        
        return {
            "success": True,
            "consent_type": consent_type,
            "consent_given": consent_given,
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def get_privacy_policy_version() -> str:
        """
        Get current privacy policy version.
        
        Returns:
            Privacy policy version string
        """
        return "1.0.0"
    
    @staticmethod
    def get_data_retention_info() -> Dict[str, Any]:
        """
        Get information about data retention policies.
        
        Returns:
            Dictionary with retention information
        """
        return {
            "user_profiles": "Retained until account deletion",
            "contributions": "Retained indefinitely (can be anonymized on request)",
            "audit_logs": "Retained for 30 days (security events) or 7 days (general)",
            "session_data": "Retained for 7 days",
            "cache_data": "Retained for 24 hours to 7 days depending on type",
        }
