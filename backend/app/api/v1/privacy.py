"""
Privacy and GDPR compliance endpoints.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.gdpr_service import GDPRService
from app.core.logging import logger

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/export")
async def export_user_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Export all user data (GDPR Article 15 - Right of Access).
    
    Returns a comprehensive export of all user data in JSON format.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        data = GDPRService.export_user_data(
            db=db,
            user_id=current_user.id,
            ip_address=client_ip,
        )
        return data
    except Exception as e:
        logger.error(
            f"Error exporting user data: {str(e)}",
            extra={"user_id": current_user.id, "error": str(e)}
        )
        raise


@router.delete("/delete-account")
async def delete_user_account(
    request: Request,
    keep_anonymized: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Delete user account and data (GDPR Article 17 - Right to Erasure).
    
    Args:
        keep_anonymized: If True, contribution records are anonymized but kept for statistics.
                        If False, all data is completely deleted.
    
    Returns:
        Dictionary with deletion results.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        results = GDPRService.delete_user_data(
            db=db,
            user_id=current_user.id,
            ip_address=client_ip,
            keep_anonymized=keep_anonymized,
        )
        return {
            "success": True,
            "message": "Account successfully deleted",
            "results": results,
        }
    except Exception as e:
        logger.error(
            f"Error deleting user account: {str(e)}",
            extra={"user_id": current_user.id, "error": str(e)}
        )
        raise


@router.get("/policy-version")
async def get_privacy_policy_version() -> Dict[str, str]:
    """
    Get current privacy policy version.
    """
    return {
        "version": GDPRService.get_privacy_policy_version(),
        "effective_date": "2024-01-01",
    }


@router.get("/retention-info")
async def get_data_retention_info() -> Dict[str, Any]:
    """
    Get information about data retention policies.
    """
    return GDPRService.get_data_retention_info()
