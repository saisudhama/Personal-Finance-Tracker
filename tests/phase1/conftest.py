"""
Shared fixtures for Phase 1 API and DB tests.
Uses a separate SQLite file (test.db) so tests never touch your dev app.db.
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-32chars")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import atexit
from opentelemetry import trace

@atexit.register
def _shutdown_tracer():
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "9999999999",
        "monthly_income": 50000,
        "password": "testpassword123",
    }
    client.post("/auth/register", json=payload)
    return payload


@pytest.fixture
def auth_token(client, registered_user):
    response = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
