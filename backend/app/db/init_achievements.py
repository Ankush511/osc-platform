"""
Initialize achievements in the database

This script should be run after database migrations to populate
the achievements table with predefined achievements.
"""
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.achievement_service import AchievementService


def init_achievements():
    """Initialize achievements in the database"""
    db: Session = SessionLocal()
    try:
        service = AchievementService(db)
        achievements = service.initialize_achievements()
        print(f"Initialized {len(achievements)} achievements")
        
        # Display all achievements
        all_achievements = service.get_all_achievements()
        print(f"\nTotal achievements in database: {len(all_achievements)}")
        
        for achievement in all_achievements:
            print(f"  - {achievement.badge_icon} {achievement.name}: {achievement.description}")
        
    except Exception as e:
        print(f"Error initializing achievements: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_achievements()
