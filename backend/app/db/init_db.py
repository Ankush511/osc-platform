"""
Database initialization utilities.
This module provides functions to initialize the database schema.
"""
from app.db.base import Base, engine


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    This is useful for development and testing.
    For production, use Alembic migrations instead.
    
    Note: Models must be imported before calling this function
    so they are registered with Base.metadata.
    """
    # Import models to register them with Base.metadata
    import app.models.user  # noqa
    import app.models.repository  # noqa
    import app.models.issue  # noqa
    import app.models.contribution  # noqa
    
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.
    WARNING: This will delete all data!
    Only use in development/testing environments.
    """
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    WARNING: This will delete all data!
    Only use in development/testing environments.
    """
    drop_db()
    init_db()
