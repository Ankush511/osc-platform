#!/usr/bin/env python3
"""
Dashboard cleanup script.
Resets all contributions, achievements, user stats, and issue statuses
back to a fresh state. Clears all in-memory caches.

Usage:
    python dashboard_cleanup.py              # Reset for all users
    python dashboard_cleanup.py --user-id 1  # Reset for a specific user
"""
import argparse
import sys
import os
from typing import Optional

# Ensure the backend app is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import SessionLocal
from app.models.contribution import Contribution
from app.models.issue import Issue, IssueStatus
from app.models.user import User
from app.models.achievement import UserAchievement
from app.services.cache_service import cache_service


def cleanup(user_id: Optional[int] = None):
    db = SessionLocal()

    try:
        # Scope queries
        contrib_query = db.query(Contribution)
        achievement_query = db.query(UserAchievement)
        user_query = db.query(User)
        if user_id:
            contrib_query = contrib_query.filter(Contribution.user_id == user_id)
            achievement_query = achievement_query.filter(UserAchievement.user_id == user_id)
            user_query = user_query.filter(User.id == user_id)

        # 1. Collect issue IDs linked to contributions being deleted
        contribs = contrib_query.all()
        issue_ids = list({c.issue_id for c in contribs})
        print(f"Contributions to delete: {len(contribs)}")

        # 2. Delete contributions
        contrib_query.delete(synchronize_session="fetch")

        # 3. Reset affected issues back to available
        if issue_ids:
            for issue in db.query(Issue).filter(Issue.id.in_(issue_ids)).all():
                issue.status = IssueStatus.AVAILABLE
                issue.claimed_by = None
                issue.claimed_at = None
                issue.claim_expires_at = None
            print(f"Issues reset to available: {issue_ids}")

        # 4. Reset user stats
        for user in user_query.all():
            user.total_contributions = 0
            user.merged_prs = 0
            print(f"User {user.id} ({user.github_username}) stats reset")

        # 5. Delete user achievements
        ach_count = achievement_query.delete(synchronize_session="fetch")
        print(f"User achievements deleted: {ach_count}")

        # 6. Clear AI summaries from issues
        ai_query = db.query(Issue).filter(Issue.ai_explanation.isnot(None))
        if user_id and issue_ids:
            ai_query = ai_query.filter(Issue.id.in_(issue_ids))
        ai_count = 0
        for issue in ai_query.all():
            issue.ai_explanation = None
            ai_count += 1
        print(f"AI summaries cleared: {ai_count}")

        db.commit()

        # 7. Flush all caches
        cache_service._store.clear()
        cache_service._expiry.clear()
        print("In-process cache cleared (restart server to clear its cache too)")

        print("\nCleanup complete. Restart the backend server for a fully fresh state.")

    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset dashboard data to a fresh state")
    parser.add_argument("--user-id", type=int, default=None, help="Reset only this user (default: all users)")
    args = parser.parse_args()

    scope = f"user {args.user_id}" if args.user_id else "all users"
    print(f"Resetting dashboard data for {scope}...\n")
    cleanup(args.user_id)
