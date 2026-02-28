"""
Audit logging system for tracking sensitive operations.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json

from sqlalchemy.orm import Session
from app.core.logging import logger
from app.services.cache_service import cache_service


class AuditEventType(str, Enum):
    """Types of auditable events."""
    
    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    TOKEN_REFRESH = "token_refresh"
    AUTH_FAILURE = "auth_failure"
    
    # User management
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ROLE_CHANGE = "user_role_change"
    USER_PREFERENCES_UPDATE = "user_preferences_update"
    
    # Issue operations
    ISSUE_CLAIM = "issue_claim"
    ISSUE_RELEASE = "issue_release"
    ISSUE_EXTEND = "issue_extend"
    ISSUE_AUTO_RELEASE = "issue_auto_release"
    
    # Contribution operations
    PR_SUBMIT = "pr_submit"
    PR_VALIDATE = "pr_validate"
    PR_MERGE = "pr_merge"
    
    # Admin operations
    ADMIN_REPO_ADD = "admin_repo_add"
    ADMIN_REPO_UPDATE = "admin_repo_update"
    ADMIN_REPO_DELETE = "admin_repo_delete"
    ADMIN_CONFIG_UPDATE = "admin_config_update"
    ADMIN_SYNC_TRIGGER = "admin_sync_trigger"
    ADMIN_USER_UPDATE = "admin_user_update"
    
    # Security events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_BLACKLISTED = "ip_blacklisted"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCESS_DENIED = "access_denied"
    
    # Data privacy
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    CONSENT_UPDATE = "consent_update"


class AuditLogger:
    """
    Centralized audit logging for sensitive operations.
    """
    
    @staticmethod
    def log_event(
        event_type: AuditEventType,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ) -> None:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            user_id: ID of user performing action
            user_name: Username of user performing action
            ip_address: IP address of request
            details: Human-readable description
            metadata: Additional structured data
            success: Whether the operation succeeded
        """
        timestamp = datetime.utcnow()
        
        audit_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "user_name": user_name,
            "ip_address": ip_address,
            "details": details,
            "metadata": metadata or {},
            "success": success,
        }
        
        # Log to application logger
        log_level = "info" if success else "warning"
        log_message = f"AUDIT: {event_type.value}"
        if details:
            log_message += f" - {details}"
        
        logger.log(
            log_level.upper(),
            log_message,
            extra={
                "audit": True,
                "event_type": event_type.value,
                "user_id": user_id,
                "user_name": user_name,
                "ip_address": ip_address,
                "success": success,
                "metadata": metadata,
            }
        )
        
        # Store in Redis for recent activity (last 1000 events, 7 days retention)
        cache_key = f"audit:recent:{timestamp.timestamp()}"
        cache_service.set(cache_key, json.dumps(audit_entry), 604800)  # 7 days
        
        # For critical security events, also store in a separate list
        if event_type in [
            AuditEventType.AUTH_FAILURE,
            AuditEventType.RATE_LIMIT_EXCEEDED,
            AuditEventType.IP_BLACKLISTED,
            AuditEventType.SUSPICIOUS_ACTIVITY,
            AuditEventType.ACCESS_DENIED,
        ]:
            security_key = f"audit:security:{timestamp.timestamp()}"
            cache_service.set(security_key, json.dumps(audit_entry), 2592000)  # 30 days
    
    @staticmethod
    def log_authentication(
        event_type: AuditEventType,
        user_id: Optional[int],
        user_name: Optional[str],
        ip_address: str,
        success: bool,
        details: Optional[str] = None,
    ) -> None:
        """
        Log authentication-related events.
        
        Args:
            event_type: Type of auth event
            user_id: User ID
            user_name: Username
            ip_address: IP address
            success: Whether auth succeeded
            details: Additional details
        """
        AuditLogger.log_event(
            event_type=event_type,
            user_id=user_id,
            user_name=user_name,
            ip_address=ip_address,
            details=details,
            success=success,
        )
    
    @staticmethod
    def log_admin_action(
        event_type: AuditEventType,
        admin_id: int,
        admin_name: str,
        ip_address: str,
        details: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log administrative actions.
        
        Args:
            event_type: Type of admin event
            admin_id: Admin user ID
            admin_name: Admin username
            ip_address: IP address
            details: Description of action
            metadata: Additional data
        """
        AuditLogger.log_event(
            event_type=event_type,
            user_id=admin_id,
            user_name=admin_name,
            ip_address=ip_address,
            details=details,
            metadata=metadata,
            success=True,
        )
    
    @staticmethod
    def log_security_event(
        event_type: AuditEventType,
        ip_address: str,
        details: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            ip_address: IP address
            details: Description of event
            metadata: Additional data
        """
        AuditLogger.log_event(
            event_type=event_type,
            ip_address=ip_address,
            details=details,
            metadata=metadata,
            success=False,
        )
    
    @staticmethod
    def log_data_privacy(
        event_type: AuditEventType,
        user_id: int,
        user_name: str,
        ip_address: str,
        details: str,
    ) -> None:
        """
        Log data privacy operations (GDPR compliance).
        
        Args:
            event_type: Type of privacy event
            user_id: User ID
            user_name: Username
            ip_address: IP address
            details: Description of operation
        """
        AuditLogger.log_event(
            event_type=event_type,
            user_id=user_id,
            user_name=user_name,
            ip_address=ip_address,
            details=details,
            success=True,
        )
    
    @staticmethod
    def get_recent_events(limit: int = 100) -> list:
        """
        Get recent audit events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent audit events
        """
        # This would query Redis for recent events
        # Implementation depends on how you want to structure the data
        # For now, return empty list as placeholder
        return []
    
    @staticmethod
    def get_user_activity(user_id: int, limit: int = 50) -> list:
        """
        Get audit events for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of events to return
            
        Returns:
            List of user's audit events
        """
        # This would query Redis/database for user-specific events
        return []
