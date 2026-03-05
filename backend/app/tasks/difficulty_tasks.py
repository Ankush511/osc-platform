"""
Background task for AI-based difficulty refinement.
Runs after issue sync to replace heuristic difficulty with AI assessment.
"""
import logging
from typing import List
from app.db.base import SessionLocal
from app.services.ai_service import AIService, AIServiceException

logger = logging.getLogger(__name__)


def refine_difficulty_for_issues(issue_ids: List[int]) -> dict:
    """
    Refine difficulty levels for a batch of issues using AI.
    Intended to run as a background task after sync.

    Args:
        issue_ids: List of issue IDs to refine.

    Returns:
        Summary dict with counts.
    """
    if not issue_ids:
        return {"refined": 0, "failed": 0, "skipped": 0}

    logger.info(f"Starting AI difficulty refinement for {len(issue_ids)} issues")
    db = SessionLocal()
    refined = 0
    failed = 0

    try:
        ai_service = AIService(db=db)
        for issue_id in issue_ids:
            try:
                ai_service.analyze_difficulty(issue_id)
                refined += 1
            except AIServiceException as e:
                logger.warning(f"AI difficulty refinement failed for issue {issue_id}: {e}")
                failed += 1
            except Exception as e:
                logger.error(f"Unexpected error refining issue {issue_id}: {e}")
                failed += 1

        logger.info(f"Difficulty refinement complete: {refined} refined, {failed} failed")
        return {"refined": refined, "failed": failed}
    finally:
        db.close()
