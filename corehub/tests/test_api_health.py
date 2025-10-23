"""
Tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from corehub.api.main import app
from corehub.db.database import get_db
from corehub.db.models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_health_check_basic(client):
    """Test basic health check endpoint."""
    response = client.get("/health/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["service"] == "CoreHub API"
    assert data["version"] == "0.1.0"


def test_health_check_detailed(client):
    """Test detailed health check endpoint."""
    response = client.get("/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "database" in data
    assert "components" in data
    assert data["components"]["api"] == "healthy"


def test_health_check_ready(client):
    """Test readiness check endpoint."""
    response = client.get("/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ready"
    assert data["ready"] is True
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "CoreHub API"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data
    assert "health" in data["endpoints"]
