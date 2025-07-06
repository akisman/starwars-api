import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.session import Base
from app.db.deps import get_db

# In-memory SQLite URL with shared cache for concurrency
SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

# Create engine with URI flag and check_same_thread False for FastAPI concurrency
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True},
)

# Session factory bound to the test engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Session:
    """
    Creates a new database session with a fresh schema for each test.
    Drops all tables after test to ensure isolation.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session):
    """
    Provides a TestClient instance that overrides the app's database dependency
    to use the test session, allowing isolated testing of API routes.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Remove override to avoid affecting other tests
    app.dependency_overrides.pop(get_db, None)
