"""
Database dependency for FastAPI routes.
Provides a SQLAlchemy session using dependency injection.
"""
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
